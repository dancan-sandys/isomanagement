from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AllergenRiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProductAllergenAssessment(Base):
    __tablename__ = "product_allergen_assessments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    inherent_allergens = Column(Text)  # JSON string array of inherent allergens from formulation
    cross_contact_sources = Column(Text)  # JSON string array of potential cross-contact sources
    risk_level = Column(Enum(AllergenRiskLevel), nullable=False, default=AllergenRiskLevel.LOW)
    precautionary_labeling = Column(String(255))  # e.g., "May contain traces of nuts"
    control_measures = Column(Text)  # procedural controls to reduce risk
    validation_verification = Column(Text)  # evidence summary
    reviewed_by = Column(Integer, nullable=True)
    last_reviewed_at = Column(DateTime)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LabelTemplate(Base):
    __tablename__ = "label_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    versions = relationship("LabelTemplateVersion", back_populates="template", cascade="all, delete-orphan")


class LabelVersionStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class LabelTemplateVersion(Base):
    __tablename__ = "label_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("label_templates.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # JSON or plain text content for the label layout/data
    change_description = Column(Text)
    change_reason = Column(Text)
    status = Column(Enum(LabelVersionStatus), nullable=False, default=LabelVersionStatus.DRAFT)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    template = relationship("LabelTemplate", back_populates="versions")
    approvals = relationship("LabelTemplateApproval", back_populates="version", cascade="all, delete-orphan")


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LabelTemplateApproval(Base):
    __tablename__ = "label_template_approvals"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("label_template_versions.id", ondelete="CASCADE"), nullable=False)
    approver_id = Column(Integer, nullable=False)
    approval_order = Column(Integer, nullable=False)
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    comments = Column(Text)
    decided_at = Column(DateTime)

    version = relationship("LabelTemplateVersion", back_populates="approvals")


