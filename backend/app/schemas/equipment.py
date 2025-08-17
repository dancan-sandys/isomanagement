from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EquipmentCreate(BaseModel):
    name: str
    equipment_type: str
    serial_number: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True
    critical_to_food_safety: Optional[bool] = False


class EquipmentResponse(EquipmentCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class MaintenancePlanCreate(BaseModel):
    frequency_days: int
    maintenance_type: str  # preventive/corrective
    notes: Optional[str] = None


class MaintenancePlanResponse(BaseModel):
    id: int
    equipment_id: int
    frequency_days: int
    maintenance_type: str
    last_performed_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    active: bool
    notes: Optional[str] = None
    # Enriched fields for UI
    equipment_name: Optional[str] = None
    last_maintenance_date: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class MaintenanceWorkOrderCreate(BaseModel):
    equipment_id: int
    plan_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: Optional[str] = 'MEDIUM'
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class MaintenanceWorkOrderResponse(BaseModel):
    id: int
    equipment_id: int
    plan_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    created_by: Optional[int] = None
    # Enriched
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True


class CalibrationPlanCreate(BaseModel):
    schedule_date: datetime
    frequency_days: int
    notes: Optional[str] = None


class CalibrationPlanResponse(BaseModel):
    id: int
    equipment_id: int
    schedule_date: datetime
    frequency_days: int
    last_calibrated_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    active: bool
    notes: Optional[str] = None
    # Enriched
    equipment_name: Optional[str] = None
    last_calibration_date: Optional[datetime] = None
    status: Optional[str] = None
    certificate_file: Optional[bool] = None

    class Config:
        from_attributes = True


class CalibrationRecordResponse(BaseModel):
    id: int
    plan_id: int
    performed_at: datetime
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: Optional[str] = None
    uploaded_by: int
    # ISO metadata
    certificate_number: Optional[str] = None
    calibrated_by: Optional[str] = None
    result: Optional[str] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True


# Updates
class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    equipment_type: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    critical_to_food_safety: Optional[bool] = None


class MaintenancePlanUpdate(BaseModel):
    frequency_days: Optional[int] = None
    maintenance_type: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class MaintenanceWorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class CalibrationPlanUpdate(BaseModel):
    schedule_date: Optional[datetime] = None
    frequency_days: Optional[int] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


