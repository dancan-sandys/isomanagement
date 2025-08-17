from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime
from .haccp import RiskLevel


class PRPCategory(str, enum.Enum):
    # ISO 22002-1:2025 Required Categories
    CONSTRUCTION_AND_LAYOUT = "construction_and_layout"
    LAYOUT_OF_PREMISES = "layout_of_premises"
    SUPPLIES_OF_AIR_WATER_ENERGY = "supplies_of_air_water_energy"
    SUPPORTING_SERVICES = "supporting_services"
    SUITABILITY_CLEANING_MAINTENANCE = "suitability_cleaning_maintenance"
    MANAGEMENT_OF_PURCHASED_MATERIALS = "management_of_purchased_materials"
    PREVENTION_OF_CROSS_CONTAMINATION = "prevention_of_cross_contamination"
    CLEANING_AND_SANITIZING = "cleaning_and_sanitizing"
    PEST_CONTROL = "pest_control"
    PERSONNEL_HYGIENE_FACILITIES = "personnel_hygiene_facilities"
    PERSONNEL_HYGIENE_PRACTICES = "personnel_hygiene_practices"
    REPROCESSING = "reprocessing"
    PRODUCT_RECALL_PROCEDURES = "product_recall_procedures"
    WAREHOUSING = "warehousing"
    PRODUCT_INFORMATION_CONSUMER_AWARENESS = "product_information_consumer_awareness"
    FOOD_DEFENSE_BIOVIGILANCE_BIOTERRORISM = "food_defense_biovigilance_bioterrorism"
    CONTROL_OF_NONCONFORMING_PRODUCT = "control_of_nonconforming_product"
    PRODUCT_RELEASE = "product_release"


class PRPFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    AS_NEEDED = "as_needed"


class PRPStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ChecklistStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    """Risk levels for PRP risk assessment"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class PRPProgram(Base):
    __tablename__ = "prp_programs"

    id = Column(Integer, primary_key=True, index=True)
    program_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(
        Enum(
            PRPCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    status = Column(
        Enum(
            PRPStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
        default=PRPStatus.ACTIVE,
    )
    
    # ISO 22002-1:2025 Required Fields
    objective = Column(Text, nullable=False)  # Must be defined per ISO
    scope = Column(Text, nullable=False)      # Must be defined per ISO
    responsible_department = Column(String(100), nullable=False)
    responsible_person = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Risk Assessment Integration
    risk_assessment_required = Column(Boolean, default=True)
    risk_assessment_date = Column(DateTime(timezone=True))
    risk_assessment_review_date = Column(DateTime(timezone=True))
    risk_level = Column(
        Enum(
            RiskLevel,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
    )
    
    # Enhanced Risk Integration Fields
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=True)
    risk_assessment_frequency = Column(String(100), nullable=True)
    risk_monitoring_plan = Column(Text, nullable=True)
    risk_review_plan = Column(Text, nullable=True)
    risk_improvement_plan = Column(Text, nullable=True)
    risk_control_effectiveness = Column(Integer, nullable=True)
    risk_residual_score = Column(Integer, nullable=True)
    risk_residual_level = Column(String(50), nullable=True)
    
    # Frequency and scheduling
    frequency = Column(
        Enum(
            PRPFrequency,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    frequency_details = Column(Text)  # Specific details about frequency
    next_due_date = Column(DateTime(timezone=True))
    
    # Documentation Requirements (ISO 22002-1:2025)
    sop_reference = Column(String(100), nullable=False)  # Must reference SOP
    forms_required = Column(Text)  # JSON array of required forms
    records_required = Column(Text)  # JSON array of required records
    training_requirements = Column(Text)  # Training requirements for personnel
    
    # Monitoring and Verification
    monitoring_frequency = Column(String(100))
    verification_frequency = Column(String(100))
    acceptance_criteria = Column(Text)  # Criteria for acceptable performance
    trend_analysis_required = Column(Boolean, default=False)
    
    # Corrective Actions
    corrective_action_procedure = Column(Text)
    escalation_procedure = Column(Text)
    preventive_action_procedure = Column(Text)
    
    # Review and Approval
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    checklists = relationship("PRPChecklist", back_populates="program")
    risk_assessments = relationship("RiskAssessment", back_populates="program")
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    risk_assessments_enhanced = relationship("HACCPRiskAssessment", foreign_keys="HACCPRiskAssessment.prp_program_id", cascade="all, delete-orphan")
    audit_integrations = relationship("PRPAuditIntegration", foreign_keys="PRPAuditIntegration.prp_program_id", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PRPProgram(id={self.id}, program_code='{self.program_code}', name='{self.name}')>"


class PRPChecklist(Base):
    __tablename__ = "prp_checklists"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=False)
    checklist_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(
        Enum(
            ChecklistStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
        default=ChecklistStatus.PENDING,
    )
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    completed_date = Column(DateTime(timezone=True))
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Results
    total_items = Column(Integer, default=0)
    passed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    not_applicable_items = Column(Integer, default=0)
    compliance_percentage = Column(Float, default=0.0)
    
    # Comments and notes
    general_comments = Column(Text)
    corrective_actions_required = Column(Boolean, default=False)
    corrective_actions = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    program = relationship("PRPProgram", back_populates="checklists")
    items = relationship("PRPChecklistItem", back_populates="checklist")
    
    def __repr__(self):
        return f"<PRPChecklist(id={self.id}, checklist_code='{self.checklist_code}', name='{self.name}')>"


class PRPChecklistItem(Base):
    __tablename__ = "prp_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("prp_checklists.id"), nullable=False)
    item_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    description = Column(Text)
    
    # Response options
    response_type = Column(String(50), nullable=False)  # yes_no, numeric, text, multiple_choice
    response_options = Column(Text)  # JSON array for multiple choice options
    expected_response = Column(Text)
    
    # Scoring
    is_critical = Column(Boolean, default=False)
    points = Column(Integer, default=1)
    
    # Response
    response = Column(Text)
    response_value = Column(Float)
    is_compliant = Column(Boolean)
    comments = Column(Text)
    
    # Evidence
    evidence_files = Column(Text)  # JSON array of file paths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    checklist = relationship("PRPChecklist", back_populates="items")
    
    def __repr__(self):
        return f"<PRPChecklistItem(id={self.id}, checklist_id={self.checklist_id}, question='{self.question[:50]}...')>"


class PRPTemplate(Base):
    __tablename__ = "prp_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(
        Enum(
            PRPCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    
    # Template structure
    template_structure = Column(JSON)  # JSON object defining the template structure
    default_frequency = Column(
        Enum(
            PRPFrequency,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    estimated_duration_minutes = Column(Integer)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    def __repr__(self):
        return f"<PRPTemplate(id={self.id}, template_code='{self.template_code}', name='{self.name}')>"


class PRPSchedule(Base):
    __tablename__ = "prp_schedules"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # recurring, one_time
    frequency = Column(
        Enum(
            PRPFrequency,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    
    # Scheduling details
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    next_due_date = Column(DateTime(timezone=True), nullable=False)
    
    # Time specifications
    preferred_time_start = Column(String(10))  # HH:MM format
    preferred_time_end = Column(String(10))  # HH:MM format
    day_of_week = Column(Integer)  # 0-6 (Monday-Sunday)
    day_of_month = Column(Integer)  # 1-31
    
    # Assignment
    default_assignee = Column(Integer, ForeignKey("users.id"))
    
    # Notifications
    reminder_days_before = Column(Integer, default=1)
    escalation_days_after = Column(Integer, default=1)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    program = relationship("PRPProgram")
    
    def __repr__(self):
        return f"<PRPSchedule(id={self.id}, program_id={self.program_id}, frequency='{self.frequency}')>" 


class RiskMatrix(Base):
    """Risk matrix configuration for PRP risk assessment"""
    __tablename__ = "prp_risk_matrices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Matrix configuration (JSON)
    likelihood_levels = Column(JSON)  # ["Rare", "Unlikely", "Possible", "Likely", "Certain"]
    severity_levels = Column(JSON)    # ["Negligible", "Minor", "Moderate", "Major", "Catastrophic"]
    risk_levels = Column(JSON)        # Matrix mapping likelihood x severity to risk levels
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<RiskMatrix(id={self.id}, name='{self.name}')>"


class RiskAssessment(Base):
    """Risk assessment for PRP programs - feeds into main risk register"""
    __tablename__ = "prp_risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("prp_programs.id", ondelete="CASCADE"), nullable=False)
    
    # Link to main risk register
    # risk_register_entry_id = Column(Integer, ForeignKey("risk_register.id", ondelete="SET NULL"), nullable=True)
    
    assessment_code = Column(String(50), unique=True, index=True, nullable=False)
    hazard_identified = Column(Text, nullable=False)
    hazard_description = Column(Text)
    likelihood_level = Column(String(50), nullable=False)
    severity_level = Column(String(50), nullable=False)
    risk_level = Column(
        Enum(
            RiskLevel,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        )
    )
    risk_score = Column(Integer)
    acceptability = Column(Boolean)
    existing_controls = Column(Text)
    additional_controls_required = Column(Text)
    control_effectiveness = Column(Text)
    residual_risk_level = Column(
        Enum(
            RiskLevel,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        )
    )
    residual_risk_score = Column(Integer)
    assessment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    next_review_date = Column(DateTime)
    
    # Integration with main risk module
    escalated_to_risk_register = Column(Boolean, default=False)
    escalation_date = Column(DateTime)
    escalated_by = Column(Integer, ForeignKey("users.id"))
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("PRPProgram")
    # risk_register_entry = relationship("RiskRegisterItem", foreign_keys=[risk_register_entry_id])
    escalated_by_user = relationship("User", foreign_keys=[escalated_by])

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, assessment_code='{self.assessment_code}', risk_level='{self.risk_level}')>"


class RiskControl(Base):
    """Risk control measures for PRP programs"""
    __tablename__ = "prp_risk_controls"

    id = Column(Integer, primary_key=True, index=True)
    risk_assessment_id = Column(Integer, ForeignKey("prp_risk_assessments.id"), nullable=False)
    control_code = Column(String(50), nullable=False)
    
    # Control details
    control_type = Column(String(50), nullable=False)  # preventive, detective, corrective
    control_description = Column(Text, nullable=False)
    control_procedure = Column(Text)
    
    # Implementation
    responsible_person = Column(Integer, ForeignKey("users.id"))
    implementation_date = Column(DateTime(timezone=True))
    frequency = Column(
        Enum(
            PRPFrequency,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
    )
    
    # Effectiveness
    effectiveness_measure = Column(Text)
    effectiveness_threshold = Column(String(100))
    last_effectiveness_check = Column(DateTime(timezone=True))
    effectiveness_result = Column(String(50))
    
    # Status
    status = Column(String(50), default="planned")  # planned, implemented, active, inactive
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    risk_assessment = relationship("RiskAssessment")
    
    def __repr__(self):
        return f"<RiskControl(id={self.id}, control_code='{self.control_code}')>" 


class CorrectiveActionStatus(str, enum.Enum):
    """Status for corrective actions"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    CLOSED = "closed"
    ESCALATED = "escalated"


class CorrectiveAction(Base):
    """Corrective actions for PRP non-conformances"""
    __tablename__ = "prp_corrective_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Source information
    source_type = Column(String(50), nullable=False)  # checklist, audit, complaint, etc.
    source_id = Column(Integer, nullable=False)  # ID of the source record
    checklist_id = Column(Integer, ForeignKey("prp_checklists.id"))
    program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=False)
    
    # Non-conformance details
    non_conformance_description = Column(Text, nullable=False)
    non_conformance_date = Column(DateTime(timezone=True), nullable=False)
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    
    # Root cause analysis
    immediate_cause = Column(Text)
    root_cause_analysis = Column(Text)
    root_cause_category = Column(String(100))  # equipment, process, personnel, etc.
    
    # Corrective action details
    action_description = Column(Text, nullable=False)
    action_type = Column(String(50), nullable=False)  # immediate, corrective, preventive
    responsible_person = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timeline
    target_completion_date = Column(DateTime(timezone=True), nullable=False)
    actual_completion_date = Column(DateTime(timezone=True))
    verification_date = Column(DateTime(timezone=True))
    
    # Status and progress
    status = Column(
        Enum(
            CorrectiveActionStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
        default=CorrectiveActionStatus.OPEN,
    )
    progress_percentage = Column(Integer, default=0)
    
    # Effectiveness verification
    effectiveness_criteria = Column(Text)
    effectiveness_verification = Column(Text)
    effectiveness_verified_by = Column(Integer, ForeignKey("users.id"))
    effectiveness_verified_at = Column(DateTime(timezone=True))
    
    # Review and approval
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    checklist = relationship("PRPChecklist")
    program = relationship("PRPProgram")
    
    def __repr__(self):
        return f"<CorrectiveAction(id={self.id}, action_code='{self.action_code}')>"


class PreventiveAction(Base):
    """Preventive actions for PRP programs"""
    __tablename__ = "prp_preventive_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Trigger information
    trigger_type = Column(String(50), nullable=False)  # trend_analysis, risk_assessment, etc.
    trigger_description = Column(Text, nullable=False)
    program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=False)
    
    # Action details
    action_description = Column(Text, nullable=False)
    objective = Column(Text, nullable=False)
    responsible_person = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Implementation
    implementation_plan = Column(Text)
    resources_required = Column(Text)
    budget_estimate = Column(Float)
    
    # Timeline
    planned_start_date = Column(DateTime(timezone=True))
    planned_completion_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Status
    status = Column(
        Enum(
            CorrectiveActionStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
        default=CorrectiveActionStatus.OPEN,
    )
    progress_percentage = Column(Integer, default=0)
    
    # Effectiveness
    success_criteria = Column(Text)
    effectiveness_measurement = Column(Text)
    effectiveness_result = Column(Text)
    
    # Review and approval
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    program = relationship("PRPProgram")
    
    def __repr__(self):
        return f"<PreventiveAction(id={self.id}, action_code='{self.action_code}')>" 