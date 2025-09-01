from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import math
import statistics
import numpy as np

from app.models.production import (
    ProductionProcess, ProcessStep, ProcessLog, YieldRecord, ColdRoomTransfer, AgingRecord,
    ProcessParameter, ProcessDeviation, ProcessAlert, ProductSpecification, ProcessTemplate,
    ProductProcessType, ProcessStatus, StepType, LogEvent,
    ProcessControlChart, ProcessControlPoint, ProcessCapabilityStudy, YieldAnalysisReport,
    YieldDefectCategory, ProcessMonitoringDashboard, ProcessMonitoringAlert,
    ProcessStage, StageStatus, StageTransition
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
from app.services import log_audit_event


class ProductionService:
    def __init__(self, db: Session):
        self.db = db

    def create_process(self, batch_id: int, process_type: ProductProcessType, operator_id: Optional[int], spec: Dict[str, Any]) -> ProductionProcess:
        print(f"DEBUG: Creating process for batch_id: {batch_id}")
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            print(f"DEBUG: Batch with ID {batch_id} not found in database")
            # Check if any batches exist
            total_batches = self.db.query(Batch).count()
            print(f"DEBUG: Total batches in database: {total_batches}")
            if total_batches > 0:
                # Get some sample batch IDs for debugging
                sample_batches = self.db.query(Batch.id, Batch.batch_number).limit(5).all()
                print(f"DEBUG: Sample batch IDs: {sample_batches}")
            raise ValueError(f"Batch with ID {batch_id} not found. Please ensure the batch exists before creating a process.")
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
        try:
            log_audit_event(
                self.db,
                user_id=operator_id,
                action="process.created",
                resource_type="production_process",
                resource_id=str(process.id),
                details={"batch_id": batch_id, "type": process_type.value}
            )
        except Exception:
            pass
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
        # Audit
        try:
            log_audit_event(
                self.db,
                user_id=data.get("created_by") or data.get("recorded_by") or process.operator_id,
                action="process.log.added",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"log_id": log.id, "event": log.event.value}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=None,
                action="process.yield.recorded",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"yield_id": yr.id, "qty": output_qty, "unit": unit}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=verified_by,
                action="process.transfer.recorded",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"transfer_id": transfer.id, "qty": quantity, "unit": unit}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=None,
                action="process.aging.recorded",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"aging_id": ar.id, "target_days": data.get("target_days")}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=data.get("updated_by") or proc.operator_id,
                action="process.updated",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"changes": list(data.keys())}
            )
        except Exception:
            pass
        return proc

    def get_analytics(self, product_type: Optional[ProductProcessType] = None) -> Dict[str, Any]:
        # Get process counts
        process_query = self.db.query(ProductionProcess)
        if product_type:
            process_query = process_query.filter(ProductionProcess.process_type == product_type)
        
        total_processes = process_query.count()
        active_processes = process_query.filter(ProductionProcess.status == ProcessStatus.IN_PROGRESS).count()
        
        # Get yield data
        yield_query = self.db.query(YieldRecord)
        if product_type:
            yield_query = yield_query.join(ProductionProcess, ProductionProcess.id == YieldRecord.process_id).filter(ProductionProcess.process_type == product_type)
        yields = yield_query.all()
        total_yields = len(yields)
        overruns = [y for y in yields if (y.overrun_percent or 0) > 0]
        underruns = [y for y in yields if (y.overrun_percent or 0) < 0]
        avg_overrun = sum((y.overrun_percent or 0) for y in yields) / total_yields if total_yields else 0.0
        
        return {
            "total_processes": total_processes,
            "active_processes": active_processes,
            "total_records": total_yields,
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
                    try:
                        log_audit_event(
                            self.db,
                            user_id=data.get("recorded_by") or process.operator_id,
                            action="process.nc.auto_created",
                            resource_type="production_process",
                            resource_id=str(process_id),
                            details={"parameter": data["parameter_name"], "value": value}
                        )
                    except Exception:
                        pass
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
        try:
            log_audit_event(
                self.db,
                user_id=data.get("recorded_by") or process.operator_id,
                action="process.parameter.recorded",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"parameter_id": parameter.id, "name": parameter.parameter_name, "within_tol": is_within_tolerance}
            )
        except Exception:
            pass
        return parameter

    def _create_deviation(self, process_id: int, parameter_data: Dict[str, Any]) -> ProcessDeviation:
        """Create a deviation record when parameters are out of tolerance"""
        deviation = ProcessDeviation(
            process_id=process_id,
            step_id=parameter_data.get("step_id"),
            deviation_type=parameter_data.get("deviation_type", parameter_data.get("parameter_name", "unknown")),
            expected_value=parameter_data.get("expected_value", parameter_data.get("target_value", 0)),
            actual_value=parameter_data.get("actual_value", parameter_data.get("parameter_value", 0)),
            severity=parameter_data.get("severity", self._calculate_severity(parameter_data)),
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
        try:
            log_audit_event(
                self.db,
                user_id=parameter_data.get("created_by") or parameter_data.get("recorded_by"),
                action="process.deviation.created",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"deviation_id": deviation.id, "type": deviation.deviation_type, "severity": deviation.severity}
            )
        except Exception:
            pass
        return deviation

    def _calculate_severity(self, parameter_data: Dict[str, Any]) -> str:
        """Calculate deviation severity based on parameter type and deviation"""
        param_name = parameter_data.get("parameter_name", parameter_data.get("deviation_type", "")).lower()
        
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
        try:
            log_audit_event(
                self.db,
                user_id=data.get("created_by"),
                action="process.alert.created",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"alert_id": alert.id, "type": alert.alert_type, "level": alert.alert_level}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=user_id,
                action="process.alert.acknowledged",
                resource_type="production_process",
                resource_id=str(alert.process_id),
                details={"alert_id": alert.id}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=user_id,
                action="process.deviation.resolved",
                resource_type="production_process",
                resource_id=str(deviation.process_id),
                details={"deviation_id": deviation.id}
            )
        except Exception:
            pass
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
        try:
            from app.models.production import MaterialConsumption
            materials = (
                self.db.query(MaterialConsumption)
                .filter(MaterialConsumption.process_id == process_id)
                .order_by(MaterialConsumption.consumed_at.desc())
                .all()
            )
        except Exception:
            materials = []
        
        stages = self.db.query(ProcessStage).filter(ProcessStage.process_id == process_id).order_by(ProcessStage.sequence_order).all()
        active_stage = next((s for s in stages if s.status == StageStatus.IN_PROGRESS), None)
        return {
            "process": process,
            "steps": steps,
            "logs": logs,
            "parameters": parameters,
            "deviations": deviations,
            "alerts": alerts,
            "materials": materials,
            "stages": stages,
            "active_stage": active_stage,
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
        
        # Get process type breakdown (grouped query)
        rows = (
            self.db.query(ProductionProcess.process_type, func.count(ProductionProcess.id))
            .group_by(ProductionProcess.process_type)
            .all()
        )
        process_breakdown = {}
        for pt, cnt in rows:
            key = pt.value if hasattr(pt, "value") else str(pt)
            process_breakdown[key] = cnt
        
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
        try:
            log_audit_event(
                self.db,
                user_id=data.get("recorded_by") or process.operator_id,
                action="process.material.consumed",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"consumption_id": mc.id, "material_id": mc.material_id, "qty": mc.quantity, "unit": mc.unit}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=None,
                action="process.spec.bound",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"document_id": document_id, "version": document_version}
            )
        except Exception:
            pass
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
        try:
            log_audit_event(
                self.db,
                user_id=approver_id or verifier_id,
                action="process.released",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"release_id": record.id, "qty": released_qty, "unit": unit}
            )
        except Exception:
            pass
        return record

    def get_latest_release(self, process_id: int) -> Optional[ReleaseRecord]:
        return (
            self.db.query(ReleaseRecord)
            .filter(ReleaseRecord.process_id == process_id)
            .order_by(ReleaseRecord.signed_at.desc())
            .first()
        )

    # ===== ENHANCED PROCESS MONITORING AND SPC METHODS =====

    def create_control_chart(self, process_id: int, parameter_name: str, data: Dict[str, Any]) -> ProcessControlChart:
        """Create a new control chart for SPC monitoring - ISO 22000:2018 Clause 8.5"""
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")

        # Get historical data for control limit calculation
        historical_params = (
            self.db.query(ProcessParameter)
            .filter(
                ProcessParameter.process_id == process_id,
                ProcessParameter.parameter_name == parameter_name
            )
            .order_by(ProcessParameter.recorded_at.desc())
            .limit(data.get("sample_size", 50))
            .all()
        )

        if len(historical_params) < 5:
            raise ValueError("Insufficient historical data for control chart creation")

        # Calculate control limits
        values = [p.parameter_value for p in historical_params]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        # Calculate control limits (3-sigma by default)
        sigma_factor = data.get("sigma_factor", 3.0)
        upper_control_limit = mean_value + (sigma_factor * std_dev)
        lower_control_limit = mean_value - (sigma_factor * std_dev)

        # Warning limits (2-sigma)
        upper_warning_limit = mean_value + (2.0 * std_dev)
        lower_warning_limit = mean_value - (2.0 * std_dev)

        control_chart = ProcessControlChart(
            process_id=process_id,
            parameter_name=parameter_name,
            chart_type=data.get("chart_type", "X-bar"),
            sample_size=data.get("sample_size", 5),
            target_value=data.get("target_value", mean_value),
            upper_control_limit=upper_control_limit,
            lower_control_limit=lower_control_limit,
            upper_warning_limit=upper_warning_limit,
            lower_warning_limit=lower_warning_limit,
            specification_upper=data.get("specification_upper"),
            specification_lower=data.get("specification_lower"),
        )

        self.db.add(control_chart)
        self.db.commit()
        self.db.refresh(control_chart)

        # Create initial control points from historical data
        for param in historical_params:
            self._add_control_point(control_chart.id, param.parameter_value, param.id, param.recorded_at)

        try:
            log_audit_event(
                self.db,
                user_id=data.get("created_by"),
                action="control_chart.created",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"chart_id": control_chart.id, "parameter": parameter_name, "chart_type": control_chart.chart_type}
            )
        except Exception:
            pass

        return control_chart

    def _add_control_point(self, control_chart_id: int, measured_value: float, parameter_id: Optional[int] = None, timestamp: Optional[datetime] = None) -> ProcessControlPoint:
        """Add a data point to control chart and check for control violations"""
        control_chart = self.db.query(ProcessControlChart).filter(ProcessControlChart.id == control_chart_id).first()
        if not control_chart:
            raise ValueError("Control chart not found")

        # Create control point
        control_point = ProcessControlPoint(
            control_chart_id=control_chart_id,
            parameter_id=parameter_id,
            timestamp=timestamp or datetime.utcnow(),
            measured_value=measured_value,
        )

        # Check for control violations using Nelson rules
        violation_rule = self._check_nelson_rules(control_chart, measured_value)
        if violation_rule:
            control_point.is_out_of_control = True
            control_point.control_rule_violated = violation_rule
            
            # Create monitoring alert
            self._create_spc_alert(control_chart, measured_value, violation_rule)

        # Calculate additional statistics based on chart type
        if control_chart.chart_type in ["CUSUM", "EWMA"]:
            control_point = self._calculate_advanced_statistics(control_point, control_chart)

        self.db.add(control_point)
        self.db.commit()
        self.db.refresh(control_point)

        return control_point

    def _check_nelson_rules(self, control_chart: ProcessControlChart, value: float) -> Optional[str]:
        """Check Nelson rules for statistical process control"""
        # Rule 1: Point beyond 3-sigma control limits
        if value > control_chart.upper_control_limit or value < control_chart.lower_control_limit:
            return "Nelson_Rule_1_Beyond_3sigma"

        # Get recent points for trend analysis (Rules 2-8)
        recent_points = (
            self.db.query(ProcessControlPoint)
            .filter(ProcessControlPoint.control_chart_id == control_chart.id)
            .order_by(ProcessControlPoint.timestamp.desc())
            .limit(9)
            .all()
        )

        if len(recent_points) < 2:
            return None

        # Rule 2: 9 points in a row on same side of center line
        if len(recent_points) >= 9:
            all_above = all(p.measured_value > control_chart.target_value for p in recent_points[:9])
            all_below = all(p.measured_value < control_chart.target_value for p in recent_points[:9])
            if all_above or all_below:
                return "Nelson_Rule_2_Nine_Same_Side"

        # Rule 3: 6 points in a row steadily increasing or decreasing
        if len(recent_points) >= 6:
            values = [p.measured_value for p in recent_points[:6]]
            increasing = all(values[i] < values[i+1] for i in range(5))
            decreasing = all(values[i] > values[i+1] for i in range(5))
            if increasing or decreasing:
                return "Nelson_Rule_3_Six_Trend"

        # Rule 4: 14 points alternating up and down
        if len(recent_points) >= 14:
            values = [p.measured_value for p in recent_points[:14]]
            alternating = all(
                (values[i] > values[i+1] and values[i+1] < values[i+2]) or
                (values[i] < values[i+1] and values[i+1] > values[i+2])
                for i in range(12)
            )
            if alternating:
                return "Nelson_Rule_4_Fourteen_Alternating"

        # Rule 5: 2 out of 3 points beyond 2-sigma warning limits
        if len(recent_points) >= 3:
            beyond_warning = sum(
                1 for p in recent_points[:3]
                if p.measured_value > control_chart.upper_warning_limit or 
                   p.measured_value < control_chart.lower_warning_limit
            )
            if beyond_warning >= 2:
                return "Nelson_Rule_5_Two_of_Three_Beyond_2sigma"

        return None

    def _calculate_advanced_statistics(self, control_point: ProcessControlPoint, control_chart: ProcessControlChart) -> ProcessControlPoint:
        """Calculate CUSUM and EWMA statistics for advanced control charts"""
        if control_chart.chart_type == "CUSUM":
            # Get previous CUSUM value
            prev_point = (
                self.db.query(ProcessControlPoint)
                .filter(ProcessControlPoint.control_chart_id == control_chart.id)
                .order_by(ProcessControlPoint.timestamp.desc())
                .first()
            )
            prev_cusum = prev_point.cumulative_sum if prev_point else 0.0
            control_point.cumulative_sum = prev_cusum + (control_point.measured_value - control_chart.target_value)

        elif control_chart.chart_type == "EWMA":
            # Exponentially Weighted Moving Average (λ = 0.2 default)
            lambda_factor = 0.2
            prev_point = (
                self.db.query(ProcessControlPoint)
                .filter(ProcessControlPoint.control_chart_id == control_chart.id)
                .order_by(ProcessControlPoint.timestamp.desc())
                .first()
            )
            prev_ewma = prev_point.moving_average if prev_point else control_chart.target_value
            control_point.moving_average = (lambda_factor * control_point.measured_value) + ((1 - lambda_factor) * prev_ewma)

        return control_point

    def _create_spc_alert(self, control_chart: ProcessControlChart, value: float, rule: str):
        """Create monitoring alert for SPC violations"""
        severity_map = {
            "Nelson_Rule_1_Beyond_3sigma": "critical",
            "Nelson_Rule_2_Nine_Same_Side": "warning",
            "Nelson_Rule_3_Six_Trend": "warning",
            "Nelson_Rule_4_Fourteen_Alternating": "info",
            "Nelson_Rule_5_Two_of_Three_Beyond_2sigma": "warning"
        }

        alert = ProcessMonitoringAlert(
            process_id=control_chart.process_id,
            control_chart_id=control_chart.id,
            alert_type="control_limit",
            severity_level=severity_map.get(rule, "warning"),
            alert_title=f"SPC Violation: {rule}",
            alert_message=f"Parameter {control_chart.parameter_name} violated {rule}. Current value: {value:.3f}",
            parameter_name=control_chart.parameter_name,
            current_value=value,
            threshold_value=control_chart.upper_control_limit if value > control_chart.target_value else control_chart.lower_control_limit,
            control_rule=rule,
            auto_generated=True,
            requires_immediate_action=(rule == "Nelson_Rule_1_Beyond_3sigma"),
            # ISO 22000 impact assessment
            food_safety_impact=self._assess_food_safety_impact(control_chart.parameter_name),
            ccp_affected=self._is_critical_control_point(control_chart.parameter_name),
            corrective_action_required=True,
            verification_required=True,
        )

        self.db.add(alert)
        self.db.commit()

        try:
            log_audit_event(
                self.db,
                user_id=None,
                action="spc_alert.created",
                resource_type="production_process",
                resource_id=str(control_chart.process_id),
                details={"alert_id": alert.id, "rule": rule, "parameter": control_chart.parameter_name, "value": value}
            )
        except Exception:
            pass

    def _assess_food_safety_impact(self, parameter_name: str) -> bool:
        """Assess if parameter deviation impacts food safety - ISO 22000:2018"""
        critical_parameters = [
            "temperature", "time", "ph", "water_activity", "pressure", 
            "pasteurization", "sterilization", "cooling", "heating"
        ]
        return any(param in parameter_name.lower() for param in critical_parameters)

    def _is_critical_control_point(self, parameter_name: str) -> bool:
        """Determine if parameter is part of a Critical Control Point (CCP)"""
        ccp_parameters = [
            "pasteurization_temperature", "pasteurization_time", "cooling_temperature",
            "sterilization_temperature", "sterilization_time", "ph_control"
        ]
        return parameter_name.lower() in ccp_parameters

    def calculate_process_capability(self, process_id: int, parameter_name: str, data: Dict[str, Any]) -> ProcessCapabilityStudy:
        """Calculate process capability indices (Cp, Cpk) - ISO 22000:2018 requirements"""
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")

        period_start = data.get("period_start") or (datetime.utcnow() - timedelta(days=30))
        period_end = data.get("period_end") or datetime.utcnow()

        # Get parameter data for the study period
        parameters = (
            self.db.query(ProcessParameter)
            .filter(
                ProcessParameter.process_id == process_id,
                ProcessParameter.parameter_name == parameter_name,
                ProcessParameter.recorded_at >= period_start,
                ProcessParameter.recorded_at <= period_end
            )
            .order_by(ProcessParameter.recorded_at.asc())
            .all()
        )

        if len(parameters) < 30:
            raise ValueError("Insufficient data for capability study (minimum 30 points required)")

        values = [p.parameter_value for p in parameters]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)

        spec_upper = data.get("specification_upper")
        spec_lower = data.get("specification_lower")

        if not spec_upper or not spec_lower:
            raise ValueError("Specification limits required for capability study")

        # Calculate capability indices
        cp_index = (spec_upper - spec_lower) / (6 * std_dev) if std_dev > 0 else 0
        
        # Cpk considers process centering
        cpu = (spec_upper - mean_value) / (3 * std_dev) if std_dev > 0 else 0
        cpl = (mean_value - spec_lower) / (3 * std_dev) if std_dev > 0 else 0
        cpk_index = min(cpu, cpl)

        # Performance indices (uses actual spread vs. 6-sigma)
        pp_index = (spec_upper - spec_lower) / (6 * std_dev) if std_dev > 0 else 0
        ppk_index = cpk_index  # Same calculation for small samples

        # Process sigma level (DPMO based)
        defect_rate_ppm = self._calculate_defect_rate_ppm(values, spec_lower, spec_upper)
        process_sigma_level = self._calculate_sigma_level(defect_rate_ppm)

        # Capability assessment
        is_capable = cp_index >= 1.33 and cpk_index >= 1.33  # Industry standard

        capability_study = ProcessCapabilityStudy(
            process_id=process_id,
            parameter_name=parameter_name,
            study_period_start=period_start,
            study_period_end=period_end,
            sample_size=len(parameters),
            mean_value=mean_value,
            standard_deviation=std_dev,
            specification_upper=spec_upper,
            specification_lower=spec_lower,
            cp_index=cp_index,
            cpk_index=cpk_index,
            pp_index=pp_index,
            ppk_index=ppk_index,
            process_sigma_level=process_sigma_level,
            defect_rate_ppm=defect_rate_ppm,
            is_capable=is_capable,
            conducted_by=data.get("conducted_by"),
            approved_by=data.get("approved_by"),
            study_notes=data.get("study_notes"),
        )

        self.db.add(capability_study)
        self.db.commit()
        self.db.refresh(capability_study)

        try:
            log_audit_event(
                self.db,
                user_id=data.get("conducted_by"),
                action="capability_study.completed",
                resource_type="production_process",
                resource_id=str(process_id),
                details={
                    "study_id": capability_study.id,
                    "parameter": parameter_name,
                    "cp": cp_index,
                    "cpk": cpk_index,
                    "capable": is_capable
                }
            )
        except Exception:
            pass

        return capability_study

    def _calculate_defect_rate_ppm(self, values: List[float], spec_lower: float, spec_upper: float) -> float:
        """Calculate defect rate in parts per million"""
        out_of_spec = sum(1 for v in values if v < spec_lower or v > spec_upper)
        total = len(values)
        return (out_of_spec / total) * 1_000_000 if total > 0 else 0

    def _calculate_sigma_level(self, defect_rate_ppm: float) -> float:
        """Calculate process sigma level from defect rate"""
        if defect_rate_ppm <= 0:
            return 6.0  # Perfect process
        elif defect_rate_ppm >= 999_999:
            return 0.0  # Extremely poor process
        
        # Convert PPM to probability and calculate Z-score
        prob_defect = defect_rate_ppm / 1_000_000
        prob_good = 1 - prob_defect
        
        # Use inverse normal distribution (approximation)
        try:
            from scipy.stats import norm
            z_score = norm.ppf(prob_good)
            return max(0, min(6, z_score))
        except ImportError:
            # Fallback approximation
            if defect_rate_ppm <= 3.4:
                return 6.0
            elif defect_rate_ppm <= 233:
                return 5.0
            elif defect_rate_ppm <= 6210:
                return 4.0
            elif defect_rate_ppm <= 66807:
                return 3.0
            elif defect_rate_ppm <= 308537:
                return 2.0
            else:
                return 1.0

    # ===== YIELD ANALYSIS METHODS =====

    def create_yield_analysis_report(self, process_id: int, data: Dict[str, Any]) -> YieldAnalysisReport:
        """Create comprehensive yield analysis report - ISO 22000:2018 monitoring"""
        process = self.get_process(process_id)
        if not process:
            raise ValueError("Process not found")

        period_start = data.get("period_start") or (datetime.utcnow() - timedelta(days=7))
        period_end = data.get("period_end") or datetime.utcnow()

        # Gather yield data from the period
        yield_records = (
            self.db.query(YieldRecord)
            .filter(
                YieldRecord.process_id == process_id,
                YieldRecord.created_at >= period_start,
                YieldRecord.created_at <= period_end
            )
            .all()
        )

        if not yield_records:
            raise ValueError("No yield data found for the specified period")

        # Calculate aggregate quantities
        total_output = sum(y.output_qty for y in yield_records)
        total_expected = sum(y.expected_qty for y in yield_records if y.expected_qty)
        
        # Get input quantities from material consumption
        from app.models.production import MaterialConsumption
        material_consumptions = (
            self.db.query(MaterialConsumption)
            .filter(
                MaterialConsumption.process_id == process_id,
                MaterialConsumption.consumed_at >= period_start,
                MaterialConsumption.consumed_at <= period_end
            )
            .all()
        )
        total_input = sum(m.quantity for m in material_consumptions) or total_expected or total_output

        # Get defect/deviation data for quality calculations
        deviations = (
            self.db.query(ProcessDeviation)
            .filter(
                ProcessDeviation.process_id == process_id,
                ProcessDeviation.created_at >= period_start,
                ProcessDeviation.created_at <= period_end
            )
            .all()
        )

        # Calculate quality metrics
        conforming_output = data.get("conforming_output_quantity") or (total_output * 0.95)  # Assume 95% if not provided
        non_conforming = total_output - conforming_output
        rework_quantity = data.get("rework_quantity", 0.0)
        waste_quantity = data.get("waste_quantity", 0.0)

        # Calculate KPIs
        first_pass_yield = (conforming_output / total_output * 100) if total_output > 0 else 0
        overall_yield = (total_output / total_input * 100) if total_input > 0 else 0
        quality_rate = first_pass_yield
        rework_rate = (rework_quantity / total_output * 100) if total_output > 0 else 0
        waste_rate = (waste_quantity / total_input * 100) if total_input > 0 else 0

        # Perform trend analysis
        baseline_comparison = self._get_baseline_yield_comparison(process_id, period_start)
        trend_analysis = self._calculate_yield_trends(process_id, period_end)

        yield_report = YieldAnalysisReport(
            process_id=process_id,
            analysis_period_start=period_start,
            analysis_period_end=period_end,
            total_input_quantity=total_input,
            total_output_quantity=total_output,
            conforming_output_quantity=conforming_output,
            non_conforming_quantity=non_conforming,
            rework_quantity=rework_quantity,
            waste_quantity=waste_quantity,
            unit=yield_records[0].unit if yield_records else "kg",
            first_pass_yield=first_pass_yield,
            overall_yield=overall_yield,
            quality_rate=quality_rate,
            rework_rate=rework_rate,
            waste_rate=waste_rate,
            analysis_method=data.get("analysis_method", "standard"),
            baseline_comparison=baseline_comparison,
            trend_analysis=trend_analysis,
            analyzed_by=data.get("analyzed_by"),
            reviewed_by=data.get("reviewed_by"),
            approved_by=data.get("approved_by"),
        )

        self.db.add(yield_report)
        self.db.commit()
        self.db.refresh(yield_report)

        # Create defect categorization (Pareto analysis)
        if deviations:
            self._create_defect_categories(yield_report.id, deviations, total_output)

        try:
            log_audit_event(
                self.db,
                user_id=data.get("analyzed_by"),
                action="yield_analysis.completed",
                resource_type="production_process",
                resource_id=str(process_id),
                details={
                    "report_id": yield_report.id,
                    "fpy": first_pass_yield,
                    "overall_yield": overall_yield,
                    "period_days": (period_end - period_start).days
                }
            )
        except Exception:
            pass

        return yield_report

    def _get_baseline_yield_comparison(self, process_id: int, current_period_start: datetime) -> Dict[str, Any]:
        """Compare current yield performance with historical baseline"""
        # Get previous period (same duration)
        period_duration = datetime.utcnow() - current_period_start
        baseline_end = current_period_start
        baseline_start = baseline_end - period_duration

        baseline_report = (
            self.db.query(YieldAnalysisReport)
            .filter(
                YieldAnalysisReport.process_id == process_id,
                YieldAnalysisReport.analysis_period_start >= baseline_start,
                YieldAnalysisReport.analysis_period_end <= baseline_end
            )
            .order_by(YieldAnalysisReport.created_at.desc())
            .first()
        )

        if not baseline_report:
            return {"baseline_available": False}

        return {
            "baseline_available": True,
            "baseline_fpy": baseline_report.first_pass_yield,
            "baseline_overall_yield": baseline_report.overall_yield,
            "baseline_quality_rate": baseline_report.quality_rate,
            "baseline_waste_rate": baseline_report.waste_rate,
            "comparison_period": f"{baseline_start.date()} to {baseline_end.date()}"
        }

    def _calculate_yield_trends(self, process_id: int, end_date: datetime) -> Dict[str, Any]:
        """Calculate yield trends over last 90 days"""
        trend_start = end_date - timedelta(days=90)
        
        reports = (
            self.db.query(YieldAnalysisReport)
            .filter(
                YieldAnalysisReport.process_id == process_id,
                YieldAnalysisReport.analysis_period_start >= trend_start
            )
            .order_by(YieldAnalysisReport.analysis_period_start.asc())
            .all()
        )

        if len(reports) < 3:
            return {"trend_available": False}

        # Calculate trends
        fpy_values = [r.first_pass_yield for r in reports]
        overall_yield_values = [r.overall_yield for r in reports]
        
        fpy_trend = self._calculate_trend_direction(fpy_values)
        yield_trend = self._calculate_trend_direction(overall_yield_values)

        return {
            "trend_available": True,
            "fpy_trend": fpy_trend,
            "overall_yield_trend": yield_trend,
            "data_points": len(reports),
            "period_days": 90,
            "latest_fpy": fpy_values[-1],
            "fpy_change": fpy_values[-1] - fpy_values[0] if len(fpy_values) > 1 else 0
        }

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction using linear regression slope"""
        if len(values) < 2:
            return "stable"
        
        x = list(range(len(values)))
        y = values
        
        # Simple linear regression
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "decreasing"
        else:
            return "stable"

    def _create_defect_categories(self, yield_report_id: int, deviations: List[ProcessDeviation], total_output: float):
        """Create defect categorization for Pareto analysis"""
        # Group deviations by type
        defect_groups = {}
        for deviation in deviations:
            defect_type = deviation.deviation_type
            if defect_type not in defect_groups:
                defect_groups[defect_type] = {
                    "count": 0,
                    "severity_sum": 0,
                    "descriptions": [],
                    "critical": False
                }
            
            defect_groups[defect_type]["count"] += 1
            defect_groups[defect_type]["severity_sum"] += self._severity_to_weight(deviation.severity)
            defect_groups[defect_type]["descriptions"].append(deviation.impact_assessment or "")
            defect_groups[defect_type]["critical"] = defect_groups[defect_type]["critical"] or (deviation.severity == "critical")

        # Sort by count (Pareto principle)
        sorted_defects = sorted(defect_groups.items(), key=lambda x: x[1]["count"], reverse=True)
        
        total_defects = sum(group["count"] for _, group in sorted_defects)
        cumulative_percentage = 0

        for defect_type, group_data in sorted_defects:
            percentage = (group_data["count"] / total_defects * 100) if total_defects > 0 else 0
            cumulative_percentage += percentage
            
            # Estimate defect quantity (assuming 1 defect affects 1 unit on average)
            defect_quantity = group_data["count"]  # Simplified assumption
            
            defect_category = YieldDefectCategory(
                yield_report_id=yield_report_id,
                defect_type=defect_type,
                defect_description="; ".join(set(group_data["descriptions"][:3])),  # Top 3 unique descriptions
                defect_count=group_data["count"],
                defect_quantity=defect_quantity,
                percentage_of_total=percentage,
                cumulative_percentage=cumulative_percentage,
                is_critical_to_quality=group_data["critical"],
                root_cause_category=self._categorize_root_cause(defect_type),
                corrective_action_required=group_data["critical"] or percentage > 10,  # Focus on critical or >10%
            )
            
            self.db.add(defect_category)

        self.db.commit()

    def _severity_to_weight(self, severity: str) -> int:
        """Convert severity to numerical weight"""
        weights = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return weights.get(severity, 1)

    def _categorize_root_cause(self, defect_type: str) -> str:
        """Categorize defect into root cause category (5Ms)"""
        defect_lower = defect_type.lower()
        
        if any(term in defect_lower for term in ["operator", "skill", "training", "human"]):
            return "man"
        elif any(term in defect_lower for term in ["equipment", "machine", "mechanical", "calibration"]):
            return "machine"
        elif any(term in defect_lower for term in ["material", "ingredient", "raw", "supplier"]):
            return "material"
        elif any(term in defect_lower for term in ["process", "procedure", "method", "recipe"]):
            return "method"
        elif any(term in defect_lower for term in ["environment", "temperature", "humidity", "contamination"]):
            return "environment"
        else:
            return "unknown"

    def get_process_monitoring_analytics(self, process_type: Optional[ProductProcessType] = None) -> Dict[str, Any]:
        """Get comprehensive process monitoring analytics dashboard"""
        base_analytics = self.get_enhanced_analytics(process_type)
        
        # SPC Analytics
        control_chart_query = self.db.query(ProcessControlChart)
        if process_type:
            control_chart_query = control_chart_query.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        active_charts = control_chart_query.filter(ProcessControlChart.is_active == True).count()
        
        # Out of control statistics
        out_of_control_points = (
            self.db.query(ProcessControlPoint)
            .join(ProcessControlChart)
            .filter(ProcessControlPoint.is_out_of_control == True)
        )
        if process_type:
            out_of_control_points = out_of_control_points.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        ooc_count = out_of_control_points.count()
        
        # Capability studies
        capability_query = self.db.query(ProcessCapabilityStudy)
        if process_type:
            capability_query = capability_query.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        capability_studies = capability_query.all()
        capable_processes = sum(1 for study in capability_studies if study.is_capable)
        avg_cpk = statistics.mean([study.cpk_index for study in capability_studies if study.cpk_index]) if capability_studies else 0
        
        # Yield analytics
        yield_query = self.db.query(YieldAnalysisReport)
        if process_type:
            yield_query = yield_query.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        recent_yields = yield_query.filter(YieldAnalysisReport.created_at >= datetime.utcnow() - timedelta(days=30)).all()
        avg_fpy = statistics.mean([y.first_pass_yield for y in recent_yields]) if recent_yields else 0
        avg_overall_yield = statistics.mean([y.overall_yield for y in recent_yields]) if recent_yields else 0
        
        # Alert statistics
        alert_query = self.db.query(ProcessMonitoringAlert)
        if process_type:
            alert_query = alert_query.join(ProductionProcess).filter(ProductionProcess.process_type == process_type)
        
        active_alerts = alert_query.filter(ProcessMonitoringAlert.resolved == False).count()
        critical_alerts = alert_query.filter(
            ProcessMonitoringAlert.resolved == False,
            ProcessMonitoringAlert.severity_level == "critical"
        ).count()
        
        return {
            **base_analytics,
            "spc_metrics": {
                "active_control_charts": active_charts,
                "out_of_control_points": ooc_count,
                "capability_studies_count": len(capability_studies),
                "capable_processes": capable_processes,
                "average_cpk": round(avg_cpk, 3)
            },
            "yield_metrics": {
                "average_first_pass_yield": round(avg_fpy, 2),
                "average_overall_yield": round(avg_overall_yield, 2),
                "yield_reports_count": len(recent_yields)
            },
            "alert_metrics": {
                "active_alerts": active_alerts,
                "critical_alerts": critical_alerts,
                "food_safety_alerts": alert_query.filter(
                    ProcessMonitoringAlert.resolved == False,
                    ProcessMonitoringAlert.food_safety_impact == True
                ).count()
            }
        }

    # =================== FSM (Finite State Machine) Methods ===================

    def create_process_with_stages(self, batch_id: int, process_type: ProductProcessType, 
                                   operator_id: Optional[int], spec: Dict[str, Any],
                                   stages_data: List[Dict[str, Any]], notes: Optional[str] = None) -> ProductionProcess:
        """Create a new production process with stages for FSM management"""
        from app.models.production import ProcessStage, StageStatus
        
        # Validate batch exists
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Create the process in DRAFT status
        process = ProductionProcess(
            batch_id=batch_id,
            process_type=process_type,
            operator_id=operator_id,
            spec=spec,
            status=ProcessStatus.DRAFT,
            notes=notes
        )
        self.db.add(process)
        self.db.flush()  # Get the process ID
        
        # Create stages
        for stage_data in stages_data:
            stage = ProcessStage(
                process_id=process.id,
                stage_name=stage_data['stage_name'],
                stage_description=stage_data.get('stage_description'),
                sequence_order=stage_data['sequence_order'],
                status=StageStatus.PENDING,
                is_critical_control_point=stage_data.get('is_critical_control_point', False),
                is_operational_prp=stage_data.get('is_operational_prp', False),
                planned_start_time=stage_data.get('planned_start_time'),
                planned_end_time=stage_data.get('planned_end_time'),
                duration_minutes=stage_data.get('duration_minutes'),
                completion_criteria=stage_data.get('completion_criteria'),
                auto_advance=stage_data.get('auto_advance', False),
                requires_approval=stage_data.get('requires_approval', False),
                assigned_operator_id=stage_data.get('assigned_operator_id'),
                stage_notes=stage_data.get('stage_notes')
            )
            self.db.add(stage)
        
        self.db.commit()
        self.db.refresh(process)
        
        # Log audit event
        try:
            log_audit_event(
                self.db,
                user_id=operator_id,
                action="process.created_with_stages",
                resource_type="production_process",
                resource_id=str(process.id),
                details={
                    "batch_id": batch_id,
                    "type": process_type.value,
                    "stages_count": len(stages_data)
                }
            )
        except Exception:
            pass
        
        return process

    def start_process(self, process_id: int, operator_id: Optional[int] = None, 
                     start_notes: Optional[str] = None) -> ProductionProcess:
        """Start a process and activate the first stage"""
        from app.models.production import ProcessStage, StageStatus, StageTransition
        
        process = self.db.query(ProductionProcess).filter(ProductionProcess.id == process_id).first()
        if not process:
            raise ValueError("Process not found")
        
        if process.status != ProcessStatus.DRAFT:
            raise ValueError(f"Process cannot be started. Current status: {process.status}")
        
        # Get the first stage
        first_stage = self.db.query(ProcessStage).filter(
            ProcessStage.process_id == process_id,
            ProcessStage.sequence_order == 1
        ).first()
        
        if not first_stage:
            raise ValueError("No stages defined for this process")
        
        # Update process status and start time
        process.status = ProcessStatus.IN_PROGRESS
        process.start_time = datetime.utcnow()
        if operator_id:
            process.operator_id = operator_id
        if start_notes:
            process.notes = (process.notes or "") + f"\nStart notes: {start_notes}"
        
        # Activate first stage
        first_stage.status = StageStatus.IN_PROGRESS
        first_stage.actual_start_time = datetime.utcnow()
        if operator_id:
            first_stage.assigned_operator_id = operator_id
        
        # Create transition record
        transition = StageTransition(
            process_id=process_id,
            from_stage_id=None,  # Initial transition
            to_stage_id=first_stage.id,
            transition_type="normal",
            transition_reason="Process started",
            initiated_by=operator_id or process.operator_id,
            transition_timestamp=datetime.utcnow(),
            prerequisites_met=True,
            transition_notes=start_notes
        )
        self.db.add(transition)
        
        self.db.commit()
        self.db.refresh(process)
        
        # Log audit event
        try:
            log_audit_event(
                self.db,
                user_id=operator_id or process.operator_id,
                action="process.started",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"first_stage_id": first_stage.id}
            )
        except Exception:
            pass
        
        return process

    def transition_to_next_stage(self, process_id: int, current_stage_id: int, 
                                user_id: int, transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition from current stage to the next stage"""
        from app.models.production import ProcessStage, StageStatus, StageTransition
        
        process = self.db.query(ProductionProcess).filter(ProductionProcess.id == process_id).first()
        if not process:
            raise ValueError("Process not found")
        
        if process.status != ProcessStatus.IN_PROGRESS:
            raise ValueError(f"Process is not in progress. Current status: {process.status}")
        
        current_stage = self.db.query(ProcessStage).filter(
            ProcessStage.id == current_stage_id,
            ProcessStage.process_id == process_id
        ).first()
        
        if not current_stage:
            raise ValueError("Current stage not found")
        
        if current_stage.status != StageStatus.IN_PROGRESS:
            raise ValueError(f"Current stage is not in progress. Current status: {current_stage.status}")
        
        # Validate stage completion requirements
        if not self._validate_stage_completion(current_stage):
            raise ValueError("Stage completion requirements not met")
        
        # Complete current stage
        current_stage.status = StageStatus.COMPLETED
        current_stage.actual_end_time = datetime.utcnow()
        current_stage.completed_by_id = user_id
        current_stage.deviations_recorded = transition_data.get('deviations_recorded')
        current_stage.corrective_actions = transition_data.get('corrective_actions')
        
        # Find next stage
        next_stage = self.db.query(ProcessStage).filter(
            ProcessStage.process_id == process_id,
            ProcessStage.sequence_order == current_stage.sequence_order + 1
        ).first()
        
        if next_stage:
            # Start next stage
            next_stage.status = StageStatus.IN_PROGRESS
            next_stage.actual_start_time = datetime.utcnow()
            if transition_data.get('assign_operator_to_next'):
                next_stage.assigned_operator_id = user_id
            
            # Create transition record
            transition = StageTransition(
                process_id=process_id,
                from_stage_id=current_stage.id,
                to_stage_id=next_stage.id,
                transition_type=transition_data.get('transition_type', 'normal'),
                transition_reason=transition_data.get('transition_reason'),
                initiated_by=user_id,
                transition_timestamp=datetime.utcnow(),
                prerequisites_met=transition_data.get('prerequisites_met', True),
                prerequisite_validation=transition_data.get('prerequisite_validation'),
                transition_notes=transition_data.get('transition_notes')
            )
            self.db.add(transition)
            
            result = {
                "completed_stage": current_stage,
                "next_stage": next_stage,
                "transition": transition,
                "process_completed": False
            }
        else:
            # No more stages - complete the process
            process.status = ProcessStatus.COMPLETED
            process.end_time = datetime.utcnow()
            
            result = {
                "completed_stage": current_stage,
                "next_stage": None,
                "transition": None,
                "process_completed": True
            }
        
        self.db.commit()
        
        # Log audit event
        try:
            log_audit_event(
                self.db,
                user_id=user_id,
                action="stage.transitioned",
                resource_type="process_stage",
                resource_id=str(current_stage.id),
                details={
                    "process_id": process_id,
                    "next_stage_id": next_stage.id if next_stage else None,
                    "process_completed": result["process_completed"]
                }
            )
        except Exception:
            pass
        
        return result

    def _validate_stage_completion(self, stage) -> bool:
        """Validate that a stage meets all completion requirements"""
        from app.models.production import StageMonitoringRequirement, StageMonitoringLog
        
        # Check if all mandatory monitoring requirements are fulfilled
        if stage.completion_criteria:
            criteria = stage.completion_criteria
            
            # Check monitoring requirements
            if criteria.get('mandatory_monitoring_required', True):
                mandatory_requirements = self.db.query(
                    StageMonitoringRequirement
                ).filter(
                    StageMonitoringRequirement.stage_id == stage.id,
                    StageMonitoringRequirement.is_mandatory == True
                ).all()
                
                for requirement in mandatory_requirements:
                    # Check if there are monitoring logs for this requirement
                    log_count = self.db.query(StageMonitoringLog).filter(
                        StageMonitoringLog.stage_id == stage.id,
                        StageMonitoringLog.requirement_id == requirement.id
                    ).count()
                    
                    if log_count == 0:
                        return False
            
            # Check minimum duration
            if criteria.get('minimum_duration_minutes'):
                min_duration = criteria['minimum_duration_minutes']
                if stage.actual_start_time and stage.actual_end_time:
                    duration = (stage.actual_end_time - stage.actual_start_time).total_seconds() / 60
                    if duration < min_duration:
                        return False
            
        return True

    def add_stage_monitoring_requirement(self, stage_id: int, requirement_data: Dict[str, Any], 
                                       created_by: int) -> 'StageMonitoringRequirement':
        """Add a monitoring requirement to a stage"""
        from app.models.production import StageMonitoringRequirement, MonitoringRequirementType, ProcessStage
        
        # Validate stage exists
        stage = self.db.query(ProcessStage).filter(ProcessStage.id == stage_id).first()
        if not stage:
            raise ValueError("Stage not found")
        
        requirement = StageMonitoringRequirement(
            stage_id=stage_id,
            requirement_name=requirement_data['requirement_name'],
            requirement_type=MonitoringRequirementType(requirement_data['requirement_type']),
            description=requirement_data.get('description'),
            is_critical_limit=requirement_data.get('is_critical_limit', False),
            is_operational_limit=requirement_data.get('is_operational_limit', False),
            target_value=requirement_data.get('target_value'),
            tolerance_min=requirement_data.get('tolerance_min'),
            tolerance_max=requirement_data.get('tolerance_max'),
            unit_of_measure=requirement_data.get('unit_of_measure'),
            monitoring_frequency=requirement_data.get('monitoring_frequency'),
            is_mandatory=requirement_data.get('is_mandatory', True),
            equipment_required=requirement_data.get('equipment_required'),
            measurement_method=requirement_data.get('measurement_method'),
            calibration_required=requirement_data.get('calibration_required', False),
            record_keeping_required=requirement_data.get('record_keeping_required', True),
            verification_required=requirement_data.get('verification_required', False),
            regulatory_reference=requirement_data.get('regulatory_reference'),
            created_by=created_by
        )
        
        self.db.add(requirement)
        self.db.commit()
        self.db.refresh(requirement)
        
        return requirement

    def log_stage_monitoring(self, stage_id: int, monitoring_data: Dict[str, Any], 
                           recorded_by: int) -> 'StageMonitoringLog':
        """Log monitoring data for a stage"""
        from app.models.production import StageMonitoringLog, StageMonitoringRequirement, ProcessStage, StageStatus
        
        # Validate stage exists and is in progress
        stage = self.db.query(ProcessStage).filter(ProcessStage.id == stage_id).first()
        if not stage:
            raise ValueError("Stage not found")
        
        if stage.status != StageStatus.IN_PROGRESS:
            raise ValueError(f"Cannot log monitoring for stage not in progress. Current status: {stage.status}")
        
        # Validate requirement if provided
        requirement_id = monitoring_data.get('requirement_id')
        requirement = None
        if requirement_id:
            requirement = self.db.query(StageMonitoringRequirement).filter(
                StageMonitoringRequirement.id == requirement_id,
                StageMonitoringRequirement.stage_id == stage_id
            ).first()
            if not requirement:
                raise ValueError("Monitoring requirement not found for this stage")
        
        # Create monitoring log
        log = StageMonitoringLog(
            stage_id=stage_id,
            requirement_id=requirement_id,
            monitoring_timestamp=monitoring_data.get('monitoring_timestamp', datetime.utcnow()),
            measured_value=monitoring_data.get('measured_value'),
            measured_text=monitoring_data.get('measured_text'),
            recorded_by=recorded_by,
            equipment_used=monitoring_data.get('equipment_used'),
            measurement_method=monitoring_data.get('measurement_method'),
            equipment_calibration_date=monitoring_data.get('equipment_calibration_date'),
            notes=monitoring_data.get('notes'),
            corrective_action_taken=monitoring_data.get('corrective_action_taken'),
            follow_up_required=monitoring_data.get('follow_up_required', False),
            regulatory_requirement_met=monitoring_data.get('regulatory_requirement_met', True),
            iso_clause_reference=monitoring_data.get('iso_clause_reference'),
            pass_fail_status=monitoring_data.get('pass_fail_status'),
            deviation_severity=monitoring_data.get('deviation_severity')
        )
        
        # Calculate if within limits if we have a requirement with limits
        if requirement and log.measured_value is not None:
            is_within_limits = True
            if requirement.tolerance_min is not None and log.measured_value < requirement.tolerance_min:
                is_within_limits = False
            if requirement.tolerance_max is not None and log.measured_value > requirement.tolerance_max:
                is_within_limits = False
            log.is_within_limits = is_within_limits
            
            # Set pass/fail status if not explicitly provided
            if not log.pass_fail_status:
                log.pass_fail_status = "pass" if is_within_limits else "fail"
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        # Create alerts for critical deviations
        if log.pass_fail_status == "fail" and requirement and requirement.is_critical_limit:
            self._create_critical_monitoring_alert(log, requirement)
        
        # Log audit event
        try:
            log_audit_event(
                self.db,
                user_id=recorded_by,
                action="stage.monitoring.logged",
                resource_type="stage_monitoring_log",
                resource_id=str(log.id),
                details={
                    "stage_id": stage_id,
                    "requirement_id": requirement_id,
                    "within_limits": log.is_within_limits,
                    "pass_fail": log.pass_fail_status
                }
            )
        except Exception:
            pass
        
        return log

    def _create_critical_monitoring_alert(self, log: 'StageMonitoringLog', 
                                        requirement: 'StageMonitoringRequirement'):
        """Create an alert for critical monitoring deviations"""
        from app.models.production import ProcessMonitoringAlert
        
        alert = ProcessMonitoringAlert(
            process_id=log.stage.process_id,
            alert_type="critical_limit_exceeded",
            severity_level="critical",
            alert_title=f"Critical Limit Exceeded: {requirement.requirement_name}",
            alert_message=f"Stage '{log.stage.stage_name}' monitoring requirement '{requirement.requirement_name}' "
                         f"exceeded critical limits. Measured: {log.measured_value} {requirement.unit_of_measure or ''}",
            parameter_name=requirement.requirement_name,
            current_value=log.measured_value,
            threshold_value=requirement.tolerance_max or requirement.tolerance_min,
            auto_generated=True,
            requires_immediate_action=True,
            food_safety_impact=requirement.is_critical_limit,
            ccp_affected=requirement.is_critical_limit,
            corrective_action_required=True,
            verification_required=True
        )
        
        self.db.add(alert)

    def get_process_with_stages(self, process_id: int) -> Optional[ProductionProcess]:
        """Get a process with all its stages and monitoring data"""
        from sqlalchemy.orm import selectinload
        from app.models.production import ProcessStage
        
        process = self.db.query(ProductionProcess).options(
            selectinload(ProductionProcess.stages).selectinload(ProcessStage.monitoring_requirements),
            selectinload(ProductionProcess.stages).selectinload(ProcessStage.monitoring_logs),
            selectinload(ProductionProcess.stages).selectinload(ProcessStage.stage_transitions)
        ).filter(ProductionProcess.id == process_id).first()
        
        return process

    def get_stage_monitoring_logs(self, stage_id: int) -> List['StageMonitoringLog']:
        """Get all monitoring logs for a stage"""
        from app.models.production import StageMonitoringLog
        
        return self.db.query(StageMonitoringLog).filter(
            StageMonitoringLog.stage_id == stage_id
        ).order_by(StageMonitoringLog.monitoring_timestamp.desc()).all()

    def get_process_summary(self, process_id: int) -> Dict[str, Any]:
        """Get a summary of the process including progress and quality metrics"""
        from app.models.production import StageStatus, ProcessMonitoringAlert
        
        process = self.get_process_with_stages(process_id)
        if not process:
            raise ValueError("Process not found")
        
        total_stages = len(process.stages)
        completed_stages = len([s for s in process.stages if s.status == StageStatus.COMPLETED])
        
        current_stage = next((s for s in process.stages if s.status == StageStatus.IN_PROGRESS), None)
        
        # Calculate progress percentage
        progress = (completed_stages / total_stages * 100) if total_stages > 0 else 0
        
        # Count deviations and alerts
        deviations_count = sum(len([log for log in stage.monitoring_logs if log.pass_fail_status == "fail"]) 
                             for stage in process.stages)
        
        # Count critical alerts
        critical_alerts_count = self.db.query(ProcessMonitoringAlert).filter(
            ProcessMonitoringAlert.process_id == process_id,
            ProcessMonitoringAlert.severity_level == "critical",
            ProcessMonitoringAlert.resolved == False
        ).count()
        
        return {
            "id": process.id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value,
            "status": process.status.value,
            "start_time": process.start_time,
            "end_time": process.end_time,
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "current_stage_name": current_stage.stage_name if current_stage else None,
            "current_stage_status": current_stage.status.value if current_stage else None,
            "progress_percentage": round(progress, 2),
            "deviations_count": deviations_count,
            "critical_alerts_count": critical_alerts_count
        }

