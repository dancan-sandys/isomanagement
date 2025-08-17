from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Boolean, Float, JSON
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


class ProgramStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RiskMethod(str, enum.Enum):
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    HYBRID = "hybrid"


class AuditProgram(Base):
    __tablename__ = "audit_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    objectives = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)  # e.g., 2024
    period = Column(String(50))  # e.g., "Q1", "Q2", "Annual"
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_method = Column(Enum(RiskMethod), nullable=False, default=RiskMethod.QUALITATIVE)
    resources = Column(Text)  # Budget, personnel, equipment
    schedule = Column(JSON)  # JSON structure for detailed scheduling
    kpis = Column(JSON)  # JSON structure for KPI targets and metrics
    status = Column(Enum(ProgramStatus), nullable=False, default=ProgramStatus.DRAFT)
    created_by = Column(Integer, nullable=False)
    # Risk integration fields
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=True)
    risk_assessment_required = Column(Boolean, default=True)
    risk_assessment_frequency = Column(String(100), nullable=True)
    risk_review_frequency = Column(String(100), nullable=True)
    last_risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    next_risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    risk_monitoring_plan = Column(Text, nullable=True)
    risk_improvement_plan = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audits = relationship("Audit", back_populates="program", cascade="all, delete-orphan")
    manager = relationship("User", foreign_keys=[manager_id])
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    risk_assessments = relationship("AuditRiskAssessment", foreign_keys="AuditRiskAssessment.audit_id", cascade="all, delete-orphan")
    risks = relationship("AuditRisk", back_populates="program", cascade="all, delete-orphan")


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
    # Link to audit program
    program_id = Column(Integer, ForeignKey("audit_programs.id"), nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Risk integration fields
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=True)
    risk_assessment_method = Column(String(100), nullable=True)
    risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    risk_assessor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_treatment_plan = Column(Text, nullable=True)
    risk_monitoring_frequency = Column(String(100), nullable=True)
    risk_review_frequency = Column(String(100), nullable=True)
    risk_control_effectiveness = Column(Integer, nullable=True)
    risk_residual_score = Column(Integer, nullable=True)
    risk_residual_level = Column(String(50), nullable=True)
    
    # Relationships
    program = relationship("AuditProgram", back_populates="audits")
    checklist_items = relationship("AuditChecklistItem", back_populates="audit", cascade="all, delete-orphan")
    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")
    attachments = relationship("AuditAttachment", back_populates="audit", cascade="all, delete-orphan")
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    risk_assessor = relationship("User", foreign_keys=[risk_assessor_id])
    risk_assessments = relationship("AuditRiskAssessment", foreign_keys="AuditRiskAssessment.audit_id", cascade="all, delete-orphan")
    team_members = relationship("AuditTeamMember", back_populates="audit", cascade="all, delete-orphan")
    evidence = relationship("AuditEvidence", back_populates="audit", cascade="all, delete-orphan")
    activity_logs = relationship("AuditActivityLog", back_populates="audit", cascade="all, delete-orphan")


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
    evidence = relationship("AuditEvidence", back_populates="checklist_item", cascade="all, delete-orphan")


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

    # Risk integration fields
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=True)
    risk_assessment_method = Column(String(100), nullable=True)
    risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    risk_assessor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_treatment_plan = Column(Text, nullable=True)
    risk_monitoring_frequency = Column(String(100), nullable=True)
    risk_review_frequency = Column(String(100), nullable=True)
    risk_control_effectiveness = Column(Integer, nullable=True)
    risk_residual_score = Column(Integer, nullable=True)
    risk_residual_level = Column(String(50), nullable=True)
    risk_acceptable = Column(Boolean, nullable=True)
    risk_justification = Column(Text, nullable=True)
    
    audit = relationship("Audit", back_populates="findings")
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    risk_assessor = relationship("User", foreign_keys=[risk_assessor_id])
    risk_assessments = relationship("AuditRiskAssessment", foreign_keys="AuditRiskAssessment.audit_finding_id", cascade="all, delete-orphan")
    prp_integrations = relationship("PRPAuditIntegration", foreign_keys="PRPAuditIntegration.audit_finding_id", cascade="all, delete-orphan")
    evidence = relationship("AuditEvidence", back_populates="finding", cascade="all, delete-orphan")


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


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditRisk(Base):
    __tablename__ = "audit_risks"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("audit_programs.id", ondelete="CASCADE"), nullable=False)
    area_name = Column(String(255), nullable=False)  # e.g., "Production Line A", "Supplier X"
    process_name = Column(String(255), nullable=True)  # e.g., "HACCP", "Document Control"
    risk_rating = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM)
    risk_score = Column(Integer, nullable=True)  # 1-10 scale for quantitative assessment
    rationale = Column(Text, nullable=False)  # Why this area/process is risky
    last_audit_date = Column(DateTime, nullable=True)
    next_audit_due = Column(DateTime, nullable=True)
    audit_frequency_months = Column(Integer, nullable=True)  # How often to audit this area
    responsible_auditor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    mitigation_measures = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("AuditProgram", back_populates="risks")
    responsible_auditor = relationship("User", foreign_keys=[responsible_auditor_id])


class TeamMemberRole(str, enum.Enum):
    LEAD_AUDITOR = "lead_auditor"
    AUDITOR = "auditor"
    OBSERVER = "observer"
    TECHNICAL_EXPERT = "technical_expert"
    TRAINEE = "trainee"


class CompetenceStatus(str, enum.Enum):
    COMPETENT = "competent"
    NEEDS_TRAINING = "needs_training"
    INCOMPETENT = "incompetent"
    PENDING_ASSESSMENT = "pending_assessment"


class AuditTeamMember(Base):
    __tablename__ = "audit_team_members"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(TeamMemberRole), nullable=False, default=TeamMemberRole.AUDITOR)
    competence_tags = Column(Text)  # JSON array of competence areas e.g., ["HACCP", "ISO 22000", "Food Safety"]
    competence_status = Column(Enum(CompetenceStatus), nullable=False, default=CompetenceStatus.PENDING_ASSESSMENT)
    independence_confirmed = Column(Boolean, default=False)  # Impartiality check
    impartiality_notes = Column(Text)  # Notes about impartiality assessment
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    signed_at = Column(DateTime, nullable=True)  # When team member accepted assignment
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    audit = relationship("Audit", back_populates="team_members")
    user = relationship("User", foreign_keys=[user_id])
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])


class AuditEvidence(Base):
    __tablename__ = "audit_evidence"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    checklist_item_id = Column(Integer, ForeignKey("audit_checklist_items.id"), nullable=True)
    finding_id = Column(Integer, ForeignKey("audit_findings.id"), nullable=True)
    evidence_type = Column(String(50), nullable=False)  # observation, document, interview, test, etc.
    description = Column(Text, nullable=False)
    source = Column(String(255))  # Who/what provided the evidence
    collected_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)
    location = Column(String(255))  # Where evidence was collected
    sample_size = Column(Integer, nullable=True)  # For sampling evidence
    sample_method = Column(String(100), nullable=True)  # Sampling methodology
    reliability_score = Column(Integer, nullable=True)  # 1-5 scale for evidence reliability
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    audit = relationship("Audit", back_populates="evidence")
    checklist_item = relationship("AuditChecklistItem", back_populates="evidence")
    finding = relationship("AuditFinding", back_populates="evidence")
    collector = relationship("User", foreign_keys=[collected_by])


class AuditActivityLog(Base):
    __tablename__ = "audit_activity_log"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # interview, walkthrough, observation, meeting, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    participants = Column(Text)  # JSON array of participant user IDs
    location = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    outcomes = Column(Text)  # Key findings or outcomes from the activity
    attachments = Column(Text)  # JSON array of attachment file paths
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    audit = relationship("Audit", back_populates="activity_logs")
    conductor = relationship("User", foreign_keys=[conducted_by])

