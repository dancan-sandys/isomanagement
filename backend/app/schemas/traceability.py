from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class BatchType(str, Enum):
    RAW_MILK = "raw_milk"
    ADDITIVE = "additive"
    CULTURE = "culture"
    PACKAGING = "packaging"
    FINAL_PRODUCT = "final_product"
    INTERMEDIATE = "intermediate"


class BatchStatus(str, Enum):
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    QUARANTINED = "quarantined"
    RELEASED = "released"
    RECALLED = "recalled"
    DISPOSED = "disposed"


class RecallStatus(str, Enum):
    DRAFT = "draft"
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecallType(str, Enum):
    CLASS_I = "class_i"
    CLASS_II = "class_ii"
    CLASS_III = "class_iii"


class ReportType(str, Enum):
    FORWARD_TRACE = "forward_trace"
    BACKWARD_TRACE = "backward_trace"
    FULL_TRACE = "full_trace"


# Batch Schemas
class BatchCreate(BaseModel):
    batch_type: BatchType
    product_name: str = Field(..., min_length=1, max_length=100)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    production_date: datetime
    expiry_date: Optional[datetime] = None
    lot_number: Optional[str] = Field(None, max_length=50)
    supplier_id: Optional[int] = None
    supplier_batch_number: Optional[str] = Field(None, max_length=50)
    coa_number: Optional[str] = Field(None, max_length=50)
    storage_location: Optional[str] = Field(None, max_length=100)
    storage_conditions: Optional[str] = None


class BatchUpdate(BaseModel):
    batch_type: Optional[BatchType] = None
    status: Optional[BatchStatus] = None
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    expiry_date: Optional[datetime] = None
    lot_number: Optional[str] = Field(None, max_length=50)
    quality_status: Optional[str] = Field(None, pattern="^(pending|passed|failed)$")
    test_results: Optional[Dict[str, Any]] = None
    storage_location: Optional[str] = Field(None, max_length=100)
    storage_conditions: Optional[str] = None


class BatchResponse(BaseModel):
    id: int
    batch_number: str
    batch_type: BatchType
    status: BatchStatus
    product_name: str
    quantity: float
    unit: str
    production_date: datetime
    expiry_date: Optional[datetime] = None
    lot_number: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_batch_number: Optional[str] = None
    coa_number: Optional[str] = None
    quality_status: str
    test_results: Optional[Dict[str, Any]] = None
    storage_location: Optional[str] = None
    storage_conditions: Optional[str] = None
    barcode: Optional[str] = None
    qr_code_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Enhanced Search Schemas
class EnhancedBatchSearch(BaseModel):
    batch_id: Optional[int] = None
    batch_number: Optional[str] = None
    product_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    batch_type: Optional[BatchType] = None
    status: Optional[BatchStatus] = None
    lot_number: Optional[str] = None
    supplier_id: Optional[int] = None


# Barcode Generation Schemas
class BarcodePrintData(BaseModel):
    batch_number: str
    barcode: str
    product_name: str
    batch_type: str
    production_date: str
    quantity: float
    unit: str
    lot_number: Optional[str] = None
    qr_code_path: Optional[str] = None
    print_timestamp: str


# Recall Simulation Schemas
class RecallSimulationRequest(BaseModel):
    batch_id: Optional[int] = None
    product_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    batch_type: Optional[BatchType] = None
    simulation_type: str = Field(..., pattern="^(full|partial|test)$")
    regulatory_notification_required: bool = False
    simulation_description: Optional[str] = None


class RecallSimulationResponse(BaseModel):
    simulation_id: str
    simulation_date: str
    simulation_criteria: Dict[str, Any]
    affected_batches: List[Dict[str, Any]]
    total_quantity_affected: float
    trace_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommended_actions: List[Dict[str, Any]]


# Corrective Action Form Schemas
class RootCauseAnalysis(BaseModel):
    immediate_cause: str = Field(..., min_length=1)
    underlying_cause: str = Field(..., min_length=1)
    systemic_cause: str = Field(..., min_length=1)
    analysis_date: datetime
    analyzed_by: int


class CorrectiveAction(BaseModel):
    action_type: str = Field(..., pattern="^(immediate|short_term|long_term)$")
    description: str = Field(..., min_length=1)
    assigned_to: int
    due_date: datetime
    priority: str = Field(..., pattern="^(high|medium|low)$")
    status: str = Field("pending", pattern="^(pending|in_progress|completed)$")


class PreventiveMeasure(BaseModel):
    measure_type: str = Field(..., pattern="^(process_improvement|training|system_update|monitoring)$")
    description: str = Field(..., min_length=1)
    implementation_date: Optional[datetime] = None
    responsible_person: int


class VerificationPlan(BaseModel):
    verification_methods: List[str] = Field(..., min_items=1)
    verification_schedule: str = Field(..., min_length=1)
    responsible_person: int
    success_criteria: List[str] = Field(..., min_items=1)


class EffectivenessReview(BaseModel):
    review_date: datetime
    reviewed_by: int
    effectiveness_score: int = Field(..., ge=0, le=100)
    additional_actions_required: bool = False
    review_notes: Optional[str] = None


class CorrectiveActionForm(BaseModel):
    form_id: str
    recall_reference: str
    root_cause_analysis: RootCauseAnalysis
    corrective_actions: List[CorrectiveAction]
    preventive_measures: List[PreventiveMeasure]
    verification_plan: VerificationPlan
    effectiveness_review: Optional[EffectivenessReview] = None


# Traceability Link Schemas
class TraceabilityLinkCreate(BaseModel):
    linked_batch_id: int
    relationship_type: str = Field(..., pattern="^(parent|child|ingredient|packaging)$")
    quantity_used: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    usage_date: datetime
    process_step: Optional[str] = Field(None, max_length=100)


class TraceabilityLinkResponse(BaseModel):
    id: int
    batch_id: int
    linked_batch_id: int
    relationship_type: str
    quantity_used: float
    unit: str
    usage_date: datetime
    process_step: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Recall Schemas
class RecallCreate(BaseModel):
    recall_type: RecallType
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    hazard_description: Optional[str] = None
    affected_products: Optional[List[str]] = None
    affected_batches: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    total_quantity_affected: float = Field(..., gt=0)
    quantity_in_distribution: Optional[float] = Field(None, ge=0)
    issue_discovered_date: datetime
    regulatory_notification_required: bool = False
    assigned_to: int


class RecallUpdate(BaseModel):
    status: Optional[RecallStatus] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    reason: Optional[str] = Field(None, min_length=1)
    hazard_description: Optional[str] = None
    affected_products: Optional[List[str]] = None
    affected_batches: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    total_quantity_affected: Optional[float] = Field(None, gt=0)
    quantity_in_distribution: Optional[float] = Field(None, ge=0)
    regulatory_notification_required: Optional[bool] = None
    assigned_to: Optional[int] = None


class RecallResponse(BaseModel):
    id: int
    recall_number: str
    recall_type: RecallType
    status: RecallStatus
    title: str
    description: str
    reason: str
    hazard_description: Optional[str] = None
    affected_products: Optional[List[str]] = None
    affected_batches: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    total_quantity_affected: float
    quantity_in_distribution: Optional[float] = None
    quantity_recalled: Optional[float] = None
    quantity_disposed: Optional[float] = None
    issue_discovered_date: datetime
    recall_initiated_date: Optional[datetime] = None
    recall_completed_date: Optional[datetime] = None
    regulatory_notification_required: bool
    regulatory_notification_date: Optional[datetime] = None
    regulatory_reference: Optional[str] = None
    assigned_to: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Recall Entry Schemas
class RecallEntryCreate(BaseModel):
    batch_id: int
    quantity_affected: float = Field(..., gt=0)
    quantity_recalled: Optional[float] = Field(None, ge=0)
    quantity_disposed: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    customer: Optional[str] = Field(None, max_length=100)


class RecallEntryResponse(BaseModel):
    id: int
    recall_id: int
    batch_id: int
    quantity_affected: float
    quantity_recalled: float
    quantity_disposed: float
    location: Optional[str] = None
    customer: Optional[str] = None
    status: str
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Recall Action Schemas
class RecallActionCreate(BaseModel):
    action_type: str = Field(..., pattern="^(notification|retrieval|disposal|investigation)$")
    description: str = Field(..., min_length=1)
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class RecallActionResponse(BaseModel):
    id: int
    recall_id: int
    action_type: str
    description: str
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    status: str
    results: Optional[str] = None
    evidence_files: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Traceability Report Schemas
class TraceabilityReportCreate(BaseModel):
    starting_batch_id: int
    report_type: ReportType = ReportType.FULL_TRACE
    trace_depth: int = Field(5, ge=1, le=10)


class TraceabilityReportResponse(BaseModel):
    id: int
    report_number: str
    report_type: str
    starting_batch_id: int
    trace_date: datetime
    trace_depth: int
    traced_batches: Optional[List[int]] = None
    trace_path: Optional[Dict[str, Any]] = None
    trace_summary: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Dashboard Schemas
class TraceabilityDashboardStats(BaseModel):
    batch_counts: Dict[str, int]
    status_counts: Dict[str, int]
    recent_batches: int
    active_recalls: int
    recent_reports: int
    quality_breakdown: Dict[str, int]


# Filter Schemas
class BatchFilter(BaseModel):
    batch_type: Optional[BatchType] = None
    status: Optional[BatchStatus] = None
    product_name: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class RecallFilter(BaseModel):
    status: Optional[RecallStatus] = None
    recall_type: Optional[RecallType] = None
    search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Trace Chain Schemas
class TraceChainResponse(BaseModel):
    starting_batch: BatchResponse
    incoming_links: List[TraceabilityLinkResponse]
    outgoing_links: List[TraceabilityLinkResponse]
    trace_path: Dict[str, Any]


# Status Update Schemas
class RecallStatusUpdate(BaseModel):
    status: RecallStatus
    notes: Optional[str] = None


class BatchStatusUpdate(BaseModel):
    status: BatchStatus
    quality_status: Optional[str] = Field(None, pattern="^(pending|passed|failed)$")
    test_results: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


# Report Generation Schemas
class TraceabilityReportRequest(BaseModel):
    starting_batch_id: int
    report_type: ReportType = ReportType.FULL_TRACE
    trace_depth: int = Field(5, ge=1, le=10)
    include_details: bool = True
    format: str = Field("json", pattern="^(json|pdf|excel)$")


class TraceabilityReportData(BaseModel):
    report_id: str
    report_number: str
    report_type: str
    starting_batch: Dict[str, Any]
    traced_batches: List[Dict[str, Any]]
    trace_path: Dict[str, Any]
    trace_summary: str
    generated_at: datetime
    trace_statistics: Dict[str, Any]


# Recall Report with Corrective Action Schemas
class RecallReportRequest(BaseModel):
    recall_id: int
    include_corrective_action: bool = True
    include_trace_analysis: bool = True
    format: str = Field("json", pattern="^(json|pdf|excel)$")


class RecallReportResponse(BaseModel):
    recall_id: int
    recall_number: str
    report_generated_at: str
    recall_details: Dict[str, Any]
    affected_batches: List[Dict[str, Any]]
    trace_analysis: Dict[str, Any]
    corrective_action_form: Optional[Dict[str, Any]] = None
    actions_taken: List[Dict[str, Any]]
    regulatory_compliance: Dict[str, Any] 