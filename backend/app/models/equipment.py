from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class MaintenanceType(str, enum.Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"


# Added work order status/priority enums
class WorkOrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class WorkOrderPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    # New fields for activity and risk
    is_active = Column(Boolean, default=True, nullable=False)
    critical_to_food_safety = Column(Boolean, default=False, nullable=False)

    maintenance_plans = relationship("MaintenancePlan", back_populates="equipment", cascade="all, delete-orphan")
    calibration_plans = relationship("CalibrationPlan", back_populates="equipment", cascade="all, delete-orphan")


class MaintenancePlan(Base):
    __tablename__ = "maintenance_plans"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    frequency_days = Column(Integer, nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    last_performed_at = Column(DateTime(timezone=True), nullable=True)
    next_due_at = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    # PRP/SOP linkage (ISO)
    prp_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    equipment = relationship("Equipment", back_populates="maintenance_plans")


class MaintenanceWorkOrder(Base):
    __tablename__ = "maintenance_work_orders"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("maintenance_plans.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    # New work order lifecycle fields
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING, nullable=False)
    priority = Column(Enum(WorkOrderPriority), default=WorkOrderPriority.MEDIUM, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Verification tracking (ISO)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)


class CalibrationPlan(Base):
    __tablename__ = "calibration_plans"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    frequency_days = Column(Integer, nullable=False, default=365)
    schedule_date = Column(DateTime(timezone=True), nullable=False)
    last_calibrated_at = Column(DateTime(timezone=True), nullable=True)
    next_due_at = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    equipment = relationship("Equipment", back_populates="calibration_plans")


class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("calibration_plans.id"), nullable=False)
    performed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    # ISO traceability metadata
    certificate_number = Column(String(100), nullable=True)
    calibrated_by = Column(String(200), nullable=True)
    result = Column(String(50), nullable=True)  # pass/fail
    comments = Column(Text, nullable=True)


