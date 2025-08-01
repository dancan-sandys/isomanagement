from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ResponseModel(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class BaseModelWithTimestamps(BaseModel):
    """Base model with timestamp fields"""
    created_at: datetime
    updated_at: datetime


class BaseModelWithAudit(BaseModelWithTimestamps):
    """Base model with audit fields"""
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class FilterParams(BaseModel):
    """Generic filter parameters"""
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(None, regex="^(asc|desc)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ExportParams(BaseModel):
    """Export parameters"""
    format: str = Field("xlsx", regex="^(xlsx|csv|pdf)$")
    include_headers: bool = True
    filters: Optional[Dict[str, Any]] = None


class BulkActionParams(BaseModel):
    """Bulk action parameters"""
    ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., regex="^(delete|activate|deactivate|export)$")


class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    file_path: str
    file_size: int
    file_type: str
    upload_time: datetime


class NotificationParams(BaseModel):
    """Notification parameters"""
    title: str
    message: str
    notification_type: str = Field("info", regex="^(info|success|warning|error)$")
    recipients: List[int] = []
    send_email: bool = True
    send_sms: bool = False


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True 