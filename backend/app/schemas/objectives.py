from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ObjectiveBase(BaseModel):
    objective_code: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    measurement_unit: Optional[str] = None
    frequency: Optional[str] = None
    responsible_person_id: Optional[int] = None
    review_frequency: Optional[str] = None
    status: Optional[Literal["active", "inactive", "archived"]] = "active"


class ObjectiveCreate(ObjectiveBase):
    created_by: int


class ObjectiveUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    measurement_unit: Optional[str] = None
    frequency: Optional[str] = None
    responsible_person_id: Optional[int] = None
    review_frequency: Optional[str] = None
    status: Optional[Literal["active", "inactive", "archived"]] = None


class Objective(ObjectiveBase):
    id: int
    created_by: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ObjectiveTargetBase(BaseModel):
    department_id: Optional[int] = None
    period_start: datetime
    period_end: datetime
    target_value: float
    lower_threshold: Optional[float] = None
    upper_threshold: Optional[float] = None
    weight: Optional[float] = 1.0
    is_lower_better: Optional[bool] = False


class ObjectiveTargetCreate(ObjectiveTargetBase):
    objective_id: int
    created_by: int


class ObjectiveTargetUpdate(BaseModel):
    department_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    target_value: Optional[float] = None
    lower_threshold: Optional[float] = None
    upper_threshold: Optional[float] = None
    weight: Optional[float] = None
    is_lower_better: Optional[bool] = None


class ObjectiveTarget(ObjectiveTargetBase):
    id: int
    objective_id: int
    created_by: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ObjectiveProgressBase(BaseModel):
    department_id: Optional[int] = None
    period_start: datetime
    period_end: datetime
    actual_value: float
    evidence: Optional[str] = None


class ObjectiveProgressCreate(ObjectiveProgressBase):
    objective_id: int
    created_by: int


class ObjectiveProgressUpdate(BaseModel):
    department_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    actual_value: Optional[float] = None
    evidence: Optional[str] = None
    attainment_percent: Optional[float] = None
    status: Optional[Literal["on_track", "at_risk", "off_track"]] = None


class ObjectiveProgress(ObjectiveProgressBase):
    id: int
    objective_id: int
    attainment_percent: Optional[float] = None
    status: Optional[Literal["on_track", "at_risk", "off_track"]] = None
    created_by: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ObjectiveKPIResponse(BaseModel):
    objective_id: int
    objective_code: str
    title: str
    measurement_unit: Optional[str]
    department_id: Optional[int]
    period_start: datetime
    period_end: datetime
    target_value: Optional[float]
    actual_value: Optional[float]
    attainment_percent: Optional[float]
    status: Optional[str]


class ObjectivesDashboardResponse(BaseModel):
    corporate_attainment: Optional[float]
    departments: List[ObjectiveKPIResponse]
    trends: List[ObjectiveKPIResponse]

