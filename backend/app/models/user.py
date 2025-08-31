from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    QA_MANAGER = "QA_MANAGER"
    QA_SPECIALIST = "QA_SPECIALIST"
    PRODUCTION_MANAGER = "PRODUCTION_MANAGER"
    PRODUCTION_OPERATOR = "PRODUCTION_OPERATOR"
    MAINTENANCE = "MAINTENANCE"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    SUPPLIER = "SUPPLIER"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING_APPROVAL)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_name = Column(String(100))  # Keep for backward compatibility
    position = Column(String(100))
    phone = Column(String(20))
    employee_id = Column(String(50), nullable=True)  # Removed unique=True, made nullable
    
    # Profile information
    profile_picture = Column(String(255))
    bio = Column(Text)
    
    # Security and audit fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    department = relationship("Department", foreign_keys=[department_id], viewonly=True)  # Make viewonly to avoid conflicts
    custom_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserPermission.user_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    dashboard_configurations = relationship("DashboardConfiguration", back_populates="user")
    
    # Actions Log relationships - Make viewonly to avoid conflicts during user creation
    assigned_actions = relationship("ActionLog", foreign_keys="ActionLog.assigned_to", back_populates="assigned_user", viewonly=True)
    created_actions = relationship("ActionLog", foreign_keys="ActionLog.assigned_by", back_populates="created_by_user", viewonly=True)
    action_progress_updates = relationship("ActionProgress", foreign_keys="ActionProgress.updated_by", back_populates="user", viewonly=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role_id={self.role_id})>"


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id})>" 