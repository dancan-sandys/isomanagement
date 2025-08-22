from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.production import (
    ProductionProcess, ProcessStep, ProcessLog, YieldRecord, ColdRoomTransfer, AgingRecord,
    ProcessParameter, ProcessDeviation, ProcessAlert, ProductSpecification, ProcessTemplate,
    ProductProcessType, ProcessStatus, StepType, LogEvent
)
from app.models.traceability import Batch, BatchStatus, BatchType


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
            created_by=parameter_data.get("recorded_by"),
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
        
        return {
            **base_analytics,
            "total_deviations": total_deviations,
            "critical_deviations": critical_deviations,
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged_alerts,
            "process_type_breakdown": process_breakdown,
        }

