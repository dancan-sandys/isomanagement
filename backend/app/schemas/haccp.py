from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class HazardType(str, Enum):
    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"
    PHYSICAL = "physical"
    ALLERGEN = "allergen"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CCPStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class DecisionTreeQuestion(str, Enum):
    Q1 = "Is control at this step necessary for safety?"
    Q2 = "Is it likely that contamination with identified hazard(s) may occur or increase to unacceptable level(s)?"
    Q3 = "Will a subsequent step eliminate or reduce the likely occurrence of a hazard to an acceptable level?"
    Q4 = "Is this step specifically designed to eliminate or reduce the likely occurrence of the hazard to an acceptable level?"


# Risk Assessment Schemas
class RiskThresholdCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    scope_type: str = Field(..., pattern="^(site|product|category)$")
    scope_id: Optional[int] = None
    low_threshold: int = Field(..., ge=1, le=25)
    medium_threshold: int = Field(..., ge=1, le=25)
    high_threshold: int = Field(..., ge=1, le=25)
    likelihood_scale: int = Field(5, ge=1, le=10)
    severity_scale: int = Field(5, ge=1, le=10)
    calculation_method: str = Field("multiplication", pattern="^(multiplication|addition|matrix)$")

    @field_validator('medium_threshold')
    @classmethod
    def validate_medium_threshold(cls, v, info):
        if 'low_threshold' in info.data and v <= info.data['low_threshold']:
            raise ValueError('medium_threshold must be greater than low_threshold')
        return v

    @field_validator('high_threshold')
    @classmethod
    def validate_high_threshold(cls, v, info):
        if 'medium_threshold' in info.data and v <= info.data['medium_threshold']:
            raise ValueError('high_threshold must be greater than medium_threshold')
        return v


class RiskThresholdUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    low_threshold: Optional[int] = Field(None, ge=1, le=25)
    medium_threshold: Optional[int] = Field(None, ge=1, le=25)
    high_threshold: Optional[int] = Field(None, ge=1, le=25)
    likelihood_scale: Optional[int] = Field(None, ge=1, le=10)
    severity_scale: Optional[int] = Field(None, ge=1, le=10)
    calculation_method: Optional[str] = Field(None, pattern="^(multiplication|addition|matrix)$")


class RiskThresholdResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    scope_type: str
    scope_id: Optional[int] = None
    low_threshold: int
    medium_threshold: int
    high_threshold: int
    likelihood_scale: int
    severity_scale: int
    calculation_method: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int

    model_config = {"from_attributes": True}


# Hazard Review Schemas
class HazardReviewCreate(BaseModel):
    hazard_id: int
    reviewer_id: int
    review_status: str = Field("pending", pattern="^(pending|approved|rejected)$")
    review_comments: Optional[str] = None
    hazard_identification_adequate: bool
    risk_assessment_appropriate: bool
    control_measures_suitable: bool
    ccp_determination_correct: bool


class HazardReviewUpdate(BaseModel):
    review_status: Optional[str] = Field(None, pattern="^(pending|approved|rejected)$")
    review_comments: Optional[str] = None
    hazard_identification_adequate: Optional[bool] = None
    risk_assessment_appropriate: Optional[bool] = None
    control_measures_suitable: Optional[bool] = None
    ccp_determination_correct: Optional[bool] = None


class HazardReviewResponse(BaseModel):
    id: int
    hazard_id: int
    reviewer_id: int
    review_status: str
    review_comments: Optional[str] = None
    review_date: Optional[datetime] = None
    hazard_identification_adequate: bool
    risk_assessment_appropriate: bool
    control_measures_suitable: bool
    ccp_determination_correct: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    reviewer_name: Optional[str] = None

    model_config = {"from_attributes": True}


# Product Management Schemas
class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    formulation: Optional[str] = None
    allergens: Optional[str] = None
    shelf_life_days: Optional[int] = Field(None, ge=1)
    storage_conditions: Optional[str] = None
    packaging_type: Optional[str] = Field(None, max_length=100)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    formulation: Optional[str] = None
    allergens: Optional[str] = None
    shelf_life_days: Optional[int] = Field(None, ge=1)
    storage_conditions: Optional[str] = None
    packaging_type: Optional[str] = Field(None, max_length=100)
    haccp_plan_approved: Optional[bool] = None
    haccp_plan_version: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    product_code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    formulation: Optional[str] = None
    allergens: Optional[str] = None
    shelf_life_days: Optional[int] = None
    storage_conditions: Optional[str] = None
    packaging_type: Optional[str] = None
    haccp_plan_approved: bool
    haccp_plan_version: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Process Flow Schemas
class ProcessFlowCreate(BaseModel):
    step_number: int = Field(..., ge=1)
    step_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    equipment: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = None
    time_minutes: Optional[float] = Field(None, ge=0)
    ph: Optional[float] = Field(None, ge=0, le=14)
    aw: Optional[float] = Field(None, ge=0, le=1)
    parameters: Optional[Dict[str, Any]] = None


class ProcessFlowUpdate(BaseModel):
    step_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    equipment: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = None
    time_minutes: Optional[float] = Field(None, ge=0)
    ph: Optional[float] = Field(None, ge=0, le=14)
    aw: Optional[float] = Field(None, ge=0, le=1)
    parameters: Optional[Dict[str, Any]] = None


class ProcessFlowResponse(BaseModel):
    id: int
    step_number: int
    step_name: str
    description: Optional[str] = None
    equipment: Optional[str] = None
    temperature: Optional[float] = None
    time_minutes: Optional[float] = None
    ph: Optional[float] = None
    aw: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Hazard Schemas
class HazardCreate(BaseModel):
    process_step_id: int
    hazard_type: HazardType
    hazard_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    rationale: Optional[str] = None  # Reasoning for hazard identification and assessment
    prp_reference_ids: Optional[List[int]] = None  # Array of PRP/SOP document IDs
    references: Optional[List[Dict[str, Any]]] = None  # Array of reference documents
    likelihood: int = Field(..., ge=1, le=5)
    severity: int = Field(..., ge=1, le=5)
    control_measures: Optional[str] = None
    is_controlled: bool = False
    control_effectiveness: Optional[int] = Field(None, ge=1, le=5)
    is_ccp: bool = False
    ccp_justification: Optional[str] = None


class HazardUpdate(BaseModel):
    hazard_type: Optional[HazardType] = None
    hazard_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    rationale: Optional[str] = None  # Reasoning for hazard identification and assessment
    prp_reference_ids: Optional[List[int]] = None  # Array of PRP/SOP document IDs
    references: Optional[List[Dict[str, Any]]] = None  # Array of reference documents
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    severity: Optional[int] = Field(None, ge=1, le=5)
    control_measures: Optional[str] = None
    is_controlled: Optional[bool] = None
    control_effectiveness: Optional[int] = Field(None, ge=1, le=5)
    is_ccp: Optional[bool] = None
    ccp_justification: Optional[str] = None


class HazardResponse(BaseModel):
    id: int
    process_step_id: int
    hazard_type: HazardType
    hazard_name: str
    description: Optional[str] = None
    rationale: Optional[str] = None  # Reasoning for hazard identification and assessment
    prp_reference_ids: Optional[List[int]] = None  # Array of PRP/SOP document IDs
    references: Optional[List[Dict[str, Any]]] = None  # Array of reference documents
    likelihood: int
    severity: int
    risk_score: int
    risk_level: RiskLevel
    control_measures: Optional[str] = None
    is_controlled: bool
    control_effectiveness: Optional[int] = None
    is_ccp: bool
    ccp_justification: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# CCP Schemas
class CCPCreate(BaseModel):
    hazard_id: int
    ccp_number: str = Field(..., min_length=1, max_length=20)
    ccp_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    critical_limit_min: Optional[float] = None
    critical_limit_max: Optional[float] = None
    critical_limit_unit: Optional[str] = Field(None, max_length=50)
    critical_limit_description: Optional[str] = None
    monitoring_frequency: Optional[str] = Field(None, max_length=100)
    monitoring_method: Optional[str] = None
    monitoring_responsible: Optional[int] = None
    monitoring_equipment: Optional[str] = Field(None, max_length=100)
    corrective_actions: Optional[str] = None
    verification_frequency: Optional[str] = Field(None, max_length=100)
    verification_method: Optional[str] = None
    verification_responsible: Optional[int] = None
    monitoring_records: Optional[str] = None
    verification_records: Optional[str] = None


class CCPUpdate(BaseModel):
    ccp_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[CCPStatus] = None
    critical_limit_min: Optional[float] = None
    critical_limit_max: Optional[float] = None
    critical_limit_unit: Optional[str] = Field(None, max_length=50)
    critical_limit_description: Optional[str] = None
    monitoring_frequency: Optional[str] = Field(None, max_length=100)
    monitoring_method: Optional[str] = None
    monitoring_responsible: Optional[int] = None
    monitoring_equipment: Optional[str] = Field(None, max_length=100)
    corrective_actions: Optional[str] = None
    verification_frequency: Optional[str] = Field(None, max_length=100)
    verification_method: Optional[str] = None
    verification_responsible: Optional[int] = None
    monitoring_records: Optional[str] = None
    verification_records: Optional[str] = None


class CCPResponse(BaseModel):
    id: int
    ccp_number: str
    ccp_name: str
    description: Optional[str] = None
    status: CCPStatus
    critical_limit_min: Optional[float] = None
    critical_limit_max: Optional[float] = None
    critical_limit_unit: Optional[str] = None
    critical_limit_description: Optional[str] = None
    monitoring_frequency: Optional[str] = None
    monitoring_method: Optional[str] = None
    monitoring_responsible: Optional[int] = None
    monitoring_equipment: Optional[str] = None
    corrective_actions: Optional[str] = None
    verification_frequency: Optional[str] = None
    verification_method: Optional[str] = None
    verification_responsible: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Monitoring Log Schemas
class MonitoringLogCreate(BaseModel):
    batch_number: Optional[str] = Field(None, min_length=1, max_length=50)
    batch_id: Optional[int] = None
    measured_value: float
    unit: Optional[str] = Field(None, max_length=20)
    additional_parameters: Optional[Dict[str, Any]] = None
    observations: Optional[str] = None
    evidence_files: Optional[str] = None
    corrective_action_taken: bool = False
    corrective_action_description: Optional[str] = None


class MonitoringLogResponse(BaseModel):
    id: int
    batch_number: Optional[str] = None
    batch_id: Optional[int] = None
    monitoring_time: datetime
    measured_value: float
    unit: Optional[str] = None
    is_within_limits: bool
    additional_parameters: Optional[Dict[str, Any]] = None
    observations: Optional[str] = None
    evidence_files: Optional[str] = None
    corrective_action_taken: bool
    corrective_action_description: Optional[str] = None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Verification Log Schemas
class VerificationLogCreate(BaseModel):
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    is_compliant: bool = True
    samples_tested: Optional[int] = Field(None, ge=0)
    test_results: Optional[Dict[str, Any]] = None
    equipment_calibration: Optional[bool] = None
    calibration_date: Optional[datetime] = None
    evidence_files: Optional[str] = None


class VerificationLogResponse(BaseModel):
    id: int
    verification_date: datetime
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    is_compliant: bool
    samples_tested: Optional[int] = None
    test_results: Optional[Dict[str, Any]] = None
    equipment_calibration: Optional[bool] = None
    calibration_date: Optional[datetime] = None
    evidence_files: Optional[str] = None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Decision Tree Schemas
class DecisionTreeStep(BaseModel):
    question: DecisionTreeQuestion
    answer: bool
    explanation: Optional[str] = None


class DecisionTreeResult(BaseModel):
    is_ccp: bool
    justification: str
    steps: List[DecisionTreeStep]


# HACCP Plan Schemas
class HACCPPlanStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"


class HACCPPlanCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content: str = Field(..., description="Serialized JSON or rich text content")
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None


class HACCPPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    status: Optional[HACCPPlanStatus] = None


class HACCPPlanResponse(BaseModel):
    id: int
    product_id: int
    title: str
    description: Optional[str]
    status: HACCPPlanStatus
    version: str
    effective_date: Optional[datetime]
    review_date: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class HACCPPlanVersionCreate(BaseModel):
    content: str
    change_description: Optional[str] = None
    change_reason: Optional[str] = None


class HACCPPlanVersionResponse(BaseModel):
    id: int
    plan_id: int
    version_number: str
    content: str
    change_description: Optional[str]
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class HACCPPlanApprovalCreate(BaseModel):
    approver_id: int
    approval_order: int
    comments: Optional[str] = None


class HACCPPlanApprovalResponse(BaseModel):
    id: int
    plan_id: int
    approver_id: int
    approval_order: int
    status: str
    comments: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# Flowchart Schemas
class FlowchartNode(BaseModel):
    id: str
    type: str  # "process", "decision", "start", "end"
    label: str
    x: float
    y: float
    data: Optional[Dict[str, Any]] = None


class FlowchartEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None


class FlowchartData(BaseModel):
    nodes: List[FlowchartNode]
    edges: List[FlowchartEdge]


# Dashboard Schemas
class HACCPDashboardStats(BaseModel):
    total_products: int
    approved_plans: int
    total_ccps: int
    active_ccps: int
    out_of_spec_count: int
    recent_logs: List[Dict[str, Any]]


# Report Schemas
class HACCPReportRequest(BaseModel):
    product_id: int
    report_type: str = Field(..., pattern="^(summary|detailed|monitoring|verification)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_charts: bool = True
    format: str = Field("pdf", pattern="^(pdf|excel|html)$")


class HACCPReportResponse(BaseModel):
    report_id: str
    report_url: str
    generated_at: datetime
    file_size: Optional[int] = None 

# Product Risk Configuration Schemas (ISO 22000 compliant)
class ProductRiskConfigCreate(BaseModel):
    calculation_method: Literal["multiplication", "addition", "matrix"] = "multiplication"
    likelihood_scale: int = Field(ge=1, le=10, default=5)
    severity_scale: int = Field(ge=1, le=10, default=5)
    low_threshold: int = Field(ge=1, default=4)
    medium_threshold: int = Field(ge=1, default=8)
    high_threshold: int = Field(ge=1, default=15)
    
    @field_validator('medium_threshold')
    @classmethod
    def validate_threshold_order(cls, v, values):
        if 'low_threshold' in values.data and v <= values.data['low_threshold']:
            raise ValueError('medium_threshold must be greater than low_threshold')
        return v
    
    @field_validator('high_threshold')
    @classmethod
    def validate_high_threshold(cls, v, values):
        if 'medium_threshold' in values.data and v <= values.data['medium_threshold']:
            raise ValueError('high_threshold must be greater than medium_threshold')
        return v

class ProductRiskConfigUpdate(BaseModel):
    calculation_method: Optional[Literal["multiplication", "addition", "matrix"]] = None
    likelihood_scale: Optional[int] = Field(None, ge=1, le=10)
    severity_scale: Optional[int] = Field(None, ge=1, le=10)
    low_threshold: Optional[int] = Field(None, ge=1)
    medium_threshold: Optional[int] = Field(None, ge=1)
    high_threshold: Optional[int] = Field(None, ge=1)

class ProductRiskConfigResponse(BaseModel):
    id: int
    product_id: int
    calculation_method: str
    likelihood_scale: int
    severity_scale: int
    low_threshold: int
    medium_threshold: int
    high_threshold: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True # Product Risk Configuration Schemas (ISO 22000 compliant)

# Product Risk Configuration Schemas (ISO 22000 compliant)
class ProductRiskConfigCreate(BaseModel):
    calculation_method: Literal["multiplication", "addition", "matrix"] = "multiplication"
    likelihood_scale: int = Field(ge=1, le=10, default=5)
    severity_scale: int = Field(ge=1, le=10, default=5)
    low_threshold: int = Field(ge=1, default=4)
    medium_threshold: int = Field(ge=1, default=8)
    high_threshold: int = Field(ge=1, default=15)
    
    @field_validator('medium_threshold')
    @classmethod
    def validate_threshold_order(cls, v, values):
        if 'low_threshold' in values.data and v <= values.data['low_threshold']:
            raise ValueError('medium_threshold must be greater than low_threshold')
        return v
    
    @field_validator('high_threshold')
    @classmethod
    def validate_high_threshold(cls, v, values):
        if 'medium_threshold' in values.data and v <= values.data['medium_threshold']:
            raise ValueError('high_threshold must be greater than medium_threshold')
        return v

class ProductRiskConfigUpdate(BaseModel):
    calculation_method: Optional[Literal["multiplication", "addition", "matrix"]] = None
    likelihood_scale: Optional[int] = Field(None, ge=1, le=10)
    severity_scale: Optional[int] = Field(None, ge=1, le=10)
    low_threshold: Optional[int] = Field(None, ge=1)
    medium_threshold: Optional[int] = Field(None, ge=1)
    high_threshold: Optional[int] = Field(None, ge=1)

class ProductRiskConfigResponse(BaseModel):
    id: int
    product_id: int
    calculation_method: str
    likelihood_scale: int
    severity_scale: int
    low_threshold: int
    medium_threshold: int
    high_threshold: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
