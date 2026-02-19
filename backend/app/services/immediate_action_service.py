from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.nonconformance import (
    ImmediateAction, NonConformance
)
from app.schemas.nonconformance import (
    ImmediateActionCreate, ImmediateActionUpdate, ImmediateActionFilter,
    ImmediateActionVerificationRequest
)


class ImmediateActionService:
    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations
    def create_immediate_action(self, action_data: ImmediateActionCreate, created_by: int) -> ImmediateAction:
        """Create a new immediate action"""
        immediate_action = ImmediateAction(
            **action_data.dict()
        )
        self.db.add(immediate_action)
        self.db.commit()
        self.db.refresh(immediate_action)
        return immediate_action

    def get_immediate_actions(self, filter_params: ImmediateActionFilter) -> Dict[str, Any]:
        """Get immediate actions with filtering and pagination"""
        query = self.db.query(ImmediateAction)

        # Apply filters
        if filter_params.non_conformance_id:
            query = query.filter(ImmediateAction.non_conformance_id == filter_params.non_conformance_id)

        if filter_params.action_type:
            query = query.filter(ImmediateAction.action_type == filter_params.action_type)

        if filter_params.implemented_by:
            query = query.filter(ImmediateAction.implemented_by == filter_params.implemented_by)

        if filter_params.effectiveness_verified is not None:
            query = query.filter(ImmediateAction.effectiveness_verified == filter_params.effectiveness_verified)

        if filter_params.date_from:
            query = query.filter(ImmediateAction.implemented_at >= filter_params.date_from)

        if filter_params.date_to:
            query = query.filter(ImmediateAction.implemented_at <= filter_params.date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        immediate_actions = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": immediate_actions,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_immediate_action(self, action_id: int) -> Optional[ImmediateAction]:
        """Get immediate action by ID"""
        return self.db.query(ImmediateAction).filter(ImmediateAction.id == action_id).first()

    def get_immediate_actions_by_nc(self, nc_id: int) -> List[ImmediateAction]:
        """Get all immediate actions for a specific non-conformance"""
        return self.db.query(ImmediateAction).filter(
            ImmediateAction.non_conformance_id == nc_id
        ).order_by(ImmediateAction.implemented_at.desc()).all()

    def update_immediate_action(self, action_id: int, action_data: ImmediateActionUpdate) -> Optional[ImmediateAction]:
        """Update immediate action"""
        immediate_action = self.get_immediate_action(action_id)
        if not immediate_action:
            return None

        update_data = action_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(immediate_action, field, value)

        self.db.commit()
        self.db.refresh(immediate_action)
        return immediate_action

    def delete_immediate_action(self, action_id: int) -> bool:
        """Delete immediate action"""
        immediate_action = self.get_immediate_action(action_id)
        if not immediate_action:
            return False

        self.db.delete(immediate_action)
        self.db.commit()
        return True

    # Business Logic Methods
    def verify_immediate_action(self, action_id: int, verification_data: ImmediateActionVerificationRequest) -> Optional[ImmediateAction]:
        """Verify the effectiveness of an immediate action"""
        immediate_action = self.get_immediate_action(action_id)
        if not immediate_action:
            return None

        # Use the model's verification method
        immediate_action.verify_effectiveness(
            verified_by=verification_data.verification_by,
            verification_date=verification_data.verification_date or datetime.now()
        )

        self.db.commit()
        self.db.refresh(immediate_action)
        return immediate_action

    def get_unverified_actions(self, nc_id: Optional[int] = None) -> List[ImmediateAction]:
        """Get all unverified immediate actions"""
        query = self.db.query(ImmediateAction).filter(
            ImmediateAction.effectiveness_verified == False
        )
        
        if nc_id:
            query = query.filter(ImmediateAction.non_conformance_id == nc_id)
        
        return query.order_by(ImmediateAction.implemented_at.desc()).all()

    def get_overdue_verifications(self, days_threshold: int = 7) -> List[ImmediateAction]:
        """Get immediate actions that are overdue for verification"""
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        return self.db.query(ImmediateAction).filter(
            and_(
                ImmediateAction.effectiveness_verified == False,
                ImmediateAction.implemented_at <= threshold_date
            )
        ).order_by(ImmediateAction.implemented_at.asc()).all()

    def get_actions_by_type(self, action_type: str, nc_id: Optional[int] = None) -> List[ImmediateAction]:
        """Get immediate actions by type"""
        query = self.db.query(ImmediateAction).filter(
            ImmediateAction.action_type == action_type
        )
        
        if nc_id:
            query = query.filter(ImmediateAction.non_conformance_id == nc_id)
        
        return query.order_by(ImmediateAction.implemented_at.desc()).all()

    def get_actions_by_implementer(self, implemented_by: int) -> List[ImmediateAction]:
        """Get immediate actions by the person who implemented them"""
        return self.db.query(ImmediateAction).filter(
            ImmediateAction.implemented_by == implemented_by
        ).order_by(ImmediateAction.implemented_at.desc()).all()

    def get_verification_statistics(self, nc_id: Optional[int] = None) -> Dict[str, Any]:
        """Get verification statistics for immediate actions"""
        query = self.db.query(ImmediateAction)
        
        if nc_id:
            query = query.filter(ImmediateAction.non_conformance_id == nc_id)
        
        total_actions = query.count()
        verified_actions = query.filter(ImmediateAction.effectiveness_verified == True).count()
        unverified_actions = total_actions - verified_actions
        
        # Calculate verification rate
        verification_rate = (verified_actions / total_actions * 100) if total_actions > 0 else 0
        
        # Get actions by type
        actions_by_type = {}
        for action_type in ['containment', 'isolation', 'emergency_response', 'notification']:
            count = query.filter(ImmediateAction.action_type == action_type).count()
            actions_by_type[action_type] = count
        
        return {
            "total_actions": total_actions,
            "verified_actions": verified_actions,
            "unverified_actions": unverified_actions,
            "verification_rate": round(verification_rate, 2),
            "actions_by_type": actions_by_type
        }

    def get_recent_actions(self, days: int = 30, nc_id: Optional[int] = None) -> List[ImmediateAction]:
        """Get recent immediate actions within specified days"""
        start_date = datetime.now() - timedelta(days=days)
        
        query = self.db.query(ImmediateAction).filter(
            ImmediateAction.implemented_at >= start_date
        )
        
        if nc_id:
            query = query.filter(ImmediateAction.non_conformance_id == nc_id)
        
        return query.order_by(ImmediateAction.implemented_at.desc()).all()

    def bulk_verify_actions(self, action_ids: List[int], verification_data: ImmediateActionVerificationRequest) -> Dict[str, Any]:
        """Bulk verify multiple immediate actions"""
        actions = self.db.query(ImmediateAction).filter(
            ImmediateAction.id.in_(action_ids)
        ).all()
        
        verified_count = 0
        for action in actions:
            if not action.effectiveness_verified:
                action.verify_effectiveness(
                    verified_by=verification_data.verification_by,
                    verification_date=verification_data.verification_date or datetime.now()
                )
                verified_count += 1
        
        self.db.commit()
        
        return {
            "total_requested": len(action_ids),
            "verified_count": verified_count,
            "already_verified": len(action_ids) - verified_count
        }

    def get_action_timeline(self, nc_id: int) -> List[Dict[str, Any]]:
        """Get timeline of immediate actions for a non-conformance"""
        actions = self.get_immediate_actions_by_nc(nc_id)
        
        timeline = []
        for action in actions:
            timeline.append({
                "id": action.id,
                "action_type": action.action_type,
                "description": action.description,
                "implemented_at": action.implemented_at,
                "implemented_by": action.implemented_by,
                "effectiveness_verified": action.effectiveness_verified,
                "verification_date": action.verification_date,
                "verification_by": action.verification_by
            })
        
        return sorted(timeline, key=lambda x: x["implemented_at"], reverse=True)

    def check_immediate_action_requirements(self, nc_id: int) -> Dict[str, Any]:
        """Check if immediate actions are required and their status"""
        non_conformance = self.db.query(NonConformance).filter(NonConformance.id == nc_id).first()
        if not non_conformance:
            return {"error": "Non-conformance not found"}
        
        actions = self.get_immediate_actions_by_nc(nc_id)
        
        # Determine if immediate actions are required based on severity
        requires_immediate_action = non_conformance.severity in ['high', 'critical']
        
        # Check if any immediate actions exist
        has_immediate_actions = len(actions) > 0
        
        # Check verification status
        verified_actions = [a for a in actions if a.effectiveness_verified]
        verification_status = "complete" if len(verified_actions) == len(actions) and len(actions) > 0 else "pending"
        
        return {
            "requires_immediate_action": requires_immediate_action,
            "has_immediate_actions": has_immediate_actions,
            "total_actions": len(actions),
            "verified_actions": len(verified_actions),
            "verification_status": verification_status,
            "actions": actions
        }

