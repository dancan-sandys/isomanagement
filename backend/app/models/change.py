from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ChangeStatus(str, enum.Enum):
	DRAFT = "draft"
	ASSESSING = "assessing"
	APPROVED = "approved"
	REJECTED = "rejected"
	IMPLEMENTED = "implemented"
	VERIFIED = "verified"
	CLOSED = "closed"


class ApprovalDecision(str, enum.Enum):
	PENDING = "pending"
	APPROVED = "approved"
	REJECTED = "rejected"


class ChangeRequest(Base):
	__tablename__ = "change_requests"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(200), nullable=False)
	reason = Column(Text, nullable=False)
	initiator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=True)
	document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
	impact_areas = Column(JSON, nullable=True)  # { areas: [...], description }
	risk_rating = Column(String(20), nullable=True)  # low/medium/high
	validation_plan = Column(Text, nullable=True)
	training_plan = Column(Text, nullable=True)
	effective_date = Column(DateTime(timezone=True), nullable=True)
	status = Column(SAEnum(ChangeStatus), nullable=False, default=ChangeStatus.DRAFT)

	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), onupdate=func.now())

	approvals = relationship("ChangeApproval", back_populates="change_request", cascade="all, delete-orphan")


class ChangeApproval(Base):
	__tablename__ = "change_approvals"

	id = Column(Integer, primary_key=True, index=True)
	change_request_id = Column(Integer, ForeignKey("change_requests.id"), nullable=False, index=True)
	approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	sequence = Column(Integer, nullable=False)
	decision = Column(SAEnum(ApprovalDecision), nullable=False, default=ApprovalDecision.PENDING)
	comments = Column(Text, nullable=True)
	decided_at = Column(DateTime(timezone=True), nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	change_request = relationship("ChangeRequest", back_populates="approvals")