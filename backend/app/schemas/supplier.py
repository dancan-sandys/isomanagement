from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SupplierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"
    BLACKLISTED = "blacklisted"


class SupplierCategory(str, Enum):
    RAW_MILK = "raw_milk"
    ADDITIVES = "additives"
    CULTURES = "cultures"
    PACKAGING = "packaging"
    EQUIPMENT = "equipment"
    CHEMICALS = "chemicals"
    SERVICES = "services"


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class InspectionStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


# Base schemas
class SupplierBase(BaseModel):
    supplier_code: str = Field(..., description="Unique supplier code")
    name: str = Field(..., description="Supplier name")
    category: SupplierCategory
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    business_registration_number: Optional[str] = None
    tax_identification_number: Optional[str] = None
    company_type: Optional[str] = None
    year_established: Optional[int] = None
    risk_level: str = Field(default="low", description="low, medium, high")
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_code: Optional[str] = None
    name: Optional[str] = None
    status: Optional[SupplierStatus] = None
    category: Optional[SupplierCategory] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    business_registration_number: Optional[str] = None
    tax_identification_number: Optional[str] = None
    company_type: Optional[str] = None
    year_established: Optional[int] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None
    overall_score: Optional[float] = None
    last_evaluation_date: Optional[datetime] = None
    next_evaluation_date: Optional[datetime] = None


class SupplierResponse(SupplierBase):
    id: int
    status: SupplierStatus
    overall_score: float = 0.0
    last_evaluation_date: Optional[datetime] = None
    next_evaluation_date: Optional[datetime] = None
    materials_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None  # Made optional
    created_by: int
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


# Material schemas
class MaterialBase(BaseModel):
    material_code: str = Field(..., description="Unique material code")
    name: str = Field(..., description="Material name")
    description: Optional[str] = None
    category: Optional[str] = None
    supplier_material_code: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    quality_parameters: Optional[List[str]] = None
    acceptable_limits: Optional[Dict[str, Any]] = None
    allergens: Optional[List[str]] = None
    allergen_statement: Optional[str] = None
    storage_conditions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    handling_instructions: Optional[str] = None


class MaterialCreate(MaterialBase):
    supplier_id: int


class MaterialUpdate(BaseModel):
    material_code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    supplier_material_code: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    quality_parameters: Optional[List[str]] = None
    acceptable_limits: Optional[Dict[str, Any]] = None
    allergens: Optional[List[str]] = None
    allergen_statement: Optional[str] = None
    storage_conditions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    handling_instructions: Optional[str] = None
    is_active: Optional[bool] = None
    approval_status: Optional[str] = None


class MaterialResponse(MaterialBase):
    id: int
    supplier_id: int
    is_active: bool
    approval_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None  # Made optional
    created_by: int

    class Config:
        from_attributes = True


# Evaluation schemas
class SupplierEvaluationBase(BaseModel):
    evaluation_period: str = Field(..., description="e.g., Q1 2024")
    evaluation_date: datetime
    quality_score: Optional[float] = Field(None, ge=1, le=5)
    delivery_score: Optional[float] = Field(None, ge=1, le=5)
    price_score: Optional[float] = Field(None, ge=1, le=5)
    communication_score: Optional[float] = Field(None, ge=1, le=5)
    technical_support_score: Optional[float] = Field(None, ge=1, le=5)
    hygiene_score: Optional[float] = Field(None, ge=1, le=5)
    quality_comments: Optional[str] = None
    delivery_comments: Optional[str] = None
    price_comments: Optional[str] = None
    communication_comments: Optional[str] = None
    technical_support_comments: Optional[str] = None
    hygiene_comments: Optional[str] = None
    issues_identified: Optional[List[str]] = None
    improvement_actions: Optional[List[str]] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None


class SupplierEvaluationCreate(SupplierEvaluationBase):
    supplier_id: int


class SupplierEvaluationUpdate(BaseModel):
    evaluation_period: Optional[str] = None
    evaluation_date: Optional[datetime] = None
    status: Optional[EvaluationStatus] = None
    quality_score: Optional[float] = Field(None, ge=1, le=5)
    delivery_score: Optional[float] = Field(None, ge=1, le=5)
    price_score: Optional[float] = Field(None, ge=1, le=5)
    communication_score: Optional[float] = Field(None, ge=1, le=5)
    technical_support_score: Optional[float] = Field(None, ge=1, le=5)
    hygiene_score: Optional[float] = Field(None, ge=1, le=5)
    overall_score: Optional[float] = None
    quality_comments: Optional[str] = None
    delivery_comments: Optional[str] = None
    price_comments: Optional[str] = None
    communication_comments: Optional[str] = None
    technical_support_comments: Optional[str] = None
    hygiene_comments: Optional[str] = None
    issues_identified: Optional[List[str]] = None
    improvement_actions: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None


class SupplierEvaluationResponse(SupplierEvaluationBase):
    id: int
    supplier_id: int
    status: EvaluationStatus
    overall_score: Optional[float] = None
    evaluated_by: int
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None  # Made optional

    class Config:
        from_attributes = True


# Delivery schemas
class IncomingDeliveryBase(BaseModel):
    delivery_number: str = Field(..., description="Unique delivery number")
    delivery_date: datetime
    expected_delivery_date: Optional[datetime] = None
    quantity_received: float
    unit: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    coa_number: Optional[str] = None
    storage_location: Optional[str] = None
    storage_conditions: Optional[str] = None


class IncomingDeliveryCreate(IncomingDeliveryBase):
    supplier_id: int
    material_id: int


class IncomingDeliveryUpdate(BaseModel):
    delivery_number: Optional[str] = None
    delivery_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    quantity_received: Optional[float] = None
    unit: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    coa_number: Optional[str] = None
    inspection_status: Optional[InspectionStatus] = None
    inspection_date: Optional[datetime] = None
    inspection_results: Optional[Dict[str, Any]] = None
    non_conformances: Optional[List[str]] = None
    corrective_actions: Optional[str] = None
    storage_location: Optional[str] = None
    storage_conditions: Optional[str] = None


class IncomingDeliveryResponse(IncomingDeliveryBase):
    id: int
    supplier_id: int
    material_id: int
    inspection_status: str
    inspection_date: Optional[datetime] = None
    inspected_by: Optional[int] = None
    inspection_results: Optional[Dict[str, Any]] = None
    non_conformances: Optional[List[str]] = None
    corrective_actions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None  # Made optional
    created_by: int

    class Config:
        from_attributes = True


# Document schemas
class SupplierDocumentBase(BaseModel):
    document_type: str = Field(..., description="certificate, license, insurance, etc.")
    document_name: str
    document_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None


class SupplierDocumentCreate(SupplierDocumentBase):
    supplier_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None


class SupplierDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None
    is_valid: Optional[bool] = None
    is_verified: Optional[bool] = None


class SupplierDocumentResponse(SupplierDocumentBase):
    id: int
    supplier_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    is_valid: bool
    is_verified: bool
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None  # Made optional
    created_by: int

    class Config:
        from_attributes = True


# Filter schemas
class SupplierFilter(BaseModel):
    search: Optional[str] = None
    category: Optional[SupplierCategory] = None
    status: Optional[SupplierStatus] = None
    risk_level: Optional[str] = None
    page: int = 1
    size: int = 20


class MaterialFilter(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None
    supplier_id: Optional[int] = None
    approval_status: Optional[str] = None
    page: int = 1
    size: int = 20


class EvaluationFilter(BaseModel):
    supplier_id: Optional[int] = None
    status: Optional[EvaluationStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


class DeliveryFilter(BaseModel):
    supplier_id: Optional[int] = None
    material_id: Optional[int] = None
    inspection_status: Optional[InspectionStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


# Dashboard schemas
class SupplierDashboardStats(BaseModel):
    total_suppliers: int
    active_suppliers: int
    overdue_evaluations: int
    suppliers_by_category: List[Dict[str, Any]]
    suppliers_by_risk: List[Dict[str, Any]]
    recent_evaluations: List[Dict[str, Any]]
    recent_deliveries: List[Dict[str, Any]]
    average_score: float
    high_risk_suppliers: int


# Bulk operations
class BulkSupplierAction(BaseModel):
    supplier_ids: List[int]
    action: str  # activate, deactivate, suspend, blacklist


class BulkMaterialAction(BaseModel):
    material_ids: List[int]
    action: str  # approve, reject, activate, deactivate


# Response schemas
class SupplierListResponse(BaseModel):
    items: List[SupplierResponse]
    total: int
    page: int
    size: int
    pages: int


class MaterialListResponse(BaseModel):
    items: List[MaterialResponse]
    total: int
    page: int
    size: int
    pages: int


class EvaluationListResponse(BaseModel):
    items: List[SupplierEvaluationResponse]
    total: int
    page: int
    size: int
    pages: int


class DeliveryListResponse(BaseModel):
    items: List[IncomingDeliveryResponse]
    total: int
    page: int
    size: int
    pages: int


class DocumentListResponse(BaseModel):
    items: List[SupplierDocumentResponse]
    total: int
    page: int
    size: int
    pages: int 


# Inspection Checklist schemas
class InspectionChecklistBase(BaseModel):
    checklist_name: str = Field(..., description="Name of the inspection checklist")
    checklist_type: Optional[str] = Field(None, description="Type of inspection")
    checklist_version: str = Field(default="1.0", description="Checklist version")
    general_notes: Optional[str] = None
    corrective_actions: Optional[str] = None


class InspectionChecklistCreate(InspectionChecklistBase):
    delivery_id: int


class InspectionChecklistUpdate(BaseModel):
    checklist_name: Optional[str] = None
    checklist_type: Optional[str] = None
    checklist_version: Optional[str] = None
    is_completed: Optional[bool] = None
    overall_result: Optional[str] = None
    total_items: Optional[int] = None
    passed_items: Optional[int] = None
    failed_items: Optional[int] = None
    general_notes: Optional[str] = None
    corrective_actions: Optional[str] = None


class InspectionChecklistResponse(InspectionChecklistBase):
    id: int
    delivery_id: int
    is_completed: bool
    completed_by: Optional[int] = None
    completed_at: Optional[datetime] = None
    overall_result: Optional[str] = None
    total_items: int
    passed_items: int
    failed_items: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # Made optional
    created_by: int

    class Config:
        from_attributes = True


class InspectionChecklistItemBase(BaseModel):
    item_name: str = Field(..., description="Name of the checklist item")
    item_description: Optional[str] = None
    item_category: Optional[str] = None
    acceptable_criteria: Optional[str] = None
    measurement_unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    comments: Optional[str] = None
    corrective_action: Optional[str] = None


class InspectionChecklistItemCreate(InspectionChecklistItemBase):
    checklist_id: int


class InspectionChecklistItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_description: Optional[str] = None
    item_category: Optional[str] = None
    acceptable_criteria: Optional[str] = None
    measurement_unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_checked: Optional[bool] = None
    result: Optional[str] = None
    actual_value: Optional[float] = None
    actual_text: Optional[str] = None
    comments: Optional[str] = None
    corrective_action: Optional[str] = None


class InspectionChecklistItemResponse(InspectionChecklistItemBase):
    id: int
    checklist_id: int
    is_checked: bool
    result: Optional[str] = None
    actual_value: Optional[float] = None
    actual_text: Optional[str] = None
    checked_at: Optional[datetime] = None
    checked_by: Optional[int] = None

    class Config:
        from_attributes = True


class InspectionChecklistListResponse(BaseModel):
    items: List[InspectionChecklistResponse]
    total: int
    page: int
    size: int
    pages: int


class InspectionChecklistItemListResponse(BaseModel):
    items: List[InspectionChecklistItemResponse]
    total: int
    page: int
    size: int
    pages: int


# Noncompliant delivery alert schemas
class NoncompliantDeliveryAlert(BaseModel):
    delivery_id: int
    delivery_number: str
    supplier_name: str
    material_name: str
    inspection_status: str
    non_conformances: List[str]
    alert_date: datetime
    days_since_delivery: int


class NoncompliantDeliveryAlertList(BaseModel):
    alerts: List[NoncompliantDeliveryAlert]
    total_alerts: int
    critical_alerts: int
    warning_alerts: int 