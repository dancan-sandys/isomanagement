from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RiskItemType(str, enum.Enum):
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class RiskCategory(str, enum.Enum):
    # Operational Categories (existing)
    PROCESS = "process"
    SUPPLIER = "supplier"
    STAFF = "staff"
    ENVIRONMENT = "environment"
    HACCP = "haccp"
    PRP = "prp"
    DOCUMENT = "document"
    TRAINING = "training"
    EQUIPMENT = "equipment"
    COMPLIANCE = "compliance"
    CUSTOMER = "customer"
    OTHER = "other"
    
    # Strategic Categories (new)
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"
    BUSINESS_CONTINUITY = "business_continuity"
    REGULATORY = "regulatory"


class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLikelihood(str, enum.Enum):
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"


class RiskClassification(str, enum.Enum):
    FOOD_SAFETY = "food_safety"
    BUSINESS = "business"
    CUSTOMER = "customer"


class RiskDetectability(str, enum.Enum):
    EASILY_DETECTABLE = "easily_detectable"
    MODERATELY_DETECTABLE = "moderately_detectable"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"
    ALMOST_UNDETECTABLE = "almost_undetectable"


class RiskRegisterItem(Base):
    __tablename__ = "risk_register"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(Enum(RiskItemType), nullable=False)
    risk_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    category = Column(Enum(RiskCategory), nullable=False, default=RiskCategory.OTHER)
    classification = Column(Enum(RiskClassification), nullable=True)
    status = Column(Enum(RiskStatus), nullable=False, default=RiskStatus.OPEN)

    severity = Column(Enum(RiskSeverity), nullable=True)
    likelihood = Column(Enum(RiskLikelihood), nullable=True)
    detectability = Column(Enum(RiskDetectability), nullable=True)
    impact_score = Column(Integer, nullable=True)  # optional numeric 1-5
    risk_score = Column(Integer, nullable=False, default=1)  # for risks: S*L*(D); for opportunities: mirrors opportunity_score

    # Opportunity-specific evaluation (ISO allows org-defined criteria; we use Benefit x Feasibility)
    opportunity_benefit = Column(Integer, nullable=True)       # 1-5
    opportunity_feasibility = Column(Integer, nullable=True)   # 1-5
    opportunity_score = Column(Integer, nullable=True)         # benefit * feasibility

    mitigation_plan = Column(Text, nullable=True)
    residual_risk = Column(String(100), nullable=True)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)

    # Optional references by string (e.g., "document:123", "batch:45") to avoid cross-deps
    references = Column(Text, nullable=True)

    # Enhanced Risk Assessment Fields
    risk_context_id = Column(Integer, ForeignKey("risk_context.id"), nullable=True)
    risk_criteria_id = Column(Integer, nullable=True)
    risk_assessment_method = Column(String(100), nullable=True)
    risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    risk_assessor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_assessment_reviewed = Column(Boolean, default=False)
    risk_assessment_reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_assessment_review_date = Column(DateTime(timezone=True), nullable=True)

    # Enhanced Risk Treatment Fields
    risk_treatment_strategy = Column(String(100), nullable=True)
    risk_treatment_plan = Column(Text, nullable=True)
    risk_treatment_cost = Column(Float, nullable=True)
    risk_treatment_benefit = Column(Float, nullable=True)
    risk_treatment_timeline = Column(String(100), nullable=True)
    risk_treatment_approved = Column(Boolean, default=False)
    risk_treatment_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_treatment_approval_date = Column(DateTime(timezone=True), nullable=True)

    # Residual Risk Fields
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_level = Column(String(50), nullable=True)
    residual_risk_acceptable = Column(Boolean, nullable=True)
    residual_risk_justification = Column(Text, nullable=True)

    # Monitoring and Review Fields
    monitoring_frequency = Column(String(100), nullable=True)
    next_monitoring_date = Column(DateTime(timezone=True), nullable=True)
    monitoring_method = Column(String(100), nullable=True)
    monitoring_responsible = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_frequency = Column(String(100), nullable=True)
    review_responsible = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    review_outcome = Column(Text, nullable=True)

    # Strategic Risk Fields
    strategic_impact = Column(Text, nullable=True)
    business_unit = Column(String(100), nullable=True)
    project_association = Column(String(100), nullable=True)
    stakeholder_impact = Column(JSON, nullable=True)
    market_impact = Column(Text, nullable=True)
    competitive_impact = Column(Text, nullable=True)
    regulatory_impact = Column(Text, nullable=True)
    financial_impact = Column(JSON, nullable=True)
    operational_impact = Column(JSON, nullable=True)
    reputational_impact = Column(Text, nullable=True)
    risk_velocity = Column(String(50), nullable=True)  # slow, medium, fast
    risk_persistence = Column(String(50), nullable=True)  # temporary, persistent, permanent
    risk_contagion = Column(Boolean, nullable=True)  # Can it spread to other areas
    risk_cascade = Column(Boolean, nullable=True)  # Can it trigger other risks
    risk_amplification = Column(Boolean, nullable=True)  # Can it amplify other risks

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    actions = relationship("RiskAction", back_populates="item", cascade="all, delete-orphan")
    risk_context = relationship("RiskContext", foreign_keys=[risk_context_id])
    assessor = relationship("User", foreign_keys=[risk_assessor_id])
    assessment_reviewer = relationship("User", foreign_keys=[risk_assessment_reviewer_id])
    treatment_approver = relationship("User", foreign_keys=[risk_treatment_approver_id])
    monitoring_responsible_user = relationship("User", foreign_keys=[monitoring_responsible])
    review_responsible_user = relationship("User", foreign_keys=[review_responsible])
    fsms_integrations = relationship("FSMSRiskIntegration", foreign_keys="FSMSRiskIntegration.risk_register_item_id", cascade="all, delete-orphan")
    correlations = relationship("RiskCorrelation", foreign_keys="RiskCorrelation.primary_risk_id", cascade="all, delete-orphan")
    resource_allocations = relationship("RiskResourceAllocation", foreign_keys="RiskResourceAllocation.risk_register_item_id", cascade="all, delete-orphan")
    communications = relationship("RiskCommunication", foreign_keys="RiskCommunication.risk_register_item_id", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RiskRegisterItem(id={self.id}, number='{self.risk_number}', type='{self.item_type}')>"


class RiskAction(Base):
    __tablename__ = "risk_actions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("RiskRegisterItem", back_populates="actions")

    def __repr__(self):
        return f"<RiskAction(id={self.id}, item_id={self.item_id}, title='{self.title}')>"


class RiskManagementFramework(Base):
    __tablename__ = "risk_management_framework"

    id = Column(Integer, primary_key=True, index=True)
    policy_statement = Column(Text, nullable=False)
    risk_appetite_statement = Column(Text, nullable=False)
    risk_tolerance_levels = Column(JSON, nullable=False)
    risk_criteria = Column(JSON, nullable=False)
    risk_assessment_methodology = Column(Text, nullable=False)
    risk_treatment_strategies = Column(JSON, nullable=False)
    monitoring_review_frequency = Column(Text, nullable=False)
    communication_plan = Column(Text, nullable=False)
    review_cycle = Column(String(50), nullable=False)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    approver = relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<RiskManagementFramework(id={self.id})>"


class RiskContext(Base):
    __tablename__ = "risk_context"

    id = Column(Integer, primary_key=True, index=True)
    organizational_context = Column(Text, nullable=False)
    external_context = Column(Text, nullable=False)
    internal_context = Column(Text, nullable=False)
    risk_management_context = Column(Text, nullable=False)
    stakeholder_analysis = Column(JSON, nullable=False)
    risk_criteria = Column(JSON, nullable=False)
    review_frequency = Column(String(50), nullable=False)
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<RiskContext(id={self.id})>"


class FSMSRiskIntegration(Base):
    __tablename__ = "fsms_risk_integration"

    id = Column(Integer, primary_key=True, index=True)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    fsms_element = Column(String(100), nullable=False)
    fsms_element_id = Column(Integer, nullable=True)
    impact_on_fsms = Column(Text, nullable=False)
    food_safety_objective_id = Column(Integer, ForeignKey("food_safety_objectives.id"), nullable=True)
    interested_party_impact = Column(JSON, nullable=True)
    compliance_requirement = Column(Text, nullable=True)
    integration_date = Column(DateTime(timezone=True), server_default=func.now())
    integrated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations,resource_allocations,communications", foreign_keys=[risk_register_item_id])
    food_safety_objective = relationship("FoodSafetyObjective", foreign_keys=[food_safety_objective_id])
    integrated_by_user = relationship("User", foreign_keys=[integrated_by])

    def __repr__(self):
        return f"<FSMSRiskIntegration(id={self.id}, risk_id={self.risk_register_item_id})>"


class RiskCorrelation(Base):
    __tablename__ = "risk_correlations"

    id = Column(Integer, primary_key=True, index=True)
    primary_risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    correlated_risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    correlation_type = Column(String(100), nullable=True)
    correlation_strength = Column(Integer, nullable=True)
    correlation_description = Column(Text, nullable=True)
    correlation_date = Column(DateTime(timezone=True), server_default=func.now())
    identified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    primary_risk = relationship("RiskRegisterItem", foreign_keys=[primary_risk_id])
    correlated_risk = relationship("RiskRegisterItem", foreign_keys=[correlated_risk_id])
    identified_by_user = relationship("User", foreign_keys=[identified_by])

    def __repr__(self):
        return f"<RiskCorrelation(id={self.id}, primary={self.primary_risk_id}, correlated={self.correlated_risk_id})>"


class RiskResourceAllocation(Base):
    __tablename__ = "risk_resource_allocation"

    id = Column(Integer, primary_key=True, index=True)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_amount = Column(Float, nullable=True)
    resource_unit = Column(String(50), nullable=True)
    allocation_justification = Column(Text, nullable=True)
    allocation_approved = Column(Boolean, default=False)
    allocation_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    allocation_date = Column(DateTime(timezone=True), nullable=True)
    allocation_period = Column(String(100), nullable=True)

    # Relationships
    risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations,resource_allocations,communications", foreign_keys=[risk_register_item_id])
    approver = relationship("User", foreign_keys=[allocation_approver_id])

    def __repr__(self):
        return f"<RiskResourceAllocation(id={self.id}, risk_id={self.risk_register_item_id})>"


class RiskCommunication(Base):
    __tablename__ = "risk_communications"

    id = Column(Integer, primary_key=True, index=True)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    communication_type = Column(String(100), nullable=True)
    communication_channel = Column(String(100), nullable=True)
    target_audience = Column(JSON, nullable=True)
    communication_content = Column(Text, nullable=True)
    communication_schedule = Column(String(100), nullable=True)
    communication_status = Column(String(100), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    delivery_confirmation = Column(Boolean, default=False)

    # Relationships
    risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations,resource_allocations,communications", foreign_keys=[risk_register_item_id])
    sent_by_user = relationship("User", foreign_keys=[sent_by])

    def __repr__(self):
        return f"<RiskCommunication(id={self.id}, risk_id={self.risk_register_item_id})>"


class RiskKPI(Base):
    __tablename__ = "risk_kpis"

    id = Column(Integer, primary_key=True, index=True)
    kpi_name = Column(String(200), nullable=False)
    kpi_description = Column(Text, nullable=True)
    kpi_category = Column(String(100), nullable=True)
    kpi_formula = Column(Text, nullable=True)
    kpi_target = Column(Float, nullable=True)
    kpi_current_value = Column(Float, nullable=True)
    kpi_unit = Column(String(50), nullable=True)
    kpi_frequency = Column(String(100), nullable=True)
    kpi_owner = Column(Integer, ForeignKey("users.id"), nullable=True)
    kpi_status = Column(String(100), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    next_update = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("User", foreign_keys=[kpi_owner])

    def __repr__(self):
        return f"<RiskKPI(id={self.id}, name='{self.kpi_name}')>"


