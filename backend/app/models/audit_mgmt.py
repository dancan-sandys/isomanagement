from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AuditType(str, enum.Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    SUPPLIER = "supplier"


class AuditStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    audit_type = Column(Enum(AuditType), nullable=False, default=AuditType.INTERNAL)
    scope = Column(Text)
    objectives = Column(Text)
    criteria = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    # Actual completion timestamp to support KPI calculations
    actual_end_at = Column(DateTime)
    status = Column(Enum(AuditStatus), nullable=False, default=AuditStatus.PLANNED)
    auditor_id = Column(Integer, nullable=True)
    lead_auditor_id = Column(Integer, nullable=True)
    auditee_department = Column(String(255))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    checklist_items = relationship("AuditChecklistItem", back_populates="audit", cascade="all, delete-orphan")
    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")
    attachments = relationship("AuditAttachment", back_populates="audit", cascade="all, delete-orphan")


class AuditChecklistTemplate(Base):
    __tablename__ = "audit_checklist_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    clause_ref = Column(String(100), nullable=True)
    question = Column(Text, nullable=False)
    requirement = Column(Text)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChecklistResponse(str, enum.Enum):
    CONFORMING = "conforming"
    NONCONFORMING = "nonconforming"
    NOT_APPLICABLE = "not_applicable"


class AuditChecklistItem(Base):
    __tablename__ = "audit_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("audit_checklist_templates.id"), nullable=True)
    clause_ref = Column(String(100))
    question = Column(Text)
    response = Column(Enum(ChecklistResponse), nullable=True)
    # scoring and comments for execution
    score = Column(Float, nullable=True)
    comment = Column(Text)
    evidence_text = Column(Text)
    evidence_file_path = Column(String(500))
    responsible_person_id = Column(Integer, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="checklist_items")


class FindingSeverity(str, enum.Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    CLOSED = "closed"


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    clause_ref = Column(String(100))
    description = Column(Text, nullable=False)
    # Finding type to distinguish NCs, observations, and opportunities for improvement
    class FindingType(str, enum.Enum):
        NONCONFORMITY = "nonconformity"
        OBSERVATION = "observation"
        OFI = "ofi"
    finding_type = Column(Enum(FindingType), nullable=False, default=FindingType.NONCONFORMITY)
    severity = Column(Enum(FindingSeverity), nullable=False, default=FindingSeverity.MINOR)
    corrective_action = Column(Text)
    responsible_person_id = Column(Integer, nullable=True)
    target_completion_date = Column(DateTime, nullable=True)
    status = Column(Enum(FindingStatus), nullable=False, default=FindingStatus.OPEN)
    # Closure timestamp to support KPI calculations and lifecycle auditing
    closed_at = Column(DateTime, nullable=True)
    related_nc_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="findings")


class AuditAttachment(Base):
    __tablename__ = "audit_attachments"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    uploaded_by = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="attachments")


# Optional per-checklist-item attachment
class AuditItemAttachment(Base):
    __tablename__ = "audit_item_attachments"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("audit_checklist_items.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    uploaded_by = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


# Optional per-finding attachment
class AuditFindingAttachment(Base):
    __tablename__ = "audit_finding_attachments"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("audit_findings.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    uploaded_by = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class AuditAuditee(Base):
    __tablename__ = "audit_auditees"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String(100))
    added_at = Column(DateTime, default=datetime.utcnow)


class AuditPlan(Base):
    __tablename__ = "audit_plans"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, unique=True)
    agenda = Column(Text)
    criteria_refs = Column(Text)
    sampling_plan = Column(Text)
    documents_to_review = Column(Text)
    logistics = Column(Text)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

