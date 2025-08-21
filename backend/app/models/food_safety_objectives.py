from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FoodSafetyObjective(Base):
    __tablename__ = "food_safety_objectives"

    id = Column(Integer, primary_key=True, index=True)
    objective_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    target_value = Column(String(100))
    measurement_unit = Column(String(50))
    frequency = Column(String(100))
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    review_frequency = Column(String(100))
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    responsible_person = relationship("User", foreign_keys=[responsible_person_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    fsms_integrations = relationship("FSMSRiskIntegration", back_populates="food_safety_objective")
    targets = relationship("ObjectiveTarget", back_populates="objective", cascade="all, delete-orphan")
    progress_entries = relationship("ObjectiveProgress", back_populates="objective", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FoodSafetyObjective(id={self.id}, code='{self.objective_code}', title='{self.title}')>"

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

    objective = relationship("FoodSafetyObjective", back_populates="targets")

    __table_args__ = (
        Index("ix_objective_target_period", "objective_id", "department_id", "period_start"),
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

    objective = relationship("FoodSafetyObjective", back_populates="progress_entries")

    __table_args__ = (
        Index("ix_objective_progress_period", "objective_id", "department_id", "period_start"),
    )
