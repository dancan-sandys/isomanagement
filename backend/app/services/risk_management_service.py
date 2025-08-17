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

    def integrate_with_fsms(self, risk_id: int, fsms_data: Dict) -> FSMSRiskIntegration:
        """Integrate risk with FSMS elements"""
        integration = FSMSRiskIntegration(
            risk_register_item_id=risk_id,
            fsms_element=fsms_data.get("fsms_element"),
            fsms_element_id=fsms_data.get("fsms_element_id"),
            impact_on_fsms=fsms_data.get("impact_on_fsms"),
            food_safety_objective_id=fsms_data.get("food_safety_objective_id"),
            interested_party_impact=fsms_data.get("interested_party_impact"),
            compliance_requirement=fsms_data.get("compliance_requirement"),
            integrated_by=fsms_data.get("integrated_by")
        )
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        return integration

    def get_fsms_integrations(self, risk_id: int) -> List[FSMSRiskIntegration]:
        """Get FSMS integrations for a risk"""
        return self.db.query(FSMSRiskIntegration).filter(
            FSMSRiskIntegration.risk_register_item_id == risk_id
        ).all()

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
