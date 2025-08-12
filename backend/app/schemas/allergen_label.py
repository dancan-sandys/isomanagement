from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductAllergenAssessmentCreate(BaseModel):
    product_id: int
    inherent_allergens: Optional[List[str]] = None
    cross_contact_sources: Optional[List[str]] = None
    risk_level: Optional[str] = Field(default="low", pattern="^(low|medium|high)$")
    precautionary_labeling: Optional[str] = None
    control_measures: Optional[str] = None
    validation_verification: Optional[str] = None
    reviewed_by: Optional[int] = None


class ProductAllergenAssessmentUpdate(ProductAllergenAssessmentCreate):
    pass


class ProductAllergenAssessmentResponse(ProductAllergenAssessmentCreate):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LabelTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    product_id: Optional[int] = None
    is_active: Optional[bool] = True


class LabelTemplateResponse(LabelTemplateCreate):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class LabelTemplateVersionCreate(BaseModel):
    content: str
    change_description: str
    change_reason: str


class LabelTemplateVersionResponse(LabelTemplateVersionCreate):
    id: int
    template_id: int
    version_number: int
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class LabelTemplateApprovalCreate(BaseModel):
    approver_id: int
    approval_order: int


class LabelTemplateApprovalResponse(LabelTemplateApprovalCreate):
    id: int
    version_id: int
    status: str
    comments: Optional[str] = None
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True


