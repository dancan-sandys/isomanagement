from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SWOTCategory(str, Enum):
    STRENGTHS = "strengths"
    WEAKNESSES = "weaknesses"
    OPPORTUNITIES = "opportunities"
    THREATS = "threats"

class PESTELCategory(str, Enum):
    POLITICAL = "political"
    ECONOMIC = "economic"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"

# SWOT Analysis Schemas
class SWOTAnalysisBase(BaseModel):
    title: str = Field(..., description="Title of the SWOT analysis")
    description: Optional[str] = Field(None, description="Description of the analysis")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Date of analysis")
    is_active: bool = Field(True, description="Whether the analysis is active")

class SWOTAnalysisCreate(SWOTAnalysisBase):
    pass

class SWOTAnalysisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    analysis_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class SWOTAnalysisResponse(SWOTAnalysisBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    strengths_count: int = 0
    weaknesses_count: int = 0
    opportunities_count: int = 0
    threats_count: int = 0
    actions_generated: int = 0
    completed_actions: int = 0

    class Config:
        from_attributes = True

# SWOT Item Schemas
class SWOTItemBase(BaseModel):
    category: SWOTCategory = Field(..., description="SWOT category")
    description: str = Field(..., description="Description of the item")
    impact_level: str = Field(..., description="Impact level (high, medium, low)")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    notes: Optional[str] = Field(None, description="Additional notes")

class SWOTItemCreate(SWOTItemBase):
    pass

class SWOTItemUpdate(BaseModel):
    category: Optional[SWOTCategory] = None
    description: Optional[str] = None
    impact_level: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class SWOTItemResponse(SWOTItemBase):
    id: int
    analysis_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# PESTEL Analysis Schemas
class PESTELAnalysisBase(BaseModel):
    title: str = Field(..., description="Title of the PESTEL analysis")
    description: Optional[str] = Field(None, description="Description of the analysis")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Date of analysis")
    is_active: bool = Field(True, description="Whether the analysis is active")

class PESTELAnalysisCreate(PESTELAnalysisBase):
    pass

class PESTELAnalysisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    analysis_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class PESTELAnalysisResponse(PESTELAnalysisBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    political_count: int = 0
    economic_count: int = 0
    social_count: int = 0
    technological_count: int = 0
    environmental_count: int = 0
    legal_count: int = 0
    actions_generated: int = 0
    completed_actions: int = 0

    class Config:
        from_attributes = True

# PESTEL Item Schemas
class PESTELItemBase(BaseModel):
    category: PESTELCategory = Field(..., description="PESTEL category")
    description: str = Field(..., description="Description of the item")
    impact_level: str = Field(..., description="Impact level (high, medium, low)")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    notes: Optional[str] = Field(None, description="Additional notes")

class PESTELItemCreate(PESTELItemBase):
    pass

class PESTELItemUpdate(BaseModel):
    category: Optional[PESTELCategory] = None
    description: Optional[str] = None
    impact_level: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class PESTELItemResponse(PESTELItemBase):
    id: int
    analysis_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# Analytics Schemas
class SWOTAnalytics(BaseModel):
    total_analyses: int
    active_analyses: int
    total_items: int
    strengths_count: int
    weaknesses_count: int
    opportunities_count: int
    threats_count: int
    actions_generated: int
    completed_actions: int
    completion_rate: float

class PESTELAnalytics(BaseModel):
    total_analyses: int
    active_analyses: int
    total_items: int
    political_count: int
    economic_count: int
    social_count: int
    technological_count: int
    environmental_count: int
    legal_count: int
    actions_generated: int
    completed_actions: int
    completion_rate: float
