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
    PASTEURIZED_MILK = "pasteurized_milk"
    FERMENTED_PRODUCTS = "fermented_products"


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
    PASTEURIZE = "pasteurize"
    FERMENT = "ferment"
    DRAIN = "drain"
    MOLD = "mold"
    CULTURE_ADDITION = "culture_addition"
    COAGULATION = "coagulation"


class LogEvent(str, enum.Enum):
    START = "start"
    READING = "reading"
    COMPLETE = "complete"
    DIVERT = "divert"
    DEVIATION = "deviation"
    ALERT = "alert"
    PARAMETER_RECORDED = "parameter_recorded"


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


class ProcessParameter(Base):
    __tablename__ = "process_parameters"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey("process_steps.id"), nullable=True)
    parameter_name = Column(String(100), nullable=False)  # temperature, time, pressure, etc.
    parameter_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # °C, seconds, bar, etc.
    target_value = Column(Float, nullable=True)
    tolerance_min = Column(Float, nullable=True)
    tolerance_max = Column(Float, nullable=True)
    is_within_tolerance = Column(Boolean, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    process = relationship("ProductionProcess")
    step = relationship("ProcessStep")
    recorder = relationship("User")

    __table_args__ = (
        Index("ix_process_parameters_process_time", "process_id", "recorded_at"),
    )


class ProcessDeviation(Base):
    __tablename__ = "process_deviations"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey("process_steps.id"), nullable=True)
    parameter_id = Column(Integer, ForeignKey("process_parameters.id"), nullable=True)
    deviation_type = Column(String(50), nullable=False)  # temperature, time, pressure, etc.
    expected_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    deviation_percent = Column(Float, nullable=True)
    severity = Column(String(20), nullable=False, default="low")  # low, medium, high, critical
    impact_assessment = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    process = relationship("ProductionProcess")
    step = relationship("ProcessStep")
    parameter = relationship("ProcessParameter")
    creator = relationship("User", foreign_keys=[created_by])
    resolver = relationship("User", foreign_keys=[resolved_by])


class ProcessAlert(Base):
    __tablename__ = "process_alerts"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # temperature_high, temperature_low, time_exceeded, etc.
    alert_level = Column(String(20), nullable=False, default="warning")  # info, warning, error, critical
    message = Column(Text, nullable=False)
    parameter_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    process = relationship("ProductionProcess")
    creator = relationship("User", foreign_keys=[created_by])
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, index=True)
    product_type = Column(SAEnum(ProductProcessType), nullable=False)
    specification_name = Column(String(100), nullable=False)
    specification_version = Column(String(20), nullable=False, default="1.0")
    is_active = Column(Boolean, default=True)
    steps = Column(JSON, nullable=False)  # Array of step specifications
    parameters = Column(JSON, nullable=True)  # Parameter specifications
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])


class ProcessSpecLink(Base):
    __tablename__ = "process_spec_links"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document_version = Column(String(20), nullable=False)
    locked_parameters = Column(JSON, nullable=True)  # { parameter_name: { target_value, tolerance_min, tolerance_max, unit? } }
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReleaseRecord(Base):
    __tablename__ = "release_records"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    checklist_results = Column(JSON, nullable=False)
    released_qty = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    verifier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    signature_hash = Column(String(256), nullable=True)

    process = relationship("ProductionProcess")


class ProcessTemplate(Base):
    __tablename__ = "process_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=False)
    product_type = Column(SAEnum(ProductProcessType), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(JSON, nullable=False)  # Array of step configurations
    parameters = Column(JSON, nullable=True)  # Parameter configurations
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])