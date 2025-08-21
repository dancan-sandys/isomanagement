from typing import Optional, List, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field


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

