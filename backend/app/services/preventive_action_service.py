from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.nonconformance import (
    PreventiveAction, NonConformance, EffectivenessMonitoring
)
from app.schemas.nonconformance import (
    PreventiveActionCreate, PreventiveActionUpdate, PreventiveActionFilter,
    PreventiveActionEffectivenessRequest
)


class PreventiveActionService:
    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations
    def create_preventive_action(self, action_data: PreventiveActionCreate, created_by: int) -> PreventiveAction:
        """Create a new preventive action"""
        preventive_action = PreventiveAction(
            **action_data.dict(),
            created_by=created_by
        )
        self.db.add(preventive_action)
        self.db.commit()
        self.db.refresh(preventive_action)
        return preventive_action

    def get_preventive_actions(self, filter_params: PreventiveActionFilter) -> Dict[str, Any]:
        """Get preventive actions with filtering and pagination"""
        query = self.db.query(PreventiveAction)

        # Apply filters
        if filter_params.non_conformance_id:
            query = query.filter(PreventiveAction.non_conformance_id == filter_params.non_conformance_id)

        if filter_params.action_type:
            query = query.filter(PreventiveAction.action_type == filter_params.action_type)

        if filter_params.priority:
            query = query.filter(PreventiveAction.priority == filter_params.priority)

        if filter_params.status:
            query = query.filter(PreventiveAction.status == filter_params.status)

        if filter_params.assigned_to:
            query = query.filter(PreventiveAction.assigned_to == filter_params.assigned_to)

        if filter_params.due_date_from:
            query = query.filter(PreventiveAction.due_date >= filter_params.due_date_from)

        if filter_params.due_date_to:
            query = query.filter(PreventiveAction.due_date <= filter_params.due_date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        preventive_actions = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": preventive_actions,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_preventive_action(self, action_id: int) -> Optional[PreventiveAction]:
        """Get preventive action by ID"""
        return self.db.query(PreventiveAction).filter(PreventiveAction.id == action_id).first()

    def get_preventive_actions_by_nc(self, nc_id: int) -> List[PreventiveAction]:
        """Get all preventive actions for a specific non-conformance"""
        return self.db.query(PreventiveAction).filter(
            PreventiveAction.non_conformance_id == nc_id
        ).order_by(PreventiveAction.due_date.asc()).all()

    def update_preventive_action(self, action_id: int, action_data: PreventiveActionUpdate, updated_by: int) -> Optional[PreventiveAction]:
        """Update preventive action"""
        preventive_action = self.get_preventive_action(action_id)
        if not preventive_action:
            return None

        update_data = action_data.dict(exclude_unset=True)
        update_data['updated_by'] = updated_by
        update_data['updated_at'] = datetime.now()

        # If status is being updated to completed, set completion date
        if 'status' in update_data and update_data['status'] == 'completed':
            update_data['completion_date'] = datetime.now()

        for field, value in update_data.items():
            setattr(preventive_action, field, value)

        self.db.commit()
        self.db.refresh(preventive_action)
        return preventive_action

    def delete_preventive_action(self, action_id: int) -> bool:
        """Delete preventive action"""
        preventive_action = self.get_preventive_action(action_id)
        if not preventive_action:
            return False

        self.db.delete(preventive_action)
        self.db.commit()
        return True

    # Business Logic Methods
    def get_overdue_actions(self) -> List[PreventiveAction]:
        """Get all overdue preventive actions"""
        return self.db.query(PreventiveAction).filter(
            and_(
                PreventiveAction.status.in_(['planned', 'in_progress']),
                PreventiveAction.due_date < datetime.now()
            )
        ).order_by(PreventiveAction.due_date.asc()).all()

    def get_actions_by_priority(self, priority: str, nc_id: Optional[int] = None) -> List[PreventiveAction]:
        """Get preventive actions by priority"""
        query = self.db.query(PreventiveAction).filter(PreventiveAction.priority == priority)
        
        if nc_id:
            query = query.filter(PreventiveAction.non_conformance_id == nc_id)
        
        return query.order_by(PreventiveAction.due_date.asc()).all()

    def get_actions_by_status(self, status: str, nc_id: Optional[int] = None) -> List[PreventiveAction]:
        """Get preventive actions by status"""
        query = self.db.query(PreventiveAction).filter(PreventiveAction.status == status)
        
        if nc_id:
            query = query.filter(PreventiveAction.non_conformance_id == nc_id)
        
        return query.order_by(PreventiveAction.due_date.asc()).all()

    def get_actions_by_assignee(self, assigned_to: int) -> List[PreventiveAction]:
        """Get preventive actions assigned to a specific user"""
        return self.db.query(PreventiveAction).filter(
            PreventiveAction.assigned_to == assigned_to
        ).order_by(PreventiveAction.due_date.asc()).all()

    def get_actions_by_type(self, action_type: str, nc_id: Optional[int] = None) -> List[PreventiveAction]:
        """Get preventive actions by type"""
        query = self.db.query(PreventiveAction).filter(PreventiveAction.action_type == action_type)
        
        if nc_id:
            query = query.filter(PreventiveAction.non_conformance_id == nc_id)
        
        return query.order_by(PreventiveAction.due_date.asc()).all()

    def get_preventive_action_statistics(self, nc_id: Optional[int] = None) -> Dict[str, Any]:
        """Get preventive action statistics"""
        query = self.db.query(PreventiveAction)
        
        if nc_id:
            query = query.filter(PreventiveAction.non_conformance_id == nc_id)
        
        total_actions = query.count()
        
        # Status distribution
        statuses = ['planned', 'in_progress', 'completed', 'cancelled']
        actions_by_status = {}
        for status in statuses:
            count = query.filter(PreventiveAction.status == status).count()
            actions_by_status[status] = count
        
        # Priority distribution
        priorities = ['low', 'medium', 'high', 'critical']
        actions_by_priority = {}
        for priority in priorities:
            count = query.filter(PreventiveAction.priority == priority).count()
            actions_by_priority[priority] = count
        
        # Type distribution
        types = ['process_improvement', 'training', 'equipment_upgrade', 'procedure_update']
        actions_by_type = {}
        for action_type in types:
            count = query.filter(PreventiveAction.action_type == action_type).count()
            actions_by_type[action_type] = count
        
        # Completion rate
        completed_actions = actions_by_status.get('completed', 0)
        completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0
        
        # Overdue actions
        overdue_actions = query.filter(
            and_(
                PreventiveAction.status.in_(['planned', 'in_progress']),
                PreventiveAction.due_date < datetime.now()
            )
        ).count()
        
        return {
            "total_actions": total_actions,
            "actions_by_status": actions_by_status,
            "actions_by_priority": actions_by_priority,
            "actions_by_type": actions_by_type,
            "completion_rate": round(completion_rate, 2),
            "overdue_actions": overdue_actions
        }

    def get_recent_actions(self, days: int = 30, nc_id: Optional[int] = None) -> List[PreventiveAction]:
        """Get recent preventive actions within specified days"""
        start_date = datetime.now() - timedelta(days=days)
        
        query = self.db.query(PreventiveAction).filter(
            PreventiveAction.created_at >= start_date
        )
        
        if nc_id:
            query = query.filter(PreventiveAction.non_conformance_id == nc_id)
        
        return query.order_by(PreventiveAction.created_at.desc()).all()

    def get_upcoming_deadlines(self, days: int = 7) -> List[PreventiveAction]:
        """Get preventive actions with upcoming deadlines"""
        end_date = datetime.now() + timedelta(days=days)
        
        return self.db.query(PreventiveAction).filter(
            and_(
                PreventiveAction.status.in_(['planned', 'in_progress']),
                PreventiveAction.due_date <= end_date,
                PreventiveAction.due_date >= datetime.now()
            )
        ).order_by(PreventiveAction.due_date.asc()).all()

    def bulk_update_actions(self, action_ids: List[int], update_data: Dict[str, Any], updated_by: int) -> Dict[str, Any]:
        """Bulk update preventive actions"""
        actions = self.db.query(PreventiveAction).filter(PreventiveAction.id.in_(action_ids)).all()
        
        updated_count = 0
        for action in actions:
            for field, value in update_data.items():
                if hasattr(action, field):
                    setattr(action, field, value)
            action.updated_by = updated_by
            action.updated_at = datetime.now()
            
            # If status is being updated to completed, set completion date
            if 'status' in update_data and update_data['status'] == 'completed':
                action.completion_date = datetime.now()
            
            updated_count += 1
        
        self.db.commit()
        
        return {
            "total_requested": len(action_ids),
            "updated_count": updated_count
        }

    # Effectiveness Monitoring
    def update_effectiveness(self, action_id: int, effectiveness_data: PreventiveActionEffectivenessRequest) -> Optional[PreventiveAction]:
        """Update the effectiveness measurement for a preventive action"""
        preventive_action = self.get_preventive_action(action_id)
        if not preventive_action:
            return None

        preventive_action.effectiveness_measured = effectiveness_data.effectiveness_measured
        preventive_action.updated_at = datetime.now()

        # Calculate effectiveness percentage
        if preventive_action.effectiveness_target:
            effectiveness_percentage = (effectiveness_data.effectiveness_measured / preventive_action.effectiveness_target) * 100
            preventive_action.effectiveness_measured = effectiveness_percentage

        self.db.commit()
        self.db.refresh(preventive_action)
        return preventive_action

    def get_effectiveness_statistics(self, nc_id: Optional[int] = None) -> Dict[str, Any]:
        """Get effectiveness statistics for preventive actions"""
        query = self.db.query(PreventiveAction).filter(
            and_(
                PreventiveAction.status == 'completed',
                PreventiveAction.effectiveness_measured.isnot(None)
            )
        )
        
        if nc_id:
            query = query.filter(PreventiveAction.non_conformance_id == nc_id)
        
        completed_actions = query.all()
        
        if not completed_actions:
            return {
                "total_completed": 0,
                "average_effectiveness": 0,
                "effectiveness_distribution": {},
                "target_achievement_rate": 0
            }
        
        # Calculate average effectiveness
        total_effectiveness = sum(action.effectiveness_measured for action in completed_actions)
        average_effectiveness = total_effectiveness / len(completed_actions)
        
        # Effectiveness distribution
        effectiveness_ranges = {
            "excellent": 0,  # 90-100%
            "good": 0,       # 80-89%
            "satisfactory": 0,  # 70-79%
            "needs_improvement": 0  # <70%
        }
        
        target_achieved = 0
        for action in completed_actions:
            effectiveness = action.effectiveness_measured
            if effectiveness >= 90:
                effectiveness_ranges["excellent"] += 1
            elif effectiveness >= 80:
                effectiveness_ranges["good"] += 1
            elif effectiveness >= 70:
                effectiveness_ranges["satisfactory"] += 1
            else:
                effectiveness_ranges["needs_improvement"] += 1
            
            # Check if target was achieved
            if action.effectiveness_target and effectiveness >= action.effectiveness_target:
                target_achieved += 1
        
        target_achievement_rate = (target_achieved / len(completed_actions)) * 100
        
        return {
            "total_completed": len(completed_actions),
            "average_effectiveness": round(average_effectiveness, 2),
            "effectiveness_distribution": effectiveness_ranges,
            "target_achievement_rate": round(target_achievement_rate, 2)
        }

    # Trend Analysis
    def get_effectiveness_trends(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get effectiveness trends over time"""
        start_date = datetime.now() - timedelta(days=days)
        
        actions = self.db.query(PreventiveAction).filter(
            and_(
                PreventiveAction.status == 'completed',
                PreventiveAction.effectiveness_measured.isnot(None),
                PreventiveAction.completion_date >= start_date
            )
        ).order_by(PreventiveAction.completion_date.asc()).all()
        
        trends = []
        for action in actions:
            trends.append({
                "date": action.completion_date.date(),
                "effectiveness": action.effectiveness_measured,
                "target": action.effectiveness_target,
                "action_type": action.action_type,
                "priority": action.priority,
                "nc_id": action.non_conformance_id
            })
        
        return trends

    def get_action_performance_by_type(self) -> Dict[str, Any]:
        """Get performance statistics by action type"""
        action_types = ['process_improvement', 'training', 'equipment_upgrade', 'procedure_update']
        
        performance_by_type = {}
        for action_type in action_types:
            actions = self.db.query(PreventiveAction).filter(
                and_(
                    PreventiveAction.action_type == action_type,
                    PreventiveAction.status == 'completed',
                    PreventiveAction.effectiveness_measured.isnot(None)
                )
            ).all()
            
            if actions:
                avg_effectiveness = sum(a.effectiveness_measured for a in actions) / len(actions)
                completion_rate = len(actions) / self.db.query(PreventiveAction).filter(
                    PreventiveAction.action_type == action_type
                ).count() * 100
                
                performance_by_type[action_type] = {
                    "total_completed": len(actions),
                    "average_effectiveness": round(avg_effectiveness, 2),
                    "completion_rate": round(completion_rate, 2)
                }
            else:
                performance_by_type[action_type] = {
                    "total_completed": 0,
                    "average_effectiveness": 0,
                    "completion_rate": 0
                }
        
        return performance_by_type

    def validate_preventive_action(self, action_data: PreventiveActionCreate) -> Dict[str, Any]:
        """Validate preventive action data and provide recommendations"""
        recommendations = []
        warnings = []
        
        # Check due date
        if action_data.due_date <= datetime.now():
            warnings.append("Due date should be in the future")
        
        # Check effectiveness target
        if action_data.effectiveness_target and (action_data.effectiveness_target < 0 or action_data.effectiveness_target > 100):
            warnings.append("Effectiveness target should be between 0 and 100")
        
        # Check priority vs due date
        if action_data.priority in ['high', 'critical'] and action_data.due_date > datetime.now() + timedelta(days=30):
            recommendations.append("Consider setting a shorter due date for high priority actions")
        
        # Check action type vs priority
        if action_data.action_type == 'training' and action_data.priority == 'critical':
            recommendations.append("Training actions are typically not critical priority")
        
        return {
            "is_valid": len(warnings) == 0,
            "recommendations": recommendations,
            "warnings": warnings
        }

    def get_action_timeline(self, nc_id: int) -> List[Dict[str, Any]]:
        """Get timeline of preventive actions for a non-conformance"""
        actions = self.get_preventive_actions_by_nc(nc_id)
        
        timeline = []
        for action in actions:
            timeline.append({
                "id": action.id,
                "action_title": action.action_title,
                "action_type": action.action_type,
                "priority": action.priority,
                "status": action.status,
                "assigned_to": action.assigned_to,
                "due_date": action.due_date,
                "completion_date": action.completion_date,
                "effectiveness_target": action.effectiveness_target,
                "effectiveness_measured": action.effectiveness_measured
            })
        
        return sorted(timeline, key=lambda x: x["due_date"], reverse=True)

