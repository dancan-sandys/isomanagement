from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ObjectiveType(str, enum.Enum):
    """Types of objectives"""
    CORPORATE = "corporate"
    DEPARTMENTAL = "departmental"
    OPERATIONAL = "operational"


class HierarchyLevel(str, enum.Enum):
    """Hierarchy levels for objectives"""
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"


class TrendDirection(str, enum.Enum):
    """Trend direction for objectives"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


class PerformanceColor(str, enum.Enum):
    """Performance color indicators"""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class DataSource(str, enum.Enum):
    """Data sources for objective tracking"""
    MANUAL = "manual"
    SYSTEM = "system"
    INTEGRATION = "integration"


class FoodSafetyObjective(Base):
    __tablename__ = "food_safety_objectives"

    id = Column(Integer, primary_key=True, index=True)
    objective_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    
    # Enhanced objective type and hierarchy
    objective_type = Column(
        Enum(ObjectiveType, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
        default=ObjectiveType.OPERATIONAL
    )
    hierarchy_level = Column(
        Enum(HierarchyLevel, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
        default=HierarchyLevel.OPERATIONAL
    )
    parent_objective_id = Column(Integer, ForeignKey("food_safety_objectives.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    
    # Enhanced measurement and tracking
    baseline_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=True)  # Changed from String to Float
    measurement_unit = Column(String(50))
    weight = Column(Float, default=1.0)  # Weight for KPI calculations
    measurement_frequency = Column(String(100))  # daily, weekly, monthly, quarterly, annually
    
    # Enhanced progress tracking
    trend_direction = Column(
        Enum(TrendDirection, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=True
    )
    performance_color = Column(
        Enum(PerformanceColor, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=True
    )
    automated_calculation = Column(Boolean, default=False)
    data_source = Column(
        Enum(DataSource, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        default=DataSource.MANUAL
    )
    
    # Existing fields
    frequency = Column(String(100))
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    review_frequency = Column(String(100))
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Enhanced tracking fields
    last_updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    parent_objective = relationship("FoodSafetyObjective", remote_side=[id], back_populates="child_objectives")
    child_objectives = relationship("FoodSafetyObjective", back_populates="parent_objective")
    department = relationship("Department", back_populates="objectives")
    responsible_person = relationship("User", foreign_keys=[responsible_person_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_updated_by_user = relationship("User", foreign_keys=[last_updated_by])
    fsms_integrations = relationship("FSMSRiskIntegration", back_populates="food_safety_objective")
    targets = relationship("ObjectiveTarget", back_populates="objective", cascade="all, delete-orphan")
    progress_entries = relationship("ObjectiveProgress", back_populates="objective", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_objectives_hierarchy", "parent_objective_id", "objective_type"),
        Index("ix_objectives_department", "department_id", "objective_type"),
        Index("ix_objectives_type_level", "objective_type", "hierarchy_level"),
    )

    def __repr__(self):
        return f"<FoodSafetyObjective(id={self.id}, code='{self.objective_code}', title='{self.title}', type='{self.objective_type}')>"


class ObjectiveTarget(Base):
    __tablename__ = "objective_targets"

    id = Column(Integer, primary_key=True, index=True)
    objective_id = Column(Integer, ForeignKey("food_safety_objectives.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    target_value = Column(Float, nullable=False)
    lower_threshold = Column(Float, nullable=True)  # for ranges or lower-is-better
    upper_threshold = Column(Float, nullable=True)
    weight = Column(Float, nullable=True, default=1.0)
    is_lower_better = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    objective = relationship("FoodSafetyObjective", back_populates="targets")
    department = relationship("Department", back_populates="objective_targets")
    created_by_user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_objective_target_period", "objective_id", "department_id", "period_start"),
        Index("ix_objective_target_department", "department_id", "period_start"),
    )


class ObjectiveProgress(Base):
    __tablename__ = "objective_progress"

    id = Column(Integer, primary_key=True, index=True)
    objective_id = Column(Integer, ForeignKey("food_safety_objectives.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    actual_value = Column(Float, nullable=False)
    attainment_percent = Column(Float, nullable=True)
    status = Column(String(20), nullable=True)  # on_track, at_risk, off_track
    evidence = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    objective = relationship("FoodSafetyObjective", back_populates="progress_entries")
    department = relationship("Department", back_populates="objective_progress")
    created_by_user = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_objective_progress_period", "objective_id", "department_id", "period_start"),
        Index("ix_objective_progress_department", "department_id", "period_start"),
        Index("ix_objective_progress_status", "status", "period_start"),
    )
