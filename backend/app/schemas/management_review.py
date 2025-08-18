from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ManagementReviewStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ManagementReviewType(str, Enum):
    SCHEDULED = "scheduled"
    AD_HOC = "ad_hoc"
    EMERGENCY = "emergency"


class ReviewInputType(str, Enum):
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


class ReviewOutputType(str, Enum):
    IMPROVEMENT_ACTION = "improvement_action"
    RESOURCE_ALLOCATION = "resource_allocation"
    POLICY_CHANGE = "policy_change"
    OBJECTIVE_UPDATE = "objective_update"
    SYSTEM_CHANGE = "system_change"
    TRAINING_REQUIREMENT = "training_requirement"
    RISK_TREATMENT = "risk_treatment"


class ActionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(str, Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ReviewAgendaItemCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    discussion: Optional[str] = None
    decision: Optional[str] = None
    order_index: Optional[int] = None


class ReviewAgendaItemResponse(BaseModel):
    id: int
    topic: str
    discussion: Optional[str] = None
    decision: Optional[str] = None
    order_index: Optional[int] = None

    model_config = {"from_attributes": True}


# Enhanced Review Input Schemas
class ManagementReviewInputCreate(BaseModel):
    input_type: ReviewInputType
    input_source: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    input_summary: Optional[str] = None
    collection_date: Optional[datetime] = None
    responsible_person_id: Optional[int] = None


class ManagementReviewInputResponse(BaseModel):
    id: int
    input_type: ReviewInputType
    input_source: Optional[str]
    input_data: Optional[Dict[str, Any]]
    input_summary: Optional[str]
    collection_date: Optional[datetime]
    responsible_person_id: Optional[int]
    data_completeness_score: Optional[float]
    data_accuracy_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Enhanced Review Output Schemas
class ManagementReviewOutputCreate(BaseModel):
    output_type: ReviewOutputType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    target_completion_date: Optional[datetime] = None
    priority: ActionPriority = ActionPriority.MEDIUM
    implementation_plan: Optional[str] = None
    resource_requirements: Optional[str] = None
    success_criteria: Optional[str] = None
    verification_required: bool = True


class ManagementReviewOutputResponse(BaseModel):
    id: int
    output_type: ReviewOutputType
    title: str
    description: Optional[str]
    assigned_to: Optional[int]
    target_completion_date: Optional[datetime]
    priority: ActionPriority
    status: ActionStatus
    implementation_plan: Optional[str]
    resource_requirements: Optional[str]
    success_criteria: Optional[str]
    progress_percentage: float
    completed: bool
    completed_at: Optional[datetime]
    verification_required: bool
    verified: bool
    verified_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# Enhanced Review Action Schemas
class ReviewActionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    action_type: Optional[ReviewOutputType] = None
    priority: ActionPriority = ActionPriority.MEDIUM
    verification_required: bool = False
    estimated_effort_hours: Optional[float] = None
    resource_requirements: Optional[str] = None


class ReviewActionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[ActionPriority] = None
    status: Optional[ActionStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    progress_notes: Optional[str] = None
    actual_effort_hours: Optional[float] = None


class ReviewActionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to: Optional[int]
    due_date: Optional[datetime]
    action_type: Optional[ReviewOutputType]
    priority: ActionPriority
    status: ActionStatus
    progress_percentage: float
    progress_notes: Optional[str]
    completed: bool
    completed_at: Optional[datetime]
    completed_by: Optional[int]
    verification_required: bool
    verified: bool
    verified_at: Optional[datetime]
    verified_by: Optional[int]
    estimated_effort_hours: Optional[float]
    actual_effort_hours: Optional[float]
    resource_requirements: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Participant Schema
class ReviewParticipant(BaseModel):
    user_id: Optional[int] = None
    name: str
    role: str
    department: Optional[str] = None
    email: Optional[str] = None
    attendance_status: str = "present"  # present, absent, partial


# Enhanced Management Review Schemas
class ManagementReviewCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    review_date: Optional[datetime] = None
    review_type: ManagementReviewType = ManagementReviewType.SCHEDULED
    review_scope: Optional[str] = None
    attendees: Optional[List[ReviewParticipant]] = None
    chairperson_id: Optional[int] = None
    review_frequency: Optional[str] = None
    
    # ISO compliance fields
    food_safety_policy_reviewed: bool = False
    food_safety_objectives_reviewed: bool = False
    fsms_changes_required: bool = False
    resource_adequacy_assessment: Optional[str] = None
    improvement_opportunities: Optional[List[Dict[str, Any]]] = None
    external_issues: Optional[str] = None
    internal_issues: Optional[str] = None
    
    # Initial data
    status: Optional[ManagementReviewStatus] = ManagementReviewStatus.PLANNED
    next_review_date: Optional[datetime] = None
    agenda: Optional[List[ReviewAgendaItemCreate]] = None


class ManagementReviewUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    review_date: Optional[datetime] = None
    review_type: Optional[ManagementReviewType] = None
    review_scope: Optional[str] = None
    attendees: Optional[List[ReviewParticipant]] = None
    chairperson_id: Optional[int] = None
    
    # ISO compliance fields
    food_safety_policy_reviewed: Optional[bool] = None
    food_safety_objectives_reviewed: Optional[bool] = None
    fsms_changes_required: Optional[bool] = None
    resource_adequacy_assessment: Optional[str] = None
    improvement_opportunities: Optional[List[Dict[str, Any]]] = None
    previous_actions_status: Optional[List[Dict[str, Any]]] = None
    external_issues: Optional[str] = None
    internal_issues: Optional[str] = None
    
    # Performance summaries
    customer_feedback_summary: Optional[str] = None
    supplier_performance_summary: Optional[str] = None
    audit_results_summary: Optional[str] = None
    nc_capa_summary: Optional[str] = None
    kpi_performance_summary: Optional[str] = None
    
    # Documentation
    minutes: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    
    # Review effectiveness
    review_effectiveness_score: Optional[float] = Field(None, ge=1, le=10)
    effectiveness_justification: Optional[str] = None
    
    # Status
    status: Optional[ManagementReviewStatus] = None
    next_review_date: Optional[datetime] = None
    review_frequency: Optional[str] = None


class ManagementReviewResponse(BaseModel):
    id: int
    title: str
    review_date: Optional[datetime]
    review_type: ManagementReviewType
    review_scope: Optional[str]
    attendees: Optional[List[ReviewParticipant]]
    chairperson_id: Optional[int]
    
    # ISO compliance fields
    food_safety_policy_reviewed: bool
    food_safety_objectives_reviewed: bool
    fsms_changes_required: bool
    resource_adequacy_assessment: Optional[str]
    improvement_opportunities: Optional[List[Dict[str, Any]]]
    previous_actions_status: Optional[List[Dict[str, Any]]]
    external_issues: Optional[str]
    internal_issues: Optional[str]
    
    # Performance summaries
    customer_feedback_summary: Optional[str]
    supplier_performance_summary: Optional[str]
    audit_results_summary: Optional[str]
    nc_capa_summary: Optional[str]
    kpi_performance_summary: Optional[str]
    
    # Documentation
    minutes: Optional[str]
    inputs: Optional[Dict[str, Any]]
    outputs: Optional[Dict[str, Any]]
    
    # Review effectiveness
    review_effectiveness_score: Optional[float]
    effectiveness_justification: Optional[str]
    
    # Status and scheduling
    status: ManagementReviewStatus
    next_review_date: Optional[datetime]
    review_frequency: Optional[str]
    
    # Audit trail
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Related data
    agenda_items: List[ReviewAgendaItemResponse] = []
    actions: List[ReviewActionResponse] = []
    inputs_data: List[ManagementReviewInputResponse] = []
    outputs_data: List[ManagementReviewOutputResponse] = []

    model_config = {"from_attributes": True}


# Template Schemas
class ManagementReviewTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    agenda_template: Optional[List[Dict[str, Any]]] = None
    input_checklist: Optional[List[Dict[str, Any]]] = None
    output_categories: Optional[List[Dict[str, Any]]] = None
    is_default: bool = False
    review_frequency: Optional[str] = None
    applicable_departments: Optional[List[str]] = None
    compliance_standards: Optional[List[str]] = None


class ManagementReviewTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    agenda_template: Optional[List[Dict[str, Any]]]
    input_checklist: Optional[List[Dict[str, Any]]]
    output_categories: Optional[List[Dict[str, Any]]]
    is_default: bool
    is_active: bool
    review_frequency: Optional[str]
    applicable_departments: Optional[List[str]]
    compliance_standards: Optional[List[str]]
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


# KPI Schemas
class ManagementReviewKPICreate(BaseModel):
    kpi_name: str = Field(..., min_length=1, max_length=200)
    kpi_description: Optional[str] = None
    kpi_category: Optional[str] = None
    target_value: Optional[float] = None
    unit_of_measure: Optional[str] = None


class ManagementReviewKPIResponse(BaseModel):
    id: int
    review_id: Optional[int]
    kpi_name: str
    kpi_description: Optional[str]
    kpi_category: Optional[str]
    target_value: Optional[float]
    actual_value: Optional[float]
    unit_of_measure: Optional[str]
    measurement_date: Optional[datetime]
    performance_status: Optional[str]
    variance_percentage: Optional[float]
    improvement_trend: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Data Collection Schemas
class DataCollectionRequest(BaseModel):
    input_types: List[ReviewInputType]
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    include_summaries: bool = True


class ComplianceCheckResponse(BaseModel):
    iso_22000_compliance: Dict[str, Any]
    missing_inputs: List[str]
    missing_outputs: List[str]
    compliance_score: float
    recommendations: List[str]


