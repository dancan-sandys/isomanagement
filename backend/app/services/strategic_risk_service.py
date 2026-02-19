from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from datetime import datetime, timedelta
import json

from app.models.risk import RiskRegisterItem, RiskCategory, RiskStatus, RiskSeverity
from app.services.risk_management_service import RiskManagementService


class StrategicRiskService:
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = RiskManagementService(db)

    def analyze_risk_correlations(self, risk_id: int) -> Dict[str, Any]:
        """Analyze correlations for a specific risk"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk not found")

        # Find correlated risks based on category, business unit, and impact areas
        correlated_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.id != risk_id,
            or_(
                RiskRegisterItem.category == risk.category,
                RiskRegisterItem.business_unit == risk.business_unit,
                RiskRegisterItem.project_association == risk.project_association
            )
        ).all()

        # Analyze correlation strength based on various factors
        correlations = []
        for correlated_risk in correlated_risks:
            correlation_strength = self._calculate_correlation_strength(risk, correlated_risk)
            correlation_type = self._determine_correlation_type(risk, correlated_risk)
            correlation_direction = self._determine_correlation_direction(risk, correlated_risk)
            
            correlations.append({
                "correlated_risk_id": correlated_risk.id,
                "correlated_risk_title": correlated_risk.title,
                "correlation_strength": correlation_strength,
                "correlation_type": correlation_type,
                "correlation_direction": correlation_direction,
                "impact_analysis": self._analyze_correlation_impact(risk, correlated_risk)
            })

        return {
            "risk_id": risk_id,
            "risk_title": risk.title,
            "correlations": correlations,
            "total_correlations": len(correlations)
        }

    def _calculate_correlation_strength(self, risk1: RiskRegisterItem, risk2: RiskRegisterItem) -> int:
        """Calculate correlation strength between two risks (1-5 scale)"""
        strength = 1
        
        # Category correlation
        if risk1.category == risk2.category:
            strength += 2
        
        # Business unit correlation
        if risk1.business_unit and risk2.business_unit and risk1.business_unit == risk2.business_unit:
            strength += 1
        
        # Project association correlation
        if risk1.project_association and risk2.project_association and risk1.project_association == risk2.project_association:
            strength += 1
        
        # Risk level correlation
        if risk1.risk_score and risk2.risk_score:
            score_diff = abs(risk1.risk_score - risk2.risk_score)
            if score_diff <= 5:
                strength += 1
        
        return min(strength, 5)

    def _determine_correlation_type(self, risk1: RiskRegisterItem, risk2: RiskRegisterItem) -> str:
        """Determine correlation type between two risks"""
        if risk1.category == risk2.category and risk1.business_unit == risk2.business_unit:
            return "direct"
        elif risk1.category == risk2.category or risk1.business_unit == risk2.business_unit:
            return "indirect"
        elif risk1.risk_cascade or risk2.risk_cascade:
            return "cascading"
        elif risk1.risk_amplification or risk2.risk_amplification:
            return "amplifying"
        else:
            return "indirect"

    def _determine_correlation_direction(self, risk1: RiskRegisterItem, risk2: RiskRegisterItem) -> str:
        """Determine correlation direction between two risks"""
        if risk1.risk_score and risk2.risk_score:
            if risk1.risk_score > risk2.risk_score:
                return "positive"
            elif risk1.risk_score < risk2.risk_score:
                return "negative"
            else:
                return "bidirectional"
        return "bidirectional"

    def _analyze_correlation_impact(self, risk1: RiskRegisterItem, risk2: RiskRegisterItem) -> str:
        """Analyze the impact of correlation between two risks"""
        impacts = []
        
        if risk1.category == risk2.category:
            impacts.append(f"Both risks are in the same category ({risk1.category.value})")
        
        if risk1.business_unit and risk2.business_unit and risk1.business_unit == risk2.business_unit:
            impacts.append(f"Both risks affect the same business unit ({risk1.business_unit})")
        
        if risk1.project_association and risk2.project_association and risk1.project_association == risk2.project_association:
            impacts.append(f"Both risks are associated with the same project ({risk1.project_association})")
        
        if risk1.risk_cascade or risk2.risk_cascade:
            impacts.append("Risk cascade effects may amplify overall impact")
        
        if risk1.risk_amplification or risk2.risk_amplification:
            impacts.append("Risk amplification may increase severity")
        
        return "; ".join(impacts) if impacts else "Limited direct correlation impact"

    def optimize_resource_allocation(self, risk_id: int, available_resources: Dict[str, float]) -> Dict[str, Any]:
        """Optimize resource allocation for a specific risk"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk not found")

        # Calculate optimal resource allocation based on risk characteristics
        allocation = {
            "personnel": self._calculate_personnel_allocation(risk, available_resources.get("personnel", 0)),
            "financial": self._calculate_financial_allocation(risk, available_resources.get("financial", 0)),
            "time": self._calculate_time_allocation(risk, available_resources.get("time", 0)),
            "equipment": self._calculate_equipment_allocation(risk, available_resources.get("equipment", 0))
        }

        # Calculate priority scores for each resource type
        priority_scores = {
            "personnel": self._calculate_priority_score(risk, "personnel"),
            "financial": self._calculate_priority_score(risk, "financial"),
            "time": self._calculate_priority_score(risk, "time"),
            "equipment": self._calculate_priority_score(risk, "equipment")
        }

        return {
            "risk_id": risk_id,
            "risk_title": risk.title,
            "allocation": allocation,
            "priority_scores": priority_scores,
            "justification": self._generate_allocation_justification(risk, allocation, priority_scores)
        }

    def _calculate_personnel_allocation(self, risk: RiskRegisterItem, available_personnel: float) -> float:
        """Calculate optimal personnel allocation"""
        base_allocation = 0.1  # 10% base allocation
        
        # Adjust based on risk score
        if risk.risk_score:
            if risk.risk_score >= 80:
                base_allocation = 0.4
            elif risk.risk_score >= 60:
                base_allocation = 0.3
            elif risk.risk_score >= 40:
                base_allocation = 0.2
            elif risk.risk_score >= 20:
                base_allocation = 0.15
        
        # Adjust based on category
        if risk.category in [RiskCategory.STRATEGIC, RiskCategory.FINANCIAL, RiskCategory.REPUTATIONAL]:
            base_allocation *= 1.5
        
        return min(base_allocation * available_personnel, available_personnel)

    def _calculate_financial_allocation(self, risk: RiskRegisterItem, available_financial: float) -> float:
        """Calculate optimal financial allocation"""
        base_allocation = 0.05  # 5% base allocation
        
        # Adjust based on risk score
        if risk.risk_score:
            if risk.risk_score >= 80:
                base_allocation = 0.3
            elif risk.risk_score >= 60:
                base_allocation = 0.2
            elif risk.risk_score >= 40:
                base_allocation = 0.15
            elif risk.risk_score >= 20:
                base_allocation = 0.1
        
        # Adjust based on financial impact
        if risk.financial_impact:
            base_allocation *= 1.5
        
        return min(base_allocation * available_financial, available_financial)

    def _calculate_time_allocation(self, risk: RiskRegisterItem, available_time: float) -> float:
        """Calculate optimal time allocation"""
        base_allocation = 0.15  # 15% base allocation
        
        # Adjust based on risk velocity
        if risk.risk_velocity:
            if risk.risk_velocity == "fast":
                base_allocation = 0.4
            elif risk.risk_velocity == "medium":
                base_allocation = 0.25
            elif risk.risk_velocity == "slow":
                base_allocation = 0.1
        
        return min(base_allocation * available_time, available_time)

    def _calculate_equipment_allocation(self, risk: RiskRegisterItem, available_equipment: float) -> float:
        """Calculate optimal equipment allocation"""
        base_allocation = 0.1  # 10% base allocation
        
        # Adjust based on category
        if risk.category in [RiskCategory.EQUIPMENT, RiskCategory.TECHNOLOGY]:
            base_allocation = 0.3
        
        return min(base_allocation * available_equipment, available_equipment)

    def _calculate_priority_score(self, risk: RiskRegisterItem, resource_type: str) -> int:
        """Calculate priority score for resource allocation (1-5 scale)"""
        score = 1
        
        # Risk score impact
        if risk.risk_score:
            if risk.risk_score >= 80:
                score += 3
            elif risk.risk_score >= 60:
                score += 2
            elif risk.risk_score >= 40:
                score += 1
        
        # Category impact
        if risk.category in [RiskCategory.STRATEGIC, RiskCategory.FINANCIAL, RiskCategory.REPUTATIONAL]:
            score += 1
        
        # Resource type specific adjustments
        if resource_type == "personnel" and risk.category in [RiskCategory.STAFF, RiskCategory.TRAINING]:
            score += 1
        elif resource_type == "financial" and risk.financial_impact:
            score += 1
        elif resource_type == "time" and risk.risk_velocity == "fast":
            score += 1
        elif resource_type == "equipment" and risk.category in [RiskCategory.EQUIPMENT, RiskCategory.TECHNOLOGY]:
            score += 1
        
        return min(score, 5)

    def _generate_allocation_justification(self, risk: RiskRegisterItem, allocation: Dict, priority_scores: Dict) -> str:
        """Generate justification for resource allocation"""
        justifications = []
        
        if allocation["personnel"] > 0:
            justifications.append(f"Personnel allocation: {allocation['personnel']:.1f} units (Priority: {priority_scores['personnel']}/5)")
        
        if allocation["financial"] > 0:
            justifications.append(f"Financial allocation: {allocation['financial']:.1f} units (Priority: {priority_scores['financial']}/5)")
        
        if allocation["time"] > 0:
            justifications.append(f"Time allocation: {allocation['time']:.1f} units (Priority: {priority_scores['time']}/5)")
        
        if allocation["equipment"] > 0:
            justifications.append(f"Equipment allocation: {allocation['equipment']:.1f} units (Priority: {priority_scores['equipment']}/5)")
        
        return "; ".join(justifications)

    def create_risk_aggregation(self, aggregation_data: Dict) -> Dict[str, Any]:
        """Create a risk aggregation based on specified criteria"""
        criteria = aggregation_data.get("criteria", {})
        
        # Build query based on criteria
        query = self.db.query(RiskRegisterItem)
        
        if "category" in criteria:
            query = query.filter(RiskRegisterItem.category == criteria["category"])
        
        if "business_unit" in criteria:
            query = query.filter(RiskRegisterItem.business_unit == criteria["business_unit"])
        
        if "status" in criteria:
            query = query.filter(RiskRegisterItem.status == criteria["status"])
        
        if "min_risk_score" in criteria:
            query = query.filter(RiskRegisterItem.risk_score >= criteria["min_risk_score"])
        
        if "max_risk_score" in criteria:
            query = query.filter(RiskRegisterItem.risk_score <= criteria["max_risk_score"])
        
        risks = query.all()
        
        if not risks:
            return {
                "aggregation_name": aggregation_data.get("name", "Risk Aggregation"),
                "risks": [],
                "aggregated_score": 0,
                "aggregated_level": "LOW",
                "message": "No risks found matching the criteria"
            }
        
        # Calculate aggregated metrics
        total_score = sum(risk.risk_score for risk in risks if risk.risk_score)
        avg_score = total_score / len(risks) if risks else 0
        
        # Determine aggregated risk level
        if avg_score >= 80:
            aggregated_level = "CRITICAL"
        elif avg_score >= 60:
            aggregated_level = "HIGH"
        elif avg_score >= 40:
            aggregated_level = "MEDIUM"
        elif avg_score >= 20:
            aggregated_level = "LOW"
        else:
            aggregated_level = "VERY_LOW"
        
        return {
            "aggregation_name": aggregation_data.get("name", "Risk Aggregation"),
            "risks": [{"id": risk.id, "title": risk.title, "risk_score": risk.risk_score} for risk in risks],
            "total_risks": len(risks),
            "aggregated_score": avg_score,
            "aggregated_level": aggregated_level,
            "category_distribution": self._get_category_distribution(risks),
            "status_distribution": self._get_status_distribution(risks)
        }

    def _get_category_distribution(self, risks: List[RiskRegisterItem]) -> Dict[str, int]:
        """Get distribution of risks by category"""
        distribution = {}
        for risk in risks:
            category = risk.category.value
            distribution[category] = distribution.get(category, 0) + 1
        return distribution

    def _get_status_distribution(self, risks: List[RiskRegisterItem]) -> Dict[str, int]:
        """Get distribution of risks by status"""
        distribution = {}
        for risk in risks:
            status = risk.status.value
            distribution[status] = distribution.get(status, 0) + 1
        return distribution

    def get_strategic_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive strategic risk summary"""
        total_risks = self.db.query(RiskRegisterItem).count()
        
        # Strategic risk categories
        strategic_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.category.in_([
                RiskCategory.STRATEGIC, RiskCategory.FINANCIAL, RiskCategory.REPUTATIONAL,
                RiskCategory.BUSINESS_CONTINUITY, RiskCategory.REGULATORY
            ])
        ).count()
        
        # High-risk strategic items
        high_risk_strategic = self.db.query(RiskRegisterItem).filter(
            and_(
                RiskRegisterItem.category.in_([
                    RiskCategory.STRATEGIC, RiskCategory.FINANCIAL, RiskCategory.REPUTATIONAL,
                    RiskCategory.BUSINESS_CONTINUITY, RiskCategory.REGULATORY
                ]),
                RiskRegisterItem.risk_score >= 60
            )
        ).count()
        
        # Risk distribution by category
        category_distribution = self.db.query(
            RiskRegisterItem.category,
            func.count(RiskRegisterItem.id)
        ).group_by(RiskRegisterItem.category).all()
        
        # Risk distribution by business unit
        business_unit_distribution = self.db.query(
            RiskRegisterItem.business_unit,
            func.count(RiskRegisterItem.id)
        ).filter(RiskRegisterItem.business_unit.isnot(None)).group_by(RiskRegisterItem.business_unit).all()
        
        return {
            "total_risks": total_risks,
            "strategic_risks": strategic_risks,
            "high_risk_strategic": high_risk_strategic,
            "category_distribution": dict(category_distribution),
            "business_unit_distribution": dict(business_unit_distribution)
        }

    def get_strategic_risk_alerts(self) -> List[Dict[str, Any]]:
        """Get strategic risk alerts and notifications"""
        alerts = []
        
        # High-risk strategic items
        high_risk_strategic = self.db.query(RiskRegisterItem).filter(
            and_(
                RiskRegisterItem.category.in_([
                    RiskCategory.STRATEGIC, RiskCategory.FINANCIAL, RiskCategory.REPUTATIONAL,
                    RiskCategory.BUSINESS_CONTINUITY, RiskCategory.REGULATORY
                ]),
                RiskRegisterItem.risk_score >= 60
            )
        ).limit(10).all()
        
        for risk in high_risk_strategic:
            alerts.append({
                "type": "high_risk_strategic",
                "risk_id": risk.id,
                "risk_title": risk.title,
                "category": risk.category.value,
                "risk_score": risk.risk_score,
                "message": f"High-risk strategic item: {risk.title}"
            })
        
        # Fast-moving risks
        fast_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.risk_velocity == "fast"
        ).limit(10).all()
        
        for risk in fast_risks:
            alerts.append({
                "type": "fast_moving_risk",
                "risk_id": risk.id,
                "risk_title": risk.title,
                "risk_velocity": risk.risk_velocity,
                "message": f"Fast-moving risk: {risk.title}"
            })
        
        # Cascade risks
        cascade_risks = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.risk_cascade == True
        ).limit(10).all()
        
        for risk in cascade_risks:
            alerts.append({
                "type": "cascade_risk",
                "risk_id": risk.id,
                "risk_title": risk.title,
                "message": f"Cascade risk identified: {risk.title}"
            })
        
        return alerts

