# -*- coding: utf-8 -*-
"""
Actions Log Service
Phase 3: Business logic for action tracking and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.actions_log import (
    ActionLog, ActionProgress, ActionRelationship, InterestedParty, PartyExpectation, PartyAction,
    SWOTAnalysis, SWOTItem, SWOTAction, PESTELAnalysis, PESTELItem, PESTELAction,
    ActionStatus, ActionPriority, ActionSource
)
from app.models.user import User
from app.models.dashboard import Department
from app.schemas.actions_log import ActionsAnalytics


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
    
    def list_actions(
        self,
        status: Optional[ActionStatus] = None,
        priority: Optional[ActionPriority] = None,
        source: Optional[ActionSource] = None,
        assigned_to: Optional[int] = None,
        department_id: Optional[int] = None,
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
