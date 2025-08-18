from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean, JSON
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


class AllergenFlagSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AllergenFlagStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AllergenDetectionLocation(str, enum.Enum):
    INGREDIENT = "ingredient"
    PROCESS = "process"
    PACKAGING = "packaging"
    EQUIPMENT = "equipment"
    ENVIRONMENT = "environment"


class AllergenFlag(Base):
    __tablename__ = "allergen_flags"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("product_allergen_assessments.id", ondelete="CASCADE"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    allergen_type = Column(String(100), nullable=False)  # e.g., "nuts", "milk", "gluten"
    detected_in = Column(Enum(AllergenDetectionLocation), nullable=False)
    severity = Column(Enum(AllergenFlagSeverity), nullable=False, default=AllergenFlagSeverity.MEDIUM)
    title = Column(String(255), nullable=False)  # Brief description for UI display
    description = Column(Text, nullable=False)  # Detailed description of the issue
    immediate_action = Column(Text, nullable=False)  # Required immediate actions
    detected_by = Column(Integer, nullable=False)  # User ID who detected/created the flag
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    status = Column(Enum(AllergenFlagStatus), nullable=False, default=AllergenFlagStatus.ACTIVE)
    nc_id = Column(Integer, ForeignKey("nonconformances.id", ondelete="SET NULL"), nullable=True)  # Auto-created NC for critical issues
    additional_data = Column(JSON)  # Additional metadata (detection method, confidence score, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("ProductAllergenAssessment", foreign_keys=[assessment_id])


class AllergenControlPoint(Base):
    __tablename__ = "allergen_control_points"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    process_step = Column(String(255), nullable=False)
    allergen_hazard = Column(String(100), nullable=False)
    control_measure = Column(Text, nullable=False)
    critical_limit = Column(String(255))
    monitoring_procedure = Column(Text)
    corrective_action = Column(Text)
    verification_procedure = Column(Text)
    is_ccp = Column(Boolean, default=False)  # Is this a Critical Control Point?
    risk_level = Column(Enum(AllergenRiskLevel), nullable=False, default=AllergenRiskLevel.MEDIUM)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RegulatoryRegion(str, enum.Enum):
    US = "US"
    EU = "EU"
    CA = "CA"
    AU = "AU"
    UK = "UK"
    JP = "JP"
    CN = "CN"


class RegulatoryComplianceMatrix(Base):
    __tablename__ = "regulatory_compliance_matrix"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(Enum(RegulatoryRegion), nullable=False, index=True)
    regulation_code = Column(String(50), nullable=False)  # FALCPA, FIC, etc.
    requirement_type = Column(String(50), nullable=False)  # labeling, declaration, warning
    requirement_text = Column(Text, nullable=False)
    requirement_details = Column(JSON)  # Structured requirement details
    is_mandatory = Column(Boolean, default=True)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)  # For temporary requirements
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceValidationStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    COMPLIANT_WITH_WARNINGS = "compliant_with_warnings"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"


class LabelComplianceValidation(Base):
    __tablename__ = "label_compliance_validations"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("label_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("label_template_versions.id", ondelete="CASCADE"), nullable=True, index=True)
    region = Column(Enum(RegulatoryRegion), nullable=False)
    compliance_score = Column(Integer, nullable=False)  # 0-100 score
    status = Column(Enum(ComplianceValidationStatus), nullable=False, default=ComplianceValidationStatus.PENDING_REVIEW)
    validation_results = Column(JSON, nullable=False)  # Detailed check results
    recommendations = Column(JSON)  # Compliance improvement recommendations
    validated_by = Column(Integer, nullable=False)
    validated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Validation expiry for regulatory changes

    # Relationships
    template = relationship("LabelTemplate", foreign_keys=[template_id])
    version = relationship("LabelTemplateVersion", foreign_keys=[version_id])


