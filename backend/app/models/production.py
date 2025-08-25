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


class MaterialConsumption(Base):
    __tablename__ = "material_consumptions"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    delivery_id = Column(Integer, ForeignKey("incoming_deliveries.id"), nullable=True)
    lot_number = Column(String(50))
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    consumed_at = Column(DateTime(timezone=True), server_default=func.now())
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text)

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


# Enhanced Process Monitoring Models for ISO 22000 Compliance

class ProcessControlChart(Base):
    """Control chart data for Statistical Process Control (SPC) - ISO 22000:2018 Clause 8.5"""
    __tablename__ = "process_control_charts"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False)
    chart_type = Column(String(20), nullable=False)  # X-bar, R, CUSUM, EWMA
    sample_size = Column(Integer, nullable=False, default=5)
    target_value = Column(Float, nullable=False)
    upper_control_limit = Column(Float, nullable=False)
    lower_control_limit = Column(Float, nullable=False)
    upper_warning_limit = Column(Float, nullable=True)
    lower_warning_limit = Column(Float, nullable=True)
    specification_upper = Column(Float, nullable=True)
    specification_lower = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    process = relationship("ProductionProcess")
    control_points = relationship("ProcessControlPoint", back_populates="control_chart", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_control_charts_process_param", "process_id", "parameter_name"),
    )


class ProcessControlPoint(Base):
    """Individual control chart data points for trend analysis"""
    __tablename__ = "process_control_points"

    id = Column(Integer, primary_key=True, index=True)
    control_chart_id = Column(Integer, ForeignKey("process_control_charts.id"), nullable=False, index=True)
    parameter_id = Column(Integer, ForeignKey("process_parameters.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    measured_value = Column(Float, nullable=False)
    subgroup_range = Column(Float, nullable=True)  # For R-charts
    cumulative_sum = Column(Float, nullable=True)  # For CUSUM charts
    moving_average = Column(Float, nullable=True)  # For EWMA charts
    is_out_of_control = Column(Boolean, default=False)
    control_rule_violated = Column(String(50), nullable=True)  # Nelson rules
    notes = Column(Text, nullable=True)

    control_chart = relationship("ProcessControlChart", back_populates="control_points")
    parameter = relationship("ProcessParameter")

    __table_args__ = (
        Index("ix_control_points_chart_time", "control_chart_id", "timestamp"),
    )


class ProcessCapabilityStudy(Base):
    """Process capability analysis data - ISO 22000:2018 requirements"""
    __tablename__ = "process_capability_studies"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False)
    study_period_start = Column(DateTime(timezone=True), nullable=False)
    study_period_end = Column(DateTime(timezone=True), nullable=False)
    sample_size = Column(Integer, nullable=False)
    mean_value = Column(Float, nullable=False)
    standard_deviation = Column(Float, nullable=False)
    specification_upper = Column(Float, nullable=False)
    specification_lower = Column(Float, nullable=False)
    cp_index = Column(Float, nullable=True)  # Process capability
    cpk_index = Column(Float, nullable=True)  # Process capability adjusted for centering
    pp_index = Column(Float, nullable=True)  # Process performance
    ppk_index = Column(Float, nullable=True)  # Process performance adjusted for centering
    process_sigma_level = Column(Float, nullable=True)
    defect_rate_ppm = Column(Float, nullable=True)  # Parts per million defects
    is_capable = Column(Boolean, nullable=True)
    study_notes = Column(Text, nullable=True)
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    process = relationship("ProductionProcess")
    conductor = relationship("User", foreign_keys=[conducted_by])
    approver = relationship("User", foreign_keys=[approved_by])


class YieldAnalysisReport(Base):
    """Comprehensive yield analysis reports - ISO 22000:2018 monitoring requirements"""
    __tablename__ = "yield_analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    analysis_period_start = Column(DateTime(timezone=True), nullable=False)
    analysis_period_end = Column(DateTime(timezone=True), nullable=False)
    total_input_quantity = Column(Float, nullable=False)
    total_output_quantity = Column(Float, nullable=False)
    conforming_output_quantity = Column(Float, nullable=False)
    non_conforming_quantity = Column(Float, nullable=False)
    rework_quantity = Column(Float, nullable=False, default=0.0)
    waste_quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(20), nullable=False)
    
    # Key Performance Indicators
    first_pass_yield = Column(Float, nullable=False)  # % conforming units first time
    rolled_throughput_yield = Column(Float, nullable=True)  # RTY for multi-step processes
    overall_yield = Column(Float, nullable=False)  # Total output / Total input
    quality_rate = Column(Float, nullable=False)  # % conforming units
    rework_rate = Column(Float, nullable=False)  # % requiring rework
    waste_rate = Column(Float, nullable=False)  # % waste
    
    # Root Cause Analysis References
    primary_loss_category = Column(String(100), nullable=True)
    secondary_loss_reasons = Column(JSON, nullable=True)  # Array of loss reasons
    improvement_opportunities = Column(JSON, nullable=True)  # Array of opportunities
    corrective_actions_taken = Column(JSON, nullable=True)  # Array of actions
    
    # Analysis metadata
    analysis_method = Column(String(50), default="standard")  # standard, lean, six_sigma
    baseline_comparison = Column(JSON, nullable=True)  # Previous period comparison
    trend_analysis = Column(JSON, nullable=True)  # Trend data
    statistical_significance = Column(Boolean, nullable=True)
    confidence_level = Column(Float, nullable=True, default=95.0)
    
    analyzed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    process = relationship("ProductionProcess")
    analyzer = relationship("User", foreign_keys=[analyzed_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    defect_categories = relationship("YieldDefectCategory", back_populates="yield_report", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_yield_reports_process_period", "process_id", "analysis_period_start", "analysis_period_end"),
    )


class YieldDefectCategory(Base):
    """Defect categorization for yield analysis - Pareto analysis support"""
    __tablename__ = "yield_defect_categories"

    id = Column(Integer, primary_key=True, index=True)
    yield_report_id = Column(Integer, ForeignKey("yield_analysis_reports.id"), nullable=False, index=True)
    defect_type = Column(String(100), nullable=False)
    defect_description = Column(Text, nullable=True)
    defect_count = Column(Integer, nullable=False)
    defect_quantity = Column(Float, nullable=False)
    defect_cost = Column(Float, nullable=True)
    percentage_of_total = Column(Float, nullable=False)
    cumulative_percentage = Column(Float, nullable=False)
    is_critical_to_quality = Column(Boolean, default=False)
    root_cause_category = Column(String(100), nullable=True)  # man, machine, material, method, environment
    corrective_action_required = Column(Boolean, default=True)
    prevention_method = Column(Text, nullable=True)

    yield_report = relationship("YieldAnalysisReport", back_populates="defect_categories")


class ProcessMonitoringDashboard(Base):
    """Real-time monitoring dashboard configuration"""
    __tablename__ = "process_monitoring_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_name = Column(String(100), nullable=False)
    process_type = Column(SAEnum(ProductProcessType), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    dashboard_config = Column(JSON, nullable=False)  # Widget configurations
    refresh_interval_seconds = Column(Integer, default=30)
    alert_thresholds = Column(JSON, nullable=True)  # Custom alert configurations
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")


class ProcessMonitoringAlert(Base):
    """Enhanced process monitoring alerts with escalation"""
    __tablename__ = "process_monitoring_alerts"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("production_processes.id"), nullable=False, index=True)
    control_chart_id = Column(Integer, ForeignKey("process_control_charts.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # control_limit, trend, capability, yield
    severity_level = Column(String(20), nullable=False)  # info, warning, critical, emergency
    alert_title = Column(String(200), nullable=False)
    alert_message = Column(Text, nullable=False)
    parameter_name = Column(String(100), nullable=True)
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    trend_direction = Column(String(20), nullable=True)  # increasing, decreasing, stable
    control_rule = Column(String(100), nullable=True)  # Nelson rules, Western Electric rules
    
    # Escalation and Response
    auto_generated = Column(Boolean, default=True)
    requires_immediate_action = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=1)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # ISO 22000 Compliance
    food_safety_impact = Column(Boolean, default=False)
    ccp_affected = Column(Boolean, default=False)  # Critical Control Point
    oprp_affected = Column(Boolean, default=False)  # Operational Prerequisite Program
    corrective_action_required = Column(Boolean, default=False)
    verification_required = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    process = relationship("ProductionProcess")
    control_chart = relationship("ProcessControlChart")
    assignee = relationship("User", foreign_keys=[assigned_to])
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
    resolver = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index("ix_monitoring_alerts_process_severity", "process_id", "severity_level"),
        Index("ix_monitoring_alerts_unresolved", "resolved", "created_at"),
    )