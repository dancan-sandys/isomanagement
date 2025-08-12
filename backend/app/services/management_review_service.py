from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime

from app.models.management_review import ManagementReview, ReviewAgendaItem, ReviewAction, ManagementReviewStatus
from app.schemas.management_review import ManagementReviewCreate, ManagementReviewUpdate


class ManagementReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: ManagementReviewCreate, created_by: int) -> ManagementReview:
        review = ManagementReview(
            title=payload.title,
            review_date=payload.review_date,
            attendees=payload.attendees,
            inputs=payload.inputs,
            status=payload.status or ManagementReviewStatus.PLANNED,
            next_review_date=payload.next_review_date,
            created_by=created_by,
        )
        self.db.add(review)
        self.db.flush()
        if payload.agenda:
            for idx, a in enumerate(payload.agenda):
                self.db.add(ReviewAgendaItem(
                    review_id=review.id,
                    topic=a.topic,
                    discussion=a.discussion,
                    decision=a.decision,
                    order_index=a.order_index if a.order_index is not None else idx + 1,
                ))
        self.db.commit()
        self.db.refresh(review)
        return review

    def list(self, page: int = 1, size: int = 20) -> Tuple[List[ManagementReview], int]:
        # SQLite does not support NULLS LAST; use COALESCE + created_at fallback
        q = self.db.query(ManagementReview).order_by(
            desc(func.coalesce(ManagementReview.review_date, ManagementReview.created_at)),
            desc(ManagementReview.created_at),
        )
        total = q.count()
        items = q.offset((page - 1) * size).limit(size).all()
        return items, total

    def get(self, review_id: int) -> ManagementReview:
        return self.db.query(ManagementReview).filter(ManagementReview.id == review_id).first()

    def update(self, review_id: int, payload: ManagementReviewUpdate) -> ManagementReview:
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(review, k, v)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review_id: int) -> bool:
        review = self.get(review_id)
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True

    # Actions
    def add_action(self, review_id: int, title: str, description: str = None, assigned_to: int = None, due_date: datetime = None) -> ReviewAction:
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        action = ReviewAction(review_id=review_id, title=title, description=description, assigned_to=assigned_to, due_date=due_date)
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def list_actions(self, review_id: int) -> List[ReviewAction]:
        return self.db.query(ReviewAction).filter(ReviewAction.review_id == review_id).order_by(desc(ReviewAction.created_at)).all()

    def complete_action(self, action_id: int) -> ReviewAction:
        action = self.db.query(ReviewAction).filter(ReviewAction.id == action_id).first()
        if not action:
            raise ValueError("Action not found")
        action.completed = True
        action.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(action)
        return action


