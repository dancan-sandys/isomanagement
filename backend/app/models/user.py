from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
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
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING_APPROVAL)
    department = Column(String(100))
    position = Column(String(100))
    phone = Column(String(20))
    employee_id = Column(String(50), unique=True)
    
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
    
    # Relationships - Commented out until other models are implemented
    # audit_logs = relationship("AuditLog", back_populates="user")
    # document_approvals = relationship("DocumentApproval", back_populates="approver")
    # training_records = relationship("TrainingRecord", back_populates="user")
    # non_conformances = relationship("NonConformance", back_populates="reported_by")
    # corrective_actions = relationship("CorrectiveAction", back_populates="assigned_to")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


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