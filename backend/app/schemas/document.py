from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    POLICY = "policy"
    PROCEDURE = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    FORM = "form"
    RECORD = "record"
    MANUAL = "manual"
    SPECIFICATION = "specification"
    PLAN = "plan"
    CHECKLIST = "checklist"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class DocumentCategory(str, Enum):
    HACCP = "haccp"
    PRP = "prp"
    TRAINING = "training"
    AUDIT = "audit"
    MAINTENANCE = "maintenance"
    SUPPLIER = "supplier"
    QUALITY = "quality"
    SAFETY = "safety"
    GENERAL = "general"
    PRODUCTION = "production"
    HR = "hr"
    FINANCE = "finance"


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    document_number: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    document_type: DocumentType
    category: DocumentCategory
    department: Optional[str] = Field(None, max_length=100)
    product_line: Optional[str] = Field(None, max_length=100)
    applicable_products: Optional[List[int]] = None
    keywords: Optional[str] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    category: Optional[DocumentCategory] = None
    status: Optional[DocumentStatus] = None
    department: Optional[str] = Field(None, max_length=100)
    product_line: Optional[str] = Field(None, max_length=100)
    applicable_products: Optional[List[int]] = None
    keywords: Optional[str] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None


class DocumentVersionCreate(BaseModel):
    change_description: str = Field(..., min_length=1)
    change_reason: str = Field(..., min_length=1)


class DocumentApprovalCreate(BaseModel):
    approver_id: int
    approval_order: int = Field(..., ge=1)
    comments: Optional[str] = None


class DocumentFilter(BaseModel):
    search: Optional[str] = None
    category: Optional[DocumentCategory] = None
    status: Optional[DocumentStatus] = None
    document_type: Optional[DocumentType] = None
    department: Optional[str] = None
    product_line: Optional[str] = None
    created_by: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    review_date_from: Optional[datetime] = None
    review_date_to: Optional[datetime] = None
    keywords: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    document_number: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    category: DocumentCategory
    status: DocumentStatus
    version: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    department: Optional[str] = None
    product_line: Optional[str] = None
    applicable_products: Optional[List[int]] = None
    keywords: Optional[str] = None
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DocumentVersionResponse(BaseModel):
    id: int
    version_number: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    change_description: Optional[str] = None
    change_reason: Optional[str] = None
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    is_current: bool = False

    model_config = {"from_attributes": True}


class DocumentChangeLogResponse(BaseModel):
    id: int
    change_type: str
    change_description: Optional[str] = None
    old_version: Optional[str] = None
    new_version: Optional[str] = None
    changed_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentApprovalResponse(BaseModel):
    id: int
    approver_id: int
    approval_order: int
    status: str
    comments: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    document_type: DocumentType
    category: DocumentCategory
    template_content: Optional[str] = None


class DocumentTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    document_type: DocumentType
    category: DocumentCategory
    template_file_path: Optional[str] = None
    template_content: Optional[str] = None
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DocumentTemplateVersionCreate(BaseModel):
    change_description: str
    template_content: Optional[str] = None


class DocumentTemplateVersionResponse(BaseModel):
    id: int
    template_id: int
    version_number: str
    template_content: Optional[str] = None
    change_description: Optional[str] = None
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentTemplateApprovalCreate(BaseModel):
    approver_id: int
    approval_order: int
    comments: Optional[str] = None


class BulkDocumentAction(BaseModel):
    document_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., pattern="^(archive|obsolete|activate|delete|export)$")
    reason: Optional[str] = None


class DocumentStatusChangeRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for status change")


class DocumentVersionCreateRequest(BaseModel):
    change_description: str = Field(..., min_length=1, description="Description of changes made")
    change_reason: str = Field(..., min_length=1, description="Reason for creating new version")


class DocumentStats(BaseModel):
    total_documents: int
    documents_by_status: Dict[str, int]
    documents_by_category: Dict[str, int]
    documents_by_type: Dict[str, int]
    pending_reviews: int
    expired_documents: int
    documents_requiring_approval: int 