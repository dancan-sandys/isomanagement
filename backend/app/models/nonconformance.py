from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class NonConformanceSource(str, enum.Enum):
    PRP = "prp"
    AUDIT = "audit"
    COMPLAINT = "complaint"
    PRODUCTION_DEVIATION = "production_deviation"
    SUPPLIER = "supplier"
    HACCP = "haccp"
    DOCUMENT = "document"
    OTHER = "other"


class NonConformanceStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    CAPA_ASSIGNED = "capa_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"


class CAPAStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"
    OVERDUE = "overdue"


class RootCauseMethod(str, enum.Enum):
    FIVE_WHYS = "five_whys"
    ISHIKAWA = "ishikawa"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    OTHER = "other"


class NonConformance(Base):
    __tablename__ = "non_conformances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(Enum(NonConformanceSource), nullable=False)
    
    # Reference information
    batch_reference = Column(String(100))
    product_reference = Column(String(100))
    process_reference = Column(String(100))
    location = Column(String(200))
    
    # Classification
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    impact_area = Column(String(100))  # food safety, quality, regulatory, customer
    category = Column(String(100))
    
    # Status and dates
    status = Column(Enum(NonConformanceStatus), nullable=False, default=NonConformanceStatus.OPEN)
    reported_date = Column(DateTime(timezone=True), nullable=False)
    target_resolution_date = Column(DateTime(timezone=True))
    actual_resolution_date = Column(DateTime(timezone=True))
    
    # Assignment
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_date = Column(DateTime(timezone=True))
    
    # Evidence and attachments
    evidence_files = Column(JSON)  # JSON array of file paths
    attachments = Column(JSON)  # JSON array of attachment information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    capa_actions = relationship("CAPAAction", back_populates="non_conformance")
    root_cause_analyses = relationship("RootCauseAnalysis", back_populates="non_conformance")
    verifications = relationship("CAPAVerification", back_populates="non_conformance")
    
    def __repr__(self):
        return f"<NonConformance(id={self.id}, nc_number='{self.nc_number}', title='{self.title}')>"


class RootCauseAnalysis(Base):
    __tablename__ = "root_cause_analyses"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # Analysis details
    method = Column(Enum(RootCauseMethod), nullable=False)
    analysis_date = Column(DateTime(timezone=True), nullable=False)
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Analysis results
    immediate_cause = Column(Text)
    underlying_cause = Column(Text)
    root_cause = Column(Text)
    
    # 5 Whys analysis
    why_1 = Column(Text)
    why_2 = Column(Text)
    why_3 = Column(Text)
    why_4 = Column(Text)
    why_5 = Column(Text)
    
    # Ishikawa/Fishbone analysis
    fishbone_categories = Column(JSON)  # JSON object with categories and factors
    fishbone_diagram_data = Column(JSON)  # JSON object with diagram structure
    
    # Contributing factors
    contributing_factors = Column(Text)  # JSON array of contributing factors
    system_failures = Column(Text)  # JSON array of system failures
    
    # Recommendations
    recommendations = Column(Text)  # JSON array of recommendations
    preventive_measures = Column(Text)  # JSON array of preventive measures
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="root_cause_analyses")
    
    def __repr__(self):
        # Avoid accessing potentially expired attributes (detached instances)
        try:
            rid = object.__getattribute__(self, 'id')
        except Exception:
            rid = None
        return f"<RootCauseAnalysis(id={rid})>"


class CAPAAction(Base):
    __tablename__ = "capa_actions"

    id = Column(Integer, primary_key=True, index=True)
    capa_number = Column(String(50), unique=True, index=True, nullable=False)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # CAPA details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(50))  # corrective, preventive, both
    
    # Assignment
    responsible_person = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_date = Column(DateTime(timezone=True), nullable=False)
    target_completion_date = Column(DateTime(timezone=True), nullable=False)
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Status and progress
    status = Column(Enum(CAPAStatus), nullable=False, default=CAPAStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    
    # Resources and budget
    required_resources = Column(Text)  # JSON array of resources
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    
    # Implementation details
    implementation_plan = Column(Text)
    milestones = Column(JSON)  # JSON array of milestones
    deliverables = Column(Text)  # JSON array of deliverables
    
    # Effectiveness
    effectiveness_criteria = Column(Text)  # JSON array of effectiveness criteria
    effectiveness_measured = Column(Boolean, default=False)
    effectiveness_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="capa_actions")
    verifications = relationship("CAPAVerification", back_populates="capa_action")
    
    def __repr__(self):
        return f"<CAPAAction(id={self.id}, capa_number='{self.capa_number}', title='{self.title}')>"


class CAPAVerification(Base):
    __tablename__ = "capa_verifications"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    capa_action_id = Column(Integer, ForeignKey("capa_actions.id"), nullable=False)
    
    # Verification details
    verification_date = Column(DateTime(timezone=True), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Verification criteria
    verification_criteria = Column(Text)  # JSON array of verification criteria
    verification_method = Column(String(100))
    verification_evidence = Column(Text)  # JSON array of evidence
    
    # Results
    verification_result = Column(String(20))  # passed, failed, conditional
    effectiveness_score = Column(Float)
    comments = Column(Text)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_actions = Column(Text)  # JSON array of follow-up actions
    next_verification_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="verifications")
    capa_action = relationship("CAPAAction", back_populates="verifications")
    
    def __repr__(self):
        return f"<CAPAVerification(id={self.id}, non_conformance_id={self.non_conformance_id}, capa_action_id={self.capa_action_id})>"


class NonConformanceAttachment(Base):
    __tablename__ = "non_conformance_attachments"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    original_filename = Column(String(255))
    
    # Attachment details
    attachment_type = Column(String(50))  # evidence, document, photo, video, etc.
    description = Column(Text)
    
    # Upload information
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    non_conformance = relationship("NonConformance")
    
    def __repr__(self):
        return f"<NonConformanceAttachment(id={self.id}, non_conformance_id={self.non_conformance_id}, file_name='{self.file_name}')>" 