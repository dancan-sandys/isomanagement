from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class HazardType(str, enum.Enum):
    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"
    PHYSICAL = "physical"
    ALLERGEN = "allergen"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CCPStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # milk, yogurt, cheese, etc.
    formulation = Column(Text)  # JSON string of ingredients and proportions
    allergens = Column(Text)  # JSON array of allergens
    shelf_life_days = Column(Integer)
    storage_conditions = Column(Text)
    packaging_type = Column(String(100))
    
    # HACCP information
    haccp_plan_approved = Column(Boolean, default=False)
    haccp_plan_version = Column(String(20))
    haccp_plan_approved_by = Column(Integer, ForeignKey("users.id"))
    haccp_plan_approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    process_flows = relationship("ProcessFlow", back_populates="product")
    hazards = relationship("Hazard", back_populates="product")
    ccps = relationship("CCP", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, product_code='{self.product_code}', name='{self.name}')>"


class ProcessFlow(Base):
    __tablename__ = "process_flows"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    description = Column(Text)
    equipment = Column(String(100))
    temperature = Column(Float)
    time_minutes = Column(Float)
    ph = Column(Float)
    aw = Column(Float)  # Water activity
    
    # Process parameters
    parameters = Column(JSON)  # JSON object for additional parameters
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="process_flows")
    hazards = relationship("Hazard", back_populates="process_step")
    
    def __repr__(self):
        return f"<ProcessFlow(id={self.id}, product_id={self.product_id}, step='{self.step_name}')>"


class Hazard(Base):
    __tablename__ = "hazards"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    process_step_id = Column(Integer, ForeignKey("process_flows.id"), nullable=False)
    hazard_type = Column(Enum(HazardType), nullable=False)
    hazard_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Hazard analysis data capture (Principle 1)
    rationale = Column(Text)  # Reasoning for hazard identification and assessment
    prp_reference_ids = Column(JSON)  # Array of PRP/SOP document IDs that control this hazard
    references = Column(JSON)  # Array of reference documents (studies, regulations, etc.)
    
    # Risk assessment
    likelihood = Column(Integer)  # 1-5 scale
    severity = Column(Integer)  # 1-5 scale
    risk_score = Column(Integer)  # likelihood * severity
    risk_level = Column(Enum(RiskLevel))
    
    # Control measures
    control_measures = Column(Text)
    is_controlled = Column(Boolean, default=False)
    control_effectiveness = Column(Integer)  # 1-5 scale
    
    # CCP determination
    is_ccp = Column(Boolean, default=False)
    ccp_justification = Column(Text)
    # Persisted decision tree outcome (serialized JSON of DecisionTreeStep list)
    decision_tree_steps = Column(Text)
    decision_tree_run_at = Column(DateTime(timezone=True))
    decision_tree_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="hazards")
    process_step = relationship("ProcessFlow", back_populates="hazards")
    ccp = relationship("CCP", back_populates="hazard", uselist=False)
    
    def __repr__(self):
        return f"<Hazard(id={self.id}, hazard_name='{self.hazard_name}', type='{self.hazard_type}')>"


class CCP(Base):
    __tablename__ = "ccps"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    hazard_id = Column(Integer, ForeignKey("hazards.id"), nullable=False)
    ccp_number = Column(String(20), nullable=False)
    ccp_name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(CCPStatus), nullable=False, default=CCPStatus.ACTIVE)
    
    # Critical limits
    critical_limit_min = Column(Float)
    critical_limit_max = Column(Float)
    critical_limit_unit = Column(String(50))
    critical_limit_description = Column(Text)
    
    # Monitoring
    monitoring_frequency = Column(String(100))  # e.g., "Every 30 minutes"
    monitoring_method = Column(Text)
    monitoring_responsible = Column(Integer, ForeignKey("users.id"))
    monitoring_equipment = Column(String(100))
    
    # Corrective actions
    corrective_actions = Column(Text)
    
    # Verification
    verification_frequency = Column(String(100))
    verification_method = Column(Text)
    verification_responsible = Column(Integer, ForeignKey("users.id"))
    
    # Documentation
    monitoring_records = Column(Text)  # JSON array of record types
    verification_records = Column(Text)  # JSON array of record types
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="ccps")
    hazard = relationship("Hazard", back_populates="ccp")
    monitoring_logs = relationship("CCPMonitoringLog", back_populates="ccp")
    verification_logs = relationship("CCPVerificationLog", back_populates="ccp")
    
    def __repr__(self):
        return f"<CCP(id={self.id}, ccp_number='{self.ccp_number}', name='{self.ccp_name}')>"


class CCPMonitoringLog(Base):
    __tablename__ = "ccp_monitoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    ccp_id = Column(Integer, ForeignKey("ccps.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    batch_number = Column(String(50), nullable=False)
    monitoring_time = Column(DateTime(timezone=True), nullable=False)
    measured_value = Column(Float, nullable=False)
    unit = Column(String(20))
    is_within_limits = Column(Boolean, nullable=False)
    
    # Additional monitoring data
    additional_parameters = Column(JSON)  # JSON object for additional readings
    observations = Column(Text)
    
    # Evidence
    evidence_files = Column(Text)  # JSON array of file paths
    
    # Corrective action if needed
    corrective_action_taken = Column(Boolean, default=False)
    corrective_action_description = Column(Text)
    corrective_action_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    ccp = relationship("CCP", back_populates="monitoring_logs")
    
    def __repr__(self):
        return f"<CCPMonitoringLog(id={self.id}, ccp_id={self.ccp_id}, batch='{self.batch_number}')>"


class CCPVerificationLog(Base):
    __tablename__ = "ccp_verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    ccp_id = Column(Integer, ForeignKey("ccps.id"), nullable=False)
    verification_date = Column(DateTime(timezone=True), nullable=False)
    verification_method = Column(Text)
    verification_result = Column(Text)
    is_compliant = Column(Boolean, nullable=False)
    
    # Verification details
    samples_tested = Column(Integer)
    test_results = Column(Text)  # JSON object with test details
    equipment_calibration = Column(Boolean)
    calibration_date = Column(DateTime(timezone=True))
    
    # Evidence
    evidence_files = Column(Text)  # JSON array of file paths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    ccp = relationship("CCP", back_populates="verification_logs")
    
    def __repr__(self):
        return f"<CCPVerificationLog(id={self.id}, ccp_id={self.ccp_id}, date='{self.verification_date}')>" 


# HACCP Plan models (versioned with approvals, similar to Documents)
class HACCPPlanStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"


class HACCPPlan(Base):
    __tablename__ = "haccp_plans"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(HACCPPlanStatus), nullable=False, default=HACCPPlanStatus.DRAFT)
    version = Column(String(20), nullable=False, default="1.0")
    # Current content pointer is stored in latest version; duplicate here for convenience
    current_content = Column(Text)
    effective_date = Column(DateTime(timezone=True))
    review_date = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    versions = relationship("HACCPPlanVersion", back_populates="plan", cascade="all, delete-orphan")
    approvals = relationship("HACCPPlanApproval", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HACCPPlan(id={self.id}, product_id={self.product_id}, version='{self.version}', status='{self.status}')>"


class HACCPPlanVersion(Base):
    __tablename__ = "haccp_plan_versions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("haccp_plans.id"), nullable=False)
    version_number = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)  # Serialized JSON or rich text
    change_description = Column(Text)
    change_reason = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plan = relationship("HACCPPlan", back_populates="versions")

    def __repr__(self):
        return f"<HACCPPlanVersion(id={self.id}, plan_id={self.plan_id}, version='{self.version_number}')>"


class HACCPPlanApproval(Base):
    __tablename__ = "haccp_plan_approvals"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("haccp_plans.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_order = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    comments = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plan = relationship("HACCPPlan", back_populates="approvals")