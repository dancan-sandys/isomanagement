from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SAEnum, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ActionSource(str, enum.Enum):
    INTERESTED_PARTY = "interested_party"
    SWOT = "swot"
    PESTEL = "pestel"
    RISK_OPPORTUNITY = "risk_opportunity"
    MANAGEMENT_REVIEW = "management_review"
    CAPA = "capa"


class ActionStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class ActionPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionLogEntry(Base):
    __tablename__ = "action_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(SAEnum(ActionSource), nullable=False)
    source_entity = Column(String(50), nullable=True)  # e.g., model name
    source_entity_id = Column(Integer, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(SAEnum(ActionPriority), nullable=False, default=ActionPriority.MEDIUM)
    status = Column(SAEnum(ActionStatus), nullable=False, default=ActionStatus.OPEN)
    effectiveness_score = Column(Float, nullable=True)
    evidence = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class InterestedParty(Base):
    __tablename__ = "interested_parties"

    id = Column(Integer, primary_key=True, index=True)
    stakeholder_name = Column(String(255), nullable=False)
    needs_expectations = Column(Text, nullable=False)
    action_to_address = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class SWOTType(str, enum.Enum):
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    OPPORTUNITY = "opportunity"
    THREAT = "threat"


class SWOTIssue(Base):
    __tablename__ = "swot_issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_type = Column(SAEnum(SWOTType), nullable=False)
    description = Column(Text, nullable=False)
    required_action = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class PESTELType(str, enum.Enum):
    POLITICAL = "political"
    ECONOMIC = "economic"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"


class PESTELIssue(Base):
    __tablename__ = "pestel_issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_type = Column(SAEnum(PESTELType), nullable=False)
    description = Column(Text, nullable=False)
    required_action = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

