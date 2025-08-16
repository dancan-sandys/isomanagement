from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime


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


class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Scope: site-wide, product-specific, or category-specific
    scope_type = Column(String(20), nullable=False)  # 'site', 'product', 'category'
    scope_id = Column(Integer, nullable=True)  # product_id or category_id, null for site-wide
    
    # Threshold configuration
    low_threshold = Column(Integer, nullable=False, default=4)  # Risk score <= this is LOW
    medium_threshold = Column(Integer, nullable=False, default=8)  # Risk score <= this is MEDIUM  
    high_threshold = Column(Integer, nullable=False, default=15)  # Risk score <= this is HIGH
    # Above high_threshold is CRITICAL
    
    # Likelihood and severity scales (1-5 by default)
    likelihood_scale = Column(Integer, nullable=False, default=5)
    severity_scale = Column(Integer, nullable=False, default=5)
    
    # Risk calculation method
    calculation_method = Column(String(20), nullable=False, default="multiplication")  # 'multiplication', 'addition', 'matrix'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    def __repr__(self):
        return f"<RiskThreshold(id={self.id}, name='{self.name}', scope='{self.scope_type}')>"
    
    def calculate_risk_level(self, likelihood: int, severity: int) -> RiskLevel:
        """Calculate risk level based on configured thresholds"""
        if self.calculation_method == "multiplication":
            risk_score = likelihood * severity
        elif self.calculation_method == "addition":
            risk_score = likelihood + severity
        elif self.calculation_method == "matrix":
            # Matrix-based calculation (could be more complex)
            risk_score = likelihood * severity
        else:
            # Default to multiplication
            risk_score = likelihood * severity
        
        if risk_score <= self.low_threshold:
            return RiskLevel.LOW
        elif risk_score <= self.medium_threshold:
            return RiskLevel.MEDIUM
        elif risk_score <= self.high_threshold:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL


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
    risk_config = relationship("ProductRiskConfig", back_populates="product", uselist=False)
    
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
    reviews = relationship("HazardReview", back_populates="hazard", cascade="all, delete-orphan")
    decision_tree = relationship("DecisionTree", back_populates="hazard", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Hazard(id={self.id}, hazard_name='{self.hazard_name}', type='{self.hazard_type}')>"


class HazardReview(Base):
    __tablename__ = "hazard_reviews"

    id = Column(Integer, primary_key=True, index=True)
    hazard_id = Column(Integer, ForeignKey("hazards.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review details
    review_status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    review_comments = Column(Text)
    review_date = Column(DateTime(timezone=True))
    
    # Review criteria
    hazard_identification_adequate = Column(Boolean, nullable=False)
    risk_assessment_appropriate = Column(Boolean, nullable=False)
    control_measures_suitable = Column(Boolean, nullable=False)
    ccp_determination_correct = Column(Boolean, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hazard = relationship("Hazard", back_populates="reviews")
    reviewer = relationship("User")
    
    def __repr__(self):
        return f"<HazardReview(id={self.id}, hazard_id={self.hazard_id}, reviewer_id={self.reviewer_id}, status='{self.review_status}')>"


class CCP(Base):
    __tablename__ = "ccps"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    hazard_id = Column(Integer, ForeignKey("hazards.id"), nullable=False)
    ccp_number = Column(String(20), nullable=False)
    ccp_name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(CCPStatus), nullable=False, default=CCPStatus.ACTIVE)
    
    # Enhanced Critical Limits - Multi-parameter support
    critical_limits = Column(JSON)  # JSON array of limit objects with parameters, values, units, and conditions
    # Example structure:
    # [
    #   {
    #     "parameter": "temperature",
    #     "min_value": 65.0,
    #     "max_value": 85.0,
    #     "unit": "Cel",  # UCUM unit
    #     "condition": "during_cooking",
    #     "limit_type": "numeric"
    #   },
    #   {
    #     "parameter": "time",
    #     "min_value": 15.0,
    #     "max_value": null,
    #     "unit": "min",  # UCUM unit
    #     "condition": "at_temperature_above_65C",
    #     "limit_type": "numeric"
    #   },
    #   {
    #     "parameter": "visual_inspection",
    #     "value": "no_foreign_material",
    #     "unit": null,
    #     "condition": "before_packaging",
    #     "limit_type": "qualitative"
    #   }
    # ]
    
    # Legacy fields for backward compatibility
    critical_limit_min = Column(Float)
    critical_limit_max = Column(Float)
    critical_limit_unit = Column(String(50))
    critical_limit_description = Column(Text)
    
    # Validation Evidence
    validation_evidence = Column(JSON)  # JSON array of evidence references
    # Example structure:
    # [
    #   {
    #     "type": "sop_reference",
    #     "document_id": 123,
    #     "section": "Cooking Procedures",
    #     "description": "Validated cooking time-temperature relationship"
    #   },
    #   {
    #     "type": "scientific_study",
    #     "reference": "Food Microbiology Journal, 2023",
    #     "study_id": "FMJ-2023-001",
    #     "description": "Pathogen reduction studies at various temperatures"
    #   },
    #   {
    #     "type": "process_authority_letter",
    #     "document_id": 456,
    #     "authority": "Dr. Smith, Food Safety Consultant",
    #     "date": "2023-01-15",
    #     "description": "Process validation for thermal treatment"
    #   }
    # ]
    
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
    
    def validate_limits(self, measured_values: dict) -> dict:
        """
        Validate measured values against critical limits
        Returns: dict with validation results for each parameter
        """
        if not self.critical_limits:
            return {"error": "No critical limits defined"}
        
        results = {}
        for limit in self.critical_limits:
            parameter = limit.get("parameter")
            limit_type = limit.get("limit_type", "numeric")
            
            if parameter not in measured_values:
                results[parameter] = {"valid": False, "error": "Parameter not measured"}
                continue
            
            measured_value = measured_values[parameter]
            
            if limit_type == "numeric":
                min_val = limit.get("min_value")
                max_val = limit.get("max_value")
                
                if min_val is not None and measured_value < min_val:
                    results[parameter] = {"valid": False, "error": f"Below minimum ({min_val})"}
                elif max_val is not None and measured_value > max_val:
                    results[parameter] = {"valid": False, "error": f"Above maximum ({max_val})"}
                else:
                    results[parameter] = {"valid": True}
                    
            elif limit_type == "qualitative":
                expected_value = limit.get("value")
                if measured_value != expected_value:
                    results[parameter] = {"valid": False, "error": f"Expected {expected_value}, got {measured_value}"}
                else:
                    results[parameter] = {"valid": True}
        
        return results
    
    def get_limits_summary(self) -> str:
        """Get a human-readable summary of critical limits"""
        if not self.critical_limits:
            return "No critical limits defined"
        
        summaries = []
        for limit in self.critical_limits:
            parameter = limit.get("parameter")
            limit_type = limit.get("limit_type", "numeric")
            
            if limit_type == "numeric":
                min_val = limit.get("min_value")
                max_val = limit.get("max_value")
                unit = limit.get("unit", "")
                
                if min_val is not None and max_val is not None:
                    summaries.append(f"{parameter}: {min_val}-{max_val} {unit}")
                elif min_val is not None:
                    summaries.append(f"{parameter}: ≥{min_val} {unit}")
                elif max_val is not None:
                    summaries.append(f"{parameter}: ≤{max_val} {unit}")
                    
            elif limit_type == "qualitative":
                value = limit.get("value")
                summaries.append(f"{parameter}: {value}")
        
        return "; ".join(summaries)
    
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


class ProductRiskConfig(Base):
    """Product-specific risk configuration for ISO 22000/HACCP compliance"""
    __tablename__ = "product_risk_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Risk calculation method
    calculation_method = Column(Enum("multiplication", "addition", "matrix", name="risk_calculation_method"), default="multiplication")
    
    # Scales for likelihood and severity
    likelihood_scale = Column(Integer, default=5)  # e.g., 1-5 scale
    severity_scale = Column(Integer, default=5)    # e.g., 1-5 scale
    
    # Risk thresholds for classification
    low_threshold = Column(Integer, default=4)
    medium_threshold = Column(Integer, default=8)
    high_threshold = Column(Integer, default=15)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="risk_config")
    creator = relationship("User")
    
    def calculate_risk_level(self, likelihood: int, severity: int) -> str:
        """Calculate risk level based on product-specific configuration"""
        if self.calculation_method == "multiplication":
            risk_score = likelihood * severity
        elif self.calculation_method == "addition":
            risk_score = likelihood + severity
        elif self.calculation_method == "matrix":
            # Matrix calculation (can be enhanced with custom matrix logic)
            risk_score = likelihood * severity
        else:
            risk_score = likelihood * severity  # Default to multiplication
        
        if risk_score <= self.low_threshold:
            return "low"
        elif risk_score <= self.medium_threshold:
            return "medium"
        else:
            return "high"
    
    def get_risk_score(self, likelihood: int, severity: int) -> int:
        """Get numeric risk score based on product-specific configuration"""
        if self.calculation_method == "multiplication":
            return likelihood * severity
        elif self.calculation_method == "addition":
            return likelihood + severity
        elif self.calculation_method == "matrix":
            return likelihood * severity  # Default matrix calculation
        else:
            return likelihood * severity


class DecisionTree(Base):
    """Codex Alimentarius Decision Tree for CCP determination"""
    __tablename__ = "decision_trees"
    
    id = Column(Integer, primary_key=True, index=True)
    hazard_id = Column(Integer, ForeignKey("hazards.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Question 1: Is control at this step necessary for safety?
    q1_answer = Column(Boolean, nullable=False)  # True = Yes, False = No
    q1_justification = Column(Text)
    q1_answered_by = Column(Integer, ForeignKey("users.id"))
    q1_answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Question 2: Is control at this step necessary to eliminate or reduce the likelihood of occurrence of a hazard to an acceptable level?
    q2_answer = Column(Boolean)  # True = Yes, False = No
    q2_justification = Column(Text)
    q2_answered_by = Column(Integer, ForeignKey("users.id"))
    q2_answered_at = Column(DateTime)
    
    # Question 3: Could contamination with identified hazard(s) occur or could this increase to unacceptable level(s)?
    q3_answer = Column(Boolean)  # True = Yes, False = No
    q3_justification = Column(Text)
    q3_answered_by = Column(Integer, ForeignKey("users.id"))
    q3_answered_at = Column(DateTime)
    
    # Question 4: Will a subsequent step eliminate or reduce the likelihood of occurrence of a hazard to an acceptable level?
    q4_answer = Column(Boolean)  # True = Yes, False = No
    q4_justification = Column(Text)
    q4_answered_by = Column(Integer, ForeignKey("users.id"))
    q4_answered_at = Column(DateTime)
    
    # Decision result
    is_ccp = Column(Boolean)  # Final CCP determination
    decision_reasoning = Column(Text)  # Explanation of the decision
    decision_date = Column(DateTime)
    decision_by = Column(Integer, ForeignKey("users.id"))
    
    # Status
    status = Column(Enum("in_progress", "completed", "reviewed", name="decision_tree_status"), default="in_progress")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hazard = relationship("Hazard", back_populates="decision_tree")
    q1_user = relationship("User", foreign_keys=[q1_answered_by])
    q2_user = relationship("User", foreign_keys=[q2_answered_by])
    q3_user = relationship("User", foreign_keys=[q3_answered_by])
    q4_user = relationship("User", foreign_keys=[q4_answered_by])
    decision_user = relationship("User", foreign_keys=[decision_by])
    
    def get_current_question(self) -> int:
        """Get the next question that needs to be answered"""
        if self.q1_answer is None:
            return 1
        elif self.q2_answer is None:
            return 2
        elif self.q3_answer is None:
            return 3
        elif self.q4_answer is None:
            return 4
        else:
            return 0  # All questions answered
    
    def can_proceed_to_next_question(self) -> bool:
        """Check if we can proceed to the next question based on current answers"""
        if self.q1_answer is False:  # If Q1 is No, stop here
            return False
        if self.q2_answer is False:  # If Q2 is No, stop here
            return False
        if self.q3_answer is False:  # If Q3 is No, stop here
            return False
        return True
    
    def determine_ccp_decision(self) -> tuple[bool, str]:
        """
        Determine CCP decision based on Codex Alimentarius decision tree
        Returns: (is_ccp, reasoning)
        """
        if self.q1_answer is False:
            return False, "Q1: Control at this step is not necessary for safety"
        
        if self.q2_answer is False:
            return False, "Q2: Control at this step is not necessary to eliminate or reduce hazard likelihood"
        
        if self.q3_answer is False:
            return False, "Q3: Contamination with identified hazard(s) could not occur or increase to unacceptable levels"
        
        if self.q4_answer is True:
            return False, "Q4: A subsequent step will eliminate or reduce the hazard likelihood to acceptable levels"
        
        # If we reach here, it's a CCP
        return True, "All questions answered affirmatively - this is a Critical Control Point"