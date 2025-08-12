from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EquipmentCreate(BaseModel):
    name: str
    equipment_type: str
    serial_number: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


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

    class Config:
        from_attributes = True


class MaintenanceWorkOrderCreate(BaseModel):
    equipment_id: int
    plan_id: Optional[int] = None
    title: str
    description: Optional[str] = None


class MaintenanceWorkOrderResponse(BaseModel):
    id: int
    equipment_id: int
    plan_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None

    class Config:
        from_attributes = True


class CalibrationPlanCreate(BaseModel):
    schedule_date: datetime
    notes: Optional[str] = None


class CalibrationPlanResponse(BaseModel):
    id: int
    equipment_id: int
    schedule_date: datetime
    last_calibrated_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    active: bool
    notes: Optional[str] = None

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

    class Config:
        from_attributes = True


