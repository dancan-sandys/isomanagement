from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BatchType(str, enum.Enum):
    RAW_MILK = "raw_milk"
    ADDITIVE = "additive"
    CULTURE = "culture"
    PACKAGING = "packaging"
    FINAL_PRODUCT = "final_product"
    INTERMEDIATE = "intermediate"


class BatchStatus(str, enum.Enum):
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    QUARANTINED = "quarantined"
    RELEASED = "released"
    RECALLED = "recalled"
    DISPOSED = "disposed"


class RecallStatus(str, enum.Enum):
    DRAFT = "draft"
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecallType(str, enum.Enum):
    CLASS_I = "class_i"  # Life-threatening
    CLASS_II = "class_ii"  # Temporary or reversible health effects
    CLASS_III = "class_iii"  # No health effects


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(50), unique=True, index=True, nullable=False)
    batch_type = Column(Enum(BatchType), nullable=False)
    status = Column(Enum(BatchStatus), nullable=False, default=BatchStatus.IN_PRODUCTION)
    
    # Product information
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(100))
    quantity = Column(Float)
    unit = Column(String(20))
    
    # Production information
    production_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    best_before_date = Column(DateTime(timezone=True))
    lot_number = Column(String(50))
    
    # Supplier information (for raw materials)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    supplier_batch_number = Column(String(50))
    coa_number = Column(String(50))  # Certificate of Analysis
    
    # Quality information
    quality_status = Column(String(20), default="pending")  # pending, passed, failed
    test_results = Column(JSON)  # JSON object with test results
    quality_approved_by = Column(Integer, ForeignKey("users.id"))
    quality_approved_at = Column(DateTime(timezone=True))
    
    # Storage and location
    storage_location = Column(String(100))
    storage_conditions = Column(Text)
    
    # Traceability
    parent_batches = Column(Text)  # JSON array of parent batch IDs
    child_batches = Column(Text)  # JSON array of child batch IDs
    
    # Barcode/QR code
    barcode = Column(String(100), unique=True)
    qr_code_path = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships - Commented out to avoid circular dependency issues
    # traceability_links = relationship("TraceabilityLink", back_populates="batch")
    recall_entries = relationship("RecallEntry", back_populates="batch")
    
    def __repr__(self):
        return f"<Batch(id={self.id}, batch_number='{self.batch_number}', type='{self.batch_type}')>"


class TraceabilityLink(Base):
    __tablename__ = "traceability_links"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    linked_batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # parent, child, ingredient, packaging
    
    # Link details
    quantity_used = Column(Float)
    unit = Column(String(20))
    usage_date = Column(DateTime(timezone=True), nullable=False)
    process_step = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships - Commented out to avoid circular dependency issues
    # batch = relationship("Batch", back_populates="traceability_links", foreign_keys=[batch_id])
    linked_batch = relationship("Batch", foreign_keys=[linked_batch_id])
    
    def __repr__(self):
        return f"<TraceabilityLink(id={self.id}, batch_id={self.batch_id}, linked_batch_id={self.linked_batch_id})>"


class Recall(Base):
    __tablename__ = "recalls"

    id = Column(Integer, primary_key=True, index=True)
    recall_number = Column(String(50), unique=True, index=True, nullable=False)
    recall_type = Column(Enum(RecallType), nullable=False)
    status = Column(Enum(RecallStatus), nullable=False, default=RecallStatus.DRAFT)
    
    # Recall details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    hazard_description = Column(Text)
    
    # Affected products
    affected_products = Column(Text)  # JSON array of product IDs
    affected_batches = Column(Text)  # JSON array of batch numbers
    date_range_start = Column(DateTime(timezone=True))
    date_range_end = Column(DateTime(timezone=True))
    
    # Quantities
    total_quantity_affected = Column(Float)
    quantity_in_distribution = Column(Float)
    quantity_recalled = Column(Float)
    quantity_disposed = Column(Float)
    
    # Dates
    issue_discovered_date = Column(DateTime(timezone=True), nullable=False)
    recall_initiated_date = Column(DateTime(timezone=True))
    recall_completed_date = Column(DateTime(timezone=True))
    
    # Regulatory information
    regulatory_notification_required = Column(Boolean, default=False)
    regulatory_notification_date = Column(DateTime(timezone=True))
    regulatory_reference = Column(String(100))
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    entries = relationship("RecallEntry", back_populates="recall")
    actions = relationship("RecallAction", back_populates="recall")
    
    def __repr__(self):
        return f"<Recall(id={self.id}, recall_number='{self.recall_number}', type='{self.recall_type}')>"


class RecallEntry(Base):
    __tablename__ = "recall_entries"

    id = Column(Integer, primary_key=True, index=True)
    recall_id = Column(Integer, ForeignKey("recalls.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    
    # Entry details
    quantity_affected = Column(Float, nullable=False)
    quantity_recalled = Column(Float, default=0)
    quantity_disposed = Column(Float, default=0)
    location = Column(String(100))
    customer = Column(String(100))
    
    # Status
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    completion_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    recall = relationship("Recall", back_populates="entries")
    batch = relationship("Batch", back_populates="recall_entries")
    
    def __repr__(self):
        return f"<RecallEntry(id={self.id}, recall_id={self.recall_id}, batch_id={self.batch_id})>"


class RecallAction(Base):
    __tablename__ = "recall_actions"

    id = Column(Integer, primary_key=True, index=True)
    recall_id = Column(Integer, ForeignKey("recalls.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # notification, retrieval, disposal, investigation
    
    # Action details
    description = Column(Text, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime(timezone=True))
    completed_date = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(20), default="pending")  # pending, in_progress, completed, overdue
    
    # Results
    results = Column(Text)
    evidence_files = Column(Text)  # JSON array of file paths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    recall = relationship("Recall", back_populates="actions")
    
    def __repr__(self):
        return f"<RecallAction(id={self.id}, recall_id={self.recall_id}, action_type='{self.action_type}')>"


class TraceabilityReport(Base):
    __tablename__ = "traceability_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True, index=True, nullable=False)
    report_type = Column(String(50), nullable=False)  # forward_trace, backward_trace, full_trace
    
    # Trace details
    starting_batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    trace_date = Column(DateTime(timezone=True), nullable=False)
    trace_depth = Column(Integer, default=5)  # Number of levels to trace
    
    # Results
    traced_batches = Column(Text)  # JSON array of traced batch IDs
    trace_path = Column(JSON)  # JSON object showing the trace path
    trace_summary = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    starting_batch = relationship("Batch", foreign_keys=[starting_batch_id])
    
    def __repr__(self):
        return f"<TraceabilityReport(id={self.id}, report_number='{self.report_number}', type='{self.report_type}')>" 