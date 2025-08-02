from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationCategory, NotificationPriority
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse, 
    NotificationListResponse, NotificationSummary, NotificationPreferences
)
from app.schemas.common import ResponseModel, PaginationParams, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NotificationResponse])
async def get_notifications(
    pagination: PaginationParams = Depends(),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    category: Optional[NotificationCategory] = Query(None, description="Filter by category"),
    priority: Optional[NotificationPriority] = Query(None, description="Filter by priority"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by type"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of notifications for current user
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    # Apply filters
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    if category:
        query = query.filter(Notification.category == category)
    
    if priority:
        query = query.filter(Notification.priority == priority)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    # Filter out expired notifications
    query = query.filter(
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        )
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    offset = (pagination.page - 1) * pagination.size
    notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(pagination.size).all()
    
    # Calculate pagination info
    pages = (total + pagination.size - 1) // pagination.size
    has_next = pagination.page < pages
    has_prev = pagination.page > 1
    
    return PaginatedResponse(
        items=[NotificationResponse.from_orm(notification) for notification in notifications],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    limit: int = Query(10, description="Number of notifications to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get unread notifications for current user
    """
    notifications = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    ).order_by(desc(Notification.created_at)).limit(limit).all()
    
    return [NotificationResponse.from_orm(notification) for notification in notifications]


@router.get("/summary", response_model=NotificationSummary)
async def get_notification_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get notification summary for current user
    """
    # Get total notifications
    total = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    ).count()
    
    # Get unread notifications
    unread = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    ).count()
    
    # Get notifications by category
    by_category = {}
    for category in NotificationCategory:
        count = db.query(Notification).filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.category == category,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        ).count()
        if count > 0:
            by_category[category.value] = count
    
    # Get notifications by priority
    by_priority = {}
    for priority in NotificationPriority:
        count = db.query(Notification).filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.priority == priority,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        ).count()
        if count > 0:
            by_priority[priority.value] = count
    
    return NotificationSummary(
        total=total,
        unread=unread,
        by_category=by_category,
        by_priority=by_priority
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific notification
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return NotificationResponse.from_orm(notification)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    
    return NotificationResponse.from_orm(notification)


@router.put("/read-all", response_model=ResponseModel)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read
    """
    updated = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message=f"Marked {updated} notifications as read"
    )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Notification deleted successfully"
    )


@router.delete("/clear-read")
async def clear_read_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Clear all read notifications
    """
    deleted = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == True
        )
    ).delete()
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message=f"Cleared {deleted} read notifications"
    )


# Utility function to create notifications (can be used by other modules)
async def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.INFO,
    category: NotificationCategory = NotificationCategory.SYSTEM,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    action_url: Optional[str] = None,
    action_text: Optional[str] = None,
    notification_data: Optional[dict] = None,
    expires_at: Optional[datetime] = None
) -> Notification:
    """
    Create a new notification
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        category=category,
        priority=priority,
        action_url=action_url,
        action_text=action_text,
        notification_data=notification_data,
        expires_at=expires_at
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification 