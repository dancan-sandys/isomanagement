from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from datetime import datetime
from fastapi.responses import FileResponse

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.equipment import CalibrationRecord
from app.models.user import User
from app.services.equipment_service import EquipmentService
from app.schemas.equipment import (
    EquipmentCreate, EquipmentResponse,
    MaintenancePlanCreate, MaintenancePlanResponse,
    MaintenanceWorkOrderCreate, MaintenanceWorkOrderResponse,
    CalibrationPlanCreate, CalibrationPlanResponse,
    CalibrationRecordResponse,
    EquipmentUpdate, MaintenancePlanUpdate, MaintenanceWorkOrderUpdate, CalibrationPlanUpdate,
)
from app.schemas.common import ResponseModel

router = APIRouter()

UPLOAD_DIR = "uploads/equipment"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Place static routes before dynamic '/{equipment_id}' routes to avoid path conflicts

@router.get("/stats", response_model=ResponseModel)
async def get_equipment_stats_root(
    db: Session = Depends(get_db)
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
async def get_upcoming_maintenance_root(
    db: Session = Depends(get_db)
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
async def get_overdue_calibrations_root(
    db: Session = Depends(get_db)
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
async def get_equipment_alerts_root(
    db: Session = Depends(get_db)
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


@router.get("/analytics/stats", response_model=ResponseModel)
async def get_equipment_stats(
    db: Session = Depends(get_db)
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


@router.get("/analytics/upcoming-maintenance", response_model=ResponseModel)
async def get_upcoming_maintenance(
    db: Session = Depends(get_db)
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


@router.get("/analytics/overdue-calibrations", response_model=ResponseModel)
async def get_overdue_calibrations(
    db: Session = Depends(get_db)
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


@router.get("/analytics/alerts", response_model=ResponseModel)
async def get_equipment_alerts(
    db: Session = Depends(get_db)
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


@router.post("/", response_model=EquipmentResponse)
async def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.create_equipment(name=payload.name, equipment_type=payload.equipment_type, serial_number=payload.serial_number, location=payload.location, notes=payload.notes, created_by=1, is_active=payload.is_active, critical_to_food_safety=payload.critical_to_food_safety)


@router.get("/", response_model=list[EquipmentResponse])
async def list_equipment(
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.list_equipment()


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    eq = svc.get_equipment(equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return eq


@router.get("/{equipment_id}/details", response_model=dict)
async def get_equipment_details(equipment_id: int, db: Session = Depends(get_db)):
    """Get comprehensive equipment details including maintenance plans, work orders, and calibration plans"""
    svc = EquipmentService(db)
    
    # Get equipment
    equipment = svc.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Get maintenance plans
    maintenance_plans = svc.list_maintenance_plans(equipment_id=equipment_id)
    
    # Get work orders
    work_orders = svc.list_work_orders(equipment_id=equipment_id)
    
    # Get calibration plans
    calibration_plans = svc.list_calibration_plans(equipment_id=equipment_id)
    
    return {
        "equipment": equipment,
        "maintenance_plans": maintenance_plans,
        "work_orders": work_orders,
        "calibration_plans": calibration_plans
    }


@router.get("/{equipment_id}/history", response_model=dict)
async def get_equipment_history(equipment_id: int, db: Session = Depends(get_db)):
    """Get equipment history including all maintenance, work orders, and calibration activities"""
    svc = EquipmentService(db)
    
    # Verify equipment exists
    equipment = svc.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Get all work orders (completed and in progress)
    work_orders = svc.list_work_orders(equipment_id=equipment_id)
    
    # Get maintenance history
    maintenance_plans = svc.list_maintenance_plans(equipment_id=equipment_id)
    
    # Get calibration history
    calibration_plans = svc.list_calibration_plans(equipment_id=equipment_id)
    
    # Combine and sort by date
    history_items = []
    
    # Add work orders to history
    for wo in work_orders:
        history_items.append({
            "type": "work_order",
            "date": wo.created_at,
            "title": wo.title,
            "status": wo.status.value if wo.status else None,
            "description": wo.description,
            "data": wo
        })
    
    # Add maintenance activities to history
    for plan in maintenance_plans:
        if plan.last_performed_at:
            history_items.append({
                "type": "maintenance",
                "date": plan.last_performed_at,
                "title": f"Maintenance: {plan.maintenance_type.value if plan.maintenance_type else 'Unknown'}",
                "status": "completed",
                "description": plan.notes,
                "data": plan
            })
    
    # Add calibration activities to history
    for plan in calibration_plans:
        if plan.last_calibrated_at:
            history_items.append({
                "type": "calibration",
                "date": plan.last_calibrated_at,
                "title": "Calibration",
                "status": "completed",
                "description": plan.notes,
                "data": plan
            })
    
    # Sort by date (newest first)
    history_items.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "equipment_id": equipment_id,
        "equipment_name": equipment.name,
        "history": history_items,
        "total_items": len(history_items)
    }


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    eq = svc.update_equipment(equipment_id, **payload.dict(exclude_unset=True))
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return eq


@router.delete("/{equipment_id}", response_model=ResponseModel)
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    ok = svc.delete_equipment(equipment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return ResponseModel(success=True, message="Equipment deleted")


# Backward compatibility endpoints for frontend - these must come BEFORE specific equipment routes
@router.get("/maintenance-plans", response_model=list[MaintenancePlanResponse])
async def list_all_maintenance_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Backward compatibility endpoint - returns all maintenance plans"""
    svc = EquipmentService(db)
    all_plans = []
    # Get all equipment and their maintenance plans
    equipment_list = svc.list_equipment()
    for equipment in equipment_list:
        plans = svc.list_maintenance_plans(equipment_id=equipment.id)
        for plan in plans:
            equipment_name = plan.equipment.name if getattr(plan, "equipment", None) else None
            status = None
            if plan.next_due_at:
                if plan.next_due_at < datetime.utcnow():
                    status = "overdue"
                elif plan.next_due_at <= datetime.utcnow():
                    status = "due"
                else:
                    status = "on_schedule"
            all_plans.append(MaintenancePlanResponse(
                id=plan.id,
                equipment_id=plan.equipment_id,
                frequency_days=plan.frequency_days,
                maintenance_type=plan.maintenance_type.value if plan.maintenance_type else None,
                last_performed_at=plan.last_performed_at,
                next_due_at=plan.next_due_at,
                active=plan.active,
                notes=plan.notes,
                equipment_name=equipment_name,
                last_maintenance_date=plan.last_performed_at,
                next_due_date=plan.next_due_at,
                status=status,
            ))
    return all_plans

@router.get("/all/work-orders", response_model=list[MaintenanceWorkOrderResponse])
async def list_all_work_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Backward compatibility endpoint - returns all work orders"""
    svc = EquipmentService(db)
    all_work_orders = []
    # Get all equipment and their work orders
    equipment_list = svc.list_equipment()
    for equipment in equipment_list:
        work_orders = svc.list_work_orders(equipment_id=equipment.id)
        for work_order in work_orders:
            equipment_name = work_order.equipment.name if getattr(work_order, "equipment", None) else None
            all_work_orders.append(MaintenanceWorkOrderResponse(
                id=work_order.id,
                equipment_id=work_order.equipment_id,
                work_order_number=work_order.work_order_number,
                description=work_order.description,
                priority=work_order.priority.value if work_order.priority else None,
                status=work_order.status.value if work_order.status else None,
                assigned_to=work_order.assigned_to,
                scheduled_date=work_order.scheduled_date,
                completed_date=work_order.completed_date,
                equipment_name=equipment_name,
                maintenance_type=work_order.maintenance_type.value if work_order.maintenance_type else None,
                estimated_hours=work_order.estimated_hours,
                actual_hours=work_order.actual_hours,
                parts_used=work_order.parts_used,
                notes=work_order.notes,
            ))
    return all_work_orders

@router.get("/all/calibration-plans", response_model=list[CalibrationPlanResponse])
async def list_all_calibration_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Backward compatibility endpoint - returns all calibration plans"""
    svc = EquipmentService(db)
    all_calibration_plans = []
    # Get all equipment and their calibration plans
    equipment_list = svc.list_equipment()
    for equipment in equipment_list:
        calibration_plans = svc.list_calibration_plans(equipment_id=equipment.id)
        for plan in calibration_plans:
            equipment_name = plan.equipment.name if getattr(plan, "equipment", None) else None
            all_calibration_plans.append(CalibrationPlanResponse(
                id=plan.id,
                equipment_id=plan.equipment_id,
                calibration_type=plan.calibration_type.value if plan.calibration_type else None,
                frequency_days=plan.frequency_days,
                last_calibrated_at=plan.last_calibrated_at,
                next_due_at=plan.next_due_at,
                active=plan.active,
                notes=plan.notes,
                equipment_name=equipment_name,
                calibration_standard=plan.calibration_standard,
                tolerance=plan.tolerance,
                calibration_procedure=plan.calibration_procedure,
            ))
    return all_calibration_plans

# Maintenance
@router.post("/{equipment_id}/maintenance-plans", response_model=MaintenancePlanResponse)
async def create_maintenance_plan(
    equipment_id: int,
    payload: MaintenancePlanCreate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.create_maintenance_plan(equipment_id=equipment_id, frequency_days=payload.frequency_days, maintenance_type=payload.maintenance_type, notes=payload.notes)


@router.get("/{equipment_id}/maintenance-plans", response_model=list[MaintenancePlanResponse])
async def list_maintenance_plans(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    plans = svc.list_maintenance_plans(equipment_id=equipment_id)
    enriched: list[MaintenancePlanResponse] = []
    for plan in plans:
        equipment_name = plan.equipment.name if getattr(plan, "equipment", None) else None
        status = None
        if plan.next_due_at:
            if plan.next_due_at < datetime.utcnow():
                status = "overdue"
            elif plan.next_due_at <= datetime.utcnow():
                status = "due"
            else:
                status = "on_schedule"
        enriched.append(MaintenancePlanResponse(
            id=plan.id,
            equipment_id=plan.equipment_id,
            frequency_days=plan.frequency_days,
            maintenance_type=plan.maintenance_type.value if plan.maintenance_type else None,
            last_performed_at=plan.last_performed_at,
            next_due_at=plan.next_due_at,
            active=plan.active,
            notes=plan.notes,
            equipment_name=equipment_name,
            last_maintenance_date=plan.last_performed_at,
            next_due_date=plan.next_due_at,
            status=status,
        ))
    return enriched


@router.put("/maintenance-plans/{plan_id}", response_model=MaintenancePlanResponse)
async def update_maintenance_plan(
    plan_id: int,
    payload: MaintenancePlanUpdate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    plan = svc.update_maintenance_plan(plan_id, **payload.dict(exclude_unset=True))
    if not plan:
        raise HTTPException(status_code=404, detail="Maintenance plan not found")
    equipment_name = plan.equipment.name if getattr(plan, "equipment", None) else None
    status = None
    if plan.next_due_at:
        if plan.next_due_at < datetime.utcnow():
            status = "overdue"
        elif plan.next_due_at <= datetime.utcnow():
            status = "due"
        else:
            status = "on_schedule"
    return MaintenancePlanResponse(
        id=plan.id,
        equipment_id=plan.equipment_id,
        frequency_days=plan.frequency_days,
        maintenance_type=plan.maintenance_type.value if plan.maintenance_type else None,
        last_performed_at=plan.last_performed_at,
        next_due_at=plan.next_due_at,
        active=plan.active,
        notes=plan.notes,
        equipment_name=equipment_name,
        last_maintenance_date=plan.last_performed_at,
        next_due_date=plan.next_due_at,
        status=status,
    )


@router.delete("/maintenance-plans/{plan_id}", response_model=ResponseModel)
async def delete_maintenance_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    ok = svc.delete_maintenance_plan(plan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Maintenance plan not found")
    return ResponseModel(success=True, message="Maintenance plan deleted")


# Work Orders
@router.post("/{equipment_id}/work-orders", response_model=MaintenanceWorkOrderResponse)
async def create_work_order(
    equipment_id: int,
    payload: MaintenanceWorkOrderCreate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.create_work_order(equipment_id=equipment_id, plan_id=payload.plan_id, title=payload.title, description=payload.description, priority=payload.priority, assigned_to=payload.assigned_to, due_date=payload.due_date, created_by=1)


@router.get("/{equipment_id}/work-orders", response_model=list[MaintenanceWorkOrderResponse])
async def list_work_orders(
    equipment_id: int,
    plan_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    items = svc.list_work_orders(equipment_id=equipment_id, plan_id=plan_id, status=status)
    enriched: list[MaintenanceWorkOrderResponse] = []
    for wo in items:
        eq = svc.get_equipment(wo.equipment_id)
        enriched.append(MaintenanceWorkOrderResponse(
            id=wo.id,
            equipment_id=wo.equipment_id,
            plan_id=wo.plan_id,
            title=wo.title,
            description=wo.description,
            created_at=wo.created_at,
            completed_at=wo.completed_at,
            completed_by=wo.completed_by,
            status=wo.status.value if wo.status else None,
            priority=wo.priority.value if wo.priority else None,
            assigned_to=wo.assigned_to,
            due_date=wo.due_date,
            created_by=wo.created_by,
            equipment_name=eq.name if eq else None,
        ))
    return enriched


@router.get("/work-orders/{work_order_id}", response_model=MaintenanceWorkOrderResponse)
async def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    wo = svc.get_work_order(work_order_id)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    eq = svc.get_equipment(wo.equipment_id)
    return MaintenanceWorkOrderResponse(
        id=wo.id,
        equipment_id=wo.equipment_id,
        plan_id=wo.plan_id,
        title=wo.title,
        description=wo.description,
        created_at=wo.created_at,
        completed_at=wo.completed_at,
        completed_by=wo.completed_by,
        status=wo.status.value if wo.status else None,
        priority=wo.priority.value if wo.priority else None,
        assigned_to=wo.assigned_to,
        due_date=wo.due_date,
        created_by=wo.created_by,
        equipment_name=eq.name if eq else None,
    )


@router.put("/work-orders/{work_order_id}", response_model=MaintenanceWorkOrderResponse)
async def update_work_order(
    work_order_id: int,
    payload: MaintenanceWorkOrderUpdate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    wo = svc.update_work_order(work_order_id, **payload.dict(exclude_unset=True))
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    eq = svc.get_equipment(wo.equipment_id)
    return MaintenanceWorkOrderResponse(
        id=wo.id,
        equipment_id=wo.equipment_id,
        plan_id=wo.plan_id,
        title=wo.title,
        description=wo.description,
        created_at=wo.created_at,
        completed_at=wo.completed_at,
        completed_by=wo.completed_by,
        status=wo.status.value if wo.status else None,
        priority=wo.priority.value if wo.priority else None,
        assigned_to=wo.assigned_to,
        due_date=wo.due_date,
        created_by=wo.created_by,
        equipment_name=eq.name if eq else None,
    )


@router.post("/work-orders/{work_order_id}/complete", response_model=MaintenanceWorkOrderResponse)
async def complete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    wo = svc.complete_work_order(work_order_id, completed_by=1)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    eq = svc.get_equipment(wo.equipment_id)
    return MaintenanceWorkOrderResponse(
        id=wo.id,
        equipment_id=wo.equipment_id,
        plan_id=wo.plan_id,
        title=wo.title,
        description=wo.description,
        created_at=wo.created_at,
        completed_at=wo.completed_at,
        completed_by=wo.completed_by,
        status=wo.status.value if wo.status else None,
        priority=wo.priority.value if wo.priority else None,
        assigned_to=wo.assigned_to,
        due_date=wo.due_date,
        created_by=wo.created_by,
        equipment_name=eq.name if eq else None,
    )


@router.delete("/work-orders/{work_order_id}", response_model=ResponseModel)
async def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    ok = svc.delete_work_order(work_order_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Work order not found")
    return ResponseModel(success=True, message="Work order deleted")


# Calibration
@router.post("/{equipment_id}/calibration-plans", response_model=CalibrationPlanResponse)
async def create_calibration_plan(
    equipment_id: int,
    payload: CalibrationPlanCreate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.create_calibration_plan(equipment_id=equipment_id, schedule_date=payload.schedule_date, frequency_days=payload.frequency_days, notes=payload.notes)


@router.get("/{equipment_id}/calibration-plans", response_model=list[CalibrationPlanResponse])
async def list_calibration_plans(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    items = svc.list_calibration_plans(equipment_id=equipment_id)
    enriched: list[CalibrationPlanResponse] = []
    for plan in items:
        equipment_name = plan.equipment.name if getattr(plan, "equipment", None) else None
        status = None
        if plan.next_due_at:
            if plan.next_due_at < datetime.utcnow():
                status = "overdue"
            elif plan.next_due_at <= datetime.utcnow():
                status = "due"
            else:
                status = "scheduled"
        enriched.append(CalibrationPlanResponse(
            id=plan.id,
            equipment_id=plan.equipment_id,
            schedule_date=plan.schedule_date,
            frequency_days=plan.frequency_days,
            last_calibrated_at=plan.last_calibrated_at,
            next_due_at=plan.next_due_at,
            active=plan.active,
            notes=plan.notes,
            equipment_name=equipment_name,
            last_calibration_date=plan.last_calibrated_at,
            status=status,
            certificate_file=False,
        ))
    return enriched


@router.put("/calibration-plans/{plan_id}", response_model=CalibrationPlanResponse)
async def update_calibration_plan(
    plan_id: int,
    payload: CalibrationPlanUpdate,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    plan = svc.update_calibration_plan(plan_id, **payload.dict(exclude_unset=True))
    if not plan:
        raise HTTPException(status_code=404, detail="Calibration plan not found")
    equipment_name = plan.equipment.name if getattr(plan, "equipment", None) else None
    status = None
    if plan.next_due_at:
        if plan.next_due_at < datetime.utcnow():
            status = "overdue"
        elif plan.next_due_at <= datetime.utcnow():
            status = "due"
        else:
            status = "scheduled"
    return CalibrationPlanResponse(
        id=plan.id,
        equipment_id=plan.equipment_id,
        schedule_date=plan.schedule_date,
        frequency_days=plan.frequency_days,
        last_calibrated_at=plan.last_calibrated_at,
        next_due_at=plan.next_due_at,
        active=plan.active,
        notes=plan.notes,
        equipment_name=equipment_name,
        last_calibration_date=plan.last_calibrated_at,
        status=status,
        certificate_file=False,
    )


@router.delete("/calibration-plans/{plan_id}", response_model=ResponseModel)
async def delete_calibration_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    ok = svc.delete_calibration_plan(plan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Calibration plan not found")
    return ResponseModel(success=True, message="Calibration plan deleted")


@router.post("/calibration-plans/{plan_id}/records", response_model=CalibrationRecordResponse)
async def upload_calibration_certificate(
    plan_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    unique = f"{uuid4().hex}_{file.filename}"
    cert_dir = os.path.join(UPLOAD_DIR, "calibration")
    os.makedirs(cert_dir, exist_ok=True)
    file_path = os.path.join(cert_dir, unique)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    svc = EquipmentService(db)
    rec = svc.record_calibration(plan_id=plan_id, original_filename=file.filename, stored_filename=unique, file_path=file_path, file_type=file.content_type, uploaded_by=1)
    return rec


@router.get("/calibration-records/{record_id}/download")
async def download_calibration_certificate(
    record_id: int,
    db: Session = Depends(get_db)
):
    rec = db.query(CalibrationRecord).filter_by(id=record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    if not os.path.exists(rec.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(rec.file_path, filename=rec.original_filename, media_type=rec.file_type or "application/octet-stream")


# History endpoints (raw lists)
@router.get("/maintenance-history")
async def maintenance_history(
    equipment_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.get_maintenance_history(equipment_id=equipment_id, start_date=start_date, end_date=end_date)


@router.get("/calibration-history")
async def calibration_history(
    equipment_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db)
):
    svc = EquipmentService(db)
    return svc.get_calibration_history(equipment_id=equipment_id, start_date=start_date, end_date=end_date)


# Equipment Analytics Endpoints (kept above dynamic routes)


