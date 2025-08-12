from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ManagementReviewStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ManagementReview(Base):
    __tablename__ = "management_reviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=True)
    attendees = Column(Text, nullable=True)  # comma-separated or free text
    inputs = Column(Text, nullable=True)     # JSON string of inputs summary
    outputs = Column(Text, nullable=True)    # JSON string of decisions/actions summary
    status = Column(Enum(ManagementReviewStatus), nullable=False, default=ManagementReviewStatus.PLANNED)
    next_review_date = Column(DateTime(timezone=True), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agenda_items = relationship("ReviewAgendaItem", back_populates="review", cascade="all, delete-orphan")
    actions = relationship("ReviewAction", back_populates="review", cascade="all, delete-orphan")


class ReviewAgendaItem(Base):
    __tablename__ = "review_agenda_items"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("management_reviews.id"), nullable=False)
    topic = Column(String(200), nullable=False)
    discussion = Column(Text, nullable=True)
    decision = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=True)

    review = relationship("ManagementReview", back_populates="agenda_items")


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("management_reviews.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    review = relationship("ManagementReview", back_populates="actions")


