from typing import Optional, List, Literal, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ProcessCreate(BaseModel):
    batch_id: int
    process_type: Literal["fresh_milk", "yoghurt", "mala", "cheese"]
    operator_id: Optional[int] = None
    spec: dict = Field(default_factory=dict)


class ProcessLogCreate(BaseModel):
    step_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    event: Literal["start", "reading", "complete", "divert"]
    measured_temp_c: Optional[float] = None
    note: Optional[str] = None
    auto_flag: Optional[bool] = False
    source: Optional[str] = "manual"


class YieldCreate(BaseModel):
    output_qty: float
    expected_qty: Optional[float] = None
    unit: str


class TransferCreate(BaseModel):
    quantity: float
    unit: str
    location: Optional[str] = None
    lot_number: Optional[str] = None
    verified_by: Optional[int] = None


class AgingCreate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    room_temperature_c: Optional[float] = None
    target_temp_min_c: Optional[float] = None
    target_temp_max_c: Optional[float] = None
    target_days: Optional[int] = None
    room_location: Optional[str] = None
    notes: Optional[str] = None


# Enhanced Production Schemas
class ProcessParameterCreate(BaseModel):
    step_id: Optional[int] = None
    parameter_name: str
    parameter_value: float
    unit: str
    target_value: Optional[float] = None
    tolerance_min: Optional[float] = None
    tolerance_max: Optional[float] = None
    notes: Optional[str] = None
    equipment_id: Optional[int] = None

    @validator('parameter_value')
    def validate_parameter_value(cls, v):
        if v < 0:
            raise ValueError('Parameter value cannot be negative')
        return v


class ProcessDeviationCreate(BaseModel):
    step_id: Optional[int] = None
    parameter_id: Optional[int] = None
    deviation_type: str
    expected_value: float
    actual_value: float
    severity: Literal["low", "medium", "high", "critical"] = "low"
    impact_assessment: Optional[str] = None
    corrective_action: Optional[str] = None


class ProcessAlertCreate(BaseModel):
    alert_type: str
    alert_level: Literal["info", "warning", "error", "critical"] = "warning"
    message: str
    parameter_value: Optional[float] = None
    threshold_value: Optional[float] = None


class ProcessStepSpec(BaseModel):
    step_type: str
    sequence: int
    target_temp_c: Optional[float] = None
    target_time_seconds: Optional[int] = None
    tolerance_c: Optional[float] = None
    required: bool = True
    step_metadata: Optional[Dict[str, Any]] = None


class ProcessTemplateCreate(BaseModel):
    template_name: str
    product_type: Literal["fresh_milk", "yoghurt", "mala", "cheese", "pasteurized_milk", "fermented_products"]
    description: Optional[str] = None
    steps: List[ProcessStepSpec]
    parameters: Optional[Dict[str, Any]] = None


class ProcessTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[ProcessStepSpec]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProcessCreateEnhanced(BaseModel):
    batch_id: int
    process_type: Literal["fresh_milk", "yoghurt", "mala", "cheese", "pasteurized_milk", "fermented_products"]
    operator_id: Optional[int] = None
    template_id: Optional[int] = None
    spec: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ProcessUpdate(BaseModel):
    status: Optional[Literal["in_progress", "diverted", "completed"]] = None
    notes: Optional[str] = None
    end_time: Optional[datetime] = None


class ProcessResponse(BaseModel):
    id: int
    batch_id: int
    process_type: str
    operator_id: Optional[int]
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    spec: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    steps: List[Dict[str, Any]] = []
    logs: List[Dict[str, Any]] = []
    parameters: List[Dict[str, Any]] = []
    deviations: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class ProcessParameterResponse(BaseModel):
    id: int
    process_id: int
    step_id: Optional[int]
    parameter_name: str
    parameter_value: float
    unit: str
    target_value: Optional[float]
    tolerance_min: Optional[float]
    tolerance_max: Optional[float]
    is_within_tolerance: Optional[bool]
    recorded_at: datetime
    recorded_by: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ProcessDeviationResponse(BaseModel):
    id: int
    process_id: int
    step_id: Optional[int]
    parameter_id: Optional[int]
    deviation_type: str
    expected_value: float
    actual_value: float
    deviation_percent: Optional[float]
    severity: str
    impact_assessment: Optional[str]
    corrective_action: Optional[str]
    resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class ProcessAlertResponse(BaseModel):
    id: int
    process_id: int
    alert_type: str
    alert_level: str
    message: str
    parameter_value: Optional[float]
    threshold_value: Optional[float]
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class ProcessTemplateResponse(BaseModel):
    id: int
    template_name: str
    product_type: str
    description: Optional[str]
    steps: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class ProductionAnalytics(BaseModel):
    total_records: int
    avg_overrun_percent: float
    overruns: int
    underruns: int
    total_deviations: int
    critical_deviations: int
    total_alerts: int
    unacknowledged_alerts: int
    process_type_breakdown: Dict[str, int]

    class Config:
        from_attributes = True


class ProcessSpecBindRequest(BaseModel):
    document_id: int
    document_version: str
    locked_parameters: Optional[Dict[str, Any]] = None


class ReleaseChecklistResult(BaseModel):
    item: str
    passed: bool
    notes: Optional[str] = None


class ReleaseCheckResponse(BaseModel):
    ready: bool
    failures: List[str] = []
    checklist: List[Dict[str, Any]] = []


class ReleaseRequest(BaseModel):
    released_qty: Optional[float] = None
    unit: Optional[str] = None
    signature_hash: str


class ReleaseResponse(BaseModel):
    message: str
    release_id: int


class MaterialConsumptionCreate(BaseModel):
    material_id: int
    quantity: float
    unit: str
    supplier_id: Optional[int] = None
    delivery_id: Optional[int] = None
    lot_number: Optional[str] = None
    notes: Optional[str] = None


# Enhanced Process Monitoring and SPC Schemas

class ProcessControlChartCreate(BaseModel):
    parameter_name: str
    chart_type: Literal["X-bar", "R", "CUSUM", "EWMA"] = "X-bar"
    sample_size: int = Field(default=5, ge=2, le=25)
    target_value: Optional[float] = None
    sigma_factor: Optional[float] = Field(default=3.0, ge=1.0, le=6.0)
    specification_upper: Optional[float] = None
    specification_lower: Optional[float] = None
    created_by: Optional[int] = None

    @validator('specification_upper')
    def validate_specification_limits(cls, v, values):
        if v is not None and 'specification_lower' in values and values['specification_lower'] is not None:
            if v <= values['specification_lower']:
                raise ValueError('Upper specification limit must be greater than lower limit')
        return v


class ProcessControlChartResponse(BaseModel):
    id: int
    process_id: int
    parameter_name: str
    chart_type: str
    sample_size: int
    target_value: float
    upper_control_limit: float
    lower_control_limit: float
    upper_warning_limit: Optional[float]
    lower_warning_limit: Optional[float]
    specification_upper: Optional[float]
    specification_lower: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProcessControlPointResponse(BaseModel):
    id: int
    control_chart_id: int
    parameter_id: Optional[int]
    timestamp: datetime
    measured_value: float
    subgroup_range: Optional[float]
    cumulative_sum: Optional[float]
    moving_average: Optional[float]
    is_out_of_control: bool
    control_rule_violated: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ProcessCapabilityStudyCreate(BaseModel):
    parameter_name: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    specification_upper: float
    specification_lower: float
    conducted_by: Optional[int] = None
    approved_by: Optional[int] = None
    study_notes: Optional[str] = None

    @validator('specification_upper')
    def validate_specification_limits(cls, v, values):
        if 'specification_lower' in values and values['specification_lower'] is not None:
            if v <= values['specification_lower']:
                raise ValueError('Upper specification limit must be greater than lower limit')
        return v


class ProcessCapabilityStudyResponse(BaseModel):
    id: int
    process_id: int
    parameter_name: str
    study_period_start: datetime
    study_period_end: datetime
    sample_size: int
    mean_value: float
    standard_deviation: float
    specification_upper: float
    specification_lower: float
    cp_index: Optional[float]
    cpk_index: Optional[float]
    pp_index: Optional[float]
    ppk_index: Optional[float]
    process_sigma_level: Optional[float]
    defect_rate_ppm: Optional[float]
    is_capable: Optional[bool]
    study_notes: Optional[str]
    conducted_by: Optional[int]
    approved_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class YieldAnalysisReportCreate(BaseModel):
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    conforming_output_quantity: Optional[float] = None
    rework_quantity: Optional[float] = 0.0
    waste_quantity: Optional[float] = 0.0
    analysis_method: Literal["standard", "lean", "six_sigma"] = "standard"
    analyzed_by: Optional[int] = None
    reviewed_by: Optional[int] = None
    approved_by: Optional[int] = None

    @validator('period_end')
    def validate_period(cls, v, values):
        if v and 'period_start' in values and values['period_start']:
            if v <= values['period_start']:
                raise ValueError('End date must be after start date')
        return v


class YieldAnalysisReportResponse(BaseModel):
    id: int
    process_id: int
    analysis_period_start: datetime
    analysis_period_end: datetime
    total_input_quantity: float
    total_output_quantity: float
    conforming_output_quantity: float
    non_conforming_quantity: float
    rework_quantity: float
    waste_quantity: float
    unit: str
    first_pass_yield: float
    rolled_throughput_yield: Optional[float]
    overall_yield: float
    quality_rate: float
    rework_rate: float
    waste_rate: float
    primary_loss_category: Optional[str]
    secondary_loss_reasons: Optional[List[str]]
    improvement_opportunities: Optional[List[str]]
    corrective_actions_taken: Optional[List[str]]
    analysis_method: str
    baseline_comparison: Optional[Dict[str, Any]]
    trend_analysis: Optional[Dict[str, Any]]
    statistical_significance: Optional[bool]
    confidence_level: Optional[float]
    analyzed_by: Optional[int]
    reviewed_by: Optional[int]
    approved_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    defect_categories: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class YieldDefectCategoryResponse(BaseModel):
    id: int
    yield_report_id: int
    defect_type: str
    defect_description: Optional[str]
    defect_count: int
    defect_quantity: float
    defect_cost: Optional[float]
    percentage_of_total: float
    cumulative_percentage: float
    is_critical_to_quality: bool
    root_cause_category: Optional[str]
    corrective_action_required: bool
    prevention_method: Optional[str]

    class Config:
        from_attributes = True


class ProcessMonitoringAlertResponse(BaseModel):
    id: int
    process_id: int
    control_chart_id: Optional[int]
    alert_type: str
    severity_level: str
    alert_title: str
    alert_message: str
    parameter_name: Optional[str]
    current_value: Optional[float]
    threshold_value: Optional[float]
    trend_direction: Optional[str]
    control_rule: Optional[str]
    auto_generated: bool
    requires_immediate_action: bool
    escalation_level: int
    assigned_to: Optional[int]
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[int]
    resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[int]
    resolution_notes: Optional[str]
    food_safety_impact: bool
    ccp_affected: bool
    oprp_affected: bool
    corrective_action_required: bool
    verification_required: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProcessMonitoringAlertUpdate(BaseModel):
    assigned_to: Optional[int] = None
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None
    escalation_level: Optional[int] = None


class ProcessMonitoringDashboardCreate(BaseModel):
    dashboard_name: str
    process_type: Optional[Literal["fresh_milk", "yoghurt", "mala", "cheese", "pasteurized_milk", "fermented_products"]] = None
    is_public: bool = False
    dashboard_config: Dict[str, Any]
    refresh_interval_seconds: int = Field(default=30, ge=5, le=300)
    alert_thresholds: Optional[Dict[str, Any]] = None


class ProcessMonitoringDashboardResponse(BaseModel):
    id: int
    dashboard_name: str
    process_type: Optional[str]
    user_id: int
    is_public: bool
    dashboard_config: Dict[str, Any]
    refresh_interval_seconds: int
    alert_thresholds: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProcessMonitoringAnalytics(BaseModel):
    # Base analytics
    total_records: int
    avg_overrun_percent: float
    overruns: int
    underruns: int
    total_deviations: int
    critical_deviations: int
    total_alerts: int
    unacknowledged_alerts: int
    process_type_breakdown: Dict[str, int]
    
    # SPC metrics
    spc_metrics: Dict[str, Any]
    
    # Yield metrics
    yield_metrics: Dict[str, Any]
    
    # Alert metrics
    alert_metrics: Dict[str, Any]

    class Config:
        from_attributes = True


class ControlChartData(BaseModel):
    """Data structure for control chart visualization"""
    chart_info: ProcessControlChartResponse
    data_points: List[ProcessControlPointResponse]
    statistics: Dict[str, Any]
    violations: List[Dict[str, Any]]

    class Config:
        from_attributes = True

