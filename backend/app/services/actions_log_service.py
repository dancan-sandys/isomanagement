# -*- coding: utf-8 -*-
"""
Actions Log Service
Phase 3: Business logic for action tracking and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from app.models.actions_log import (
    ActionLog, ActionProgress, ActionRelationship, InterestedParty, PartyExpectation, PartyAction,
    SWOTAnalysis, SWOTItem, SWOTAction, PESTELAnalysis, PESTELItem, PESTELAction,
    ActionStatus, ActionPriority, ActionSource
)
from app.models.user import User
from app.models.dashboard import Department
from app.schemas.actions_log import ActionsAnalytics
from app.schemas.swot_pestel import (
    SWOTAnalysisCreate, SWOTAnalysisUpdate, SWOTAnalysisResponse,
    SWOTItemCreate, SWOTItemUpdate, SWOTItemResponse,
    PESTELAnalysisCreate, PESTELAnalysisUpdate, PESTELAnalysisResponse,
    PESTELItemCreate, PESTELItemUpdate, PESTELItemResponse,
    SWOTAnalytics, PESTELAnalytics, ISOComplianceMetrics, 
    StrategicInsights, ContinuousImprovementMetrics, ISODashboardMetrics
)


class ActionsLogService:
    """Service class for actions log management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Action Log Management
    def create_action(self, action_data: Dict[str, Any]) -> ActionLog:
        """Create a new action log entry"""
        action = ActionLog(**action_data)
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action
    
    def get_action(self, action_id: int) -> Optional[ActionLog]:
        """Get action by ID"""
        return self.db.query(ActionLog).filter(ActionLog.id == action_id).first()
    
    def update_action(self, action_id: int, update_data: Dict[str, Any]) -> Optional[ActionLog]:
        """Update an action log entry"""
        action = self.get_action(action_id)
        if not action:
            return None
        
        for key, value in update_data.items():
            if hasattr(action, key):
                setattr(action, key, value)
        
        # Update timestamps based on status changes
        if 'status' in update_data:
            if update_data['status'] == ActionStatus.IN_PROGRESS and not action.started_at:
                action.started_at = datetime.now()
            elif update_data['status'] == ActionStatus.COMPLETED:
                action.completed_at = datetime.now()
                action.progress_percent = 100.0
        
        self.db.commit()
        self.db.refresh(action)
        return action

    def delete_action(self, action_id: int) -> bool:
        """Delete an action log entry"""
        action = self.get_action(action_id)
        if not action:
            return False
        self.db.delete(action)
        self.db.commit()
        return True
    
    def list_actions(
        self,
        status: Optional[ActionStatus] = None,
        priority: Optional[ActionPriority] = None,
        source: Optional[ActionSource] = None,
        assigned_to: Optional[int] = None,
        department_id: Optional[int] = None,
        risk_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActionLog]:
        """List actions with filtering"""
        query = self.db.query(ActionLog)
        
        if status:
            query = query.filter(ActionLog.status == status)
        if priority:
            query = query.filter(ActionLog.priority == priority)
        if source:
            query = query.filter(ActionLog.action_source == source)
        if assigned_to:
            query = query.filter(ActionLog.assigned_to == assigned_to)
        if department_id:
            query = query.filter(ActionLog.department_id == department_id)
        if risk_id:
            # Direct linkage via risk_id or tagged via tags.risk_item_id
            query = query.filter(
                or_(
                    ActionLog.risk_id == risk_id,
                    # For SQLite/JSON, a simple LIKE fallback if JSON querying is unavailable
                    ActionLog.tags.like(f'%"risk_item_id": {risk_id}%')
                )
            )
        
        return query.order_by(desc(ActionLog.created_at)).offset(offset).limit(limit).all()
    
    # Analytics
    def get_analytics(self) -> ActionsAnalytics:
        """Get comprehensive actions analytics"""
        total_actions = self.db.query(func.count(ActionLog.id)).scalar()
        
        # Status breakdown
        status_counts = self.db.query(
            ActionLog.status,
            func.count(ActionLog.id)
        ).group_by(ActionLog.status).all()
        
        status_breakdown = {status: count for status, count in status_counts}
        
        # Priority breakdown
        priority_counts = self.db.query(
            ActionLog.priority,
            func.count(ActionLog.id)
        ).group_by(ActionLog.priority).all()
        
        priority_breakdown = {priority: count for priority, count in priority_counts}
        
        # Source breakdown
        source_counts = self.db.query(
            ActionLog.action_source,
            func.count(ActionLog.id)
        ).group_by(ActionLog.action_source).all()
        
        source_breakdown = {source: count for source, count in source_counts}
        
        # Calculate completion rate
        completed = status_breakdown.get(ActionStatus.COMPLETED, 0)
        completion_rate = (completed / total_actions * 100) if total_actions > 0 else 0
        
        return ActionsAnalytics(
            total_actions=total_actions,
            pending_actions=status_breakdown.get(ActionStatus.PENDING, 0),
            in_progress_actions=status_breakdown.get(ActionStatus.IN_PROGRESS, 0),
            completed_actions=completed,
            overdue_actions=status_breakdown.get(ActionStatus.OVERDUE, 0),
            critical_actions=priority_breakdown.get(ActionPriority.CRITICAL, 0),
            high_priority_actions=priority_breakdown.get(ActionPriority.HIGH, 0),
            average_completion_time=None,
            completion_rate=completion_rate,
            source_breakdown=source_breakdown,
            priority_breakdown=priority_breakdown,
            status_breakdown=status_breakdown,
            department_breakdown={}
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for actions"""
        # Recent actions (last 10)
        recent_actions = self.db.query(ActionLog).order_by(
            desc(ActionLog.created_at)
        ).limit(10).all()
        
        # Critical actions
        critical_actions = self.db.query(ActionLog).filter(
            ActionLog.priority == ActionPriority.CRITICAL
        ).order_by(desc(ActionLog.created_at)).limit(10).all()
        
        analytics = self.get_analytics()
        
        return {
            "recent_actions": recent_actions,
            "critical_actions": critical_actions,
            "analytics": analytics
        }
    
    # SWOT Analysis Management
    def create_swot_analysis(self, analysis_data: Union[SWOTAnalysisCreate, dict]) -> SWOTAnalysis:
        """Create a new SWOT analysis with ISO compliance features"""
        # Convert Pydantic model to dict for SQLAlchemy if needed
        if hasattr(analysis_data, 'dict'):
            analysis_dict = analysis_data.dict()
        else:
            analysis_dict = analysis_data
        
        # Filter out fields that don't exist in the SWOTAnalysis model
        valid_fields = {
            'title', 'description', 'analysis_date', 'next_review_date',
            'scope', 'context', 'status', 'is_current', 'created_by'
        }
        
        filtered_dict = {k: v for k, v in analysis_dict.items() if k in valid_fields}
        
        analysis = SWOTAnalysis(**filtered_dict)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_swot_analysis(self, analysis_id: int) -> Optional[SWOTAnalysis]:
        """Get SWOT analysis by ID"""
        return self.db.query(SWOTAnalysis).filter(SWOTAnalysis.id == analysis_id).first()
    
    def get_swot_analyses(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        scope: Optional[str] = None
    ) -> List[SWOTAnalysis]:
        """Get SWOT analyses with filtering"""
        query = self.db.query(SWOTAnalysis)
        
        if is_active is not None:
            query = query.filter(SWOTAnalysis.status == "active" if is_active else SWOTAnalysis.status != "active")
        if scope:
            query = query.filter(SWOTAnalysis.scope == scope)
            
        return query.order_by(desc(SWOTAnalysis.created_at)).offset(skip).limit(limit).all()
    
    def update_swot_analysis(self, analysis_id: int, update_data: SWOTAnalysisUpdate) -> Optional[SWOTAnalysis]:
        """Update SWOT analysis"""
        analysis = self.get_swot_analysis(analysis_id)
        if not analysis:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(analysis, key):
                setattr(analysis, key, value)
        
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def delete_swot_analysis(self, analysis_id: int) -> bool:
        """Delete SWOT analysis"""
        analysis = self.get_swot_analysis(analysis_id)
        if not analysis:
            return False
        
        self.db.delete(analysis)
        self.db.commit()
        return True
    
    # SWOT Items Management
    def create_swot_item(self, analysis_id: int, item_data: SWOTItemCreate) -> SWOTItem:
        """Create a new SWOT item"""
        item_dict = item_data.dict()
        item_dict['analysis_id'] = analysis_id
        
        item = SWOTItem(**item_dict)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_swot_items(self, analysis_id: int, category: Optional[str] = None) -> List[SWOTItem]:
        """Get SWOT items for an analysis"""
        query = self.db.query(SWOTItem).filter(SWOTItem.analysis_id == analysis_id)
        
        if category:
            query = query.filter(SWOTItem.category == category)
            
        return query.order_by(SWOTItem.created_at).all()
    
    def update_swot_item(self, item_id: int, update_data: SWOTItemUpdate) -> Optional[SWOTItem]:
        """Update SWOT item"""
        item = self.db.query(SWOTItem).filter(SWOTItem.id == item_id).first()
        if not item:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete_swot_item(self, item_id: int) -> bool:
        """Delete SWOT item"""
        item = self.db.query(SWOTItem).filter(SWOTItem.id == item_id).first()
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    # PESTEL Analysis Management
    def create_pestel_analysis(self, analysis_data: Union[PESTELAnalysisCreate, dict]) -> PESTELAnalysis:
        """Create a new PESTEL analysis with ISO compliance features"""
        # Convert Pydantic model to dict for SQLAlchemy if needed
        if hasattr(analysis_data, 'dict'):
            analysis_dict = analysis_data.dict()
        else:
            analysis_dict = analysis_data
        
        # Filter out fields that don't exist in the PESTELAnalysis model
        valid_fields = {
            'title', 'description', 'analysis_date', 'next_review_date',
            'scope', 'context', 'status', 'is_current', 'created_by'
        }
        
        filtered_dict = {k: v for k, v in analysis_dict.items() if k in valid_fields}
        
        analysis = PESTELAnalysis(**filtered_dict)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_pestel_analysis(self, analysis_id: int) -> Optional[PESTELAnalysis]:
        """Get PESTEL analysis by ID"""
        return self.db.query(PESTELAnalysis).filter(PESTELAnalysis.id == analysis_id).first()
    
    def get_pestel_analyses(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        scope: Optional[str] = None
    ) -> List[PESTELAnalysis]:
        """Get PESTEL analyses with filtering"""
        query = self.db.query(PESTELAnalysis)
        
        if is_active is not None:
            query = query.filter(PESTELAnalysis.status == "active" if is_active else PESTELAnalysis.status != "active")
        if scope:
            query = query.filter(PESTELAnalysis.scope == scope)
            
        return query.order_by(desc(PESTELAnalysis.created_at)).offset(skip).limit(limit).all()
    
    def update_pestel_analysis(self, analysis_id: int, update_data: PESTELAnalysisUpdate) -> Optional[PESTELAnalysis]:
        """Update PESTEL analysis"""
        analysis = self.get_pestel_analysis(analysis_id)
        if not analysis:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(analysis, key):
                setattr(analysis, key, value)
        
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def delete_pestel_analysis(self, analysis_id: int) -> bool:
        """Delete PESTEL analysis"""
        analysis = self.get_pestel_analysis(analysis_id)
        if not analysis:
            return False
        
        self.db.delete(analysis)
        self.db.commit()
        return True
    
    # PESTEL Items Management
    def create_pestel_item(self, analysis_id: int, item_data: PESTELItemCreate) -> PESTELItem:
        """Create a new PESTEL item"""
        item_dict = item_data.dict()
        item_dict['analysis_id'] = analysis_id
        
        item = PESTELItem(**item_dict)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_pestel_items(self, analysis_id: int, category: Optional[str] = None) -> List[PESTELItem]:
        """Get PESTEL items for an analysis"""
        query = self.db.query(PESTELItem).filter(PESTELItem.analysis_id == analysis_id)
        
        if category:
            query = query.filter(PESTELItem.category == category)
            
        return query.order_by(PESTELItem.created_at).all()
    
    def update_pestel_item(self, item_id: int, update_data: PESTELItemUpdate) -> Optional[PESTELItem]:
        """Update PESTEL item"""
        item = self.db.query(PESTELItem).filter(PESTELItem.id == item_id).first()
        if not item:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete_pestel_item(self, item_id: int) -> bool:
        """Delete PESTEL item"""
        item = self.db.query(PESTELItem).filter(PESTELItem.id == item_id).first()
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    # ISO-Specific Analytics Methods
    def get_swot_analytics(self) -> SWOTAnalytics:
        """Get comprehensive SWOT analytics with ISO compliance metrics"""
        total_analyses = self.db.query(func.count(SWOTAnalysis.id)).scalar() or 0
        active_analyses = self.db.query(func.count(SWOTAnalysis.id)).filter(
            SWOTAnalysis.status == "active"
        ).scalar() or 0
        
        # Count items by category
        strengths_count = self.db.query(func.count(SWOTItem.id)).filter(
            SWOTItem.category == "strengths"
        ).scalar() or 0
        
        weaknesses_count = self.db.query(func.count(SWOTItem.id)).filter(
            SWOTItem.category == "weaknesses"
        ).scalar() or 0
        
        opportunities_count = self.db.query(func.count(SWOTItem.id)).filter(
            SWOTItem.category == "opportunities"
        ).scalar() or 0
        
        threats_count = self.db.query(func.count(SWOTItem.id)).filter(
            SWOTItem.category == "threats"
        ).scalar() or 0
        
        total_items = strengths_count + weaknesses_count + opportunities_count + threats_count
        
        # Count actions generated from SWOT analyses
        actions_generated = self.db.query(func.count(SWOTAction.id)).scalar() or 0
        
        # Count completed actions
        completed_actions = self.db.query(func.count(ActionLog.id)).join(
            SWOTAction, ActionLog.id == SWOTAction.action_log_id
        ).filter(ActionLog.status == ActionStatus.COMPLETED).scalar() or 0
        
        completion_rate = (completed_actions / actions_generated * 100) if actions_generated > 0 else 0
        
        return SWOTAnalytics(
            total_analyses=total_analyses,
            active_analyses=active_analyses,
            total_items=total_items,
            strengths_count=strengths_count,
            weaknesses_count=weaknesses_count,
            opportunities_count=opportunities_count,
            threats_count=threats_count,
            actions_generated=actions_generated,
            completed_actions=completed_actions,
            completion_rate=completion_rate
        )
    
    def get_pestel_analytics(self) -> PESTELAnalytics:
        """Get comprehensive PESTEL analytics with ISO compliance metrics"""
        total_analyses = self.db.query(func.count(PESTELAnalysis.id)).scalar() or 0
        active_analyses = self.db.query(func.count(PESTELAnalysis.id)).filter(
            PESTELAnalysis.status == "active"
        ).scalar() or 0
        
        # Count items by category
        political_count = self.db.query(func.count(PESTELItem.id)).filter(
            PESTELItem.category == "political"
        ).scalar() or 0
        
        economic_count = self.db.query(func.count(PESTELItem.id)).filter(
            PESTELItem.category == "economic"
        ).scalar() or 0
        
        social_count = self.db.query(func.count(PESTELItem.id)).filter(
            PESTELItem.category == "social"
        ).scalar() or 0
        
        technological_count = self.db.query(func.count(PESTELItem.id)).filter(
            PESTELItem.category == "technological"
        ).scalar() or 0
        
        environmental_count = self.db.query(func.count(PESTELItem.id)).filter(
            PESTELItem.category == "environmental"
        ).scalar() or 0
        
        legal_count = self.db.query(func.count(PESTELItem.id)).filter(
            PESTELItem.category == "legal"
        ).scalar() or 0
        
        total_items = (political_count + economic_count + social_count + 
                      technological_count + environmental_count + legal_count)
        
        # Count actions generated from PESTEL analyses
        actions_generated = self.db.query(func.count(PESTELAction.id)).scalar() or 0
        
        # Count completed actions
        completed_actions = self.db.query(func.count(ActionLog.id)).join(
            PESTELAction, ActionLog.id == PESTELAction.action_log_id
        ).filter(ActionLog.status == ActionStatus.COMPLETED).scalar() or 0
        
        completion_rate = (completed_actions / actions_generated * 100) if actions_generated > 0 else 0
        
        return PESTELAnalytics(
            total_analyses=total_analyses,
            active_analyses=active_analyses,
            total_items=total_items,
            political_count=political_count,
            economic_count=economic_count,
            social_count=social_count,
            technological_count=technological_count,
            environmental_count=environmental_count,
            legal_count=legal_count,
            actions_generated=actions_generated,
            completed_actions=completed_actions,
            completion_rate=completion_rate
        )
    
    def get_iso_compliance_metrics(self) -> ISOComplianceMetrics:
        """Get ISO compliance metrics for SWOT/PESTEL analyses"""
        # Count analyses with context defined
        swot_with_context = self.db.query(func.count(SWOTAnalysis.id)).filter(
            and_(SWOTAnalysis.context.isnot(None), SWOTAnalysis.status == "active")
        ).scalar() or 0
        
        pestel_with_context = self.db.query(func.count(PESTELAnalysis.id)).filter(
            PESTELAnalysis.context.isnot(None)
        ).scalar() or 0
        
        total_analyses_with_context = swot_with_context + pestel_with_context
        
        # Total analyses
        total_swot = self.db.query(func.count(SWOTAnalysis.id)).scalar() or 0
        total_pestel = self.db.query(func.count(PESTELAnalysis.id)).scalar() or 0
        total_analyses = total_swot + total_pestel
        
        # Calculate compliance rate
        clause_4_1_compliance_rate = (total_analyses_with_context / total_analyses * 100) if total_analyses > 0 else 0
        
        # Count overdue reviews
        now = datetime.now()
        overdue_swot = self.db.query(func.count(SWOTAnalysis.id)).filter(
            and_(SWOTAnalysis.next_review_date.isnot(None), SWOTAnalysis.next_review_date < now)
        ).scalar() or 0
        
        overdue_pestel = self.db.query(func.count(PESTELAnalysis.id)).filter(
            and_(PESTELAnalysis.next_review_date.isnot(None), PESTELAnalysis.next_review_date < now)
        ).scalar() or 0
        
        overdue_reviews = overdue_swot + overdue_pestel
        
        # Risk integration rate - using available fields
        swot_with_risk = self.db.query(func.count(SWOTAnalysis.id)).filter(
            SWOTAnalysis.scope.isnot(None)
        ).scalar() or 0
        
        pestel_with_risk = self.db.query(func.count(PESTELAnalysis.id)).filter(
            PESTELAnalysis.scope.isnot(None)
        ).scalar() or 0
        
        risk_integration_rate = ((swot_with_risk + pestel_with_risk) / total_analyses * 100) if total_analyses > 0 else 0
        
        # Strategic alignment rate - using available fields
        swot_with_alignment = self.db.query(func.count(SWOTAnalysis.id)).filter(
            SWOTAnalysis.is_current == True
        ).scalar() or 0
        
        pestel_with_alignment = self.db.query(func.count(PESTELAnalysis.id)).filter(
            PESTELAnalysis.is_current == True
        ).scalar() or 0
        
        strategic_alignment_rate = ((swot_with_alignment + pestel_with_alignment) / total_analyses * 100) if total_analyses > 0 else 0
        
        # Basic documented evidence rate (simplified for now)
        documented_evidence_rate = 75.0  # Placeholder - would need actual evidence tracking
        
        return ISOComplianceMetrics(
            total_analyses_with_context=total_analyses_with_context,
            clause_4_1_compliance_rate=clause_4_1_compliance_rate,
            overdue_reviews=overdue_reviews,
            risk_integration_rate=risk_integration_rate,
            strategic_alignment_rate=strategic_alignment_rate,
            documented_evidence_rate=documented_evidence_rate
        )
    
    def get_iso_dashboard_metrics(self) -> ISODashboardMetrics:
        """Get comprehensive ISO dashboard metrics"""
        compliance_metrics = self.get_iso_compliance_metrics()
        
        # Strategic insights (simplified)
        strategic_insights = StrategicInsights(
            critical_strengths=["Strong quality management system", "Experienced team"],
            major_weaknesses=["Resource constraints", "Technology gaps"],
            high_impact_opportunities=["Market expansion", "Digital transformation"],
            significant_threats=["Regulatory changes", "Competition"],
            key_external_factors=["Economic uncertainty", "Technology evolution"],
            regulatory_compliance_gaps=["New regulations pending"]
        )
        
        # Improvement metrics
        total_actions = self.db.query(func.count(ActionLog.id)).filter(
            ActionLog.action_source.in_(["swot_analysis", "pestel_analysis"])
        ).scalar() or 0
        
        completed_actions = self.db.query(func.count(ActionLog.id)).filter(
            and_(
                ActionLog.action_source.in_(["swot_analysis", "pestel_analysis"]),
                ActionLog.status == ActionStatus.COMPLETED
            )
        ).scalar() or 0
        
        critical_pending = self.db.query(func.count(ActionLog.id)).filter(
            and_(
                ActionLog.action_source.in_(["swot_analysis", "pestel_analysis"]),
                ActionLog.priority == ActionPriority.CRITICAL,
                ActionLog.status.in_([ActionStatus.PENDING, ActionStatus.IN_PROGRESS])
            )
        ).scalar() or 0
        
        improvement_metrics = ContinuousImprovementMetrics(
            actions_from_analyses=total_actions,
            completed_improvement_actions=completed_actions,
            pending_critical_actions=critical_pending,
            average_action_completion_time=15.0,  # Placeholder
            stakeholder_satisfaction_improvement=5.2  # Placeholder
        )
        
        return ISODashboardMetrics(
            compliance_metrics=compliance_metrics,
            strategic_insights=strategic_insights,
            improvement_metrics=improvement_metrics
        )

    # Interested Parties Management
    def list_interested_parties(self) -> List[InterestedParty]:
        """List all interested parties"""
        return self.db.query(InterestedParty).filter(InterestedParty.is_active == True).all()
    
    def get_interested_party(self, party_id: int) -> Optional[InterestedParty]:
        """Get interested party by ID"""
        return self.db.query(InterestedParty).filter(InterestedParty.id == party_id).first()
    
    def create_interested_party(self, party_data: Dict[str, Any]) -> InterestedParty:
        """Create a new interested party"""
        party = InterestedParty(**party_data)
        self.db.add(party)
        self.db.commit()
        self.db.refresh(party)
        return party
    
    def update_interested_party(self, party_id: int, update_data: Dict[str, Any]) -> Optional[InterestedParty]:
        """Update an interested party"""
        party = self.get_interested_party(party_id)
        if not party:
            return None
        
        for key, value in update_data.items():
            if hasattr(party, key):
                setattr(party, key, value)
        
        self.db.commit()
        self.db.refresh(party)
        return party
        
    def get_party_actions(self, party_id: int) -> List[ActionLog]:
        """Get all actions related to a specific interested party"""
        # Get actions linked through PartyAction table
        party_action_ids = self.db.query(PartyAction.action_log_id).filter(
            PartyAction.party_id == party_id
        ).all()
        action_ids = [pa.action_log_id for pa in party_action_ids]
        
        # Build query to get actions from both sources
        query_conditions = []
        
        # Add linked actions if any exist
        if action_ids:
            query_conditions.append(ActionLog.id.in_(action_ids))
            
        # Add actions with source = interested_party and source_id = party_id
        query_conditions.append(
            and_(
                ActionLog.action_source == ActionSource.INTERESTED_PARTY,
                ActionLog.source_id == party_id
            )
        )
        
        if not query_conditions:
            return []
            
        actions = self.db.query(ActionLog).filter(
            or_(*query_conditions)
        ).order_by(desc(ActionLog.created_at)).all()
        
        return actions
