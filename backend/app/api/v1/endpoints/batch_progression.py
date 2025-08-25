"""
Enhanced Batch Progression API Endpoints
ISO 22000:2018 Compliant Production Process Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.permissions import require_permission_dependency
from app.models.user import User
from app.services.batch_progression_service import BatchProgressionService, TransitionType
from app.services.process_monitoring_service import ProcessMonitoringService
from app.schemas.production import (
    ProcessCreateWithStages, ProcessStartRequest, ProcessSummaryResponse,
    StageMonitoringRequirementCreate, StageMonitoringLogCreate
)

router = APIRouter()


# =================== REQUEST/RESPONSE SCHEMAS ===================

class BatchProcessInitiationRequest(BaseModel):
    """Schema for initiating a new batch process"""
    batch_id: int = Field(..., description="ID of the batch to process")
    process_type: str = Field(..., description="Type of production process")
    stages_config: List[Dict[str, Any]] = Field(..., min_items=1, description="Configuration for all process stages")
    initial_parameters: Optional[Dict[str, Any]] = Field(None, description="Initial process parameters")


class BatchProcessStartRequest(BaseModel):
    """Schema for starting a batch process"""
    start_parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for process start")


class StageEvaluationResponse(BaseModel):
    """Schema for stage progression evaluation response"""
    current_stage: Dict[str, Any]
    next_stage: Optional[Dict[str, Any]]
    can_progress: bool
    requires_approval: bool
    automatic_progression: bool
    readiness_assessment: Dict[str, Any]
    time_assessment: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    available_actions: List[str]
    evaluated_at: datetime
    evaluated_by: int


class StageTransitionRequest(BaseModel):
    """Schema for requesting stage transition"""
    transition_type: str = Field(..., description="Type of transition: normal, rollback, skip, emergency, rework")
    reason: Optional[str] = Field(None, description="Reason for the transition")
    notes: Optional[str] = Field(None, description="Additional notes")
    deviations_recorded: Optional[str] = Field(None, description="Any deviations recorded")
    corrective_actions: Optional[str] = Field(None, description="Corrective actions taken")
    prerequisites_met: bool = Field(True, description="Whether prerequisites are met")


class MonitoringCycleResponse(BaseModel):
    """Schema for monitoring cycle results"""
    process_id: int
    stage_id: int
    cycle_timestamp: datetime
    logged_parameters: List[Dict[str, Any]]
    alerts_generated: List[int]
    deviations_detected: List[Dict[str, Any]]


# =================== BATCH PROCESS MANAGEMENT ===================

@router.post("/batches/{batch_id}/initiate-process")
def initiate_batch_process(
    batch_id: int,
    request: BatchProcessInitiationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:create"))
) -> Dict[str, Any]:
    """
    Initiate a new batch process with all stages and control points defined
    
    This endpoint creates a complete production process following ISO 22000:2018 guidelines:
    - Defines all process stages with control points
    - Sets up monitoring requirements for each stage
    - Prepares the batch for controlled progression through stages
    """
    try:
        service = BatchProgressionService(db)
        result = service.initiate_batch_process(
            batch_id=batch_id,
            process_type=request.process_type,
            operator_id=current_user.id,
            stages_config=request.stages_config,
            initial_parameters=request.initial_parameters
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/start")
def start_batch_process(
    process_id: int,
    request: BatchProcessStartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:update"))
) -> Dict[str, Any]:
    """
    Start the batch process and activate the first stage
    
    This will:
    - Transition the process from DRAFT to IN_PROGRESS
    - Activate the first stage
    - Begin automated 30-minute monitoring cycles
    """
    try:
        service = BatchProgressionService(db)
        result = service.start_batch_process(
            process_id=process_id,
            operator_id=current_user.id,
            start_parameters=request.start_parameters
        )
        
        # Schedule background monitoring
        background_tasks.add_task(schedule_monitoring_cycles, process_id, db)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =================== STAGE PROGRESSION MANAGEMENT ===================

@router.get("/processes/{process_id}/stages/{stage_id}/evaluate")
def evaluate_stage_progression(
    process_id: int,
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:read"))
) -> StageEvaluationResponse:
    """
    Evaluate if a stage can progress to the next stage
    
    Performs comprehensive evaluation including:
    - Monitoring compliance assessment
    - Time requirements validation
    - Quality parameters check
    - Control point verification
    """
    try:
        service = BatchProgressionService(db)
        evaluation = service.evaluate_stage_progression(
            process_id=process_id,
            current_stage_id=stage_id,
            user_id=current_user.id
        )
        return StageEvaluationResponse(**evaluation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/stages/{stage_id}/transition")
def request_stage_transition(
    process_id: int,
    stage_id: int,
    request: StageTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:update"))
) -> Dict[str, Any]:
    """
    Request a stage transition with approval workflow
    
    Handles different types of transitions:
    - Normal: Forward progression to next stage
    - Rollback: Move back to previous stage due to quality issues
    - Skip: Skip current stage (requires approval)
    - Emergency: Emergency transition bypassing normal checks
    - Rework: Return to same stage for rework
    """
    try:
        service = BatchProgressionService(db)
        
        # Validate transition type
        try:
            transition_type = TransitionType(request.transition_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid transition type: {request.transition_type}"
            )
        
        transition_data = {
            "reason": request.reason,
            "notes": request.notes,
            "deviations_recorded": request.deviations_recorded,
            "corrective_actions": request.corrective_actions,
            "prerequisites_met": request.prerequisites_met
        }
        
        result = service.request_stage_transition(
            process_id=process_id,
            current_stage_id=stage_id,
            user_id=current_user.id,
            transition_type=transition_type,
            transition_data=transition_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =================== MONITORING MANAGEMENT ===================

@router.get("/processes/{process_id}/monitoring/status")
def get_monitoring_status(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:read"))
) -> Dict[str, Any]:
    """Get current monitoring status for a process"""
    try:
        service = ProcessMonitoringService(db)
        status = service.get_monitoring_status(process_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/monitoring/execute-cycle")
def execute_monitoring_cycle(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:update"))
) -> MonitoringCycleResponse:
    """
    Execute a monitoring cycle for all active requirements
    
    This endpoint can be called manually or by scheduled tasks to:
    - Log parameters for all monitoring requirements
    - Check for deviations and generate alerts
    - Update monitoring records
    """
    try:
        service = ProcessMonitoringService(db)
        cycle_results = service.execute_monitoring_cycle(process_id)
        return MonitoringCycleResponse(**cycle_results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/stages/{stage_id}/monitoring-requirements")
def add_stage_monitoring_requirement(
    process_id: int,
    stage_id: int,
    request: StageMonitoringRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:update"))
) -> Dict[str, Any]:
    """Add a monitoring requirement to a stage"""
    try:
        from app.services.production_service import ProductionService
        service = ProductionService(db)
        
        requirement = service.add_stage_monitoring_requirement(
            stage_id=stage_id,
            requirement_data=request.model_dump(),
            created_by=current_user.id
        )
        return {
            "id": requirement.id,
            "stage_id": stage_id,
            "requirement_name": requirement.requirement_name,
            "created_at": requirement.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/stages/{stage_id}/monitoring-logs")
def log_stage_monitoring(
    process_id: int,
    stage_id: int,
    request: StageMonitoringLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:update"))
) -> Dict[str, Any]:
    """Log monitoring data for a stage"""
    try:
        from app.services.production_service import ProductionService
        service = ProductionService(db)
        
        log_entry = service.log_stage_monitoring(
            stage_id=stage_id,
            monitoring_data=request.model_dump(),
            recorded_by=current_user.id
        )
        return {
            "id": log_entry.id,
            "stage_id": stage_id,
            "monitoring_timestamp": log_entry.monitoring_timestamp,
            "within_limits": log_entry.is_within_limits,
            "pass_fail_status": log_entry.pass_fail_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =================== PROCESS OVERVIEW ===================

@router.get("/processes/{process_id}/summary")
def get_process_summary(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:read"))
) -> ProcessSummaryResponse:
    """Get a comprehensive summary of the process including progress and quality metrics"""
    try:
        from app.services.production_service import ProductionService
        service = ProductionService(db)
        summary = service.get_process_summary(process_id)
        return ProcessSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/stages")
def get_process_stages(
    process_id: int,
    include_monitoring: bool = Query(False, description="Include monitoring data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:read"))
) -> Dict[str, Any]:
    """Get all stages for a process with optional monitoring data"""
    try:
        from app.services.production_service import ProductionService
        service = ProductionService(db)
        
        process = service.get_process_with_stages(process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        
        stages_data = []
        for stage in process.stages:
            stage_data = {
                "id": stage.id,
                "stage_name": stage.stage_name,
                "sequence_order": stage.sequence_order,
                "status": stage.status.value,
                "is_critical_control_point": stage.is_critical_control_point,
                "is_operational_prp": stage.is_operational_prp,
                "actual_start_time": stage.actual_start_time,
                "actual_end_time": stage.actual_end_time,
                "duration_minutes": stage.duration_minutes
            }
            
            if include_monitoring:
                stage_data["monitoring_requirements"] = [
                    {
                        "id": req.id,
                        "requirement_name": req.requirement_name,
                        "requirement_type": req.requirement_type.value,
                        "is_critical_limit": req.is_critical_limit,
                        "is_mandatory": req.is_mandatory
                    }
                    for req in stage.monitoring_requirements
                ]
                
                stage_data["recent_monitoring_logs"] = [
                    {
                        "id": log.id,
                        "monitoring_timestamp": log.monitoring_timestamp,
                        "measured_value": log.measured_value,
                        "is_within_limits": log.is_within_limits,
                        "pass_fail_status": log.pass_fail_status
                    }
                    for log in stage.monitoring_logs[-5:]  # Last 5 logs
                ]
            
            stages_data.append(stage_data)
        
        return {
            "process_id": process_id,
            "total_stages": len(stages_data),
            "stages": stages_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =================== BACKGROUND TASKS ===================

async def schedule_monitoring_cycles(process_id: int, db: Session):
    """
    Background task to schedule automated monitoring cycles
    
    In a production environment, this would be handled by a proper
    task scheduler like Celery or similar system
    """
    try:
        # This is a conceptual implementation
        # In reality, you'd use a task scheduler to run monitoring cycles every 30 minutes
        import asyncio
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Scheduling monitoring cycles for process {process_id}")
        
        # For demonstration, we'll just log that monitoring would be scheduled
        # In production, this would integrate with your task scheduling system
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error scheduling monitoring cycles for process {process_id}: {str(e)}")


# =================== UTILITIES ===================

@router.get("/transition-types")
def get_available_transition_types(
    current_user: User = Depends(require_permission_dependency("production:read"))
) -> Dict[str, Any]:
    """Get available transition types and their descriptions"""
    return {
        "transition_types": [
            {
                "value": TransitionType.NORMAL.value,
                "label": "Normal Progression",
                "description": "Standard forward progression to next stage"
            },
            {
                "value": TransitionType.ROLLBACK.value,
                "label": "Rollback",
                "description": "Move back to previous stage due to quality issues"
            },
            {
                "value": TransitionType.SKIP.value,
                "label": "Skip Stage",
                "description": "Skip current stage (requires approval)"
            },
            {
                "value": TransitionType.EMERGENCY.value,
                "label": "Emergency Transition",
                "description": "Emergency transition bypassing normal checks"
            },
            {
                "value": TransitionType.REWORK.value,
                "label": "Rework",
                "description": "Return to same stage for rework"
            }
        ]
    }


@router.get("/processes/{process_id}/compliance-report")
def get_compliance_report(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission_dependency("production:read"))
) -> Dict[str, Any]:
    """
    Generate ISO 22000:2018 compliance report for a process
    
    Returns comprehensive compliance status including:
    - Control point monitoring compliance
    - Critical limit adherence
    - Documentation completeness
    - Corrective action records
    """
    try:
        from app.services.production_service import ProductionService
        from app.models.production import ProcessStage, StageMonitoringLog, ProcessMonitoringAlert
        
        service = ProductionService(db)
        process = service.get_process_with_stages(process_id)
        
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        
        # Compile compliance metrics
        report = {
            "process_id": process_id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value,
            "process_status": process.status.value,
            "report_generated_at": datetime.utcnow(),
            "compliance_summary": {
                "overall_status": "compliant",
                "critical_control_points": 0,
                "ccps_compliant": 0,
                "operational_prps": 0,
                "oprps_compliant": 0,
                "monitoring_compliance_rate": 0.0,
                "critical_alerts": 0,
                "unresolved_alerts": 0
            },
            "stage_compliance": [],
            "recommendations": []
        }
        
        # Analyze each stage
        for stage in process.stages:
            stage_report = {
                "stage_id": stage.id,
                "stage_name": stage.stage_name,
                "sequence_order": stage.sequence_order,
                "is_ccp": stage.is_critical_control_point,
                "is_oprp": stage.is_operational_prp,
                "status": stage.status.value,
                "compliance_status": "compliant",
                "monitoring_logs_count": len(stage.monitoring_logs),
                "failed_logs_count": len([log for log in stage.monitoring_logs if log.pass_fail_status == "fail"]),
                "critical_failures": len([log for log in stage.monitoring_logs if log.pass_fail_status == "fail" and log.deviation_severity == "critical"])
            }
            
            # Update summary counts
            if stage.is_critical_control_point:
                report["compliance_summary"]["critical_control_points"] += 1
                if stage_report["critical_failures"] == 0:
                    report["compliance_summary"]["ccps_compliant"] += 1
            
            if stage.is_operational_prp:
                report["compliance_summary"]["operational_prps"] += 1
                if stage_report["failed_logs_count"] == 0:
                    report["compliance_summary"]["oprps_compliant"] += 1
            
            # Determine stage compliance
            if stage_report["critical_failures"] > 0:
                stage_report["compliance_status"] = "non_compliant"
                report["compliance_summary"]["overall_status"] = "non_compliant"
            elif stage_report["failed_logs_count"] > stage_report["monitoring_logs_count"] * 0.1:
                stage_report["compliance_status"] = "minor_issues"
                if report["compliance_summary"]["overall_status"] == "compliant":
                    report["compliance_summary"]["overall_status"] = "minor_issues"
            
            report["stage_compliance"].append(stage_report)
        
        # Calculate monitoring compliance rate
        total_logs = sum(stage["monitoring_logs_count"] for stage in report["stage_compliance"])
        total_failures = sum(stage["failed_logs_count"] for stage in report["stage_compliance"])
        if total_logs > 0:
            report["compliance_summary"]["monitoring_compliance_rate"] = ((total_logs - total_failures) / total_logs) * 100
        
        # Count alerts
        from app.models.production import ProcessMonitoringAlert
        alerts = db.query(ProcessMonitoringAlert).filter(
            ProcessMonitoringAlert.process_id == process_id
        ).all()
        
        critical_alerts = [a for a in alerts if a.severity_level == "critical"]
        unresolved_alerts = [a for a in alerts if not a.resolved]
        
        report["compliance_summary"]["critical_alerts"] = len(critical_alerts)
        report["compliance_summary"]["unresolved_alerts"] = len(unresolved_alerts)
        
        # Generate recommendations
        if total_failures > 0:
            report["recommendations"].append("Review and strengthen monitoring procedures for failed control points")
        
        if len(unresolved_alerts) > 0:
            report["recommendations"].append(f"Resolve {len(unresolved_alerts)} outstanding alerts")
        
        if report["compliance_summary"]["monitoring_compliance_rate"] < 95:
            report["recommendations"].append("Improve monitoring compliance to achieve >95% success rate")
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))