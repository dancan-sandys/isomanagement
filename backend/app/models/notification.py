from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class NotificationType(str, enum.Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    ALERT = "ALERT"


class NotificationCategory(str, enum.Enum):
    SYSTEM = "SYSTEM"
    HACCP = "HACCP"
    PRP = "PRP"
    SUPPLIER = "SUPPLIER"
    TRACEABILITY = "TRACEABILITY"
    DOCUMENT = "DOCUMENT"
    USER = "USER"
    TRAINING = "TRAINING"
    AUDIT = "AUDIT"
    MAINTENANCE = "MAINTENANCE"


class NotificationPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False, default=NotificationType.INFO)
    category = Column(Enum(NotificationCategory), nullable=False, default=NotificationCategory.SYSTEM)
    priority = Column(Enum(NotificationPriority), nullable=False, default=NotificationPriority.MEDIUM)
    
    # Read status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # Action data
    action_url = Column(String(500))  # URL to navigate to when clicked
    action_text = Column(String(100))  # Text for action button
    
    # Additional data
    notification_data = Column(JSON)  # Store additional data as JSON
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # Optional expiration
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}')>"


# Update User model to include notifications relationship
# This will be added to the User model in user.py 