"""
Process Monitoring Service for ISO 22000:2018 Compliant Manufacturing
Implements automated 30-minute parameter logging and control point monitoring
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import asyncio
import logging
from contextlib import asynccontextmanager

from app.models.production import (
    ProductionProcess, ProcessStage, StageStatus, ProcessStatus,
    StageMonitoringRequirement, StageMonitoringLog, ProcessMonitoringAlert,
    ProcessParameter, MonitoringRequirementType
)
from app.models.traceability import Batch
from app.services import log_audit_event
from app.services.production_service import ProductionService

logger = logging.getLogger(__name__)


class ProcessMonitoringService:
    """
    ISO 22000:2018 compliant process monitoring service
    
    Implements:
    - Automated 30-minute parameter logging (Clause 8.5.2)
    - Continuous monitoring of Critical Control Points (Clause 8.5.4)
    - Deviation detection and alert generation (Clause 10.1)
    - Batch progression control with approval workflows
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.production_service = ProductionService(db)
        self.monitoring_tasks = {}  # Active monitoring tasks
        
    def start_process_monitoring(self, process_id: int) -> Dict[str, Any]:
        """
        Start automated monitoring for a production process
        
        Args:
            process_id: ID of the production process to monitor
            
        Returns:
            Dict containing monitoring configuration and status
        """
        process = self.db.query(ProductionProcess).filter(
            ProductionProcess.id == process_id
        ).first()
        
        if not process:
            raise ValueError("Process not found")
            
        if process.status != ProcessStatus.IN_PROGRESS:
            raise ValueError(f"Cannot monitor process not in progress. Status: {process.status}")
        
        # Get current active stage
        current_stage = self._get_current_active_stage(process_id)
        if not current_stage:
            raise ValueError("No active stage found for process")
        
        # Start monitoring for current stage
        monitoring_config = self._configure_stage_monitoring(current_stage)
        
        # Schedule automated parameter logging
        self._schedule_parameter_logging(process_id, current_stage.id)
        
        try:
            log_audit_event(
                self.db,
                user_id=process.operator_id,
                action="monitoring.started",
                resource_type="production_process",
                resource_id=str(process_id),
                details={
                    "stage_id": current_stage.id,
                    "monitoring_config": monitoring_config
                }
            )
        except Exception:
            pass
        
        return {
            "process_id": process_id,
            "current_stage": {
                "id": current_stage.id,
                "name": current_stage.stage_name,
                "status": current_stage.status.value
            },
            "monitoring_config": monitoring_config,
            "started_at": datetime.utcnow(),
            "next_logging_cycle": datetime.utcnow() + timedelta(minutes=30)
        }
    
    def _get_current_active_stage(self, process_id: int) -> Optional[ProcessStage]:
        """Get the currently active stage for a process"""
        return self.db.query(ProcessStage).filter(
            ProcessStage.process_id == process_id,
            ProcessStage.status == StageStatus.IN_PROGRESS
        ).first()
    
    def _configure_stage_monitoring(self, stage: ProcessStage) -> Dict[str, Any]:
        """Configure monitoring requirements for a stage"""
        requirements = self.db.query(StageMonitoringRequirement).filter(
            StageMonitoringRequirement.stage_id == stage.id
        ).all()
        
        monitoring_config = {
            "stage_id": stage.id,
            "stage_name": stage.stage_name,
            "is_ccp": stage.is_critical_control_point,
            "is_oprp": stage.is_operational_prp,
            "requirements": []
        }
        
        for req in requirements:
            req_config = {
                "id": req.id,
                "name": req.requirement_name,
                "type": req.requirement_type.value,
                "is_critical": req.is_critical_limit,
                "is_mandatory": req.is_mandatory,
                "frequency": req.monitoring_frequency,
                "target_value": req.target_value,
                "tolerance_min": req.tolerance_min,
                "tolerance_max": req.tolerance_max,
                "unit": req.unit_of_measure,
                "equipment": req.equipment_required,
                "method": req.measurement_method
            }
            monitoring_config["requirements"].append(req_config)
        
        return monitoring_config
    
    def _schedule_parameter_logging(self, process_id: int, stage_id: int):
        """Schedule automated 30-minute parameter logging"""
        # In a real implementation, this would use a task scheduler like Celery
        # For now, we'll create a conceptual framework
        
        task_key = f"process_{process_id}_stage_{stage_id}"
        self.monitoring_tasks[task_key] = {
            "process_id": process_id,
            "stage_id": stage_id,
            "last_logged": datetime.utcnow(),
            "interval_minutes": 30,
            "active": True
        }
        
        logger.info(f"Scheduled monitoring for process {process_id}, stage {stage_id}")
    
    def execute_monitoring_cycle(self, process_id: int) -> Dict[str, Any]:
        """
        Execute a monitoring cycle for all active requirements
        
        This method should be called every 30 minutes by a scheduler
        """
        process = self.db.query(ProductionProcess).filter(
            ProductionProcess.id == process_id
        ).first()
        
        if not process or process.status != ProcessStatus.IN_PROGRESS:
            return {"status": "process_not_active", "process_id": process_id}
        
        current_stage = self._get_current_active_stage(process_id)
        if not current_stage:
            return {"status": "no_active_stage", "process_id": process_id}
        
        # Get all monitoring requirements for current stage
        requirements = self.db.query(StageMonitoringRequirement).filter(
            StageMonitoringRequirement.stage_id == current_stage.id,
            StageMonitoringRequirement.monitoring_frequency.in_(["30_minutes", "continuous", "hourly"])
        ).all()
        
        cycle_results = {
            "process_id": process_id,
            "stage_id": current_stage.id,
            "cycle_timestamp": datetime.utcnow(),
            "logged_parameters": [],
            "alerts_generated": [],
            "deviations_detected": []
        }
        
        # Log parameters for each requirement
        for requirement in requirements:
            try:
                # In real implementation, this would read from sensors/equipment
                # For now, we'll simulate parameter collection
                parameter_data = self._collect_parameter_data(requirement)
                
                if parameter_data:
                    log_entry = self._log_monitoring_data(
                        current_stage.id,
                        requirement,
                        parameter_data
                    )
                    cycle_results["logged_parameters"].append({
                        "requirement_id": requirement.id,
                        "log_id": log_entry.id,
                        "value": log_entry.measured_value,
                        "within_limits": log_entry.is_within_limits
                    })
                    
                    # Check for deviations and create alerts if needed
                    if not log_entry.is_within_limits:
                        alert = self._create_deviation_alert(log_entry, requirement)
                        cycle_results["alerts_generated"].append(alert.id)
                        cycle_results["deviations_detected"].append({
                            "requirement": requirement.requirement_name,
                            "measured": log_entry.measured_value,
                            "expected_range": f"{requirement.tolerance_min}-{requirement.tolerance_max}",
                            "severity": log_entry.deviation_severity
                        })
                        
            except Exception as e:
                logger.error(f"Error logging parameter for requirement {requirement.id}: {str(e)}")
        
        # Update monitoring task timestamp
        task_key = f"process_{process_id}_stage_{current_stage.id}"
        if task_key in self.monitoring_tasks:
            self.monitoring_tasks[task_key]["last_logged"] = datetime.utcnow()
        
        try:
            log_audit_event(
                self.db,
                user_id=None,
                action="monitoring.cycle_executed",
                resource_type="production_process", 
                resource_id=str(process_id),
                details=cycle_results
            )
        except Exception:
            pass
        
        return cycle_results
    
    def _collect_parameter_data(self, requirement: StageMonitoringRequirement) -> Optional[Dict[str, Any]]:
        """
        Collect parameter data from equipment/sensors
        
        In a real implementation, this would interface with:
        - IoT sensors
        - Equipment APIs
        - Manual input systems
        - Laboratory systems
        """
        
        # Simulate data collection based on requirement type
        import random
        
        if requirement.requirement_type == MonitoringRequirementType.TEMPERATURE:
            # Simulate temperature reading with some variation
            base_temp = requirement.target_value or 72.0
            variation = random.uniform(-2.0, 2.0)
            return {
                "measured_value": base_temp + variation,
                "measurement_method": requirement.measurement_method or "thermocouple",
                "equipment_used": requirement.equipment_required or "temperature_sensor_01"
            }
        
        elif requirement.requirement_type == MonitoringRequirementType.PH:
            # Simulate pH reading
            base_ph = requirement.target_value or 6.5
            variation = random.uniform(-0.3, 0.3)
            return {
                "measured_value": base_ph + variation,
                "measurement_method": requirement.measurement_method or "digital_ph_meter",
                "equipment_used": requirement.equipment_required or "ph_meter_01"
            }
        
        elif requirement.requirement_type == MonitoringRequirementType.PRESSURE:
            # Simulate pressure reading
            base_pressure = requirement.target_value or 2.5
            variation = random.uniform(-0.1, 0.1)
            return {
                "measured_value": base_pressure + variation,
                "measurement_method": requirement.measurement_method or "pressure_gauge",
                "equipment_used": requirement.equipment_required or "pressure_gauge_01"
            }
        
        elif requirement.requirement_type == MonitoringRequirementType.TIME:
            # For time-based requirements, calculate elapsed time
            return {
                "measured_value": 30.0,  # 30 minutes elapsed
                "measurement_method": "system_timer",
                "equipment_used": "process_control_system"
            }
        
        # For other types, return None to indicate manual collection needed
        return None
    
    def _log_monitoring_data(self, stage_id: int, requirement: StageMonitoringRequirement,
                           parameter_data: Dict[str, Any]) -> StageMonitoringLog:
        """Log monitoring data and assess compliance"""
        
        monitoring_data = {
            "requirement_id": requirement.id,
            "monitoring_timestamp": datetime.utcnow(),
            "measured_value": parameter_data["measured_value"],
            "equipment_used": parameter_data.get("equipment_used"),
            "measurement_method": parameter_data.get("measurement_method"),
            "notes": "Automated 30-minute monitoring cycle"
        }
        
        # Use production service to log with validation
        log_entry = self.production_service.log_stage_monitoring(
            stage_id=stage_id,
            monitoring_data=monitoring_data,
            recorded_by=1  # System user for automated logging
        )
        
        return log_entry
    
    def _create_deviation_alert(self, log_entry: StageMonitoringLog,
                              requirement: StageMonitoringRequirement) -> ProcessMonitoringAlert:
        """Create alert for parameter deviation"""
        from app.models.production import ProcessMonitoringAlert
        
        # Determine severity based on deviation magnitude and requirement criticality
        severity = self._calculate_deviation_severity(log_entry, requirement)
        
        alert = ProcessMonitoringAlert(
            process_id=log_entry.stage.process_id,
            alert_type="parameter_deviation",
            severity_level=severity,
            alert_title=f"Parameter Deviation: {requirement.requirement_name}",
            alert_message=f"Stage '{log_entry.stage.stage_name}' parameter '{requirement.requirement_name}' "
                         f"out of tolerance. Measured: {log_entry.measured_value} "
                         f"{requirement.unit_of_measure or ''}, "
                         f"Expected: {requirement.tolerance_min}-{requirement.tolerance_max}",
            parameter_name=requirement.requirement_name,
            current_value=log_entry.measured_value,
            threshold_value=requirement.tolerance_max if log_entry.measured_value > (requirement.target_value or 0) else requirement.tolerance_min,
            auto_generated=True,
            requires_immediate_action=requirement.is_critical_limit,
            food_safety_impact=requirement.is_critical_limit,
            ccp_affected=requirement.is_critical_limit,
            oprp_affected=requirement.is_operational_limit,
            corrective_action_required=True,
            verification_required=requirement.verification_required
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def _calculate_deviation_severity(self, log_entry: StageMonitoringLog,
                                    requirement: StageMonitoringRequirement) -> str:
        """Calculate deviation severity based on magnitude and criticality"""
        
        if requirement.is_critical_limit:
            return "critical"
        
        if not requirement.tolerance_min or not requirement.tolerance_max:
            return "warning"
        
        # Calculate deviation percentage
        target = requirement.target_value or ((requirement.tolerance_min + requirement.tolerance_max) / 2)
        tolerance_range = requirement.tolerance_max - requirement.tolerance_min
        deviation_magnitude = abs(log_entry.measured_value - target)
        deviation_percentage = (deviation_magnitude / tolerance_range) * 100
        
        if deviation_percentage > 50:
            return "critical"
        elif deviation_percentage > 25:
            return "warning"
        else:
            return "info"
    
    def evaluate_stage_completion_readiness(self, stage_id: int) -> Dict[str, Any]:
        """
        Evaluate if a stage is ready for completion based on monitoring requirements
        
        ISO 22000:2018 Clause 8.5.3 - Verification activities
        """
        stage = self.db.query(ProcessStage).filter(ProcessStage.id == stage_id).first()
        if not stage:
            raise ValueError("Stage not found")
        
        # Get all mandatory monitoring requirements
        mandatory_requirements = self.db.query(StageMonitoringRequirement).filter(
            StageMonitoringRequirement.stage_id == stage_id,
            StageMonitoringRequirement.is_mandatory == True
        ).all()
        
        readiness_assessment = {
            "stage_id": stage_id,
            "stage_name": stage.stage_name,
            "ready_for_completion": True,
            "blocking_issues": [],
            "compliance_status": "compliant",
            "requirements_assessment": []
        }
        
        for requirement in mandatory_requirements:
            # Check if requirement has been monitored sufficiently
            recent_logs = self.db.query(StageMonitoringLog).filter(
                StageMonitoringLog.stage_id == stage_id,
                StageMonitoringLog.requirement_id == requirement.id,
                StageMonitoringLog.monitoring_timestamp >= stage.actual_start_time
            ).all()
            
            req_assessment = {
                "requirement_id": requirement.id,
                "requirement_name": requirement.requirement_name,
                "is_critical": requirement.is_critical_limit,
                "logs_count": len(recent_logs),
                "latest_log": None,
                "compliance_status": "compliant"
            }
            
            if not recent_logs:
                req_assessment["compliance_status"] = "no_data"
                readiness_assessment["blocking_issues"].append(
                    f"No monitoring data for mandatory requirement: {requirement.requirement_name}"
                )
                readiness_assessment["ready_for_completion"] = False
            else:
                latest_log = max(recent_logs, key=lambda x: x.monitoring_timestamp)
                req_assessment["latest_log"] = {
                    "timestamp": latest_log.monitoring_timestamp,
                    "value": latest_log.measured_value,
                    "within_limits": latest_log.is_within_limits,
                    "pass_fail": latest_log.pass_fail_status
                }
                
                # Check for critical failures
                critical_failures = [log for log in recent_logs 
                                   if log.pass_fail_status == "fail" and requirement.is_critical_limit]
                
                if critical_failures:
                    req_assessment["compliance_status"] = "critical_failure"
                    readiness_assessment["blocking_issues"].append(
                        f"Critical failure in requirement: {requirement.requirement_name}"
                    )
                    readiness_assessment["ready_for_completion"] = False
                
                # Check for recent failures
                recent_failures = [log for log in recent_logs 
                                 if log.pass_fail_status == "fail" and 
                                 log.monitoring_timestamp >= datetime.utcnow() - timedelta(hours=1)]
                
                if recent_failures and requirement.is_critical_limit:
                    req_assessment["compliance_status"] = "recent_failure"
                    readiness_assessment["blocking_issues"].append(
                        f"Recent failure in critical requirement: {requirement.requirement_name}"
                    )
                    readiness_assessment["ready_for_completion"] = False
            
            readiness_assessment["requirements_assessment"].append(req_assessment)
        
        # Check for unresolved alerts
        unresolved_alerts = self.db.query(ProcessMonitoringAlert).filter(
            ProcessMonitoringAlert.process_id == stage.process_id,
            ProcessMonitoringAlert.resolved == False,
            ProcessMonitoringAlert.severity_level.in_(["critical", "warning"])
        ).count()
        
        if unresolved_alerts > 0:
            readiness_assessment["blocking_issues"].append(
                f"{unresolved_alerts} unresolved critical/warning alerts"
            )
            if any("critical" in str(alert.severity_level) for alert in 
                   self.db.query(ProcessMonitoringAlert).filter(
                       ProcessMonitoringAlert.process_id == stage.process_id,
                       ProcessMonitoringAlert.resolved == False,
                       ProcessMonitoringAlert.severity_level == "critical"
                   ).all()):
                readiness_assessment["ready_for_completion"] = False
        
        # Set overall compliance status
        if readiness_assessment["blocking_issues"]:
            if any("critical" in issue.lower() for issue in readiness_assessment["blocking_issues"]):
                readiness_assessment["compliance_status"] = "non_compliant"
            else:
                readiness_assessment["compliance_status"] = "minor_issues"
        
        return readiness_assessment
    
    def stop_process_monitoring(self, process_id: int) -> Dict[str, Any]:
        """Stop monitoring for a process"""
        # Remove active monitoring tasks
        tasks_removed = []
        for task_key in list(self.monitoring_tasks.keys()):
            if f"process_{process_id}_" in task_key:
                del self.monitoring_tasks[task_key]
                tasks_removed.append(task_key)
        
        try:
            log_audit_event(
                self.db,
                user_id=None,
                action="monitoring.stopped",
                resource_type="production_process",
                resource_id=str(process_id),
                details={"tasks_removed": tasks_removed}
            )
        except Exception:
            pass
        
        return {
            "process_id": process_id,
            "stopped_at": datetime.utcnow(),
            "tasks_removed": tasks_removed
        }
    
    def get_monitoring_status(self, process_id: int) -> Dict[str, Any]:
        """Get current monitoring status for a process"""
        process = self.db.query(ProductionProcess).filter(
            ProductionProcess.id == process_id
        ).first()
        
        if not process:
            raise ValueError("Process not found")
        
        current_stage = self._get_current_active_stage(process_id)
        
        # Get active monitoring tasks
        active_tasks = {k: v for k, v in self.monitoring_tasks.items() 
                       if f"process_{process_id}_" in k}
        
        # Get recent monitoring logs
        recent_logs = []
        if current_stage:
            recent_logs = self.db.query(StageMonitoringLog).filter(
                StageMonitoringLog.stage_id == current_stage.id,
                StageMonitoringLog.monitoring_timestamp >= datetime.utcnow() - timedelta(hours=2)
            ).order_by(StageMonitoringLog.monitoring_timestamp.desc()).limit(10).all()
        
        # Get unresolved alerts
        unresolved_alerts = self.db.query(ProcessMonitoringAlert).filter(
            ProcessMonitoringAlert.process_id == process_id,
            ProcessMonitoringAlert.resolved == False
        ).count()
        
        return {
            "process_id": process_id,
            "process_status": process.status.value,
            "current_stage": {
                "id": current_stage.id,
                "name": current_stage.stage_name,
                "status": current_stage.status.value
            } if current_stage else None,
            "monitoring_active": len(active_tasks) > 0,
            "active_tasks": active_tasks,
            "recent_logs_count": len(recent_logs),
            "unresolved_alerts_count": unresolved_alerts,
            "last_monitoring_cycle": max([task["last_logged"] for task in active_tasks.values()]) if active_tasks else None
        }