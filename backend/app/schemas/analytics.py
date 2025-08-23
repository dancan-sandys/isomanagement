# -*- coding: utf-8 -*-
"""
Advanced Analytics & Reporting System Schemas
Phase 4: Pydantic schemas for analytics, reporting, and business intelligence
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
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


class ChartType(str, Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    KPI_CARD = "kpi_card"


# Analytics Report schemas
class AnalyticsReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    report_config: Optional[Dict[str, Any]] = Field({}, description="Report configuration")
    chart_configs: Optional[Dict[str, Any]] = None
    export_formats: Optional[List[str]] = None
    is_public: bool = False
    department_id: Optional[int] = None


class AnalyticsReportCreate(AnalyticsReportBase):
    created_by: Optional[int] = Field(None, description="User ID who created the report")


class AnalyticsReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: Optional[ReportType] = None
    report_config: Optional[Dict[str, Any]] = None
    chart_configs: Optional[Dict[str, Any]] = None
    export_formats: Optional[List[str]] = None
    is_public: Optional[bool] = None
    department_id: Optional[int] = None
    status: Optional[ReportStatus] = None


class AnalyticsReportResponse(AnalyticsReportBase):
    id: int
    status: ReportStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    department_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# KPI schemas
class KPIBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    module: str = Field(..., min_length=1, max_length=100)
    calculation_method: str = Field(..., min_length=1, max_length=50)
    calculation_query: Optional[str] = None
    data_sources: Optional[Dict[str, Any]] = None
    aggregation_type: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = Field(None, max_length=50)
    decimal_places: int = Field(2, ge=0, le=10)
    target_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    alert_enabled: bool = False
    refresh_interval: int = Field(3600, ge=60)


class KPICreate(KPIBase):
    created_by: Optional[int] = Field(None, description="User ID who created the KPI")


class KPIUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    module: Optional[str] = Field(None, min_length=1, max_length=100)
    calculation_method: Optional[str] = Field(None, min_length=1, max_length=50)
    calculation_query: Optional[str] = None
    data_sources: Optional[Dict[str, Any]] = None
    aggregation_type: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = Field(None, max_length=50)
    decimal_places: Optional[int] = Field(None, ge=0, le=10)
    target_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    alert_enabled: Optional[bool] = None
    refresh_interval: Optional[int] = Field(None, ge=60)
    is_active: Optional[bool] = None


class KPIResponse(KPIBase):
    id: int
    is_active: bool
    last_calculation_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    creator_name: Optional[str] = None
    current_value: Optional[float] = None
    trend: Optional[str] = None  # increasing, decreasing, stable
    
    class Config:
        from_attributes = True


# KPI Value schemas
class KPIValueBase(BaseModel):
    value: float = Field(..., ge=0)
    department_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    context_data: Optional[Dict[str, Any]] = None


class KPIValueCreate(KPIValueBase):
    kpi_id: int


class KPIValueResponse(KPIValueBase):
    id: int
    kpi_id: int
    calculated_at: datetime
    department_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Dashboard schemas
class AnalyticsDashboardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = Field({}, description="Dashboard layout configuration")
    theme: str = Field("light", max_length=50)
    refresh_interval: int = Field(300, ge=30)
    is_public: bool = False
    department_id: Optional[int] = None


class AnalyticsDashboardCreate(AnalyticsDashboardBase):
    created_by: Optional[int] = Field(None, description="User ID who created the dashboard")


class AnalyticsDashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    theme: Optional[str] = Field(None, max_length=50)
    refresh_interval: Optional[int] = Field(None, ge=30)
    is_public: Optional[bool] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class AnalyticsDashboardResponse(AnalyticsDashboardBase):
    id: int
    is_active: bool
    is_default: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    department_name: Optional[str] = None
    widgets_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# Widget schemas
class DashboardWidgetBase(BaseModel):
    widget_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    position_x: int = Field(..., ge=0)
    position_y: int = Field(..., ge=0)
    width: int = Field(..., ge=1, le=12)
    height: int = Field(..., ge=1, le=12)
    data_source: Optional[str] = Field(None, max_length=100)
    data_config: Optional[Dict[str, Any]] = None
    chart_config: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=30)
    is_visible: bool = True


class DashboardWidgetCreate(DashboardWidgetBase):
    dashboard_id: int


class DashboardWidgetUpdate(BaseModel):
    widget_type: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, ge=1, le=12)
    height: Optional[int] = Field(None, ge=1, le=12)
    data_source: Optional[str] = Field(None, max_length=100)
    data_config: Optional[Dict[str, Any]] = None
    chart_config: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=30)
    is_visible: Optional[bool] = None


class DashboardWidgetResponse(DashboardWidgetBase):
    id: int
    dashboard_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Trend Analysis schemas
class TrendAnalysisBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    analysis_type: str = Field(..., min_length=1, max_length=50)
    data_source: str = Field(..., min_length=1, max_length=100)
    time_period: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    confidence_level: float = Field(0.95, ge=0.5, le=1.0)


class TrendAnalysisCreate(TrendAnalysisBase):
    created_by: Optional[int] = Field(None, description="User ID who created the analysis")


class TrendAnalysisUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    analysis_type: Optional[str] = Field(None, min_length=1, max_length=50)
    data_source: Optional[str] = Field(None, min_length=1, max_length=100)
    time_period: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    confidence_level: Optional[float] = Field(None, ge=0.5, le=1.0)
    is_active: Optional[bool] = None


class TrendAnalysisResponse(TrendAnalysisBase):
    id: int
    trend_direction: Optional[str] = None
    trend_strength: Optional[float] = None
    forecast_values: Optional[Dict[str, Any]] = None
    confidence_intervals: Optional[Dict[str, Any]] = None
    is_active: bool
    last_updated_at: datetime
    created_by: int
    created_at: datetime
    creator_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Analytics and reporting schemas
class AnalyticsSummary(BaseModel):
    total_reports: int
    total_kpis: int
    total_dashboards: int
    active_trend_analyses: int
    recent_reports: List[AnalyticsReportResponse]
    top_kpis: List[KPIResponse]
    system_health: Dict[str, Any]
    
    class Config:
        from_attributes = True


class KPIAnalytics(BaseModel):
    kpi_id: int
    kpi_name: str
    current_value: float
    target_value: Optional[float] = None
    trend: str  # increasing, decreasing, stable
    trend_percentage: float
    historical_values: List[KPIValueResponse]
    performance_status: str  # on_target, below_target, above_target
    alerts_count: int
    
    class Config:
        from_attributes = True


class ReportAnalytics(BaseModel):
    report_id: int
    report_title: str
    report_type: ReportType
    execution_count: int
    last_execution: Optional[datetime] = None
    average_execution_time: Optional[float] = None
    success_rate: float
    user_engagement: Dict[str, Any]
    
    class Config:
        from_attributes = True


class DashboardAnalytics(BaseModel):
    dashboard_id: int
    dashboard_name: str
    view_count: int
    last_viewed: Optional[datetime] = None
    average_session_duration: Optional[float] = None
    popular_widgets: List[Dict[str, Any]]
    user_feedback: Dict[str, Any]
    
    class Config:
        from_attributes = True
