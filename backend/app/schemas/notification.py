from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.notification import NotificationType, NotificationCategory, NotificationPriority


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    category: NotificationCategory = NotificationCategory.SYSTEM
    priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    notification_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationSummary(BaseModel):
    total: int
    unread: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]


class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    categories: List[NotificationCategory] = []
    priority_levels: List[NotificationPriority] = []
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format 