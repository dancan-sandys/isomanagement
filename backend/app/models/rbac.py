from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# Permission types enum
class PermissionType(enum.Enum):
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    ASSIGN = "assign"
    EXPORT = "export"
    IMPORT = "import"
    MANAGE_PROGRAM = "manage_program"

# Module enum
class Module(enum.Enum):
    DASHBOARD = "dashboard"
    DOCUMENTS = "documents"
    HACCP = "haccp"
    PRP = "prp"
    SUPPLIERS = "suppliers"
    TRACEABILITY = "traceability"
    USERS = "users"
    ROLES = "roles"
    SETTINGS = "settings"
    NOTIFICATIONS = "notifications"
    AUDITS = "audits"
    TRAINING = "training"
    MAINTENANCE = "maintenance"
    COMPLAINTS = "complaints"
    NC_CAPA = "nc_capa"
    RISK_OPPORTUNITY = "risk_opportunity"
    MANAGEMENT_REVIEW = "management_review"
    ALLERGEN_LABEL = "allergen_label"

# Role-Permission association table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_editable = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    module = Column(Enum(Module), nullable=False)
    action = Column(Enum(PermissionType), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    granted = Column(Boolean, default=True, nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission")
    granted_by_user = relationship("User", foreign_keys=[granted_by]) 