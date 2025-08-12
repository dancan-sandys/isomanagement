from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RiskItemType(str, enum.Enum):
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class RiskCategory(str, enum.Enum):
    PROCESS = "process"
    SUPPLIER = "supplier"
    STAFF = "staff"
    ENVIRONMENT = "environment"
    HACCP = "haccp"
    PRP = "prp"
    DOCUMENT = "document"
    TRAINING = "training"
    EQUIPMENT = "equipment"
    COMPLIANCE = "compliance"
    CUSTOMER = "customer"
    OTHER = "other"


class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLikelihood(str, enum.Enum):
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"


class RiskClassification(str, enum.Enum):
    FOOD_SAFETY = "food_safety"
    BUSINESS = "business"
    CUSTOMER = "customer"


class RiskDetectability(str, enum.Enum):
    EASILY_DETECTABLE = "easily_detectable"
    MODERATELY_DETECTABLE = "moderately_detectable"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"
    ALMOST_UNDETECTABLE = "almost_undetectable"


class RiskRegisterItem(Base):
    __tablename__ = "risk_register"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(Enum(RiskItemType), nullable=False)
    risk_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    category = Column(Enum(RiskCategory), nullable=False, default=RiskCategory.OTHER)
    classification = Column(Enum(RiskClassification), nullable=True)
    status = Column(Enum(RiskStatus), nullable=False, default=RiskStatus.OPEN)

    severity = Column(Enum(RiskSeverity), nullable=False, default=RiskSeverity.LOW)
    likelihood = Column(Enum(RiskLikelihood), nullable=False, default=RiskLikelihood.UNLIKELY)
    detectability = Column(Enum(RiskDetectability), nullable=True)
    impact_score = Column(Integer, nullable=True)  # optional numeric 1-5
    risk_score = Column(Integer, nullable=False, default=1)  # computed S*L*(D)

    mitigation_plan = Column(Text, nullable=True)
    residual_risk = Column(String(100), nullable=True)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)

    # Optional references by string (e.g., "document:123", "batch:45") to avoid cross-deps
    references = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    actions = relationship("RiskAction", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RiskRegisterItem(id={self.id}, number='{self.risk_number}', type='{self.item_type}')>"


class RiskAction(Base):
    __tablename__ = "risk_actions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("RiskRegisterItem", back_populates="actions")

    def __repr__(self):
        return f"<RiskAction(id={self.id}, item_id={self.item_id}, title='{self.title}')>"


