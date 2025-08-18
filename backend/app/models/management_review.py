from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ManagementReviewStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ManagementReviewType(str, enum.Enum):
    SCHEDULED = "scheduled"
    AD_HOC = "ad_hoc"
    EMERGENCY = "emergency"


class ReviewInputType(str, enum.Enum):
    AUDIT_RESULTS = "audit_results"
    NC_CAPA_STATUS = "nc_capa_status"
    SUPPLIER_PERFORMANCE = "supplier_performance"
    KPI_METRICS = "kpi_metrics"
    CUSTOMER_FEEDBACK = "customer_feedback"
    RISK_ASSESSMENT = "risk_assessment"
    HACCP_PERFORMANCE = "haccp_performance"
    PRP_PERFORMANCE = "prp_performance"
    RESOURCE_ADEQUACY = "resource_adequacy"
    EXTERNAL_ISSUES = "external_issues"
    INTERNAL_ISSUES = "internal_issues"
    PREVIOUS_ACTIONS = "previous_actions"


class ReviewOutputType(str, enum.Enum):
    IMPROVEMENT_ACTION = "improvement_action"
    RESOURCE_ALLOCATION = "resource_allocation"
    POLICY_CHANGE = "policy_change"
    OBJECTIVE_UPDATE = "objective_update"
    SYSTEM_CHANGE = "system_change"
    TRAINING_REQUIREMENT = "training_requirement"
    RISK_TREATMENT = "risk_treatment"


class ActionPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ManagementReview(Base):
    __tablename__ = "management_reviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Enhanced fields for ISO 22000:2018 compliance
    review_type = Column(Enum(ManagementReviewType), nullable=False, default=ManagementReviewType.SCHEDULED)
    review_scope = Column(Text, nullable=True)  # Areas covered in this review
    
    # Attendee information (structured)
    attendees = Column(JSON, nullable=True)  # Structured participant data
    chairperson_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # ISO-required review elements
    food_safety_policy_reviewed = Column(Boolean, default=False)
    food_safety_objectives_reviewed = Column(Boolean, default=False)
    fsms_changes_required = Column(Boolean, default=False)
    resource_adequacy_assessment = Column(Text, nullable=True)
    improvement_opportunities = Column(JSON, nullable=True)
    previous_actions_status = Column(JSON, nullable=True)
    external_issues = Column(Text, nullable=True)
    internal_issues = Column(Text, nullable=True)
    
    # Performance data summaries
    customer_feedback_summary = Column(Text, nullable=True)
    supplier_performance_summary = Column(Text, nullable=True)
    audit_results_summary = Column(Text, nullable=True)
    nc_capa_summary = Column(Text, nullable=True)
    kpi_performance_summary = Column(Text, nullable=True)
    
    # Review documentation
    minutes = Column(Text, nullable=True)  # Detailed meeting minutes
    inputs = Column(JSON, nullable=True)   # Structured inputs data
    outputs = Column(JSON, nullable=True)  # Structured decisions/actions
    
    # Review effectiveness
    review_effectiveness_score = Column(Float, nullable=True)
    effectiveness_justification = Column(Text, nullable=True)
    
    # Status and scheduling
    status = Column(Enum(ManagementReviewStatus), nullable=False, default=ManagementReviewStatus.PLANNED)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    review_frequency = Column(String(50), nullable=True)  # e.g., "quarterly", "annually"
    
    # Audit trail
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    agenda_items = relationship("ReviewAgendaItem", back_populates="review", cascade="all, delete-orphan")
    actions = relationship("ReviewAction", back_populates="review", cascade="all, delete-orphan")
    inputs_data = relationship("ManagementReviewInput", back_populates="review", cascade="all, delete-orphan")
    outputs_data = relationship("ManagementReviewOutput", back_populates="review", cascade="all, delete-orphan")
    chairperson = relationship("User", foreign_keys=[chairperson_id])
    creator = relationship("User", foreign_keys=[created_by])


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
    
    # Enhanced fields for better tracking
    action_type = Column(Enum(ReviewOutputType), nullable=True)
    priority = Column(Enum(ActionPriority), nullable=False, default=ActionPriority.MEDIUM)
    status = Column(Enum(ActionStatus), nullable=False, default=ActionStatus.ASSIGNED)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    progress_notes = Column(Text, nullable=True)
    
    # Completion tracking
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Verification
    verification_required = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Resource requirements
    estimated_effort_hours = Column(Float, nullable=True)
    actual_effort_hours = Column(Float, nullable=True)
    resource_requirements = Column(Text, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    review = relationship("ManagementReview", back_populates="actions")
    assignee = relationship("User", foreign_keys=[assigned_to])
    completer = relationship("User", foreign_keys=[completed_by])
    verifier = relationship("User", foreign_keys=[verified_by])


class ManagementReviewInput(Base):
    """Model for tracking structured inputs to management reviews"""
    __tablename__ = "management_review_inputs"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("management_reviews.id"), nullable=False)
    input_type = Column(Enum(ReviewInputType), nullable=False)
    input_source = Column(String(100), nullable=True)  # Source module/system
    input_data = Column(JSON, nullable=True)  # Structured data
    input_summary = Column(Text, nullable=True)  # Human-readable summary
    collection_date = Column(DateTime(timezone=True), nullable=True)
    responsible_person_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Data quality indicators
    data_completeness_score = Column(Float, nullable=True)
    data_accuracy_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    review = relationship("ManagementReview", back_populates="inputs_data")
    responsible_person = relationship("User", foreign_keys=[responsible_person_id])


class ManagementReviewOutput(Base):
    """Model for tracking structured outputs from management reviews"""
    __tablename__ = "management_review_outputs"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("management_reviews.id"), nullable=False)
    output_type = Column(Enum(ReviewOutputType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Assignment and tracking
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Enum(ActionPriority), nullable=False, default=ActionPriority.MEDIUM)
    status = Column(Enum(ActionStatus), nullable=False, default=ActionStatus.ASSIGNED)
    
    # Implementation details
    implementation_plan = Column(Text, nullable=True)
    resource_requirements = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    progress_updates = Column(JSON, nullable=True)  # Array of progress updates
    
    # Completion and verification
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completion_evidence = Column(Text, nullable=True)
    
    verification_required = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Impact assessment
    expected_impact = Column(Text, nullable=True)
    actual_impact = Column(Text, nullable=True)
    impact_measurement_date = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    review = relationship("ManagementReview", back_populates="outputs_data")
    assignee = relationship("User", foreign_keys=[assigned_to])
    verifier = relationship("User", foreign_keys=[verified_by])


class ManagementReviewTemplate(Base):
    """Model for management review templates to ensure consistency"""
    __tablename__ = "management_review_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template structure
    agenda_template = Column(JSON, nullable=True)  # Standard agenda items
    input_checklist = Column(JSON, nullable=True)  # Required inputs checklist
    output_categories = Column(JSON, nullable=True)  # Standard output categories
    
    # Configuration
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    review_frequency = Column(String(50), nullable=True)
    
    # Template metadata
    applicable_departments = Column(JSON, nullable=True)  # Departments this applies to
    compliance_standards = Column(JSON, nullable=True)  # ISO standards covered
    
    # Audit trail
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])


class ManagementReviewKPI(Base):
    """Model for tracking management review effectiveness KPIs"""
    __tablename__ = "management_review_kpis"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("management_reviews.id"), nullable=True)
    
    # KPI details
    kpi_name = Column(String(200), nullable=False)
    kpi_description = Column(Text, nullable=True)
    kpi_category = Column(String(100), nullable=True)  # effectiveness, timeliness, action_completion, etc.
    
    # Measurement
    target_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    unit_of_measure = Column(String(50), nullable=True)
    measurement_date = Column(DateTime(timezone=True), nullable=True)
    
    # Performance assessment
    performance_status = Column(String(50), nullable=True)  # on_target, below_target, above_target
    variance_percentage = Column(Float, nullable=True)
    improvement_trend = Column(String(50), nullable=True)  # improving, declining, stable
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    review = relationship("ManagementReview")


