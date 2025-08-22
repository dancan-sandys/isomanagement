#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Objectives Service for Phase 1 Implementation
Supports corporate and departmental objectives with advanced tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

from app.models.food_safety_objectives import (
    FoodSafetyObjective, ObjectiveTarget, ObjectiveProgress,
    ObjectiveType, HierarchyLevel, TrendDirection, PerformanceColor, DataSource
)
from app.models.departments import Department as DepartmentModel
from app.models.user import User


class ObjectivesServiceEnhanced:
    def __init__(self, db: Session):
        self.db = db

    def create_objective(self, objective_data: Dict[str, Any]) -> FoodSafetyObjective:
        """Create a new objective with enhanced validation"""
        
        # Generate objective code if not provided
        if 'objective_code' not in objective_data or not objective_data['objective_code']:
            objective_data['objective_code'] = self._generate_objective_code()
        
        # Set defaults
        objective_data.setdefault('objective_type', ObjectiveType.OPERATIONAL)
        objective_data.setdefault('hierarchy_level', HierarchyLevel.OPERATIONAL)
        objective_data.setdefault('weight', 1.0)
        objective_data.setdefault('data_source', DataSource.MANUAL)
        objective_data.setdefault('status', 'active')
        
        # Create objective
        objective = FoodSafetyObjective(**objective_data)
        self.db.add(objective)
        self.db.commit()
        self.db.refresh(objective)
        
        return objective

    def get_objective(self, objective_id: int) -> Optional[FoodSafetyObjective]:
        """Get objective by ID with related data"""
        return self.db.query(FoodSafetyObjective).filter(
            FoodSafetyObjective.id == objective_id
        ).first()

    def list_objectives(
        self,
        objective_type: Optional[ObjectiveType] = None,
        department_id: Optional[int] = None,
        hierarchy_level: Optional[HierarchyLevel] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FoodSafetyObjective]:
        """List objectives with filtering"""
        
        query = self.db.query(FoodSafetyObjective)
        
        if objective_type:
            query = query.filter(FoodSafetyObjective.objective_type == objective_type)
        
        if department_id:
            query = query.filter(FoodSafetyObjective.department_id == department_id)
        
        if hierarchy_level:
            query = query.filter(FoodSafetyObjective.hierarchy_level == hierarchy_level)
        
        if status:
            query = query.filter(FoodSafetyObjective.status == status)
        
        objectives = query.order_by(desc(FoodSafetyObjective.created_at)).offset(offset).limit(limit).all()
        
        # Ensure all objectives have a valid status
        for objective in objectives:
            if objective.status is None:
                objective.status = 'active'
        
        return objectives

    def get_corporate_objectives(self) -> List[FoodSafetyObjective]:
        """Get all corporate objectives"""
        return self.db.query(FoodSafetyObjective).filter(
            FoodSafetyObjective.objective_type == ObjectiveType.CORPORATE
        ).order_by(desc(FoodSafetyObjective.created_at)).all()

    def get_departmental_objectives(self, department_id: int) -> List[FoodSafetyObjective]:
        """Get objectives for a specific department"""
        return self.db.query(FoodSafetyObjective).filter(
            FoodSafetyObjective.department_id == department_id
        ).order_by(desc(FoodSafetyObjective.created_at)).all()

    def get_hierarchical_objectives(self) -> List[Dict[str, Any]]:
        """Get objectives in hierarchical structure"""
        objectives = self.db.query(FoodSafetyObjective).filter(
            FoodSafetyObjective.status == 'active'
        ).order_by(
            FoodSafetyObjective.objective_type,
            FoodSafetyObjective.hierarchy_level,
            FoodSafetyObjective.title
        ).all()
        
        # Build hierarchy
        hierarchy = []
        objective_map = {obj.id: obj for obj in objectives}
        
        for obj in objectives:
            if obj.parent_objective_id is None:
                hierarchy.append(self._build_objective_tree(obj, objective_map))
        
        return hierarchy

    def update_objective(self, objective_id: int, update_data: Dict[str, Any]) -> Optional[FoodSafetyObjective]:
        """Update objective with tracking"""
        
        objective = self.get_objective(objective_id)
        if not objective:
            return None
        
        # Update tracking fields
        update_data['last_updated_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            if hasattr(objective, field):
                setattr(objective, field, value)
        
        self.db.commit()
        self.db.refresh(objective)
        
        return objective

    def delete_objective(self, objective_id: int) -> bool:
        """Delete objective (soft delete by setting status to inactive)"""
        
        objective = self.get_objective(objective_id)
        if not objective:
            return False
        
        objective.status = 'inactive'
        objective.last_updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    # ------------------------------
    # Linkages
    # ------------------------------
    def get_objective_links(self, objective_id: int) -> Dict[str, Any]:
        obj = self.get_objective(objective_id)
        if not obj:
            return {}
        def parse(text_value: Optional[str]) -> list:
            try:
                return json.loads(text_value) if text_value else []
            except Exception:
                return []
        return {
            "linked_risk_ids": parse(obj.linked_risk_ids),
            "linked_control_ids": parse(obj.linked_control_ids),
            "linked_document_ids": parse(obj.linked_document_ids),
            "management_review_refs": parse(obj.management_review_refs),
        }

    def update_objective_links(self, objective_id: int, links: Dict[str, Any]) -> Optional[FoodSafetyObjective]:
        obj = self.get_objective(objective_id)
        if not obj:
            return None
        def dump(val):
            return json.dumps(val) if isinstance(val, (list, dict)) else None
        if 'linked_risk_ids' in links:
            obj.linked_risk_ids = dump(links.get('linked_risk_ids'))
        if 'linked_control_ids' in links:
            obj.linked_control_ids = dump(links.get('linked_control_ids'))
        if 'linked_document_ids' in links:
            obj.linked_document_ids = dump(links.get('linked_document_ids'))
        if 'management_review_refs' in links:
            obj.management_review_refs = dump(links.get('management_review_refs'))
        obj.last_updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def create_target(self, target_data: Dict[str, Any]) -> ObjectiveTarget:
        """Create objective target"""
        
        target = ObjectiveTarget(**target_data)
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        
        return target

    def get_targets(self, objective_id: int) -> List[ObjectiveTarget]:
        """Get targets for an objective"""
        return self.db.query(ObjectiveTarget).filter(
            ObjectiveTarget.objective_id == objective_id
        ).order_by(ObjectiveTarget.period_start).all()

    def create_progress(self, progress_data: Dict[str, Any]) -> ObjectiveProgress:
        """Create progress entry with automatic calculations"""
        
        # Calculate attainment percentage
        if 'actual_value' in progress_data and 'objective_id' in progress_data:
            objective = self.get_objective(progress_data['objective_id'])
            if objective and objective.target_value:
                # Ensure target_value is a float
                target_value = float(objective.target_value) if objective.target_value else 0
                if target_value > 0:
                    attainment = (progress_data['actual_value'] / target_value) * 100
                    progress_data['attainment_percent'] = round(attainment, 2)
                
                # Determine status
                if attainment >= 100:
                    progress_data['status'] = 'on_track'
                elif attainment >= 80:
                    progress_data['status'] = 'at_risk'
                else:
                    progress_data['status'] = 'off_track'
        
        progress = ObjectiveProgress(**progress_data)
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        
        # Update objective trend and performance color
        self._update_objective_performance(progress.objective_id)
        
        return progress

    def get_progress(self, objective_id: int, limit: int = 50) -> List[ObjectiveProgress]:
        """Get progress history for an objective"""
        return self.db.query(ObjectiveProgress).filter(
            ObjectiveProgress.objective_id == objective_id
        ).order_by(desc(ObjectiveProgress.period_start)).limit(limit).all()

    def get_trend_analysis(self, objective_id: int, periods: int = 6) -> Dict[str, Any]:
        """Get trend analysis for an objective"""
        
        # Get recent progress entries
        progress_entries = self.db.query(ObjectiveProgress).filter(
            ObjectiveProgress.objective_id == objective_id
        ).order_by(desc(ObjectiveProgress.period_start)).limit(periods).all()
        
        if not progress_entries:
            return {"trend": "no_data", "direction": None, "slope": 0}
        
        # Calculate trend
        values = [entry.actual_value for entry in reversed(progress_entries)]
        if len(values) < 2:
            return {"trend": "stable", "direction": TrendDirection.STABLE, "slope": 0}
        
        # Simple linear trend calculation
        x_values = list(range(len(values)))
        slope = self._calculate_slope(x_values, values)
        
        if slope > 0.1:
            direction = TrendDirection.IMPROVING
            trend = "improving"
        elif slope < -0.1:
            direction = TrendDirection.DECLINING
            trend = "declining"
        else:
            direction = TrendDirection.STABLE
            trend = "stable"
        
        return {
            "trend": trend,
            "direction": direction,
            "slope": slope,
            "values": values,
            "periods": len(values)
        }

    def get_dashboard_kpis(self) -> Dict[str, Any]:
        """Get KPI summary for dashboard"""
        
        # Get active objectives
        active_objectives = self.db.query(FoodSafetyObjective).filter(
            FoodSafetyObjective.status == 'active'
        ).all()
        
        # Calculate summary statistics
        total_objectives = len(active_objectives)
        corporate_objectives = len([obj for obj in active_objectives if obj.objective_type == ObjectiveType.CORPORATE])
        departmental_objectives = len([obj for obj in active_objectives if obj.objective_type == ObjectiveType.DEPARTMENTAL])
        operational_objectives = len([obj for obj in active_objectives if obj.objective_type == ObjectiveType.OPERATIONAL])
        
        # Get recent progress entries
        recent_progress = self.db.query(ObjectiveProgress).filter(
            ObjectiveProgress.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        # Calculate performance metrics
        on_track_count = len([p for p in recent_progress if p.status == 'on_track'])
        at_risk_count = len([p for p in recent_progress if p.status == 'at_risk'])
        off_track_count = len([p for p in recent_progress if p.status == 'off_track'])
        
        total_progress = len(recent_progress)
        on_track_percentage = (on_track_count / total_progress * 100) if total_progress > 0 else 0
        
        return {
            "total_objectives": total_objectives,
            "corporate_objectives": corporate_objectives,
            "departmental_objectives": departmental_objectives,
            "operational_objectives": operational_objectives,
            "recent_progress_entries": total_progress,
            "on_track_percentage": round(on_track_percentage, 1),
            "performance_breakdown": {
                "on_track": on_track_count,
                "at_risk": at_risk_count,
                "off_track": off_track_count
            }
        }

    def get_performance_metrics(self, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Get performance metrics for objectives"""
        
        query = self.db.query(ObjectiveProgress).join(FoodSafetyObjective)
        
        if department_id:
            query = query.filter(FoodSafetyObjective.department_id == department_id)
        
        # Get recent progress (last 3 months)
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        recent_progress = query.filter(
            ObjectiveProgress.period_start >= three_months_ago
        ).all()
        
        if not recent_progress:
            return {"average_attainment": 0, "trend": "no_data"}
        
        # Calculate average attainment
        total_attainment = sum(p.attainment_percent or 0 for p in recent_progress)
        average_attainment = total_attainment / len(recent_progress)
        
        # Calculate trend
        monthly_data = {}
        for progress in recent_progress:
            month_key = progress.period_start.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(progress.attainment_percent or 0)
        
        # Calculate monthly averages
        monthly_averages = []
        for month in sorted(monthly_data.keys()):
            avg = sum(monthly_data[month]) / len(monthly_data[month])
            monthly_averages.append(avg)
        
        # Determine trend
        if len(monthly_averages) >= 2:
            trend_slope = monthly_averages[-1] - monthly_averages[0]
            if trend_slope > 2:
                trend = "improving"
            elif trend_slope < -2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "average_attainment": round(average_attainment, 1),
            "trend": trend,
            "monthly_averages": monthly_averages,
            "total_entries": len(recent_progress)
        }

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts"""
        
        alerts = []
        
        # Check for objectives with no recent progress
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        objectives_without_progress = self.db.query(FoodSafetyObjective).filter(
            and_(
                FoodSafetyObjective.status == 'active',
                ~FoodSafetyObjective.id.in_(
                    self.db.query(ObjectiveProgress.objective_id).filter(
                        ObjectiveProgress.created_at >= thirty_days_ago
                    )
                )
            )
        ).all()
        
        for objective in objectives_without_progress:
            alerts.append({
                "type": "no_recent_progress",
                "objective_id": objective.id,
                "objective_title": objective.title,
                "message": f"No progress recorded for '{objective.title}' in the last 30 days",
                "severity": "medium"
            })
        
        # Check for objectives significantly off track
        off_track_progress = self.db.query(ObjectiveProgress).filter(
            and_(
                ObjectiveProgress.status == 'off_track',
                ObjectiveProgress.created_at >= thirty_days_ago
            )
        ).all()
        
        for progress in off_track_progress:
            objective = self.get_objective(progress.objective_id)
            if objective:
                alerts.append({
                    "type": "off_track",
                    "objective_id": objective.id,
                    "objective_title": objective.title,
                    "message": f"'{objective.title}' is significantly off track ({progress.attainment_percent}% attainment)",
                    "severity": "high",
                    "attainment_percent": progress.attainment_percent
                })
        
        return alerts

    # ------------------------------
    # Departments CRUD
    # ------------------------------
    def create_department(self, data: Dict[str, Any]) -> DepartmentModel:
        """Create a new department"""
        # Ensure required metadata
        if 'created_by' not in data or not data['created_by']:
            data['created_by'] = 1  # fallback system user
        # Default status
        data.setdefault('status', 'active')
        department = DepartmentModel(**data)
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department

    def get_department(self, department_id: int) -> Optional[DepartmentModel]:
        return self.db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()

    def list_departments(self, status: Optional[str] = None) -> List[DepartmentModel]:
        query = self.db.query(DepartmentModel)
        if status:
            query = query.filter(DepartmentModel.status == status)
        return query.order_by(DepartmentModel.name.asc()).all()

    def update_department(self, department_id: int, data: Dict[str, Any]) -> Optional[DepartmentModel]:
        department = self.get_department(department_id)
        if not department:
            return None
        for field, value in data.items():
            if hasattr(department, field):
                setattr(department, field, value)
        self.db.commit()
        self.db.refresh(department)
        return department

    def delete_department(self, department_id: int) -> bool:
        department = self.get_department(department_id)
        if not department:
            return False
        # Soft delete by setting status
        department.status = 'inactive'
        self.db.commit()
        return True

    def _generate_objective_code(self) -> str:
        """Generate unique objective code"""
        prefix = "OBJ"
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}"

    def _build_objective_tree(self, objective: FoodSafetyObjective, objective_map: Dict[int, FoodSafetyObjective]) -> Dict[str, Any]:
        """Build hierarchical tree structure for objectives"""
        
        tree = {
            "id": objective.id,
            "title": objective.title,
            "objective_type": objective.objective_type,
            "hierarchy_level": objective.hierarchy_level,
            "department_id": objective.department_id,
            "children": []
        }
        
        # Find child objectives
        for obj_id, obj in objective_map.items():
            if obj.parent_objective_id == objective.id:
                tree["children"].append(self._build_objective_tree(obj, objective_map))
        
        return tree

    def _calculate_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calculate slope for trend analysis"""
        n = len(x_values)
        if n < 2:
            return 0
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

    def _update_objective_performance(self, objective_id: int):
        """Update objective trend and performance color based on recent progress"""
        
        objective = self.get_objective(objective_id)
        if not objective:
            return
        
        # Get trend analysis
        trend_data = self.get_trend_analysis(objective_id)
        
        # Update trend direction
        objective.trend_direction = trend_data.get("direction")
        
        # Update performance color based on recent attainment
        recent_progress = self.db.query(ObjectiveProgress).filter(
            ObjectiveProgress.objective_id == objective_id
        ).order_by(desc(ObjectiveProgress.created_at)).first()
        
        if recent_progress and recent_progress.attainment_percent is not None:
            if recent_progress.attainment_percent >= 100:
                objective.performance_color = PerformanceColor.GREEN
            elif recent_progress.attainment_percent >= 80:
                objective.performance_color = PerformanceColor.YELLOW
            else:
                objective.performance_color = PerformanceColor.RED
        
        self.db.commit()
