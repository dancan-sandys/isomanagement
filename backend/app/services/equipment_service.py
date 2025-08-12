from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.equipment import Equipment, MaintenancePlan, MaintenanceType, MaintenanceWorkOrder, CalibrationPlan, CalibrationRecord


class EquipmentService:
    def __init__(self, db: Session):
        self.db = db

    # Equipment
    def create_equipment(self, *, name: str, equipment_type: str, serial_number: Optional[str], location: Optional[str], notes: Optional[str], created_by: Optional[int]) -> Equipment:
        eq = Equipment(name=name, equipment_type=equipment_type, serial_number=serial_number, location=location, notes=notes, created_by=created_by)
        self.db.add(eq)
        self.db.commit()
        self.db.refresh(eq)
        return eq

    def list_equipment(self) -> List[Equipment]:
        return self.db.query(Equipment).order_by(Equipment.created_at.desc()).all()

    # Maintenance
    def create_maintenance_plan(self, *, equipment_id: int, frequency_days: int, maintenance_type: str, notes: Optional[str]) -> MaintenancePlan:
        mt = MaintenanceType(maintenance_type)
        plan = MaintenancePlan(equipment_id=equipment_id, frequency_days=frequency_days, maintenance_type=mt, notes=notes)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def list_maintenance_plans(self, equipment_id: Optional[int] = None) -> List[MaintenancePlan]:
        q = self.db.query(MaintenancePlan)
        if equipment_id is not None:
            q = q.filter(MaintenancePlan.equipment_id == equipment_id)
        return q.order_by(MaintenancePlan.id.desc()).all()

    def create_work_order(self, *, equipment_id: int, plan_id: Optional[int], title: str, description: Optional[str]) -> MaintenanceWorkOrder:
        wo = MaintenanceWorkOrder(equipment_id=equipment_id, plan_id=plan_id, title=title, description=description)
        self.db.add(wo)
        self.db.commit()
        self.db.refresh(wo)
        return wo

    def complete_work_order(self, work_order_id: int, completed_by: int) -> Optional[MaintenanceWorkOrder]:
        wo = self.db.query(MaintenanceWorkOrder).filter(MaintenanceWorkOrder.id == work_order_id).first()
        if not wo:
            return None
        wo.completed_by = completed_by
        wo.completed_at = datetime.utcnow()
        # Update plan last_performed and next_due if applicable
        if wo.plan_id:
            plan = self.db.query(MaintenancePlan).filter(MaintenancePlan.id == wo.plan_id).first()
            if plan:
                plan.last_performed_at = wo.completed_at
                plan.next_due_at = plan.last_performed_at + timedelta(days=plan.frequency_days)
        self.db.commit()
        self.db.refresh(wo)
        return wo

    def list_work_orders(self, equipment_id: Optional[int] = None, plan_id: Optional[int] = None) -> List[MaintenanceWorkOrder]:
        q = self.db.query(MaintenanceWorkOrder)
        if equipment_id is not None:
            q = q.filter(MaintenanceWorkOrder.equipment_id == equipment_id)
        if plan_id is not None:
            q = q.filter(MaintenanceWorkOrder.plan_id == plan_id)
        return q.order_by(MaintenanceWorkOrder.created_at.desc()).all()

    # Calibration
    def create_calibration_plan(self, *, equipment_id: int, schedule_date: datetime, notes: Optional[str]) -> CalibrationPlan:
        plan = CalibrationPlan(equipment_id=equipment_id, schedule_date=schedule_date, next_due_at=schedule_date, notes=notes)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def list_calibration_plans(self, equipment_id: Optional[int] = None) -> List[CalibrationPlan]:
        q = self.db.query(CalibrationPlan)
        if equipment_id is not None:
            q = q.filter(CalibrationPlan.equipment_id == equipment_id)
        return q.order_by(CalibrationPlan.next_due_at.asc().nulls_last()).all()

    def record_calibration(self, *, plan_id: int, original_filename: str, stored_filename: str, file_path: str, file_type: Optional[str], uploaded_by: int) -> CalibrationRecord:
        rec = CalibrationRecord(plan_id=plan_id, original_filename=original_filename, stored_filename=stored_filename, file_path=file_path, file_type=file_type, uploaded_by=uploaded_by)
        # Update plan last/next
        plan = self.db.query(CalibrationPlan).filter(CalibrationPlan.id == plan_id).first()
        if plan:
            plan.last_calibrated_at = datetime.utcnow()
            # Keep schedule cadence by adding (next_due - last_calibrated) delta if exists, else leave next_due
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec


