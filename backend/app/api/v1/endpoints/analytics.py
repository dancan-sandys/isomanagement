# -*- coding: utf-8 -*-
"""
Analytics API Endpoints
Phase 4: FastAPI endpoints for analytics, reporting, and business intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from sqlalchemy import desc

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsReportCreate, AnalyticsReportUpdate, AnalyticsReportResponse,
    KPICreate, KPIUpdate, KPIResponse, KPIValueCreate, KPIValueResponse,
    AnalyticsDashboardCreate, AnalyticsDashboardUpdate, AnalyticsDashboardResponse,
    DashboardWidgetCreate, DashboardWidgetUpdate, DashboardWidgetResponse,
    TrendAnalysisCreate, TrendAnalysisUpdate, TrendAnalysisResponse,
    AnalyticsSummary, KPIAnalytics, ReportAnalytics, DashboardAnalytics,
    ReportType, ReportStatus
)

router = APIRouter()


# Analytics Summary
@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Get comprehensive analytics summary"""
    service = AnalyticsService(db)
    return service.get_analytics_summary()


# Analytics Reports
@router.post("/reports", response_model=AnalyticsReportResponse)
def create_report(payload: AnalyticsReportCreate, db: Session = Depends(get_db)):
    """Create a new analytics report"""
    service = AnalyticsService(db)
    try:
        report = service.create_report(payload.model_dump())
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports", response_model=List[AnalyticsReportResponse])
def list_reports(
    report_type: Optional[ReportType] = Query(None),
    status: Optional[ReportStatus] = Query(None),
    is_public: Optional[bool] = Query(None),
    department_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List analytics reports with filtering"""
    service = AnalyticsService(db)
    reports = service.list_reports(
        report_type=report_type,
        status=status,
        is_public=is_public,
        department_id=department_id,
        limit=limit,
        offset=offset
    )
    return reports


@router.get("/reports/{report_id}", response_model=AnalyticsReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get analytics report by ID"""
    service = AnalyticsService(db)
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/reports/{report_id}", response_model=AnalyticsReportResponse)
def update_report(report_id: int, payload: AnalyticsReportUpdate, db: Session = Depends(get_db)):
    """Update an analytics report"""
    service = AnalyticsService(db)
    report = service.update_report(report_id, payload.model_dump(exclude_unset=True))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports/{report_id}/analytics", response_model=ReportAnalytics)
def get_report_analytics(report_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific report"""
    service = AnalyticsService(db)
    analytics = service.get_report_analytics(report_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Report not found")
    return analytics


# KPIs
@router.post("/kpis", response_model=KPIResponse)
def create_kpi(payload: KPICreate, db: Session = Depends(get_db)):
    """Create a new KPI"""
    service = AnalyticsService(db)
    try:
        kpi = service.create_kpi(payload.model_dump())
        return kpi
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kpis", response_model=List[KPIResponse])
def list_kpis(
    category: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List KPIs with filtering"""
    service = AnalyticsService(db)
    kpis = service.list_kpis(
        category=category,
        module=module,
        is_active=is_active,
        limit=limit,
        offset=offset
    )
    return kpis


@router.get("/kpis/{kpi_id}", response_model=KPIResponse)
def get_kpi(kpi_id: int, db: Session = Depends(get_db)):
    """Get KPI by ID"""
    service = AnalyticsService(db)
    kpi = service.get_kpi(kpi_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    return kpi


@router.put("/kpis/{kpi_id}", response_model=KPIResponse)
def update_kpi(kpi_id: int, payload: KPIUpdate, db: Session = Depends(get_db)):
    """Update a KPI"""
    service = AnalyticsService(db)
    kpi = service.update_kpi(kpi_id, payload.model_dump(exclude_unset=True))
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    return kpi


@router.post("/kpis/{kpi_id}/calculate")
def calculate_kpi(kpi_id: int, department_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Calculate current value for a KPI"""
    service = AnalyticsService(db)
    value = service.calculate_kpi_value(kpi_id, department_id)
    if value is None:
        raise HTTPException(status_code=404, detail="KPI not found or inactive")
    return {"kpi_id": kpi_id, "value": value, "calculated_at": datetime.now()}


@router.get("/kpis/{kpi_id}/trend")
def get_kpi_trend(kpi_id: int, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get KPI trend over time"""
    service = AnalyticsService(db)
    trend = service.get_kpi_trend(kpi_id, days)
    if not trend:
        raise HTTPException(status_code=404, detail="KPI not found")
    return trend


@router.get("/kpis/{kpi_id}/analytics", response_model=KPIAnalytics)
def get_kpi_analytics(kpi_id: int, db: Session = Depends(get_db)):
    """Get detailed analytics for a KPI"""
    service = AnalyticsService(db)
    analytics = service.get_kpi_analytics(kpi_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="KPI not found")
    return analytics


# KPI Values
@router.post("/kpi-values", response_model=KPIValueResponse)
def create_kpi_value(payload: KPIValueCreate, db: Session = Depends(get_db)):
    """Create a new KPI value"""
    service = AnalyticsService(db)
    try:
        # For now, we'll use the calculate_kpi_value method
        value = service.calculate_kpi_value(payload.kpi_id, payload.department_id)
        if value is None:
            raise HTTPException(status_code=404, detail="KPI not found or inactive")
        
        # Get the latest KPI value
        from app.models.analytics import AnalyticsKPIValue
        kpi_values = service.db.query(AnalyticsKPIValue).filter(
            AnalyticsKPIValue.kpi_id == payload.kpi_id
        ).order_by(desc(AnalyticsKPIValue.calculated_at)).limit(1).all()
        
        if kpi_values:
            return kpi_values[0]
        else:
            raise HTTPException(status_code=404, detail="KPI value not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kpi-values/{kpi_id}", response_model=List[KPIValueResponse])
def get_kpi_values(
    kpi_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get historical values for a KPI"""
    service = AnalyticsService(db)
    from app.models.analytics import AnalyticsKPIValue
    values = service.db.query(AnalyticsKPIValue).filter(
        AnalyticsKPIValue.kpi_id == kpi_id
    ).order_by(desc(AnalyticsKPIValue.calculated_at)).offset(offset).limit(limit).all()
    return values


# Dashboards
@router.post("/dashboards", response_model=AnalyticsDashboardResponse)
def create_dashboard(payload: AnalyticsDashboardCreate, db: Session = Depends(get_db)):
    """Create a new analytics dashboard"""
    service = AnalyticsService(db)
    try:
        dashboard = service.create_dashboard(payload.model_dump())
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboards", response_model=List[AnalyticsDashboardResponse])
def list_dashboards(
    is_public: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    department_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List analytics dashboards with filtering"""
    service = AnalyticsService(db)
    dashboards = service.list_dashboards(
        is_public=is_public,
        is_active=is_active,
        department_id=department_id,
        limit=limit,
        offset=offset
    )
    return dashboards


@router.get("/dashboards/{dashboard_id}", response_model=AnalyticsDashboardResponse)
def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    """Get analytics dashboard by ID"""
    service = AnalyticsService(db)
    dashboard = service.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=AnalyticsDashboardResponse)
def update_dashboard(dashboard_id: int, payload: AnalyticsDashboardUpdate, db: Session = Depends(get_db)):
    """Update an analytics dashboard"""
    service = AnalyticsService(db)
    dashboard = service.update_dashboard(dashboard_id, payload.model_dump(exclude_unset=True))
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.get("/dashboards/{dashboard_id}/analytics", response_model=DashboardAnalytics)
def get_dashboard_analytics(dashboard_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific dashboard"""
    service = AnalyticsService(db)
    analytics = service.get_dashboard_analytics(dashboard_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return analytics


# Widgets
@router.post("/widgets", response_model=DashboardWidgetResponse)
def create_widget(payload: DashboardWidgetCreate, db: Session = Depends(get_db)):
    """Create a new dashboard widget"""
    service = AnalyticsService(db)
    try:
        widget = service.create_widget(payload.model_dump())
        return widget
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboards/{dashboard_id}/widgets", response_model=List[DashboardWidgetResponse])
def get_dashboard_widgets(dashboard_id: int, db: Session = Depends(get_db)):
    """Get all widgets for a dashboard"""
    service = AnalyticsService(db)
    widgets = service.get_dashboard_widgets(dashboard_id)
    return widgets


@router.get("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
def get_widget(widget_id: int, db: Session = Depends(get_db)):
    """Get dashboard widget by ID"""
    service = AnalyticsService(db)
    widget = service.get_widget(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@router.put("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
def update_widget(widget_id: int, payload: DashboardWidgetUpdate, db: Session = Depends(get_db)):
    """Update a dashboard widget"""
    service = AnalyticsService(db)
    widget = service.update_widget(widget_id, payload.model_dump(exclude_unset=True))
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


# Trend Analysis
@router.post("/trend-analysis", response_model=TrendAnalysisResponse)
def create_trend_analysis(payload: TrendAnalysisCreate, db: Session = Depends(get_db)):
    """Create a new trend analysis"""
    service = AnalyticsService(db)
    try:
        analysis = service.create_trend_analysis(payload.model_dump())
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trend-analysis", response_model=List[TrendAnalysisResponse])
def list_trend_analyses(
    is_active: Optional[bool] = Query(None),
    analysis_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List trend analyses with filtering"""
    service = AnalyticsService(db)
    analyses = service.list_trend_analyses(
        is_active=is_active,
        analysis_type=analysis_type,
        limit=limit,
        offset=offset
    )
    return analyses


@router.get("/trend-analysis/{analysis_id}", response_model=TrendAnalysisResponse)
def get_trend_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get trend analysis by ID"""
    service = AnalyticsService(db)
    analysis = service.get_trend_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Trend analysis not found")
    return analysis


@router.post("/trend-analysis/{analysis_id}/calculate")
def calculate_trend_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Calculate trend analysis results"""
    service = AnalyticsService(db)
    results = service.calculate_trend_analysis(analysis_id)
    if not results:
        raise HTTPException(status_code=404, detail="Trend analysis not found")
    return results


# System Health
@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    """Get analytics system health status"""
    service = AnalyticsService(db)
    summary = service.get_analytics_summary()
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "metrics": summary.system_health,
        "uptime": "99.9%",
        "version": "1.0.0"
    }
