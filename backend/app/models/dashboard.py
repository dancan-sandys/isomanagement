from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON, Date, Enum, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# Dashboard configuration and KPI models for ISO 22000 FSMS

class KPICategory(enum.Enum):
    HACCP_COMPLIANCE = "haccp_compliance"
    PRP_PERFORMANCE = "prp_performance" 
    NC_CAPA = "nc_capa"
    SUPPLIER_PERFORMANCE = "supplier_performance"
    TRAINING_COMPETENCY = "training_competency"
    DOCUMENT_CONTROL = "document_control"
    AUDIT_MANAGEMENT = "audit_management"
    RISK_MANAGEMENT = "risk_management"
    OPERATIONAL_METRICS = "operational_metrics"
    COMPLIANCE_SCORE = "compliance_score"

class ThresholdType(enum.Enum):
    ABOVE = "above"
    BELOW = "below"
    EQUALS = "equals"
    BETWEEN = "between"

class AlertLevel(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class WidgetSize(enum.Enum):
    SMALL = "small"      # 1x1
    MEDIUM = "medium"    # 2x1
    LARGE = "large"      # 2x2
    XLARGE = "xlarge"    # 3x2
    FULL = "full"        # Full width

class DashboardConfiguration(Base):
    """User-specific dashboard layout and preferences"""
    __tablename__ = "dashboard_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False, default="Default Dashboard")
    description = Column(Text, nullable=True)
    
    # Layout configuration stored as JSON
    layout_config = Column(JSON, nullable=True)  # Grid positions, sizes, etc.
    widget_preferences = Column(JSON, nullable=True)  # Widget-specific settings
    
    # Dashboard settings
    refresh_interval = Column(Integer, default=300)  # seconds
    theme = Column(String(50), default="light")
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="dashboard_configurations")
    role = relationship("Role")

class KPIDefinition(Base):
    """Defines KPIs and their calculation methods"""
    __tablename__ = "kpi_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # KPI categorization
    category = Column(Enum(KPICategory), nullable=False)
    module = Column(String(100), nullable=False)  # Maps to RBAC Module
    
    # Calculation configuration
    calculation_formula = Column(Text, nullable=True)  # SQL or formula
    data_sources = Column(JSON, nullable=True)  # Tables, fields used
    calculation_method = Column(String(100), default="sql")  # sql, python, api
    
    # Display configuration
    unit = Column(String(50), nullable=True)  # %, count, score, etc.
    decimal_places = Column(Integer, default=2)
    target_value = Column(Numeric(10, 2), nullable=True)
    target_operator = Column(String(10), default=">=")  # >=, <=, =, !=
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    requires_department_filter = Column(Boolean, default=False)
    update_frequency = Column(Integer, default=300)  # seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    kpi_values = relationship("KPIValue", back_populates="kpi_definition")
    dashboard_alerts = relationship("DashboardAlert", back_populates="kpi_definition")

class KPIValue(Base):
    """Stores calculated KPI values over time"""
    __tablename__ = "kpi_values"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_definition_id = Column(Integer, ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False)
    
    # Value and period
    value = Column(Numeric(15, 4), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Context filters
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    location_id = Column(Integer, nullable=True)  # For future use
    product_category_id = Column(Integer, nullable=True)  # For future use
    
    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    calculation_duration = Column(Integer, nullable=True)  # milliseconds
    kpi_metadata = Column(JSON, nullable=True)  # Additional context
    
    # Data quality indicators
    confidence_score = Column(Numeric(3, 2), default=1.00)  # 0.00 to 1.00
    data_completeness = Column(Numeric(3, 2), default=1.00)  # 0.00 to 1.00
    
    # Relationships
    kpi_definition = relationship("KPIDefinition", back_populates="kpi_values")
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_kpi_values_dept_period", "department_id", "period_start"),
        {'extend_existing': True}
    )

class DashboardWidget(Base):
    """Registry of available dashboard widgets"""
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Widget configuration
    component_name = Column(String(255), nullable=False)  # React component name
    category = Column(String(100), nullable=False)  # charts, kpis, tables, alerts
    widget_type = Column(String(100), nullable=False)  # line_chart, bar_chart, kpi_card, etc.
    
    # Permissions and access
    required_permissions = Column(JSON, nullable=True)  # Array of permission strings
    required_modules = Column(JSON, nullable=True)  # Array of module names
    
    # Layout configuration
    default_size = Column(Enum(WidgetSize), default=WidgetSize.MEDIUM)
    min_size = Column(JSON, default={"w": 1, "h": 1})
    max_size = Column(JSON, default={"w": 4, "h": 4})
    
    # Widget configuration schema
    config_schema = Column(JSON, nullable=True)  # JSON schema for widget config
    default_config = Column(JSON, nullable=True)  # Default configuration
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0.0")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DashboardAlert(Base):
    """Alert rules and thresholds for KPIs"""
    __tablename__ = "dashboard_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_definition_id = Column(Integer, ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False)
    
    # Alert configuration
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Threshold settings
    threshold_type = Column(Enum(ThresholdType), nullable=False)
    threshold_value = Column(Numeric(15, 4), nullable=False)
    threshold_value_max = Column(Numeric(15, 4), nullable=True)  # For BETWEEN type
    
    # Alert settings
    alert_level = Column(Enum(AlertLevel), nullable=False)
    consecutive_periods = Column(Integer, default=1)  # Trigger after N periods
    
    # Notification configuration
    notification_config = Column(JSON, nullable=True)  # Email, SMS, etc.
    notification_recipients = Column(JSON, nullable=True)  # User IDs, emails
    
    # Cooldown and frequency
    cooldown_minutes = Column(Integer, default=60)  # Min time between alerts
    max_alerts_per_day = Column(Integer, default=10)
    
    # Context filters (inherit from KPI if null)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    kpi_definition = relationship("KPIDefinition", back_populates="dashboard_alerts")

class ScheduledReport(Base):
    """Scheduled report configurations"""
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Report configuration
    report_type = Column(String(100), nullable=False)  # dashboard_summary, kpi_report, etc.
    report_config = Column(JSON, nullable=False)  # KPIs, filters, format settings
    
    # Schedule configuration
    schedule_expression = Column(String(100), nullable=False)  # Cron expression
    timezone = Column(String(50), default="UTC")
    
    # Output configuration
    output_format = Column(String(20), default="pdf")  # pdf, excel, csv
    recipients = Column(JSON, nullable=False)  # Email addresses
    
    # Execution tracking
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_status = Column(String(50), nullable=True)  # success, failed, running
    last_run_error = Column(Text, nullable=True)
    execution_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")

class DashboardAuditLog(Base):
    """Audit log for dashboard access and changes"""
    __tablename__ = "dashboard_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Action details
    action = Column(String(100), nullable=False)  # view, export, configure, etc.
    resource_type = Column(String(100), nullable=False)  # dashboard, widget, kpi, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Action metadata
    details = Column(JSON, nullable=True)  # Additional context
    duration_ms = Column(Integer, nullable=True)  # Action duration
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

# Department model is defined in app.models.departments; import it here to avoid duplicate table definitions
from app.models.departments import Department
