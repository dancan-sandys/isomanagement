# -*- coding: utf-8 -*-
"""
ISO Compliance Service
Dedicated service for ISO 9001:2015 compliance tracking and assessment
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.actions_log import (
    SWOTAnalysis, SWOTItem, SWOTAction, PESTELAnalysis, PESTELItem, PESTELAction,
    ActionLog, ActionStatus, ActionPriority
)
from app.schemas.swot_pestel import (
    ISOComplianceMetrics, StrategicInsights, ContinuousImprovementMetrics,
    ISODashboardMetrics, ISOAuditFinding, ManagementReviewInput
)


class ISOComplianceService:
    """Service class for ISO 9001:2015 compliance management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assess_clause_4_1_compliance(self) -> Dict[str, Any]:
        """
        Assess compliance with ISO 9001:2015 Clause 4.1 - Understanding the organization and its context
        """
        # Get all SWOT and PESTEL analyses
        swot_analyses = self.db.query(SWOTAnalysis).all()
        pestel_analyses = self.db.query(PESTELAnalysis).all()
        
        total_analyses = len(swot_analyses) + len(pestel_analyses)
        
        # Check for strategic context documentation
        swot_with_context = sum(1 for a in swot_analyses if a.strategic_context)
        pestel_with_context = sum(1 for a in pestel_analyses if a.strategic_context)
        total_with_context = swot_with_context + pestel_with_context
        
        # Check for internal/external issues identification
        internal_issues_identified = sum(1 for a in swot_analyses if a.strategic_context and 
                                       'internal_issues' in str(a.strategic_context))
        external_issues_identified = sum(1 for a in pestel_analyses if a.strategic_context and 
                                       'external_issues' in str(a.strategic_context))
        
        # Check for interested parties identification
        interested_parties_documented = sum(1 for a in swot_analyses + pestel_analyses if a.strategic_context and 
                                          'interested_parties' in str(a.strategic_context))
        
        # Calculate compliance percentages
        context_compliance_rate = (total_with_context / total_analyses * 100) if total_analyses > 0 else 0
        
        return {
            "clause": "4.1",
            "title": "Understanding the organization and its context",
            "total_analyses": total_analyses,
            "analyses_with_context": total_with_context,
            "context_compliance_rate": context_compliance_rate,
            "internal_issues_identified": internal_issues_identified,
            "external_issues_identified": external_issues_identified,
            "interested_parties_documented": interested_parties_documented,
            "swot_analyses": {
                "total": len(swot_analyses),
                "with_context": swot_with_context,
                "organization_wide": sum(1 for a in swot_analyses if a.scope == "organization_wide"),
                "current_analyses": sum(1 for a in swot_analyses if a.is_current)
            },
            "pestel_analyses": {
                "total": len(pestel_analyses),
                "with_context": pestel_with_context,
                "organization_wide": sum(1 for a in pestel_analyses if a.scope == "organization_wide"),
                "current_analyses": sum(1 for a in pestel_analyses if a.is_current)
            },
            "compliance_gaps": self._identify_compliance_gaps(swot_analyses, pestel_analyses),
            "recommendations": self._get_clause_4_1_recommendations(context_compliance_rate)
        }
    
    def _identify_compliance_gaps(self, swot_analyses: List[SWOTAnalysis], 
                                pestel_analyses: List[PESTELAnalysis]) -> List[str]:
        """Identify specific compliance gaps"""
        gaps = []
        
        if not swot_analyses:
            gaps.append("No SWOT analyses found - internal context assessment missing")
        
        if not pestel_analyses:
            gaps.append("No PESTEL analyses found - external context assessment missing")
        
        # Check for missing strategic context
        swot_without_context = [a for a in swot_analyses if not a.strategic_context]
        if swot_without_context:
            gaps.append(f"{len(swot_without_context)} SWOT analyses missing strategic context")
        
        pestel_without_context = [a for a in pestel_analyses if not a.strategic_context]
        if pestel_without_context:
            gaps.append(f"{len(pestel_without_context)} PESTEL analyses missing strategic context")
        
        # Check for missing scope definition
        analyses_without_scope = [a for a in swot_analyses + pestel_analyses if not a.scope]
        if analyses_without_scope:
            gaps.append(f"{len(analyses_without_scope)} analyses missing scope definition")
        
        # Check for missing review schedules
        analyses_without_review = [a for a in swot_analyses + pestel_analyses if not a.next_review_date]
        if analyses_without_review:
            gaps.append(f"{len(analyses_without_review)} analyses missing review schedules")
        
        return gaps
    
    def _get_clause_4_1_recommendations(self, compliance_rate: float) -> List[str]:
        """Get recommendations based on compliance rate"""
        recommendations = []
        
        if compliance_rate < 50:
            recommendations.extend([
                "Immediate action required: Conduct comprehensive organizational context analysis",
                "Document organizational purpose and strategic direction",
                "Identify and document all relevant interested parties",
                "Assess internal and external issues affecting the organization"
            ])
        elif compliance_rate < 80:
            recommendations.extend([
                "Enhance existing analyses with complete strategic context",
                "Ensure all analyses include interested parties assessment",
                "Establish regular review schedules for context monitoring"
            ])
        else:
            recommendations.extend([
                "Maintain current high compliance level",
                "Ensure continuous monitoring of context changes",
                "Regular updates to interested parties requirements"
            ])
        
        recommendations.extend([
            "Link SWOT/PESTEL findings to risk management processes",
            "Integrate context understanding into strategic planning",
            "Document evidence sources for all context factors"
        ])
        
        return recommendations
    
    def generate_management_review_input(self, 
                                       start_date: datetime, 
                                       end_date: datetime) -> ManagementReviewInput:
        """Generate management review input from SWOT/PESTEL analyses"""
        # Get analyses within the review period
        swot_analyses = self.db.query(SWOTAnalysis).filter(
            and_(SWOTAnalysis.analysis_date >= start_date, SWOTAnalysis.analysis_date <= end_date)
        ).all()
        
        pestel_analyses = self.db.query(PESTELAnalysis).filter(
            and_(PESTELAnalysis.analysis_date >= start_date, PESTELAnalysis.analysis_date <= end_date)
        ).all()
        
        # Calculate analytics
        swot_analytics = self._calculate_swot_period_analytics(swot_analyses)
        pestel_analytics = self._calculate_pestel_period_analytics(pestel_analyses)
        iso_compliance = self._calculate_period_compliance_metrics(swot_analyses, pestel_analyses)
        
        # Extract strategic insights
        strategic_insights = self._extract_period_insights(swot_analyses, pestel_analyses)
        
        # Identify improvement opportunities
        improvement_opportunities = self._identify_improvement_opportunities(swot_analyses, pestel_analyses)
        
        # Assess resource requirements
        resource_requirements = self._assess_resource_requirements(swot_analyses, pestel_analyses)
        
        # Generate management recommendations
        management_recommendations = self._generate_management_recommendations(
            iso_compliance, strategic_insights, improvement_opportunities
        )
        
        return ManagementReviewInput(
            review_period_start=start_date,
            review_period_end=end_date,
            swot_summary=swot_analytics,
            pestel_summary=pestel_analytics,
            iso_compliance=iso_compliance,
            strategic_insights=strategic_insights,
            improvement_opportunities=improvement_opportunities,
            resource_requirements=resource_requirements,
            management_recommendations=management_recommendations
        )
    
    def _calculate_swot_period_analytics(self, analyses: List[SWOTAnalysis]) -> Dict[str, Any]:
        """Calculate SWOT analytics for a specific period"""
        if not analyses:
            return {
                "total_analyses": 0,
                "active_analyses": 0,
                "total_items": 0,
                "strengths_count": 0,
                "weaknesses_count": 0,
                "opportunities_count": 0,
                "threats_count": 0,
                "actions_generated": 0,
                "completed_actions": 0,
                "completion_rate": 0
            }
        
        analysis_ids = [a.id for a in analyses]
        
        # Count items by category
        items = self.db.query(SWOTItem).filter(SWOTItem.analysis_id.in_(analysis_ids)).all()
        strengths = [i for i in items if i.category == "strengths"]
        weaknesses = [i for i in items if i.category == "weaknesses"]
        opportunities = [i for i in items if i.category == "opportunities"]
        threats = [i for i in items if i.category == "threats"]
        
        # Count actions
        actions_generated = self.db.query(func.count(SWOTAction.id)).filter(
            SWOTAction.analysis_id.in_(analysis_ids)
        ).scalar() or 0
        
        completed_actions = self.db.query(func.count(ActionLog.id)).join(
            SWOTAction, ActionLog.id == SWOTAction.action_log_id
        ).filter(
            and_(
                SWOTAction.analysis_id.in_(analysis_ids),
                ActionLog.status == ActionStatus.COMPLETED
            )
        ).scalar() or 0
        
        completion_rate = (completed_actions / actions_generated * 100) if actions_generated > 0 else 0
        
        return {
            "total_analyses": len(analyses),
            "active_analyses": sum(1 for a in analyses if a.is_active),
            "total_items": len(items),
            "strengths_count": len(strengths),
            "weaknesses_count": len(weaknesses),
            "opportunities_count": len(opportunities),
            "threats_count": len(threats),
            "actions_generated": actions_generated,
            "completed_actions": completed_actions,
            "completion_rate": completion_rate
        }
    
    def _calculate_pestel_period_analytics(self, analyses: List[PESTELAnalysis]) -> Dict[str, Any]:
        """Calculate PESTEL analytics for a specific period"""
        if not analyses:
            return {
                "total_analyses": 0,
                "active_analyses": 0,
                "total_items": 0,
                "political_count": 0,
                "economic_count": 0,
                "social_count": 0,
                "technological_count": 0,
                "environmental_count": 0,
                "legal_count": 0,
                "actions_generated": 0,
                "completed_actions": 0,
                "completion_rate": 0
            }
        
        analysis_ids = [a.id for a in analyses]
        
        # Count items by category
        items = self.db.query(PESTELItem).filter(PESTELItem.analysis_id.in_(analysis_ids)).all()
        political = [i for i in items if i.category == "political"]
        economic = [i for i in items if i.category == "economic"]
        social = [i for i in items if i.category == "social"]
        technological = [i for i in items if i.category == "technological"]
        environmental = [i for i in items if i.category == "environmental"]
        legal = [i for i in items if i.category == "legal"]
        
        # Count actions
        actions_generated = self.db.query(func.count(PESTELAction.id)).filter(
            PESTELAction.analysis_id.in_(analysis_ids)
        ).scalar() or 0
        
        completed_actions = self.db.query(func.count(ActionLog.id)).join(
            PESTELAction, ActionLog.id == PESTELAction.action_log_id
        ).filter(
            and_(
                PESTELAction.analysis_id.in_(analysis_ids),
                ActionLog.status == ActionStatus.COMPLETED
            )
        ).scalar() or 0
        
        completion_rate = (completed_actions / actions_generated * 100) if actions_generated > 0 else 0
        
        return {
            "total_analyses": len(analyses),
            "active_analyses": sum(1 for a in analyses if a.is_active),
            "total_items": len(items),
            "political_count": len(political),
            "economic_count": len(economic),
            "social_count": len(social),
            "technological_count": len(technological),
            "environmental_count": len(environmental),
            "legal_count": len(legal),
            "actions_generated": actions_generated,
            "completed_actions": completed_actions,
            "completion_rate": completion_rate
        }
    
    def _calculate_period_compliance_metrics(self, 
                                           swot_analyses: List[SWOTAnalysis], 
                                           pestel_analyses: List[PESTELAnalysis]) -> ISOComplianceMetrics:
        """Calculate ISO compliance metrics for a specific period"""
        total_analyses = len(swot_analyses) + len(pestel_analyses)
        
        analyses_with_context = (
            sum(1 for a in swot_analyses if a.strategic_context) +
            sum(1 for a in pestel_analyses if a.strategic_context)
        )
        
        clause_4_1_compliance_rate = (analyses_with_context / total_analyses * 100) if total_analyses > 0 else 0
        
        # Count overdue reviews
        now = datetime.now()
        overdue_reviews = (
            sum(1 for a in swot_analyses if a.next_review_date and a.next_review_date < now) +
            sum(1 for a in pestel_analyses if a.next_review_date and a.next_review_date < now)
        )
        
        # Risk integration rate
        risk_integrated = (
            sum(1 for a in swot_analyses if a.risk_assessment_id) +
            sum(1 for a in pestel_analyses if a.risk_assessment_id)
        )
        risk_integration_rate = (risk_integrated / total_analyses * 100) if total_analyses > 0 else 0
        
        # Strategic alignment rate
        strategically_aligned = (
            sum(1 for a in swot_analyses if a.strategic_objectives_alignment) +
            sum(1 for a in pestel_analyses if a.strategic_objectives_alignment)
        )
        strategic_alignment_rate = (strategically_aligned / total_analyses * 100) if total_analyses > 0 else 0
        
        return ISOComplianceMetrics(
            total_analyses_with_context=analyses_with_context,
            clause_4_1_compliance_rate=clause_4_1_compliance_rate,
            overdue_reviews=overdue_reviews,
            risk_integration_rate=risk_integration_rate,
            strategic_alignment_rate=strategic_alignment_rate,
            documented_evidence_rate=85.0  # Would need to calculate based on actual evidence tracking
        )
    
    def _extract_period_insights(self, 
                                swot_analyses: List[SWOTAnalysis], 
                                pestel_analyses: List[PESTELAnalysis]) -> StrategicInsights:
        """Extract strategic insights from analyses in a specific period"""
        analysis_ids = [a.id for a in swot_analyses + pestel_analyses]
        
        if not analysis_ids:
            return StrategicInsights()
        
        # Get high-impact SWOT items
        swot_items = self.db.query(SWOTItem).filter(
            and_(
                SWOTItem.analysis_id.in_([a.id for a in swot_analyses]),
                SWOTItem.impact_level.in_(["high", "very_high"])
            )
        ).all()
        
        # Get high-impact PESTEL items
        pestel_items = self.db.query(PESTELItem).filter(
            and_(
                PESTELItem.analysis_id.in_([a.id for a in pestel_analyses]),
                PESTELItem.impact_level.in_(["high", "very_high"])
            )
        ).all()
        
        # Extract insights by category
        critical_strengths = [item.description for item in swot_items if item.category == "strengths"][:5]
        major_weaknesses = [item.description for item in swot_items if item.category == "weaknesses"][:5]
        high_impact_opportunities = [item.description for item in swot_items if item.category == "opportunities"][:5]
        significant_threats = [item.description for item in swot_items if item.category == "threats"][:5]
        
        key_external_factors = [item.description for item in pestel_items][:10]
        regulatory_gaps = [item.compliance_implications for item in pestel_items 
                          if item.category == "legal" and item.compliance_implications][:5]
        
        return StrategicInsights(
            critical_strengths=critical_strengths,
            major_weaknesses=major_weaknesses,
            high_impact_opportunities=high_impact_opportunities,
            significant_threats=significant_threats,
            key_external_factors=key_external_factors,
            regulatory_compliance_gaps=regulatory_gaps
        )
    
    def _identify_improvement_opportunities(self, 
                                          swot_analyses: List[SWOTAnalysis], 
                                          pestel_analyses: List[PESTELAnalysis]) -> List[str]:
        """Identify improvement opportunities from analyses"""
        opportunities = []
        
        # Check for strategic context gaps
        missing_context = [a for a in swot_analyses + pestel_analyses if not a.strategic_context]
        if missing_context:
            opportunities.append(f"Enhance strategic context documentation for {len(missing_context)} analyses")
        
        # Check for risk integration opportunities
        missing_risk_integration = [a for a in swot_analyses + pestel_analyses if not a.risk_assessment_id]
        if missing_risk_integration:
            opportunities.append(f"Integrate {len(missing_risk_integration)} analyses with risk management")
        
        # Check for action generation opportunities
        analyses_without_actions = []
        for analysis in swot_analyses:
            action_count = self.db.query(func.count(SWOTAction.id)).filter(
                SWOTAction.analysis_id == analysis.id
            ).scalar() or 0
            if action_count == 0:
                analyses_without_actions.append(analysis)
        
        for analysis in pestel_analyses:
            action_count = self.db.query(func.count(PESTELAction.id)).filter(
                PESTELAction.analysis_id == analysis.id
            ).scalar() or 0
            if action_count == 0:
                analyses_without_actions.append(analysis)
        
        if analyses_without_actions:
            opportunities.append(f"Generate actionable items from {len(analyses_without_actions)} analyses")
        
        opportunities.extend([
            "Establish systematic review processes for context monitoring",
            "Enhance stakeholder engagement in context analysis",
            "Improve integration with strategic planning processes",
            "Develop automated monitoring of external factors"
        ])
        
        return opportunities
    
    def _assess_resource_requirements(self, 
                                    swot_analyses: List[SWOTAnalysis], 
                                    pestel_analyses: List[PESTELAnalysis]) -> List[str]:
        """Assess resource requirements for improvement"""
        requirements = []
        
        total_actions = 0
        for analysis in swot_analyses:
            total_actions += self.db.query(func.count(SWOTAction.id)).filter(
                SWOTAction.analysis_id == analysis.id
            ).scalar() or 0
        
        for analysis in pestel_analyses:
            total_actions += self.db.query(func.count(PESTELAction.id)).filter(
                PESTELAction.analysis_id == analysis.id
            ).scalar() or 0
        
        if total_actions > 50:
            requirements.append("Additional project management resources for action tracking")
        
        if len(swot_analyses + pestel_analyses) > 10:
            requirements.append("Dedicated analyst for strategic context monitoring")
        
        requirements.extend([
            "Training on ISO 9001:2015 context requirements",
            "Software tools for systematic context analysis",
            "Regular stakeholder engagement sessions",
            "External expertise for regulatory landscape monitoring"
        ])
        
        return requirements
    
    def _generate_management_recommendations(self, 
                                           compliance_metrics: ISOComplianceMetrics,
                                           strategic_insights: StrategicInsights,
                                           improvement_opportunities: List[str]) -> List[str]:
        """Generate recommendations for management"""
        recommendations = []
        
        # Compliance-based recommendations
        if compliance_metrics.clause_4_1_compliance_rate < 80:
            recommendations.append("Priority: Improve ISO 9001:2015 Clause 4.1 compliance")
        
        if compliance_metrics.overdue_reviews > 0:
            recommendations.append("Immediate: Address overdue context reviews")
        
        if compliance_metrics.risk_integration_rate < 70:
            recommendations.append("Enhance integration with risk management processes")
        
        # Strategic recommendations
        if strategic_insights.major_weaknesses:
            recommendations.append("Develop action plans to address major organizational weaknesses")
        
        if strategic_insights.significant_threats:
            recommendations.append("Implement threat mitigation strategies")
        
        if strategic_insights.high_impact_opportunities:
            recommendations.append("Capitalize on identified high-impact opportunities")
        
        # Process improvement recommendations
        recommendations.extend([
            "Establish quarterly context review meetings",
            "Implement systematic stakeholder feedback collection",
            "Develop context change monitoring dashboard",
            "Ensure adequate resources for strategic context management"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations