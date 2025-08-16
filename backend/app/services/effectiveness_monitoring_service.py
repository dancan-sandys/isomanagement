from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.nonconformance import (
    EffectivenessMonitoring, NonConformance, PreventiveAction
)
from app.schemas.nonconformance import (
    EffectivenessMonitoringCreate, EffectivenessMonitoringUpdate, EffectivenessMonitoringFilter,
    EffectivenessMonitoringUpdateRequest
)


class EffectivenessMonitoringService:
    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations
    def create_effectiveness_monitoring(self, monitoring_data: EffectivenessMonitoringCreate, created_by: int) -> EffectivenessMonitoring:
        """Create a new effectiveness monitoring record"""
        # Calculate achievement percentage if actual value is provided
        if monitoring_data.actual_value is not None:
            achievement_percentage = self._calculate_achievement_percentage(
                monitoring_data.actual_value, monitoring_data.target_value
            )
            monitoring_data_dict = monitoring_data.dict()
            monitoring_data_dict['achievement_percentage'] = achievement_percentage
        else:
            monitoring_data_dict = monitoring_data.dict()

        effectiveness_monitoring = EffectivenessMonitoring(
            **monitoring_data_dict,
            created_by=created_by
        )
        
        self.db.add(effectiveness_monitoring)
        self.db.commit()
        self.db.refresh(effectiveness_monitoring)
        return effectiveness_monitoring

    def get_effectiveness_monitoring(self, filter_params: EffectivenessMonitoringFilter) -> Dict[str, Any]:
        """Get effectiveness monitoring records with filtering and pagination"""
        query = self.db.query(EffectivenessMonitoring)

        # Apply filters
        if filter_params.non_conformance_id:
            query = query.filter(EffectivenessMonitoring.non_conformance_id == filter_params.non_conformance_id)

        if filter_params.metric_name:
            query = query.filter(EffectivenessMonitoring.metric_name.ilike(f"%{filter_params.metric_name}%"))

        if filter_params.status:
            query = query.filter(EffectivenessMonitoring.status == filter_params.status)

        if filter_params.measurement_frequency:
            query = query.filter(EffectivenessMonitoring.measurement_frequency == filter_params.measurement_frequency)

        if filter_params.period_start_from:
            query = query.filter(EffectivenessMonitoring.monitoring_period_start >= filter_params.period_start_from)

        if filter_params.period_start_to:
            query = query.filter(EffectivenessMonitoring.monitoring_period_start <= filter_params.period_start_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        monitoring_records = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": monitoring_records,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_effectiveness_monitoring_record(self, monitoring_id: int) -> Optional[EffectivenessMonitoring]:
        """Get effectiveness monitoring record by ID"""
        return self.db.query(EffectivenessMonitoring).filter(EffectivenessMonitoring.id == monitoring_id).first()

    def get_monitoring_by_nc(self, nc_id: int) -> List[EffectivenessMonitoring]:
        """Get all effectiveness monitoring records for a specific non-conformance"""
        return self.db.query(EffectivenessMonitoring).filter(
            EffectivenessMonitoring.non_conformance_id == nc_id
        ).order_by(EffectivenessMonitoring.monitoring_period_start.desc()).all()

    def update_effectiveness_monitoring(self, monitoring_id: int, monitoring_data: EffectivenessMonitoringUpdate, updated_by: int) -> Optional[EffectivenessMonitoring]:
        """Update effectiveness monitoring record"""
        monitoring_record = self.get_effectiveness_monitoring_record(monitoring_id)
        if not monitoring_record:
            return None

        update_data = monitoring_data.dict(exclude_unset=True)
        update_data['updated_by'] = updated_by
        update_data['updated_at'] = datetime.now()

        # Recalculate achievement percentage if actual value is updated
        if 'actual_value' in update_data and update_data['actual_value'] is not None:
            achievement_percentage = self._calculate_achievement_percentage(
                update_data['actual_value'], 
                update_data.get('target_value', monitoring_record.target_value)
            )
            update_data['achievement_percentage'] = achievement_percentage

        for field, value in update_data.items():
            setattr(monitoring_record, field, value)

        self.db.commit()
        self.db.refresh(monitoring_record)
        return monitoring_record

    def delete_effectiveness_monitoring(self, monitoring_id: int) -> bool:
        """Delete effectiveness monitoring record"""
        monitoring_record = self.get_effectiveness_monitoring_record(monitoring_id)
        if not monitoring_record:
            return False

        self.db.delete(monitoring_record)
        self.db.commit()
        return True

    # Business Logic Methods
    def update_monitoring_value(self, update_request: EffectivenessMonitoringUpdateRequest) -> Optional[EffectivenessMonitoring]:
        """Update the actual value for a monitoring record"""
        monitoring_record = self.get_effectiveness_monitoring_record(update_request.monitoring_id)
        if not monitoring_record:
            return None

        # Calculate achievement percentage
        achievement_percentage = self._calculate_achievement_percentage(
            update_request.actual_value, monitoring_record.target_value
        )

        monitoring_record.actual_value = update_request.actual_value
        monitoring_record.achievement_percentage = achievement_percentage
        monitoring_record.updated_at = datetime.now()

        # Update trend analysis
        trend_data = self._update_trend_analysis(monitoring_record, update_request.actual_value)
        monitoring_record.trend_analysis = json.dumps(trend_data)

        self.db.commit()
        self.db.refresh(monitoring_record)
        return monitoring_record

    def get_active_monitoring(self, nc_id: Optional[int] = None) -> List[EffectivenessMonitoring]:
        """Get all active monitoring records"""
        query = self.db.query(EffectivenessMonitoring).filter(
            EffectivenessMonitoring.status == 'active'
        )
        
        if nc_id:
            query = query.filter(EffectivenessMonitoring.non_conformance_id == nc_id)
        
        return query.order_by(EffectivenessMonitoring.monitoring_period_start.asc()).all()

    def get_completed_monitoring(self, nc_id: Optional[int] = None) -> List[EffectivenessMonitoring]:
        """Get all completed monitoring records"""
        query = self.db.query(EffectivenessMonitoring).filter(
            EffectivenessMonitoring.status == 'completed'
        )
        
        if nc_id:
            query = query.filter(EffectivenessMonitoring.non_conformance_id == nc_id)
        
        return query.order_by(EffectivenessMonitoring.monitoring_period_end.desc()).all()

    def get_monitoring_by_metric(self, metric_name: str, nc_id: Optional[int] = None) -> List[EffectivenessMonitoring]:
        """Get monitoring records by metric name"""
        query = self.db.query(EffectivenessMonitoring).filter(
            EffectivenessMonitoring.metric_name.ilike(f"%{metric_name}%")
        )
        
        if nc_id:
            query = query.filter(EffectivenessMonitoring.non_conformance_id == nc_id)
        
        return query.order_by(EffectivenessMonitoring.monitoring_period_start.desc()).all()

    def get_monitoring_by_frequency(self, frequency: str, nc_id: Optional[int] = None) -> List[EffectivenessMonitoring]:
        """Get monitoring records by measurement frequency"""
        query = self.db.query(EffectivenessMonitoring).filter(
            EffectivenessMonitoring.measurement_frequency == frequency
        )
        
        if nc_id:
            query = query.filter(EffectivenessMonitoring.non_conformance_id == nc_id)
        
        return query.order_by(EffectivenessMonitoring.monitoring_period_start.desc()).all()

    def get_monitoring_statistics(self, nc_id: Optional[int] = None) -> Dict[str, Any]:
        """Get effectiveness monitoring statistics"""
        query = self.db.query(EffectivenessMonitoring)
        
        if nc_id:
            query = query.filter(EffectivenessMonitoring.non_conformance_id == nc_id)
        
        total_monitoring = query.count()
        
        # Status distribution
        statuses = ['active', 'completed', 'suspended']
        monitoring_by_status = {}
        for status in statuses:
            count = query.filter(EffectivenessMonitoring.status == status).count()
            monitoring_by_status[status] = count
        
        # Frequency distribution
        frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        monitoring_by_frequency = {}
        for frequency in frequencies:
            count = query.filter(EffectivenessMonitoring.measurement_frequency == frequency).count()
            monitoring_by_frequency[frequency] = count
        
        # Achievement statistics
        completed_monitoring = query.filter(
            and_(
                EffectivenessMonitoring.status == 'completed',
                EffectivenessMonitoring.achievement_percentage.isnot(None)
            )
        ).all()
        
        if completed_monitoring:
            avg_achievement = sum(m.achievement_percentage for m in completed_monitoring) / len(completed_monitoring)
            on_target_count = sum(1 for m in completed_monitoring if m.achievement_percentage >= 100)
            on_target_rate = (on_target_count / len(completed_monitoring)) * 100
        else:
            avg_achievement = 0
            on_target_rate = 0
        
        return {
            "total_monitoring": total_monitoring,
            "monitoring_by_status": monitoring_by_status,
            "monitoring_by_frequency": monitoring_by_frequency,
            "average_achievement": round(avg_achievement, 2),
            "on_target_rate": round(on_target_rate, 2),
            "completed_monitoring_count": len(completed_monitoring)
        }

    def get_monitoring_trends(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get monitoring trends over time"""
        start_date = datetime.now() - timedelta(days=days)
        
        monitoring_records = self.db.query(EffectivenessMonitoring).filter(
            and_(
                EffectivenessMonitoring.achievement_percentage.isnot(None),
                EffectivenessMonitoring.created_at >= start_date
            )
        ).order_by(EffectivenessMonitoring.created_at.asc()).all()
        
        trends = []
        for record in monitoring_records:
            trends.append({
                "date": record.created_at.date(),
                "metric_name": record.metric_name,
                "target_value": record.target_value,
                "actual_value": record.actual_value,
                "achievement_percentage": record.achievement_percentage,
                "status": record.status,
                "nc_id": record.non_conformance_id
            })
        
        return trends

    def get_metric_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary by metric"""
        metrics = self.db.query(EffectivenessMonitoring.metric_name).distinct().all()
        metric_names = [m[0] for m in metrics]
        
        performance_by_metric = {}
        for metric_name in metric_names:
            records = self.db.query(EffectivenessMonitoring).filter(
                and_(
                    EffectivenessMonitoring.metric_name == metric_name,
                    EffectivenessMonitoring.achievement_percentage.isnot(None)
                )
            ).all()
            
            if records:
                avg_achievement = sum(r.achievement_percentage for r in records) / len(records)
                on_target_count = sum(1 for r in records if r.achievement_percentage >= 100)
                on_target_rate = (on_target_count / len(records)) * 100
                
                performance_by_metric[metric_name] = {
                    "total_records": len(records),
                    "average_achievement": round(avg_achievement, 2),
                    "on_target_rate": round(on_target_rate, 2),
                    "on_target_count": on_target_count
                }
            else:
                performance_by_metric[metric_name] = {
                    "total_records": 0,
                    "average_achievement": 0,
                    "on_target_rate": 0,
                    "on_target_count": 0
                }
        
        return performance_by_metric

    def get_overdue_measurements(self, days_threshold: int = 7) -> List[EffectivenessMonitoring]:
        """Get monitoring records that are overdue for measurement"""
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        return self.db.query(EffectivenessMonitoring).filter(
            and_(
                EffectivenessMonitoring.status == 'active',
                EffectivenessMonitoring.monitoring_period_start <= threshold_date,
                EffectivenessMonitoring.actual_value.is_(None)
            )
        ).order_by(EffectivenessMonitoring.monitoring_period_start.asc()).all()

    def get_upcoming_measurements(self, days: int = 7) -> List[EffectivenessMonitoring]:
        """Get monitoring records with upcoming measurement dates"""
        end_date = datetime.now() + timedelta(days=days)
        
        return self.db.query(EffectivenessMonitoring).filter(
            and_(
                EffectivenessMonitoring.status == 'active',
                EffectivenessMonitoring.monitoring_period_start <= end_date,
                EffectivenessMonitoring.monitoring_period_start >= datetime.now()
            )
        ).order_by(EffectivenessMonitoring.monitoring_period_start.asc()).all()

    def bulk_update_monitoring(self, monitoring_ids: List[int], update_data: Dict[str, Any], updated_by: int) -> Dict[str, Any]:
        """Bulk update monitoring records"""
        monitoring_records = self.db.query(EffectivenessMonitoring).filter(
            EffectivenessMonitoring.id.in_(monitoring_ids)
        ).all()
        
        updated_count = 0
        for record in monitoring_records:
            for field, value in update_data.items():
                if hasattr(record, field):
                    setattr(record, field, value)
            record.updated_by = updated_by
            record.updated_at = datetime.now()
            
            # Recalculate achievement percentage if actual value is updated
            if 'actual_value' in update_data and update_data['actual_value'] is not None:
                achievement_percentage = self._calculate_achievement_percentage(
                    update_data['actual_value'], record.target_value
                )
                record.achievement_percentage = achievement_percentage
            
            updated_count += 1
        
        self.db.commit()
        
        return {
            "total_requested": len(monitoring_ids),
            "updated_count": updated_count
        }

    # Helper Methods
    def _calculate_achievement_percentage(self, actual_value: float, target_value: float) -> float:
        """Calculate achievement percentage"""
        if target_value == 0:
            return 0.0
        return round((actual_value / target_value) * 100, 2)

    def _update_trend_analysis(self, monitoring_record: EffectivenessMonitoring, new_value: float) -> Dict[str, Any]:
        """Update trend analysis data"""
        # Get historical data for this metric
        historical_data = self.db.query(EffectivenessMonitoring).filter(
            and_(
                EffectivenessMonitoring.metric_name == monitoring_record.metric_name,
                EffectivenessMonitoring.non_conformance_id == monitoring_record.non_conformance_id,
                EffectivenessMonitoring.actual_value.isnot(None)
            )
        ).order_by(EffectivenessMonitoring.created_at.asc()).all()
        
        # Calculate trend
        values = [record.actual_value for record in historical_data] + [new_value]
        
        if len(values) >= 2:
            # Simple linear trend calculation
            trend_direction = "increasing" if values[-1] > values[-2] else "decreasing" if values[-1] < values[-2] else "stable"
            trend_magnitude = abs(values[-1] - values[-2])
        else:
            trend_direction = "stable"
            trend_magnitude = 0
        
        return {
            "historical_values": values,
            "trend_direction": trend_direction,
            "trend_magnitude": trend_magnitude,
            "last_updated": datetime.now().isoformat()
        }

    def validate_monitoring_data(self, monitoring_data: EffectivenessMonitoringCreate) -> Dict[str, Any]:
        """Validate monitoring data and provide recommendations"""
        recommendations = []
        warnings = []
        
        # Check monitoring period
        if monitoring_data.monitoring_period_end <= monitoring_data.monitoring_period_start:
            warnings.append("Monitoring period end must be after start date")
        
        # Check target value
        if monitoring_data.target_value <= 0:
            warnings.append("Target value must be positive")
        
        # Check measurement frequency vs period
        period_days = (monitoring_data.monitoring_period_end - monitoring_data.monitoring_period_start).days
        
        if monitoring_data.measurement_frequency == 'daily' and period_days < 7:
            recommendations.append("Consider longer monitoring period for daily measurements")
        elif monitoring_data.measurement_frequency == 'weekly' and period_days < 28:
            recommendations.append("Consider longer monitoring period for weekly measurements")
        elif monitoring_data.measurement_frequency == 'monthly' and period_days < 90:
            recommendations.append("Consider longer monitoring period for monthly measurements")
        
        return {
            "is_valid": len(warnings) == 0,
            "recommendations": recommendations,
            "warnings": warnings
        }

    def get_monitoring_timeline(self, nc_id: int) -> List[Dict[str, Any]]:
        """Get timeline of monitoring activities for a non-conformance"""
        monitoring_records = self.get_monitoring_by_nc(nc_id)
        
        timeline = []
        for record in monitoring_records:
            timeline.append({
                "id": record.id,
                "metric_name": record.metric_name,
                "target_value": record.target_value,
                "actual_value": record.actual_value,
                "achievement_percentage": record.achievement_percentage,
                "status": record.status,
                "monitoring_period_start": record.monitoring_period_start,
                "monitoring_period_end": record.monitoring_period_end,
                "measurement_frequency": record.measurement_frequency
            })
        
        return sorted(timeline, key=lambda x: x["monitoring_period_start"], reverse=True)
