from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.production import (
    ProductionProcess, ProcessStep, ProcessLog, YieldRecord, ColdRoomTransfer, AgingRecord,
    ProcessParameter, ProcessDeviation, ProcessAlert, ProductSpecification, ProcessTemplate,
    ProductProcessType, ProcessStatus, StepType, LogEvent
)
from app.models.traceability import Batch, BatchStatus, BatchType
from app.models.production import ProcessSpecLink, ReleaseRecord
from app.models.document import Document
from app.services.nonconformance_service import NonConformanceService
from app.schemas.nonconformance import NonConformanceCreate as NCCreateSchema, NonConformanceSource as NCSource
from app.models.nonconformance import NonConformance, NonConformanceStatus, NonConformanceSource
from app.services.training_service import TrainingService
from app.services.equipment_calibration_service import EquipmentCalibrationService
from app.models.supplier import IncomingDelivery, Supplier, Material as SupplierMaterial


class ProductionService:
    def __init__(self, db: Session):
        self.db = db

    def create_process(self, batch_id: int, process_type: ProductProcessType, operator_id: Optional[int], spec: Dict[str, Any]) -> ProductionProcess:
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        process = ProductionProcess(
            batch_id=batch_id,
            process_type=process_type,
            operator_id=operator_id,
            spec=spec,
            status=ProcessStatus.IN_PROGRESS,
        )
        self.db.add(process)
        # Create steps from spec
        for seq, step in enumerate(spec.get("steps", []), start=1):
            ps = ProcessStep(
                process=process,
                step_type=StepType(step["type"]),
                sequence=seq,
                target_temp_c=step.get("target_temp_c"),
                target_time_seconds=step.get("target_time_seconds"),
                tolerance_c=step.get("tolerance_c"),
                required=step.get("required", True),
                step_metadata=step.get("metadata"),
            )
            self.db.add(ps)
        self.db.commit()
        self.db.refresh(process)
        return process

    def add_log(self, process_id: int, data: Dict[str, Any]) -> ProcessLog:
        process = self.db.query(ProductionProcess).filter(ProductionProcess.id == process_id).first()
        if not process:
            raise ValueError("Process not found")
        log = ProcessLog(
            process_id=process_id,
            step_id=data.get("step_id"),
            timestamp=data.get("timestamp") or datetime.utcnow(),
            event=LogEvent(data.get("event")),
            measured_temp_c=data.get("measured_temp_c"),
            note=data.get("note"),
            auto_flag=data.get("auto_flag", False),
            source=data.get("source", "manual"),
        )
        self.db.add(log)
        # Validate critical steps (e.g., HTST 72C for 15 sec)
        self._evaluate_diversion(process, log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def record_yield(self, process_id: int, output_qty: float, unit: str, expected_qty: Optional[float] = None) -> YieldRecord:
        yr = YieldRecord(
            process_id=process_id,
            output_qty=output_qty,
            expected_qty=expected_qty,
            unit=unit,
        )
        if expected_qty and expected_qty != 0:
            yr.overrun_percent = ((output_qty - expected_qty) / expected_qty) * 100.0
        self.db.add(yr)
        self.db.commit()
        self.db.refresh(yr)
        return yr

    def record_transfer(self, process_id: int, quantity: float, unit: str, location: Optional[str], lot_number: Optional[str], verified_by: Optional[int]) -> ColdRoomTransfer:
        transfer = ColdRoomTransfer(
            process_id=process_id,
            quantity=quantity,
            unit=unit,
            location=location,
            lot_number=lot_number,
            verified_by=verified_by,
        )
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def record_aging(self, process_id: int, data: Dict[str, Any]) -> AgingRecord:
        ar = AgingRecord(
            process_id=process_id,
            start_time=data.get("start_time") or datetime.utcnow(),
            end_time=data.get("end_time"),
            room_temperature_c=data.get("room_temperature_c"),
            target_temp_min_c=data.get("target_temp_min_c"),
            target_temp_max_c=data.get("target_temp_max_c"),
            target_days=data.get("target_days"),
            room_location=data.get("room_location"),
            notes=data.get("notes"),
        )
        self.db.add(ar)
        self.db.commit()
        self.db.refresh(ar)
        return ar

    def get_process(self, process_id: int) -> Optional[ProductionProcess]:
        return self.db.query(ProductionProcess).filter(ProductionProcess.id == process_id).first()

    def list_processes(self, product_type: Optional[ProductProcessType], status: Optional[ProcessStatus], limit: int, offset: int) -> List[ProductionProcess]:
        query = self.db.query(ProductionProcess)
        if product_type:
            query = query.filter(ProductionProcess.process_type == product_type)
        if status:
            query = query.filter(ProductionProcess.status == status)
        return query.order_by(ProductionProcess.start_time.desc()).offset(offset).limit(limit).all()

    def get_process_parameters(self, process_id: int) -> List[ProcessParameter]:
        return (
            self.db.query(ProcessParameter)
            .filter(ProcessParameter.process_id == process_id)
            .order_by(ProcessParameter.recorded_at.asc())
            .all()
        )

    def update_process(self, process_id: int, data: Dict[str, Any]) -> ProductionProcess:
        proc = self.get_process(process_id)
        if not proc:
            raise ValueError("Process not found")
        # Update allowed fields
        if "status" in data and data["status"]:
            # Map incoming string to enum if needed
            if isinstance(data["status"], str):
                proc.status = ProcessStatus(data["status"])  # may raise ValueError for invalid
            else:
                proc.status = data["status"]
        if "notes" in data:
            proc.notes = data["notes"]
        if "end_time" in data:
            proc.end_time = data["end_time"]
        # Touch updated_at if present on model
        try:
            proc.updated_at = datetime.utcnow()
        except Exception:
            pass
        self.db.commit()
        self.db.refresh(proc)
        return proc

    def get_analytics(self, product_type: Optional[ProductProcessType] = None) -> Dict[str, Any]:
        query = self.db.query(YieldRecord)
        if product_type:
            query = query.join(ProductionProcess, ProductionProcess.id == YieldRecord.process_id).filter(ProductionProcess.process_type == product_type)
        yields = query.all()
        total = len(yields)
        overruns = [y for y in yields if (y.overrun_percent or 0) > 0]
        underruns = [y for y in yields if (y.overrun_percent or 0) < 0]
        avg_overrun = sum((y.overrun_percent or 0) for y in yields) / total if total else 0.0
        return {
            "total_records": total,
            "avg_overrun_percent": round(avg_overrun, 2),
            "overruns": len(overruns),
            "underruns": len(underruns),
        }

    # Internal validation
    def _evaluate_diversion(self, process: ProductionProcess, log: ProcessLog) -> None:
        # Applies for Fresh milk HTST: >=72C for 15s; otherwise mark diverted
        try:
            if process.process_type == ProductProcessType.FRESH_MILK:
                # Consider last 20 seconds readings
                window_start = log.timestamp - timedelta(seconds=20)
                logs = self.db.query(ProcessLog).filter(
                    ProcessLog.process_id == process.id,
                    ProcessLog.timestamp >= window_start
                ).order_by(ProcessLog.timestamp.asc()).all()
                # Count consecutive seconds above 72C
                above = 0
                for l in logs:
                    if (l.measured_temp_c or 0) >= 72.0:
                        above += 1
                    else:
                        above = 0
                if above < 15 and any(l.event == LogEvent.READING for l in logs):
                    # Automatically divert
                    divert = ProcessLog(
                        process_id=process.id,
                        step_id=log.step_id,
                        timestamp=datetime.utcnow(),
                        event=LogEvent.DIVERT,
                        measured_temp_c=log.measured_temp_c,
                        note="Auto-divert: HTST criteria not met",
                        auto_flag=True,
                        source="auto",
                    )
                    process.status = ProcessStatus.DIVERTED
                    self.db.add(divert)
        except Exception:
            # Do not block logging on validation errors
            pass

    # Enhanced Production Methods
    def record_parameter(self, process_id: int, data: Dict[str, Any]) -> ProcessParameter:
        """Record a process parameter with validation"""
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")
        
        # Competence check for operator (if provided)
        try:
            operator_id = data.get("recorded_by") or process.operator_id
            if operator_id:
                training = TrainingService(self.db)
                eligibility = training.check_eligibility(operator_id)
                if not eligibility.get("eligible", True):
                    raise ValueError("Operator not eligible: required training incomplete")
        except Exception:
            pass
        
        # Equipment calibration check (if equipment specified)
        try:
            if data.get("equipment_id"):
                ecs = EquipmentCalibrationService(self.db)
                status = ecs.check_equipment_calibration(int(data["equipment_id"]))
                if not status.get("is_valid", False):
                    raise ValueError(f"Equipment calibration invalid: {status.get('message')}")
        except Exception:
            pass
        
        # Validate parameter value against tolerances
        is_within_tolerance = None
        if data.get("target_value") and data.get("tolerance_min") and data.get("tolerance_max"):
            value = data["parameter_value"]
            min_val = data["tolerance_min"]
            max_val = data["tolerance_max"]
            is_within_tolerance = min_val <= value <= max_val
            
            # Create deviation if out of tolerance
            if not is_within_tolerance:
                self._create_deviation(process_id, data)
                # Auto-create NC for production deviation (link batch)
                try:
                    process = self.get_process(process_id)
                    batch = self.db.query(Batch).filter(Batch.id == process.batch_id).first()
                    nc_svc = NonConformanceService(self.db)
                    nc_payload = NCCreateSchema(
                        title=f"Production deviation: {data['parameter_name']}",
                        description=f"Parameter {data['parameter_name']} value {value} outside tolerance ({min_val}-{max_val}).",
                        source=NCSource.PRODUCTION_DEVIATION,
                        batch_reference=(batch.batch_number if batch else None),
                        product_reference=(batch.product_name if batch else None),
                        process_reference=str(process_id),
                        severity="high",
                        impact_area="food_safety"
                    )
                    nc_svc.create_non_conformance(nc_payload, reported_by=data.get("recorded_by") or process.operator_id or 1)
                except Exception:
                    pass
        
        parameter = ProcessParameter(
            process_id=process_id,
            step_id=data.get("step_id"),
            parameter_name=data["parameter_name"],
            parameter_value=data["parameter_value"],
            unit=data["unit"],
            target_value=data.get("target_value"),
            tolerance_min=data.get("tolerance_min"),
            tolerance_max=data.get("tolerance_max"),
            is_within_tolerance=is_within_tolerance,
            recorded_by=data.get("recorded_by"),
            notes=data.get("notes"),
        )
        
        self.db.add(parameter)
        self.db.commit()
        self.db.refresh(parameter)
        return parameter

    def _create_deviation(self, process_id: int, parameter_data: Dict[str, Any]) -> ProcessDeviation:
        """Create a deviation record when parameters are out of tolerance"""
        deviation = ProcessDeviation(
            process_id=process_id,
            step_id=parameter_data.get("step_id"),
            deviation_type=parameter_data["parameter_name"],
            expected_value=parameter_data.get("target_value", 0),
            actual_value=parameter_data["parameter_value"],
            severity=self._calculate_severity(parameter_data),
            created_by=parameter_data.get("created_by") or parameter_data.get("recorded_by"),
        )
        
        # Calculate deviation percentage
        if parameter_data.get("target_value") and parameter_data["target_value"] != 0:
            deviation.deviation_percent = (
                (parameter_data["parameter_value"] - parameter_data["target_value"]) / 
                parameter_data["target_value"] * 100
            )
        
        self.db.add(deviation)
        self.db.commit()
        self.db.refresh(deviation)
        return deviation

    def _calculate_severity(self, parameter_data: Dict[str, Any]) -> str:
        """Calculate deviation severity based on parameter type and deviation"""
        param_name = parameter_data["parameter_name"].lower()
        
        # Critical parameters for food safety
        if "temperature" in param_name and "pasteurization" in param_name:
            return "critical"
        elif "temperature" in param_name:
            return "high"
        elif "time" in param_name:
            return "medium"
        else:
            return "low"

    def create_alert(self, process_id: int, data: Dict[str, Any]) -> ProcessAlert:
        """Create a process alert"""
        alert = ProcessAlert(
            process_id=process_id,
            alert_type=data["alert_type"],
            alert_level=data["alert_level"],
            message=data["message"],
            parameter_value=data.get("parameter_value"),
            threshold_value=data.get("threshold_value"),
            created_by=data.get("created_by"),
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def acknowledge_alert(self, alert_id: int, user_id: int) -> ProcessAlert:
        """Acknowledge a process alert"""
        alert = self.db.query(ProcessAlert).filter(ProcessAlert.id == alert_id).first()
        if not alert:
            raise ValueError("Alert not found")
        
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def resolve_deviation(self, deviation_id: int, user_id: int, corrective_action: str) -> ProcessDeviation:
        """Resolve a process deviation"""
        deviation = self.db.query(ProcessDeviation).filter(ProcessDeviation.id == deviation_id).first()
        if not deviation:
            raise ValueError("Deviation not found")
        
        deviation.resolved = True
        deviation.resolved_at = datetime.utcnow()
        deviation.resolved_by = user_id
        deviation.corrective_action = corrective_action
        
        self.db.commit()
        self.db.refresh(deviation)
        return deviation

    def create_process_template(self, data: Dict[str, Any]) -> ProcessTemplate:
        """Create a process template"""
        template = ProcessTemplate(
            template_name=data["template_name"],
            product_type=ProductProcessType(data["product_type"]),
            description=data.get("description"),
            steps=data["steps"],
            parameters=data.get("parameters"),
            created_by=data.get("created_by"),
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_process_templates(self, product_type: Optional[ProductProcessType] = None) -> List[ProcessTemplate]:
        """Get process templates"""
        query = self.db.query(ProcessTemplate).filter(ProcessTemplate.is_active == True)
        if product_type:
            query = query.filter(ProcessTemplate.product_type == product_type)
        return query.all()

    def get_process_with_details(self, process_id: int) -> Optional[Dict[str, Any]]:
        """Get process with all related data"""
        process = self.get_process(process_id)
        if not process:
            return None
        
        # Get related data
        steps = self.db.query(ProcessStep).filter(ProcessStep.process_id == process_id).order_by(ProcessStep.sequence).all()
        logs = self.db.query(ProcessLog).filter(ProcessLog.process_id == process_id).order_by(ProcessLog.timestamp).all()
        parameters = self.db.query(ProcessParameter).filter(ProcessParameter.process_id == process_id).order_by(ProcessParameter.recorded_at).all()
        deviations = self.db.query(ProcessDeviation).filter(ProcessDeviation.process_id == process_id).order_by(ProcessDeviation.created_at).all()
        alerts = self.db.query(ProcessAlert).filter(ProcessAlert.process_id == process_id).order_by(ProcessAlert.created_at).all()
        
        return {
            "process": process,
            "steps": steps,
            "logs": logs,
            "parameters": parameters,
            "deviations": deviations,
            "alerts": alerts,
        }

    def get_enhanced_analytics(self, process_type: Optional[ProductProcessType] = None) -> Dict[str, Any]:
        """Get comprehensive production analytics"""
        base_analytics = self.get_analytics(process_type)
        
        # Get deviation statistics
        deviation_query = self.db.query(ProcessDeviation)
        if process_type:
            deviation_query = deviation_query.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        total_deviations = deviation_query.count()
        critical_deviations = deviation_query.filter(ProcessDeviation.severity == "critical").count()
        
        # Get alert statistics
        alert_query = self.db.query(ProcessAlert)
        if process_type:
            alert_query = alert_query.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        total_alerts = alert_query.count()
        unacknowledged_alerts = alert_query.filter(ProcessAlert.acknowledged == False).count()
        
        # Get process type breakdown
        process_breakdown = {}
        for pt in ProductProcessType:
            count = self.db.query(ProductionProcess).filter(ProductionProcess.process_type == pt).count()
            if count > 0:
                process_breakdown[pt.value] = count
        
        # Trends: last 30 days
        try:
            from datetime import datetime, timedelta
            cutoff = datetime.utcnow() - timedelta(days=30)
            # Yield trends (counts per day)
            yq = self.db.query(func.date(YieldRecord.created_at).label('d'), func.count(YieldRecord.id)).filter(
                YieldRecord.created_at >= cutoff
            )
            if process_type:
                yq = yq.join(ProductionProcess, ProductionProcess.id == YieldRecord.process_id).filter(ProductionProcess.process_type == process_type)
            yq = yq.group_by('d').order_by('d').all()
            yield_trends = [{"date": str(d), "count": c} for d, c in yq]
            # Deviation trends
            dq = self.db.query(func.date(ProcessDeviation.created_at).label('d'), func.count(ProcessDeviation.id)).filter(
                ProcessDeviation.created_at >= cutoff
            )
            if process_type:
                dq = dq.join(ProductionProcess, ProductionProcess.id == ProcessDeviation.process_id).filter(ProductionProcess.process_type == process_type)
            dq = dq.group_by('d').order_by('d').all()
            deviation_trends = [{"date": str(d), "count": c} for d, c in dq]
        except Exception:
            yield_trends = []
            deviation_trends = []
        
        return {
            **base_analytics,
            "total_deviations": total_deviations,
            "critical_deviations": critical_deviations,
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged_alerts,
            "process_type_breakdown": process_breakdown,
            "yield_trends": yield_trends,
            "deviation_trends": deviation_trends,
        }

    # Materials
    def record_material_consumption(self, process_id: int, data: Dict[str, Any]) -> Any:
        from app.models.production import MaterialConsumption
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")
        # Optional supplier/delivery validation
        if data.get("delivery_id"):
            delivery = self.db.query(IncomingDelivery).filter(IncomingDelivery.id == data["delivery_id"]).first()
            if not delivery:
                raise ValueError("Delivery not found")
            if delivery.inspection_status not in ("passed",):
                raise ValueError("Cannot consume materials from unapproved delivery")
            if data.get("material_id") and delivery.material_id != data["material_id"]:
                raise ValueError("Delivery does not match selected material")
        mc = MaterialConsumption(
            process_id=process_id,
            material_id=int(data["material_id"]),
            supplier_id=data.get("supplier_id"),
            delivery_id=data.get("delivery_id"),
            lot_number=data.get("lot_number"),
            quantity=float(data["quantity"]),
            unit=data["unit"],
            recorded_by=data.get("recorded_by"),
            notes=data.get("notes"),
        )
        self.db.add(mc)
        self.db.commit()
        self.db.refresh(mc)
        return mc

    # Spec binding and release
    def bind_spec_version(self, process_id: int, document_id: int, document_version: str, locked_parameters: Optional[Dict[str, Any]]) -> ProcessSpecLink:
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError("Document not found")
        link = ProcessSpecLink(
            process_id=process_id,
            document_id=document_id,
            document_version=document_version,
            locked_parameters=locked_parameters or {},
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def get_spec_link(self, process_id: int) -> Optional[ProcessSpecLink]:
        return self.db.query(ProcessSpecLink).filter(ProcessSpecLink.process_id == process_id).order_by(ProcessSpecLink.created_at.desc()).first()

    def check_release_ready(self, process_id: int) -> Dict[str, Any]:
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")
        checklist = []
        failures = []
        # Spec/version bound
        spec_link = self.get_spec_link(process_id)
        has_spec = spec_link is not None
        checklist.append({"item": "Spec version bound", "passed": has_spec})
        if not has_spec:
            failures.append("Spec version is not bound to process")
        # All critical deviations resolved
        critical_open = (
            self.db.query(ProcessDeviation)
            .filter(ProcessDeviation.process_id == process_id, ProcessDeviation.severity == "critical", ProcessDeviation.resolved == False)
            .count()
        )
        checklist.append({"item": "Critical deviations resolved", "passed": critical_open == 0})
        if critical_open > 0:
            failures.append("Critical deviations are open")
        # Parameters exist (basic evidence)
        params_count = self.db.query(ProcessParameter).filter(ProcessParameter.process_id == process_id).count()
        checklist.append({"item": "Process parameters recorded", "passed": params_count > 0})
        if params_count == 0:
            failures.append("No parameters recorded")
        # Status not diverted
        not_diverted = process.status != ProcessStatus.DIVERTED
        checklist.append({"item": "Process not diverted", "passed": not_diverted})
        if not not_diverted:
            failures.append("Process was diverted")
        # Alerts acknowledged
        unack = self.db.query(ProcessAlert).filter(ProcessAlert.process_id == process_id, ProcessAlert.acknowledged == False).count()
        checklist.append({"item": "Alerts acknowledged", "passed": unack == 0})
        if unack > 0:
            failures.append("Unacknowledged alerts present")
        # Open NCs blocking
        try:
            open_ncs = self.db.query(NonConformance).filter(
                NonConformance.source == NonConformanceSource.PRODUCTION_DEVIATION,
                NonConformance.process_reference == str(process_id),
                NonConformance.status.in_([NonConformanceStatus.OPEN, NonConformanceStatus.UNDER_INVESTIGATION, NonConformanceStatus.IN_PROGRESS])
            ).count()
            checklist.append({"item": "No open nonconformances", "passed": open_ncs == 0})
            if open_ncs > 0:
                failures.append("Open nonconformances exist")
        except Exception:
            pass
        # Equipment calibration OK (optional global equipment used at release if any recorded)
        try:
            # If any parameter recorded with equipment_id has invalid calibration, block
            from app.models.production import ProcessParameter as PP
            ecs = EquipmentCalibrationService(self.db)
            equip_ids = [pid for (pid,) in self.db.query(PP.equipment_id).filter(PP.process_id == process_id, PP.equipment_id.isnot(None)).distinct().all()]
            bad = False
            for eid in equip_ids:
                if not eid:
                    continue
                status = ecs.check_equipment_calibration(int(eid))
                if not status.get("is_valid", False):
                    bad = True
                    break
            checklist.append({"item": "Equipment calibration valid", "passed": not bad})
            if bad:
                failures.append("Equipment calibration invalid")
        except Exception:
            pass
        ready = len(failures) == 0
        return {"ready": ready, "failures": failures, "checklist": checklist}

    def create_release(self, process_id: int, checklist: Dict[str, Any], released_qty: Optional[float], unit: Optional[str], verifier_id: Optional[int], approver_id: Optional[int], signature_hash: str) -> ReleaseRecord:
        if not checklist.get("ready"):
            raise ValueError("Process is not ready for release")
        record = ReleaseRecord(
            process_id=process_id,
            checklist_results=checklist,
            released_qty=released_qty,
            unit=unit,
            verifier_id=verifier_id,
            approver_id=approver_id,
            signature_hash=signature_hash,
        )
        self.db.add(record)
        # Optionally mark process completed
        process = self.get_process(process_id)
        if process and process.status != ProcessStatus.COMPLETED:
            process.status = ProcessStatus.COMPLETED
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_release(self, process_id: int) -> Optional[ReleaseRecord]:
        return (
            self.db.query(ReleaseRecord)
            .filter(ReleaseRecord.process_id == process_id)
            .order_by(ReleaseRecord.signed_at.desc())
            .first()
        )

