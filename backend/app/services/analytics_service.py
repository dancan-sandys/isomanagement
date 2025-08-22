# -*- coding: utf-8 -*-
"""
Analytics Service
Phase 4: Business logic for analytics, reporting, and business intelligence
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.analytics import (
    AnalyticsReport, KPI, AnalyticsKPIValue, AnalyticsDashboard, AnalyticsDashboardWidget, TrendAnalysis,
    ReportType, ReportStatus
)
from app.models.user import User
from app.models.dashboard import Department
from app.schemas.analytics import AnalyticsSummary, KPIAnalytics, ReportAnalytics, DashboardAnalytics


class AnalyticsService:
    """Service class for analytics and reporting management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Analytics Report Management
    def create_report(self, report_data: Dict[str, Any]) -> AnalyticsReport:
        """Create a new analytics report"""
        report = AnalyticsReport(**report_data)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def get_report(self, report_id: int) -> Optional[AnalyticsReport]:
        """Get report by ID"""
        return self.db.query(AnalyticsReport).filter(AnalyticsReport.id == report_id).first()
    
    def update_report(self, report_id: int, update_data: Dict[str, Any]) -> Optional[AnalyticsReport]:
        """Update an analytics report"""
        report = self.get_report(report_id)
        if not report:
            return None
        
        for key, value in update_data.items():
            if hasattr(report, key):
                setattr(report, key, value)
        
        # Update published_at if status changes to published
        if 'status' in update_data and update_data['status'] == ReportStatus.PUBLISHED:
            report.published_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def list_reports(
        self,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        is_public: Optional[bool] = None,
        department_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AnalyticsReport]:
        """List reports with filtering"""
        query = self.db.query(AnalyticsReport)
        
        if report_type:
            query = query.filter(AnalyticsReport.report_type == report_type)
        if status:
            query = query.filter(AnalyticsReport.status == status)
        if is_public is not None:
            query = query.filter(AnalyticsReport.is_public == is_public)
        if department_id:
            query = query.filter(AnalyticsReport.department_id == department_id)
        
        return query.order_by(desc(AnalyticsReport.created_at)).offset(offset).limit(limit).all()
    
    # KPI Management
    def create_kpi(self, kpi_data: Dict[str, Any]) -> KPI:
        """Create a new KPI"""
        kpi = KPI(**kpi_data)
        self.db.add(kpi)
        self.db.commit()
        self.db.refresh(kpi)
        return kpi
    
    def get_kpi(self, kpi_id: int) -> Optional[KPI]:
        """Get KPI by ID"""
        return self.db.query(KPI).filter(KPI.id == kpi_id).first()
    
    def update_kpi(self, kpi_id: int, update_data: Dict[str, Any]) -> Optional[KPI]:
        """Update a KPI"""
        kpi = self.get_kpi(kpi_id)
        if not kpi:
            return None
        
        for key, value in update_data.items():
            if hasattr(kpi, key):
                setattr(kpi, key, value)
        
        self.db.commit()
        self.db.refresh(kpi)
        return kpi
    
    def list_kpis(
        self,
        category: Optional[str] = None,
        module: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[KPI]:
        """List KPIs with filtering"""
        query = self.db.query(KPI)
        
        if category:
            query = query.filter(KPI.category == category)
        if module:
            query = query.filter(KPI.module == module)
        if is_active is not None:
            query = query.filter(KPI.is_active == is_active)
        
        return query.order_by(KPI.display_name).offset(offset).limit(limit).all()
    
    def calculate_kpi_value(self, kpi_id: int, department_id: Optional[int] = None) -> Optional[float]:
        """Calculate current value for a KPI"""
        kpi = self.get_kpi(kpi_id)
        if not kpi or not kpi.is_active:
            return None
        
        # This is a simplified calculation - in a real system, you would execute the calculation_query
        # For now, we'll return a mock value based on the KPI ID
        mock_value = (kpi_id * 10) % 100 + 20  # Generate a realistic-looking value
        
        # Store the calculated value
        kpi_value = AnalyticsKPIValue(
            kpi_id=kpi_id,
            value=mock_value,
            department_id=department_id,
            calculated_at=datetime.now()
        )
        self.db.add(kpi_value)
        
        # Update KPI last calculation time
        kpi.last_calculation_at = datetime.now()
        
        self.db.commit()
        return mock_value
    
    def get_kpi_trend(self, kpi_id: int, days: int = 30) -> Dict[str, Any]:
        """Get KPI trend over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        values = self.db.query(AnalyticsKPIValue).filter(
            and_(
                AnalyticsKPIValue.kpi_id == kpi_id,
                AnalyticsKPIValue.calculated_at >= start_date,
                AnalyticsKPIValue.calculated_at <= end_date
            )
        ).order_by(AnalyticsKPIValue.calculated_at).all()
        
        if len(values) < 2:
            return {"trend": "stable", "percentage_change": 0.0}
        
        first_value = values[0].value
        last_value = values[-1].value
        
        if first_value == 0:
            percentage_change = 0.0
        else:
            percentage_change = ((last_value - first_value) / first_value) * 100
        
        if percentage_change > 5:
            trend = "increasing"
        elif percentage_change < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "percentage_change": percentage_change,
            "values": [{"date": v.calculated_at, "value": v.value} for v in values]
        }
    
    # Dashboard Management
    def create_dashboard(self, dashboard_data: Dict[str, Any]) -> AnalyticsDashboard:
        """Create a new analytics dashboard"""
        dashboard = AnalyticsDashboard(**dashboard_data)
        self.db.add(dashboard)
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard
    
    def get_dashboard(self, dashboard_id: int) -> Optional[AnalyticsDashboard]:
        """Get dashboard by ID"""
        return self.db.query(AnalyticsDashboard).filter(AnalyticsDashboard.id == dashboard_id).first()
    
    def update_dashboard(self, dashboard_id: int, update_data: Dict[str, Any]) -> Optional[AnalyticsDashboard]:
        """Update an analytics dashboard"""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        for key, value in update_data.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard
    
    def list_dashboards(
        self,
        is_public: Optional[bool] = None,
        is_active: Optional[bool] = None,
        department_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AnalyticsDashboard]:
        """List dashboards with filtering"""
        query = self.db.query(AnalyticsDashboard)
        
        if is_public is not None:
            query = query.filter(AnalyticsDashboard.is_public == is_public)
        if is_active is not None:
            query = query.filter(AnalyticsDashboard.is_active == is_active)
        if department_id:
            query = query.filter(AnalyticsDashboard.department_id == department_id)
        
        return query.order_by(desc(AnalyticsDashboard.created_at)).offset(offset).limit(limit).all()
    
    # Widget Management
    def create_widget(self, widget_data: Dict[str, Any]) -> AnalyticsDashboardWidget:
        """Create a new dashboard widget"""
        widget = AnalyticsDashboardWidget(**widget_data)
        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)
        return widget
    
    def get_widget(self, widget_id: int) -> Optional[AnalyticsDashboardWidget]:
        """Get widget by ID"""
        return self.db.query(AnalyticsDashboardWidget).filter(AnalyticsDashboardWidget.id == widget_id).first()
    
    def update_widget(self, widget_id: int, update_data: Dict[str, Any]) -> Optional[AnalyticsDashboardWidget]:
        """Update a dashboard widget"""
        widget = self.get_widget(widget_id)
        if not widget:
            return None
        
        for key, value in update_data.items():
            if hasattr(widget, key):
                setattr(widget, key, value)
        
        self.db.commit()
        self.db.refresh(widget)
        return widget
    
    def get_dashboard_widgets(self, dashboard_id: int) -> List[AnalyticsDashboardWidget]:
        """Get all widgets for a dashboard"""
        return self.db.query(AnalyticsDashboardWidget).filter(
            AnalyticsDashboardWidget.dashboard_id == dashboard_id
        ).order_by(AnalyticsDashboardWidget.position_y, AnalyticsDashboardWidget.position_x).all()
    
    # Analytics Summary
    def get_analytics_summary(self) -> AnalyticsSummary:
        """Get comprehensive analytics summary"""
        total_reports = self.db.query(func.count(AnalyticsReport.id)).scalar()
        total_kpis = self.db.query(func.count(KPI.id)).scalar()
        total_dashboards = self.db.query(func.count(AnalyticsDashboard.id)).scalar()
        active_trend_analyses = self.db.query(func.count(TrendAnalysis.id)).filter(
            TrendAnalysis.is_active == True
        ).scalar()
        
        # Get recent reports
        recent_reports = self.db.query(AnalyticsReport).order_by(
            desc(AnalyticsReport.created_at)
        ).limit(5).all()
        
        # Get top KPIs (most recently calculated)
        top_kpis = self.db.query(KPI).filter(
            KPI.is_active == True
        ).order_by(desc(KPI.last_calculation_at)).limit(10).all()
        
        # System health metrics
        system_health = {
            "total_reports": total_reports,
            "total_kpis": total_kpis,
            "total_dashboards": total_dashboards,
            "active_trend_analyses": active_trend_analyses,
            "recent_activity": "normal",
            "system_status": "healthy"
        }
        
        return AnalyticsSummary(
            total_reports=total_reports,
            total_kpis=total_kpis,
            total_dashboards=total_dashboards,
            active_trend_analyses=active_trend_analyses,
            recent_reports=recent_reports,
            top_kpis=top_kpis,
            system_health=system_health
        )
    
    # KPI Analytics
    def get_kpi_analytics(self, kpi_id: int) -> Optional[KPIAnalytics]:
        """Get detailed analytics for a KPI"""
        kpi = self.get_kpi(kpi_id)
        if not kpi:
            return None
        
        # Get current value
        current_value = self.calculate_kpi_value(kpi_id)
        if current_value is None:
            current_value = 0.0
        
        # Get trend
        trend_data = self.get_kpi_trend(kpi_id)
        
        # Get historical values
        historical_values = self.db.query(AnalyticsKPIValue).filter(
            AnalyticsKPIValue.kpi_id == kpi_id
        ).order_by(desc(AnalyticsKPIValue.calculated_at)).limit(30).all()
        
        # Determine performance status
        if kpi.target_value is None:
            performance_status = "no_target"
        elif current_value >= kpi.target_value:
            performance_status = "on_target"
        else:
            performance_status = "below_target"
        
        return KPIAnalytics(
            kpi_id=kpi_id,
            kpi_name=kpi.display_name,
            current_value=current_value,
            target_value=kpi.target_value,
            trend=trend_data["trend"],
            trend_percentage=trend_data["percentage_change"],
            historical_values=historical_values,
            performance_status=performance_status,
            alerts_count=0  # Placeholder for alerts count
        )
    
    # Report Analytics
    def get_report_analytics(self, report_id: int) -> Optional[ReportAnalytics]:
        """Get analytics for a report"""
        report = self.get_report(report_id)
        if not report:
            return None
        
        # Mock data for report analytics
        return ReportAnalytics(
            report_id=report_id,
            report_title=report.title,
            report_type=report.report_type,
            execution_count=0,  # Placeholder
            last_execution=None,  # Placeholder
            average_execution_time=None,  # Placeholder
            success_rate=100.0,  # Placeholder
            user_engagement={"views": 0, "downloads": 0}  # Placeholder
        )
    
    # Dashboard Analytics
    def get_dashboard_analytics(self, dashboard_id: int) -> Optional[DashboardAnalytics]:
        """Get analytics for a dashboard"""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        # Get widgets
        widgets = self.get_dashboard_widgets(dashboard_id)
        
        # Mock data for dashboard analytics
        return DashboardAnalytics(
            dashboard_id=dashboard_id,
            dashboard_name=dashboard.name,
            view_count=0,  # Placeholder
            last_viewed=None,  # Placeholder
            average_session_duration=None,  # Placeholder
            popular_widgets=[],  # Placeholder
            user_feedback={"rating": 0, "comments": []}  # Placeholder
        )
    
    # Trend Analysis
    def create_trend_analysis(self, analysis_data: Dict[str, Any]) -> TrendAnalysis:
        """Create a new trend analysis"""
        analysis = TrendAnalysis(**analysis_data)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_trend_analysis(self, analysis_id: int) -> Optional[TrendAnalysis]:
        """Get trend analysis by ID"""
        return self.db.query(TrendAnalysis).filter(TrendAnalysis.id == analysis_id).first()
    
    def list_trend_analyses(
        self,
        is_active: Optional[bool] = None,
        analysis_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TrendAnalysis]:
        """List trend analyses with filtering"""
        query = self.db.query(TrendAnalysis)
        
        if is_active is not None:
            query = query.filter(TrendAnalysis.is_active == is_active)
        if analysis_type:
            query = query.filter(TrendAnalysis.analysis_type == analysis_type)
        
        return query.order_by(desc(TrendAnalysis.created_at)).offset(offset).limit(limit).all()
    
    def calculate_trend_analysis(self, analysis_id: int) -> Dict[str, Any]:
        """Calculate trend analysis results"""
        analysis = self.get_trend_analysis(analysis_id)
        if not analysis:
            return {}
        
        # Mock trend calculation
        # In a real system, this would perform statistical analysis
        trend_direction = "increasing"
        trend_strength = 0.75
        forecast_values = {
            "next_period": 85.5,
            "confidence_interval": [80.0, 91.0]
        }
        
        # Update analysis with results
        analysis.trend_direction = trend_direction
        analysis.trend_strength = trend_strength
        analysis.forecast_values = forecast_values
        analysis.last_updated_at = datetime.now()
        
        self.db.commit()
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "forecast_values": forecast_values,
            "analysis_id": analysis_id
        }
