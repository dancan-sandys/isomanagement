from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from datetime import datetime
import uuid

from app.models.risk import (
    RiskRegisterItem, RiskAction, RiskItemType, RiskCategory,
    RiskStatus, RiskSeverity, RiskLikelihood, RiskDetectability,
)
from app.schemas.risk import RiskFilter, RiskItemCreate, RiskItemUpdate


class RiskService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_number(self) -> str:
        return f"RISK-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    def create_item(self, payload: RiskItemCreate, created_by: int) -> RiskRegisterItem:
        risk_score = payload.risk_score
        if risk_score is None:
            # S * L * D (detectability optional; default 1 when not provided)
            sev_map = {
                RiskSeverity.LOW: 1,
                RiskSeverity.MEDIUM: 2,
                RiskSeverity.HIGH: 3,
                RiskSeverity.CRITICAL: 4,
            }
            lik_map = {
                RiskLikelihood.RARE: 1,
                RiskLikelihood.UNLIKELY: 2,
                RiskLikelihood.POSSIBLE: 3,
                RiskLikelihood.LIKELY: 4,
                RiskLikelihood.ALMOST_CERTAIN: 5,
            }
            det_map = {
                None: 1,
                RiskDetectability.EASILY_DETECTABLE: 1,
                RiskDetectability.MODERATELY_DETECTABLE: 2,
                RiskDetectability.DIFFICULT: 3,
                RiskDetectability.VERY_DIFFICULT: 4,
                RiskDetectability.ALMOST_UNDETECTABLE: 5,
            }
            risk_score = sev_map[payload.severity] * lik_map[payload.likelihood] * det_map[payload.detectability]

        item = RiskRegisterItem(
            item_type=payload.item_type,
            risk_number=self._generate_number(),
            title=payload.title,
            description=payload.description,
            category=payload.category,
                classification=payload.classification,
            status=RiskStatus.OPEN,
            severity=payload.severity,
            likelihood=payload.likelihood,
                detectability=payload.detectability,
            impact_score=payload.impact_score,
            risk_score=risk_score,
            mitigation_plan=payload.mitigation_plan,
            residual_risk=payload.residual_risk,
            assigned_to=payload.assigned_to,
            due_date=payload.due_date,
            next_review_date=payload.next_review_date,
            references=payload.references,
            created_by=created_by,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id: int, payload: RiskItemUpdate) -> RiskRegisterItem:
        item = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == item_id).first()
        if not item:
            raise ValueError("Risk item not found")

        data = payload.model_dump(exclude_unset=True)
        # If severity/likelihood change but risk_score not provided, recompute
        severity = data.get("severity", item.severity)
        likelihood = data.get("likelihood", item.likelihood)
        detectability = data.get("detectability", item.detectability)
        if ("severity" in data or "likelihood" in data or "detectability" in data) and "risk_score" not in data:
            sev_map = {RiskSeverity.LOW: 1, RiskSeverity.MEDIUM: 2, RiskSeverity.HIGH: 3, RiskSeverity.CRITICAL: 4}
            lik_map = {RiskLikelihood.RARE: 1, RiskLikelihood.UNLIKELY: 2, RiskLikelihood.POSSIBLE: 3, RiskLikelihood.LIKELY: 4, RiskLikelihood.ALMOST_CERTAIN: 5}
            det_map = {None: 1, RiskDetectability.EASILY_DETECTABLE: 1, RiskDetectability.MODERATELY_DETECTABLE: 2, RiskDetectability.DIFFICULT: 3, RiskDetectability.VERY_DIFFICULT: 4, RiskDetectability.ALMOST_UNDETECTABLE: 5}
            data["risk_score"] = sev_map[severity] * lik_map[likelihood] * det_map[detectability]

        for k, v in data.items():
            setattr(item, k, v)
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        item = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == item_id).first()
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True

    def get_items(self, filters: RiskFilter, page: int = 1, size: int = 20) -> Tuple[List[RiskRegisterItem], int]:
        q = self.db.query(RiskRegisterItem)
        if filters.search:
            term = f"%{filters.search}%"
            q = q.filter(or_(RiskRegisterItem.title.ilike(term), RiskRegisterItem.description.ilike(term), RiskRegisterItem.risk_number.ilike(term)))
        if filters.item_type:
            q = q.filter(RiskRegisterItem.item_type == filters.item_type)
        if filters.category:
            q = q.filter(RiskRegisterItem.category == filters.category)
        if filters.status:
            q = q.filter(RiskRegisterItem.status == filters.status)
        if filters.severity:
            q = q.filter(RiskRegisterItem.severity == filters.severity)
        if filters.likelihood:
            q = q.filter(RiskRegisterItem.likelihood == filters.likelihood)
        if filters.classification:
            q = q.filter(RiskRegisterItem.classification == filters.classification)
        if filters.detectability:
            q = q.filter(RiskRegisterItem.detectability == filters.detectability)
        if filters.assigned_to:
            q = q.filter(RiskRegisterItem.assigned_to == filters.assigned_to)
        if filters.date_from:
            q = q.filter(RiskRegisterItem.created_at >= filters.date_from)
        if filters.date_to:
            q = q.filter(RiskRegisterItem.created_at <= filters.date_to)

        total = q.count()
        items = q.order_by(desc(RiskRegisterItem.created_at)).offset((page - 1) * size).limit(size).all()
        return items, total

    def get_stats(self) -> Dict[str, Any]:
        total = self.db.query(RiskRegisterItem).count()
        by_status = {k: v for k, v in self.db.query(RiskRegisterItem.status, func.count(RiskRegisterItem.id)).group_by(RiskRegisterItem.status).all()}
        by_category = {k: v for k, v in self.db.query(RiskRegisterItem.category, func.count(RiskRegisterItem.id)).group_by(RiskRegisterItem.category).all()}
        by_severity = {k: v for k, v in self.db.query(RiskRegisterItem.severity, func.count(RiskRegisterItem.id)).group_by(RiskRegisterItem.severity).all()}
        by_item_type = {k: v for k, v in self.db.query(RiskRegisterItem.item_type, func.count(RiskRegisterItem.id)).group_by(RiskRegisterItem.item_type).all()}
        # Convert enums to string keys
        normalize = lambda d: { (k.value if hasattr(k, 'value') else str(k)): v for k, v in d.items() }
        return {
            "total": total,
            "by_status": normalize(by_status),
            "by_category": normalize(by_category),
            "by_severity": normalize(by_severity),
            "by_item_type": normalize(by_item_type),
        }

    def add_action(self, item_id: int, title: str, description: str = None, assigned_to: int = None, due_date: datetime = None) -> RiskAction:
        item = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == item_id).first()
        if not item:
            raise ValueError("Risk item not found")
        action = RiskAction(
            item_id=item_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            due_date=due_date,
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def complete_action(self, action_id: int) -> RiskAction:
        action = self.db.query(RiskAction).filter(RiskAction.id == action_id).first()
        if not action:
            raise ValueError("Risk action not found")
        action.completed = True
        action.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(action)
        return action

    def list_actions(self, item_id: int) -> List[RiskAction]:
        item = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == item_id).first()
        if not item:
            raise ValueError("Risk item not found")
        return self.db.query(RiskAction).filter(RiskAction.item_id == item_id).order_by(desc(RiskAction.created_at)).all()

    def update_action(self, action_id: int, data: Dict[str, Any]) -> RiskAction:
        action = self.db.query(RiskAction).filter(RiskAction.id == action_id).first()
        if not action:
            raise ValueError("Risk action not found")
        for k, v in data.items():
            setattr(action, k, v)
        if data.get("completed"):
            action.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(action)
        return action

    def delete_action(self, action_id: int) -> bool:
        action = self.db.query(RiskAction).filter(RiskAction.id == action_id).first()
        if not action:
            return False
        self.db.delete(action)
        self.db.commit()
        return True


