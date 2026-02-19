from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from datetime import datetime, timedelta
import json

from app.models.risk import (
    RiskRegisterItem, RiskAction, RiskManagementFramework, RiskContext,
    FSMSRiskIntegration, RiskCorrelation, RiskResourceAllocation,
    RiskCommunication, RiskKPI, RiskItemType, RiskCategory,
    RiskStatus, RiskSeverity, RiskLikelihood, RiskDetectability,
)
from app.schemas.risk import RiskFilter, RiskItemCreate, RiskItemUpdate


class RiskManagementService:
    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # RISK MANAGEMENT FRAMEWORK METHODS
    # ============================================================================

    def get_framework(self) -> Optional[RiskManagementFramework]:
        """Get the current risk management framework"""
        return self.db.query(RiskManagementFramework).first()

    def create_framework(self, framework_data: Dict) -> RiskManagementFramework:
        """Create or update the risk management framework"""
        existing = self.get_framework()
        if existing:
            # Update existing framework
            for key, value in framework_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new framework
            framework = RiskManagementFramework(**framework_data)
            self.db.add(framework)
            self.db.commit()
            self.db.refresh(framework)
            return framework

    def get_risk_appetite(self) -> Dict[str, Any]:
        """Get risk appetite and tolerance levels"""
        framework = self.get_framework()
        if not framework:
            return {}
        return {
            "risk_appetite_statement": framework.risk_appetite_statement,
            "risk_tolerance_levels": framework.risk_tolerance_levels,
            "risk_criteria": framework.risk_criteria
        }

    def get_risk_matrix(self) -> Dict[str, Any]:
        """Get risk assessment matrix configuration"""
        framework = self.get_framework()
        if not framework:
            return {}
        return {
            "risk_criteria": framework.risk_criteria,
            "risk_assessment_methodology": framework.risk_assessment_methodology,
            "risk_treatment_strategies": framework.risk_treatment_strategies
        }

    # ============================================================================
    # RISK CONTEXT METHODS
    # ============================================================================

    def get_risk_context(self) -> Optional[RiskContext]:
        """Get the current risk context"""
        return self.db.query(RiskContext).first()

    def create_risk_context(self, context_data: Dict) -> RiskContext:
        """Create or update the risk context"""
        existing = self.get_risk_context()
        if existing:
            # Update existing context
            for key, value in context_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new context
            context = RiskContext(**context_data)
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
            return context

    # ============================================================================
    # ENHANCED RISK ASSESSMENT METHODS
    # ============================================================================

    def assess_risk(self, risk_id: int, assessment_data: Dict) -> RiskRegisterItem:
        """Perform comprehensive risk assessment"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk item not found")

        # Update assessment fields
        risk.risk_assessment_method = assessment_data.get("assessment_method")
        risk.risk_assessment_date = datetime.utcnow()
        risk.risk_assessor_id = assessment_data.get("assessor_id")
        risk.risk_assessment_reviewed = False

        # Calculate enhanced risk score
        if risk.item_type == RiskItemType.RISK:
            risk_score = self._calculate_enhanced_risk_score(assessment_data)
            risk.risk_score = risk_score
            risk.residual_risk_score = assessment_data.get("residual_risk_score", risk_score)
            risk.residual_risk_level = self._determine_risk_level(risk.residual_risk_score)
            risk.residual_risk_acceptable = assessment_data.get("residual_risk_acceptable", False)
            risk.residual_risk_justification = assessment_data.get("residual_risk_justification")

        # Set monitoring and review schedule
        risk.monitoring_frequency = assessment_data.get("monitoring_frequency", "monthly")
        risk.review_frequency = assessment_data.get("review_frequency", "quarterly")
        risk.next_monitoring_date = self._calculate_next_date(risk.monitoring_frequency)
        risk.next_review_date = self._calculate_next_date(risk.review_frequency)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def _calculate_enhanced_risk_score(self, assessment_data: Dict) -> int:
        """Calculate enhanced risk score with additional factors"""
        # Base S × L × D calculation
        sev_map = {RiskSeverity.LOW: 1, RiskSeverity.MEDIUM: 2, RiskSeverity.HIGH: 3, RiskSeverity.CRITICAL: 4}
        lik_map = {RiskLikelihood.RARE: 1, RiskLikelihood.UNLIKELY: 2, RiskLikelihood.POSSIBLE: 3, RiskLikelihood.LIKELY: 4, RiskLikelihood.ALMOST_CERTAIN: 5}
        det_map = {RiskDetectability.EASILY_DETECTABLE: 1, RiskDetectability.MODERATELY_DETECTABLE: 2, RiskDetectability.DIFFICULT: 3, RiskDetectability.VERY_DIFFICULT: 4, RiskDetectability.ALMOST_UNDETECTABLE: 5}

        severity = assessment_data.get("severity", RiskSeverity.LOW)
        likelihood = assessment_data.get("likelihood", RiskLikelihood.UNLIKELY)
        detectability = assessment_data.get("detectability", RiskDetectability.MODERATELY_DETECTABLE)

        base_score = sev_map[severity] * lik_map[likelihood] * det_map[detectability]

        # Apply additional factors
        impact_multiplier = assessment_data.get("impact_multiplier", 1.0)
        complexity_factor = assessment_data.get("complexity_factor", 1.0)
        urgency_factor = assessment_data.get("urgency_factor", 1.0)

        enhanced_score = int(base_score * impact_multiplier * complexity_factor * urgency_factor)
        return min(enhanced_score, 100)  # Cap at 100

    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level based on score and tolerance levels"""
        framework = self.get_framework()
        if not framework:
            # Default risk levels
            if score <= 10:
                return "LOW"
            elif score <= 30:
                return "MEDIUM"
            elif score <= 60:
                return "HIGH"
            else:
                return "CRITICAL"

        tolerance_levels = framework.risk_tolerance_levels
        # Use framework-defined tolerance levels
        for level, threshold in tolerance_levels.items():
            if score <= threshold:
                return level.upper()
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

    # ============================================================================
    # RISK TREATMENT METHODS
    # ============================================================================

    def plan_risk_treatment(self, risk_id: int, treatment_data: Dict) -> RiskRegisterItem:
        """Plan comprehensive risk treatment"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk item not found")

        # Update treatment fields
        risk.risk_treatment_strategy = treatment_data.get("strategy")
        risk.risk_treatment_plan = treatment_data.get("plan")
        risk.risk_treatment_cost = treatment_data.get("cost")
        risk.risk_treatment_benefit = treatment_data.get("benefit")
        risk.risk_treatment_timeline = treatment_data.get("timeline")
        risk.risk_treatment_approved = False
        risk.risk_treatment_approver_id = treatment_data.get("approver_id")

        # Calculate cost-benefit ratio
        if risk.risk_treatment_cost and risk.risk_treatment_benefit:
            cost_benefit_ratio = risk.risk_treatment_benefit / risk.risk_treatment_cost
            treatment_data["cost_benefit_ratio"] = cost_benefit_ratio

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def approve_risk_treatment(self, risk_id: int, approver_id: int, approval_notes: str = None) -> RiskRegisterItem:
        """Approve risk treatment plan"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk item not found")

        risk.risk_treatment_approved = True
        risk.risk_treatment_approver_id = approver_id
        risk.risk_treatment_approval_date = datetime.utcnow()

        # Update status based on treatment strategy
        if risk.risk_treatment_strategy == "mitigate":
            risk.status = RiskStatus.MONITORING
        elif risk.risk_treatment_strategy == "accept":
            risk.status = RiskStatus.MONITORING

        self.db.commit()
        self.db.refresh(risk)
        return risk

    # ============================================================================
    # MONITORING AND REVIEW METHODS
    # ============================================================================

    def schedule_monitoring(self, risk_id: int, monitoring_data: Dict) -> RiskRegisterItem:
        """Schedule risk monitoring"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk item not found")

        risk.monitoring_frequency = monitoring_data.get("frequency", "monthly")
        risk.monitoring_method = monitoring_data.get("method")
        risk.monitoring_responsible = monitoring_data.get("responsible_id")
        risk.next_monitoring_date = self._calculate_next_date(risk.monitoring_frequency)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def schedule_review(self, risk_id: int, review_data: Dict) -> RiskRegisterItem:
        """Schedule risk review"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk item not found")

        risk.review_frequency = review_data.get("frequency", "quarterly")
        risk.review_responsible = review_data.get("responsible_id")
        risk.next_review_date = self._calculate_next_date(risk.review_frequency)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def conduct_review(self, risk_id: int, review_data: Dict) -> RiskRegisterItem:
        """Conduct risk review"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk item not found")

        risk.last_review_date = datetime.utcnow()
        risk.review_outcome = review_data.get("outcome")
        risk.next_review_date = self._calculate_next_date(risk.review_frequency)

        # Update risk status based on review outcome
        if review_data.get("status_change"):
            risk.status = review_data.get("status_change")

        self.db.commit()
        self.db.refresh(risk)
        return risk

    # ============================================================================
    # FSMS INTEGRATION METHODS
    # ============================================================================

    def create_fsms_integration(self, integration_data: Dict, integrated_by: int) -> FSMSRiskIntegration:
        """Create FSMS risk integration"""
        integration_data["integrated_by"] = integrated_by
        integration = FSMSRiskIntegration(**integration_data)
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        return integration

    def get_fsms_integrations(self, risk_id: int) -> List[FSMSRiskIntegration]:
        """Get FSMS integrations for a risk"""
        return self.db.query(FSMSRiskIntegration).filter(
            FSMSRiskIntegration.risk_register_item_id == risk_id
        ).all()

    def create_risk_from_haccp_hazard(self, hazard_id: int, created_by: int) -> RiskRegisterItem:
        """Create risk from HACCP hazard"""
        from app.models.haccp import Hazard
        
        hazard = self.db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise ValueError("Hazard not found")

        # Create risk based on hazard
        risk_data = {
            "item_type": RiskItemType.RISK,
            "title": f"HACCP Risk: {hazard.hazard_name}",
            "description": f"Risk identified from HACCP hazard analysis: {hazard.description}",
            "category": RiskCategory.HACCP,
            "classification": "food_safety",
            "severity": self._map_hazard_severity(hazard.severity),
            "likelihood": self._map_hazard_likelihood(hazard.likelihood),
            "mitigation_plan": f"Control through CCP monitoring and verification",
            "references": f"hazard:{hazard_id}",
            "created_by": created_by
        }

        # Calculate risk score
        sev_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        lik_map = {"rare": 1, "unlikely": 2, "possible": 3, "likely": 4, "almost_certain": 5}
        severity_score = sev_map.get(risk_data["severity"].value if risk_data["severity"] else "medium", 2)
        likelihood_score = lik_map.get(risk_data["likelihood"].value if risk_data["likelihood"] else "possible", 3)
        risk_data["risk_score"] = severity_score * likelihood_score

        risk = RiskRegisterItem(**risk_data)
        self.db.add(risk)
        self.db.flush()

        # Create FSMS integration
        integration_data = {
            "risk_register_item_id": risk.id,
            "fsms_element": "HACCP",
            "fsms_element_id": hazard_id,
            "impact_on_fsms": f"Potential food safety hazard requiring control measures",
            "compliance_requirement": "ISO 22000:2018 - HACCP principles"
        }
        integration = self.create_fsms_integration(integration_data, created_by)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def create_risk_from_prp_nonconformance(self, prp_id: int, nonconformance_description: str, created_by: int) -> RiskRegisterItem:
        """Create risk from PRP non-conformance"""
        from app.models.prp import PRPProgram
        
        prp = self.db.query(PRPProgram).filter(PRPProgram.id == prp_id).first()
        if not prp:
            raise ValueError("PRP program not found")

        risk_data = {
            "item_type": RiskItemType.RISK,
            "title": f"PRP Risk: {prp.name}",
            "description": f"Risk from PRP non-conformance: {nonconformance_description}",
            "category": RiskCategory.PRP,
            "classification": "food_safety",
            "severity": RiskSeverity.MEDIUM,
            "likelihood": RiskLikelihood.POSSIBLE,
            "mitigation_plan": f"Implement corrective actions for PRP program",
            "references": f"prp:{prp_id}",
            "created_by": created_by,
            "risk_score": 6  # Medium severity * Possible likelihood
        }

        risk = RiskRegisterItem(**risk_data)
        self.db.add(risk)
        self.db.flush()

        # Create FSMS integration
        integration_data = {
            "risk_register_item_id": risk.id,
            "fsms_element": "PRP",
            "fsms_element_id": prp_id,
            "impact_on_fsms": f"PRP non-conformance affecting prerequisite programs",
            "compliance_requirement": "ISO 22000:2018 - Prerequisite programs"
        }
        integration = self.create_fsms_integration(integration_data, created_by)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def create_risk_from_supplier_evaluation(self, supplier_id: int, evaluation_findings: str, created_by: int) -> RiskRegisterItem:
        """Create risk from supplier evaluation"""
        from app.models.supplier import Supplier
        
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise ValueError("Supplier not found")

        risk_data = {
            "item_type": RiskItemType.RISK,
            "title": f"Supplier Risk: {supplier.name}",
            "description": f"Risk identified from supplier evaluation: {evaluation_findings}",
            "category": RiskCategory.SUPPLIER,
            "classification": "business",
            "severity": RiskSeverity.MEDIUM,
            "likelihood": RiskLikelihood.POSSIBLE,
            "mitigation_plan": f"Implement supplier monitoring and corrective actions",
            "references": f"supplier:{supplier_id}",
            "created_by": created_by,
            "risk_score": 6  # Medium severity * Possible likelihood
        }

        risk = RiskRegisterItem(**risk_data)
        self.db.add(risk)
        self.db.flush()

        # Create FSMS integration
        integration_data = {
            "risk_register_item_id": risk.id,
            "fsms_element": "Supplier Management",
            "fsms_element_id": supplier_id,
            "impact_on_fsms": f"Supplier performance affecting food safety",
            "compliance_requirement": "ISO 22000:2018 - Supplier control"
        }
        integration = self.create_fsms_integration(integration_data, created_by)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def create_risk_from_audit_finding(self, finding_id: int, created_by: int) -> RiskRegisterItem:
        """Create risk from audit finding"""
        from app.models.audit_mgmt import AuditFinding
        
        finding = self.db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
        if not finding:
            raise ValueError("Audit finding not found")

        # Map finding severity to risk severity
        severity_map = {
            "critical": RiskSeverity.CRITICAL,
            "major": RiskSeverity.HIGH,
            "minor": RiskSeverity.MEDIUM,
            "observation": RiskSeverity.LOW
        }

        risk_data = {
            "item_type": RiskItemType.RISK,
            "title": f"Audit Risk: {finding.finding_title}",
            "description": f"Risk identified from audit finding: {finding.description}",
            "category": RiskCategory.COMPLIANCE,
            "classification": "business",
            "severity": severity_map.get(finding.severity.value if finding.severity else "minor", RiskSeverity.MEDIUM),
            "likelihood": RiskLikelihood.LIKELY,  # Audit findings are likely to reoccur if not addressed
            "mitigation_plan": f"Implement corrective action plan from audit",
            "references": f"audit_finding:{finding_id}",
            "created_by": created_by
        }

        # Calculate risk score
        sev_map = {RiskSeverity.LOW: 1, RiskSeverity.MEDIUM: 2, RiskSeverity.HIGH: 3, RiskSeverity.CRITICAL: 4}
        severity_score = sev_map.get(risk_data["severity"], 2)
        risk_data["risk_score"] = severity_score * 4  # Likely likelihood = 4

        risk = RiskRegisterItem(**risk_data)
        self.db.add(risk)
        self.db.flush()

        # Create FSMS integration
        integration_data = {
            "risk_register_item_id": risk.id,
            "fsms_element": "Audit Management",
            "fsms_element_id": finding_id,
            "impact_on_fsms": f"Audit non-conformance affecting system compliance",
            "compliance_requirement": "ISO 22000:2018 - Internal audit requirements"
        }
        integration = self.create_fsms_integration(integration_data, created_by)

        self.db.commit()
        self.db.refresh(risk)
        return risk

    def create_opportunity_from_audit_finding(self, finding_id: int, created_by: int) -> RiskRegisterItem:
        """Create opportunity from positive audit finding"""
        from app.models.audit_mgmt import AuditFinding
        
        finding = self.db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
        if not finding:
            raise ValueError("Audit finding not found")

        opportunity_data = {
            "item_type": RiskItemType.OPPORTUNITY,
            "title": f"Improvement Opportunity: {finding.finding_title}",
            "description": f"Opportunity identified from audit: {finding.description}",
            "category": RiskCategory.COMPLIANCE,
            "classification": "business",
            "opportunity_benefit": 4,  # High benefit
            "opportunity_feasibility": 3,  # Moderate feasibility
            "opportunity_score": 12,  # 4 * 3
            "risk_score": 12,  # Same as opportunity score
            "mitigation_plan": f"Implement improvement actions from audit recommendations",
            "references": f"audit_finding:{finding_id}",
            "created_by": created_by
        }

        opportunity = RiskRegisterItem(**opportunity_data)
        self.db.add(opportunity)
        self.db.flush()

        # Create FSMS integration
        integration_data = {
            "risk_register_item_id": opportunity.id,
            "fsms_element": "Continuous Improvement",
            "fsms_element_id": finding_id,
            "impact_on_fsms": f"Opportunity for system improvement and efficiency",
            "compliance_requirement": "ISO 22000:2018 - Continual improvement"
        }
        integration = self.create_fsms_integration(integration_data, created_by)

        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def _map_hazard_severity(self, hazard_severity: str) -> RiskSeverity:
        """Map HACCP hazard severity to risk severity"""
        mapping = {
            "low": RiskSeverity.LOW,
            "medium": RiskSeverity.MEDIUM,
            "high": RiskSeverity.HIGH,
            "critical": RiskSeverity.CRITICAL
        }
        return mapping.get(hazard_severity.lower() if hazard_severity else "medium", RiskSeverity.MEDIUM)

    def _map_hazard_likelihood(self, hazard_likelihood: str) -> RiskLikelihood:
        """Map HACCP hazard likelihood to risk likelihood"""
        mapping = {
            "rare": RiskLikelihood.RARE,
            "unlikely": RiskLikelihood.UNLIKELY,
            "possible": RiskLikelihood.POSSIBLE,
            "likely": RiskLikelihood.LIKELY,
            "almost_certain": RiskLikelihood.ALMOST_CERTAIN
        }
        return mapping.get(hazard_likelihood.lower() if hazard_likelihood else "possible", RiskLikelihood.POSSIBLE)

    # ============================================================================
    # RISK CORRELATION METHODS
    # ============================================================================

    def correlate_risks(self, primary_risk_id: int, correlated_risk_id: int, correlation_data: Dict) -> RiskCorrelation:
        """Create risk correlation"""
        correlation = RiskCorrelation(
            primary_risk_id=primary_risk_id,
            correlated_risk_id=correlated_risk_id,
            correlation_type=correlation_data.get("correlation_type"),
            correlation_strength=correlation_data.get("correlation_strength"),
            correlation_description=correlation_data.get("correlation_description"),
            identified_by=correlation_data.get("identified_by")
        )
        self.db.add(correlation)
        self.db.commit()
        self.db.refresh(correlation)
        return correlation

    def get_risk_correlations(self, risk_id: int) -> List[RiskCorrelation]:
        """Get correlations for a risk"""
        return self.db.query(RiskCorrelation).filter(
            or_(
                RiskCorrelation.primary_risk_id == risk_id,
                RiskCorrelation.correlated_risk_id == risk_id
            )
        ).all()

    # ============================================================================
    # RESOURCE ALLOCATION METHODS
    # ============================================================================

    def allocate_resources(self, risk_id: int, allocation_data: Dict) -> RiskResourceAllocation:
        """Allocate resources to risk treatment"""
        allocation = RiskResourceAllocation(
            risk_register_item_id=risk_id,
            resource_type=allocation_data.get("resource_type"),
            resource_amount=allocation_data.get("resource_amount"),
            resource_unit=allocation_data.get("resource_unit"),
            allocation_justification=allocation_data.get("allocation_justification"),
            allocation_approver_id=allocation_data.get("approver_id"),
            allocation_date=datetime.utcnow(),
            allocation_period=allocation_data.get("allocation_period")
        )
        self.db.add(allocation)
        self.db.commit()
        self.db.refresh(allocation)
        return allocation

    def approve_resource_allocation(self, allocation_id: int, approver_id: int) -> RiskResourceAllocation:
        """Approve resource allocation"""
        allocation = self.db.query(RiskResourceAllocation).filter(RiskResourceAllocation.id == allocation_id).first()
        if not allocation:
            raise ValueError("Resource allocation not found")

        allocation.allocation_approved = True
        allocation.allocation_approver_id = approver_id
        allocation.allocation_date = datetime.utcnow()

        self.db.commit()
        self.db.refresh(allocation)
        return allocation

    # ============================================================================
    # COMMUNICATION METHODS
    # ============================================================================

    def create_communication(self, risk_id: int, communication_data: Dict) -> RiskCommunication:
        """Create risk communication"""
        communication = RiskCommunication(
            risk_register_item_id=risk_id,
            communication_type=communication_data.get("communication_type"),
            communication_channel=communication_data.get("communication_channel"),
            target_audience=communication_data.get("target_audience"),
            communication_content=communication_data.get("communication_content"),
            communication_schedule=communication_data.get("communication_schedule"),
            communication_status="scheduled",
            sent_by=communication_data.get("sent_by")
        )
        self.db.add(communication)
        self.db.commit()
        self.db.refresh(communication)
        return communication

    def send_communication(self, communication_id: int) -> RiskCommunication:
        """Send risk communication"""
        communication = self.db.query(RiskCommunication).filter(RiskCommunication.id == communication_id).first()
        if not communication:
            raise ValueError("Communication not found")

        communication.sent_at = datetime.utcnow()
        communication.communication_status = "sent"

        self.db.commit()
        self.db.refresh(communication)
        return communication

    # ============================================================================
    # KPI METHODS
    # ============================================================================

    def create_kpi(self, kpi_data: Dict) -> RiskKPI:
        """Create risk KPI"""
        kpi = RiskKPI(**kpi_data)
        self.db.add(kpi)
        self.db.commit()
        self.db.refresh(kpi)
        return kpi

    def update_kpi_value(self, kpi_id: int, new_value: float) -> RiskKPI:
        """Update KPI current value"""
        kpi = self.db.query(RiskKPI).filter(RiskKPI.id == kpi_id).first()
        if not kpi:
            raise ValueError("KPI not found")

        kpi.kpi_current_value = new_value
        kpi.last_updated = datetime.utcnow()
        kpi.next_update = self._calculate_next_date(kpi.kpi_frequency or "monthly")

        self.db.commit()
        self.db.refresh(kpi)
        return kpi

    def get_kpis(self, category: str = None) -> List[RiskKPI]:
        """Get KPIs, optionally filtered by category"""
        query = self.db.query(RiskKPI)
        if category:
            query = query.filter(RiskKPI.kpi_category == category)
        return query.all()

    # ============================================================================
    # DASHBOARD AND ANALYTICS METHODS
    # ============================================================================

    def get_risk_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "risk_summary": self._get_risk_summary(),
            "risk_trends": self._get_risk_trends(),
            "risk_distribution": self._get_risk_distribution(),
            "risk_performance": self._get_risk_performance(),
            "risk_alerts": self._get_risk_alerts(),
            "risk_opportunities": self._get_risk_opportunities()
        }

    def _get_risk_summary(self) -> Dict[str, Any]:
        """Get risk summary statistics"""
        total_risks = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.RISK).count()
        total_opportunities = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.OPPORTUNITY).count()
        
        high_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.RISK,
            RiskRegisterItem.risk_score >= 30
        ).count()
        
        overdue_reviews = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.next_review_date < datetime.utcnow()
        ).count()

        return {
            "total_risks": total_risks,
            "total_opportunities": total_opportunities,
            "high_risks": high_risks,
            "overdue_reviews": overdue_reviews
        }

    def _get_risk_trends(self) -> Dict[str, Any]:
        """Get risk trends over time"""
        # Implementation for trend analysis
        return {"trends": "To be implemented"}

    def _get_risk_distribution(self) -> Dict[str, Any]:
        """Get risk distribution by category and severity"""
        category_distribution = self.db.query(
            RiskRegisterItem.category,
            func.count(RiskRegisterItem.id)
        ).group_by(RiskRegisterItem.category).all()

        severity_distribution = self.db.query(
            RiskRegisterItem.severity,
            func.count(RiskRegisterItem.id)
        ).filter(RiskRegisterItem.severity.isnot(None)).group_by(RiskRegisterItem.severity).all()

        return {
            "by_category": dict(category_distribution),
            "by_severity": dict(severity_distribution)
        }

    def _get_risk_performance(self) -> Dict[str, Any]:
        """Get risk performance metrics"""
        # Implementation for performance metrics
        return {"performance": "To be implemented"}

    def _get_risk_alerts(self) -> List[Dict[str, Any]]:
        """Get risk alerts and notifications"""
        alerts = []
        
        # Overdue reviews
        overdue_reviews = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.next_review_date < datetime.utcnow()
        ).limit(10).all()
        
        for risk in overdue_reviews:
            alerts.append({
                "type": "overdue_review",
                "risk_id": risk.id,
                "title": risk.title,
                "message": f"Review overdue for {risk.title}"
            })

        # High risks
        high_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.RISK,
            RiskRegisterItem.risk_score >= 30,
            RiskRegisterItem.status == RiskStatus.OPEN
        ).limit(10).all()
        
        for risk in high_risks:
            alerts.append({
                "type": "high_risk",
                "risk_id": risk.id,
                "title": risk.title,
                "message": f"High risk item: {risk.title}"
            })

        return alerts

    def _get_risk_opportunities(self) -> List[Dict[str, Any]]:
        """Get risk opportunities"""
        opportunities = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.OPPORTUNITY,
            RiskRegisterItem.status == RiskStatus.OPEN
        ).order_by(desc(RiskRegisterItem.opportunity_score)).limit(10).all()

        return [
            {
                "id": opp.id,
                "title": opp.title,
                "opportunity_score": opp.opportunity_score,
                "benefit": opp.opportunity_benefit,
                "feasibility": opp.opportunity_feasibility
            }
            for opp in opportunities
        ]

    # ============================================================================
    # ENHANCED ANALYTICS METHODS
    # ============================================================================

    def get_risk_analytics(self, filters) -> Dict[str, Any]:
        """Get comprehensive risk analytics"""
        query = self.db.query(RiskRegisterItem)
        
        # Apply filters
        if filters.date_from:
            query = query.filter(RiskRegisterItem.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(RiskRegisterItem.created_at <= filters.date_to)
        if filters.category:
            query = query.filter(RiskRegisterItem.category == filters.category)
        if filters.severity:
            query = query.filter(RiskRegisterItem.severity == filters.severity)
        if filters.status:
            query = query.filter(RiskRegisterItem.status == filters.status)
        if not filters.include_opportunities:
            query = query.filter(RiskRegisterItem.item_type == RiskItemType.RISK)

        risks = query.all()

        return {
            "total_items": len(risks),
            "risk_distribution": self._analyze_distribution(risks),
            "risk_trends": self._analyze_trends(risks),
            "risk_performance": self._analyze_performance(risks),
            "compliance_metrics": self._analyze_compliance(risks)
        }

    def get_risk_trends(self, period: str, periods_back: int) -> Dict[str, Any]:
        """Get risk trends analysis"""
        from dateutil.relativedelta import relativedelta
        
        now = datetime.utcnow()
        trends = []
        
        for i in range(periods_back):
            if period == "weekly":
                start_date = now - relativedelta(weeks=i+1)
                end_date = now - relativedelta(weeks=i)
            elif period == "monthly":
                start_date = now - relativedelta(months=i+1)
                end_date = now - relativedelta(months=i)
            elif period == "quarterly":
                start_date = now - relativedelta(months=(i+1)*3)
                end_date = now - relativedelta(months=i*3)
            else:
                continue

            period_risks = self.db.query(RiskRegisterItem).filter(
                RiskRegisterItem.created_at >= start_date,
                RiskRegisterItem.created_at < end_date
            ).all()

            new_risks = len([r for r in period_risks if r.item_type == RiskItemType.RISK])
            new_opportunities = len([r for r in period_risks if r.item_type == RiskItemType.OPPORTUNITY])
            
            resolved_risks = self.db.query(RiskRegisterItem).filter(
                RiskRegisterItem.updated_at >= start_date,
                RiskRegisterItem.updated_at < end_date,
                RiskRegisterItem.status.in_([RiskStatus.MITIGATED, RiskStatus.CLOSED])
            ).count()

            avg_risk_score = sum([r.risk_score for r in period_risks if r.risk_score]) / max(len(period_risks), 1)

            trends.append({
                "period": start_date.strftime("%Y-%m-%d"),
                "new_risks": new_risks,
                "new_opportunities": new_opportunities,
                "resolved_risks": resolved_risks,
                "avg_risk_score": round(avg_risk_score, 2)
            })

        return {"trends": trends[::-1]}  # Reverse to show oldest first

    def get_risk_performance(self) -> Dict[str, Any]:
        """Get risk management performance metrics"""
        total_risks = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.RISK).count()
        
        resolved_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.RISK,
            RiskRegisterItem.status.in_([RiskStatus.MITIGATED, RiskStatus.CLOSED])
        ).count()

        overdue_reviews = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.next_review_date < datetime.utcnow()
        ).count()

        pending_treatments = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.risk_treatment_approved == False,
            RiskRegisterItem.risk_treatment_plan.isnot(None)
        ).count()

        # Calculate performance scores
        resolution_rate = (resolved_risks / max(total_risks, 1)) * 100
        review_compliance = ((total_risks - overdue_reviews) / max(total_risks, 1)) * 100
        treatment_efficiency = ((total_risks - pending_treatments) / max(total_risks, 1)) * 100

        return {
            "total_risks": total_risks,
            "resolved_risks": resolved_risks,
            "resolution_rate": round(resolution_rate, 2),
            "overdue_reviews": overdue_reviews,
            "review_compliance": round(review_compliance, 2),
            "pending_treatments": pending_treatments,
            "treatment_efficiency": round(treatment_efficiency, 2),
            "overall_performance": round((resolution_rate + review_compliance + treatment_efficiency) / 3, 2)
        }

    def get_compliance_status(self) -> Dict[str, Any]:
        """Get ISO compliance status"""
        framework = self.get_framework()
        context = self.get_risk_context()
        
        compliance_checks = {
            "risk_management_framework": framework is not None,
            "risk_context_established": context is not None,
            "systematic_risk_assessment": self._check_assessment_compliance(),
            "risk_treatment_planning": self._check_treatment_compliance(),
            "monitoring_and_review": self._check_monitoring_compliance(),
            "fsms_integration": self._check_fsms_integration(),
            "documentation_completeness": self._check_documentation_compliance()
        }

        compliance_score = (sum(compliance_checks.values()) / len(compliance_checks)) * 100

        return {
            "compliance_score": round(compliance_score, 2),
            "compliance_checks": compliance_checks,
            "iso_31000_compliance": compliance_score >= 85,
            "iso_22000_integration": compliance_checks["fsms_integration"],
            "recommendations": self._get_compliance_recommendations(compliance_checks)
        }

    # ============================================================================
    # HELPER METHODS FOR ANALYTICS
    # ============================================================================

    def _analyze_distribution(self, risks) -> Dict[str, Any]:
        """Analyze risk distribution"""
        by_category = {}
        by_severity = {}
        by_status = {}
        
        for risk in risks:
            # Category distribution
            category = risk.category.value if risk.category else "unknown"
            by_category[category] = by_category.get(category, 0) + 1
            
            # Severity distribution (for risks only)
            if risk.item_type == RiskItemType.RISK and risk.severity:
                severity = risk.severity.value
                by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Status distribution
            status = risk.status.value if risk.status else "unknown"
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "by_category": by_category,
            "by_severity": by_severity,
            "by_status": by_status
        }

    def _analyze_trends(self, risks) -> Dict[str, Any]:
        """Analyze risk trends"""
        monthly_counts = {}
        for risk in risks:
            month = risk.created_at.strftime("%Y-%m") if risk.created_at else "unknown"
            monthly_counts[month] = monthly_counts.get(month, 0) + 1
        
        return {"monthly_creation": monthly_counts}

    def _analyze_performance(self, risks) -> Dict[str, Any]:
        """Analyze risk performance"""
        total = len(risks)
        with_treatment = len([r for r in risks if r.risk_treatment_plan])
        approved_treatment = len([r for r in risks if r.risk_treatment_approved])
        
        return {
            "total_risks": total,
            "treatment_planning_rate": (with_treatment / max(total, 1)) * 100,
            "treatment_approval_rate": (approved_treatment / max(total, 1)) * 100
        }

    def _analyze_compliance(self, risks) -> Dict[str, Any]:
        """Analyze compliance metrics"""
        total = len(risks)
        with_assessment = len([r for r in risks if r.risk_assessment_date])
        reviewed = len([r for r in risks if r.last_review_date])
        
        return {
            "assessment_compliance": (with_assessment / max(total, 1)) * 100,
            "review_compliance": (reviewed / max(total, 1)) * 100
        }

    def _check_assessment_compliance(self) -> bool:
        """Check if systematic risk assessment is in place"""
        total_risks = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.RISK).count()
        assessed_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.RISK,
            RiskRegisterItem.risk_assessment_date.isnot(None)
        ).count()
        return (assessed_risks / max(total_risks, 1)) >= 0.8

    def _check_treatment_compliance(self) -> bool:
        """Check if risk treatment planning is compliant"""
        total_risks = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.RISK).count()
        planned_treatments = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.RISK,
            RiskRegisterItem.risk_treatment_plan.isnot(None)
        ).count()
        return (planned_treatments / max(total_risks, 1)) >= 0.7

    def _check_monitoring_compliance(self) -> bool:
        """Check if monitoring and review is compliant"""
        total_risks = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.RISK).count()
        monitored_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.item_type == RiskItemType.RISK,
            RiskRegisterItem.next_monitoring_date.isnot(None)
        ).count()
        return (monitored_risks / max(total_risks, 1)) >= 0.7

    def _check_fsms_integration(self) -> bool:
        """Check if FSMS integration is in place"""
        total_risks = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == RiskItemType.RISK).count()
        integrated_risks = self.db.query(FSMSRiskIntegration).count()
        return (integrated_risks / max(total_risks, 1)) >= 0.5

    def _check_documentation_compliance(self) -> bool:
        """Check if documentation is compliant"""
        framework = self.get_framework()
        context = self.get_risk_context()
        return framework is not None and context is not None

    def _get_compliance_recommendations(self, compliance_checks: Dict[str, bool]) -> List[str]:
        """Get compliance recommendations"""
        recommendations = []
        
        if not compliance_checks["risk_management_framework"]:
            recommendations.append("Establish a comprehensive risk management framework (ISO 31000:2018)")
        if not compliance_checks["risk_context_established"]:
            recommendations.append("Define organizational risk context and stakeholder analysis")
        if not compliance_checks["systematic_risk_assessment"]:
            recommendations.append("Implement systematic risk assessment methodology")
        if not compliance_checks["risk_treatment_planning"]:
            recommendations.append("Develop comprehensive risk treatment plans")
        if not compliance_checks["monitoring_and_review"]:
            recommendations.append("Establish monitoring and review schedules")
        if not compliance_checks["fsms_integration"]:
            recommendations.append("Integrate risk management with FSMS elements (ISO 22000:2018)")
        if not compliance_checks["documentation_completeness"]:
            recommendations.append("Complete risk management documentation")
        
        return recommendations
