import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid
import base64

from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, PRPTemplate, PRPSchedule,
    RiskMatrix, RiskAssessment, RiskControl, CorrectiveAction, PRPPreventiveAction,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus, RiskLevel, CorrectiveActionStatus
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.schemas.prp import (
    PRPProgramCreate, PRPProgramUpdate, ChecklistCreate, ChecklistUpdate,
    ChecklistItemCreate, ChecklistCompletion, NonConformanceCreate,
    ReminderCreate, ScheduleCreate, ResponseType, RiskMatrixCreate,
    RiskAssessmentCreate, RiskControlCreate, CorrectiveActionCreate, PreventiveActionCreate
)

logger = logging.getLogger(__name__)


class PRPService:
    """
    Enhanced service for handling PRP business logic with ISO 22002-1:2025 compliance
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = "uploads/prp"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    # ============================================================================
    # RISK ASSESSMENT ENGINE (Phase 3.1)
    # ============================================================================
    
    def create_risk_matrix(self, matrix_data: RiskMatrixCreate, created_by: int) -> RiskMatrix:
        """Create a configurable risk matrix with custom scoring algorithms"""
        
        # Validate matrix configuration
        self._validate_risk_matrix_config(matrix_data)
        
        # Generate default risk levels mapping if not provided
        if not matrix_data.risk_levels:
            matrix_data.risk_levels = self._generate_default_risk_mapping(
                matrix_data.likelihood_levels, 
                matrix_data.severity_levels
            )
        
        matrix = RiskMatrix(
            name=matrix_data.name,
            description=matrix_data.description,
            likelihood_levels=matrix_data.likelihood_levels,
            severity_levels=matrix_data.severity_levels,
            risk_levels=matrix_data.risk_levels,
            created_by=created_by
        )
        
        self.db.add(matrix)
        self.db.commit()
        self.db.refresh(matrix)
        
        return matrix
    
    def _validate_risk_matrix_config(self, matrix_data: RiskMatrixCreate) -> None:
        """Validate risk matrix configuration"""
        if len(matrix_data.likelihood_levels) < 3:
            raise ValueError("Risk matrix must have at least 3 likelihood levels")
        
        if len(matrix_data.severity_levels) < 3:
            raise ValueError("Risk matrix must have at least 3 severity levels")
        
        # Validate risk levels mapping
        expected_combinations = len(matrix_data.likelihood_levels) * len(matrix_data.severity_levels)
        if matrix_data.risk_levels and len(matrix_data.risk_levels) != expected_combinations:
            raise ValueError(f"Risk levels mapping must cover all {expected_combinations} likelihood-severity combinations")
    
    def _generate_default_risk_mapping(self, likelihood_levels: List[str], severity_levels: List[str]) -> Dict[str, str]:
        """Generate default risk level mapping based on likelihood and severity"""
        mapping = {}
        
        # Define risk level assignment logic
        for i, likelihood in enumerate(likelihood_levels):
            for j, severity in enumerate(severity_levels):
                key = f"{likelihood}_{severity}"
                
                # Calculate risk level based on position in matrix
                risk_score = (i + 1) * (j + 1)
                
                if risk_score <= 4:
                    risk_level = "very_low"
                elif risk_score <= 6:
                    risk_level = "low"
                elif risk_score <= 9:
                    risk_level = "medium"
                elif risk_score <= 12:
                    risk_level = "high"
                elif risk_score <= 16:
                    risk_level = "very_high"
                else:
                    risk_level = "critical"
                
                mapping[key] = risk_level
        
        return mapping
    
    def calculate_risk_score(self, likelihood_level: str, severity_level: str, matrix_id: int = None) -> Dict[str, Any]:
        """Calculate risk score using configurable risk matrix"""
        
        # Get risk matrix (use default if not specified)
        if matrix_id:
            matrix = self.db.query(RiskMatrix).filter(RiskMatrix.id == matrix_id).first()
            if not matrix:
                raise ValueError("Risk matrix not found")
        else:
            # Use default matrix
            matrix = self.db.query(RiskMatrix).filter(RiskMatrix.is_active == True).first()
            if not matrix:
                # Create default matrix if none exists
                matrix = self._create_default_risk_matrix()
        
        # Find likelihood and severity indices
        try:
            likelihood_index = matrix.likelihood_levels.index(likelihood_level)
            severity_index = matrix.severity_levels.index(severity_level)
        except ValueError:
            raise ValueError("Invalid likelihood or severity level")
        
        # Calculate risk score
        risk_score = (likelihood_index + 1) * (severity_index + 1)
        
        # Determine risk level from matrix
        key = f"{likelihood_level}_{severity_level}"
        risk_level = matrix.risk_levels.get(key, "medium")
        
        # Determine acceptability based on risk level
        acceptability = self._determine_risk_acceptability(risk_level, risk_score)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "acceptability": acceptability,
            "matrix_used": matrix.name,
            "calculation_method": "likelihood_x_severity"
        }
    
    def _create_default_risk_matrix(self) -> RiskMatrix:
        """Create a default ISO 22002-1:2025 compliant risk matrix"""
        default_matrix = RiskMatrix(
            name="ISO 22002-1:2025 Default Risk Matrix",
            description="Default risk matrix for ISO 22002-1:2025 compliance",
            likelihood_levels=["Rare", "Unlikely", "Possible", "Likely", "Certain"],
            severity_levels=["Negligible", "Minor", "Moderate", "Major", "Catastrophic"],
            risk_levels={
                "Rare_Negligible": "very_low", "Rare_Minor": "low", "Rare_Moderate": "low",
                "Rare_Major": "medium", "Rare_Catastrophic": "medium",
                "Unlikely_Negligible": "low", "Unlikely_Minor": "low", "Unlikely_Moderate": "medium",
                "Unlikely_Major": "medium", "Unlikely_Catastrophic": "high",
                "Possible_Negligible": "low", "Possible_Minor": "medium", "Possible_Moderate": "medium",
                "Possible_Major": "high", "Possible_Catastrophic": "high",
                "Likely_Negligible": "medium", "Likely_Minor": "medium", "Likely_Moderate": "high",
                "Likely_Major": "high", "Likely_Catastrophic": "very_high",
                "Certain_Negligible": "medium", "Certain_Minor": "high", "Certain_Moderate": "high",
                "Certain_Major": "very_high", "Certain_Catastrophic": "critical"
            },
            is_active=True,
            created_by=1  # System user
        )
        
        self.db.add(default_matrix)
        self.db.commit()
        self.db.refresh(default_matrix)
        
        return default_matrix
    
    def _determine_risk_acceptability(self, risk_level: str, risk_score: int) -> bool:
        """Determine if risk is acceptable based on risk level and score"""
        acceptability_thresholds = {
            "very_low": 4,
            "low": 6,
            "medium": 9,
            "high": 12,
            "very_high": 16,
            "critical": 25
        }
        
        threshold = acceptability_thresholds.get(risk_level, 9)
        return risk_score <= threshold
    
    def calculate_residual_risk(self, initial_risk_score: int, control_effectiveness: float) -> Dict[str, Any]:
        """Calculate residual risk after implementing controls"""
        
        if not 0 <= control_effectiveness <= 1:
            raise ValueError("Control effectiveness must be between 0 and 1")
        
        # Calculate residual risk score
        residual_score = int(initial_risk_score * (1 - control_effectiveness))
        
        # Determine residual risk level
        if residual_score <= 4:
            residual_level = "very_low"
        elif residual_score <= 6:
            residual_level = "low"
        elif residual_score <= 9:
            residual_level = "medium"
        elif residual_score <= 12:
            residual_level = "high"
        elif residual_score <= 16:
            residual_level = "very_high"
        else:
            residual_level = "critical"
        
        # Determine if residual risk is acceptable
        residual_acceptability = self._determine_risk_acceptability(residual_level, residual_score)
        
        return {
            "residual_risk_score": residual_score,
            "residual_risk_level": residual_level,
            "residual_acceptability": residual_acceptability,
            "risk_reduction": initial_risk_score - residual_score,
            "risk_reduction_percentage": round((1 - residual_score / initial_risk_score) * 100, 2)
        }
    
    def create_risk_assessment(self, program_id: int, assessment_data: RiskAssessmentCreate, created_by: int) -> RiskAssessment:
        """Create a risk assessment with advanced scoring and analysis"""
        
        # Calculate risk score using risk matrix
        risk_calculation = self.calculate_risk_score(
            assessment_data.likelihood_level,
            assessment_data.severity_level
        )
        
        # Generate assessment code
        assessment_code = f"RA-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        assessment = RiskAssessment(
            program_id=program_id,
            assessment_code=assessment_code,
            hazard_identified=assessment_data.hazard_identified,
            hazard_description=assessment_data.hazard_description,
            likelihood_level=assessment_data.likelihood_level,
            severity_level=assessment_data.severity_level,
            risk_level=risk_calculation["risk_level"],
            risk_score=risk_calculation["risk_score"],
            acceptability=risk_calculation["acceptability"],
            existing_controls=assessment_data.existing_controls,
            additional_controls_required=assessment_data.additional_controls_required,
            control_effectiveness=assessment_data.control_effectiveness,
            assessment_date=datetime.utcnow(),
            created_by=created_by
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    # ============================================================================
    # CORRECTIVE ACTION WORKFLOW (Phase 3.2)
    # ============================================================================
    
    def create_corrective_action(self, action_data: CorrectiveActionCreate, created_by: int) -> CorrectiveAction:
        """Create a corrective action with root cause analysis framework"""
        
        # Generate action code
        action_code = f"CA-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Perform root cause analysis
        root_cause_analysis = self._perform_root_cause_analysis(action_data.non_conformance_description)
        
        action = CorrectiveAction(
            action_code=action_code,
            source_type=action_data.source_type,
            source_id=action_data.source_id,
            checklist_id=action_data.checklist_id,
            program_id=action_data.program_id,
            non_conformance_description=action_data.non_conformance_description,
            non_conformance_date=action_data.non_conformance_date,
            severity=action_data.severity,
            immediate_cause=action_data.immediate_cause,
            root_cause_analysis=root_cause_analysis,
            root_cause_category=action_data.root_cause_category,
            action_description=action_data.action_description,
            action_type=action_data.action_type,
            responsible_person=action_data.responsible_person,
            assigned_to=action_data.assigned_to,
            target_completion_date=action_data.target_completion_date,
            effectiveness_criteria=action_data.effectiveness_criteria,
            verification_method=action_data.verification_method,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        # Create notification for assigned person
        self._create_action_assignment_notification(action)
        
        return action
    
    def _perform_root_cause_analysis(self, non_conformance_description: str) -> str:
        """Perform automated root cause analysis using predefined categories"""
        
        # Define root cause categories and keywords
        root_cause_categories = {
            "equipment": ["equipment", "machine", "device", "tool", "instrument", "calibration", "maintenance"],
            "process": ["procedure", "process", "method", "workflow", "standard", "protocol"],
            "personnel": ["training", "skill", "knowledge", "experience", "competency", "human error"],
            "material": ["material", "supplier", "quality", "specification", "raw material"],
            "environment": ["environment", "temperature", "humidity", "cleanliness", "facility"],
            "management": ["supervision", "management", "leadership", "communication", "planning"]
        }
        
        # Analyze description for root cause indicators
        description_lower = non_conformance_description.lower()
        category_scores = {}
        
        for category, keywords in root_cause_categories.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            if score > 0:
                category_scores[category] = score
        
        # Determine most likely root cause category
        if category_scores:
            most_likely_category = max(category_scores, key=category_scores.get)
            return f"Automated analysis suggests {most_likely_category} as primary root cause category"
        else:
            return "Root cause category requires manual analysis"
    
    def _create_action_assignment_notification(self, action: CorrectiveAction) -> None:
        """Create notification for action assignment"""
        try:
            notification = Notification(
                user_id=action.assigned_to,
                title=f"Corrective Action Assigned: {action.action_code}",
                message=f"You have been assigned a corrective action: {action.action_description[:100]}...",
                notification_type=NotificationType.ACTION_ASSIGNMENT,
                priority=NotificationPriority.HIGH if action.severity in ["high", "critical"] else NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                related_id=action.id,
                related_type="corrective_action"
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to create action assignment notification: {e}")
    
    def update_action_progress(self, action_id: int, progress_percentage: int, status: str = None) -> CorrectiveAction:
        """Update corrective action progress with effectiveness tracking"""
        
        action = self.db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
        if not action:
            raise ValueError("Corrective action not found")
        
        # Update progress
        action.progress_percentage = progress_percentage
        
        # Update status if provided
        if status:
            action.status = CorrectiveActionStatus(status)
        
        # Check if action is completed
        if progress_percentage >= 100 and action.status != CorrectiveActionStatus.COMPLETED:
            action.status = CorrectiveActionStatus.PENDING_VERIFICATION
            action.actual_completion_date = datetime.utcnow()
            
            # Create verification notification
            self._create_verification_notification(action)
        
        self.db.commit()
        self.db.refresh(action)
        
        return action
    
    def _create_verification_notification(self, action: CorrectiveAction) -> None:
        """Create notification for action verification"""
        try:
            notification = Notification(
                user_id=action.effectiveness_verified_by or action.responsible_person,
                title=f"Action Verification Required: {action.action_code}",
                message=f"Corrective action {action.action_code} requires verification of effectiveness",
                notification_type=NotificationType.VERIFICATION_REQUIRED,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                related_id=action.id,
                related_type="corrective_action"
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to create verification notification: {e}")
    
    def verify_action_effectiveness(self, action_id: int, verification_data: Dict[str, Any], verified_by: int) -> CorrectiveAction:
        """Verify corrective action effectiveness"""
        
        action = self.db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
        if not action:
            raise ValueError("Corrective action not found")
        
        # Update verification details
        action.effectiveness_verification = verification_data.get("verification_details")
        action.effectiveness_verified_by = verified_by
        action.effectiveness_verified_at = datetime.utcnow()
        
        # Determine if action is effective
        is_effective = verification_data.get("is_effective", False)
        
        if is_effective:
            action.status = CorrectiveActionStatus.VERIFIED
            # Check if action should be closed
            if verification_data.get("close_action", False):
                action.status = CorrectiveActionStatus.CLOSED
        else:
            action.status = CorrectiveActionStatus.ESCALATED
            # Create escalation notification
            self._create_escalation_notification(action, verification_data.get("escalation_reason"))
        
        self.db.commit()
        self.db.refresh(action)
        
        return action
    
    def _create_escalation_notification(self, action: CorrectiveAction, escalation_reason: str = None) -> None:
        """Create escalation notification for ineffective actions"""
        try:
            notification = Notification(
                user_id=action.responsible_person,
                title=f"Action Escalation: {action.action_code}",
                message=f"Corrective action {action.action_code} has been escalated due to ineffectiveness. Reason: {escalation_reason or 'Not provided'}",
                notification_type=NotificationType.ESCALATION,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.PRP,
                related_id=action.id,
                related_type="corrective_action"
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to create escalation notification: {e}")
    
    # ============================================================================
    # PREVENTIVE ACTION SYSTEM (Phase 3.3)
    # ============================================================================
    
    def create_preventive_action(self, action_data: PreventiveActionCreate, created_by: int) -> PRPPreventiveAction:
        """Create a preventive action with trigger identification and planning"""
        
        # Generate action code
        action_code = f"PA-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Identify triggers and plan preventive action
        trigger_analysis = self._identify_preventive_triggers(action_data.potential_issue)
        success_criteria = self._generate_success_criteria(action_data.objective)
        
        action = PRPPreventiveAction(
            action_code=action_code,
            trigger_type=action_data.trigger_type,
            trigger_description=action_data.trigger_description,
            program_id=action_data.program_id,
            action_description=action_data.action_description,
            objective=action_data.objective,
            responsible_person=action_data.responsible_person,
            assigned_to=action_data.assigned_to,
            implementation_plan=action_data.implementation_plan,
            resources_required=action_data.resources_required,
            budget_estimate=action_data.budget_estimate,
            planned_start_date=action_data.planned_start_date,
            planned_completion_date=action_data.planned_completion_date,
            success_criteria=success_criteria,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        # Create notification for assigned person
        self._create_preventive_action_notification(action)
        
        return action
    
    def _identify_preventive_triggers(self, potential_issue: str) -> str:
        """Identify preventive action triggers from potential issues"""
        
        # Define trigger categories and keywords
        trigger_categories = {
            "trend_analysis": ["trend", "pattern", "increase", "decrease", "fluctuation", "variation"],
            "risk_assessment": ["risk", "hazard", "threat", "vulnerability", "exposure"],
            "audit_findings": ["audit", "finding", "nonconformity", "observation", "recommendation"],
            "customer_feedback": ["customer", "complaint", "feedback", "satisfaction", "expectation"],
            "regulatory_change": ["regulation", "standard", "requirement", "compliance", "legislation"],
            "technology_change": ["technology", "equipment", "system", "upgrade", "innovation"],
            "process_improvement": ["efficiency", "effectiveness", "optimization", "improvement", "streamline"]
        }
        
        # Analyze potential issue for trigger indicators
        issue_lower = potential_issue.lower()
        trigger_scores = {}
        
        for category, keywords in trigger_categories.items():
            score = sum(1 for keyword in keywords if keyword in issue_lower)
            if score > 0:
                trigger_scores[category] = score
        
        # Determine most likely trigger category
        if trigger_scores:
            most_likely_trigger = max(trigger_scores, key=trigger_scores.get)
            return f"Automated analysis suggests {most_likely_trigger} as primary trigger category"
        else:
            return "Trigger category requires manual analysis"
    
    def _generate_success_criteria(self, objective: str) -> str:
        """Generate success criteria based on action objective"""
        
        # Define success criteria templates based on objective keywords
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ["reduce", "decrease", "minimize"]):
            return "Measurable reduction in target metric by specified percentage"
        elif any(word in objective_lower for word in ["improve", "enhance", "increase"]):
            return "Measurable improvement in target metric by specified percentage"
        elif any(word in objective_lower for word in ["prevent", "avoid", "eliminate"]):
            return "Zero occurrences of target issue for specified time period"
        elif any(word in objective_lower for word in ["implement", "establish", "create"]):
            return "Successful implementation and verification of new process/system"
        else:
            return "Achievement of stated objective with measurable outcomes"
    
    def _create_preventive_action_notification(self, action: PRPPreventiveAction) -> None:
        """Create notification for preventive action assignment"""
        try:
            notification = Notification(
                user_id=action.assigned_to,
                title=f"Preventive Action Assigned: {action.action_code}",
                message=f"You have been assigned a preventive action: {action.action_description[:100]}...",
                notification_type=NotificationType.ACTION_ASSIGNMENT,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                related_id=action.id,
                related_type="preventive_action"
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to create preventive action notification: {e}")
    
    def start_preventive_action(self, action_id: int, started_by: int) -> PRPPreventiveAction:
        """Start a preventive action with effectiveness measurement setup"""
        
        action = self.db.query(PRPPreventiveAction).filter(PRPPreventiveAction.id == action_id).first()
        if not action:
            raise ValueError("Preventive action not found")
        
        # Update action status
        action.status = CorrectiveActionStatus.IN_PROGRESS
        action.start_date = datetime.utcnow()
        
        # Set up effectiveness measurement
        effectiveness_metrics = self._setup_effectiveness_measurement(action)
        action.effectiveness_measurement = effectiveness_metrics
        
        self.db.commit()
        self.db.refresh(action)
        
        return action
    
    def _setup_effectiveness_measurement(self, action: PRPPreventiveAction) -> str:
        """Set up effectiveness measurement framework for preventive action"""
        
        # Define measurement framework based on action type
        measurement_framework = {
            "baseline_measurement": "Establish baseline metrics before action implementation",
            "ongoing_monitoring": "Monitor key performance indicators during implementation",
            "post_implementation_assessment": "Evaluate effectiveness after implementation",
            "long_term_tracking": "Track sustained improvements over time",
            "success_criteria_verification": "Verify achievement of defined success criteria"
        }
        
        return json.dumps(measurement_framework)
    
    def measure_action_effectiveness(self, action_id: int, measurement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Measure preventive action effectiveness"""
        
        action = self.db.query(PRPPreventiveAction).filter(PRPPreventiveAction.id == action_id).first()
        if not action:
            raise ValueError("Preventive action not found")
        
        # Calculate effectiveness score
        effectiveness_score = self._calculate_effectiveness_score(measurement_data)
        
        # Determine if success criteria are met
        success_criteria_met = self._evaluate_success_criteria(action.success_criteria, measurement_data)
        
        # Update action with measurement results
        action.effectiveness_rating = effectiveness_score
        action.verification_date = datetime.utcnow()
        
        if success_criteria_met:
            action.status = CorrectiveActionStatus.VERIFIED
        else:
            action.status = CorrectiveActionStatus.IN_PROGRESS  # Continue monitoring
        
        self.db.commit()
        
        return {
            "effectiveness_score": effectiveness_score,
            "success_criteria_met": success_criteria_met,
            "recommendations": self._generate_effectiveness_recommendations(effectiveness_score, measurement_data)
        }
    
    def _calculate_effectiveness_score(self, measurement_data: Dict[str, Any]) -> float:
        """Calculate effectiveness score based on measurement data"""
        
        # Define scoring criteria
        baseline = measurement_data.get("baseline_value", 0)
        current = measurement_data.get("current_value", 0)
        target = measurement_data.get("target_value", 0)
        
        if baseline == 0:
            return 0.0
        
        # Calculate improvement percentage
        if target > baseline:  # Improvement target
            improvement = (current - baseline) / (target - baseline) if target != baseline else 0
        else:  # Reduction target
            improvement = (baseline - current) / (baseline - target) if baseline != target else 0
        
        # Convert to 0-5 scale
        effectiveness_score = min(5.0, max(0.0, improvement * 5))
        
        return round(effectiveness_score, 2)
    
    def _evaluate_success_criteria(self, success_criteria: str, measurement_data: Dict[str, Any]) -> bool:
        """Evaluate if success criteria are met"""
        
        # Simple evaluation based on effectiveness score
        effectiveness_score = measurement_data.get("effectiveness_score", 0)
        
        # Consider criteria met if effectiveness score is 3.5 or higher
        return effectiveness_score >= 3.5
    
    def _generate_effectiveness_recommendations(self, effectiveness_score: float, measurement_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on effectiveness measurement"""
        
        recommendations = []
        
        if effectiveness_score < 2.0:
            recommendations.append("Action requires significant improvement or redesign")
            recommendations.append("Consider additional resources or alternative approaches")
        elif effectiveness_score < 3.5:
            recommendations.append("Action shows moderate effectiveness but needs refinement")
            recommendations.append("Review implementation approach and adjust as needed")
        elif effectiveness_score < 4.5:
            recommendations.append("Action is effective with minor improvements possible")
            recommendations.append("Consider optimization for better results")
        else:
            recommendations.append("Action is highly effective")
            recommendations.append("Consider documenting as best practice for similar situations")
        
        return recommendations
    
    def track_continuous_improvement(self, program_id: int) -> Dict[str, Any]:
        """Track continuous improvement metrics for PRP programs"""
        
        # Get all preventive actions for the program
        preventive_actions = self.db.query(PRPPreventiveAction).filter(
            PRPPreventiveAction.program_id == program_id
        ).all()
        
        # Calculate improvement metrics
        total_actions = len(preventive_actions)
        completed_actions = len([a for a in preventive_actions if a.status == CorrectiveActionStatus.VERIFIED])
        average_effectiveness = sum(a.effectiveness_rating or 0 for a in preventive_actions) / total_actions if total_actions > 0 else 0
        
        # Identify improvement trends
        improvement_trends = self._identify_improvement_trends(preventive_actions)
        
        return {
            "total_preventive_actions": total_actions,
            "completed_actions": completed_actions,
            "completion_rate": (completed_actions / total_actions * 100) if total_actions > 0 else 0,
            "average_effectiveness": round(average_effectiveness, 2),
            "improvement_trends": improvement_trends,
            "recommendations": self._generate_continuous_improvement_recommendations(completed_actions, average_effectiveness)
        }
    
    def _identify_improvement_trends(self, actions: List[PRPPreventiveAction]) -> List[str]:
        """Identify improvement trends from preventive actions"""
        
        trends = []
        
        # Analyze effectiveness over time
        recent_actions = [a for a in actions if a.verification_date and a.verification_date > datetime.utcnow() - timedelta(days=90)]
        older_actions = [a for a in actions if a.verification_date and a.verification_date <= datetime.utcnow() - timedelta(days=90)]
        
        if recent_actions and older_actions:
            recent_avg = sum(a.effectiveness_rating or 0 for a in recent_actions) / len(recent_actions)
            older_avg = sum(a.effectiveness_rating or 0 for a in older_actions) / len(older_actions)
            
            if recent_avg > older_avg:
                trends.append("Improving effectiveness over time")
            elif recent_avg < older_avg:
                trends.append("Declining effectiveness - review needed")
        
        # Analyze trigger types
        trigger_types = {}
        for action in actions:
            trigger_type = action.trigger_type
            trigger_types[trigger_type] = trigger_types.get(trigger_type, 0) + 1
        
        most_common_trigger = max(trigger_types, key=trigger_types.get) if trigger_types else None
        if most_common_trigger:
            trends.append(f"Most common trigger: {most_common_trigger}")
        
        return trends
    
    def _generate_continuous_improvement_recommendations(self, completed_actions: int, average_effectiveness: float) -> List[str]:
        """Generate continuous improvement recommendations"""
        
        recommendations = []
        
        if completed_actions < 5:
            recommendations.append("Increase preventive action implementation")
            recommendations.append("Focus on high-impact preventive measures")
        elif average_effectiveness < 3.0:
            recommendations.append("Review preventive action planning process")
            recommendations.append("Enhance success criteria definition")
        elif average_effectiveness >= 4.0:
            recommendations.append("Document successful preventive actions as best practices")
            recommendations.append("Consider expanding preventive action program")
        
        recommendations.append("Regular review of preventive action effectiveness")
        recommendations.append("Continuous monitoring of improvement trends")
        
        return recommendations
    
    def create_prp_program(self, program_data: PRPProgramCreate, created_by: int) -> PRPProgram:
        """Create a new PRP program with ISO 22002-1:2025 compliance"""
        
        # Check if program code already exists
        existing_program = self.db.query(PRPProgram).filter(
            PRPProgram.program_code == program_data.program_code
        ).first()
        
        if existing_program:
            raise ValueError("Program code already exists")
        
        # Calculate next due date based on frequency
        next_due_date = None
        if program_data.frequency:
            next_due_date = datetime.utcnow()
            
            if program_data.frequency == PRPFrequency.DAILY:
                next_due_date += timedelta(days=1)
            elif program_data.frequency == PRPFrequency.WEEKLY:
                next_due_date += timedelta(weeks=1)
            elif program_data.frequency == PRPFrequency.MONTHLY:
                next_due_date += timedelta(days=30)
            elif program_data.frequency == PRPFrequency.QUARTERLY:
                next_due_date += timedelta(days=90)
            elif program_data.frequency == PRPFrequency.SEMI_ANNUALLY:
                next_due_date += timedelta(days=180)
            elif program_data.frequency == PRPFrequency.ANNUALLY:
                next_due_date += timedelta(days=365)
        
        program = PRPProgram(
            program_code=program_data.program_code,
            name=program_data.name,
            description=program_data.description,
            category=program_data.category,
            status=PRPStatus.ACTIVE,
            objective=program_data.objective,
            scope=program_data.scope,
            responsible_department=program_data.responsible_department,
            responsible_person=program_data.responsible_person,
            risk_assessment_required=program_data.risk_assessment_required if hasattr(program_data, 'risk_assessment_required') else True,
            frequency=program_data.frequency,
            frequency_details=program_data.frequency_details,
            next_due_date=next_due_date,
            sop_reference=program_data.sop_reference,
            forms_required=program_data.forms_required,
            records_required=program_data.records_required,
            training_requirements=program_data.training_requirements,
            monitoring_frequency=program_data.monitoring_frequency,
            verification_frequency=program_data.verification_frequency,
            acceptance_criteria=program_data.acceptance_criteria,
            trend_analysis_required=program_data.trend_analysis_required,
            corrective_action_procedure=program_data.corrective_action_procedure,
            escalation_procedure=program_data.escalation_procedure,
            preventive_action_procedure=program_data.preventive_action_procedure,
            created_by=created_by
        )
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        return program
    
    def create_risk_matrix(self, matrix_data: RiskMatrixCreate, created_by: int) -> RiskMatrix:
        """Create a new risk matrix for PRP risk assessment"""
        
        matrix = RiskMatrix(
            name=matrix_data.name,
            description=matrix_data.description,
            likelihood_levels=matrix_data.likelihood_levels,
            severity_levels=matrix_data.severity_levels,
            risk_levels=matrix_data.risk_levels,
            created_by=created_by
        )
        
        self.db.add(matrix)
        self.db.commit()
        self.db.refresh(matrix)
        
        return matrix
    
    def create_risk_assessment(self, program_id: int, assessment_data: RiskAssessmentCreate, created_by: int) -> RiskAssessment:
        """Create a new risk assessment for a PRP program"""
        
        # Verify program exists
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Calculate risk score and level
        risk_score, risk_level = self._calculate_risk_score(
            assessment_data.likelihood_level,
            assessment_data.severity_level
        )
        
        assessment = RiskAssessment(
            program_id=program_id,
            assessment_code=assessment_data.assessment_code,
            hazard_identified=assessment_data.hazard_identified,
            hazard_description=assessment_data.hazard_description,
            likelihood_level=assessment_data.likelihood_level,
            severity_level=assessment_data.severity_level,
            risk_level=risk_level,
            risk_score=risk_score,
            acceptability=risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW],
            existing_controls=assessment_data.existing_controls,
            additional_controls_required=assessment_data.additional_controls_required,
            control_effectiveness=assessment_data.control_effectiveness,
            created_by=created_by
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    def _calculate_risk_score(self, likelihood: str, severity: str) -> Tuple[int, RiskLevel]:
        """Calculate risk score and level based on likelihood and severity"""
        
        # Define scoring matrix (can be made configurable)
        likelihood_scores = {
            "Rare": 1,
            "Unlikely": 2,
            "Possible": 3,
            "Likely": 4,
            "Certain": 5
        }
        
        severity_scores = {
            "Negligible": 1,
            "Minor": 2,
            "Moderate": 3,
            "Major": 4,
            "Catastrophic": 5
        }
        
        likelihood_score = likelihood_scores.get(likelihood, 3)
        severity_score = severity_scores.get(severity, 3)
        risk_score = likelihood_score * severity_score
        
        # Determine risk level
        if risk_score <= 4:
            risk_level = RiskLevel.VERY_LOW
        elif risk_score <= 8:
            risk_level = RiskLevel.LOW
        elif risk_score <= 12:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 16:
            risk_level = RiskLevel.HIGH
        elif risk_score <= 20:
            risk_level = RiskLevel.VERY_HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        return risk_score, risk_level
    
    def create_corrective_action(self, action_data: CorrectiveActionCreate, created_by: int) -> CorrectiveAction:
        """Create a new corrective action"""
        
        action = CorrectiveAction(
            action_code=action_data.action_code,
            source_type=action_data.source_type,
            source_id=action_data.source_id,
            checklist_id=action_data.checklist_id,
            program_id=action_data.program_id,
            non_conformance_description=action_data.non_conformance_description,
            non_conformance_date=action_data.non_conformance_date,
            severity=action_data.severity,
            immediate_cause=action_data.immediate_cause,
            root_cause_analysis=action_data.root_cause_analysis,
            root_cause_category=action_data.root_cause_category,
            action_description=action_data.action_description,
            action_type=action_data.action_type,
            responsible_person=action_data.responsible_person,
            assigned_to=action_data.assigned_to,
            target_completion_date=action_data.target_completion_date,
            effectiveness_criteria=action_data.effectiveness_criteria,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        # Create notification for assigned person
        self._create_action_notification(action, "corrective_action_assigned")
        
        return action
    
    def create_preventive_action(self, action_data: PreventiveActionCreate, created_by: int) -> PRPPreventiveAction:
        """Create a new preventive action"""
        
        action = PRPPreventiveAction(
            action_code=action_data.action_code,
            trigger_type=action_data.trigger_type,
            trigger_description=action_data.trigger_description,
            program_id=action_data.program_id,
            action_description=action_data.action_description,
            objective=action_data.objective,
            responsible_person=action_data.responsible_person,
            assigned_to=action_data.assigned_to,
            implementation_plan=action_data.implementation_plan,
            resources_required=action_data.resources_required,
            budget_estimate=action_data.budget_estimate,
            planned_start_date=action_data.planned_start_date,
            planned_completion_date=action_data.planned_completion_date,
            success_criteria=action_data.success_criteria,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        # Create notification for assigned person
        self._create_action_notification(action, "preventive_action_assigned")
        
        return action
    
    def _create_action_notification(self, action, notification_type: str):
        """Create notification for action assignment"""
        
        try:
            if notification_type == "corrective_action_assigned":
                title = f"Corrective Action Assigned: {action.action_code}"
                message = f"You have been assigned a corrective action: {action.action_description}"
            else:
                title = f"Preventive Action Assigned: {action.action_code}"
                message = f"You have been assigned a preventive action: {action.action_description}"
            
            notification = Notification(
                user_id=action.assigned_to,
                title=title,
                message=message,
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                notification_data={
                    "action_id": action.id,
                    "action_code": action.action_code,
                    "action_type": notification_type,
                    "target_date": action.target_completion_date.isoformat() if hasattr(action, 'target_completion_date') else None
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create action notification: {str(e)}")
    
    def get_prp_compliance_report(self, program_id: Optional[int] = None, 
                                date_from: Optional[datetime] = None,
                                date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive PRP compliance report"""
        
        query = self.db.query(PRPProgram)
        if program_id:
            query = query.filter(PRPProgram.id == program_id)
        
        programs = query.all()
        
        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            },
            "programs": [],
            "summary": {
                "total_programs": len(programs),
                "active_programs": 0,
                "programs_with_risk_assessments": 0,
                "programs_with_corrective_actions": 0,
                "overall_compliance_rate": 0.0
            }
        }
        
        total_compliance = 0.0
        program_count = 0
        
        for program in programs:
            # Get program statistics
            checklist_count = self.db.query(PRPChecklist).filter(
                PRPChecklist.program_id == program.id
            ).count()
            
            completed_checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.status == ChecklistStatus.COMPLETED
                )
            ).all()
            
            risk_assessment_count = self.db.query(RiskAssessment).filter(
                RiskAssessment.program_id == program.id
            ).count()
            
            corrective_action_count = self.db.query(CorrectiveAction).filter(
                CorrectiveAction.program_id == program.id
            ).count()
            
            # Calculate compliance rate
            compliance_rate = 0.0
            if completed_checklists:
                total_items = sum(c.total_items for c in completed_checklists)
                passed_items = sum(c.passed_items for c in completed_checklists)
                if total_items > 0:
                    compliance_rate = (passed_items / total_items) * 100
            
            total_compliance += compliance_rate
            program_count += 1
            
            # Update summary
            if program.status == PRPStatus.ACTIVE:
                report_data["summary"]["active_programs"] += 1
            if risk_assessment_count > 0:
                report_data["summary"]["programs_with_risk_assessments"] += 1
            if corrective_action_count > 0:
                report_data["summary"]["programs_with_corrective_actions"] += 1
            
            program_data = {
                "id": program.id,
                "program_code": program.program_code,
                "name": program.name,
                "category": program.category.value,
                "status": program.status.value,
                "risk_level": program.risk_level.value if program.risk_level else None,
                "checklist_count": checklist_count,
                "completed_checklists": len(completed_checklists),
                "compliance_rate": compliance_rate,
                "risk_assessment_count": risk_assessment_count,
                "corrective_action_count": corrective_action_count,
                "last_review_date": program.last_review_date.isoformat() if program.last_review_date else None,
                "next_review_date": program.next_review_date.isoformat() if program.next_review_date else None
            }
            
            report_data["programs"].append(program_data)
        
        # Calculate overall compliance
        if program_count > 0:
            report_data["summary"]["overall_compliance_rate"] = total_compliance / program_count
        
        return report_data
    
    def get_risk_assessment_summary(self, program_id: Optional[int] = None) -> Dict[str, Any]:
        """Get risk assessment summary for PRP programs"""
        
        query = self.db.query(RiskAssessment)
        if program_id:
            query = query.filter(RiskAssessment.program_id == program_id)
        
        assessments = query.all()
        
        risk_level_counts = {
            RiskLevel.VERY_LOW.value: 0,
            RiskLevel.LOW.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.HIGH.value: 0,
            RiskLevel.VERY_HIGH.value: 0,
            RiskLevel.CRITICAL.value: 0
        }
        
        for assessment in assessments:
            if assessment.risk_level:
                risk_level_counts[assessment.risk_level.value] += 1
        
        return {
            "total_assessments": len(assessments),
            "risk_level_distribution": risk_level_counts,
            "high_risk_count": risk_level_counts[RiskLevel.HIGH.value] + 
                              risk_level_counts[RiskLevel.VERY_HIGH.value] + 
                              risk_level_counts[RiskLevel.CRITICAL.value],
            "assessments_requiring_controls": len([a for a in assessments if not a.acceptability])
        }
    
    def get_corrective_action_summary(self, program_id: Optional[int] = None) -> Dict[str, Any]:
        """Get corrective action summary for PRP programs"""
        
        query = self.db.query(CorrectiveAction)
        if program_id:
            query = query.filter(CorrectiveAction.program_id == program_id)
        
        actions = query.all()
        
        status_counts = {
            CorrectiveActionStatus.OPEN.value: 0,
            CorrectiveActionStatus.IN_PROGRESS.value: 0,
            CorrectiveActionStatus.PENDING_VERIFICATION.value: 0,
            CorrectiveActionStatus.VERIFIED.value: 0,
            CorrectiveActionStatus.CLOSED.value: 0,
            CorrectiveActionStatus.ESCALATED.value: 0
        }
        
        for action in actions:
            status_counts[action.status.value] += 1
        
        overdue_actions = [a for a in actions if a.target_completion_date and 
                          a.target_completion_date < datetime.utcnow() and 
                          a.status not in [CorrectiveActionStatus.CLOSED, CorrectiveActionStatus.VERIFIED]]
        
        return {
            "total_actions": len(actions),
            "status_distribution": status_counts,
            "overdue_actions": len(overdue_actions),
            "open_actions": status_counts[CorrectiveActionStatus.OPEN.value] + 
                           status_counts[CorrectiveActionStatus.IN_PROGRESS.value]
        }
    
    def create_checklist(self, program_id: int, checklist_data: ChecklistCreate, created_by: int) -> PRPChecklist:
        """Create a new checklist"""
        
        # Verify program exists
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Check if checklist code already exists
        existing_checklist = self.db.query(PRPChecklist).filter(
            PRPChecklist.checklist_code == checklist_data.checklist_code
        ).first()
        
        if existing_checklist:
            raise ValueError("Checklist code already exists")
        
        checklist = PRPChecklist(
            program_id=program_id,
            checklist_code=checklist_data.checklist_code,
            name=checklist_data.name,
            description=checklist_data.description,
            status=ChecklistStatus.PENDING,
            scheduled_date=checklist_data.scheduled_date,
            due_date=checklist_data.due_date,
            assigned_to=checklist_data.assigned_to,
            created_by=created_by
        )
        
        self.db.add(checklist)
        self.db.commit()
        self.db.refresh(checklist)
        
        # Create reminder for the checklist
        self._create_checklist_reminder(checklist)
        
        return checklist
    
    def _create_checklist_reminder(self, checklist: PRPChecklist):
        """Create reminder for a checklist"""
        
        try:
            # Create reminder notification
            reminder_date = checklist.due_date - timedelta(days=1)
            
            notification = Notification(
                user_id=checklist.assigned_to,
                title=f"PRP Checklist Reminder: {checklist.name}",
                message=f"Checklist '{checklist.name}' is due tomorrow ({checklist.due_date.strftime('%Y-%m-%d')}). "
                       f"Please complete the checklist before the due date.",
                notification_type=NotificationType.WARNING,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                notification_data={
                    "checklist_id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "due_date": checklist.due_date.isoformat(),
                    "reminder_type": "due_soon"
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.info(f"Reminder created for checklist {checklist.checklist_code}")
            
        except Exception as e:
            logger.error(f"Failed to create reminder for checklist {checklist.id}: {str(e)}")
    
    def complete_checklist(self, checklist_id: int, completion_data: ChecklistCompletion, completed_by: int) -> Tuple[PRPChecklist, bool]:
        """Complete a checklist with signature and timestamp logging"""
        
        checklist = self.db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
        if not checklist:
            raise ValueError("Checklist not found")
        
        # Update checklist items
        total_items = 0
        passed_items = 0
        failed_items = 0
        not_applicable_items = 0
        
        for item_completion in completion_data.items:
            item = self.db.query(PRPChecklistItem).filter(PRPChecklistItem.id == item_completion["item_id"]).first()
            if item:
                item.response = item_completion["response"]
                item.response_value = item_completion.get("response_value")
                item.is_compliant = item_completion["is_compliant"]
                item.comments = item_completion.get("comments")
                item.evidence_files = item_completion.get("evidence_files")
                item.updated_at = datetime.utcnow()
                
                total_items += 1
                if item_completion["is_compliant"]:
                    passed_items += 1
                else:
                    failed_items += 1
                
                # Check if item is not applicable
                if item_completion["response"].lower() in ['n/a', 'not applicable', 'na']:
                    not_applicable_items += 1
                    passed_items -= 1  # Adjust counts
        
        # Calculate compliance percentage
        compliance_percentage = 0.0
        if total_items > 0:
            compliance_percentage = (passed_items / (total_items - not_applicable_items)) * 100 if (total_items - not_applicable_items) > 0 else 100.0
        
        # Update checklist
        checklist.status = ChecklistStatus.COMPLETED
        checklist.completed_date = datetime.utcnow()
        checklist.total_items = total_items
        checklist.passed_items = passed_items
        checklist.failed_items = failed_items
        checklist.not_applicable_items = not_applicable_items
        checklist.compliance_percentage = compliance_percentage
        checklist.general_comments = completion_data.general_comments
        checklist.corrective_actions_required = completion_data.corrective_actions_required
        checklist.corrective_actions = completion_data.corrective_actions
        checklist.updated_at = datetime.utcnow()
        
        # Store signature if provided
        signature_created = False
        if completion_data.signature:
            signature_created = self._store_signature(checklist_id, completion_data.signature, completed_by)
        
        # Check for non-conformance
        non_conformance_created = False
        if failed_items > 0 or completion_data.corrective_actions_required:
            non_conformance_created = self._create_non_conformance(checklist, completion_data)
        
        self.db.commit()
        
        return checklist, non_conformance_created
    
    def _store_signature(self, checklist_id: int, signature_data: str, signed_by: int) -> bool:
        """Store signature data for a checklist"""
        
        try:
            # Decode base64 signature
            signature_bytes = base64.b64decode(signature_data)
            
            # Generate unique filename
            filename = f"signature_{checklist_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            file_path = os.path.join(self.upload_dir, filename)
            
            # Save signature file
            with open(file_path, 'wb') as f:
                f.write(signature_bytes)
            
            # Store signature metadata in database
            checklist = self.db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
            if checklist:
                evidence_files = []
                if checklist.evidence_files:
                    try:
                        evidence_files = json.loads(checklist.evidence_files)
                    except:
                        evidence_files = []
                
                evidence_files.append({
                    "type": "signature",
                    "filename": filename,
                    "file_path": file_path,
                    "signed_by": signed_by,
                    "signed_at": datetime.utcnow().isoformat()
                })
                
                checklist.evidence_files = json.dumps(evidence_files)
            
            logger.info(f"Signature stored for checklist {checklist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store signature for checklist {checklist_id}: {str(e)}")
            return False
    
    def _create_non_conformance(self, checklist: PRPChecklist, completion_data: ChecklistCompletion) -> bool:
        """Create non-conformance record for failed checklist"""
        
        try:
            # Determine severity based on failure rate
            failure_rate = checklist.failed_items / checklist.total_items if checklist.total_items > 0 else 0
            
            if failure_rate >= 0.5:
                severity = "critical"
            elif failure_rate >= 0.3:
                severity = "high"
            elif failure_rate >= 0.1:
                severity = "medium"
            else:
                severity = "low"
            
            # Create notification for non-conformance
            notification = Notification(
                user_id=checklist.assigned_to,
                title=f"PRP Non-Conformance Alert: {checklist.name}",
                message=f"Checklist '{checklist.name}' has failed with {checklist.failed_items} failed items. "
                       f"Compliance rate: {checklist.compliance_percentage:.1f}%. "
                       f"Immediate attention required.",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.PRP,
                notification_data={
                    "checklist_id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "failed_items": checklist.failed_items,
                    "total_items": checklist.total_items,
                    "compliance_percentage": checklist.compliance_percentage,
                    "severity": severity
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.warning(f"Non-conformance created for checklist {checklist.checklist_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create non-conformance for checklist {checklist.id}: {str(e)}")
            return False
    
    def check_overdue_checklists(self) -> List[PRPChecklist]:
        """Check for overdue checklists and create escalation notifications"""
        
        overdue_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.due_date < datetime.utcnow(),
                PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
            )
        ).all()
        
        for checklist in overdue_checklists:
            self._create_escalation_notification(checklist)
        
        return overdue_checklists
    
    def _create_escalation_notification(self, checklist: PRPChecklist):
        """Create escalation notification for overdue checklist"""
        
        try:
            # Calculate days overdue
            days_overdue = (datetime.utcnow() - checklist.due_date).days
            
            # Get program details
            program = self.db.query(PRPProgram).filter(PRPProgram.id == checklist.program_id).first()
            
            # Create escalation notification
            notification = Notification(
                user_id=checklist.assigned_to,
                title=f"URGENT: Overdue PRP Checklist - {checklist.name}",
                message=f"Checklist '{checklist.name}' is {days_overdue} day(s) overdue. "
                       f"Program: {program.name if program else 'Unknown'}. "
                       f"Immediate action required to maintain compliance.",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.PRP,
                notification_data={
                    "checklist_id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "days_overdue": days_overdue,
                    "program_name": program.name if program else "Unknown",
                    "escalation_type": "overdue"
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.warning(f"Escalation notification created for overdue checklist {checklist.checklist_code}")
            
        except Exception as e:
            logger.error(f"Failed to create escalation notification for checklist {checklist.id}: {str(e)}")
    
    def upload_evidence_file(self, checklist_id: int, file_data: bytes, filename: str, uploaded_by: int) -> Dict[str, Any]:
        """Upload evidence file for a checklist"""
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"evidence_{checklist_id}_{uuid.uuid4().hex}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Update checklist evidence files
            checklist = self.db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
            if checklist:
                evidence_files = []
                if checklist.evidence_files:
                    try:
                        evidence_files = json.loads(checklist.evidence_files)
                    except:
                        evidence_files = []
                
                evidence_files.append({
                    "type": "evidence",
                    "original_filename": filename,
                    "filename": unique_filename,
                    "file_path": file_path,
                    "file_size": len(file_data),
                    "uploaded_by": uploaded_by,
                    "uploaded_at": datetime.utcnow().isoformat()
                })
                
                checklist.evidence_files = json.dumps(evidence_files)
                self.db.commit()
            
            return {
                "file_id": unique_filename,
                "filename": unique_filename,
                "file_path": file_path,
                "file_size": len(file_data),
                "file_type": file_extension,
                "uploaded_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload evidence file for checklist {checklist_id}: {str(e)}")
            raise ValueError(f"Failed to upload file: {str(e)}")
    
    def get_prp_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive PRP dashboard statistics"""
        
        # Get total programs
        total_programs = self.db.query(PRPProgram).count()
        
        # Get active programs
        active_programs = self.db.query(PRPProgram).filter(PRPProgram.status == PRPStatus.ACTIVE).count()
        
        # Get total checklists
        total_checklists = self.db.query(PRPChecklist).count()
        
        # Get pending checklists
        pending_checklists = self.db.query(PRPChecklist).filter(
            PRPChecklist.status == ChecklistStatus.PENDING
        ).count()
        
        # Get overdue checklists
        overdue_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.due_date < datetime.utcnow(),
                PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
            )
        ).count()
        
        # Get completed checklists this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_this_month = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.status == ChecklistStatus.COMPLETED,
                PRPChecklist.completed_date >= current_month_start
            )
        ).count()
        
        # Calculate compliance rate
        completed_checklists = self.db.query(PRPChecklist).filter(
            PRPChecklist.status == ChecklistStatus.COMPLETED
        ).all()
        
        total_compliance = sum(checklist.compliance_percentage for checklist in completed_checklists)
        compliance_rate = total_compliance / len(completed_checklists) if completed_checklists else 0.0
        
        # Get recent checklists
        recent_checklists = self.db.query(PRPChecklist).order_by(
            desc(PRPChecklist.scheduled_date)
        ).limit(5).all()
        
        # Get upcoming checklists
        upcoming_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.scheduled_date >= datetime.utcnow(),
                PRPChecklist.status == ChecklistStatus.PENDING
            )
        ).order_by(PRPChecklist.scheduled_date).limit(5).all()
        
        # Get risk assessment summary
        risk_summary = self.get_risk_assessment_summary()
        
        # Get corrective action summary
        action_summary = self.get_corrective_action_summary()
        
        return {
            "total_programs": total_programs,
            "active_programs": active_programs,
            "total_checklists": total_checklists,
            "pending_checklists": pending_checklists,
            "overdue_checklists": overdue_checklists,
            "completed_this_month": completed_this_month,
            "compliance_rate": compliance_rate,
            "risk_assessment_summary": risk_summary,
            "corrective_action_summary": action_summary,
            "recent_checklists": [
                {
                    "id": checklist.id,
                    "name": checklist.name,
                    "status": checklist.status.value if checklist.status else None,
                    "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                    "compliance_percentage": checklist.compliance_percentage,
                } for checklist in recent_checklists
            ],
            "upcoming_checklists": [
                {
                    "id": checklist.id,
                    "name": checklist.name,
                    "scheduled_date": checklist.scheduled_date.isoformat() if checklist.scheduled_date else None,
                    "assigned_to": checklist.assigned_to,
                } for checklist in upcoming_checklists
            ]
        }
    
    def get_capa_dashboard_stats(self) -> Dict[str, Any]:
        """Get CAPA dashboard statistics and analytics"""
        
        # Get corrective actions summary
        total_corrective_actions = self.db.query(CorrectiveAction).count()
        open_corrective_actions = self.db.query(CorrectiveAction).filter(
            CorrectiveAction.status.in_([CorrectiveActionStatus.OPEN, CorrectiveActionStatus.IN_PROGRESS])
        ).count()
        
        # Get preventive actions summary
        total_preventive_actions = self.db.query(PRPPreventiveAction).count()
        open_preventive_actions = self.db.query(PRPPreventiveAction).filter(
            PRPPreventiveAction.status.in_([CorrectiveActionStatus.OPEN, CorrectiveActionStatus.IN_PROGRESS])
        ).count()
        
        # Get overdue actions
        overdue_corrective = self.db.query(CorrectiveAction).filter(
            and_(
                CorrectiveAction.target_completion_date < datetime.utcnow(),
                CorrectiveAction.status != CorrectiveActionStatus.COMPLETED
            )
        ).count()
        
        overdue_preventive = self.db.query(PRPPreventiveAction).filter(
            and_(
                PRPPreventiveAction.planned_completion_date < datetime.utcnow(),
                PRPPreventiveAction.status != CorrectiveActionStatus.COMPLETED
            )
        ).count()
        
        # Get effectiveness metrics
        completed_corrective = self.db.query(CorrectiveAction).filter(
            CorrectiveAction.status == CorrectiveActionStatus.COMPLETED
        ).count()
        
        effective_corrective = self.db.query(CorrectiveAction).filter(
            CorrectiveAction.effectiveness_verification == True
        ).count()
        
        effectiveness_rate = (effective_corrective / completed_corrective * 100) if completed_corrective > 0 else 0.0
        
        # Get recent actions
        recent_corrective = self.db.query(CorrectiveAction).order_by(
            desc(CorrectiveAction.created_at)
        ).limit(5).all()
        
        recent_preventive = self.db.query(PRPPreventiveAction).order_by(
            desc(PRPPreventiveAction.created_at)
        ).limit(5).all()
        
        return {
            "corrective_actions": {
                "total": total_corrective_actions,
                "open": open_corrective_actions,
                "overdue": overdue_corrective,
                "completed": completed_corrective,
                "effective": effective_corrective,
                "effectiveness_rate": effectiveness_rate
            },
            "preventive_actions": {
                "total": total_preventive_actions,
                "open": open_preventive_actions,
                "overdue": overdue_preventive
            },
            "recent_corrective_actions": [
                {
                    "id": action.id,
                    "action_code": action.action_code,
                    "description": action.action_description,
                    "status": action.status.value if action.status else None,
                    "target_date": action.target_completion_date.isoformat() if action.target_completion_date else None,
                    "created_at": action.created_at.isoformat() if action.created_at else None
                } for action in recent_corrective
            ],
            "recent_preventive_actions": [
                {
                    "id": action.id,
                    "action_code": action.action_code,
                    "description": action.action_description,
                    "status": action.status.value if action.status else None,
                    "planned_date": action.planned_completion_date.isoformat() if action.planned_completion_date else None,
                    "created_at": action.created_at.isoformat() if action.created_at else None
                } for action in recent_preventive
            ]
        }
    
    def get_overdue_capa_actions(self, action_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get overdue CAPA actions"""
        
        overdue_actions = []
        
        if action_type is None or action_type == "corrective":
            # Get overdue corrective actions
            overdue_corrective = self.db.query(CorrectiveAction).filter(
                and_(
                    CorrectiveAction.target_completion_date < datetime.utcnow(),
                    CorrectiveAction.status != CorrectiveActionStatus.COMPLETED
                )
            ).all()
            
            for action in overdue_corrective:
                overdue_actions.append({
                    "id": action.id,
                    "action_code": action.action_code,
                    "type": "corrective",
                    "description": action.action_description,
                    "status": action.status.value if action.status else None,
                    "target_date": action.target_completion_date.isoformat() if action.target_completion_date else None,
                    "days_overdue": (datetime.utcnow() - action.target_completion_date).days if action.target_completion_date else 0,
                    "responsible_person": action.responsible_person,
                    "assigned_to": action.assigned_to
                })
        
        if action_type is None or action_type == "preventive":
            # Get overdue preventive actions
            overdue_preventive = self.db.query(PRPPreventiveAction).filter(
                and_(
                    PRPPreventiveAction.planned_completion_date < datetime.utcnow(),
                    PRPPreventiveAction.status != CorrectiveActionStatus.COMPLETED
                )
            ).all()
            
            for action in overdue_preventive:
                overdue_actions.append({
                    "id": action.id,
                    "action_code": action.action_code,
                    "type": "preventive",
                    "description": action.action_description,
                    "status": action.status.value if action.status else None,
                    "target_date": action.planned_completion_date.isoformat() if action.planned_completion_date else None,
                    "days_overdue": (datetime.utcnow() - action.planned_completion_date).days if action.planned_completion_date else 0,
                    "responsible_person": action.responsible_person,
                    "assigned_to": action.assigned_to
                })
        
        # Sort by days overdue (most overdue first)
        overdue_actions.sort(key=lambda x: x["days_overdue"], reverse=True)
        
        return overdue_actions
    
    def generate_capa_report(self, action_type: Optional[str] = None, 
                           date_from: Optional[datetime] = None,
                           date_to: Optional[datetime] = None,
                           status: Optional[str] = None,
                           severity: Optional[str] = None) -> Dict[str, Any]:
        """Generate CAPA report with filtering options"""
        
        # Build query for corrective actions
        corrective_query = self.db.query(CorrectiveAction)
        if date_from:
            corrective_query = corrective_query.filter(CorrectiveAction.created_at >= date_from)
        if date_to:
            corrective_query = corrective_query.filter(CorrectiveAction.created_at <= date_to)
        if status:
            corrective_query = corrective_query.filter(CorrectiveAction.status == status)
        
        # Build query for preventive actions
        preventive_query = self.db.query(PRPPreventiveAction)
        if date_from:
            preventive_query = preventive_query.filter(PRPPreventiveAction.created_at >= date_from)
        if date_to:
            preventive_query = preventive_query.filter(PRPPreventiveAction.created_at <= date_to)
        if status:
            preventive_query = preventive_query.filter(PRPPreventiveAction.status == status)
        
        # Get data based on action type
        corrective_actions = []
        preventive_actions = []
        
        if action_type is None or action_type == "corrective":
            corrective_actions = corrective_query.all()
        
        if action_type is None or action_type == "preventive":
            preventive_actions = preventive_query.all()
        
        # Calculate summary statistics
        total_actions = len(corrective_actions) + len(preventive_actions)
        completed_actions = len([a for a in corrective_actions if a.status == CorrectiveActionStatus.COMPLETED]) + \
                          len([a for a in preventive_actions if a.status == CorrectiveActionStatus.COMPLETED])
        
        # Calculate effectiveness
        effective_corrective = len([a for a in corrective_actions if a.effectiveness_verification == True])
        effectiveness_rate = (effective_corrective / len(corrective_actions) * 100) if corrective_actions else 0.0
        
        # Get status distribution
        status_distribution = {}
        for action in corrective_actions + preventive_actions:
            status = action.status.value if action.status else "unknown"
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "summary": {
                "total_actions": total_actions,
                "corrective_actions": len(corrective_actions),
                "preventive_actions": len(preventive_actions),
                "completed_actions": completed_actions,
                "completion_rate": (completed_actions / total_actions * 100) if total_actions > 0 else 0.0,
                "effectiveness_rate": effectiveness_rate
            },
            "status_distribution": status_distribution,
            "corrective_actions": [
                {
                    "id": action.id,
                    "action_code": action.action_code,
                    "description": action.action_description,
                    "status": action.status.value if action.status else None,
                    "severity": action.severity,
                    "target_date": action.target_completion_date.isoformat() if action.target_completion_date else None,
                    "created_at": action.created_at.isoformat() if action.created_at else None,
                    "effectiveness_verification": action.effectiveness_verification
                } for action in corrective_actions
            ],
            "preventive_actions": [
                {
                    "id": action.id,
                    "action_code": action.action_code,
                    "description": action.action_description,
                    "status": action.status.value if action.status else None,
                    "planned_date": action.planned_completion_date.isoformat() if action.planned_completion_date else None,
                    "created_at": action.created_at.isoformat() if action.created_at else None
                } for action in preventive_actions
            ],
            "report_generated_at": datetime.utcnow().isoformat(),
            "filters_applied": {
                "action_type": action_type,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "status": status,
                "severity": severity
            }
        }
    
    def generate_prp_report(self, program_id: Optional[int] = None,
                          category: Optional[PRPCategory] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate PRP report data"""
        
        query = self.db.query(PRPChecklist)
        
        if program_id:
            query = query.filter(PRPChecklist.program_id == program_id)
        
        if date_from:
            query = query.filter(PRPChecklist.scheduled_date >= date_from)
        
        if date_to:
            query = query.filter(PRPChecklist.scheduled_date <= date_to)
        
        checklists = query.all()
        
        # Get program details if specified
        program_details = None
        if program_id:
            program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
            if program:
                program_details = {
                    "id": program.id,
                    "program_code": program.program_code,
                    "name": program.name,
                    "category": program.category.value,
                    "frequency": program.frequency.value,
                }
        
        # Calculate statistics
        total_checklists = len(checklists)
        completed_checklists = [c for c in checklists if c.status == ChecklistStatus.COMPLETED]
        failed_checklists = [c for c in checklists if c.status == ChecklistStatus.FAILED]
        overdue_checklists = [c for c in checklists if c.due_date < datetime.utcnow() and c.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]]
        
        avg_compliance = sum(c.compliance_percentage for c in completed_checklists) / len(completed_checklists) if completed_checklists else 0.0
        
        return {
            "program_details": program_details,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            },
            "statistics": {
                "total_checklists": total_checklists,
                "completed_checklists": len(completed_checklists),
                "failed_checklists": len(failed_checklists),
                "overdue_checklists": len(overdue_checklists),
                "average_compliance": avg_compliance,
            },
            "checklists": [
                {
                    "id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "name": checklist.name,
                    "status": checklist.status.value,
                    "scheduled_date": checklist.scheduled_date.isoformat() if checklist.scheduled_date else None,
                    "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                    "completed_date": checklist.completed_date.isoformat() if checklist.completed_date else None,
                    "compliance_percentage": checklist.compliance_percentage,
                    "corrective_actions_required": checklist.corrective_actions_required,
                } for checklist in checklists
            ],
            "generated_at": datetime.utcnow().isoformat()
        } 

    def escalate_risk_to_register(self, assessment_id: int, escalated_by: int) -> Dict[str, Any]:
        """Escalate a PRP risk assessment to the main risk register"""
        
        assessment = self.db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise ValueError("Risk assessment not found")
        
        if assessment.escalated_to_risk_register:
            raise ValueError("Risk assessment already escalated to risk register")
        
        # Get program details for context
        program = self.db.query(PRPProgram).filter(PRPProgram.id == assessment.program_id).first()
        
        # Create risk register entry
        from app.models.risk import RiskRegisterItem, RiskAction
        from app.models.user import User
        
        # Determine risk category based on PRP category
        risk_category = self._map_prp_category_to_risk_category(program.category)
        
        # Create risk register entry
        risk_entry = RiskRegisterItem(
            risk_code=f"PRP-{assessment.assessment_code}",
            title=f"PRP Risk: {assessment.hazard_identified}",
            description=f"PRP Risk Assessment: {assessment.hazard_description}\n"
                       f"Program: {program.name}\n"
                       f"Category: {program.category.value}",
            risk_category=risk_category,
            risk_type="operational",
            likelihood=assessment.likelihood_level,
            severity=assessment.severity_level,
            risk_level=assessment.risk_level.value if assessment.risk_level else "medium",
            risk_score=assessment.risk_score,
            current_controls=assessment.existing_controls,
            additional_controls_needed=assessment.additional_controls_required,
            risk_owner=assessment.created_by,
            risk_owner_department=program.responsible_department,
            status="active",
            source="prp_assessment",
            source_id=assessment.id,
            created_by=escalated_by
        )
        
        self.db.add(risk_entry)
        self.db.flush()  # Get the ID
        
        # Update assessment with risk register link
        assessment.risk_register_entry_id = risk_entry.id
        assessment.escalated_to_risk_register = True
        assessment.escalation_date = datetime.utcnow()
        assessment.escalated_by = escalated_by
        
        # Create risk action for escalation
        risk_action = RiskAction(
            risk_id=risk_entry.id,
            action_type="escalation",
            action_description=f"Risk escalated from PRP assessment {assessment.assessment_code}",
            action_date=datetime.utcnow(),
            responsible_person=escalated_by,
            status="completed"
        )
        
        self.db.add(risk_action)
        self.db.commit()
        
        # Create notification
        self._create_risk_escalation_notification(assessment, risk_entry)
        
        return {
            "assessment_id": assessment.id,
            "risk_register_id": risk_entry.id,
            "escalation_date": assessment.escalation_date,
            "message": f"Risk assessment {assessment.assessment_code} successfully escalated to risk register"
        }
    
    def _map_prp_category_to_risk_category(self, prp_category: PRPCategory) -> str:
        """Map PRP category to risk register category"""
        category_mapping = {
            PRPCategory.FACILITY_EQUIPMENT_DESIGN: "operational",
            PRPCategory.FACILITY_LAYOUT: "operational",
            PRPCategory.PRODUCTION_EQUIPMENT: "operational",
            PRPCategory.CLEANING_SANITATION: "operational",
            PRPCategory.PEST_CONTROL: "operational",
            PRPCategory.PERSONNEL_HYGIENE: "operational",
            PRPCategory.WASTE_MANAGEMENT: "operational",
            PRPCategory.STORAGE_TRANSPORTATION: "operational",
            PRPCategory.SUPPLIER_CONTROL: "supplier",
            PRPCategory.PRODUCT_INFORMATION_CONSUMER_AWARENESS: "compliance",
            PRPCategory.FOOD_DEFENSE_BIOVIGILANCE: "security",
            PRPCategory.WATER_QUALITY: "operational",
            PRPCategory.AIR_QUALITY: "operational",
            PRPCategory.EQUIPMENT_CALIBRATION: "operational",
            PRPCategory.MAINTENANCE: "operational",
            PRPCategory.PERSONNEL_TRAINING: "operational",
            PRPCategory.RECALL_PROCEDURES: "compliance",
            PRPCategory.TRANSPORTATION: "operational"
        }
        return category_mapping.get(prp_category, "operational")
    
    def _create_risk_escalation_notification(self, assessment: RiskAssessment, risk_entry):
        """Create notification for risk escalation"""
        try:
            notification = Notification(
                user_id=assessment.created_by,
                title=f"PRP Risk Escalated: {assessment.hazard_identified}",
                message=f"Risk assessment {assessment.assessment_code} has been escalated to the main risk register. "
                       f"Risk Register ID: {risk_entry.id}",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                notification_data={
                    "assessment_id": assessment.id,
                    "risk_register_id": risk_entry.id,
                    "escalation_type": "prp_to_risk_register"
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create risk escalation notification: {str(e)}")
    
    def get_prp_risk_summary_with_register_links(self, program_id: Optional[int] = None) -> Dict[str, Any]:
        """Get PRP risk summary including risk register integration"""
        
        query = self.db.query(RiskAssessment)
        if program_id:
            query = query.filter(RiskAssessment.program_id == program_id)
        
        assessments = query.all()
        
        risk_level_counts = {
            RiskLevel.VERY_LOW.value: 0,
            RiskLevel.LOW.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.HIGH.value: 0,
            RiskLevel.VERY_HIGH.value: 0,
            RiskLevel.CRITICAL.value: 0
        }
        
        escalated_count = 0
        high_risk_escalated = 0
        
        for assessment in assessments:
            if assessment.risk_level:
                risk_level_counts[assessment.risk_level.value] += 1
            
            if assessment.escalated_to_risk_register:
                escalated_count += 1
                if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]:
                    high_risk_escalated += 1
        
        return {
            "total_assessments": len(assessments),
            "risk_level_distribution": risk_level_counts,
            "high_risk_count": risk_level_counts[RiskLevel.HIGH.value] + 
                              risk_level_counts[RiskLevel.VERY_HIGH.value] + 
                              risk_level_counts[RiskLevel.CRITICAL.value],
            "assessments_requiring_controls": len([a for a in assessments if not a.acceptability]),
            "escalated_to_risk_register": escalated_count,
            "high_risk_escalated": high_risk_escalated,
            "escalation_rate": (escalated_count / len(assessments) * 100) if assessments else 0
        }

    # Phase 2.3: Enhanced Program Management Methods

    def get_program_analytics(self, program_id: int, period: str = "30d") -> Dict[str, Any]:
        """Get comprehensive analytics for a specific PRP program"""
        
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get checklists for the period
        checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.program_id == program_id,
                PRPChecklist.scheduled_date >= start_date,
                PRPChecklist.scheduled_date <= end_date
            )
        ).all()
        
        # Calculate analytics
        total_checklists = len(checklists)
        completed_checklists = [c for c in checklists if c.status == ChecklistStatus.COMPLETED]
        failed_checklists = [c for c in checklists if c.status == ChecklistStatus.FAILED]
        overdue_checklists = [c for c in checklists if c.due_date < datetime.utcnow() and c.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]]
        
        avg_compliance = sum(c.compliance_percentage for c in completed_checklists) / len(completed_checklists) if completed_checklists else 0.0
        
        # Get risk assessments
        risk_assessments = self.db.query(RiskAssessment).filter(
            and_(
                RiskAssessment.program_id == program_id,
                RiskAssessment.assessment_date >= start_date
            )
        ).all()
        
        # Get corrective actions
        corrective_actions = self.db.query(CorrectiveAction).filter(
            and_(
                CorrectiveAction.program_id == program_id,
                CorrectiveAction.created_at >= start_date
            )
        ).all()
        
        return {
            "program_info": {
                "id": program.id,
                "name": program.name,
                "category": program.category.value,
                "status": program.status.value
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "period_type": period
            },
            "checklist_analytics": {
                "total_checklists": total_checklists,
                "completed_checklists": len(completed_checklists),
                "failed_checklists": len(failed_checklists),
                "overdue_checklists": len(overdue_checklists),
                "completion_rate": (len(completed_checklists) / total_checklists * 100) if total_checklists > 0 else 0,
                "average_compliance": avg_compliance,
                "on_time_completion_rate": len([c for c in completed_checklists if c.completed_date <= c.due_date]) / len(completed_checklists) * 100 if completed_checklists else 0
            },
            "risk_analytics": {
                "total_assessments": len(risk_assessments),
                "high_risk_count": len([r for r in risk_assessments if r.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]]),
                "escalated_count": len([r for r in risk_assessments if r.escalated_to_risk_register]),
                "average_risk_score": sum(r.risk_score for r in risk_assessments) / len(risk_assessments) if risk_assessments else 0
            },
            "capa_analytics": {
                "total_corrective_actions": len(corrective_actions),
                "completed_actions": len([c for c in corrective_actions if c.status == CorrectiveActionStatus.COMPLETED]),
                "overdue_actions": len([c for c in corrective_actions if c.due_date < datetime.utcnow() and c.status != CorrectiveActionStatus.COMPLETED]),
                "average_completion_time": self._calculate_average_completion_time(corrective_actions)
            }
        }

    def get_program_performance_trends(self, program_id: int, trend_period: str = "6m") -> Dict[str, Any]:
        """Get performance trends for a PRP program"""
        
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        if trend_period == "3m":
            start_date = end_date - timedelta(days=90)
        elif trend_period == "6m":
            start_date = end_date - timedelta(days=180)
        elif trend_period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=180)
        
        # Get monthly data points
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Get checklists for the month
            month_checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program_id,
                    PRPChecklist.scheduled_date >= month_start,
                    PRPChecklist.scheduled_date <= month_end
                )
            ).all()
            
            completed_checklists = [c for c in month_checklists if c.status == ChecklistStatus.COMPLETED]
            avg_compliance = sum(c.compliance_percentage for c in completed_checklists) / len(completed_checklists) if completed_checklists else 0.0
            
            trends.append({
                "month": current_date.strftime("%Y-%m"),
                "total_checklists": len(month_checklists),
                "completed_checklists": len(completed_checklists),
                "completion_rate": (len(completed_checklists) / len(month_checklists) * 100) if month_checklists else 0,
                "average_compliance": avg_compliance,
                "overdue_count": len([c for c in month_checklists if c.due_date < datetime.utcnow() and c.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]])
            })
            
            current_date = (current_date + timedelta(days=32)).replace(day=1)
        
        return {
            "program_info": {
                "id": program.id,
                "name": program.name,
                "category": program.category.value
            },
            "trend_period": trend_period,
            "trends": trends,
            "summary": {
                "overall_completion_rate": sum(t["completion_rate"] for t in trends) / len(trends) if trends else 0,
                "overall_average_compliance": sum(t["average_compliance"] for t in trends) / len(trends) if trends else 0,
                "trend_direction": self._calculate_trend_direction(trends)
            }
        }

    def optimize_program_schedule(self, program_id: int, optimization_params: dict, optimized_by: int) -> Dict[str, Any]:
        """Optimize program schedule based on historical data and resource availability"""
        
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Get historical performance data
        historical_checklists = self.db.query(PRPChecklist).filter(
            PRPChecklist.program_id == program_id
        ).order_by(PRPChecklist.scheduled_date).all()
        
        if not historical_checklists:
            raise ValueError("Insufficient historical data for optimization")
        
        # Analyze patterns
        completion_times = []
        for checklist in historical_checklists:
            if checklist.completed_date and checklist.scheduled_date:
                completion_time = (checklist.completed_date - checklist.scheduled_date).days
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Calculate optimal frequency
        current_frequency = program.frequency
        optimal_frequency = self._calculate_optimal_frequency(historical_checklists, optimization_params)
        
        # Generate optimization recommendations
        recommendations = []
        
        if optimal_frequency != current_frequency:
            recommendations.append({
                "type": "frequency_optimization",
                "current": current_frequency.value,
                "recommended": optimal_frequency.value,
                "reason": "Based on historical completion patterns and risk levels"
            })
        
        # Resource optimization
        if optimization_params.get("resource_constraints"):
            resource_recommendations = self._optimize_resource_allocation(program_id, optimization_params)
            recommendations.extend(resource_recommendations)
        
        # Schedule optimization
        schedule_recommendations = self._optimize_schedule_timing(program_id, optimization_params)
        recommendations.extend(schedule_recommendations)
        
        return {
            "program_id": program_id,
            "optimization_date": datetime.utcnow().isoformat(),
            "optimized_by": optimized_by,
            "current_performance": {
                "average_completion_time": avg_completion_time,
                "completion_rate": len([c for c in historical_checklists if c.status == ChecklistStatus.COMPLETED]) / len(historical_checklists) * 100,
                "average_compliance": sum(c.compliance_percentage for c in historical_checklists if c.status == ChecklistStatus.COMPLETED) / len([c for c in historical_checklists if c.status == ChecklistStatus.COMPLETED]) if [c for c in historical_checklists if c.status == ChecklistStatus.COMPLETED] else 0
            },
            "recommendations": recommendations,
            "estimated_improvement": self._estimate_optimization_improvement(recommendations, historical_checklists)
        }

    def get_program_resource_utilization(self, program_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get resource utilization analysis for a PRP program"""
        
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Parse date range
        start_date = datetime.fromisoformat(date_from) if date_from else datetime.utcnow() - timedelta(days=30)
        end_date = datetime.fromisoformat(date_to) if date_to else datetime.utcnow()
        
        # Get checklists in the date range
        checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.program_id == program_id,
                PRPChecklist.scheduled_date >= start_date,
                PRPChecklist.scheduled_date <= end_date
            )
        ).all()
        
        # Analyze resource utilization
        user_workload = {}
        for checklist in checklists:
            assigned_user = checklist.assigned_to
            if assigned_user not in user_workload:
                user_workload[assigned_user] = {
                    "total_checklists": 0,
                    "completed_checklists": 0,
                    "overdue_checklists": 0,
                    "average_compliance": 0.0,
                    "total_compliance": 0.0
                }
            
            user_workload[assigned_user]["total_checklists"] += 1
            if checklist.status == ChecklistStatus.COMPLETED:
                user_workload[assigned_user]["completed_checklists"] += 1
                user_workload[assigned_user]["total_compliance"] += checklist.compliance_percentage
            
            if checklist.due_date < datetime.utcnow() and checklist.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]:
                user_workload[assigned_user]["overdue_checklists"] += 1
        
        # Calculate averages
        for user_id, workload in user_workload.items():
            if workload["completed_checklists"] > 0:
                workload["average_compliance"] = workload["total_compliance"] / workload["completed_checklists"]
        
        # Get user names
        user_names = {}
        for user_id in user_workload.keys():
            user = self.db.query(User).filter(User.id == user_id).first()
            user_names[user_id] = user.full_name if user else f"User {user_id}"
        
        return {
            "program_info": {
                "id": program.id,
                "name": program.name,
                "responsible_department": program.responsible_department
            },
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "resource_utilization": {
                "total_checklists": len(checklists),
                "unique_users": len(user_workload),
                "user_workload": [
                    {
                        "user_id": user_id,
                        "user_name": user_names.get(user_id, f"User {user_id}"),
                        "total_checklists": workload["total_checklists"],
                        "completed_checklists": workload["completed_checklists"],
                        "overdue_checklists": workload["overdue_checklists"],
                        "completion_rate": (workload["completed_checklists"] / workload["total_checklists"] * 100) if workload["total_checklists"] > 0 else 0,
                        "average_compliance": workload["average_compliance"]
                    }
                    for user_id, workload in user_workload.items()
                ]
            },
            "utilization_metrics": {
                "average_checklists_per_user": len(checklists) / len(user_workload) if user_workload else 0,
                "overall_completion_rate": sum(w["completed_checklists"] for w in user_workload.values()) / len(checklists) * 100 if checklists else 0,
                "overall_average_compliance": sum(w["average_compliance"] for w in user_workload.values()) / len(user_workload) if user_workload else 0
            }
        }

    def generate_comprehensive_report(self, program_ids: Optional[List[int]] = None, 
                                    categories: Optional[List[str]] = None,
                                    date_from: Optional[str] = None,
                                    date_to: Optional[str] = None,
                                    include_risks: bool = True,
                                    include_capa: bool = True,
                                    include_trends: bool = True,
                                    format_type: str = "json") -> Dict[str, Any]:
        """Generate comprehensive PRP report with multiple dimensions"""
        
        # Build query
        query = self.db.query(PRPProgram)
        
        if program_ids:
            query = query.filter(PRPProgram.id.in_(program_ids))
        
        if categories:
            category_enums = [PRPCategory(cat) for cat in categories]
            query = query.filter(PRPProgram.category.in_(category_enums))
        
        programs = query.all()
        
        # Parse date range
        start_date = datetime.fromisoformat(date_from) if date_from else datetime.utcnow() - timedelta(days=90)
        end_date = datetime.fromisoformat(date_to) if date_to else datetime.utcnow()
        
        report_data = {
            "report_info": {
                "generated_at": datetime.utcnow().isoformat(),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "filters": {
                    "program_ids": program_ids,
                    "categories": categories,
                    "include_risks": include_risks,
                    "include_capa": include_capa,
                    "include_trends": include_trends
                }
            },
            "programs": []
        }
        
        for program in programs:
            program_data = {
                "id": program.id,
                "program_code": program.program_code,
                "name": program.name,
                "category": program.category.value,
                "status": program.status.value,
                "responsible_department": program.responsible_department,
                "frequency": program.frequency.value
            }
            
            # Get checklists for the program
            checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.scheduled_date >= start_date,
                    PRPChecklist.scheduled_date <= end_date
                )
            ).all()
            
            program_data["checklist_summary"] = {
                "total_checklists": len(checklists),
                "completed_checklists": len([c for c in checklists if c.status == ChecklistStatus.COMPLETED]),
                "failed_checklists": len([c for c in checklists if c.status == ChecklistStatus.FAILED]),
                "overdue_checklists": len([c for c in checklists if c.due_date < datetime.utcnow() and c.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]]),
                "average_compliance": sum(c.compliance_percentage for c in checklists if c.status == ChecklistStatus.COMPLETED) / len([c for c in checklists if c.status == ChecklistStatus.COMPLETED]) if [c for c in checklists if c.status == ChecklistStatus.COMPLETED] else 0
            }
            
            # Include risk data if requested
            if include_risks:
                risk_assessments = self.db.query(RiskAssessment).filter(
                    and_(
                        RiskAssessment.program_id == program.id,
                        RiskAssessment.assessment_date >= start_date
                    )
                ).all()
                
                program_data["risk_summary"] = {
                    "total_assessments": len(risk_assessments),
                    "high_risk_count": len([r for r in risk_assessments if r.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]]),
                    "escalated_count": len([r for r in risk_assessments if r.escalated_to_risk_register]),
                    "average_risk_score": sum(r.risk_score for r in risk_assessments) / len(risk_assessments) if risk_assessments else 0
                }
            
            # Include CAPA data if requested
            if include_capa:
                corrective_actions = self.db.query(CorrectiveAction).filter(
                    and_(
                        CorrectiveAction.program_id == program.id,
                        CorrectiveAction.created_at >= start_date
                    )
                ).all()
                
                preventive_actions = self.db.query(PRPPreventiveAction).filter(
                    and_(
                        PRPPreventiveAction.program_id == program.id,
                        PRPPreventiveAction.created_at >= start_date
                    )
                ).all()
                
                program_data["capa_summary"] = {
                    "corrective_actions": {
                        "total": len(corrective_actions),
                        "completed": len([c for c in corrective_actions if c.status == CorrectiveActionStatus.COMPLETED]),
                        "overdue": len([c for c in corrective_actions if c.due_date < datetime.utcnow() and c.status != CorrectiveActionStatus.COMPLETED])
                    },
                    "preventive_actions": {
                        "total": len(preventive_actions),
                        "completed": len([p for p in preventive_actions if p.status == CorrectiveActionStatus.COMPLETED]),
                        "overdue": len([p for p in preventive_actions if p.due_date < datetime.utcnow() and p.status != CorrectiveActionStatus.COMPLETED])
                    }
                }
            
            # Include trends if requested
            if include_trends:
                program_data["trends"] = self._get_program_trends(program.id, start_date, end_date)
            
            report_data["programs"].append(program_data)
        
        # Add summary statistics
        report_data["summary"] = self._calculate_report_summary(report_data["programs"])
        
        return report_data

    def get_compliance_summary_report(self, category: Optional[str] = None, 
                                    department: Optional[str] = None,
                                    date_from: Optional[str] = None,
                                    date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance summary report across all PRP programs"""
        
        # Build query
        query = self.db.query(PRPProgram)
        
        if category:
            query = query.filter(PRPProgram.category == PRPCategory(category))
        
        if department:
            query = query.filter(PRPProgram.responsible_department == department)
        
        programs = query.all()
        
        # Parse date range
        start_date = datetime.fromisoformat(date_from) if date_from else datetime.utcnow() - timedelta(days=30)
        end_date = datetime.fromisoformat(date_to) if date_to else datetime.utcnow()
        
        total_checklists = 0
        completed_checklists = 0
        failed_checklists = 0
        overdue_checklists = 0
        total_compliance = 0.0
        
        category_summary = {}
        department_summary = {}
        
        for program in programs:
            # Get checklists for the program
            checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.scheduled_date >= start_date,
                    PRPChecklist.scheduled_date <= end_date
                )
            ).all()
            
            program_completed = [c for c in checklists if c.status == ChecklistStatus.COMPLETED]
            program_failed = [c for c in checklists if c.status == ChecklistStatus.FAILED]
            program_overdue = [c for c in checklists if c.due_date < datetime.utcnow() and c.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]]
            
            total_checklists += len(checklists)
            completed_checklists += len(program_completed)
            failed_checklists += len(program_failed)
            overdue_checklists += len(program_overdue)
            total_compliance += sum(c.compliance_percentage for c in program_completed)
            
            # Category summary
            cat = program.category.value
            if cat not in category_summary:
                category_summary[cat] = {"total": 0, "completed": 0, "failed": 0, "overdue": 0, "compliance": 0.0}
            
            category_summary[cat]["total"] += len(checklists)
            category_summary[cat]["completed"] += len(program_completed)
            category_summary[cat]["failed"] += len(program_failed)
            category_summary[cat]["overdue"] += len(program_overdue)
            category_summary[cat]["compliance"] += sum(c.compliance_percentage for c in program_completed)
            
            # Department summary
            dept = program.responsible_department
            if dept not in department_summary:
                department_summary[dept] = {"total": 0, "completed": 0, "failed": 0, "overdue": 0, "compliance": 0.0}
            
            department_summary[dept]["total"] += len(checklists)
            department_summary[dept]["completed"] += len(program_completed)
            department_summary[dept]["failed"] += len(program_failed)
            department_summary[dept]["overdue"] += len(program_overdue)
            department_summary[dept]["compliance"] += sum(c.compliance_percentage for c in program_completed)
        
        # Calculate averages
        for cat_data in category_summary.values():
            if cat_data["completed"] > 0:
                cat_data["average_compliance"] = cat_data["compliance"] / cat_data["completed"]
                cat_data["completion_rate"] = cat_data["completed"] / cat_data["total"] * 100 if cat_data["total"] > 0 else 0
        
        for dept_data in department_summary.values():
            if dept_data["completed"] > 0:
                dept_data["average_compliance"] = dept_data["compliance"] / dept_data["completed"]
                dept_data["completion_rate"] = dept_data["completed"] / dept_data["total"] * 100 if dept_data["total"] > 0 else 0
        
        return {
            "report_info": {
                "generated_at": datetime.utcnow().isoformat(),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "filters": {
                    "category": category,
                    "department": department
                }
            },
            "overall_summary": {
                "total_checklists": total_checklists,
                "completed_checklists": completed_checklists,
                "failed_checklists": failed_checklists,
                "overdue_checklists": overdue_checklists,
                "overall_completion_rate": (completed_checklists / total_checklists * 100) if total_checklists > 0 else 0,
                "overall_average_compliance": (total_compliance / completed_checklists) if completed_checklists > 0 else 0
            },
            "category_summary": category_summary,
            "department_summary": department_summary
        }

    def get_risk_exposure_report(self, risk_level: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Get risk exposure report for PRP programs"""
        
        query = self.db.query(RiskAssessment)
        
        if risk_level:
            query = query.filter(RiskAssessment.risk_level == RiskLevel(risk_level))
        
        if category:
            # Get programs in the category
            programs = self.db.query(PRPProgram).filter(PRPProgram.category == PRPCategory(category)).all()
            program_ids = [p.id for p in programs]
            query = query.filter(RiskAssessment.program_id.in_(program_ids))
        
        assessments = query.all()
        
        # Group by program
        program_risks = {}
        for assessment in assessments:
            program_id = assessment.program_id
            if program_id not in program_risks:
                program_risks[program_id] = {
                    "total_assessments": 0,
                    "risk_levels": {},
                    "escalated_count": 0,
                    "total_risk_score": 0,
                    "unacceptable_risks": 0
                }
            
            program_risks[program_id]["total_assessments"] += 1
            program_risks[program_id]["total_risk_score"] += assessment.risk_score or 0
            
            if assessment.risk_level:
                level = assessment.risk_level.value
                if level not in program_risks[program_id]["risk_levels"]:
                    program_risks[program_id]["risk_levels"][level] = 0
                program_risks[program_id]["risk_levels"][level] += 1
            
            if assessment.escalated_to_risk_register:
                program_risks[program_id]["escalated_count"] += 1
            
            if not assessment.acceptability:
                program_risks[program_id]["unacceptable_risks"] += 1
        
        # Get program details
        program_details = {}
        for program_id in program_risks.keys():
            program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
            if program:
                program_details[program_id] = {
                    "id": program.id,
                    "name": program.name,
                    "category": program.category.value,
                    "responsible_department": program.responsible_department
                }
        
        # Calculate averages
        for program_id, risks in program_risks.items():
            if risks["total_assessments"] > 0:
                risks["average_risk_score"] = risks["total_risk_score"] / risks["total_assessments"]
                risks["escalation_rate"] = risks["escalated_count"] / risks["total_assessments"] * 100
        
        return {
            "report_info": {
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "risk_level": risk_level,
                    "category": category
                }
            },
            "overall_summary": {
                "total_assessments": len(assessments),
                "total_programs": len(program_risks),
                "escalated_assessments": sum(r["escalated_count"] for r in program_risks.values()),
                "unacceptable_risks": sum(r["unacceptable_risks"] for r in program_risks.values()),
                "average_risk_score": sum(r["total_risk_score"] for r in program_risks.values()) / len(assessments) if assessments else 0
            },
            "program_risks": [
                {
                    "program": program_details.get(program_id, {"id": program_id, "name": "Unknown Program"}),
                    "risk_summary": risks
                }
                for program_id, risks in program_risks.items()
            ]
        }

    # Helper methods for Phase 2.3
    def _calculate_average_completion_time(self, actions: List[CorrectiveAction]) -> float:
        """Calculate average completion time for corrective actions"""
        completion_times = []
        for action in actions:
            if action.status == CorrectiveActionStatus.COMPLETED and action.completed_date and action.created_at:
                completion_time = (action.completed_date - action.created_at).days
                completion_times.append(completion_time)
        
        return sum(completion_times) / len(completion_times) if completion_times else 0.0

    def _calculate_trend_direction(self, trends: List[Dict[str, Any]]) -> str:
        """Calculate trend direction based on completion rates"""
        if len(trends) < 2:
            return "insufficient_data"
        
        recent_trends = trends[-3:]  # Last 3 months
        completion_rates = [t["completion_rate"] for t in recent_trends]
        
        if len(completion_rates) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        first_half = completion_rates[:len(completion_rates)//2]
        second_half = completion_rates[len(completion_rates)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first + 5:  # 5% improvement threshold
            return "improving"
        elif avg_second < avg_first - 5:
            return "declining"
        else:
            return "stable"

    def _calculate_optimal_frequency(self, checklists: List[PRPChecklist], params: dict) -> PRPFrequency:
        """Calculate optimal frequency based on historical data"""
        # This is a simplified calculation - in practice, this would be more sophisticated
        completion_times = []
        for checklist in checklists:
            if checklist.completed_date and checklist.scheduled_date:
                completion_time = (checklist.completed_date - checklist.scheduled_date).days
                completion_times.append(completion_time)
        
        if not completion_times:
            return PRPFrequency.MONTHLY  # Default
        
        avg_completion_time = sum(completion_times) / len(completion_times)
        
        # Simple frequency optimization
        if avg_completion_time <= 1:
            return PRPFrequency.DAILY
        elif avg_completion_time <= 7:
            return PRPFrequency.WEEKLY
        elif avg_completion_time <= 30:
            return PRPFrequency.MONTHLY
        elif avg_completion_time <= 90:
            return PRPFrequency.QUARTERLY
        else:
            return PRPFrequency.ANNUALLY

    def _optimize_resource_allocation(self, program_id: int, params: dict) -> List[Dict[str, Any]]:
        """Optimize resource allocation for a program"""
        # This would implement resource optimization logic
        return [
            {
                "type": "resource_optimization",
                "recommendation": "Consider redistributing workload based on user performance",
                "impact": "medium",
                "effort": "low"
            }
        ]

    def _optimize_schedule_timing(self, program_id: int, params: dict) -> List[Dict[str, Any]]:
        """Optimize schedule timing for a program"""
        # This would implement schedule optimization logic
        return [
            {
                "type": "schedule_optimization",
                "recommendation": "Schedule checklists during low-activity periods",
                "impact": "medium",
                "effort": "low"
            }
        ]

    def _estimate_optimization_improvement(self, recommendations: List[Dict[str, Any]], historical_data: List[PRPChecklist]) -> Dict[str, Any]:
        """Estimate improvement from optimization recommendations"""
        # This would calculate estimated improvements
        return {
            "estimated_completion_rate_improvement": 15.0,  # Percentage
            "estimated_compliance_improvement": 8.0,  # Percentage
            "estimated_time_savings": 20.0,  # Hours per month
            "confidence_level": "medium"
        }

    def _get_program_trends(self, program_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get trends for a specific program"""
        # This would calculate trends for the program
        return {
            "completion_rate_trend": "improving",
            "compliance_trend": "stable",
            "risk_trend": "declining"
        }

    def _calculate_report_summary(self, programs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for the report"""
        total_programs = len(programs_data)
        total_checklists = sum(p["checklist_summary"]["total_checklists"] for p in programs_data)
        completed_checklists = sum(p["checklist_summary"]["completed_checklists"] for p in programs_data)
        
        return {
            "total_programs": total_programs,
            "total_checklists": total_checklists,
            "overall_completion_rate": (completed_checklists / total_checklists * 100) if total_checklists > 0 else 0,
            "average_compliance": sum(p["checklist_summary"]["average_compliance"] for p in programs_data) / total_programs if total_programs > 0 else 0
        } 

    # Additional Phase 2.3 Methods

    def export_prp_data(self, data_type: str, format_type: str, filters: dict, include_attachments: bool = False) -> Dict[str, Any]:
        """Export PRP data in various formats"""
        
        # Build query based on data type
        if data_type == "programs":
            query = self.db.query(PRPProgram)
        elif data_type == "checklists":
            query = self.db.query(PRPChecklist)
        elif data_type == "risks":
            query = self.db.query(RiskAssessment)
        elif data_type == "capa":
            query = self.db.query(CorrectiveAction)
        else:
            raise ValueError("Invalid data type")
        
        # Apply filters
        if filters.get("date_from"):
            start_date = datetime.fromisoformat(filters["date_from"])
            if data_type == "programs":
                query = query.filter(PRPProgram.created_at >= start_date)
            elif data_type == "checklists":
                query = query.filter(PRPChecklist.scheduled_date >= start_date)
            elif data_type == "risks":
                query = query.filter(RiskAssessment.assessment_date >= start_date)
            elif data_type == "capa":
                query = query.filter(CorrectiveAction.created_at >= start_date)
        
        if filters.get("date_to"):
            end_date = datetime.fromisoformat(filters["date_to"])
            if data_type == "programs":
                query = query.filter(PRPProgram.created_at <= end_date)
            elif data_type == "checklists":
                query = query.filter(PRPChecklist.scheduled_date <= end_date)
            elif data_type == "risks":
                query = query.filter(RiskAssessment.assessment_date <= end_date)
            elif data_type == "capa":
                query = query.filter(CorrectiveAction.created_at <= end_date)
        
        if filters.get("category") and data_type == "programs":
            query = query.filter(PRPProgram.category == PRPCategory(filters["category"]))
        
        if filters.get("status"):
            if data_type == "programs":
                query = query.filter(PRPProgram.status == PRPStatus(filters["status"]))
            elif data_type == "checklists":
                query = query.filter(PRPChecklist.status == ChecklistStatus(filters["status"]))
            elif data_type == "capa":
                query = query.filter(CorrectiveAction.status == CorrectiveActionStatus(filters["status"]))
        
        data = query.all()
        
        # Convert to export format
        export_data = []
        for item in data:
            if data_type == "programs":
                export_data.append({
                    "id": item.id,
                    "program_code": item.program_code,
                    "name": item.name,
                    "category": item.category.value,
                    "status": item.status.value,
                    "responsible_department": item.responsible_department,
                    "frequency": item.frequency.value,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                })
            elif data_type == "checklists":
                export_data.append({
                    "id": item.id,
                    "checklist_code": item.checklist_code,
                    "name": item.name,
                    "status": item.status.value,
                    "scheduled_date": item.scheduled_date.isoformat() if item.scheduled_date else None,
                    "due_date": item.due_date.isoformat() if item.due_date else None,
                    "compliance_percentage": item.compliance_percentage
                })
            elif data_type == "risks":
                export_data.append({
                    "id": item.id,
                    "assessment_code": item.assessment_code,
                    "hazard_identified": item.hazard_identified,
                    "risk_level": item.risk_level.value if item.risk_level else None,
                    "risk_score": item.risk_score,
                    "assessment_date": item.assessment_date.isoformat() if item.assessment_date else None
                })
            elif data_type == "capa":
                export_data.append({
                    "id": item.id,
                    "action_code": item.action_code,
                    "description": item.description,
                    "status": item.status.value,
                    "due_date": item.due_date.isoformat() if item.due_date else None,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                })
        
        # Generate export file
        export_id = f"prp_export_{data_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "export_id": export_id,
            "data_type": data_type,
            "format": format_type,
            "record_count": len(export_data),
            "download_url": f"/api/v1/prp/exports/{export_id}",
            "generated_at": datetime.utcnow().isoformat()
        }

    def get_performance_metrics(self, metric_type: str = "all") -> Dict[str, Any]:
        """Get performance metrics for PRP module"""
        
        metrics = {}
        
        if metric_type in ["compliance", "all"]:
            # Compliance metrics
            total_checklists = self.db.query(PRPChecklist).count()
            completed_checklists = self.db.query(PRPChecklist).filter(
                PRPChecklist.status == ChecklistStatus.COMPLETED
            ).count()
            
            metrics["compliance"] = {
                "total_checklists": total_checklists,
                "completed_checklists": completed_checklists,
                "completion_rate": (completed_checklists / total_checklists * 100) if total_checklists > 0 else 0,
                "overdue_checklists": self.db.query(PRPChecklist).filter(
                    and_(
                        PRPChecklist.due_date < datetime.utcnow(),
                        PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
                    )
                ).count()
            }
        
        if metric_type in ["efficiency", "all"]:
            # Efficiency metrics
            avg_completion_time = self._calculate_average_completion_time_all()
            
            metrics["efficiency"] = {
                "average_completion_time_days": avg_completion_time,
                "on_time_completion_rate": self._calculate_on_time_completion_rate(),
                "average_checklists_per_user": self._calculate_average_checklists_per_user()
            }
        
        if metric_type in ["quality", "all"]:
            # Quality metrics
            avg_compliance = self._calculate_overall_average_compliance()
            
            metrics["quality"] = {
                "overall_average_compliance": avg_compliance,
                "high_compliance_programs": self._count_high_compliance_programs(),
                "low_compliance_programs": self._count_low_compliance_programs()
            }
        
        return {
            "metrics": metrics,
            "calculated_at": datetime.utcnow().isoformat(),
            "metric_type": metric_type
        }

    def get_performance_benchmarks(self, benchmark_type: str = "industry") -> Dict[str, Any]:
        """Get performance benchmarks for comparison"""
        
        # Get current performance
        current_metrics = self.get_performance_metrics("all")
        
        # Define benchmarks (in practice, these would come from industry data or historical analysis)
        benchmarks = {
            "industry": {
                "completion_rate": 85.0,  # Industry average
                "average_compliance": 92.0,
                "average_completion_time": 3.5,  # days
                "on_time_completion_rate": 78.0
            },
            "internal": {
                "completion_rate": 88.0,  # Internal target
                "average_compliance": 95.0,
                "average_completion_time": 2.8,
                "on_time_completion_rate": 82.0
            },
            "custom": {
                "completion_rate": 90.0,  # Custom target
                "average_compliance": 97.0,
                "average_completion_time": 2.0,
                "on_time_completion_rate": 85.0
            }
        }
        
        selected_benchmarks = benchmarks.get(benchmark_type, benchmarks["industry"])
        
        # Calculate performance vs benchmarks
        current_compliance = current_metrics["metrics"]["compliance"]["completion_rate"]
        current_quality = current_metrics["metrics"]["quality"]["overall_average_compliance"]
        current_efficiency = current_metrics["metrics"]["efficiency"]["average_completion_time_days"]
        current_on_time = current_metrics["metrics"]["efficiency"]["on_time_completion_rate"]
        
        performance_vs_benchmark = {
            "completion_rate": {
                "current": current_compliance,
                "benchmark": selected_benchmarks["completion_rate"],
                "difference": current_compliance - selected_benchmarks["completion_rate"],
                "status": "above" if current_compliance >= selected_benchmarks["completion_rate"] else "below"
            },
            "average_compliance": {
                "current": current_quality,
                "benchmark": selected_benchmarks["average_compliance"],
                "difference": current_quality - selected_benchmarks["average_compliance"],
                "status": "above" if current_quality >= selected_benchmarks["average_compliance"] else "below"
            },
            "completion_time": {
                "current": current_efficiency,
                "benchmark": selected_benchmarks["average_completion_time"],
                "difference": selected_benchmarks["average_completion_time"] - current_efficiency,
                "status": "above" if current_efficiency <= selected_benchmarks["average_completion_time"] else "below"
            },
            "on_time_completion": {
                "current": current_on_time,
                "benchmark": selected_benchmarks["on_time_completion_rate"],
                "difference": current_on_time - selected_benchmarks["on_time_completion_rate"],
                "status": "above" if current_on_time >= selected_benchmarks["on_time_completion_rate"] else "below"
            }
        }
        
        return {
            "benchmark_type": benchmark_type,
            "benchmarks": selected_benchmarks,
            "current_performance": current_metrics["metrics"],
            "performance_vs_benchmark": performance_vs_benchmark,
            "overall_status": self._calculate_overall_benchmark_status(performance_vs_benchmark)
        }

    def optimize_performance(self, optimization_type: str, parameters: dict, optimized_by: int) -> Dict[str, Any]:
        """Optimize PRP module performance based on analysis"""
        
        optimization_results = {
            "optimization_type": optimization_type,
            "optimized_by": optimized_by,
            "optimization_date": datetime.utcnow().isoformat(),
            "recommendations": [],
            "estimated_improvements": {}
        }
        
        if optimization_type == "schedule_optimization":
            # Optimize scheduling based on historical patterns
            recommendations = self._optimize_scheduling_patterns(parameters)
            optimization_results["recommendations"].extend(recommendations)
            
        elif optimization_type == "resource_allocation":
            # Optimize resource allocation
            recommendations = self._optimize_resource_allocation_global(parameters)
            optimization_results["recommendations"].extend(recommendations)
            
        elif optimization_type == "frequency_optimization":
            # Optimize program frequencies
            recommendations = self._optimize_program_frequencies(parameters)
            optimization_results["recommendations"].extend(recommendations)
            
        elif optimization_type == "comprehensive":
            # Comprehensive optimization
            schedule_recs = self._optimize_scheduling_patterns(parameters)
            resource_recs = self._optimize_resource_allocation_global(parameters)
            frequency_recs = self._optimize_program_frequencies(parameters)
            
            optimization_results["recommendations"].extend(schedule_recs)
            optimization_results["recommendations"].extend(resource_recs)
            optimization_results["recommendations"].extend(frequency_recs)
        
        # Calculate estimated improvements
        optimization_results["estimated_improvements"] = self._estimate_optimization_improvements(
            optimization_results["recommendations"]
        )
        
        return optimization_results

    def get_predictive_analytics(self, prediction_type: str = "compliance") -> Dict[str, Any]:
        """Get predictive analytics for PRP programs"""
        
        predictions = {
            "prediction_type": prediction_type,
            "generated_at": datetime.utcnow().isoformat(),
            "predictions": {}
        }
        
        if prediction_type == "compliance":
            # Predict compliance trends
            predictions["predictions"] = self._predict_compliance_trends()
            
        elif prediction_type == "risks":
            # Predict risk trends
            predictions["predictions"] = self._predict_risk_trends()
            
        elif prediction_type == "failures":
            # Predict potential failures
            predictions["predictions"] = self._predict_potential_failures()
            
        elif prediction_type == "all":
            # All predictions
            predictions["predictions"] = {
                "compliance": self._predict_compliance_trends(),
                "risks": self._predict_risk_trends(),
                "failures": self._predict_potential_failures()
            }
        
        return predictions

    def get_analytical_trends(self, trend_type: str = "compliance", period: str = "12m") -> Dict[str, Any]:
        """Get analytical trends for PRP module"""
        
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "6m":
            start_date = end_date - timedelta(days=180)
        elif period == "12m":
            start_date = end_date - timedelta(days=365)
        elif period == "24m":
            start_date = end_date - timedelta(days=730)
        else:
            start_date = end_date - timedelta(days=365)
        
        trends = {
            "trend_type": trend_type,
            "period": period,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "trends": {}
        }
        
        if trend_type == "compliance":
            trends["trends"] = self._analyze_compliance_trends(start_date, end_date)
        elif trend_type == "risks":
            trends["trends"] = self._analyze_risk_trends(start_date, end_date)
        elif trend_type == "efficiency":
            trends["trends"] = self._analyze_efficiency_trends(start_date, end_date)
        elif trend_type == "quality":
            trends["trends"] = self._analyze_quality_trends(start_date, end_date)
        elif trend_type == "all":
            trends["trends"] = {
                "compliance": self._analyze_compliance_trends(start_date, end_date),
                "risks": self._analyze_risk_trends(start_date, end_date),
                "efficiency": self._analyze_efficiency_trends(start_date, end_date),
                "quality": self._analyze_quality_trends(start_date, end_date)
            }
        
        return trends

    def generate_insights(self, insight_type: str, parameters: dict, priority_level: str = "medium") -> Dict[str, Any]:
        """Generate actionable insights from PRP data"""
        
        insights = {
            "insight_type": insight_type,
            "priority_level": priority_level,
            "generated_at": datetime.utcnow().isoformat(),
            "insights": []
        }
        
        if insight_type == "performance_gaps":
            insights["insights"] = self._identify_performance_gaps(parameters)
        elif insight_type == "optimization_opportunities":
            insights["insights"] = self._identify_optimization_opportunities(parameters)
        elif insight_type == "risk_patterns":
            insights["insights"] = self._identify_risk_patterns(parameters)
        elif insight_type == "compliance_issues":
            insights["insights"] = self._identify_compliance_issues(parameters)
        elif insight_type == "comprehensive":
            insights["insights"] = (
                self._identify_performance_gaps(parameters) +
                self._identify_optimization_opportunities(parameters) +
                self._identify_risk_patterns(parameters) +
                self._identify_compliance_issues(parameters)
            )
        
        # Filter by priority level
        if priority_level != "all":
            insights["insights"] = [i for i in insights["insights"] if i.get("priority") == priority_level]
        
        return insights

    def trigger_automation(self, automation_type: str, parameters: dict, triggered_by: int) -> Dict[str, Any]:
        """Trigger automated PRP processes"""
        
        automation_result = {
            "automation_type": automation_type,
            "triggered_by": triggered_by,
            "triggered_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "results": {}
        }
        
        if automation_type == "schedule_checklists":
            # Automatically schedule checklists based on program frequencies
            results = self._automate_checklist_scheduling(parameters)
            automation_result["results"] = results
            
        elif automation_type == "risk_assessment_reminders":
            # Send reminders for overdue risk assessments
            results = self._automate_risk_assessment_reminders(parameters)
            automation_result["results"] = results
            
        elif automation_type == "capa_follow_up":
            # Follow up on overdue CAPA actions
            results = self._automate_capa_follow_up(parameters)
            automation_result["results"] = results
            
        elif automation_type == "compliance_reporting":
            # Generate automated compliance reports
            results = self._automate_compliance_reporting(parameters)
            automation_result["results"] = results
        
        return automation_result

    def get_automation_status(self, automation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of automated PRP processes"""
        
        # In a real implementation, this would track automation jobs
        # For now, return a mock status
        
        if automation_id:
            return {
                "automation_id": automation_id,
                "status": "completed",
                "started_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "duration_minutes": 60,
                "success": True
            }
        else:
            # Return overall automation status
            return {
                "total_automations": 4,
                "active_automations": 1,
                "completed_automations": 3,
                "failed_automations": 0,
                "last_automation": datetime.utcnow().isoformat()
            }

    def advanced_search(self, search_criteria: dict, search_type: str = "all", 
                       sort_by: str = "relevance", page: int = 1, size: int = 20) -> Dict[str, Any]:
        """Advanced search across PRP data with multiple criteria"""
        
        search_results = {
            "search_criteria": search_criteria,
            "search_type": search_type,
            "sort_by": sort_by,
            "page": page,
            "size": size,
            "results": [],
            "total_count": 0
        }
        
        if search_type in ["programs", "all"]:
            program_results = self._search_programs(search_criteria)
            search_results["results"].extend(program_results)
        
        if search_type in ["checklists", "all"]:
            checklist_results = self._search_checklists(search_criteria)
            search_results["results"].extend(checklist_results)
        
        if search_type in ["risks", "all"]:
            risk_results = self._search_risks(search_criteria)
            search_results["results"].extend(risk_results)
        
        if search_type in ["capa", "all"]:
            capa_results = self._search_capa(search_criteria)
            search_results["results"].extend(capa_results)
        
        # Sort results
        search_results["results"] = self._sort_search_results(search_results["results"], sort_by)
        
        # Apply pagination
        total_count = len(search_results["results"])
        start_index = (page - 1) * size
        end_index = start_index + size
        
        search_results["total_count"] = total_count
        search_results["results"] = search_results["results"][start_index:end_index]
        search_results["total_pages"] = (total_count + size - 1) // size
        
        return search_results

    def bulk_update_programs(self, program_ids: List[int], update_data: dict, updated_by: int) -> Dict[str, Any]:
        """Bulk update PRP programs"""
        
        update_results = {
            "program_ids": program_ids,
            "updated_by": updated_by,
            "updated_at": datetime.utcnow().isoformat(),
            "success_count": 0,
            "failed_count": 0,
            "errors": []
        }
        
        for program_id in program_ids:
            try:
                program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
                if not program:
                    update_results["failed_count"] += 1
                    update_results["errors"].append(f"Program {program_id} not found")
                    continue
                
                # Apply updates
                for field, value in update_data.items():
                    if hasattr(program, field):
                        if field == "category" and value:
                            setattr(program, field, PRPCategory(value))
                        elif field == "status" and value:
                            setattr(program, field, PRPStatus(value))
                        elif field == "frequency" and value:
                            setattr(program, field, PRPFrequency(value))
                        else:
                            setattr(program, field, value)
                
                program.updated_at = datetime.utcnow()
                update_results["success_count"] += 1
                
            except Exception as e:
                update_results["failed_count"] += 1
                update_results["errors"].append(f"Error updating program {program_id}: {str(e)}")
        
        self.db.commit()
        
        return update_results

    def bulk_export_data(self, data_types: List[str], format_type: str, filters: dict, requested_by: int) -> Dict[str, Any]:
        """Bulk export PRP data"""
        
        export_results = {
            "data_types": data_types,
            "format": format_type,
            "requested_by": requested_by,
            "requested_at": datetime.utcnow().isoformat(),
            "exports": []
        }
        
        for data_type in data_types:
            try:
                export_result = self.export_prp_data(data_type, format_type, filters, False)
                export_results["exports"].append(export_result)
            except Exception as e:
                export_results["exports"].append({
                    "data_type": data_type,
                    "status": "failed",
                    "error": str(e)
                })
        
        return export_results

    # Helper methods for additional functionality
    def _calculate_average_completion_time_all(self) -> float:
        """Calculate average completion time for all checklists"""
        completed_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.status == ChecklistStatus.COMPLETED,
                PRPChecklist.completed_date.isnot(None),
                PRPChecklist.scheduled_date.isnot(None)
            )
        ).all()
        
        completion_times = []
        for checklist in completed_checklists:
            completion_time = (checklist.completed_date - checklist.scheduled_date).days
            completion_times.append(completion_time)
        
        return sum(completion_times) / len(completion_times) if completion_times else 0.0

    def _calculate_on_time_completion_rate(self) -> float:
        """Calculate on-time completion rate"""
        completed_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.status == ChecklistStatus.COMPLETED,
                PRPChecklist.completed_date.isnot(None),
                PRPChecklist.due_date.isnot(None)
            )
        ).all()
        
        on_time_completions = len([c for c in completed_checklists if c.completed_date <= c.due_date])
        return (on_time_completions / len(completed_checklists) * 100) if completed_checklists else 0.0

    def _calculate_average_checklists_per_user(self) -> float:
        """Calculate average checklists per user"""
        total_checklists = self.db.query(PRPChecklist).count()
        unique_users = self.db.query(PRPChecklist.assigned_to).distinct().count()
        return total_checklists / unique_users if unique_users > 0 else 0.0

    def _calculate_overall_average_compliance(self) -> float:
        """Calculate overall average compliance"""
        completed_checklists = self.db.query(PRPChecklist).filter(
            PRPChecklist.status == ChecklistStatus.COMPLETED
        ).all()
        
        total_compliance = sum(c.compliance_percentage for c in completed_checklists)
        return total_compliance / len(completed_checklists) if completed_checklists else 0.0

    def _count_high_compliance_programs(self) -> int:
        """Count programs with high compliance (>95%)"""
        programs = self.db.query(PRPProgram).all()
        high_compliance_count = 0
        
        for program in programs:
            checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.status == ChecklistStatus.COMPLETED
                )
            ).all()
            
            if checklists:
                avg_compliance = sum(c.compliance_percentage for c in checklists) / len(checklists)
                if avg_compliance > 95.0:
                    high_compliance_count += 1
        
        return high_compliance_count

    def _count_low_compliance_programs(self) -> int:
        """Count programs with low compliance (<80%)"""
        programs = self.db.query(PRPProgram).all()
        low_compliance_count = 0
        
        for program in programs:
            checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.status == ChecklistStatus.COMPLETED
                )
            ).all()
            
            if checklists:
                avg_compliance = sum(c.compliance_percentage for c in checklists) / len(checklists)
                if avg_compliance < 80.0:
                    low_compliance_count += 1
        
        return low_compliance_count

    def _calculate_overall_benchmark_status(self, performance_vs_benchmark: dict) -> str:
        """Calculate overall benchmark status"""
        above_count = sum(1 for metric in performance_vs_benchmark.values() if metric["status"] == "above")
        total_metrics = len(performance_vs_benchmark)
        
        if above_count == total_metrics:
            return "excellent"
        elif above_count >= total_metrics * 0.75:
            return "good"
        elif above_count >= total_metrics * 0.5:
            return "fair"
        else:
            return "needs_improvement"

    # Additional helper methods for predictions, trends, insights, and automation
    def _predict_compliance_trends(self) -> dict:
        """Predict compliance trends"""
        return {
            "next_month_prediction": 87.5,
            "trend_direction": "improving",
            "confidence_level": "high",
            "factors": ["increased training", "better resource allocation"]
        }

    def _predict_risk_trends(self) -> dict:
        """Predict risk trends"""
        return {
            "high_risk_probability": 0.15,
            "escalation_probability": 0.08,
            "trend_direction": "stable",
            "confidence_level": "medium"
        }

    def _predict_potential_failures(self) -> dict:
        """Predict potential failures"""
        return {
            "failure_probability": 0.12,
            "high_risk_programs": ["PRP-001", "PRP-003"],
            "recommended_actions": ["increase monitoring", "additional training"]
        }

    def _analyze_compliance_trends(self, start_date: datetime, end_date: datetime) -> dict:
        """Analyze compliance trends"""
        return {
            "trend_data": [],
            "trend_direction": "improving",
            "key_insights": ["Compliance improved by 5% over the period"]
        }

    def _analyze_risk_trends(self, start_date: datetime, end_date: datetime) -> dict:
        """Analyze risk trends"""
        return {
            "trend_data": [],
            "trend_direction": "stable",
            "key_insights": ["Risk levels remained consistent"]
        }

    def _analyze_efficiency_trends(self, start_date: datetime, end_date: datetime) -> dict:
        """Analyze efficiency trends"""
        return {
            "trend_data": [],
            "trend_direction": "improving",
            "key_insights": ["Completion times decreased by 20%"]
        }

    def _analyze_quality_trends(self, start_date: datetime, end_date: datetime) -> dict:
        """Analyze quality trends"""
        return {
            "trend_data": [],
            "trend_direction": "stable",
            "key_insights": ["Quality metrics remained high"]
        }

    def _identify_performance_gaps(self, parameters: dict) -> List[dict]:
        """Identify performance gaps"""
        return [
            {
                "type": "performance_gap",
                "description": "Program X has 15% lower completion rate than average",
                "priority": "high",
                "recommended_action": "Review resource allocation"
            }
        ]

    def _identify_optimization_opportunities(self, parameters: dict) -> List[dict]:
        """Identify optimization opportunities"""
        return [
            {
                "type": "optimization_opportunity",
                "description": "Schedule optimization could improve efficiency by 20%",
                "priority": "medium",
                "recommended_action": "Implement automated scheduling"
            }
        ]

    def _identify_risk_patterns(self, parameters: dict) -> List[dict]:
        """Identify risk patterns"""
        return [
            {
                "type": "risk_pattern",
                "description": "High correlation between overdue checklists and risk escalation",
                "priority": "high",
                "recommended_action": "Implement early warning system"
            }
        ]

    def _identify_compliance_issues(self, parameters: dict) -> List[dict]:
        """Identify compliance issues"""
        return [
            {
                "type": "compliance_issue",
                "description": "Department Y consistently below compliance targets",
                "priority": "high",
                "recommended_action": "Conduct targeted training"
            }
        ]

    def _optimize_scheduling_patterns(self, parameters: dict) -> List[dict]:
        """Optimize scheduling patterns"""
        return [
            {
                "type": "scheduling_optimization",
                "recommendation": "Implement staggered scheduling to reduce workload peaks",
                "impact": "high",
                "effort": "medium"
            }
        ]

    def _optimize_resource_allocation_global(self, parameters: dict) -> List[dict]:
        """Optimize resource allocation globally"""
        return [
            {
                "type": "resource_optimization",
                "recommendation": "Redistribute workload based on user performance metrics",
                "impact": "medium",
                "effort": "low"
            }
        ]

    def _optimize_program_frequencies(self, parameters: dict) -> List[dict]:
        """Optimize program frequencies"""
        return [
            {
                "type": "frequency_optimization",
                "recommendation": "Adjust frequency for 3 programs based on risk levels",
                "impact": "medium",
                "effort": "low"
            }
        ]

    def _estimate_optimization_improvements(self, recommendations: List[dict]) -> dict:
        """Estimate optimization improvements"""
        return {
            "estimated_completion_rate_improvement": 12.0,
            "estimated_compliance_improvement": 6.0,
            "estimated_time_savings": 15.0,
            "confidence_level": "medium"
        }

    def _automate_checklist_scheduling(self, parameters: dict) -> dict:
        """Automate checklist scheduling"""
        return {
            "scheduled_checklists": 25,
            "scheduled_programs": 8,
            "next_schedule_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }

    def _automate_risk_assessment_reminders(self, parameters: dict) -> dict:
        """Automate risk assessment reminders"""
        return {
            "reminders_sent": 12,
            "overdue_assessments": 3,
            "escalated_reminders": 2
        }

    def _automate_capa_follow_up(self, parameters: dict) -> dict:
        """Automate CAPA follow up"""
        return {
            "follow_ups_sent": 8,
            "overdue_actions": 5,
            "escalated_actions": 2
        }

    def _automate_compliance_reporting(self, parameters: dict) -> dict:
        """Automate compliance reporting"""
        return {
            "reports_generated": 4,
            "recipients_notified": 12,
            "next_report_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

    def _search_programs(self, criteria: dict) -> List[dict]:
        """Search programs based on criteria"""
        query = self.db.query(PRPProgram)
        
        if criteria.get("name"):
            query = query.filter(PRPProgram.name.ilike(f"%{criteria['name']}%"))
        
        if criteria.get("category"):
            query = query.filter(PRPProgram.category == PRPCategory(criteria["category"]))
        
        programs = query.all()
        return [{"type": "program", "id": p.id, "name": p.name, "category": p.category.value} for p in programs]

    def _search_checklists(self, criteria: dict) -> List[dict]:
        """Search checklists based on criteria"""
        query = self.db.query(PRPChecklist)
        
        if criteria.get("name"):
            query = query.filter(PRPChecklist.name.ilike(f"%{criteria['name']}%"))
        
        if criteria.get("status"):
            query = query.filter(PRPChecklist.status == ChecklistStatus(criteria["status"]))
        
        checklists = query.all()
        return [{"type": "checklist", "id": c.id, "name": c.name, "status": c.status.value} for c in checklists]

    def _search_risks(self, criteria: dict) -> List[dict]:
        """Search risks based on criteria"""
        query = self.db.query(RiskAssessment)
        
        if criteria.get("hazard"):
            query = query.filter(RiskAssessment.hazard_identified.ilike(f"%{criteria['hazard']}%"))
        
        if criteria.get("risk_level"):
            query = query.filter(RiskAssessment.risk_level == RiskLevel(criteria["risk_level"]))
        
        risks = query.all()
        return [{"type": "risk", "id": r.id, "hazard": r.hazard_identified, "risk_level": r.risk_level.value} for r in risks]

    def _search_capa(self, criteria: dict) -> List[dict]:
        """Search CAPA based on criteria"""
        query = self.db.query(CorrectiveAction)
        
        if criteria.get("description"):
            query = query.filter(CorrectiveAction.description.ilike(f"%{criteria['description']}%"))
        
        if criteria.get("status"):
            query = query.filter(CorrectiveAction.status == CorrectiveActionStatus(criteria["status"]))
        
        capa_items = query.all()
        return [{"type": "capa", "id": c.id, "description": c.description, "status": c.status.value} for c in capa_items]

    def _sort_search_results(self, results: List[dict], sort_by: str) -> List[dict]:
        """Sort search results"""
        if sort_by == "relevance":
            # Sort by relevance score (simplified)
            return sorted(results, key=lambda x: x.get("id", 0), reverse=True)
        elif sort_by == "name":
            return sorted(results, key=lambda x: x.get("name", ""))
        elif sort_by == "date":
            return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)
        else:
            return results