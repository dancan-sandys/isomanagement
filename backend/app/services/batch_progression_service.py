"""
Batch Progression Service for ISO 22000:2018 Compliant Manufacturing
Implements controlled batch progression through process stages with approval workflows
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from enum import Enum
import logging

from app.models.production import (
    ProductionProcess, ProcessStage, StageStatus, ProcessStatus,
    StageTransition, StageMonitoringLog, ProcessMonitoringAlert,
    MonitoringRequirementType
)
from app.models.traceability import Batch, BatchStatus
from app.models.user import User
from app.services import log_audit_event
from app.services.process_monitoring_service import ProcessMonitoringService

logger = logging.getLogger(__name__)


class TransitionType(str, Enum):
    """Types of stage transitions"""
    NORMAL = "normal"           # Standard forward progression
    SKIP = "skip"              # Skip current stage (with approval)
    ROLLBACK = "rollback"      # Move back to previous stage
    EMERGENCY = "emergency"     # Emergency transition (bypass normal checks)
    REWORK = "rework"          # Return to same stage for rework


class BatchProgressionService:
    """
    ISO 22000:2018 compliant batch progression service
    
    Implements:
    - Controlled stage transitions with quality gates (Clause 8.5)
    - Approval workflows for critical decisions (Clause 5.3)
    - Rollback mechanisms for non-conforming batches (Clause 10.2)
    - Documentation and traceability (Clause 7.4)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.monitoring_service = ProcessMonitoringService(db)
        
    def initiate_batch_process(self, batch_id: int, process_type: str, 
                             operator_id: int, stages_config: List[Dict[str, Any]],
                             initial_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initiate a new batch process with all stages and control points defined
        
        Args:
            batch_id: ID of the batch to process
            process_type: Type of production process
            operator_id: ID of the operator initiating the process
            stages_config: Configuration for all process stages
            initial_parameters: Initial process parameters
            
        Returns:
            Dict containing process information and initial stage setup
        """
        # Validate batch exists and is in appropriate status
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
            
        if batch.status not in [BatchStatus.RECEIVED, BatchStatus.IN_PROGRESS]:
            raise ValueError(f"Batch cannot be processed. Current status: {batch.status}")
        
        # Validate operator permissions
        operator = self.db.query(User).filter(User.id == operator_id).first()
        if not operator:
            raise ValueError("Operator not found")
        
        # Check if batch already has an active process
        existing_process = self.db.query(ProductionProcess).filter(
            ProductionProcess.batch_id == batch_id,
            ProductionProcess.status.in_([ProcessStatus.DRAFT, ProcessStatus.IN_PROGRESS])
        ).first()
        
        if existing_process:
            raise ValueError(f"Batch already has an active process (ID: {existing_process.id})")
        
        # Create production process with stages
        from app.services.production_service import ProductionService
        from app.models.production import ProductProcessType
        
        production_service = ProductionService(self.db)
        
        process = production_service.create_process_with_stages(
            batch_id=batch_id,
            process_type=ProductProcessType(process_type),
            operator_id=operator_id,
            spec=initial_parameters or {},
            stages_data=stages_config,
            notes=f"Process initiated for batch {batch.batch_number}"
        )
        
        # Update batch status
        batch.status = BatchStatus.IN_PROGRESS
        
        # Setup initial monitoring requirements for all stages
        self._setup_monitoring_requirements(process.id, stages_config)
        
        # Prepare initial stage activation
        first_stage = self.db.query(ProcessStage).filter(
            ProcessStage.process_id == process.id,
            ProcessStage.sequence_order == 1
        ).first()
        
        result = {
            "process_id": process.id,
            "batch_id": batch_id,
            "batch_number": batch.batch_number,
            "process_type": process_type,
            "status": "initiated",
            "total_stages": len(stages_config),
            "first_stage": {
                "id": first_stage.id,
                "name": first_stage.stage_name,
                "description": first_stage.stage_description,
                "is_ccp": first_stage.is_critical_control_point,
                "is_oprp": first_stage.is_operational_prp,
                "requires_approval": first_stage.requires_approval
            } if first_stage else None,
            "initiated_at": datetime.utcnow(),
            "initiated_by": operator_id
        }
        
        self.db.commit()
        
        try:
            log_audit_event(
                self.db,
                user_id=operator_id,
                action="batch.process_initiated",
                resource_type="batch",
                resource_id=str(batch_id),
                details=result
            )
        except Exception:
            pass
        
        return result
    
    def start_batch_process(self, process_id: int, operator_id: int, 
                          start_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start the batch process and activate the first stage
        
        Args:
            process_id: ID of the production process
            operator_id: ID of the operator starting the process
            start_parameters: Additional parameters for process start
            
        Returns:
            Dict containing process start information
        """
        process = self.db.query(ProductionProcess).filter(
            ProductionProcess.id == process_id
        ).first()
        
        if not process:
            raise ValueError("Process not found")
            
        if process.status != ProcessStatus.DRAFT:
            raise ValueError(f"Process cannot be started. Current status: {process.status}")
        
        # Start the process using production service
        from app.services.production_service import ProductionService
        production_service = ProductionService(self.db)
        
        updated_process = production_service.start_process(
            process_id=process_id,
            operator_id=operator_id,
            start_notes=start_parameters.get('notes') if start_parameters else None
        )
        
        # Get the now-active first stage
        active_stage = self.db.query(ProcessStage).filter(
            ProcessStage.process_id == process_id,
            ProcessStage.status == StageStatus.IN_PROGRESS
        ).first()
        
        # Start automated monitoring
        monitoring_status = self.monitoring_service.start_process_monitoring(process_id)
        
        result = {
            "process_id": process_id,
            "status": "started",
            "active_stage": {
                "id": active_stage.id,
                "name": active_stage.stage_name,
                "sequence": active_stage.sequence_order,
                "started_at": active_stage.actual_start_time
            } if active_stage else None,
            "monitoring_status": monitoring_status,
            "started_at": updated_process.start_time,
            "started_by": operator_id
        }
        
        try:
            log_audit_event(
                self.db,
                user_id=operator_id,
                action="batch.process_started",
                resource_type="production_process",
                resource_id=str(process_id),
                details=result
            )
        except Exception:
            pass
        
        return result
    
    def evaluate_stage_progression(self, process_id: int, current_stage_id: int,
                                 user_id: int) -> Dict[str, Any]:
        """
        Evaluate if a stage can progress to the next stage
        
        Args:
            process_id: ID of the production process
            current_stage_id: ID of the current stage
            user_id: ID of the user requesting evaluation
            
        Returns:
            Dict containing progression evaluation results
        """
        stage = self.db.query(ProcessStage).filter(
            ProcessStage.id == current_stage_id,
            ProcessStage.process_id == process_id
        ).first()
        
        if not stage:
            raise ValueError("Stage not found")
            
        if stage.status != StageStatus.IN_PROGRESS:
            raise ValueError(f"Stage is not in progress. Current status: {stage.status}")
        
        # Evaluate monitoring compliance
        readiness_assessment = self.monitoring_service.evaluate_stage_completion_readiness(
            current_stage_id
        )
        
        # Check time requirements
        time_assessment = self._evaluate_time_requirements(stage)
        
        # Check quality parameters
        quality_assessment = self._evaluate_quality_parameters(stage)
        
        # Determine if stage can progress
        can_progress = (
            readiness_assessment["ready_for_completion"] and
            time_assessment["time_requirements_met"] and
            quality_assessment["quality_standards_met"]
        )
        
        # Determine if approval is required
        requires_approval = (
            stage.requires_approval or
            not can_progress or
            quality_assessment.get("deviations_detected", False) or
            stage.is_critical_control_point
        )
        
        # Find next stage
        next_stage = self.db.query(ProcessStage).filter(
            ProcessStage.process_id == process_id,
            ProcessStage.sequence_order == stage.sequence_order + 1
        ).first()
        
        evaluation_result = {
            "current_stage": {
                "id": stage.id,
                "name": stage.stage_name,
                "sequence": stage.sequence_order,
                "is_ccp": stage.is_critical_control_point,
                "status": stage.status.value
            },
            "next_stage": {
                "id": next_stage.id,
                "name": next_stage.stage_name,
                "sequence": next_stage.sequence_order,
                "is_ccp": next_stage.is_critical_control_point
            } if next_stage else None,
            "can_progress": can_progress,
            "requires_approval": requires_approval,
            "automatic_progression": stage.auto_advance and can_progress and not requires_approval,
            "readiness_assessment": readiness_assessment,
            "time_assessment": time_assessment,
            "quality_assessment": quality_assessment,
            "available_actions": self._get_available_actions(stage, can_progress),
            "evaluated_at": datetime.utcnow(),
            "evaluated_by": user_id
        }
        
        return evaluation_result
    
    def request_stage_transition(self, process_id: int, current_stage_id: int,
                               user_id: int, transition_type: TransitionType,
                               transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request a stage transition with approval workflow
        
        Args:
            process_id: ID of the production process
            current_stage_id: ID of the current stage
            user_id: ID of the user requesting transition
            transition_type: Type of transition requested
            transition_data: Additional data for the transition
            
        Returns:
            Dict containing transition request results
        """
        # Validate inputs
        stage = self.db.query(ProcessStage).filter(
            ProcessStage.id == current_stage_id,
            ProcessStage.process_id == process_id
        ).first()
        
        if not stage:
            raise ValueError("Stage not found")
        
        # Get evaluation first
        evaluation = self.evaluate_stage_progression(process_id, current_stage_id, user_id)
        
        # Handle different transition types
        if transition_type == TransitionType.NORMAL:
            return self._handle_normal_transition(stage, evaluation, user_id, transition_data)
        elif transition_type == TransitionType.ROLLBACK:
            return self._handle_rollback_transition(stage, user_id, transition_data)
        elif transition_type == TransitionType.SKIP:
            return self._handle_skip_transition(stage, evaluation, user_id, transition_data)
        elif transition_type == TransitionType.EMERGENCY:
            return self._handle_emergency_transition(stage, user_id, transition_data)
        elif transition_type == TransitionType.REWORK:
            return self._handle_rework_transition(stage, user_id, transition_data)
        else:
            raise ValueError(f"Unknown transition type: {transition_type}")
    
    def _handle_normal_transition(self, stage: ProcessStage, evaluation: Dict[str, Any],
                                user_id: int, transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle normal forward progression to next stage"""
        
        if not evaluation["can_progress"]:
            # Create approval request if stage cannot progress normally
            return self._create_approval_request(
                stage=stage,
                transition_type=TransitionType.NORMAL,
                user_id=user_id,
                reason="Stage quality gates not met",
                evaluation=evaluation,
                additional_data=transition_data
            )
        
        if evaluation["requires_approval"]:
            # Create approval request for critical stages
            return self._create_approval_request(
                stage=stage,
                transition_type=TransitionType.NORMAL,
                user_id=user_id,
                reason="Approval required for critical control point",
                evaluation=evaluation,
                additional_data=transition_data
            )
        
        # Execute immediate transition
        return self._execute_stage_transition(stage, user_id, transition_data)
    
    def _handle_rollback_transition(self, stage: ProcessStage, user_id: int,
                                  transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rollback to previous stage due to quality issues"""
        
        # Find previous stage
        previous_stage = self.db.query(ProcessStage).filter(
            ProcessStage.process_id == stage.process_id,
            ProcessStage.sequence_order == stage.sequence_order - 1
        ).first()
        
        if not previous_stage:
            raise ValueError("No previous stage available for rollback")
        
        # Rollback always requires approval
        return self._create_approval_request(
            stage=stage,
            transition_type=TransitionType.ROLLBACK,
            user_id=user_id,
            reason=transition_data.get("reason", "Quality standards not met - rollback required"),
            evaluation=None,
            additional_data=transition_data,
            target_stage_id=previous_stage.id
        )
    
    def _handle_skip_transition(self, stage: ProcessStage, evaluation: Dict[str, Any],
                              user_id: int, transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle skipping current stage"""
        
        # Skipping always requires approval
        return self._create_approval_request(
            stage=stage,
            transition_type=TransitionType.SKIP,
            user_id=user_id,
            reason=transition_data.get("reason", "Stage skip requested"),
            evaluation=evaluation,
            additional_data=transition_data
        )
    
    def _handle_emergency_transition(self, stage: ProcessStage, user_id: int,
                                   transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency transition bypassing normal checks"""
        
        # Emergency transitions require immediate supervisor approval
        return self._create_approval_request(
            stage=stage,
            transition_type=TransitionType.EMERGENCY,
            user_id=user_id,
            reason=transition_data.get("reason", "Emergency transition required"),
            evaluation=None,
            additional_data=transition_data,
            priority="high"
        )
    
    def _handle_rework_transition(self, stage: ProcessStage, user_id: int,
                                transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle returning batch to same stage for rework"""
        
        # Reset stage to allow rework
        stage.status = StageStatus.PENDING
        stage.actual_start_time = None
        stage.actual_end_time = None
        stage.deviations_recorded = transition_data.get("rework_reason")
        
        # Create transition record
        transition = StageTransition(
            process_id=stage.process_id,
            from_stage_id=stage.id,
            to_stage_id=stage.id,  # Same stage
            transition_type=TransitionType.REWORK,
            transition_reason=transition_data.get("reason", "Rework required"),
            initiated_by=user_id,
            transition_timestamp=datetime.utcnow(),
            prerequisites_met=False,  # Indicates rework needed
            transition_notes=transition_data.get("notes")
        )
        
        self.db.add(transition)
        self.db.commit()
        
        return {
            "status": "rework_initiated",
            "stage_id": stage.id,
            "transition_id": transition.id,
            "message": "Stage reset for rework",
            "rework_reason": transition_data.get("rework_reason"),
            "initiated_by": user_id,
            "initiated_at": datetime.utcnow()
        }
    
    def _create_approval_request(self, stage: ProcessStage, transition_type: TransitionType,
                               user_id: int, reason: str, evaluation: Optional[Dict[str, Any]],
                               additional_data: Dict[str, Any], target_stage_id: Optional[int] = None,
                               priority: str = "normal") -> Dict[str, Any]:
        """Create an approval request for stage transition"""
        
        # In a real implementation, this would integrate with a workflow system
        # For now, we'll create a conceptual approval request structure
        
        approval_request = {
            "id": f"AR_{stage.process_id}_{stage.id}_{int(datetime.utcnow().timestamp())}",
            "process_id": stage.process_id,
            "current_stage_id": stage.id,
            "target_stage_id": target_stage_id,
            "transition_type": transition_type.value,
            "requested_by": user_id,
            "requested_at": datetime.utcnow(),
            "reason": reason,
            "priority": priority,
            "status": "pending",
            "evaluation_data": evaluation,
            "additional_data": additional_data,
            "approver_required": self._determine_required_approver(stage, transition_type),
            "deadline": datetime.utcnow() + timedelta(hours=24 if priority == "normal" else 4)
        }
        
        # Store approval request (in real implementation, this would go to a workflow table)
        # For now, we'll log it as an audit event
        try:
            log_audit_event(
                self.db,
                user_id=user_id,
                action="approval.requested",
                resource_type="stage_transition",
                resource_id=str(stage.id),
                details=approval_request
            )
        except Exception:
            pass
        
        return {
            "status": "approval_required",
            "approval_request": approval_request,
            "message": f"Approval required for {transition_type.value} transition",
            "next_steps": [
                f"Await approval from {approval_request['approver_required']}",
                "Monitor process parameters during wait",
                "Document any additional issues or observations"
            ]
        }
    
    def _determine_required_approver(self, stage: ProcessStage, transition_type: TransitionType) -> str:
        """Determine who needs to approve the transition"""
        
        if transition_type == TransitionType.EMERGENCY:
            return "production_manager"
        elif stage.is_critical_control_point:
            return "quality_manager"
        elif transition_type == TransitionType.ROLLBACK:
            return "shift_supervisor"
        else:
            return "line_supervisor"
    
    def _execute_stage_transition(self, stage: ProcessStage, user_id: int,
                                transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual stage transition"""
        
        from app.services.production_service import ProductionService
        production_service = ProductionService(self.db)
        
        # Execute transition using production service
        result = production_service.transition_to_next_stage(
            process_id=stage.process_id,
            current_stage_id=stage.id,
            user_id=user_id,
            transition_data=transition_data
        )
        
        # If process completed, stop monitoring
        if result.get("process_completed"):
            self.monitoring_service.stop_process_monitoring(stage.process_id)
            
            # Update batch status
            process = self.db.query(ProductionProcess).filter(
                ProductionProcess.id == stage.process_id
            ).first()
            if process:
                batch = self.db.query(Batch).filter(Batch.id == process.batch_id).first()
                if batch:
                    batch.status = BatchStatus.COMPLETED
        
        # If moved to next stage, start monitoring for new stage
        elif result.get("next_stage"):
            # Update monitoring to new stage
            self.monitoring_service.stop_process_monitoring(stage.process_id)
            self.monitoring_service.start_process_monitoring(stage.process_id)
        
        self.db.commit()
        
        return {
            "status": "transition_completed",
            "transition_result": result,
            "executed_at": datetime.utcnow(),
            "executed_by": user_id
        }
    
    def _setup_monitoring_requirements(self, process_id: int, stages_config: List[Dict[str, Any]]):
        """Setup monitoring requirements for all stages based on configuration"""
        
        for stage_config in stages_config:
            # This would be expanded based on the specific requirements
            # For now, we'll add basic monitoring requirements
            
            stage = self.db.query(ProcessStage).filter(
                ProcessStage.process_id == process_id,
                ProcessStage.sequence_order == stage_config["sequence_order"]
            ).first()
            
            if stage and stage_config.get("monitoring_requirements"):
                for req_config in stage_config["monitoring_requirements"]:
                    from app.services.production_service import ProductionService
                    production_service = ProductionService(self.db)
                    
                    production_service.add_stage_monitoring_requirement(
                        stage_id=stage.id,
                        requirement_data=req_config,
                        created_by=1  # System user
                    )
    
    def _evaluate_time_requirements(self, stage: ProcessStage) -> Dict[str, Any]:
        """Evaluate if stage time requirements are met"""
        
        if not stage.actual_start_time:
            return {
                "time_requirements_met": False,
                "reason": "Stage not started",
                "elapsed_time": None
            }
        
        elapsed_minutes = (datetime.utcnow() - stage.actual_start_time).total_seconds() / 60
        
        assessment = {
            "elapsed_time_minutes": elapsed_minutes,
            "planned_duration": stage.duration_minutes,
            "time_requirements_met": True,
            "status": "on_time"
        }
        
        if stage.duration_minutes:
            if elapsed_minutes < stage.duration_minutes:
                assessment["time_requirements_met"] = False
                assessment["status"] = "insufficient_time"
                assessment["reason"] = f"Minimum duration not met: {elapsed_minutes:.1f}/{stage.duration_minutes} minutes"
            elif elapsed_minutes > stage.duration_minutes * 1.5:  # 50% overtime threshold
                assessment["status"] = "overtime"
                assessment["reason"] = f"Stage running overtime: {elapsed_minutes:.1f}/{stage.duration_minutes} minutes"
        
        return assessment
    
    def _evaluate_quality_parameters(self, stage: ProcessStage) -> Dict[str, Any]:
        """Evaluate quality parameters for the stage"""
        
        # Get recent monitoring logs for this stage
        recent_logs = self.db.query(StageMonitoringLog).filter(
            StageMonitoringLog.stage_id == stage.id,
            StageMonitoringLog.monitoring_timestamp >= stage.actual_start_time
        ).all()
        
        assessment = {
            "quality_standards_met": True,
            "total_measurements": len(recent_logs),
            "failed_measurements": 0,
            "critical_failures": 0,
            "deviations_detected": False,
            "quality_score": 100.0
        }
        
        if not recent_logs:
            assessment["quality_standards_met"] = False
            assessment["reason"] = "No quality measurements recorded"
            assessment["quality_score"] = 0.0
            return assessment
        
        # Analyze measurement results
        failed_logs = [log for log in recent_logs if log.pass_fail_status == "fail"]
        critical_logs = [log for log in failed_logs if log.deviation_severity == "critical"]
        
        assessment["failed_measurements"] = len(failed_logs)
        assessment["critical_failures"] = len(critical_logs)
        assessment["deviations_detected"] = len(failed_logs) > 0
        
        # Calculate quality score
        if len(recent_logs) > 0:
            pass_rate = (len(recent_logs) - len(failed_logs)) / len(recent_logs)
            assessment["quality_score"] = pass_rate * 100
        
        # Determine if standards are met
        if critical_logs:
            assessment["quality_standards_met"] = False
            assessment["reason"] = f"{len(critical_logs)} critical quality failures detected"
        elif len(failed_logs) > len(recent_logs) * 0.1:  # More than 10% failure rate
            assessment["quality_standards_met"] = False
            assessment["reason"] = f"Quality failure rate too high: {len(failed_logs)}/{len(recent_logs)}"
        
        return assessment
    
    def _get_available_actions(self, stage: ProcessStage, can_progress: bool) -> List[str]:
        """Get list of available actions for the current stage"""
        
        actions = []
        
        if can_progress:
            actions.append("advance_to_next_stage")
        else:
            actions.append("request_approval_to_advance")
        
        if stage.sequence_order > 1:
            actions.append("rollback_to_previous_stage")
        
        actions.extend([
            "record_deviation",
            "add_monitoring_log",
            "request_supervisor_review",
            "hold_for_investigation"
        ])
        
        if stage.is_critical_control_point:
            actions.append("emergency_stop")
        
        return actions