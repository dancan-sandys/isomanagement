# -*- coding: utf-8 -*-
"""
Advanced Analytics & Reporting System Models
Phase 4: Comprehensive analytics, reporting, and business intelligence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ReportType(str, Enum):
    KPI_DASHBOARD = "kpi_dashboard"
    COMPLIANCE_REPORT = "compliance_report"
    PERFORMANCE_REPORT = "performance_report"
    TREND_ANALYSIS = "trend_analysis"
    AUDIT_REPORT = "audit_report"
    RISK_REPORT = "risk_report"
    ACTION_REPORT = "action_report"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class AnalyticsReport(Base):
    """Main analytics report table"""
    __tablename__ = "analytics_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default=ReportStatus.DRAFT, index=True)
    
    # Report configuration
    report_config = Column(JSON, nullable=False)  # Filters, date ranges, KPIs, etc.
    chart_configs = Column(JSON, nullable=True)  # Chart configurations
    export_formats = Column(JSON, nullable=True)  # PDF, Excel, CSV, etc.
    
    # Access control
    is_public = Column(Boolean, default=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    department = relationship("Department", foreign_keys=[department_id])


class KPI(Base):
    """Key Performance Indicators"""
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # KPI configuration
    category = Column(String(100), nullable=False, index=True)  # compliance, performance, quality, etc.
    module = Column(String(100), nullable=False, index=True)  # haccp, prp, audit, etc.
    calculation_method = Column(String(50), nullable=False)  # sql, python, aggregation
    
    # Calculation details
    calculation_query = Column(Text, nullable=True)  # SQL query or calculation logic
    data_sources = Column(JSON, nullable=True)  # Tables and fields used
    aggregation_type = Column(String(50), nullable=True)  # sum, avg, count, min, max
    
    # Display configuration
    unit = Column(String(50), nullable=True)  # %, count, score, etc.
    decimal_places = Column(Integer, default=2)
    target_value = Column(Numeric(10, 4), nullable=True)
    min_value = Column(Numeric(10, 4), nullable=True)
    max_value = Column(Numeric(10, 4), nullable=True)
    
    # Thresholds and alerts
    warning_threshold = Column(Numeric(10, 4), nullable=True)
    critical_threshold = Column(Numeric(10, 4), nullable=True)
    alert_enabled = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    refresh_interval = Column(Integer, default=3600)  # seconds
    last_calculation_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    analytics_values = relationship("AnalyticsKPIValue", back_populates="kpi", cascade="all, delete-orphan")


class AnalyticsKPIValue(Base):
    """Analytics KPI historical values"""
    __tablename__ = "analytics_kpi_values"

    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey("kpis.id"), nullable=False, index=True)
    
    # Value details
    value = Column(Numeric(10, 4), nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Context
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Additional metadata
    context_data = Column(JSON, nullable=True)  # Additional context information
    
    # Relationships
    kpi = relationship("KPI", back_populates="analytics_values")
    department = relationship("Department", foreign_keys=[department_id])


class AnalyticsDashboard(Base):
    """Analytics dashboards"""
    __tablename__ = "analytics_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Dashboard configuration
    layout_config = Column(JSON, nullable=False)  # Widget positions and sizes
    theme = Column(String(50), default="light")
    refresh_interval = Column(Integer, default=300)  # seconds
    
    # Access control
    is_public = Column(Boolean, default=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False, index=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    department = relationship("Department", foreign_keys=[department_id])
    widgets = relationship("AnalyticsDashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")


class AnalyticsDashboardWidget(Base):
    """Analytics dashboard widgets"""
    __tablename__ = "analytics_dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("analytics_dashboards.id"), nullable=False, index=True)
    
    # Widget configuration
    widget_type = Column(String(50), nullable=False)  # chart, kpi, table, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Position and size
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # Data configuration
    data_source = Column(String(100), nullable=True)  # kpi, report, custom query
    data_config = Column(JSON, nullable=True)  # Configuration for data source
    chart_config = Column(JSON, nullable=True)  # Chart-specific configuration
    
    # Display settings
    refresh_interval = Column(Integer, nullable=True)  # seconds
    is_visible = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("AnalyticsDashboard", back_populates="widgets")


class TrendAnalysis(Base):
    """Trend analysis results"""
    __tablename__ = "trend_analyses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Analysis configuration
    analysis_type = Column(String(50), nullable=False)  # linear, seasonal, cyclical
    data_source = Column(String(100), nullable=False)  # kpi, custom query
    time_period = Column(String(50), nullable=False)  # daily, weekly, monthly
    
    # Analysis parameters
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    confidence_level = Column(Float, default=0.95)
    
    # Results
    trend_direction = Column(String(20), nullable=True)  # increasing, decreasing, stable
    trend_strength = Column(Float, nullable=True)  # 0-1 scale
    forecast_values = Column(JSON, nullable=True)  # Predicted values
    confidence_intervals = Column(JSON, nullable=True)  # Confidence intervals
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
