from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RiskItemType(str, Enum):
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class RiskCategory(str, Enum):
    PROCESS = "process"
    SUPPLIER = "supplier"
    STAFF = "staff"
    ENVIRONMENT = "environment"
    HACCP = "haccp"
    PRP = "prp"
    DOCUMENT = "document"
    TRAINING = "training"
    EQUIPMENT = "equipment"
    COMPLIANCE = "compliance"
    CUSTOMER = "customer"
    OTHER = "other"


class RiskStatus(str, Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLikelihood(str, Enum):
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"


class RiskClassification(str, Enum):
    FOOD_SAFETY = "food_safety"
    BUSINESS = "business"
    CUSTOMER = "customer"


class RiskDetectability(str, Enum):
    EASILY_DETECTABLE = "easily_detectable"
    MODERATELY_DETECTABLE = "moderately_detectable"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"
    ALMOST_UNDETECTABLE = "almost_undetectable"


class RiskActionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class RiskActionResponse(BaseModel):
    id: int
    item_id: int
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskActionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


class RiskItemCreate(BaseModel):
    item_type: RiskItemType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: RiskCategory = RiskCategory.OTHER
    classification: Optional[RiskClassification] = None
    # Risk-only fields
    severity: Optional[RiskSeverity] = RiskSeverity.LOW
    likelihood: Optional[RiskLikelihood] = RiskLikelihood.UNLIKELY
    detectability: Optional[RiskDetectability] = None
    impact_score: Optional[int] = Field(None, ge=1, le=5)
    risk_score: Optional[int] = Field(None, ge=1, le=125)
    # Opportunity-only fields
    opportunity_benefit: Optional[int] = Field(None, ge=1, le=5)
    opportunity_feasibility: Optional[int] = Field(None, ge=1, le=5)
    opportunity_score: Optional[int] = Field(None, ge=1, le=25)
    mitigation_plan: Optional[str] = None
    residual_risk: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    references: Optional[str] = None


class RiskItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[RiskCategory] = None
    classification: Optional[RiskClassification] = None
    status: Optional[RiskStatus] = None
    severity: Optional[RiskSeverity] = None
    likelihood: Optional[RiskLikelihood] = None
    detectability: Optional[RiskDetectability] = None
    impact_score: Optional[int] = Field(None, ge=1, le=5)
    risk_score: Optional[int] = Field(None, ge=1, le=125)
    opportunity_benefit: Optional[int] = Field(None, ge=1, le=5)
    opportunity_feasibility: Optional[int] = Field(None, ge=1, le=5)
    opportunity_score: Optional[int] = Field(None, ge=1, le=25)
    mitigation_plan: Optional[str] = None
    residual_risk: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    references: Optional[str] = None


class RiskItemResponse(BaseModel):
    id: int
    risk_number: str
    item_type: RiskItemType
    title: str
    description: Optional[str] = None
    category: RiskCategory
    classification: Optional[RiskClassification] = None
    status: RiskStatus
    severity: RiskSeverity
    likelihood: RiskLikelihood
    detectability: Optional[RiskDetectability] = None
    impact_score: Optional[int] = None
    risk_score: int
    opportunity_benefit: Optional[int] = None
    opportunity_feasibility: Optional[int] = None
    opportunity_score: Optional[int] = None
    mitigation_plan: Optional[str] = None
    residual_risk: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    references: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RiskFilter(BaseModel):
    search: Optional[str] = None
    item_type: Optional[RiskItemType] = None
    category: Optional[RiskCategory] = None
    classification: Optional[RiskClassification] = None
    status: Optional[RiskStatus] = None
    severity: Optional[RiskSeverity] = None
    likelihood: Optional[RiskLikelihood] = None
    detectability: Optional[RiskDetectability] = None
    assigned_to: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class RiskStats(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    by_item_type: Dict[str, int]


