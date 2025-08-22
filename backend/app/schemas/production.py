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
    total_processes: int
    active_processes: int
    completed_processes: int
    diverted_processes: int
    average_yield_percent: Optional[float]
    total_deviations: int
    critical_deviations: int
    total_alerts: int
    unacknowledged_alerts: int
    process_type_breakdown: Dict[str, int]
    yield_trends: List[Dict[str, Any]]
    deviation_trends: List[Dict[str, Any]]

    class Config:
        from_attributes = True

