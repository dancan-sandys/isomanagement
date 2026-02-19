from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.equipment import Equipment, MaintenancePlan, MaintenanceType, MaintenanceWorkOrder, CalibrationPlan, CalibrationRecord, WorkOrderStatus, WorkOrderPriority


class EquipmentService:
    def __init__(self, db: Session):
        self.db = db

    # Equipment
    def create_equipment(self, *, name: str, equipment_type: str, serial_number: Optional[str], location: Optional[str], notes: Optional[str], created_by: Optional[int], is_active: Optional[bool] = True, critical_to_food_safety: Optional[bool] = False) -> Equipment:
        eq = Equipment(name=name, equipment_type=equipment_type, serial_number=serial_number, location=location, notes=notes, created_by=created_by, is_active=is_active if is_active is not None else True, critical_to_food_safety=critical_to_food_safety if critical_to_food_safety is not None else False)
        self.db.add(eq)
        self.db.commit()
        self.db.refresh(eq)
        return eq

    def list_equipment(self) -> List[Equipment]:
        return self.db.query(Equipment).order_by(Equipment.created_at.desc()).all()

    def get_equipment(self, equipment_id: int) -> Optional[Equipment]:
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).first()

    def update_equipment(self, equipment_id: int, **kwargs) -> Optional[Equipment]:
        eq = self.get_equipment(equipment_id)
        if not eq:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(eq, key):
                setattr(eq, key, value)
        eq.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(eq)
        return eq

    def delete_equipment(self, equipment_id: int) -> bool:
        eq = self.get_equipment(equipment_id)
        if not eq:
            return False
        self.db.delete(eq)
        self.db.commit()
        return True

    # Maintenance
    def _normalize_maintenance_type(self, maintenance_type: Optional[str]) -> Optional[MaintenanceType]:
        if maintenance_type is None:
            return None
        mt = maintenance_type.strip().lower()
        if mt in ("preventive", "corrective"):
            # cast back to Enum (defined with lowercase values)
            if mt == "preventive":
                return MaintenanceType.PREVENTIVE
            return MaintenanceType.CORRECTIVE
        raise ValueError(f"Invalid maintenance_type: {maintenance_type}")

    def create_maintenance_plan(self, *, equipment_id: int, frequency_days: int, maintenance_type: str, notes: Optional[str]) -> MaintenancePlan:
        mt = self._normalize_maintenance_type(maintenance_type)
        plan = MaintenancePlan(equipment_id=equipment_id, frequency_days=frequency_days, maintenance_type=mt, notes=notes)
        # Set initial next_due_at
        plan.next_due_at = datetime.utcnow() + timedelta(days=frequency_days)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def list_maintenance_plans(self, equipment_id: Optional[int] = None) -> List[MaintenancePlan]:
        q = self.db.query(MaintenancePlan)
        if equipment_id is not None:
            q = q.filter(MaintenancePlan.equipment_id == equipment_id)
        return q.order_by(MaintenancePlan.id.desc()).all()

    def update_maintenance_plan(self, plan_id: int, *, frequency_days: Optional[int] = None, maintenance_type: Optional[str] = None, notes: Optional[str] = None, active: Optional[bool] = None) -> Optional[MaintenancePlan]:
        plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
        if not plan:
            return None
        if frequency_days is not None:
            plan.frequency_days = frequency_days
            # Recompute next_due_at if last_performed_at exists else from now
            base = plan.last_performed_at or datetime.utcnow()
            plan.next_due_at = base + timedelta(days=frequency_days)
        if maintenance_type is not None:
            plan.maintenance_type = self._normalize_maintenance_type(maintenance_type)
        if notes is not None:
            plan.notes = notes
        if active is not None:
            plan.active = active
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete_maintenance_plan(self, plan_id: int) -> bool:
        plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
        if not plan:
            return False
        self.db.delete(plan)
        self.db.commit()
        return True

    def create_work_order(self, *, equipment_id: int, plan_id: Optional[int], title: str, description: Optional[str], priority: Optional[str] = None, assigned_to: Optional[int] = None, due_date: Optional[datetime] = None, created_by: Optional[int] = None) -> MaintenanceWorkOrder:
        # Normalize priority
        pr = WorkOrderPriority(priority.upper()) if priority else WorkOrderPriority.MEDIUM
        wo = MaintenanceWorkOrder(
            equipment_id=equipment_id,
            plan_id=plan_id,
            title=title,
            description=description,
            status=WorkOrderStatus.PENDING,
            priority=pr,
            assigned_to=assigned_to,
            due_date=due_date,
            created_by=created_by,
        )
        self.db.add(wo)
        self.db.commit()
        self.db.refresh(wo)
        return wo

    def get_work_order(self, work_order_id: int) -> Optional[MaintenanceWorkOrder]:
        return self.db.query(MaintenanceWorkOrder).filter(MaintenanceWorkOrder.id == work_order_id).first()

    def update_work_order(self, work_order_id: int, *, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None, priority: Optional[str] = None, assigned_to: Optional[int] = None, due_date: Optional[datetime] = None) -> Optional[MaintenanceWorkOrder]:
        wo = self.get_work_order(work_order_id)
        if not wo:
            return None
        if title is not None:
            wo.title = title
        if description is not None:
            wo.description = description
        if status is not None:
            wo.status = WorkOrderStatus(status.upper())
        if priority is not None:
            wo.priority = WorkOrderPriority(priority.upper())
        if assigned_to is not None:
            wo.assigned_to = assigned_to
        if due_date is not None:
            wo.due_date = due_date
        self.db.commit()
        self.db.refresh(wo)
        return wo

    def delete_work_order(self, work_order_id: int) -> bool:
        wo = self.get_work_order(work_order_id)
        if not wo:
            return False
        self.db.delete(wo)
        self.db.commit()
        return True

    def complete_work_order(self, work_order_id: int, completed_by: int) -> Optional[MaintenanceWorkOrder]:
        wo = self.db.query(MaintenanceWorkOrder).filter(MaintenanceWorkOrder.id == work_order_id).first()
        if not wo:
            return None
        wo.completed_by = completed_by
        wo.completed_at = datetime.utcnow()
        wo.status = WorkOrderStatus.COMPLETED
        # Update plan last_performed and next_due if applicable
        if wo.plan_id:
            plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == wo.plan_id).first()
            if plan:
                plan.last_performed_at = wo.completed_at
                plan.next_due_at = plan.last_performed_at + timedelta(days=plan.frequency_days)
        self.db.commit()
        self.db.refresh(wo)
        return wo

    def list_work_orders(self, equipment_id: Optional[int] = None, plan_id: Optional[int] = None, status: Optional[str] = None) -> List[MaintenanceWorkOrder]:
        q = self.db.query(MaintenanceWorkOrder)
        if equipment_id is not None:
            q = q.filter(MaintenanceWorkOrder.equipment_id == equipment_id)
        if plan_id is not None:
            q = q.filter(MaintenanceWorkOrder.plan_id == plan_id)
        if status is not None:
            q = q.filter(MaintenanceWorkOrder.status == WorkOrderStatus(status.upper()))
        return q.order_by(MaintenanceWorkOrder.created_at.desc()).all()

    # Calibration
    def create_calibration_plan(self, *, equipment_id: int, schedule_date: datetime, frequency_days: int, notes: Optional[str]) -> CalibrationPlan:
        plan = CalibrationPlan(equipment_id=equipment_id, schedule_date=schedule_date, frequency_days=frequency_days, next_due_at=schedule_date, notes=notes)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def list_calibration_plans(self, equipment_id: Optional[int] = None) -> List[CalibrationPlan]:
        q = self.db.query(CalibrationPlan)
        if equipment_id is not None:
            q = q.filter(CalibrationPlan.equipment_id == equipment_id)
        return q.order_by(CalibrationPlan.next_due_at.asc().nulls_last()).all()

    def update_calibration_plan(self, plan_id: int, *, schedule_date: Optional[datetime] = None, frequency_days: Optional[int] = None, notes: Optional[str] = None, active: Optional[bool] = None) -> Optional[CalibrationPlan]:
        plan = self.db.query(CalibrationPlan).filter(CalibrationPlan.id == plan_id).first()
        if not plan:
            return None
        if schedule_date is not None:
            plan.schedule_date = schedule_date
            if plan.last_calibrated_at is None:
                plan.next_due_at = schedule_date
        if frequency_days is not None:
            plan.frequency_days = frequency_days
            # If we have a last calibration date, compute next due accordingly
            base = plan.last_calibrated_at or plan.schedule_date or datetime.utcnow()
            plan.next_due_at = base + timedelta(days=plan.frequency_days)
        if notes is not None:
            plan.notes = notes
        if active is not None:
            plan.active = active
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete_calibration_plan(self, plan_id: int) -> bool:
        plan = self.db.query(CalibrationPlan).filter(CalibrationPlan.id == plan_id).first()
        if not plan:
            return False
        self.db.delete(plan)
        self.db.commit()
        return True

    def record_calibration(self, *, plan_id: int, original_filename: str, stored_filename: str, file_path: str, file_type: Optional[str], uploaded_by: int) -> CalibrationRecord:
        rec = CalibrationRecord(plan_id=plan_id, original_filename=original_filename, stored_filename=stored_filename, file_path=file_path, file_type=file_type, uploaded_by=uploaded_by)
        # Update plan last/next
        plan = self.db.query(CalibrationPlan).filter(CalibrationPlan.id == plan_id).first()
        if plan:
            performed = rec.performed_at if hasattr(rec, 'performed_at') and rec.performed_at else datetime.utcnow()
            plan.last_calibrated_at = performed
            if getattr(plan, 'frequency_days', None):
                plan.next_due_at = performed + timedelta(days=plan.frequency_days)
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    # History helpers
    def get_maintenance_history(self, equipment_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        q = self.db.query(MaintenanceWorkOrder)
        if equipment_id is not None:
            q = q.filter(MaintenanceWorkOrder.equipment_id == equipment_id)
        if start_date is not None:
            q = q.filter(MaintenanceWorkOrder.created_at >= start_date)
        if end_date is not None:
            q = q.filter(MaintenanceWorkOrder.created_at <= end_date)
        orders = q.order_by(MaintenanceWorkOrder.created_at.desc()).all()
        results: List[dict] = []
        for wo in orders:
            eq = self.db.query(Equipment).filter(Equipment.id == wo.equipment_id).first()
            results.append({
                "id": wo.id,
                "equipment_id": wo.equipment_id,
                "equipment_name": eq.name if eq else "Unknown",
                "title": wo.title,
                "plan_id": wo.plan_id,
                "created_at": wo.created_at.isoformat() if wo.created_at else None,
                "completed_at": wo.completed_at.isoformat() if wo.completed_at else None,
            })
        return results

    def get_calibration_history(self, equipment_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        # Join records -> plans to get equipment
        from sqlalchemy import join
        j = self.db.query(CalibrationRecord, CalibrationPlan).join(CalibrationPlan, CalibrationRecord.plan_id == CalibrationPlan.id)
        if equipment_id is not None:
            j = j.filter(CalibrationPlan.equipment_id == equipment_id)
        if start_date is not None:
            j = j.filter(CalibrationRecord.performed_at >= start_date)
        if end_date is not None:
            j = j.filter(CalibrationRecord.performed_at <= end_date)
        rows = j.order_by(CalibrationRecord.performed_at.desc()).all()
        results: List[dict] = []
        for rec, plan in rows:
            eq = self.db.query(Equipment).filter(Equipment.id == plan.equipment_id).first()
            results.append({
                "id": rec.id,
                "equipment_id": plan.equipment_id,
                "equipment_name": eq.name if eq else "Unknown",
                "performed_at": rec.performed_at.isoformat() if rec.performed_at else None,
                "original_filename": rec.original_filename,
                "stored_filename": rec.stored_filename,
                "file_type": rec.file_type,
            })
        return results

    # Analytics and Statistics
    def get_equipment_stats(self) -> dict:
        """Get equipment statistics and analytics"""
        total_equipment = self.db.query(Equipment).count()
        active_equipment = total_equipment  # All equipment is considered active since there's no is_active field
        maintenance_plans = self.db.query(MaintenancePlan).count()
        calibration_plans = self.db.query(CalibrationPlan).count()
        pending_work_orders = self.db.query(MaintenanceWorkOrder).filter(MaintenanceWorkOrder.completed_at == None).count()
        
        return {
            "total_equipment": total_equipment,
            "active_equipment": active_equipment,
            "maintenance_plans": maintenance_plans,
            "calibration_plans": calibration_plans,
            "pending_work_orders": pending_work_orders,
            "equipment_by_type": self._get_equipment_by_type(),
            "maintenance_status": self._get_maintenance_status()
        }

    def get_upcoming_maintenance(self) -> List[dict]:
        """Get upcoming maintenance schedules"""
        upcoming_date = datetime.utcnow() + timedelta(days=30)
        plans = self.db.query(MaintenancePlan).filter(
            MaintenancePlan.next_due_at <= upcoming_date,
            MaintenancePlan.next_due_at >= datetime.utcnow()
        ).order_by(MaintenancePlan.next_due_at.asc()).all()
        
        return [
            {
                "id": plan.id,
                "equipment_id": plan.equipment_id,
                "equipment_name": plan.equipment.name if plan.equipment else "Unknown",
                "maintenance_type": plan.maintenance_type.value if plan.maintenance_type else None,
                "next_due_at": plan.next_due_at.isoformat() if plan.next_due_at else None,
                "frequency_days": plan.frequency_days,
                "notes": plan.notes
            }
            for plan in plans
        ]

    def get_overdue_calibrations(self) -> List[dict]:
        """Get overdue calibration schedules"""
        overdue_plans = self.db.query(CalibrationPlan).filter(
            CalibrationPlan.next_due_at < datetime.utcnow()
        ).order_by(CalibrationPlan.next_due_at.asc()).all()
        
        return [
            {
                "id": plan.id,
                "equipment_id": plan.equipment_id,
                "equipment_name": plan.equipment.name if plan.equipment else "Unknown",
                "next_due_at": plan.next_due_at.isoformat() if plan.next_due_at else None,
                "days_overdue": (datetime.utcnow() - plan.next_due_at).days if plan.next_due_at else 0,
                "notes": plan.notes
            }
            for plan in overdue_plans
        ]

    def get_equipment_alerts(self) -> List[dict]:
        """Get equipment alerts and notifications"""
        alerts = []
        
        # Overdue calibrations
        overdue_calibrations = self.get_overdue_calibrations()
        for cal in overdue_calibrations:
            alerts.append({
                "type": "overdue_calibration",
                "severity": "high",
                "title": f"Overdue Calibration: {cal['equipment_name']}",
                "message": f"Calibration is {cal['days_overdue']} days overdue",
                "equipment_id": cal["equipment_id"],
                "due_date": cal["next_due_at"]
            })
        
        # Upcoming maintenance
        upcoming_maintenance = self.get_upcoming_maintenance()
        for maint in upcoming_maintenance:
            if maint["next_due_at"]:
                try:
                    next_due = datetime.fromisoformat(maint["next_due_at"].replace('Z', '+00:00'))
                    days_until_due = (next_due - datetime.utcnow()).days
                except:
                    days_until_due = 0
            else:
                days_until_due = 0
            if days_until_due <= 7:
                alerts.append({
                    "type": "upcoming_maintenance",
                    "severity": "medium" if days_until_due <= 3 else "low",
                    "title": f"Upcoming Maintenance: {maint['equipment_name']}",
                    "message": f"Maintenance due in {days_until_due} days",
                    "equipment_id": maint["equipment_id"],
                    "due_date": maint["next_due_at"]
                })
        
        return alerts

    def _get_equipment_by_type(self) -> dict:
        """Get equipment count by type"""
        from sqlalchemy import func
        result = self.db.query(
            Equipment.equipment_type,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.equipment_type).all()
        
        return {row.equipment_type: row.count for row in result}

    def _get_maintenance_status(self) -> dict:
        """Get maintenance status summary"""
        total_plans = self.db.query(MaintenancePlan).count()
        overdue_plans = self.db.query(MaintenancePlan).filter(
            MaintenancePlan.next_due_at < datetime.utcnow()
        ).count()
        upcoming_plans = self.db.query(MaintenancePlan).filter(
            MaintenancePlan.next_due_at >= datetime.utcnow(),
            MaintenancePlan.next_due_at <= datetime.utcnow() + timedelta(days=30)
        ).count()
        
        return {
            "total_plans": total_plans,
            "overdue": overdue_plans,
            "upcoming": upcoming_plans,
            "on_schedule": total_plans - overdue_plans - upcoming_plans
        }


