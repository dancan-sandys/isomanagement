from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PRPCategory(str, enum.Enum):
    CLEANING_SANITATION = "cleaning_sanitation"
    PEST_CONTROL = "pest_control"
    STAFF_HYGIENE = "staff_hygiene"
    WASTE_MANAGEMENT = "waste_management"
    EQUIPMENT_CALIBRATION = "equipment_calibration"
    MAINTENANCE = "maintenance"
    PERSONNEL_TRAINING = "personnel_training"
    SUPPLIER_CONTROL = "supplier_control"
    RECALL_PROCEDURES = "recall_procedures"
    WATER_QUALITY = "water_quality"
    AIR_QUALITY = "air_quality"
    TRANSPORTATION = "transportation"


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


class PRPProgram(Base):
    __tablename__ = "prp_programs"

    id = Column(Integer, primary_key=True, index=True)
    program_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(PRPCategory), nullable=False)
    status = Column(Enum(PRPStatus), nullable=False, default=PRPStatus.ACTIVE)
    
    # Program details
    objective = Column(Text)
    scope = Column(Text)
    responsible_department = Column(String(100))
    responsible_person = Column(Integer, ForeignKey("users.id"))
    
    # Frequency and scheduling
    frequency = Column(Enum(PRPFrequency), nullable=False)
    frequency_details = Column(Text)  # Specific details about frequency
    next_due_date = Column(DateTime(timezone=True))
    
    # Documentation
    sop_reference = Column(String(100))
    forms_required = Column(Text)  # JSON array of required forms
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    checklists = relationship("PRPChecklist", back_populates="program")
    
    def __repr__(self):
        return f"<PRPProgram(id={self.id}, program_code='{self.program_code}', name='{self.name}')>"


class PRPChecklist(Base):
    __tablename__ = "prp_checklists"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=False)
    checklist_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(ChecklistStatus), nullable=False, default=ChecklistStatus.PENDING)
    
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
    category = Column(Enum(PRPCategory), nullable=False)
    
    # Template structure
    template_structure = Column(JSON)  # JSON object defining the template structure
    default_frequency = Column(Enum(PRPFrequency), nullable=False)
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
    frequency = Column(Enum(PRPFrequency), nullable=False)
    
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