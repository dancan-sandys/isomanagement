from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RiskItemType(str, Enum):
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class RiskCategory(str, Enum):
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


class RiskStatus(str, Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLikelihood(str, Enum):
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"


class RiskClassification(str, Enum):
    FOOD_SAFETY = "food_safety"
    BUSINESS = "business"
    CUSTOMER = "customer"


class RiskDetectability(str, Enum):
    EASILY_DETECTABLE = "easily_detectable"
    MODERATELY_DETECTABLE = "moderately_detectable"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"
    ALMOST_UNDETECTABLE = "almost_undetectable"


class RiskActionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class RiskActionResponse(BaseModel):
    id: int
    item_id: int
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskActionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


class RiskItemCreate(BaseModel):
    item_type: RiskItemType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: RiskCategory = RiskCategory.OTHER
    classification: Optional[RiskClassification] = None
    # Risk-only fields
    severity: Optional[RiskSeverity] = RiskSeverity.LOW
    likelihood: Optional[RiskLikelihood] = RiskLikelihood.UNLIKELY
    detectability: Optional[RiskDetectability] = None
    impact_score: Optional[int] = Field(None, ge=1, le=5)
    risk_score: Optional[int] = Field(None, ge=1, le=125)
    # Opportunity-only fields
    opportunity_benefit: Optional[int] = Field(None, ge=1, le=5)
    opportunity_feasibility: Optional[int] = Field(None, ge=1, le=5)
    opportunity_score: Optional[int] = Field(None, ge=1, le=25)
    mitigation_plan: Optional[str] = None
    residual_risk: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    references: Optional[str] = None


class RiskItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[RiskCategory] = None
    classification: Optional[RiskClassification] = None
    status: Optional[RiskStatus] = None
    severity: Optional[RiskSeverity] = None
    likelihood: Optional[RiskLikelihood] = None
    detectability: Optional[RiskDetectability] = None
    impact_score: Optional[int] = Field(None, ge=1, le=5)
    risk_score: Optional[int] = Field(None, ge=1, le=125)
    opportunity_benefit: Optional[int] = Field(None, ge=1, le=5)
    opportunity_feasibility: Optional[int] = Field(None, ge=1, le=5)
    opportunity_score: Optional[int] = Field(None, ge=1, le=25)
    mitigation_plan: Optional[str] = None
    residual_risk: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    references: Optional[str] = None


class RiskItemResponse(BaseModel):
    id: int
    risk_number: str
    item_type: RiskItemType
    title: str
    description: Optional[str] = None
    category: RiskCategory
    classification: Optional[RiskClassification] = None
    status: RiskStatus
    severity: Optional[RiskSeverity] = None
    likelihood: Optional[RiskLikelihood] = None
    detectability: Optional[RiskDetectability] = None
    impact_score: Optional[int] = None
    risk_score: int
    opportunity_benefit: Optional[int] = None
    opportunity_feasibility: Optional[int] = None
    opportunity_score: Optional[int] = None
    mitigation_plan: Optional[str] = None
    residual_risk: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    references: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RiskFilter(BaseModel):
    search: Optional[str] = None
    item_type: Optional[RiskItemType] = None
    category: Optional[RiskCategory] = None
    classification: Optional[RiskClassification] = None
    status: Optional[RiskStatus] = None
    severity: Optional[RiskSeverity] = None
    likelihood: Optional[RiskLikelihood] = None
    detectability: Optional[RiskDetectability] = None
    assigned_to: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class RiskStats(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    by_item_type: Dict[str, int]


# ============================================================================
# ISO 31000:2018 RISK MANAGEMENT FRAMEWORK SCHEMAS
# ============================================================================

class RiskManagementFrameworkCreate(BaseModel):
    policy_statement: str = Field(..., min_length=10, description="Risk management policy statement")
    risk_appetite_statement: str = Field(..., min_length=10, description="Organization's risk appetite")
    risk_tolerance_levels: Dict[str, Any] = Field(..., description="Risk tolerance levels configuration")
    risk_criteria: Dict[str, Any] = Field(..., description="Risk assessment criteria")
    risk_assessment_methodology: str = Field(..., min_length=10, description="Risk assessment methodology")
    risk_treatment_strategies: Dict[str, Any] = Field(..., description="Risk treatment strategies")
    monitoring_review_frequency: str = Field(..., description="Monitoring and review frequency")
    communication_plan: str = Field(..., min_length=10, description="Risk communication plan")
    review_cycle: str = Field(..., description="Framework review cycle (monthly, quarterly, annually)")
    next_review_date: Optional[datetime] = None


class RiskManagementFrameworkUpdate(BaseModel):
    policy_statement: Optional[str] = Field(None, min_length=10)
    risk_appetite_statement: Optional[str] = Field(None, min_length=10)
    risk_tolerance_levels: Optional[Dict[str, Any]] = None
    risk_criteria: Optional[Dict[str, Any]] = None
    risk_assessment_methodology: Optional[str] = Field(None, min_length=10)
    risk_treatment_strategies: Optional[Dict[str, Any]] = None
    monitoring_review_frequency: Optional[str] = None
    communication_plan: Optional[str] = Field(None, min_length=10)
    review_cycle: Optional[str] = None
    next_review_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None


class RiskManagementFrameworkResponse(BaseModel):
    id: int
    policy_statement: str
    risk_appetite_statement: str
    risk_tolerance_levels: Dict[str, Any]
    risk_criteria: Dict[str, Any]
    risk_assessment_methodology: str
    risk_treatment_strategies: Dict[str, Any]
    monitoring_review_frequency: str
    communication_plan: str
    review_cycle: str
    next_review_date: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ============================================================================
# RISK CONTEXT SCHEMAS
# ============================================================================

class RiskContextCreate(BaseModel):
    organizational_context: str = Field(..., min_length=10, description="Organizational context description")
    external_context: str = Field(..., min_length=10, description="External context factors")
    internal_context: str = Field(..., min_length=10, description="Internal context factors")
    risk_management_context: str = Field(..., min_length=10, description="Risk management specific context")
    stakeholder_analysis: Dict[str, Any] = Field(..., description="Stakeholder analysis results")
    risk_criteria: Dict[str, Any] = Field(..., description="Context-specific risk criteria")
    review_frequency: str = Field(..., description="Context review frequency")
    next_review_date: Optional[datetime] = None


class RiskContextUpdate(BaseModel):
    organizational_context: Optional[str] = Field(None, min_length=10)
    external_context: Optional[str] = Field(None, min_length=10)
    internal_context: Optional[str] = Field(None, min_length=10)
    risk_management_context: Optional[str] = Field(None, min_length=10)
    stakeholder_analysis: Optional[Dict[str, Any]] = None
    risk_criteria: Optional[Dict[str, Any]] = None
    review_frequency: Optional[str] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None


class RiskContextResponse(BaseModel):
    id: int
    organizational_context: str
    external_context: str
    internal_context: str
    risk_management_context: str
    stakeholder_analysis: Dict[str, Any]
    risk_criteria: Dict[str, Any]
    review_frequency: str
    last_review_date: Optional[datetime]
    next_review_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ============================================================================
# FSMS RISK INTEGRATION SCHEMAS
# ============================================================================

class FSMSRiskIntegrationCreate(BaseModel):
    risk_register_item_id: int
    fsms_element: str = Field(..., description="FSMS element (policy, objectives, processes, etc.)")
    fsms_element_id: Optional[int] = None
    impact_on_fsms: str = Field(..., min_length=10, description="Impact on FSMS description")
    food_safety_objective_id: Optional[int] = None
    interested_party_impact: Optional[Dict[str, Any]] = None
    compliance_requirement: Optional[str] = None


class FSMSRiskIntegrationResponse(BaseModel):
    id: int
    risk_register_item_id: int
    fsms_element: str
    fsms_element_id: Optional[int]
    impact_on_fsms: str
    food_safety_objective_id: Optional[int]
    interested_party_impact: Optional[Dict[str, Any]]
    compliance_requirement: Optional[str]
    integration_date: datetime
    integrated_by: Optional[int]

    model_config = {"from_attributes": True}


# ============================================================================
# RISK ASSESSMENT SCHEMAS
# ============================================================================

class RiskAssessmentCreate(BaseModel):
    risk_id: int
    risk_context_id: Optional[int] = None
    assessment_method: str = Field(..., description="Assessment methodology used")
    assessor_id: int
    assessment_data: Dict[str, Any] = Field(..., description="Assessment results and data")


class RiskAssessmentResponse(BaseModel):
    risk_id: int
    risk_context_id: Optional[int]
    risk_assessment_method: Optional[str]
    risk_assessment_date: Optional[datetime]
    risk_assessor_id: Optional[int]
    risk_assessment_reviewed: bool
    risk_assessment_reviewer_id: Optional[int]
    risk_assessment_review_date: Optional[datetime]

    model_config = {"from_attributes": True}


# ============================================================================
# RISK TREATMENT SCHEMAS
# ============================================================================

class RiskTreatmentCreate(BaseModel):
    risk_id: int
    treatment_strategy: str = Field(..., description="Treatment strategy: avoid, transfer, mitigate, accept")
    treatment_plan: str = Field(..., min_length=10, description="Detailed treatment plan")
    treatment_cost: Optional[float] = None
    treatment_benefit: Optional[float] = None
    treatment_timeline: Optional[str] = None


class RiskTreatmentResponse(BaseModel):
    risk_id: int
    risk_treatment_strategy: Optional[str]
    risk_treatment_plan: Optional[str]
    risk_treatment_cost: Optional[float]
    risk_treatment_benefit: Optional[float]
    risk_treatment_timeline: Optional[str]
    risk_treatment_approved: bool
    risk_treatment_approver_id: Optional[int]
    risk_treatment_approval_date: Optional[datetime]

    model_config = {"from_attributes": True}


# ============================================================================
# RISK ANALYTICS SCHEMAS
# ============================================================================

class RiskDashboardData(BaseModel):
    risk_summary: Dict[str, Any]
    risk_trends: List[Dict[str, Any]]
    risk_distribution: Dict[str, Any]
    risk_performance: Dict[str, Any]
    risk_alerts: List[Dict[str, Any]]
    risk_opportunities: List[Dict[str, Any]]


class RiskAnalyticsFilter(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category: Optional[RiskCategory] = None
    severity: Optional[RiskSeverity] = None
    status: Optional[RiskStatus] = None
    include_opportunities: bool = True


# ============================================================================
# RISK KPI SCHEMAS
# ============================================================================

class RiskKPICreate(BaseModel):
    kpi_name: str = Field(..., min_length=1, max_length=200)
    kpi_description: Optional[str] = None
    kpi_category: str = Field(..., description="Category: risk_identification, risk_assessment, risk_treatment, risk_monitoring")
    kpi_formula: Optional[str] = None
    kpi_target: Optional[float] = None
    kpi_unit: Optional[str] = None
    kpi_frequency: str = Field(..., description="Measurement frequency")
    kpi_owner: int


class RiskKPIResponse(BaseModel):
    id: int
    kpi_name: str
    kpi_description: Optional[str]
    kpi_category: str
    kpi_formula: Optional[str]
    kpi_target: Optional[float]
    kpi_current_value: Optional[float]
    kpi_unit: Optional[str]
    kpi_frequency: str
    kpi_owner: int
    kpi_status: Optional[str]
    last_updated: Optional[datetime]
    next_update: Optional[datetime]

    model_config = {"from_attributes": True}


