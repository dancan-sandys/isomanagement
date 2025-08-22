from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Hierarchy support
    parent_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    
    # Department management
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Status and metadata
    status = Column(String(20), default="active")  # active, inactive, archived
    color_code = Column(String(7), nullable=True)  # Hex color for UI display
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    parent_department = relationship("Department", remote_side=[id], back_populates="child_departments")
    child_departments = relationship("Department", back_populates="parent_department")
    manager = relationship("User", foreign_keys=[manager_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    users = relationship("User", back_populates="department")
    objectives = relationship("FoodSafetyObjective", back_populates="department")
    objective_targets = relationship("ObjectiveTarget", back_populates="department")
    objective_progress = relationship("ObjectiveProgress", back_populates="department")

    __table_args__ = (
        Index("ix_departments_hierarchy", "parent_department_id", "status"),
        Index("ix_departments_manager", "manager_id", "status"),
    )

    def __repr__(self):
        return f"<Department(id={self.id}, code='{self.department_code}', name='{self.name}')>"


class DepartmentUser(Base):
    __tablename__ = "department_users"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Role within department
    role = Column(String(100), nullable=True)  # manager, member, supervisor, etc.
    
    # Assignment period
    assigned_from = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_until = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    department = relationship("Department")
    user = relationship("User")
    created_by_user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_department_users_active", "department_id", "user_id", "is_active"),
        Index("ix_department_users_period", "assigned_from", "assigned_until"),
    )

    def __repr__(self):
        return f"<DepartmentUser(department_id={self.department_id}, user_id={self.user_id}, role='{self.role}')>"
