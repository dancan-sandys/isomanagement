from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.actions import (
    ActionLogEntry, ActionSource, ActionStatus, ActionPriority,
    InterestedParty, SWOTIssue, SWOTType, PESTELIssue, PESTELType
)


class ActionsService:
    def __init__(self, db: Session):
        self.db = db

    # Core actions log
    def list_actions(self, filters: Optional[Dict[str, Any]] = None) -> List[ActionLogEntry]:
        q = self.db.query(ActionLogEntry)
        f = filters or {}
        if f.get("source"):
            q = q.filter(ActionLogEntry.source == ActionSource(f["source"]))
        if f.get("status"):
            q = q.filter(ActionLogEntry.status == ActionStatus(f["status"]))
        if f.get("priority"):
            q = q.filter(ActionLogEntry.priority == ActionPriority(f["priority"]))
        return q.order_by(ActionLogEntry.created_at.desc()).all()

    def update_action(self, action_id: int, updates: Dict[str, Any]) -> Optional[ActionLogEntry]:
        a = self.db.query(ActionLogEntry).filter(ActionLogEntry.id == action_id).first()
        if not a:
            return None
        for k, v in updates.items():
            if v is not None:
                if k == "status":
                    v = ActionStatus(v)
                if k == "priority":
                    v = ActionPriority(v)
                setattr(a, k, v)
        self.db.commit()
        self.db.refresh(a)
        return a

    def _create_action(self, title: str, description: str, source: ActionSource,
                        source_entity: str, source_entity_id: int,
                        owner_id: Optional[int], due_date: Optional[datetime]) -> ActionLogEntry:
        entry = ActionLogEntry(
            title=title,
            description=description,
            source=source,
            source_entity=source_entity,
            source_entity_id=source_entity_id,
            owner_id=owner_id,
            due_date=due_date,
            priority=ActionPriority.MEDIUM,
            status=ActionStatus.OPEN,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    # Interested parties
    def create_interested_party(self, data: Dict[str, Any]) -> InterestedParty:
        ip = InterestedParty(**data)
        self.db.add(ip)
        self.db.commit()
        self.db.refresh(ip)
        if ip.action_to_address:
            self._create_action(
                title=f"Interested Party: {ip.stakeholder_name}",
                description=ip.action_to_address,
                source=ActionSource.INTERESTED_PARTY,
                source_entity="interested_parties",
                source_entity_id=ip.id,
                owner_id=ip.owner_id,
                due_date=ip.due_date,
            )
        return ip

    # SWOT
    def create_swot_issue(self, data: Dict[str, Any]) -> SWOTIssue:
        data = data.copy()
        data["issue_type"] = SWOTType(data["issue_type"]) if isinstance(data.get("issue_type"), str) else data.get("issue_type")
        issue = SWOTIssue(**data)
        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)
        if issue.required_action:
            self._create_action(
                title=f"SWOT: {issue.issue_type.value}",
                description=issue.required_action,
                source=ActionSource.SWOT,
                source_entity="swot_issues",
                source_entity_id=issue.id,
                owner_id=issue.owner_id,
                due_date=issue.due_date,
            )
        return issue

    # PESTEL
    def create_pestel_issue(self, data: Dict[str, Any]) -> PESTELIssue:
        data = data.copy()
        data["issue_type"] = PESTELType(data["issue_type"]) if isinstance(data.get("issue_type"), str) else data.get("issue_type")
        issue = PESTELIssue(**data)
        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)
        if issue.required_action:
            self._create_action(
                title=f"PESTEL: {issue.issue_type.value}",
                description=issue.required_action,
                source=ActionSource.PESTEL,
                source_entity="pestel_issues",
                source_entity_id=issue.id,
                owner_id=issue.owner_id,
                due_date=issue.due_date,
            )
        return issue

