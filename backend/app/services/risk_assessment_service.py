from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.nonconformance import (
    NonConformanceRiskAssessment, NonConformance, EscalationRule
)
from app.schemas.nonconformance import (
    NonConformanceRiskAssessmentCreate,
    NonConformanceRiskAssessmentUpdate,
    NonConformanceRiskAssessmentFilter,
    NonConformanceRiskAssessmentCalculationRequest,
)


class RiskAssessmentService:
    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations
    def create_risk_assessment(self, assessment_data: NonConformanceRiskAssessmentCreate, created_by: int) -> NonConformanceRiskAssessment:
        """Create a new risk assessment"""
        # Calculate risk score and matrix position
        risk_score = self._calculate_risk_score(
            assessment_data.food_safety_impact,
            assessment_data.regulatory_impact,
            assessment_data.customer_impact,
            assessment_data.business_impact
        )
        
        matrix_position = self._calculate_risk_matrix_position(risk_score)
        requires_escalation = self._determine_escalation_need(risk_score)
        escalation_level = self._determine_escalation_level(risk_score) if requires_escalation else None
        
        risk_assessment = NonConformanceRiskAssessment(
            **assessment_data.dict(),
            overall_risk_score=risk_score,
            risk_matrix_position=matrix_position,
            requires_escalation=requires_escalation,
            escalation_level=escalation_level,
            created_by=created_by
        )
        
        self.db.add(risk_assessment)
        self.db.commit()
        self.db.refresh(risk_assessment)
        
        # Check for escalation triggers
        if requires_escalation:
            self._trigger_escalation(risk_assessment)
        
        return risk_assessment

    def get_risk_assessments(self, filter_params: NonConformanceRiskAssessmentFilter) -> Dict[str, Any]:
        """Get risk assessments with filtering and pagination"""
        query = self.db.query(NonConformanceRiskAssessment)

        # Apply filters
        if filter_params.non_conformance_id:
            query = query.filter(NonConformanceRiskAssessment.non_conformance_id == filter_params.non_conformance_id)

        if filter_params.food_safety_impact:
            query = query.filter(NonConformanceRiskAssessment.food_safety_impact == filter_params.food_safety_impact)

        if filter_params.regulatory_impact:
            query = query.filter(NonConformanceRiskAssessment.regulatory_impact == filter_params.regulatory_impact)

        if filter_params.requires_escalation is not None:
            query = query.filter(NonConformanceRiskAssessment.requires_escalation == filter_params.requires_escalation)

        if filter_params.risk_score_min is not None:
            query = query.filter(NonConformanceRiskAssessment.overall_risk_score >= filter_params.risk_score_min)

        if filter_params.risk_score_max is not None:
            query = query.filter(NonConformanceRiskAssessment.overall_risk_score <= filter_params.risk_score_max)

        if filter_params.date_from:
            query = query.filter(NonConformanceRiskAssessment.created_at >= filter_params.date_from)

        if filter_params.date_to:
            query = query.filter(NonConformanceRiskAssessment.created_at <= filter_params.date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        risk_assessments = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": risk_assessments,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_risk_assessment(self, assessment_id: int) -> Optional[NonConformanceRiskAssessment]:
        """Get risk assessment by ID"""
        return self.db.query(NonConformanceRiskAssessment).filter(NonConformanceRiskAssessment.id == assessment_id).first()

    def get_risk_assessment_by_nc(self, nc_id: int) -> Optional[NonConformanceRiskAssessment]:
        """Get risk assessment for a specific non-conformance"""
        return self.db.query(NonConformanceRiskAssessment).filter(
            NonConformanceRiskAssessment.non_conformance_id == nc_id
        ).order_by(NonConformanceRiskAssessment.created_at.desc()).first()

    def update_risk_assessment(self, assessment_id: int, assessment_data: NonConformanceRiskAssessmentUpdate) -> Optional[NonConformanceRiskAssessment]:
        """Update risk assessment"""
        risk_assessment = self.get_risk_assessment(assessment_id)
        if not risk_assessment:
            return None

        update_data = assessment_data.dict(exclude_unset=True)
        
        # Recalculate risk score if impact fields are updated
        if any(field in update_data for field in ['food_safety_impact', 'regulatory_impact', 'customer_impact', 'business_impact']):
            risk_score = self._calculate_risk_score(
                update_data.get('food_safety_impact', risk_assessment.food_safety_impact),
                update_data.get('regulatory_impact', risk_assessment.regulatory_impact),
                update_data.get('customer_impact', risk_assessment.customer_impact),
                update_data.get('business_impact', risk_assessment.business_impact)
            )
            update_data['overall_risk_score'] = risk_score
            update_data['risk_matrix_position'] = self._calculate_risk_matrix_position(risk_score)
            update_data['requires_escalation'] = self._determine_escalation_need(risk_score)
            update_data['escalation_level'] = self._determine_escalation_level(risk_score) if update_data['requires_escalation'] else None

        for field, value in update_data.items():
            setattr(risk_assessment, field, value)

        self.db.commit()
        self.db.refresh(risk_assessment)
        
        # Check for escalation triggers if risk score changed
        if 'overall_risk_score' in update_data:
            self._trigger_escalation(risk_assessment)
        
        return risk_assessment

    def delete_risk_assessment(self, assessment_id: int) -> bool:
        """Delete risk assessment"""
        risk_assessment = self.get_risk_assessment(assessment_id)
        if not risk_assessment:
            return False

        self.db.delete(risk_assessment)
        self.db.commit()
        return True

    # Risk Calculation Logic
    def _calculate_risk_score(self, food_safety_impact: str, regulatory_impact: str, 
                            customer_impact: str, business_impact: str) -> float:
        """Calculate the overall risk score based on impact assessments"""
        impact_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        food_safety = impact_scores.get(food_safety_impact.lower(), 1)
        regulatory = impact_scores.get(regulatory_impact.lower(), 1)
        customer = impact_scores.get(customer_impact.lower(), 1)
        business = impact_scores.get(business_impact.lower(), 1)
        
        # Weighted average (food safety and regulatory have higher weights)
        overall_score = (food_safety * 0.4 + regulatory * 0.3 + customer * 0.2 + business * 0.1)
        return round(overall_score, 2)

    def _calculate_risk_matrix_position(self, risk_score: float) -> str:
        """Calculate risk matrix position based on risk score"""
        if risk_score >= 3.5:
            return "A1"  # Critical
        elif risk_score >= 2.5:
            return "B2"  # High
        elif risk_score >= 1.5:
            return "C3"  # Medium
        else:
            return "D4"  # Low

    def _determine_escalation_need(self, risk_score: float) -> bool:
        """Determine if escalation is required based on risk score"""
        return risk_score >= 3.0

    def _determine_escalation_level(self, risk_score: float) -> str:
        """Determine escalation level based on risk score"""
        if risk_score >= 3.5:
            return "executive"
        elif risk_score >= 3.0:
            return "director"
        elif risk_score >= 2.5:
            return "manager"
        else:
            return "supervisor"

    def calculate_risk_from_request(self, calculation_request: NonConformanceRiskAssessmentCalculationRequest) -> Dict[str, Any]:
        """Calculate risk score from request data"""
        risk_score = self._calculate_risk_score(
            calculation_request.food_safety_impact,
            calculation_request.regulatory_impact,
            calculation_request.customer_impact,
            calculation_request.business_impact
        )
        
        matrix_position = self._calculate_risk_matrix_position(risk_score)
        requires_escalation = self._determine_escalation_need(risk_score)
        escalation_level = self._determine_escalation_level(risk_score) if requires_escalation else None
        risk_level = self._get_risk_level(risk_score)
        
        return {
            "overall_risk_score": risk_score,
            "risk_matrix_position": matrix_position,
            "requires_escalation": requires_escalation,
            "escalation_level": escalation_level,
            "risk_level": risk_level
        }

    def _get_risk_level(self, risk_score: float) -> str:
        """Get the risk level based on the overall risk score"""
        if risk_score >= 3.5:
            return "critical"
        elif risk_score >= 2.5:
            return "high"
        elif risk_score >= 1.5:
            return "medium"
        else:
            return "low"

    # Escalation Trigger Logic
    def _trigger_escalation(self, risk_assessment: NonConformanceRiskAssessment) -> None:
        """Trigger escalation based on risk assessment"""
        # Get active escalation rules
        escalation_rules = self.db.query(EscalationRule).filter(
            and_(
                EscalationRule.is_active == True,
                EscalationRule.trigger_condition == "risk_score"
            )
        ).all()
        
        for rule in escalation_rules:
            if rule.should_trigger(risk_assessment.overall_risk_score):
                # Here you would implement the actual escalation logic
                # For now, we'll just log it
                print(f"Escalation triggered: Rule '{rule.rule_name}' for risk score {risk_assessment.overall_risk_score}")

    # Business Logic Methods
    def get_high_risk_assessments(self, threshold: float = 3.0) -> List[NonConformanceRiskAssessment]:
        """Get all risk assessments above a certain threshold"""
        return (
            self.db.query(NonConformanceRiskAssessment)
            .filter(NonConformanceRiskAssessment.overall_risk_score >= threshold)
            .order_by(NonConformanceRiskAssessment.overall_risk_score.desc())
            .all()
        )

    def get_assessments_requiring_escalation(self) -> List[NonConformanceRiskAssessment]:
        """Get all risk assessments that require escalation"""
        return (
            self.db.query(NonConformanceRiskAssessment)
            .filter(NonConformanceRiskAssessment.requires_escalation == True)
            .order_by(NonConformanceRiskAssessment.created_at.desc())
            .all()
        )

    def get_risk_statistics(self, nc_id: Optional[int] = None) -> Dict[str, Any]:
        """Get risk assessment statistics"""
        query = self.db.query(NonConformanceRiskAssessment)
        
        if nc_id:
            query = query.filter(NonConformanceRiskAssessment.non_conformance_id == nc_id)
        
        total_assessments = query.count()
        
        # Risk level distribution
        risk_levels = {
            'critical': query.filter(NonConformanceRiskAssessment.overall_risk_score >= 3.5).count(),
            'high': query.filter(and_(NonConformanceRiskAssessment.overall_risk_score >= 2.5, NonConformanceRiskAssessment.overall_risk_score < 3.5)).count(),
            'medium': query.filter(and_(NonConformanceRiskAssessment.overall_risk_score >= 1.5, NonConformanceRiskAssessment.overall_risk_score < 2.5)).count(),
            'low': query.filter(NonConformanceRiskAssessment.overall_risk_score < 1.5).count()
        }
        
        # Escalation statistics
        requiring_escalation = query.filter(RiskAssessment.requires_escalation == True).count()
        escalation_rate = (requiring_escalation / total_assessments * 100) if total_assessments > 0 else 0
        
        # Average risk score
        avg_risk_score = query.with_entities(func.avg(NonConformanceRiskAssessment.overall_risk_score)).scalar() or 0
        
        return {
            "total_assessments": total_assessments,
            "risk_levels": risk_levels,
            "requiring_escalation": requiring_escalation,
            "escalation_rate": round(escalation_rate, 2),
            "average_risk_score": round(avg_risk_score, 2)
        }

    def get_risk_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get risk assessment trends over time"""
        start_date = datetime.now() - timedelta(days=days)
        
        assessments = (
            self.db.query(NonConformanceRiskAssessment)
            .filter(NonConformanceRiskAssessment.created_at >= start_date)
            .order_by(NonConformanceRiskAssessment.created_at.asc())
            .all()
        )
        
        trends = []
        for assessment in assessments:
            trends.append({
                "date": assessment.created_at.date(),
                "risk_score": assessment.overall_risk_score,
                "risk_level": self._get_risk_level(assessment.overall_risk_score),
                "requires_escalation": assessment.requires_escalation,
                "nc_id": assessment.non_conformance_id
            })
        
        return trends

    def get_risk_matrix_summary(self) -> Dict[str, Any]:
        """Get summary of risk matrix positions"""
        matrix_positions = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D4']
        
        summary = {}
        for position in matrix_positions:
            count = (
                self.db.query(NonConformanceRiskAssessment)
                .filter(NonConformanceRiskAssessment.risk_matrix_position == position)
                .count()
            )
            summary[position] = count
        
        return summary

    def get_recent_high_risk_assessments(self, days: int = 7, threshold: float = 3.0) -> List[NonConformanceRiskAssessment]:
        """Get recent high-risk assessments"""
        start_date = datetime.now() - timedelta(days=days)
        
        return (
            self.db.query(NonConformanceRiskAssessment)
            .filter(
                and_(
                    NonConformanceRiskAssessment.overall_risk_score >= threshold,
                    NonConformanceRiskAssessment.created_at >= start_date,
                )
            )
            .order_by(NonConformanceRiskAssessment.created_at.desc())
            .all()
        )

    def validate_risk_assessment(self, assessment_data: NonConformanceRiskAssessmentCalculationRequest) -> Dict[str, Any]:
        """Validate risk assessment data and provide recommendations"""
        risk_score = self._calculate_risk_score(
            assessment_data.food_safety_impact,
            assessment_data.regulatory_impact,
            assessment_data.customer_impact,
            assessment_data.business_impact
        )
        
        recommendations = []
        warnings = []
        
        # Check for high-risk combinations
        if assessment_data.food_safety_impact == 'critical' and assessment_data.regulatory_impact == 'critical':
            warnings.append("Critical food safety and regulatory impact detected - immediate escalation required")
        
        if risk_score >= 3.5:
            recommendations.append("Consider immediate containment actions")
            recommendations.append("Notify executive management immediately")
        
        if risk_score >= 3.0:
            recommendations.append("Escalation to management required")
            recommendations.append("Implement immediate corrective actions")
        
        return {
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "requires_escalation": self._determine_escalation_need(risk_score),
            "recommendations": recommendations,
            "warnings": warnings,
            "is_valid": True
        }
