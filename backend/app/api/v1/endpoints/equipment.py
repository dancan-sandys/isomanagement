from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.equipment_service import EquipmentService
from app.schemas.equipment import (
    EquipmentCreate, EquipmentResponse,
    MaintenancePlanCreate, MaintenancePlanResponse,
    MaintenanceWorkOrderCreate, MaintenanceWorkOrderResponse,
    CalibrationPlanCreate, CalibrationPlanResponse,
    CalibrationRecordResponse,
)
from app.schemas.common import ResponseModel

router = APIRouter()

UPLOAD_DIR = "uploads/equipment"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=EquipmentResponse)
async def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.create_equipment(name=payload.name, equipment_type=payload.equipment_type, serial_number=payload.serial_number, location=payload.location, notes=payload.notes, created_by=current_user.id)


@router.get("/", response_model=list[EquipmentResponse])
async def list_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.list_equipment()


# Maintenance
@router.post("/{equipment_id}/maintenance-plans", response_model=MaintenancePlanResponse)
async def create_maintenance_plan(
    equipment_id: int,
    payload: MaintenancePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.create_maintenance_plan(equipment_id=equipment_id, frequency_days=payload.frequency_days, maintenance_type=payload.maintenance_type, notes=payload.notes)


@router.get("/{equipment_id}/maintenance-plans", response_model=list[MaintenancePlanResponse])
async def list_maintenance_plans(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.list_maintenance_plans(equipment_id=equipment_id)


@router.post("/work-orders", response_model=MaintenanceWorkOrderResponse)
async def create_work_order(
    payload: MaintenanceWorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.create_work_order(equipment_id=payload.equipment_id, plan_id=payload.plan_id, title=payload.title, description=payload.description)


@router.post("/work-orders/{work_order_id}/complete", response_model=MaintenanceWorkOrderResponse)
async def complete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    wo = svc.complete_work_order(work_order_id, completed_by=current_user.id)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return wo


@router.get("/work-orders", response_model=list[MaintenanceWorkOrderResponse])
async def list_work_orders(
    equipment_id: int | None = Query(default=None),
    plan_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.list_work_orders(equipment_id=equipment_id, plan_id=plan_id)


# Calibration
@router.post("/{equipment_id}/calibration-plans", response_model=CalibrationPlanResponse)
async def create_calibration_plan(
    equipment_id: int,
    payload: CalibrationPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.create_calibration_plan(equipment_id=equipment_id, schedule_date=payload.schedule_date, notes=payload.notes)


@router.get("/{equipment_id}/calibration-plans", response_model=list[CalibrationPlanResponse])
async def list_calibration_plans(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EquipmentService(db)
    return svc.list_calibration_plans(equipment_id=equipment_id)


@router.post("/calibration-plans/{plan_id}/records", response_model=CalibrationRecordResponse)
async def upload_calibration_certificate(
    plan_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unique = f"{uuid4().hex}_{file.filename}"
    cert_dir = os.path.join(UPLOAD_DIR, "calibration")
    os.makedirs(cert_dir, exist_ok=True)
    file_path = os.path.join(cert_dir, unique)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    svc = EquipmentService(db)
    rec = svc.record_calibration(plan_id=plan_id, original_filename=file.filename, stored_filename=unique, file_path=file_path, file_type=file.content_type, uploaded_by=current_user.id)
    return rec


# Equipment Analytics Endpoints
@router.get("/stats", response_model=ResponseModel)
async def get_equipment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment statistics and analytics"""
    try:
        svc = EquipmentService(db)
        stats = svc.get_equipment_stats()
        return ResponseModel(
            success=True,
            message="Equipment statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve equipment stats: {str(e)}")


@router.get("/upcoming-maintenance", response_model=ResponseModel)
async def get_upcoming_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming maintenance schedules"""
    try:
        svc = EquipmentService(db)
        maintenance = svc.get_upcoming_maintenance()
        return ResponseModel(
            success=True,
            message="Upcoming maintenance retrieved successfully",
            data=maintenance
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve upcoming maintenance: {str(e)}")


@router.get("/overdue-calibrations", response_model=ResponseModel)
async def get_overdue_calibrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue calibration schedules"""
    try:
        svc = EquipmentService(db)
        calibrations = svc.get_overdue_calibrations()
        return ResponseModel(
            success=True,
            message="Overdue calibrations retrieved successfully",
            data=calibrations
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve overdue calibrations: {str(e)}")


@router.get("/alerts", response_model=ResponseModel)
async def get_equipment_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment alerts and notifications"""
    try:
        svc = EquipmentService(db)
        alerts = svc.get_equipment_alerts()
        return ResponseModel(
            success=True,
            message="Equipment alerts retrieved successfully",
            data=alerts
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve equipment alerts: {str(e)}")


