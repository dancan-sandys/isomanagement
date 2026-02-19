from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from datetime import datetime, timedelta
import json

from app.models.haccp import Hazard, CCP, Product, ProcessFlow
from app.models.prp import PRPProgram
from app.models.risk import RiskRegisterItem, RiskItemType, RiskCategory, RiskStatus
from app.models.haccp_risk import (
    HACCPRiskAssessment, HACCPRiskIntegration, HACCPRiskMonitoring, HACCPRiskReview,
    HACCPRiskAssessmentType, HACCPRiskReviewStatus, HACCPRiskReviewType,
    HACCPRiskMonitoringType, HACCPRiskMonitoringResult, HACCPRiskIntegrationType,
    HACCPElementType, HACCPRiskReviewOutcome
)
from app.services.risk_management_service import RiskManagementService


class HACCPRiskService:
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = RiskManagementService(db)

    # ============================================================================
    # HACCP RISK ASSESSMENT METHODS
    # ============================================================================

    def assess_hazard_risk(self, hazard_id: int, assessment_data: Dict) -> HACCPRiskAssessment:
        """Perform comprehensive risk assessment for a HACCP hazard"""
        hazard = self.db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise ValueError("Hazard not found")

        # Calculate initial risk score based on HACCP methodology
        initial_risk_score = self._calculate_hazard_risk_score(hazard, assessment_data)
        initial_risk_level = self._determine_hazard_risk_level(initial_risk_score)

        # Create risk assessment record
        assessment = HACCPRiskAssessment(
            hazard_id=hazard_id,
            assessment_type=HACCPRiskAssessmentType.HAZARD,
            assessment_method=assessment_data.get("assessment_method", "HACCP Risk Assessment"),
            assessment_date=datetime.utcnow(),
            assessor_id=assessment_data.get("assessor_id"),
            initial_risk_score=initial_risk_score,
            initial_risk_level=initial_risk_level,
            control_effectiveness=assessment_data.get("control_effectiveness"),
            control_measures=assessment_data.get("control_measures"),
            control_verification=assessment_data.get("control_verification"),
            control_monitoring=assessment_data.get("control_monitoring"),
            treatment_plan=assessment_data.get("treatment_plan"),
            monitoring_frequency=assessment_data.get("monitoring_frequency", "monthly"),
            review_frequency=assessment_data.get("review_frequency", "quarterly")
        )

        # Calculate residual risk
        if assessment.control_effectiveness:
            residual_score = self._calculate_residual_risk_score(initial_risk_score, assessment.control_effectiveness)
            assessment.residual_risk_score = residual_score
            assessment.residual_risk_level = self._determine_hazard_risk_level(residual_score)
            assessment.risk_acceptable = residual_score <= 15  # Threshold for acceptability

        # Set next monitoring and review dates
        assessment.next_monitoring_date = self._calculate_next_date(assessment.monitoring_frequency)
        assessment.next_review_date = self._calculate_next_date(assessment.review_frequency)

        # Update hazard with risk information
        hazard.risk_assessment_method = assessment.assessment_method
        hazard.risk_assessment_date = assessment.assessment_date
        hazard.risk_assessor_id = assessment.assessor_id
        hazard.risk_treatment_plan = assessment.treatment_plan
        hazard.risk_monitoring_frequency = assessment.monitoring_frequency
        hazard.risk_review_frequency = assessment.review_frequency
        hazard.risk_control_effectiveness = assessment.control_effectiveness
        hazard.risk_residual_score = assessment.residual_risk_score
        hazard.risk_residual_level = assessment.residual_risk_level
        hazard.risk_acceptable = assessment.risk_acceptable
        hazard.risk_justification = assessment_data.get("risk_justification")

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def assess_ccp_risk(self, ccp_id: int, assessment_data: Dict) -> HACCPRiskAssessment:
        """Perform comprehensive risk assessment for a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")

        # Calculate initial risk score based on CCP methodology
        initial_risk_score = self._calculate_ccp_risk_score(ccp, assessment_data)
        initial_risk_level = self._determine_ccp_risk_level(initial_risk_score)

        # Create risk assessment record
        assessment = HACCPRiskAssessment(
            ccp_id=ccp_id,
            assessment_type=HACCPRiskAssessmentType.CCP,
            assessment_method=assessment_data.get("assessment_method", "CCP Risk Assessment"),
            assessment_date=datetime.utcnow(),
            assessor_id=assessment_data.get("assessor_id"),
            initial_risk_score=initial_risk_score,
            initial_risk_level=initial_risk_level,
            control_effectiveness=assessment_data.get("control_effectiveness"),
            control_measures=assessment_data.get("control_measures"),
            control_verification=assessment_data.get("control_verification"),
            control_monitoring=assessment_data.get("control_monitoring"),
            treatment_plan=assessment_data.get("treatment_plan"),
            monitoring_frequency=assessment_data.get("monitoring_frequency", "daily"),
            review_frequency=assessment_data.get("review_frequency", "monthly")
        )

        # Calculate residual risk
        if assessment.control_effectiveness:
            residual_score = self._calculate_residual_risk_score(initial_risk_score, assessment.control_effectiveness)
            assessment.residual_risk_score = residual_score
            assessment.residual_risk_level = self._determine_ccp_risk_level(residual_score)
            assessment.risk_acceptable = residual_score <= 10  # Stricter threshold for CCPs

        # Set next monitoring and review dates
        assessment.next_monitoring_date = self._calculate_next_date(assessment.monitoring_frequency)
        assessment.next_review_date = self._calculate_next_date(assessment.review_frequency)

        # Update CCP with risk information
        ccp.risk_assessment_method = assessment.assessment_method
        ccp.risk_assessment_date = assessment.assessment_date
        ccp.risk_assessor_id = assessment.assessor_id
        ccp.risk_treatment_plan = assessment.treatment_plan
        ccp.risk_monitoring_frequency = assessment.monitoring_frequency
        ccp.risk_review_frequency = assessment.review_frequency
        ccp.risk_control_effectiveness = assessment.control_effectiveness
        ccp.risk_residual_score = assessment.residual_risk_score
        ccp.risk_residual_level = assessment.residual_risk_level

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def assess_prp_risk(self, prp_program_id: int, assessment_data: Dict) -> HACCPRiskAssessment:
        """Perform comprehensive risk assessment for a PRP program"""
        prp_program = self.db.query(PRPProgram).filter(PRPProgram.id == prp_program_id).first()
        if not prp_program:
            raise ValueError("PRP Program not found")

        # Calculate initial risk score based on PRP methodology
        initial_risk_score = self._calculate_prp_risk_score(prp_program, assessment_data)
        initial_risk_level = self._determine_prp_risk_level(initial_risk_score)

        # Create risk assessment record
        assessment = HACCPRiskAssessment(
            prp_program_id=prp_program_id,
            assessment_type=HACCPRiskAssessmentType.PRP,
            assessment_method=assessment_data.get("assessment_method", "PRP Risk Assessment"),
            assessment_date=datetime.utcnow(),
            assessor_id=assessment_data.get("assessor_id"),
            initial_risk_score=initial_risk_score,
            initial_risk_level=initial_risk_level,
            control_effectiveness=assessment_data.get("control_effectiveness"),
            control_measures=assessment_data.get("control_measures"),
            control_verification=assessment_data.get("control_verification"),
            control_monitoring=assessment_data.get("control_monitoring"),
            treatment_plan=assessment_data.get("treatment_plan"),
            monitoring_frequency=assessment_data.get("monitoring_frequency", "weekly"),
            review_frequency=assessment_data.get("review_frequency", "monthly")
        )

        # Calculate residual risk
        if assessment.control_effectiveness:
            residual_score = self._calculate_residual_risk_score(initial_risk_score, assessment.control_effectiveness)
            assessment.residual_risk_score = residual_score
            assessment.residual_risk_level = self._determine_prp_risk_level(residual_score)
            assessment.risk_acceptable = residual_score <= 20  # Threshold for PRPs

        # Set next monitoring and review dates
        assessment.next_monitoring_date = self._calculate_next_date(assessment.monitoring_frequency)
        assessment.next_review_date = self._calculate_next_date(assessment.review_frequency)

        # Update PRP program with risk information
        prp_program.risk_assessment_date = assessment.assessment_date
        prp_program.risk_assessment_frequency = assessment.monitoring_frequency
        prp_program.risk_monitoring_plan = assessment.control_monitoring
        prp_program.risk_review_plan = assessment_data.get("review_plan")
        prp_program.risk_improvement_plan = assessment_data.get("improvement_plan")
        prp_program.risk_control_effectiveness = assessment.control_effectiveness
        prp_program.risk_residual_score = assessment.residual_risk_score
        prp_program.risk_residual_level = assessment.residual_risk_level

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def _calculate_hazard_risk_score(self, hazard: Hazard, assessment_data: Dict) -> int:
        """Calculate risk score for a hazard based on HACCP methodology"""
        # Base score from existing hazard assessment
        base_score = hazard.risk_score or 0
        
        # Additional factors
        severity_multiplier = assessment_data.get("severity_multiplier", 1.0)
        likelihood_multiplier = assessment_data.get("likelihood_multiplier", 1.0)
        detectability_multiplier = assessment_data.get("detectability_multiplier", 1.0)
        
        # Calculate enhanced score
        enhanced_score = int(base_score * severity_multiplier * likelihood_multiplier * detectability_multiplier)
        return min(enhanced_score, 100)  # Cap at 100

    def _calculate_ccp_risk_score(self, ccp: CCP, assessment_data: Dict) -> int:
        """Calculate risk score for a CCP based on critical control methodology"""
        # Base score from critical limits and monitoring
        base_score = 50  # Default high risk for CCPs
        
        # Adjust based on monitoring effectiveness
        monitoring_effectiveness = assessment_data.get("monitoring_effectiveness", 3)  # 1-5 scale
        base_score = base_score * (6 - monitoring_effectiveness) / 5
        
        # Additional factors
        critical_limit_complexity = assessment_data.get("critical_limit_complexity", 3)  # 1-5 scale
        verification_frequency = assessment_data.get("verification_frequency", "monthly")
        
        # Adjust for complexity and verification
        complexity_factor = critical_limit_complexity / 5
        verification_factor = self._get_verification_factor(verification_frequency)
        
        final_score = int(base_score * complexity_factor * verification_factor)
        return min(final_score, 100)

    def _calculate_prp_risk_score(self, prp_program: PRPProgram, assessment_data: Dict) -> int:
        """Calculate risk score for a PRP program"""
        # Base score from PRP category and frequency
        base_score = 30  # Default moderate risk for PRPs
        
        # Adjust based on frequency
        frequency = prp_program.frequency
        if frequency == "daily":
            base_score = 40
        elif frequency == "weekly":
            base_score = 30
        elif frequency == "monthly":
            base_score = 20
        elif frequency == "quarterly":
            base_score = 15
        
        # Additional factors
        compliance_history = assessment_data.get("compliance_history", 3)  # 1-5 scale
        training_adequacy = assessment_data.get("training_adequacy", 3)  # 1-5 scale
        
        # Adjust for compliance and training
        compliance_factor = (6 - compliance_history) / 5
        training_factor = (6 - training_adequacy) / 5
        
        final_score = int(base_score * compliance_factor * training_factor)
        return min(final_score, 100)

    def _calculate_residual_risk_score(self, initial_score: int, control_effectiveness: int) -> int:
        """Calculate residual risk score after control measures"""
        # Control effectiveness is 1-5 scale, where 5 is most effective
        effectiveness_factor = (6 - control_effectiveness) / 5
        residual_score = int(initial_score * effectiveness_factor)
        return max(residual_score, 1)  # Minimum score of 1

    def _determine_hazard_risk_level(self, score: int) -> str:
        """Determine risk level for hazards"""
        if score <= 15:
            return "LOW"
        elif score <= 30:
            return "MEDIUM"
        elif score <= 60:
            return "HIGH"
        else:
            return "CRITICAL"

    def _determine_ccp_risk_level(self, score: int) -> str:
        """Determine risk level for CCPs (stricter thresholds)"""
        if score <= 10:
            return "LOW"
        elif score <= 25:
            return "MEDIUM"
        elif score <= 50:
            return "HIGH"
        else:
            return "CRITICAL"

    def _determine_prp_risk_level(self, score: int) -> str:
        """Determine risk level for PRPs"""
        if score <= 20:
            return "LOW"
        elif score <= 40:
            return "MEDIUM"
        elif score <= 70:
            return "HIGH"
        else:
            return "CRITICAL"

    def _get_verification_factor(self, frequency: str) -> float:
        """Get verification frequency factor"""
        factors = {
            "daily": 1.0,
            "weekly": 1.2,
            "monthly": 1.5,
            "quarterly": 2.0,
            "annually": 3.0
        }
        return factors.get(frequency, 1.5)

    def _calculate_next_date(self, frequency: str) -> datetime:
        """Calculate next date based on frequency"""
        now = datetime.utcnow()
        if frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        elif frequency == "monthly":
            return now + timedelta(days=30)
        elif frequency == "quarterly":
            return now + timedelta(days=90)
        elif frequency == "annually":
            return now + timedelta(days=365)
        else:
            return now + timedelta(days=30)  # Default to monthly

    # ============================================================================
    # HACCP RISK INTEGRATION METHODS
    # ============================================================================

    def integrate_hazard_with_risk_register(self, hazard_id: int, risk_register_item_id: int, integration_data: Dict) -> HACCPRiskIntegration:
        """Integrate a hazard with the risk register"""
        integration = HACCPRiskIntegration(
            risk_register_item_id=risk_register_item_id,
            haccp_element_type=HACCPElementType.HAZARD,
            haccp_element_id=hazard_id,
            integration_type=integration_data.get("integration_type", HACCPRiskIntegrationType.DIRECT),
            integration_strength=integration_data.get("integration_strength", 5),
            impact_description=integration_data.get("impact_description"),
            food_safety_impact=integration_data.get("food_safety_impact"),
            compliance_impact=integration_data.get("compliance_impact"),
            operational_impact=integration_data.get("operational_impact"),
            integrated_by=integration_data.get("integrated_by"),
            review_frequency=integration_data.get("review_frequency", "monthly")
        )

        # Update hazard with risk register link
        hazard = self.db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if hazard:
            hazard.risk_register_item_id = risk_register_item_id

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        return integration

    def integrate_ccp_with_risk_register(self, ccp_id: int, risk_register_item_id: int, integration_data: Dict) -> HACCPRiskIntegration:
        """Integrate a CCP with the risk register"""
        integration = HACCPRiskIntegration(
            risk_register_item_id=risk_register_item_id,
            haccp_element_type=HACCPElementType.CCP,
            haccp_element_id=ccp_id,
            integration_type=integration_data.get("integration_type", HACCPRiskIntegrationType.DIRECT),
            integration_strength=integration_data.get("integration_strength", 5),
            impact_description=integration_data.get("impact_description"),
            food_safety_impact=integration_data.get("food_safety_impact"),
            compliance_impact=integration_data.get("compliance_impact"),
            operational_impact=integration_data.get("operational_impact"),
            integrated_by=integration_data.get("integrated_by"),
            review_frequency=integration_data.get("review_frequency", "weekly")
        )

        # Update CCP with risk register link
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if ccp:
            ccp.risk_register_item_id = risk_register_item_id

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        return integration

    def integrate_prp_with_risk_register(self, prp_program_id: int, risk_register_item_id: int, integration_data: Dict) -> HACCPRiskIntegration:
        """Integrate a PRP program with the risk register"""
        integration = HACCPRiskIntegration(
            risk_register_item_id=risk_register_item_id,
            haccp_element_type=HACCPElementType.PRP,
            haccp_element_id=prp_program_id,
            integration_type=integration_data.get("integration_type", HACCPRiskIntegrationType.INDIRECT),
            integration_strength=integration_data.get("integration_strength", 3),
            impact_description=integration_data.get("impact_description"),
            food_safety_impact=integration_data.get("food_safety_impact"),
            compliance_impact=integration_data.get("compliance_impact"),
            operational_impact=integration_data.get("operational_impact"),
            integrated_by=integration_data.get("integrated_by"),
            review_frequency=integration_data.get("review_frequency", "monthly")
        )

        # Update PRP program with risk register link
        prp_program = self.db.query(PRPProgram).filter(PRPProgram.id == prp_program_id).first()
        if prp_program:
            prp_program.risk_register_item_id = risk_register_item_id

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        return integration

    def get_haccp_integrations(self, risk_register_item_id: int) -> List[HACCPRiskIntegration]:
        """Get all HACCP integrations for a risk register item"""
        return self.db.query(HACCPRiskIntegration).filter(
            HACCPRiskIntegration.risk_register_item_id == risk_register_item_id
        ).all()

    def get_risk_integrations_by_element(self, element_type: str, element_id: int) -> List[HACCPRiskIntegration]:
        """Get risk integrations for a specific HACCP element"""
        return self.db.query(HACCPRiskIntegration).filter(
            HACCPRiskIntegration.haccp_element_type == element_type,
            HACCPRiskIntegration.haccp_element_id == element_id
        ).all()

    # ============================================================================
    # HACCP RISK MONITORING METHODS
    # ============================================================================

    def conduct_haccp_risk_monitoring(self, assessment_id: int, monitoring_data: Dict) -> HACCPRiskMonitoring:
        """Conduct monitoring for a HACCP risk assessment"""
        assessment = self.db.query(HACCPRiskAssessment).filter(HACCPRiskAssessment.id == assessment_id).first()
        if not assessment:
            raise ValueError("HACCP Risk Assessment not found")

        monitoring = HACCPRiskMonitoring(
            haccp_risk_assessment_id=assessment_id,
            monitoring_date=datetime.utcnow(),
            monitor_id=monitoring_data.get("monitor_id"),
            monitoring_type=monitoring_data.get("monitoring_type", HACCPRiskMonitoringType.ROUTINE),
            monitoring_method=monitoring_data.get("monitoring_method"),
            monitoring_result=monitoring_data.get("monitoring_result", HACCPRiskMonitoringResult.ACCEPTABLE),
            risk_score_observed=monitoring_data.get("risk_score_observed"),
            risk_level_observed=monitoring_data.get("risk_level_observed"),
            control_effectiveness_observed=monitoring_data.get("control_effectiveness_observed"),
            deviations_found=monitoring_data.get("deviations_found", False),
            deviation_description=monitoring_data.get("deviation_description"),
            corrective_actions_required=monitoring_data.get("corrective_actions_required", False),
            corrective_actions=monitoring_data.get("corrective_actions"),
            preventive_actions=monitoring_data.get("preventive_actions"),
            comments=monitoring_data.get("comments")
        )

        # Set next monitoring date
        monitoring.next_monitoring_date = self._calculate_next_date(assessment.monitoring_frequency)

        self.db.add(monitoring)
        self.db.commit()
        self.db.refresh(monitoring)

        return monitoring

    def get_haccp_risk_monitoring_history(self, assessment_id: int) -> List[HACCPRiskMonitoring]:
        """Get monitoring history for a HACCP risk assessment"""
        return self.db.query(HACCPRiskMonitoring).filter(
            HACCPRiskMonitoring.haccp_risk_assessment_id == assessment_id
        ).order_by(desc(HACCPRiskMonitoring.monitoring_date)).all()

    # ============================================================================
    # HACCP RISK REVIEW METHODS
    # ============================================================================

    def conduct_haccp_risk_review(self, assessment_id: int, review_data: Dict) -> HACCPRiskReview:
        """Conduct review for a HACCP risk assessment"""
        assessment = self.db.query(HACCPRiskAssessment).filter(HACCPRiskAssessment.id == assessment_id).first()
        if not assessment:
            raise ValueError("HACCP Risk Assessment not found")

        review = HACCPRiskReview(
            haccp_risk_assessment_id=assessment_id,
            review_date=datetime.utcnow(),
            reviewer_id=review_data.get("reviewer_id"),
            review_type=review_data.get("review_type", HACCPRiskReviewType.PERIODIC),
            review_status=review_data.get("review_status", HACCPRiskReviewStatus.PENDING),
            review_outcome=review_data.get("review_outcome"),
            risk_score_reviewed=review_data.get("risk_score_reviewed"),
            risk_level_reviewed=review_data.get("risk_level_reviewed"),
            control_effectiveness_reviewed=review_data.get("control_effectiveness_reviewed"),
            changes_identified=review_data.get("changes_identified", False),
            changes_description=review_data.get("changes_description"),
            actions_required=review_data.get("actions_required", False),
            actions_description=review_data.get("actions_description"),
            review_comments=review_data.get("review_comments")
        )

        # Set next review date
        review.next_review_date = self._calculate_next_date(assessment.review_frequency)

        # Update assessment review status
        assessment.review_status = review.review_status
        assessment.review_date = review.review_date
        assessment.reviewer_id = review.reviewer_id

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return review

    def get_haccp_risk_review_history(self, assessment_id: int) -> List[HACCPRiskReview]:
        """Get review history for a HACCP risk assessment"""
        return self.db.query(HACCPRiskReview).filter(
            HACCPRiskReview.haccp_risk_assessment_id == assessment_id
        ).order_by(desc(HACCPRiskReview.review_date)).all()

    # ============================================================================
    # HACCP RISK ANALYTICS METHODS
    # ============================================================================

    def get_haccp_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive HACCP risk summary"""
        total_hazards = self.db.query(Hazard).count()
        total_ccps = self.db.query(CCP).count()
        total_prps = self.db.query(PRPProgram).count()
        
        # Risk assessments by type
        hazard_assessments = self.db.query(HACCPRiskAssessment).filter(
            HACCPRiskAssessment.assessment_type == HACCPRiskAssessmentType.HAZARD
        ).count()
        
        ccp_assessments = self.db.query(HACCPRiskAssessment).filter(
            HACCPRiskAssessment.assessment_type == HACCPRiskAssessmentType.CCP
        ).count()
        
        prp_assessments = self.db.query(HACCPRiskAssessment).filter(
            HACCPRiskAssessment.assessment_type == HACCPRiskAssessmentType.PRP
        ).count()

        # High-risk items
        high_risk_hazards = self.db.query(Hazard).filter(
            Hazard.risk_residual_score >= 30
        ).count()
        
        high_risk_ccps = self.db.query(CCP).filter(
            CCP.risk_residual_score >= 25
        ).count()

        # Overdue reviews
        overdue_reviews = self.db.query(HACCPRiskAssessment).filter(
            HACCPRiskAssessment.next_review_date < datetime.utcnow()
        ).count()

        return {
            "total_hazards": total_hazards,
            "total_ccps": total_ccps,
            "total_prps": total_prps,
            "hazard_assessments": hazard_assessments,
            "ccp_assessments": ccp_assessments,
            "prp_assessments": prp_assessments,
            "high_risk_hazards": high_risk_hazards,
            "high_risk_ccps": high_risk_ccps,
            "overdue_reviews": overdue_reviews
        }

    def get_haccp_risk_distribution(self) -> Dict[str, Any]:
        """Get HACCP risk distribution by type and level"""
        # Hazard risk distribution
        hazard_risk_distribution = self.db.query(
            Hazard.risk_residual_level,
            func.count(Hazard.id)
        ).filter(Hazard.risk_residual_level.isnot(None)).group_by(Hazard.risk_residual_level).all()

        # CCP risk distribution
        ccp_risk_distribution = self.db.query(
            CCP.risk_residual_level,
            func.count(CCP.id)
        ).filter(CCP.risk_residual_level.isnot(None)).group_by(CCP.risk_residual_level).all()

        # PRP risk distribution
        prp_risk_distribution = self.db.query(
            PRPProgram.risk_residual_level,
            func.count(PRPProgram.id)
        ).filter(PRPProgram.risk_residual_level.isnot(None)).group_by(PRPProgram.risk_residual_level).all()

        return {
            "hazards": dict(hazard_risk_distribution),
            "ccps": dict(ccp_risk_distribution),
            "prps": dict(prp_risk_distribution)
        }

    def get_haccp_risk_alerts(self) -> List[Dict[str, Any]]:
        """Get HACCP risk alerts and notifications"""
        alerts = []
        
        # Overdue reviews
        overdue_assessments = self.db.query(HACCPRiskAssessment).filter(
            HACCPRiskAssessment.next_review_date < datetime.utcnow()
        ).limit(10).all()
        
        for assessment in overdue_assessments:
            alerts.append({
                "type": "overdue_review",
                "assessment_id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "message": f"Review overdue for {assessment.assessment_type} assessment"
            })

        # High-risk hazards
        high_risk_hazards = self.db.query(Hazard).filter(
            Hazard.risk_residual_score >= 30
        ).limit(10).all()
        
        for hazard in high_risk_hazards:
            alerts.append({
                "type": "high_risk_hazard",
                "hazard_id": hazard.id,
                "hazard_name": hazard.hazard_name,
                "message": f"High risk hazard: {hazard.hazard_name}"
            })

        # High-risk CCPs
        high_risk_ccps = self.db.query(CCP).filter(
            CCP.risk_residual_score >= 25
        ).limit(10).all()
        
        for ccp in high_risk_ccps:
            alerts.append({
                "type": "high_risk_ccp",
                "ccp_id": ccp.id,
                "ccp_name": ccp.ccp_name,
                "message": f"High risk CCP: {ccp.ccp_name}"
            })

        return alerts

    def get_haccp_risk_trends(self) -> Dict[str, Any]:
        """Get HACCP risk trends over time"""
        # Implementation for trend analysis
        return {
            "hazard_trends": "To be implemented",
            "ccp_trends": "To be implemented",
            "prp_trends": "To be implemented"
        }
