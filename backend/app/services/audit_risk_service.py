from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from datetime import datetime, timedelta
import json

from app.models.audit_mgmt import AuditProgram, Audit, AuditFinding, AuditType, AuditStatus, FindingSeverity, FindingStatus
from app.models.prp import PRPProgram
from app.models.risk import RiskRegisterItem, RiskItemType, RiskCategory, RiskStatus
from app.models.audit_risk import (
    AuditRiskAssessment, AuditRiskIntegration, AuditRiskMonitoring, AuditRiskReview,
    AuditRiskAssessmentType, AuditRiskReviewStatus, AuditRiskReviewType,
    AuditRiskMonitoringType, AuditRiskMonitoringResult, AuditRiskIntegrationType,
    AuditElementType, AuditRiskReviewOutcome, PRPAuditIntegration
)
from app.services.risk_management_service import RiskManagementService


class AuditRiskService:
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = RiskManagementService(db)

    def assess_audit_risk(self, audit_id: int, assessment_data: Dict) -> AuditRiskAssessment:
        """Perform comprehensive risk assessment for an audit"""
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise ValueError("Audit not found")

        # Calculate initial risk score based on audit methodology
        initial_risk_score = self._calculate_audit_risk_score(audit, assessment_data)
        initial_risk_level = self._determine_audit_risk_level(initial_risk_score)

        # Create risk assessment record
        assessment = AuditRiskAssessment(
            audit_id=audit_id,
            assessment_type=AuditRiskAssessmentType.AUDIT,
            assessment_method=assessment_data.get("assessment_method", "Audit Risk Assessment"),
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
            assessment.residual_risk_level = self._determine_audit_risk_level(residual_score)
            assessment.risk_acceptable = residual_score <= 25  # Threshold for audits

        # Set next monitoring and review dates
        assessment.next_monitoring_date = self._calculate_next_date(assessment.monitoring_frequency)
        assessment.next_review_date = self._calculate_next_date(assessment.review_frequency)

        # Update audit with risk information
        audit.risk_assessment_method = assessment.assessment_method
        audit.risk_assessment_date = assessment.assessment_date
        audit.risk_assessor_id = assessment.assessor_id
        audit.risk_treatment_plan = assessment.treatment_plan
        audit.risk_monitoring_frequency = assessment.monitoring_frequency
        audit.risk_review_frequency = assessment.review_frequency
        audit.risk_control_effectiveness = assessment.control_effectiveness
        audit.risk_residual_score = assessment.residual_risk_score
        audit.risk_residual_level = assessment.residual_risk_level

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def assess_audit_finding_risk(self, finding_id: int, assessment_data: Dict) -> AuditRiskAssessment:
        """Perform comprehensive risk assessment for an audit finding"""
        finding = self.db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
        if not finding:
            raise ValueError("Audit finding not found")

        # Calculate initial risk score based on finding methodology
        initial_risk_score = self._calculate_finding_risk_score(finding, assessment_data)
        initial_risk_level = self._determine_finding_risk_level(initial_risk_score)

        # Create risk assessment record
        assessment = AuditRiskAssessment(
            audit_finding_id=finding_id,
            assessment_type=AuditRiskAssessmentType.FINDING,
            assessment_method=assessment_data.get("assessment_method", "Audit Finding Risk Assessment"),
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
            assessment.residual_risk_level = self._determine_finding_risk_level(residual_score)
            assessment.risk_acceptable = residual_score <= 20  # Stricter threshold for findings

        # Set next monitoring and review dates
        assessment.next_monitoring_date = self._calculate_next_date(assessment.monitoring_frequency)
        assessment.next_review_date = self._calculate_next_date(assessment.review_frequency)

        # Update finding with risk information
        finding.risk_assessment_method = assessment.assessment_method
        finding.risk_assessment_date = assessment.assessment_date
        finding.risk_assessor_id = assessment.assessor_id
        finding.risk_treatment_plan = assessment.treatment_plan
        finding.risk_monitoring_frequency = assessment.monitoring_frequency
        finding.risk_review_frequency = assessment.review_frequency
        finding.risk_control_effectiveness = assessment.control_effectiveness
        finding.risk_residual_score = assessment.residual_risk_score
        finding.risk_residual_level = assessment.residual_risk_level
        finding.risk_acceptable = assessment.risk_acceptable
        finding.risk_justification = assessment_data.get("risk_justification")

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def _calculate_audit_risk_score(self, audit: Audit, assessment_data: Dict) -> int:
        """Calculate risk score for an audit based on audit methodology"""
        # Base score from audit type and status
        base_score = 30  # Default moderate risk for audits
        
        # Adjust based on audit type
        if audit.audit_type == AuditType.EXTERNAL:
            base_score = 50
        elif audit.audit_type == AuditType.SUPPLIER:
            base_score = 40
        elif audit.audit_type == AuditType.INTERNAL:
            base_score = 30
        
        # Adjust based on audit status
        if audit.status == AuditStatus.COMPLETED:
            base_score = base_score * 0.5
        elif audit.status == AuditStatus.IN_PROGRESS:
            base_score = base_score * 1.2
        elif audit.status == AuditStatus.PLANNED:
            base_score = base_score * 0.8
        
        # Additional factors
        scope_complexity = assessment_data.get("scope_complexity", 3)  # 1-5 scale
        compliance_requirements = assessment_data.get("compliance_requirements", 3)  # 1-5 scale
        
        # Adjust for complexity and compliance
        complexity_factor = scope_complexity / 5
        compliance_factor = compliance_requirements / 5
        
        final_score = int(base_score * complexity_factor * compliance_factor)
        return min(final_score, 100)

    def _calculate_finding_risk_score(self, finding: AuditFinding, assessment_data: Dict) -> int:
        """Calculate risk score for an audit finding"""
        # Base score from finding severity and status
        severity_scores = {
            FindingSeverity.MINOR: 20,
            FindingSeverity.MAJOR: 40,
            FindingSeverity.CRITICAL: 60
        }
        base_score = severity_scores.get(finding.severity, 30)
        
        # Adjust based on finding status
        if finding.status == FindingStatus.CLOSED:
            base_score = base_score * 0.3
        elif finding.status == FindingStatus.VERIFIED:
            base_score = base_score * 0.5
        elif finding.status == FindingStatus.IN_PROGRESS:
            base_score = base_score * 1.1
        elif finding.status == FindingStatus.OPEN:
            base_score = base_score * 1.3
        
        # Additional factors
        compliance_impact = assessment_data.get("compliance_impact", 3)  # 1-5 scale
        operational_impact = assessment_data.get("operational_impact", 3)  # 1-5 scale
        
        # Adjust for impact
        compliance_factor = compliance_impact / 5
        operational_factor = operational_impact / 5
        
        final_score = int(base_score * compliance_factor * operational_factor)
        return min(final_score, 100)

    def _calculate_residual_risk_score(self, initial_score: int, control_effectiveness: int) -> int:
        """Calculate residual risk score after control measures"""
        # Control effectiveness is 1-5 scale, where 5 is most effective
        effectiveness_factor = (6 - control_effectiveness) / 5
        residual_score = int(initial_score * effectiveness_factor)
        return max(residual_score, 1)  # Minimum score of 1

    def _determine_audit_risk_level(self, score: int) -> str:
        """Determine risk level for audits"""
        if score <= 25:
            return "LOW"
        elif score <= 50:
            return "MEDIUM"
        elif score <= 75:
            return "HIGH"
        else:
            return "CRITICAL"

    def _determine_finding_risk_level(self, score: int) -> str:
        """Determine risk level for audit findings (stricter thresholds)"""
        if score <= 20:
            return "LOW"
        elif score <= 40:
            return "MEDIUM"
        elif score <= 70:
            return "HIGH"
        else:
            return "CRITICAL"

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

    def integrate_audit_with_risk_register(self, audit_id: int, risk_register_item_id: int, integration_data: Dict) -> AuditRiskIntegration:
        """Integrate an audit with the risk register"""
        integration = AuditRiskIntegration(
            risk_register_item_id=risk_register_item_id,
            audit_element_type=AuditElementType.AUDIT,
            audit_element_id=audit_id,
            integration_type=integration_data.get("integration_type", AuditRiskIntegrationType.DIRECT),
            integration_strength=integration_data.get("integration_strength", 4),
            impact_description=integration_data.get("impact_description"),
            compliance_impact=integration_data.get("compliance_impact"),
            operational_impact=integration_data.get("operational_impact"),
            quality_impact=integration_data.get("quality_impact"),
            integrated_by=integration_data.get("integrated_by"),
            review_frequency=integration_data.get("review_frequency", "monthly")
        )

        # Update audit with risk register link
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if audit:
            audit.risk_register_item_id = risk_register_item_id

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        return integration

    def integrate_finding_with_risk_register(self, finding_id: int, risk_register_item_id: int, integration_data: Dict) -> AuditRiskIntegration:
        """Integrate an audit finding with the risk register"""
        integration = AuditRiskIntegration(
            risk_register_item_id=risk_register_item_id,
            audit_element_type=AuditElementType.FINDING,
            audit_element_id=finding_id,
            integration_type=integration_data.get("integration_type", AuditRiskIntegrationType.DIRECT),
            integration_strength=integration_data.get("integration_strength", 5),
            impact_description=integration_data.get("impact_description"),
            compliance_impact=integration_data.get("compliance_impact"),
            operational_impact=integration_data.get("operational_impact"),
            quality_impact=integration_data.get("quality_impact"),
            integrated_by=integration_data.get("integrated_by"),
            review_frequency=integration_data.get("review_frequency", "weekly")
        )

        # Update finding with risk register link
        finding = self.db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
        if finding:
            finding.risk_register_item_id = risk_register_item_id

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        return integration

    def integrate_prp_with_audit_finding(self, prp_program_id: int, audit_finding_id: int, integration_data: Dict) -> PRPAuditIntegration:
        """Integrate a PRP program with an audit finding"""
        integration = PRPAuditIntegration(
            prp_program_id=prp_program_id,
            audit_finding_id=audit_finding_id,
            integration_type=integration_data.get("integration_type", AuditRiskIntegrationType.DIRECT),
            integration_strength=integration_data.get("integration_strength", 4),
            impact_description=integration_data.get("impact_description"),
            prp_impact=integration_data.get("prp_impact"),
            audit_impact=integration_data.get("audit_impact"),
            compliance_impact=integration_data.get("compliance_impact"),
            integrated_by=integration_data.get("integrated_by"),
            review_frequency=integration_data.get("review_frequency", "monthly")
        )

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        return integration

    def get_audit_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive audit risk summary"""
        total_audits = self.db.query(Audit).count()
        total_findings = self.db.query(AuditFinding).count()
        total_programs = self.db.query(AuditProgram).count()
        
        # Risk assessments by type
        audit_assessments = self.db.query(AuditRiskAssessment).filter(
            AuditRiskAssessment.assessment_type == AuditRiskAssessmentType.AUDIT
        ).count()
        
        finding_assessments = self.db.query(AuditRiskAssessment).filter(
            AuditRiskAssessment.assessment_type == AuditRiskAssessmentType.FINDING
        ).count()

        # High-risk items
        high_risk_audits = self.db.query(Audit).filter(
            Audit.risk_residual_score >= 40
        ).count()
        
        high_risk_findings = self.db.query(AuditFinding).filter(
            AuditFinding.risk_residual_score >= 30
        ).count()

        # Overdue reviews
        overdue_reviews = self.db.query(AuditRiskAssessment).filter(
            AuditRiskAssessment.next_review_date < datetime.utcnow()
        ).count()

        return {
            "total_audits": total_audits,
            "total_findings": total_findings,
            "total_programs": total_programs,
            "audit_assessments": audit_assessments,
            "finding_assessments": finding_assessments,
            "high_risk_audits": high_risk_audits,
            "high_risk_findings": high_risk_findings,
            "overdue_reviews": overdue_reviews
        }

    def get_audit_risk_alerts(self) -> List[Dict[str, Any]]:
        """Get audit risk alerts and notifications"""
        alerts = []
        
        # Overdue reviews
        overdue_assessments = self.db.query(AuditRiskAssessment).filter(
            AuditRiskAssessment.next_review_date < datetime.utcnow()
        ).limit(10).all()
        
        for assessment in overdue_assessments:
            alerts.append({
                "type": "overdue_review",
                "assessment_id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "message": f"Review overdue for {assessment.assessment_type} assessment"
            })

        # High-risk audits
        high_risk_audits = self.db.query(Audit).filter(
            Audit.risk_residual_score >= 40
        ).limit(10).all()
        
        for audit in high_risk_audits:
            alerts.append({
                "type": "high_risk_audit",
                "audit_id": audit.id,
                "title": audit.title,
                "message": f"High risk audit: {audit.title}"
            })

        # High-risk findings
        high_risk_findings = self.db.query(AuditFinding).filter(
            AuditFinding.risk_residual_score >= 30
        ).limit(10).all()
        
        for finding in high_risk_findings:
            alerts.append({
                "type": "high_risk_finding",
                "finding_id": finding.id,
                "description": finding.description[:50] + "..." if len(finding.description) > 50 else finding.description,
                "message": f"High risk finding: {finding.description[:50]}..."
            })

        return alerts
