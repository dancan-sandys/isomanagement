from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NonConformanceSource(str, Enum):
    PRP = "PRP"
    AUDIT = "AUDIT"
    COMPLAINT = "COMPLAINT"
    PRODUCTION_DEVIATION = "PRODUCTION_DEVIATION"
    SUPPLIER = "SUPPLIER"
    HACCP = "HACCP"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"


class NonConformanceStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    ROOT_CAUSE_IDENTIFIED = "ROOT_CAUSE_IDENTIFIED"
    CAPA_ASSIGNED = "CAPA_ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


class CAPAStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"
    OVERDUE = "overdue"


class RootCauseMethod(str, Enum):
    FIVE_WHYS = "five_whys"
    ISHIKAWA = "ishikawa"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    OTHER = "other"


# Base schemas
class NonConformanceBase(BaseModel):
    title: str = Field(..., description="Title of the non-conformance")
    description: str = Field(..., description="Detailed description of the non-conformance")
    source: NonConformanceSource
    batch_reference: Optional[str] = None
    product_reference: Optional[str] = None
    process_reference: Optional[str] = None
    location: Optional[str] = None
    severity: str = Field(default="medium", description="low, medium, high, critical")
    impact_area: Optional[str] = None
    category: Optional[str] = None
    target_resolution_date: Optional[datetime] = None


class NonConformanceCreate(NonConformanceBase):
    pass


class NonConformanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[NonConformanceSource] = None
    batch_reference: Optional[str] = None
    product_reference: Optional[str] = None
    process_reference: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    impact_area: Optional[str] = None
    category: Optional[str] = None
    status: Optional[NonConformanceStatus] = None
    target_resolution_date: Optional[datetime] = None
    actual_resolution_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    assigned_date: Optional[datetime] = None
    evidence_files: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class NonConformanceResponse(NonConformanceBase):
    id: int
    nc_number: str
    status: NonConformanceStatus
    reported_date: datetime
    actual_resolution_date: Optional[datetime] = None
    reported_by: int
    assigned_to: Optional[int] = None
    assigned_date: Optional[datetime] = None
    evidence_files: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Root Cause Analysis schemas
class RootCauseAnalysisBase(BaseModel):
    method: RootCauseMethod
    analysis_date: datetime
    immediate_cause: Optional[str] = None
    underlying_cause: Optional[str] = None
    root_cause: Optional[str] = None
    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None
    fishbone_categories: Optional[Dict[str, Any]] = None
    fishbone_diagram_data: Optional[Dict[str, Any]] = None
    contributing_factors: Optional[List[str]] = None
    system_failures: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    preventive_measures: Optional[List[str]] = None


class RootCauseAnalysisCreate(RootCauseAnalysisBase):
    non_conformance_id: int


class RootCauseAnalysisUpdate(BaseModel):
    method: Optional[RootCauseMethod] = None
    analysis_date: Optional[datetime] = None
    immediate_cause: Optional[str] = None
    underlying_cause: Optional[str] = None
    root_cause: Optional[str] = None
    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None
    fishbone_categories: Optional[Dict[str, Any]] = None
    fishbone_diagram_data: Optional[Dict[str, Any]] = None
    contributing_factors: Optional[List[str]] = None
    system_failures: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    preventive_measures: Optional[List[str]] = None


class RootCauseAnalysisResponse(RootCauseAnalysisBase):
    id: int
    non_conformance_id: int
    conducted_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# CAPA Action schemas
class CAPAActionBase(BaseModel):
    title: str = Field(..., description="Title of the CAPA action")
    description: str = Field(..., description="Detailed description of the CAPA action")
    action_type: Optional[str] = None  # corrective, preventive, both
    responsible_person: int
    target_completion_date: datetime
    required_resources: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    implementation_plan: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    deliverables: Optional[List[str]] = None
    effectiveness_criteria: Optional[List[str]] = None


class CAPAActionCreate(CAPAActionBase):
    non_conformance_id: Optional[int] = None


class CAPAActionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None
    responsible_person: Optional[int] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    status: Optional[CAPAStatus] = None
    progress_percentage: Optional[float] = None
    required_resources: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    implementation_plan: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    deliverables: Optional[List[str]] = None
    effectiveness_criteria: Optional[List[str]] = None
    effectiveness_measured: Optional[bool] = None
    effectiveness_score: Optional[float] = None


class CAPAActionResponse(CAPAActionBase):
    id: int
    capa_number: str
    non_conformance_id: int
    assigned_date: datetime
    actual_completion_date: Optional[datetime] = None
    status: CAPAStatus
    progress_percentage: float
    actual_cost: Optional[float] = None
    effectiveness_measured: bool
    effectiveness_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int

    class Config:
        from_attributes = True


# CAPA Verification schemas
class CAPAVerificationBase(BaseModel):
    verification_date: datetime
    verification_criteria: Optional[List[str]] = None
    verification_method: Optional[str] = None
    verification_evidence: Optional[List[str]] = None
    verification_result: Optional[str] = None  # passed, failed, conditional
    effectiveness_score: Optional[float] = None
    comments: Optional[str] = None
    follow_up_required: bool = False
    follow_up_actions: Optional[List[str]] = None
    next_verification_date: Optional[datetime] = None


class CAPAVerificationCreate(CAPAVerificationBase):
    non_conformance_id: Optional[int] = None
    capa_action_id: Optional[int] = None


class CAPAVerificationUpdate(BaseModel):
    verification_date: Optional[datetime] = None
    verification_criteria: Optional[List[str]] = None
    verification_method: Optional[str] = None
    verification_evidence: Optional[List[str]] = None
    verification_result: Optional[str] = None
    effectiveness_score: Optional[float] = None
    comments: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_actions: Optional[List[str]] = None
    next_verification_date: Optional[datetime] = None


class CAPAVerificationResponse(CAPAVerificationBase):
    id: int
    non_conformance_id: int
    capa_action_id: int
    verified_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Attachment schemas
class NonConformanceAttachmentBase(BaseModel):
    file_name: str
    attachment_type: Optional[str] = None  # evidence, document, photo, video, etc.
    description: Optional[str] = None


class NonConformanceAttachmentCreate(NonConformanceAttachmentBase):
    non_conformance_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None


class NonConformanceAttachmentUpdate(BaseModel):
    file_name: Optional[str] = None
    attachment_type: Optional[str] = None
    description: Optional[str] = None


class NonConformanceAttachmentResponse(NonConformanceAttachmentBase):
    id: int
    non_conformance_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    uploaded_by: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Filter schemas
class NonConformanceFilter(BaseModel):
    search: Optional[str] = None
    source: Optional[NonConformanceSource] = None
    status: Optional[NonConformanceStatus] = None
    severity: Optional[str] = None
    impact_area: Optional[str] = None
    reported_by: Optional[int] = None
    assigned_to: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


class CAPAFilter(BaseModel):
    non_conformance_id: Optional[int] = None
    status: Optional[CAPAStatus] = None
    responsible_person: Optional[int] = None
    action_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


# Dashboard schemas
class NonConformanceDashboardStats(BaseModel):
    total_non_conformances: int
    open_non_conformances: int
    overdue_capas: int
    non_conformances_by_source: List[Dict[str, Any]]
    non_conformances_by_status: List[Dict[str, Any]]
    non_conformances_by_severity: List[Dict[str, Any]]
    recent_non_conformances: List[Dict[str, Any]]
    capa_completion_rate: float
    average_resolution_time: float


# Response schemas
class NonConformanceListResponse(BaseModel):
    items: List[NonConformanceResponse]
    total: int
    page: int
    size: int
    pages: int


class CAPAListResponse(BaseModel):
    items: List[CAPAActionResponse]
    total: int
    page: int
    size: int
    pages: int


class RootCauseAnalysisListResponse(BaseModel):
    items: List[RootCauseAnalysisResponse]
    total: int
    page: int
    size: int
    pages: int


class VerificationListResponse(BaseModel):
    items: List[CAPAVerificationResponse]
    total: int
    page: int
    size: int
    pages: int


class AttachmentListResponse(BaseModel):
    items: List[NonConformanceAttachmentResponse]
    total: int
    page: int
    size: int
    pages: int


# Bulk operations
class BulkNonConformanceAction(BaseModel):
    non_conformance_ids: List[int]
    action: str  # assign, update_status, close


class BulkCAPAAction(BaseModel):
    capa_ids: List[int]
    action: str  # update_status, assign, complete


# Root cause analysis tools
class FiveWhysAnalysis(BaseModel):
    problem: str
    why_1: str
    why_2: str
    why_3: str
    why_4: str
    why_5: str
    root_cause: str


class IshikawaAnalysis(BaseModel):
    problem: str
    categories: Dict[str, List[str]]  # e.g., {"People": ["training", "experience"], "Process": ["procedure", "equipment"]}
    diagram_data: Dict[str, Any]


class RootCauseAnalysisRequest(BaseModel):
    non_conformance_id: int
    method: RootCauseMethod
    analysis_data: Dict[str, Any]  # Flexible data structure for different methods


# New NC/CAPA Schemas

# Immediate Action schemas
class ImmediateActionBase(BaseModel):
    action_type: str = Field(..., description="containment, isolation, emergency_response, notification")
    description: str = Field(..., description="Detailed description of the immediate action")
    implemented_by: int = Field(..., description="User ID of the person implementing the action")
    implemented_at: datetime = Field(..., description="When the action was implemented")

    @validator('action_type')
    def validate_action_type(cls, v):
        valid_types = ['containment', 'isolation', 'emergency_response', 'notification']
        if v not in valid_types:
            raise ValueError(f'action_type must be one of: {valid_types}')
        return v

    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('description must be at least 10 characters long')
        return v

    @validator('implemented_at')
    def validate_implemented_at(cls, v):
        if v > datetime.now():
            raise ValueError('implemented_at cannot be in the future')
        return v


class ImmediateActionCreate(ImmediateActionBase):
    non_conformance_id: int


class ImmediateActionUpdate(BaseModel):
    action_type: Optional[str] = None
    description: Optional[str] = None
    effectiveness_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None
    verification_by: Optional[int] = None


class ImmediateActionResponse(ImmediateActionBase):
    id: int
    non_conformance_id: int
    effectiveness_verified: bool
    verification_date: Optional[datetime] = None
    verification_by: Optional[int] = None

    class Config:
        from_attributes = True


# Non-Conformance Risk Assessment schemas
class NonConformanceRiskAssessmentBase(BaseModel):
    food_safety_impact: str = Field(..., description="low, medium, high, critical")
    regulatory_impact: str = Field(..., description="low, medium, high, critical")
    customer_impact: str = Field(..., description="low, medium, high, critical")
    business_impact: str = Field(..., description="low, medium, high, critical")
    overall_risk_score: float = Field(..., description="Calculated risk score")
    risk_matrix_position: str = Field(..., description="e.g., A1, B2, C3")
    requires_escalation: bool = Field(default=False, description="Whether escalation is required")
    escalation_level: Optional[str] = Field(None, description="supervisor, manager, director, executive")

    @validator('food_safety_impact', 'regulatory_impact', 'customer_impact', 'business_impact')
    def validate_impact_levels(cls, v):
        valid_levels = ['low', 'medium', 'high', 'critical']
        if v not in valid_levels:
            raise ValueError(f'impact level must be one of: {valid_levels}')
        return v

    @validator('overall_risk_score')
    def validate_risk_score(cls, v):
        if not 0.0 <= v <= 4.0:
            raise ValueError('overall_risk_score must be between 0.0 and 4.0')
        return v

    @validator('risk_matrix_position')
    def validate_matrix_position(cls, v):
        import re
        if not re.match(r'^[A-D][1-4]$', v):
            raise ValueError('risk_matrix_position must be in format A1, B2, C3, D4')
        return v

    @validator('escalation_level')
    def validate_escalation_level(cls, v):
        if v is not None:
            valid_levels = ['supervisor', 'manager', 'director', 'executive']
            if v not in valid_levels:
                raise ValueError(f'escalation_level must be one of: {valid_levels}')
        return v


class NonConformanceRiskAssessmentCreate(NonConformanceRiskAssessmentBase):
    non_conformance_id: int


class NonConformanceRiskAssessmentUpdate(BaseModel):
    food_safety_impact: Optional[str] = None
    regulatory_impact: Optional[str] = None
    customer_impact: Optional[str] = None
    business_impact: Optional[str] = None
    overall_risk_score: Optional[float] = None
    risk_matrix_position: Optional[str] = None
    requires_escalation: Optional[bool] = None
    escalation_level: Optional[str] = None


class NonConformanceRiskAssessmentResponse(NonConformanceRiskAssessmentBase):
    id: int
    non_conformance_id: int
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True


# Escalation Rule schemas
class EscalationRuleBase(BaseModel):
    rule_name: str = Field(..., description="Name of the escalation rule")
    rule_description: Optional[str] = Field(None, description="Description of the rule")
    trigger_condition: str = Field(..., description="risk_score, time_delay, severity_level")
    trigger_value: float = Field(..., description="Value that triggers the escalation")
    escalation_level: str = Field(..., description="supervisor, manager, director, executive")
    notification_recipients: Optional[str] = Field(None, description="JSON array of user IDs or email addresses")
    escalation_timeframe: Optional[int] = Field(None, description="Timeframe in hours")
    is_active: bool = Field(default=True, description="Whether the rule is active")

    @validator('rule_name')
    def validate_rule_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('rule_name must be at least 3 characters long')
        return v

    @validator('trigger_condition')
    def validate_trigger_condition(cls, v):
        valid_conditions = ['risk_score', 'time_delay', 'severity_level']
        if v not in valid_conditions:
            raise ValueError(f'trigger_condition must be one of: {valid_conditions}')
        return v

    @validator('trigger_value')
    def validate_trigger_value(cls, v):
        if v < 0:
            raise ValueError('trigger_value must be non-negative')
        return v

    @validator('escalation_level')
    def validate_escalation_level(cls, v):
        valid_levels = ['supervisor', 'manager', 'director', 'executive']
        if v not in valid_levels:
            raise ValueError(f'escalation_level must be one of: {valid_levels}')
        return v

    @validator('notification_recipients')
    def validate_notification_recipients(cls, v):
        if v is not None:
            import json
            try:
                recipients = json.loads(v)
                if not isinstance(recipients, list):
                    raise ValueError('notification_recipients must be a valid JSON array')
            except json.JSONDecodeError:
                raise ValueError('notification_recipients must be valid JSON')
        return v

    @validator('escalation_timeframe')
    def validate_escalation_timeframe(cls, v):
        if v is not None and v <= 0:
            raise ValueError('escalation_timeframe must be positive')
        return v


class EscalationRuleCreate(EscalationRuleBase):
    pass


class EscalationRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    trigger_condition: Optional[str] = None
    trigger_value: Optional[float] = None
    escalation_level: Optional[str] = None
    notification_recipients: Optional[str] = None
    escalation_timeframe: Optional[int] = None
    is_active: Optional[bool] = None


class EscalationRuleResponse(EscalationRuleBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# Preventive Action schemas
class PreventiveActionBase(BaseModel):
    action_title: str = Field(..., description="Title of the preventive action")
    action_description: str = Field(..., description="Detailed description of the preventive action")
    action_type: str = Field(..., description="process_improvement, training, equipment_upgrade, procedure_update")
    priority: str = Field(..., description="low, medium, high, critical")
    assigned_to: int = Field(..., description="User ID of the person assigned to the action")
    due_date: datetime = Field(..., description="Due date for the preventive action")
    status: str = Field(..., description="planned, in_progress, completed, cancelled")
    effectiveness_target: Optional[float] = Field(None, description="Percentage target for effectiveness")
    effectiveness_measured: Optional[float] = Field(None, description="Actual effectiveness percentage")

    @validator('action_title')
    def validate_action_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('action_title must be at least 5 characters long')
        return v

    @validator('action_description')
    def validate_action_description(cls, v):
        if len(v.strip()) < 20:
            raise ValueError('action_description must be at least 20 characters long')
        return v

    @validator('action_type')
    def validate_action_type(cls, v):
        valid_types = ['process_improvement', 'training', 'equipment_upgrade', 'procedure_update']
        if v not in valid_types:
            raise ValueError(f'action_type must be one of: {valid_types}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'priority must be one of: {valid_priorities}')
        return v

    @validator('due_date')
    def validate_due_date(cls, v):
        if v < datetime.now():
            raise ValueError('due_date cannot be in the past')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {valid_statuses}')
        return v

    @validator('effectiveness_target', 'effectiveness_measured')
    def validate_effectiveness_values(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('effectiveness values must be between 0 and 100')
        return v


class PreventiveActionCreate(PreventiveActionBase):
    non_conformance_id: int


class PreventiveActionUpdate(BaseModel):
    action_title: Optional[str] = None
    action_description: Optional[str] = None
    action_type: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    completion_date: Optional[datetime] = None
    effectiveness_target: Optional[float] = None
    effectiveness_measured: Optional[float] = None


class PreventiveActionResponse(PreventiveActionBase):
    id: int
    non_conformance_id: int
    completion_date: Optional[datetime] = None
    created_at: datetime
    created_by: int
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# Effectiveness Monitoring schemas
class EffectivenessMonitoringBase(BaseModel):
    monitoring_period_start: datetime = Field(..., description="Start of monitoring period")
    monitoring_period_end: datetime = Field(..., description="End of monitoring period")
    metric_name: str = Field(..., description="Name of the metric being monitored")
    metric_description: Optional[str] = Field(None, description="Description of the metric")
    target_value: float = Field(..., description="Target value for the metric")
    actual_value: Optional[float] = Field(None, description="Actual measured value")
    measurement_unit: Optional[str] = Field(None, description="percentage, count, days, etc.")
    measurement_frequency: str = Field(..., description="daily, weekly, monthly, quarterly")
    measurement_method: Optional[str] = Field(None, description="How the measurement is taken")
    status: str = Field(..., description="active, completed, suspended")
    achievement_percentage: Optional[float] = Field(None, description="Calculated achievement percentage")
    trend_analysis: Optional[str] = Field(None, description="JSON data for trend analysis")

    @validator('monitoring_period_end')
    def validate_monitoring_period(cls, v, values):
        if 'monitoring_period_start' in values and v <= values['monitoring_period_start']:
            raise ValueError('monitoring_period_end must be after monitoring_period_start')
        return v

    @validator('metric_name')
    def validate_metric_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('metric_name must be at least 3 characters long')
        return v

    @validator('target_value')
    def validate_target_value(cls, v):
        if v <= 0:
            raise ValueError('target_value must be positive')
        return v

    @validator('actual_value')
    def validate_actual_value(cls, v):
        if v is not None and v < 0:
            raise ValueError('actual_value cannot be negative')
        return v

    @validator('measurement_frequency')
    def validate_measurement_frequency(cls, v):
        valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        if v not in valid_frequencies:
            raise ValueError(f'measurement_frequency must be one of: {valid_frequencies}')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'completed', 'suspended']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {valid_statuses}')
        return v

    @validator('achievement_percentage')
    def validate_achievement_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('achievement_percentage must be between 0 and 100')
        return v

    @validator('trend_analysis')
    def validate_trend_analysis(cls, v):
        if v is not None:
            import json
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('trend_analysis must be valid JSON')
        return v


class EffectivenessMonitoringCreate(EffectivenessMonitoringBase):
    non_conformance_id: int


class EffectivenessMonitoringUpdate(BaseModel):
    monitoring_period_start: Optional[datetime] = None
    monitoring_period_end: Optional[datetime] = None
    metric_name: Optional[str] = None
    metric_description: Optional[str] = None
    target_value: Optional[float] = None
    actual_value: Optional[float] = None
    measurement_unit: Optional[str] = None
    measurement_frequency: Optional[str] = None
    measurement_method: Optional[str] = None
    status: Optional[str] = None
    achievement_percentage: Optional[float] = None
    trend_analysis: Optional[str] = None


class EffectivenessMonitoringResponse(EffectivenessMonitoringBase):
    id: int
    non_conformance_id: int
    created_at: datetime
    created_by: int
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# List response schemas for new models
class ImmediateActionListResponse(BaseModel):
    items: List[ImmediateActionResponse]
    total: int
    page: int
    size: int
    pages: int


class RiskAssessmentListResponse(BaseModel):
    items: List[NonConformanceRiskAssessmentResponse]
    total: int
    page: int
    size: int
    pages: int


class EscalationRuleListResponse(BaseModel):
    items: List[EscalationRuleResponse]
    total: int
    page: int
    size: int
    pages: int


class PreventiveActionListResponse(BaseModel):
    items: List[PreventiveActionResponse]
    total: int
    page: int
    size: int
    pages: int


class EffectivenessMonitoringListResponse(BaseModel):
    items: List[EffectivenessMonitoringResponse]
    total: int
    page: int
    size: int
    pages: int


# Filter schemas for new models
class ImmediateActionFilter(BaseModel):
    non_conformance_id: Optional[int] = None
    action_type: Optional[str] = None
    implemented_by: Optional[int] = None
    effectiveness_verified: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


class RiskAssessmentFilter(BaseModel):
    non_conformance_id: Optional[int] = None
    food_safety_impact: Optional[str] = None
    regulatory_impact: Optional[str] = None
    requires_escalation: Optional[bool] = None
    risk_score_min: Optional[float] = None
    risk_score_max: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20

# Backwards-compatibility alias for tests expecting these names
# Some tests import RiskAssessmentCreate directly from nonconformance schemas
RiskAssessmentCreate = NonConformanceRiskAssessmentCreate
NonConformanceRiskAssessmentFilter = RiskAssessmentFilter


class EscalationRuleFilter(BaseModel):
    trigger_condition: Optional[str] = None
    escalation_level: Optional[str] = None
    is_active: Optional[bool] = None
    created_by: Optional[int] = None
    page: int = 1
    size: int = 20


class PreventiveActionFilter(BaseModel):
    non_conformance_id: Optional[int] = None
    action_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


class EffectivenessMonitoringFilter(BaseModel):
    non_conformance_id: Optional[int] = None
    metric_name: Optional[str] = None
    status: Optional[str] = None
    measurement_frequency: Optional[str] = None
    period_start_from: Optional[datetime] = None
    period_start_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


# Specialized request schemas
class ImmediateActionVerificationRequest(BaseModel):
    verification_by: int
    verification_date: Optional[datetime] = None


class RiskAssessmentCalculationRequest(BaseModel):
    food_safety_impact: str
    regulatory_impact: str
    customer_impact: str
    business_impact: str

# Backwards-compatibility alias for service/tests
NonConformanceRiskAssessmentCalculationRequest = RiskAssessmentCalculationRequest


class EscalationRuleTriggerRequest(BaseModel):
    rule_id: int
    trigger_value: float
    context_data: Optional[Dict[str, Any]] = None


class PreventiveActionEffectivenessRequest(BaseModel):
    action_id: int
    effectiveness_measured: float
    measurement_date: datetime
    measurement_method: Optional[str] = None


class EffectivenessMonitoringUpdateRequest(BaseModel):
    monitoring_id: int
    actual_value: float
    measurement_date: datetime
    measurement_notes: Optional[str] = None 