from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SupplierStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"
    BLACKLISTED = "blacklisted"


class SupplierCategory(str, enum.Enum):
    RAW_MILK = "raw_milk"
    ADDITIVES = "additives"
    CULTURES = "cultures"
    PACKAGING = "packaging"
    EQUIPMENT = "equipment"
    CHEMICALS = "chemicals"
    SERVICES = "services"


class EvaluationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class InspectionStatus(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    status = Column(
        Enum(
            SupplierStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
        default=SupplierStatus.PENDING_APPROVAL,
    )
    category = Column(
        Enum(
            SupplierCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    
    # Contact information
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    website = Column(String(200))
    
    # Address
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Business information
    business_registration_number = Column(String(100))
    tax_identification_number = Column(String(100))
    company_type = Column(String(100))
    year_established = Column(Integer)
    
    # Certifications
    certifications = Column(Text)  # JSON array of certifications
    certification_expiry_dates = Column(JSON)  # JSON object with certification expiry dates
    
    # Evaluation
    overall_score = Column(Float, default=0.0)
    last_evaluation_date = Column(DateTime(timezone=True))
    next_evaluation_date = Column(DateTime(timezone=True))
    
    # Risk assessment
    risk_level = Column(String(20), default="low")  # low, medium, high
    risk_factors = Column(Text)  # JSON array of risk factors
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    materials = relationship("Material", back_populates="supplier")
    evaluations = relationship("SupplierEvaluation", back_populates="supplier")
    deliveries = relationship("IncomingDelivery", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, supplier_code='{self.supplier_code}', name='{self.name}')>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    
    # Supplier information
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier_material_code = Column(String(50))
    
    # Specifications
    specifications = Column(JSON)  # JSON object with material specifications
    quality_parameters = Column(Text)  # JSON array of quality parameters
    acceptable_limits = Column(JSON)  # JSON object with acceptable limits
    
    # Allergen information
    allergens = Column(Text)  # JSON array of allergens
    allergen_statement = Column(Text)
    
    # Storage and handling
    storage_conditions = Column(Text)
    shelf_life_days = Column(Integer)
    handling_instructions = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="materials")
    deliveries = relationship("IncomingDelivery", back_populates="material")
    
    def __repr__(self):
        return f"<Material(id={self.id}, material_code='{self.material_code}', name='{self.name}')>"


class SupplierEvaluation(Base):
    __tablename__ = "supplier_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    evaluation_period = Column(String(50), nullable=False)  # e.g., "Q1 2024"
    evaluation_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(EvaluationStatus), nullable=False, default=EvaluationStatus.PENDING)
    
    # Evaluation criteria scores (1-5 scale)
    quality_score = Column(Float)
    delivery_score = Column(Float)
    price_score = Column(Float)
    communication_score = Column(Float)
    technical_support_score = Column(Float)
    hygiene_score = Column(Float)  # Added hygiene score
    overall_score = Column(Float)
    
    # Detailed evaluation
    quality_comments = Column(Text)
    delivery_comments = Column(Text)
    price_comments = Column(Text)
    communication_comments = Column(Text)
    technical_support_comments = Column(Text)
    hygiene_comments = Column(Text)  # Added hygiene comments
    
    # Issues and improvements
    issues_identified = Column(Text)  # JSON array of issues
    improvement_actions = Column(Text)  # JSON array of improvement actions
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime(timezone=True))
    
    # Assignment
    evaluated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="evaluations")
    
    def __repr__(self):
        return f"<SupplierEvaluation(id={self.id}, supplier_id={self.supplier_id}, period='{self.evaluation_period}')>"


class IncomingDelivery(Base):
    __tablename__ = "incoming_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    delivery_number = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    
    # Delivery details
    delivery_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    quantity_received = Column(Float, nullable=False)
    unit = Column(String(20))
    batch_number = Column(String(50))
    lot_number = Column(String(50))
    
    # Quality information
    coa_number = Column(String(50))  # Certificate of Analysis
    coa_file_path = Column(String(500))
    inspection_status = Column(String(20), default="pending")  # pending, passed, failed, quarantined
    inspection_date = Column(DateTime(timezone=True))
    inspected_by = Column(Integer, ForeignKey("users.id"))
    
    # Inspection results
    inspection_results = Column(JSON)  # JSON object with inspection results
    non_conformances = Column(Text)  # JSON array of non-conformances
    corrective_actions = Column(Text)
    
    # Storage
    storage_location = Column(String(100))
    storage_conditions = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="deliveries")
    material = relationship("Material", back_populates="deliveries")
    
    def __repr__(self):
        return f"<IncomingDelivery(id={self.id}, delivery_number='{self.delivery_number}', supplier_id={self.supplier_id})>"


class InspectionChecklist(Base):
    __tablename__ = "inspection_checklists"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("incoming_deliveries.id"), nullable=False)
    
    # Checklist details
    checklist_name = Column(String(200), nullable=False)
    checklist_type = Column(String(100))  # visual, microbiological, chemical, etc.
    checklist_version = Column(String(20), default="1.0")
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_by = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime(timezone=True))
    
    # Results
    overall_result = Column(String(20))  # passed, failed, conditional
    total_items = Column(Integer, default=0)
    passed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Notes
    general_notes = Column(Text)
    corrective_actions = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    delivery = relationship("IncomingDelivery")
    checklist_items = relationship("InspectionChecklistItem", back_populates="checklist")
    
    def __repr__(self):
        return f"<InspectionChecklist(id={self.id}, delivery_id={self.delivery_id}, checklist_name='{self.checklist_name}')>"


class InspectionChecklistItem(Base):
    __tablename__ = "inspection_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("inspection_checklists.id"), nullable=False)
    
    # Item details
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text)
    item_category = Column(String(100))  # visual, measurement, test, etc.
    
    # Criteria
    acceptable_criteria = Column(Text)
    measurement_unit = Column(String(50))
    min_value = Column(Float)
    max_value = Column(Float)
    
    # Results
    is_checked = Column(Boolean, default=False)
    result = Column(String(20))  # passed, failed, n/a
    actual_value = Column(Float)
    actual_text = Column(Text)
    
    # Comments
    comments = Column(Text)
    corrective_action = Column(Text)
    
    # Timestamps
    checked_at = Column(DateTime(timezone=True))
    checked_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    checklist = relationship("InspectionChecklist", back_populates="checklist_items")
    
    def __repr__(self):
        return f"<InspectionChecklistItem(id={self.id}, checklist_id={self.checklist_id}, item_name='{self.item_name}')>"


class SupplierDocument(Base):
    __tablename__ = "supplier_documents"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # certificate, license, insurance, etc.
    document_name = Column(String(200), nullable=False)
    document_number = Column(String(100))
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    original_filename = Column(String(255))
    
    # Document details
    issue_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    issuing_authority = Column(String(200))
    
    # Status
    is_valid = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    supplier = relationship("Supplier")
    
    def __repr__(self):
        return f"<SupplierDocument(id={self.id}, supplier_id={self.supplier_id}, document_type='{self.document_type}')>" 