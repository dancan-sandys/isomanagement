from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, Enum as SAEnum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ProductProcessType(str, enum.Enum):
    FRESH_MILK = "fresh_milk"
    YOGHURT = "yoghurt"
    MALA = "mala"
    CHEESE = "cheese"


class ProcessStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    DIVERTED = "diverted"
    COMPLETED = "completed"


class StepType(str, enum.Enum):
    HEAT = "heat"
    HOLD = "hold"
    COOL = "cool"
    ADD_INGREDIENT = "add_ingredient"
    INOCULATE = "inoculate"
    CUT_CURD = "cut_curd"
    PRESS = "press"
    PACK = "pack"
    TRANSFER_COLD_ROOM = "transfer_cold_room"
    AGE = "age"


class LogEvent(str, enum.Enum):
    START = "start"
    READING = "reading"
    COMPLETE = "complete"
    DIVERT = "divert"


class ProductionProcess(Base):
    __tablename__ = "production_processes"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    process_type = Column(SAEnum(ProductProcessType), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SAEnum(ProcessStatus), nullable=False, default=ProcessStatus.IN_PROGRESS)
    start_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    spec = Column(JSON, nullable=True)  # Holds temperature/time targets per step
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    steps = relationship("ProcessStep", back_populates="process", cascade="all, delete-orphan")
    logs = relationship("ProcessLog", back_populates="process", cascade="all, delete-orphan")
    yields = relationship("YieldRecord", back_populates="process", cascade="all, delete-orphan")
    transfers = relationship("ColdRoomTransfer", back_populates="process", cascade="all, delete-orphan")
    aging_records = relationship("AgingRecord", back_populates="process", cascade="all, delete-orphan")


class ProcessStep(Base):
    __tablename__ = "process_steps"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    step_type = Column(SAEnum(StepType), nullable=False)
    sequence = Column(Integer, nullable=False)
    target_temp_c = Column(Float, nullable=True)
    target_time_seconds = Column(Integer, nullable=True)
    tolerance_c = Column(Float, nullable=True)
    required = Column(Boolean, default=True)
    step_metadata = Column(JSON, nullable=True)

    process = relationship("ProductionProcess", back_populates="steps")

    __table_args__ = (
        Index("ix_process_steps_process_seq", "process_id", "sequence"),
    )


class ProcessLog(Base):
    __tablename__ = "process_logs"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey("process_steps.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    event = Column(SAEnum(LogEvent), nullable=False)
    measured_temp_c = Column(Float, nullable=True)
    note = Column(Text, nullable=True)
    auto_flag = Column(Boolean, default=False)
    source = Column(String(20), default="manual")  # manual, iot

    process = relationship("ProductionProcess", back_populates="logs")
    step = relationship("ProcessStep")

    __table_args__ = (
        Index("ix_process_logs_process_time", "process_id", "timestamp"),
    )


class YieldRecord(Base):
    __tablename__ = "yield_records"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    output_qty = Column(Float, nullable=False)
    expected_qty = Column(Float, nullable=True)
    unit = Column(String(20), nullable=False)
    overrun_percent = Column(Float, nullable=True)  # +overrun / -underrun
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    process = relationship("ProductionProcess", back_populates="yields")


class ColdRoomTransfer(Base):
    __tablename__ = "cold_room_transfers"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    location = Column(String(100), nullable=True)
    lot_number = Column(String(50), nullable=True)
    transferred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    process = relationship("ProductionProcess", back_populates="transfers")


class AgingRecord(Base):
    __tablename__ = "aging_records"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    room_temperature_c = Column(Float, nullable=True)
    target_temp_min_c = Column(Float, nullable=True)
    target_temp_max_c = Column(Float, nullable=True)
    target_days = Column(Integer, nullable=True)
    room_location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    process = relationship("ProductionProcess", back_populates="aging_records")

