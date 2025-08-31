from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.database import get_db
from app.services.production_service import ProductionService
from app.schemas.production import (
    ProcessCreate, ProcessLogCreate, YieldCreate, TransferCreate, AgingCreate,
    ProcessParameterCreate, ProcessDeviationCreate, ProcessAlertCreate,
    ProcessTemplateCreate, ProcessTemplateUpdate, ProcessCreateEnhanced,
    ProcessUpdate, ProcessResponse, ProcessParameterResponse, ProcessDeviationResponse,
    ProcessAlertResponse, ProcessTemplateResponse, ProductionAnalytics,
    ProcessControlChartCreate, ProcessControlChartResponse, ProcessControlPointResponse,
    ProcessCapabilityStudyCreate, ProcessCapabilityStudyResponse,
    YieldAnalysisReportCreate, YieldAnalysisReportResponse, YieldDefectCategoryResponse,
    ProcessMonitoringAlertResponse, ProcessMonitoringAlertUpdate,
    ProcessMonitoringDashboardCreate, ProcessMonitoringDashboardResponse,
    ProcessMonitoringAnalytics, ControlChartData,
    # FSM Schemas
    ProcessCreateWithStages, ProcessStartRequest, ProcessStageCompletionRequest,
    ProcessSummaryResponse, StageMonitoringRequirementCreate, StageMonitoringRequirementResponse,
    StageMonitoringLogCreate, StageMonitoringLogResponse
)
from app.schemas.production import ProcessSpecBindRequest, ReleaseCheckResponse, ReleaseRequest, ReleaseResponse
from app.schemas.production import MaterialConsumptionCreate
from app.models.production import ProductProcessType, ProcessStatus
from app.core.security import get_current_active_user
from app.core.permissions import require_permission_dependency
from app.models.production import ProcessParameter as PP
from app.models.production import MaterialConsumption as MC
from app.models.audit import AuditLog

router = APIRouter()


@router.get("/analytics")
def get_analytics(process_type: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = ProductionService(db)
    pt = ProductProcessType(process_type) if process_type else None
    return service.get_analytics(pt)


@router.post("/process")
def create_process(payload: ProcessCreate, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:create"))):
    service = ProductionService(db)
    try:
        pt = ProductProcessType(payload.process_type)
        proc = service.create_process(payload.batch_id, pt, payload.operator_id, payload.spec)
        return proc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/log")
def add_log(process_id: int, payload: ProcessLogCreate, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:update"))):
    service = ProductionService(db)
    try:
        log = service.add_log(process_id, payload.model_dump())
        return log
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/yield")
def record_yield(process_id: int, payload: YieldCreate, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:update"))):
    service = ProductionService(db)
    try:
        yr = service.record_yield(process_id, payload.output_qty, payload.unit, payload.expected_qty)
        return yr
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/transfer")
def record_transfer(process_id: int, payload: TransferCreate, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:update"))):
    service = ProductionService(db)
    try:
        tr = service.record_transfer(process_id, payload.quantity, payload.unit, payload.location, payload.lot_number, payload.verified_by)
        return tr
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/aging")
def record_aging(process_id: int, payload: AgingCreate, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:update"))):
    service = ProductionService(db)
    try:
        ar = service.record_aging(process_id, payload.model_dump())
        return ar
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Enhanced Production Endpoints
@router.post("/processes", response_model=ProcessResponse)
def create_process_enhanced(payload: ProcessCreateEnhanced, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:create"))):
    """Create a new production process with enhanced features"""
    service = ProductionService(db)
    try:
        print(f"DEBUG: Received payload: batch_id={payload.batch_id}, process_type={payload.process_type}, operator_id={payload.operator_id}")
        
        if payload.template_id:
            # Use template if provided
            template = service.get_process_templates()
            # TODO: Implement template-based process creation
            pass
        
        proc = service.create_process(
            payload.batch_id, 
            ProductProcessType(payload.process_type), 
            payload.operator_id, 
            payload.spec or {}
        )
        return proc
    except ValueError as e:
        print(f"DEBUG: ValueError in create_process_enhanced: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"DEBUG: Unexpected error in create_process_enhanced: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create process: {str(e)}")


@router.get("/processes", response_model=List[ProcessResponse])
def list_processes(
    process_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """List production processes with filtering"""
    service = ProductionService(db)
    
    # Safe enum conversion with error handling
    pt = None
    if process_type:
        try:
            pt = ProductProcessType(process_type)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid process_type: {process_type}")
    
    st = None
    if status:
        try:
            st = ProcessStatus(status)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
    
    processes = service.list_processes(pt, st, limit, offset)
    
    # Convert to response format with empty related data
    result = []
    for process in processes:
        process_dict = {
            "id": process.id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value if hasattr(process.process_type, 'value') else str(process.process_type),
            "operator_id": process.operator_id,
            "status": process.status.value if hasattr(process.status, 'value') else str(process.status),
            "start_time": process.start_time,
            "end_time": process.end_time,
            "spec": process.spec,
            "notes": process.notes,
            "created_at": process.created_at,
            "updated_at": process.updated_at,
            "steps": [],
            "logs": [],
            "parameters": [],
            "deviations": [],
            "alerts": []
        }
        result.append(process_dict)
    
    return result


@router.get("/templates", response_model=List[ProcessTemplateResponse])
def get_templates(
    product_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get process templates"""
    service = ProductionService(db)
    
    # Safe enum conversion with error handling
    pt = None
    if product_type:
        try:
            pt = ProductProcessType(product_type)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid product_type: {product_type}")
    
    templates = service.get_process_templates(pt)
    return templates





@router.put("/processes/{process_id}", response_model=ProcessResponse)
def update_process(
    process_id: int, 
    payload: ProcessUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Update a production process"""
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        updated = service.update_process(process_id, payload.model_dump(exclude_unset=True))
        
        # Convert to response format
        process_dict = {
            "id": updated.id,
            "batch_id": updated.batch_id,
            "process_type": updated.process_type.value if hasattr(updated.process_type, 'value') else str(updated.process_type),
            "operator_id": updated.operator_id,
            "status": updated.status.value if hasattr(updated.status, 'value') else str(updated.status),
            "start_time": updated.start_time,
            "end_time": updated.end_time,
            "spec": updated.spec,
            "notes": updated.notes,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at,
            "steps": [],
            "logs": [],
            "parameters": [],
            "deviations": [],
            "alerts": []
        }
        return process_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/parameters", response_model=ProcessParameterResponse)
def record_parameter(
    process_id: int, 
    payload: ProcessParameterCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Record a process parameter"""
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["recorded_by"] = getattr(current_user, "id", None)
        parameter = service.record_parameter(process_id, data)
        return parameter
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/parameters", response_model=List[ProcessParameterResponse])
def get_process_parameters(process_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:view"))):
    """Get all parameters for a process"""
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    
    return service.get_process_parameters(process_id)


@router.post("/processes/{process_id}/deviations", response_model=ProcessDeviationResponse)
def create_deviation(
    process_id: int, 
    payload: ProcessDeviationCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Create a process deviation"""
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["created_by"] = getattr(current_user, "id", None)
        deviation = service._create_deviation(process_id, data)
        return deviation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/deviations/{deviation_id}/resolve")
def resolve_deviation(
    deviation_id: int, 
    corrective_action: str = Query(..., description="Corrective action taken"),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Resolve a process deviation"""
    service = ProductionService(db)
    try:
        user_id = getattr(current_user, "id", None)
        deviation = service.resolve_deviation(deviation_id, user_id, corrective_action)
        return {"message": "Deviation resolved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/alerts", response_model=ProcessAlertResponse)
def create_alert(
    process_id: int, 
    payload: ProcessAlertCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Create a process alert"""
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["created_by"] = getattr(current_user, "id", None)
        alert = service.create_alert(process_id, data)
        return alert
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:update"))):
    """Acknowledge a process alert"""
    service = ProductionService(db)
    try:
        user_id = getattr(current_user, "id", None)
        alert = service.acknowledge_alert(alert_id, user_id)
        return {"message": "Alert acknowledged successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/templates", response_model=ProcessTemplateResponse)
def create_template(payload: ProcessTemplateCreate, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:create"))):
    """Create a process template"""
    service = ProductionService(db)
    try:
        template = service.create_process_template(payload.model_dump())
        return template
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=List[ProcessTemplateResponse])
def get_templates(
    product_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get process templates"""
    service = ProductionService(db)
    pt = ProductProcessType(product_type) if product_type else None
    templates = service.get_process_templates(pt)
    return templates
@router.get("/analytics/enhanced", response_model=ProductionAnalytics)
def get_enhanced_analytics(
    process_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get comprehensive production analytics"""
    service = ProductionService(db)
    pt = ProductProcessType(process_type) if process_type else None
    analytics = service.get_enhanced_analytics(pt)
    return analytics

@router.get("/analytics/export/csv")
def export_analytics_csv(
    process_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    service = ProductionService(db)
    pt = ProductProcessType(process_type) if process_type else None
    data = service.get_enhanced_analytics(pt)
    # Build a simple CSV with key metrics and trend rows
    import csv, io as _io
    buf = _io.StringIO()
    w = csv.writer(buf)
    w.writerow(["metric", "value"])
    w.writerow(["total_deviations", data.get("total_deviations")])
    w.writerow(["critical_deviations", data.get("critical_deviations")])
    w.writerow(["total_alerts", data.get("total_alerts")])
    w.writerow(["unacknowledged_alerts", data.get("unacknowledged_alerts")])
    w.writerow([])
    w.writerow(["process_type", "count"])
    for k, v in (data.get("process_type_breakdown") or {}).items():
        w.writerow([k, v])
    w.writerow([])
    w.writerow(["yield_trend_date", "count"])
    for r in (data.get("yield_trends") or []):
        w.writerow([r.get("date"), r.get("count")])
    w.writerow([])
    w.writerow(["deviation_trend_date", "count"])
    for r in (data.get("deviation_trends") or []):
        w.writerow([r.get("date"), r.get("count")])
    out = buf.getvalue().encode("utf-8")
    return StreamingResponse(io.BytesIO(out), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=production_analytics.csv"})

@router.get("/analytics/export/pdf")
def export_analytics_pdf(
    process_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    service = ProductionService(db)
    pt = ProductProcessType(process_type) if process_type else None
    data = service.get_enhanced_analytics(pt)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    x, y = 40, height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Production Analytics Summary")
    y -= 18
    c.setFont("Helvetica", 10)
    metrics = [
        ("Total deviations", data.get("total_deviations")),
        ("Critical deviations", data.get("critical_deviations")),
        ("Total alerts", data.get("total_alerts")),
        ("Unacknowledged alerts", data.get("unacknowledged_alerts")),
    ]
    for k, v in metrics:
        c.drawString(x, y, f"{k}: {v}"); y -= 14
    y -= 6
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Process Type Breakdown"); y -= 16
    c.setFont("Helvetica", 10)
    for k, v in (data.get("process_type_breakdown") or {}).items():
        if y < 60:
            c.showPage(); y = height - 40; c.setFont("Helvetica", 10)
        c.drawString(x, y, f"{k}: {v}"); y -= 12
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "30-Day Yield Trend"); y -= 16
    c.setFont("Helvetica", 10)
    for r in (data.get("yield_trends") or [])[:30]:
        if y < 60:
            c.showPage(); y = height - 40; c.setFont("Helvetica", 10)
        c.drawString(x, y, f"{r.get('date')}: {r.get('count')}"); y -= 12
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "30-Day Deviation Trend"); y -= 16
    c.setFont("Helvetica", 10)
    for r in (data.get("deviation_trends") or [])[:30]:
        if y < 60:
            c.showPage(); y = height - 40; c.setFont("Helvetica", 10)
        c.drawString(x, y, f"{r.get('date')}: {r.get('count')}"); y -= 12
    c.showPage(); c.save()
    return StreamingResponse(io.BytesIO(buf.getvalue()), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=production_analytics.pdf"})

@router.get("/processes/{process_id}/audit")
def list_process_audit(
    process_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    q = (
        db.query(AuditLog)
        .filter(AuditLog.resource_type == "production_process", AuditLog.resource_id == str(process_id))
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = q.all()
    return [{
        "id": r.id,
        "user_id": r.user_id,
        "action": r.action,
        "details": r.details,
        "created_at": r.created_at,
        "ip_address": r.ip_address,
        "user_agent": r.user_agent,
    } for r in rows]

@router.get("/processes/{process_id}/details", response_model=ProcessResponse)
def get_process_details(process_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:view"))):
    """Get process with details (steps, logs, parameters, deviations, alerts)"""
    service = ProductionService(db)
    details = service.get_process_with_details(process_id)
    if not details:
        raise HTTPException(status_code=404, detail="Process not found")
    # Flatten to match ProcessResponse fields while including related lists
    process = details["process"]
    response = {
        "id": process.id,
        "batch_id": process.batch_id,
        "process_type": process.process_type.value if hasattr(process.process_type, "value") else str(process.process_type),
        "operator_id": process.operator_id,
        "status": process.status.value if hasattr(process.status, "value") else str(process.status),
        "start_time": process.start_time,
        "end_time": process.end_time,
        "spec": process.spec,
        "notes": getattr(process, "notes", None),
        "created_at": process.created_at,
        "updated_at": process.updated_at,
        "steps": [
            {
                "id": s.id,
                "step_type": s.step_type.value if hasattr(s.step_type, "value") else str(s.step_type),
                "sequence": s.sequence,
                "target_temp_c": s.target_temp_c,
                "target_time_seconds": s.target_time_seconds,
                "tolerance_c": s.tolerance_c,
                "required": s.required,
                "step_metadata": s.step_metadata,
            }
            for s in details["steps"]
        ],
        "logs": [
            {
                "id": l.id,
                "step_id": l.step_id,
                "timestamp": l.timestamp,
                "event": l.event.value if hasattr(l.event, "value") else str(l.event),
                "measured_temp_c": l.measured_temp_c,
                "note": l.note,
                "auto_flag": l.auto_flag,
                "source": l.source,
            }
            for l in details["logs"]
        ],
        "parameters": [
            {
                "id": p.id,
                "process_id": p.process_id,
                "step_id": p.step_id,
                "parameter_name": p.parameter_name,
                "parameter_value": p.parameter_value,
                "unit": p.unit,
                "target_value": p.target_value,
                "tolerance_min": p.tolerance_min,
                "tolerance_max": p.tolerance_max,
                "is_within_tolerance": p.is_within_tolerance,
                "recorded_at": p.recorded_at,
                "recorded_by": p.recorded_by,
                "notes": p.notes,
            }
            for p in details["parameters"]
        ],
        "deviations": [
            {
                "id": d.id,
                "process_id": d.process_id,
                "step_id": d.step_id,
                "parameter_id": d.parameter_id,
                "deviation_type": d.deviation_type,
                "expected_value": d.expected_value,
                "actual_value": d.actual_value,
                "deviation_percent": d.deviation_percent,
                "severity": d.severity,
                "impact_assessment": d.impact_assessment,
                "corrective_action": d.corrective_action,
                "resolved": d.resolved,
                "resolved_at": d.resolved_at,
                "resolved_by": d.resolved_by,
                "created_at": d.created_at,
                "created_by": d.created_by,
            }
            for d in details["deviations"]
        ],
        "alerts": [
            {
                "id": a.id,
                "process_id": a.process_id,
                "alert_type": a.alert_type,
                "alert_level": a.alert_level,
                "message": a.message,
                "parameter_value": a.parameter_value,
                "threshold_value": a.threshold_value,
                "acknowledged": a.acknowledged,
                "acknowledged_at": a.acknowledged_at,
                "acknowledged_by": a.acknowledged_by,
                "created_at": a.created_at,
                "created_by": a.created_by,
            }
            for a in details["alerts"]
        ],
    }
    response["stages_list"] = [
        {
            "id": st.id,
            "stage_name": st.stage_name,
            "sequence_order": st.sequence_order,
            "status": st.status.value if hasattr(st.status, 'value') else str(st.status),
            "is_ccp": st.is_critical_control_point,
            "requires_approval": st.requires_approval,
        }
        for st in details.get("stages", [])
    ]
    if details.get("active_stage"):
        a = details["active_stage"]
        response["active_stage"] = {
            "id": a.id,
            "name": a.stage_name,
            "sequence": a.sequence_order,
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
        }
    return response

@router.get("/processes/{process_id}/active-stage")
def get_active_stage_id(
    process_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Return the current active stage for a process (id, name, sequence, status)."""
    from app.models.production import ProcessStage, StageStatus
    st = (
        db.query(ProcessStage)
        .filter(ProcessStage.process_id == process_id, ProcessStage.status == StageStatus.IN_PROGRESS)
        .first()
    )
    if not st:
        return {"active_stage": None}
    return {
        "active_stage": {
            "id": st.id,
            "name": st.stage_name,
            "sequence": st.sequence_order,
            "status": st.status.value if hasattr(st.status, 'value') else str(st.status),
        }
    }

@router.post("/processes/{process_id}/spec/bind")
def bind_process_spec(
    process_id: int,
    payload: ProcessSpecBindRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("documents:view"))
):
    service = ProductionService(db)
    try:
        link = service.bind_spec_version(process_id, payload.document_id, payload.document_version, payload.locked_parameters)
        return {"message": "Spec bound", "process_id": process_id, "document_id": link.document_id, "document_version": link.document_version}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/release/check", response_model=ReleaseCheckResponse)
def check_release(process_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:view"))):
    service = ProductionService(db)
    try:
        result = service.check_release_ready(process_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/release", response_model=ReleaseResponse)
def release_process(
    process_id: int,
    payload: ReleaseRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("documents:approve"))
):
    service = ProductionService(db)
    try:
        check = service.check_release_ready(process_id)
        record = service.create_release(
            process_id,
            check,
            payload.released_qty,
            payload.unit,
            verifier_id=getattr(current_user, "id", None),
            approver_id=getattr(current_user, "id", None),
            signature_hash=payload.signature_hash,
        )
        return {"message": "Released successfully", "release_id": record.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/materials")
def record_material_consumption_endpoint(
    process_id: int,
    payload: MaterialConsumptionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("suppliers:update"))
):
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["recorded_by"] = getattr(current_user, "id", None)
        row = service.record_material_consumption(process_id, data)
        return {"message": "Material consumption recorded", "id": row.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/export/pdf")
def export_production_sheet_pdf(
    process_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Export a production sheet PDF including core process details, parameters, deviations, alerts, and release info."""
    service = ProductionService(db)
    details = service.get_process_with_details(process_id)
    if not details:
        raise HTTPException(status_code=404, detail="Process not found")
    release = service.get_latest_release(process_id)
    # Generate PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 40
    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, f"Production Sheet - Process #{details['process'].id}")
    y -= 18
    c.setFont("Helvetica", 10)
    proc = details['process']
    c.drawString(x, y, f"Type: {getattr(proc.process_type, 'value', str(proc.process_type))} | Status: {getattr(proc.status, 'value', str(proc.status))}")
    y -= 14
    c.drawString(x, y, f"Batch ID: {proc.batch_id} | Operator: {proc.operator_id or '-'} | Start: {proc.start_time}")
    y -= 14
    spec_link = service.get_spec_link(process_id)
    c.drawString(x, y, f"Spec Doc: {(spec_link.document_id if spec_link else '-') } v{(spec_link.document_version if spec_link else '-')}")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Parameters (latest 15)")
    y -= 16
    c.setFont("Helvetica", 9)
    for p in (details["parameters"] or [])[-15:]:
        line = f"{p.parameter_name}: {p.parameter_value}{p.unit}  target={p.target_value} tol=({p.tolerance_min}-{p.tolerance_max}) {'OOT' if p.is_within_tolerance is False else ''}"
        if y < 60:
            c.showPage(); y = height - 40; c.setFont("Helvetica", 9)
        c.drawString(x, y, line[:120]); y -= 12
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Deviations (latest 10)")
    y -= 16
    c.setFont("Helvetica", 9)
    for d in (details["deviations"] or [])[-10:]:
        line = f"{d.deviation_type}: actual {d.actual_value} vs {d.expected_value} • {d.severity} • {'resolved' if d.resolved else 'open'}"
        if y < 60:
            c.showPage(); y = height - 40; c.setFont("Helvetica", 9)
        c.drawString(x, y, line[:120]); y -= 12
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Alerts (latest 10)")
    y -= 16
    c.setFont("Helvetica", 9)
    for a in (details["alerts"] or [])[-10:]:
        line = f"{a.alert_level.upper()} {a.alert_type}: {a.message} • ack={'yes' if a.acknowledged else 'no'}"
        if y < 60:
            c.showPage(); y = height - 40; c.setFont("Helvetica", 9)
        c.drawString(x, y, line[:120]); y -= 12
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Release")
    y -= 16
    c.setFont("Helvetica", 9)
    if release:
        c.drawString(x, y, f"Released Qty: {release.released_qty or '-'} {release.unit or ''} • Signed: {release.signed_at} • SignHash: {release.signature_hash[:12] if release.signature_hash else '-'}")
        y -= 12
        # Print checklist summary
        try:
            checklist = release.checklist_results or {}
            for item in checklist.get("checklist", [])[:8]:
                if y < 60:
                    c.showPage(); y = height - 40; c.setFont("Helvetica", 9)
                c.drawString(x, y, f"- {item.get('item')}: {'OK' if item.get('passed') else 'FAIL'}"); y -= 12
        except Exception:
            pass
    else:
        c.drawString(x, y, "Not released")
        y -= 12
    # Materials
    try:
        rows = db.query(MC).filter(MC.process_id == process_id).order_by(MC.consumed_at.asc()).all()
        if rows:
            if y < 80:
                c.showPage(); y = height - 40
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y, "Materials Consumption")
            y -= 16
            c.setFont("Helvetica", 9)
            for m in rows[-12:]:
                if y < 60:
                    c.showPage(); y = height - 40; c.setFont("Helvetica", 9)
                c.drawString(x, y, f"Material {m.material_id} • {m.quantity} {m.unit} • Lot {m.lot_number or '-'}"); y -= 12
    except Exception:
        pass
    c.showPage(); c.save(); buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=production_sheet_{process_id}.pdf"})


# ===== ENHANCED PROCESS MONITORING AND SPC ENDPOINTS =====

@router.post("/processes/{process_id}/control-charts", response_model=ProcessControlChartResponse)
def create_control_chart(
    process_id: int,
    payload: ProcessControlChartCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Create a new control chart for SPC monitoring - ISO 22000:2018 Clause 8.5"""
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["created_by"] = getattr(current_user, "id", None)
        control_chart = service.create_control_chart(process_id, payload.parameter_name, data)
        return control_chart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/control-charts", response_model=List[ProcessControlChartResponse])
def get_process_control_charts(
    process_id: int,
    parameter_name: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get control charts for a process"""
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    
    from app.models.production import ProcessControlChart
    query = db.query(ProcessControlChart).filter(ProcessControlChart.process_id == process_id)
    
    if parameter_name:
        query = query.filter(ProcessControlChart.parameter_name == parameter_name)
    if active_only:
        query = query.filter(ProcessControlChart.is_active == True)
    
    charts = query.order_by(ProcessControlChart.created_at.desc()).all()
    return charts


@router.get("/control-charts/{chart_id}/data", response_model=ControlChartData)
def get_control_chart_data(
    chart_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get control chart data with visualization information"""
    from app.models.production import ProcessControlChart, ProcessControlPoint
    
    chart = db.query(ProcessControlChart).filter(ProcessControlChart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Control chart not found")
    
    # Get recent data points
    data_points = (
        db.query(ProcessControlPoint)
        .filter(ProcessControlPoint.control_chart_id == chart_id)
        .order_by(ProcessControlPoint.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    # Calculate statistics
    values = [p.measured_value for p in data_points]
    statistics_data = {
        "count": len(values),
        "mean": sum(values) / len(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
        "out_of_control_count": sum(1 for p in data_points if p.is_out_of_control),
        "last_violation": max((p.timestamp for p in data_points if p.is_out_of_control), default=None)
    }
    
    # Get violations
    violations = [
        {
            "timestamp": p.timestamp,
            "value": p.measured_value,
            "rule": p.control_rule_violated,
            "notes": p.notes
        }
        for p in data_points if p.is_out_of_control
    ]
    
    return ControlChartData(
        chart_info=chart,
        data_points=list(reversed(data_points)),  # Chronological order
        statistics=statistics_data,
        violations=violations
    )


@router.post("/processes/{process_id}/capability-studies", response_model=ProcessCapabilityStudyResponse)
def create_capability_study(
    process_id: int,
    payload: ProcessCapabilityStudyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Calculate process capability indices (Cp, Cpk) - ISO 22000:2018 requirements"""
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["conducted_by"] = getattr(current_user, "id", None)
        capability_study = service.calculate_process_capability(process_id, payload.parameter_name, data)
        return capability_study
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/capability-studies", response_model=List[ProcessCapabilityStudyResponse])
def get_capability_studies(
    process_id: int,
    parameter_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get process capability studies"""
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    
    from app.models.production import ProcessCapabilityStudy
    query = db.query(ProcessCapabilityStudy).filter(ProcessCapabilityStudy.process_id == process_id)
    
    if parameter_name:
        query = query.filter(ProcessCapabilityStudy.parameter_name == parameter_name)
    
    studies = query.order_by(ProcessCapabilityStudy.created_at.desc()).all()
    return studies


@router.post("/processes/{process_id}/yield-reports", response_model=YieldAnalysisReportResponse)
def create_yield_analysis_report(
    process_id: int,
    payload: YieldAnalysisReportCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Create comprehensive yield analysis report - ISO 22000:2018 monitoring"""
    service = ProductionService(db)
    try:
        data = payload.model_dump()
        data["analyzed_by"] = getattr(current_user, "id", None)
        yield_report = service.create_yield_analysis_report(process_id, data)
        
        # Include defect categories in response
        from app.models.production import YieldDefectCategory
        defect_categories = (
            db.query(YieldDefectCategory)
            .filter(YieldDefectCategory.yield_report_id == yield_report.id)
            .order_by(YieldDefectCategory.cumulative_percentage.asc())
            .all()
        )
        
        # Convert to response format
        report_dict = {
            **yield_report.__dict__,
            "defect_categories": [
                {
                    "id": dc.id,
                    "defect_type": dc.defect_type,
                    "defect_description": dc.defect_description,
                    "defect_count": dc.defect_count,
                    "defect_quantity": dc.defect_quantity,
                    "percentage_of_total": dc.percentage_of_total,
                    "cumulative_percentage": dc.cumulative_percentage,
                    "is_critical_to_quality": dc.is_critical_to_quality,
                    "root_cause_category": dc.root_cause_category,
                    "corrective_action_required": dc.corrective_action_required
                }
                for dc in defect_categories
            ]
        }
        
        return report_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/yield-reports", response_model=List[YieldAnalysisReportResponse])
def get_yield_reports(
    process_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get yield analysis reports for a process"""
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    
    from app.models.production import YieldAnalysisReport
    reports = (
        db.query(YieldAnalysisReport)
        .filter(YieldAnalysisReport.process_id == process_id)
        .order_by(YieldAnalysisReport.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Convert to response format with defect categories
    result = []
    for report in reports:
        from app.models.production import YieldDefectCategory
        defect_categories = (
            db.query(YieldDefectCategory)
            .filter(YieldDefectCategory.yield_report_id == report.id)
            .order_by(YieldDefectCategory.cumulative_percentage.asc())
            .all()
        )
        
        report_dict = {
            **report.__dict__,
            "defect_categories": [
                {
                    "id": dc.id,
                    "defect_type": dc.defect_type,
                    "defect_description": dc.defect_description,
                    "defect_count": dc.defect_count,
                    "percentage_of_total": dc.percentage_of_total,
                    "is_critical_to_quality": dc.is_critical_to_quality,
                    "root_cause_category": dc.root_cause_category
                }
                for dc in defect_categories
            ]
        }
        result.append(report_dict)
    
    return result


@router.get("/monitoring/alerts", response_model=List[ProcessMonitoringAlertResponse])
def get_monitoring_alerts(
    process_id: Optional[int] = Query(None),
    severity_level: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    food_safety_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get process monitoring alerts with filtering"""
    from app.models.production import ProcessMonitoringAlert
    
    query = db.query(ProcessMonitoringAlert)
    
    if process_id:
        query = query.filter(ProcessMonitoringAlert.process_id == process_id)
    if severity_level:
        query = query.filter(ProcessMonitoringAlert.severity_level == severity_level)
    if resolved is not None:
        query = query.filter(ProcessMonitoringAlert.resolved == resolved)
    if food_safety_only:
        query = query.filter(ProcessMonitoringAlert.food_safety_impact == True)
    
    alerts = (
        query.order_by(ProcessMonitoringAlert.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return alerts


@router.put("/monitoring/alerts/{alert_id}", response_model=ProcessMonitoringAlertResponse)
def update_monitoring_alert(
    alert_id: int,
    payload: ProcessMonitoringAlertUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Update monitoring alert (acknowledge, resolve, assign)"""
    from app.models.production import ProcessMonitoringAlert
    from datetime import datetime
    
    alert = db.query(ProcessMonitoringAlert).filter(ProcessMonitoringAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    user_id = getattr(current_user, "id", None)
    
    # Update fields
    if payload.assigned_to is not None:
        alert.assigned_to = payload.assigned_to
    
    if payload.acknowledged is not None and payload.acknowledged and not alert.acknowledged:
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
    
    if payload.resolved is not None and payload.resolved and not alert.resolved:
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = user_id
        alert.resolution_notes = payload.resolution_notes
    
    if payload.escalation_level is not None:
        alert.escalation_level = payload.escalation_level
    
    alert.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    try:
        from app.services import log_audit_event
        log_audit_event(
            db,
            user_id=user_id,
            action="monitoring_alert.updated",
            resource_type="production_process",
            resource_id=str(alert.process_id),
            details={"alert_id": alert_id, "updates": payload.model_dump(exclude_unset=True)}
        )
    except Exception:
        pass
    
    return alert


@router.get("/monitoring/analytics", response_model=ProcessMonitoringAnalytics)
def get_monitoring_analytics(
    process_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get comprehensive process monitoring analytics dashboard"""
    service = ProductionService(db)
    
    pt = None
    if process_type:
        try:
            pt = ProductProcessType(process_type)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid process_type: {process_type}")
    
    analytics = service.get_process_monitoring_analytics(pt)
    return analytics


@router.post("/monitoring/dashboards", response_model=ProcessMonitoringDashboardResponse)
def create_monitoring_dashboard(
    payload: ProcessMonitoringDashboardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Create a custom monitoring dashboard configuration"""
    from app.models.production import ProcessMonitoringDashboard
    
    user_id = getattr(current_user, "id", None)
    
    dashboard = ProcessMonitoringDashboard(
        dashboard_name=payload.dashboard_name,
        process_type=ProductProcessType(payload.process_type) if payload.process_type else None,
        user_id=user_id,
        is_public=payload.is_public,
        dashboard_config=payload.dashboard_config,
        refresh_interval_seconds=payload.refresh_interval_seconds,
        alert_thresholds=payload.alert_thresholds,
    )
    
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    try:
        from app.services import log_audit_event
        log_audit_event(
            db,
            user_id=user_id,
            action="monitoring_dashboard.created",
            resource_type="monitoring_dashboard",
            resource_id=str(dashboard.id),
            details={"dashboard_name": dashboard.dashboard_name}
        )
    except Exception:
        pass
    
    return dashboard


@router.get("/monitoring/dashboards", response_model=List[ProcessMonitoringDashboardResponse])
def get_monitoring_dashboards(
    process_type: Optional[str] = Query(None),
    public_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get monitoring dashboard configurations"""
    from app.models.production import ProcessMonitoringDashboard
    
    user_id = getattr(current_user, "id", None)
    
    query = db.query(ProcessMonitoringDashboard).filter(ProcessMonitoringDashboard.is_active == True)
    
    if process_type:
        try:
            pt = ProductProcessType(process_type)
            query = query.filter(ProcessMonitoringDashboard.process_type == pt)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid process_type: {process_type}")
    
    if public_only:
        query = query.filter(ProcessMonitoringDashboard.is_public == True)
    else:
        # Show public dashboards + user's own dashboards
        query = query.filter(
            or_(
                ProcessMonitoringDashboard.is_public == True,
                ProcessMonitoringDashboard.user_id == user_id
            )
        )
    
    dashboards = query.order_by(ProcessMonitoringDashboard.created_at.desc()).all()
    return dashboards


@router.get("/monitoring/real-time/{process_id}")
def get_real_time_monitoring_data(
    process_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Get real-time monitoring data for a process - WebSocket alternative"""
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    
    from datetime import datetime, timedelta
    from app.models.production import (
        ProcessParameter, ProcessControlPoint, ProcessMonitoringAlert,
        ProcessControlChart
    )
    
    # Get recent parameters (last hour)
    recent_cutoff = datetime.utcnow() - timedelta(hours=1)
    
    recent_parameters = (
        db.query(ProcessParameter)
        .filter(
            ProcessParameter.process_id == process_id,
            ProcessParameter.recorded_at >= recent_cutoff
        )
        .order_by(ProcessParameter.recorded_at.desc())
        .limit(100)
        .all()
    )
    
    # Get active alerts
    active_alerts = (
        db.query(ProcessMonitoringAlert)
        .filter(
            ProcessMonitoringAlert.process_id == process_id,
            ProcessMonitoringAlert.resolved == False
        )
        .order_by(ProcessMonitoringAlert.created_at.desc())
        .limit(10)
        .all()
    )
    
    # Get control chart status
    control_charts = (
        db.query(ProcessControlChart)
        .filter(
            ProcessControlChart.process_id == process_id,
            ProcessControlChart.is_active == True
        )
        .all()
    )
    
    chart_status = []
    for chart in control_charts:
        latest_point = (
            db.query(ProcessControlPoint)
            .filter(ProcessControlPoint.control_chart_id == chart.id)
            .order_by(ProcessControlPoint.timestamp.desc())
            .first()
        )
        
        chart_status.append({
            "chart_id": chart.id,
            "parameter_name": chart.parameter_name,
            "chart_type": chart.chart_type,
            "latest_value": latest_point.measured_value if latest_point else None,
            "latest_timestamp": latest_point.timestamp if latest_point else None,
            "is_out_of_control": latest_point.is_out_of_control if latest_point else False,
            "target_value": chart.target_value,
            "upper_control_limit": chart.upper_control_limit,
            "lower_control_limit": chart.lower_control_limit
        })
    
    return {
        "process_id": process_id,
        "process_status": proc.status.value if hasattr(proc.status, 'value') else str(proc.status),
        "timestamp": datetime.utcnow(),
        "recent_parameters": [
            {
                "id": p.id,
                "parameter_name": p.parameter_name,
                "parameter_value": p.parameter_value,
                "unit": p.unit,
                "recorded_at": p.recorded_at,
                "is_within_tolerance": p.is_within_tolerance
            }
            for p in recent_parameters
        ],
        "active_alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity_level": a.severity_level,
                "alert_title": a.alert_title,
                "created_at": a.created_at,
                "food_safety_impact": a.food_safety_impact,
                "requires_immediate_action": a.requires_immediate_action
            }
            for a in active_alerts
        ],
        "control_chart_status": chart_status,
        "summary": {
            "total_parameters_last_hour": len(recent_parameters),
            "out_of_tolerance_count": sum(1 for p in recent_parameters if p.is_within_tolerance is False),
            "active_alert_count": len(active_alerts),
            "critical_alert_count": sum(1 for a in active_alerts if a.severity_level == "critical"),
            "control_charts_out_of_control": sum(1 for cs in chart_status if cs["is_out_of_control"])
        }
    }


# =================== FSM (Finite State Machine) Endpoints ===================

@router.post("/processes/fsm", response_model=ProcessResponse)
def create_process_with_stages(
    payload: ProcessCreateWithStages, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Create a new production process with stages for FSM management"""
    service = ProductionService(db)
    try:
        from app.models.production import ProductProcessType
        
        # Convert stages data
        stages_data = [stage.model_dump() for stage in payload.stages]
        
        # Create process with stages
        process = service.create_process_with_stages(
            batch_id=payload.batch_id,
            process_type=ProductProcessType(payload.process_type),
            operator_id=payload.operator_id,
            spec=payload.spec,
            stages_data=stages_data,
            notes=payload.notes
        )
        
        # Return process with stages
        process_dict = {
            "id": process.id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value,
            "operator_id": process.operator_id,
            "status": process.status.value,
            "start_time": process.start_time,
            "end_time": process.end_time,
            "spec": process.spec,
            "notes": process.notes,
            "created_at": process.created_at,
            "updated_at": process.updated_at,
            "stages": [
                {
                    "id": stage.id,
                    "process_id": stage.process_id,
                    "stage_name": stage.stage_name,
                    "stage_description": stage.stage_description,
                    "sequence_order": stage.sequence_order,
                    "status": stage.status.value,
                    "is_critical_control_point": stage.is_critical_control_point,
                    "is_operational_prp": stage.is_operational_prp,
                    "planned_start_time": stage.planned_start_time,
                    "actual_start_time": stage.actual_start_time,
                    "planned_end_time": stage.planned_end_time,
                    "actual_end_time": stage.actual_end_time,
                    "duration_minutes": stage.duration_minutes,
                    "completion_criteria": stage.completion_criteria,
                    "auto_advance": stage.auto_advance,
                    "requires_approval": stage.requires_approval,
                    "assigned_operator_id": stage.assigned_operator_id,
                    "completed_by_id": stage.completed_by_id,
                    "approved_by_id": stage.approved_by_id,
                    "stage_notes": stage.stage_notes,
                    "deviations_recorded": stage.deviations_recorded,
                    "corrective_actions": stage.corrective_actions,
                    "created_at": stage.created_at,
                    "updated_at": stage.updated_at
                } for stage in process.stages
            ],
            "current_stage_id": next((s.id for s in process.stages if s.status.value == "in_progress"), None)
        }
        
        return ProcessResponse(**process_dict)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/start", response_model=ProcessResponse)
def start_process(
    process_id: int, 
    payload: ProcessStartRequest,
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Start a process and activate the first stage"""
    service = ProductionService(db)
    try:
        process = service.start_process(
            process_id=process_id,
            operator_id=payload.operator_id,
            start_notes=payload.start_notes
        )
        
        # Convert to response format
        process_dict = {
            "id": process.id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value,
            "operator_id": process.operator_id,
            "status": process.status.value,
            "start_time": process.start_time,
            "end_time": process.end_time,
            "spec": process.spec,
            "notes": process.notes,
            "created_at": process.created_at,
            "updated_at": process.updated_at,
            "stages": [
                {
                    "id": stage.id,
                    "process_id": stage.process_id,
                    "stage_name": stage.stage_name,
                    "stage_description": stage.stage_description,
                    "sequence_order": stage.sequence_order,
                    "status": stage.status.value,
                    "is_critical_control_point": stage.is_critical_control_point,
                    "is_operational_prp": stage.is_operational_prp,
                    "planned_start_time": stage.planned_start_time,
                    "actual_start_time": stage.actual_start_time,
                    "planned_end_time": stage.planned_end_time,
                    "actual_end_time": stage.actual_end_time,
                    "duration_minutes": stage.duration_minutes,
                    "completion_criteria": stage.completion_criteria,
                    "auto_advance": stage.auto_advance,
                    "requires_approval": stage.requires_approval,
                    "assigned_operator_id": stage.assigned_operator_id,
                    "completed_by_id": stage.completed_by_id,
                    "approved_by_id": stage.approved_by_id,
                    "stage_notes": stage.stage_notes,
                    "deviations_recorded": stage.deviations_recorded,
                    "corrective_actions": stage.corrective_actions,
                    "created_at": stage.created_at,
                    "updated_at": stage.updated_at
                } for stage in process.stages
            ],
            "current_stage_id": next((s.id for s in process.stages if s.status.value == "in_progress"), None)
        }
        
        return ProcessResponse(**process_dict)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/stages/{stage_id}/complete")
def complete_stage_and_transition(
    process_id: int, 
    stage_id: int,
    payload: ProcessStageCompletionRequest,
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Complete current stage and transition to next stage"""
    service = ProductionService(db)
    try:
        # Prepare transition data
        transition_data = {
            "deviations_recorded": payload.deviations_recorded,
            "corrective_actions": payload.corrective_actions,
            "transition_notes": payload.completion_notes,
            "assign_operator_to_next": True,
            "transition_type": "normal",
            "prerequisites_met": True
        }
        
        # Get current user ID (assuming it's available from the dependency)
        user_id = getattr(current_user, 'id', 1)  # Fallback to 1 if not available
        
        result = service.transition_to_next_stage(
            process_id=process_id,
            current_stage_id=stage_id,
            user_id=user_id,
            transition_data=transition_data
        )
        
        return {
            "success": True,
            "message": "Stage completed successfully" if not result["process_completed"] else "Process completed successfully",
            "completed_stage_id": result["completed_stage"].id,
            "next_stage_id": result["next_stage"].id if result["next_stage"] else None,
            "process_completed": result["process_completed"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/fsm", response_model=ProcessResponse)
def get_process_with_stages(
    process_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:read"))
):
    """Get a process with all its stages and monitoring data"""
    service = ProductionService(db)
    try:
        process = service.get_process_with_stages(process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        
        # Convert to response format
        process_dict = {
            "id": process.id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value,
            "operator_id": process.operator_id,
            "status": process.status.value,
            "start_time": process.start_time,
            "end_time": process.end_time,
            "spec": process.spec,
            "notes": process.notes,
            "created_at": process.created_at,
            "updated_at": process.updated_at,
            "stages": [
                {
                    "id": stage.id,
                    "process_id": stage.process_id,
                    "stage_name": stage.stage_name,
                    "stage_description": stage.stage_description,
                    "sequence_order": stage.sequence_order,
                    "status": stage.status.value,
                    "is_critical_control_point": stage.is_critical_control_point,
                    "is_operational_prp": stage.is_operational_prp,
                    "planned_start_time": stage.planned_start_time,
                    "actual_start_time": stage.actual_start_time,
                    "planned_end_time": stage.planned_end_time,
                    "actual_end_time": stage.actual_end_time,
                    "duration_minutes": stage.duration_minutes,
                    "completion_criteria": stage.completion_criteria,
                    "auto_advance": stage.auto_advance,
                    "requires_approval": stage.requires_approval,
                    "assigned_operator_id": stage.assigned_operator_id,
                    "completed_by_id": stage.completed_by_id,
                    "approved_by_id": stage.approved_by_id,
                    "stage_notes": stage.stage_notes,
                    "deviations_recorded": stage.deviations_recorded,
                    "corrective_actions": stage.corrective_actions,
                    "created_at": stage.created_at,
                    "updated_at": stage.updated_at
                } for stage in process.stages
            ],
            "current_stage_id": next((s.id for s in process.stages if s.status.value == "in_progress"), None)
        }
        
        return ProcessResponse(**process_dict)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/summary", response_model=ProcessSummaryResponse)
def get_process_summary(
    process_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:read"))
):
    """Get a summary of the process including progress and quality metrics"""
    service = ProductionService(db)
    try:
        summary = service.get_process_summary(process_id)
        return ProcessSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stages/{stage_id}/monitoring-requirements", response_model=StageMonitoringRequirementResponse)
def add_stage_monitoring_requirement(
    stage_id: int, 
    payload: StageMonitoringRequirementCreate,
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Add a monitoring requirement to a stage"""
    service = ProductionService(db)
    try:
        # Get current user ID
        user_id = getattr(current_user, 'id', 1)
        
        requirement = service.add_stage_monitoring_requirement(
            stage_id=stage_id,
            requirement_data=payload.model_dump(),
            created_by=user_id
        )
        
        # Convert to response format
        requirement_dict = {
            "id": requirement.id,
            "stage_id": requirement.stage_id,
            "requirement_name": requirement.requirement_name,
            "requirement_type": requirement.requirement_type.value,
            "description": requirement.description,
            "is_critical_limit": requirement.is_critical_limit,
            "is_operational_limit": requirement.is_operational_limit,
            "target_value": requirement.target_value,
            "tolerance_min": requirement.tolerance_min,
            "tolerance_max": requirement.tolerance_max,
            "unit_of_measure": requirement.unit_of_measure,
            "monitoring_frequency": requirement.monitoring_frequency,
            "is_mandatory": requirement.is_mandatory,
            "equipment_required": requirement.equipment_required,
            "measurement_method": requirement.measurement_method,
            "calibration_required": requirement.calibration_required,
            "record_keeping_required": requirement.record_keeping_required,
            "verification_required": requirement.verification_required,
            "regulatory_reference": requirement.regulatory_reference,
            "created_at": requirement.created_at,
            "created_by": requirement.created_by
        }
        
        return StageMonitoringRequirementResponse(**requirement_dict)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stages/{stage_id}/monitoring-logs", response_model=StageMonitoringLogResponse)
def log_stage_monitoring(
    stage_id: int, 
    payload: StageMonitoringLogCreate,
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:update"))
):
    """Log monitoring data for a stage"""
    service = ProductionService(db)
    try:
        # Get current user ID
        user_id = getattr(current_user, 'id', 1)
        
        log = service.log_stage_monitoring(
            stage_id=stage_id,
            monitoring_data=payload.model_dump(),
            recorded_by=user_id
        )
        
        # Convert to response format
        log_dict = {
            "id": log.id,
            "stage_id": log.stage_id,
            "requirement_id": log.requirement_id,
            "monitoring_timestamp": log.monitoring_timestamp,
            "measured_value": log.measured_value,
            "measured_text": log.measured_text,
            "is_within_limits": log.is_within_limits,
            "pass_fail_status": log.pass_fail_status,
            "deviation_severity": log.deviation_severity,
            "recorded_by": log.recorded_by,
            "verified_by": log.verified_by,
            "verification_timestamp": log.verification_timestamp,
            "equipment_used": log.equipment_used,
            "measurement_method": log.measurement_method,
            "equipment_calibration_date": log.equipment_calibration_date,
            "notes": log.notes,
            "corrective_action_taken": log.corrective_action_taken,
            "follow_up_required": log.follow_up_required,
            "regulatory_requirement_met": log.regulatory_requirement_met,
            "iso_clause_reference": log.iso_clause_reference,
            "created_at": log.created_at,
            "updated_at": log.updated_at
        }
        
        return StageMonitoringLogResponse(**log_dict)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stages/{stage_id}/monitoring-logs", response_model=List[StageMonitoringLogResponse])
def get_stage_monitoring_logs(
    stage_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:read"))
):
    """Get all monitoring logs for a stage"""
    service = ProductionService(db)
    try:
        logs = service.get_stage_monitoring_logs(stage_id)
        
        # Convert to response format
        logs_dict = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "stage_id": log.stage_id,
                "requirement_id": log.requirement_id,
                "monitoring_timestamp": log.monitoring_timestamp,
                "measured_value": log.measured_value,
                "measured_text": log.measured_text,
                "is_within_limits": log.is_within_limits,
                "pass_fail_status": log.pass_fail_status,
                "deviation_severity": log.deviation_severity,
                "recorded_by": log.recorded_by,
                "verified_by": log.verified_by,
                "verification_timestamp": log.verification_timestamp,
                "equipment_used": log.equipment_used,
                "measurement_method": log.measurement_method,
                "equipment_calibration_date": log.equipment_calibration_date,
                "notes": log.notes,
                "corrective_action_taken": log.corrective_action_taken,
                "follow_up_required": log.follow_up_required,
                "regulatory_requirement_met": log.regulatory_requirement_met,
                "iso_clause_reference": log.iso_clause_reference,
                "created_at": log.created_at,
                "updated_at": log.updated_at
            }
            logs_dict.append(log_dict)
        
        return [StageMonitoringLogResponse(**log_dict) for log_dict in logs_dict]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates/stages/{product_type}")
def get_iso_stage_template(
    product_type: str,
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:read"))
):
    """Get ISO 22000:2018 compliant stage template for a product type"""
    try:
        from app.utils.iso_stage_templates import ISO22000StageTemplates
        
        # Validate product type
        valid_types = ["fresh_milk", "pasteurized_milk", "yoghurt", "cheese", "mala", "fermented_products"]
        if product_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid product type. Valid types: {', '.join(valid_types)}"
            )
        
        # Get stage template
        stages = ISO22000StageTemplates.get_template_by_product_type(product_type)
        
        # Add monitoring requirements for each stage
        for stage in stages:
            stage["monitoring_requirements"] = ISO22000StageTemplates.get_monitoring_requirements_for_stage(
                stage["stage_name"], 
                stage.get("is_critical_control_point", False)
            )
        
        # Validate ISO compliance
        validation = ISO22000StageTemplates.validate_iso_compliance(stages)
        
        return {
            "product_type": product_type,
            "stages": stages,
            "iso_compliance": validation,
            "total_stages": len(stages),
            "ccps_count": sum(1 for s in stages if s.get("is_critical_control_point", False)),
            "oprps_count": sum(1 for s in stages if s.get("is_operational_prp", False)),
            "estimated_total_duration_hours": round(sum(s.get("duration_minutes", 0) for s in stages) / 60, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/fsm/from-template")
def create_process_from_iso_template(
    payload: Dict[str, Any],
    db: Session = Depends(get_db), 
    current_user = Depends(require_permission_dependency("traceability:create"))
):
    """Create a new process using an ISO 22000:2018 compliant template"""
    try:
        from app.utils.iso_stage_templates import ISO22000StageTemplates
        from app.models.production import ProductProcessType
        
        batch_id = payload.get("batch_id")
        product_type = payload.get("process_type")
        operator_id = payload.get("operator_id")
        
        if not batch_id or not product_type:
            raise HTTPException(status_code=400, detail="batch_id and process_type are required")
        
        # Get template stages
        template_stages = ISO22000StageTemplates.get_template_by_product_type(product_type)
        if not template_stages:
            raise HTTPException(status_code=400, detail=f"No template available for product type: {product_type}")
        
        # Validate ISO compliance
        validation = ISO22000StageTemplates.validate_iso_compliance(template_stages)
        if not validation["is_compliant"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Template validation failed: {'; '.join(validation['errors'])}"
            )
        
        # Create process with template stages
        service = ProductionService(db)
        process = service.create_process_with_stages(
            batch_id=batch_id,
            process_type=ProductProcessType(product_type),
            operator_id=operator_id,
            spec=payload.get("spec", {}),
            stages_data=template_stages,
            notes=f"Created from ISO 22000:2018 template for {product_type}. Template validation: {validation['is_compliant']}"
        )
        
        # Add monitoring requirements for each stage
        for stage in process.stages:
            stage_name = stage.stage_name
            is_ccp = stage.is_critical_control_point
            
            monitoring_requirements = ISO22000StageTemplates.get_monitoring_requirements_for_stage(stage_name, is_ccp)
            
            for req_data in monitoring_requirements:
                service.add_stage_monitoring_requirement(
                    stage_id=stage.id,
                    requirement_data=req_data,
                    created_by=getattr(current_user, 'id', 1)
                )
        
        # Convert to response format
        process_dict = {
            "id": process.id,
            "batch_id": process.batch_id,
            "process_type": process.process_type.value,
            "operator_id": process.operator_id,
            "status": process.status.value,
            "start_time": process.start_time,
            "end_time": process.end_time,
            "spec": process.spec,
            "notes": process.notes,
            "created_at": process.created_at,
            "updated_at": process.updated_at,
            "stages": [
                {
                    "id": stage.id,
                    "process_id": stage.process_id,
                    "stage_name": stage.stage_name,
                    "stage_description": stage.stage_description,
                    "sequence_order": stage.sequence_order,
                    "status": stage.status.value,
                    "is_critical_control_point": stage.is_critical_control_point,
                    "is_operational_prp": stage.is_operational_prp,
                    "planned_start_time": stage.planned_start_time,
                    "actual_start_time": stage.actual_start_time,
                    "planned_end_time": stage.planned_end_time,
                    "actual_end_time": stage.actual_end_time,
                    "duration_minutes": stage.duration_minutes,
                    "completion_criteria": stage.completion_criteria,
                    "auto_advance": stage.auto_advance,
                    "requires_approval": stage.requires_approval,
                    "assigned_operator_id": stage.assigned_operator_id,
                    "completed_by_id": stage.completed_by_id,
                    "approved_by_id": stage.approved_by_id,
                    "stage_notes": stage.stage_notes,
                    "deviations_recorded": stage.deviations_recorded,
                    "corrective_actions": stage.corrective_actions,
                    "created_at": stage.created_at,
                    "updated_at": stage.updated_at
                } for stage in process.stages
            ],
            "current_stage_id": None,  # Process is in DRAFT status
            "template_info": {
                "template_used": product_type,
                "iso_compliant": validation["is_compliant"],
                "ccps_count": sum(1 for s in process.stages if s.is_critical_control_point),
                "oprps_count": sum(1 for s in process.stages if s.is_operational_prp)
            }
        }
        
        return ProcessResponse(**process_dict)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/processes/{process_id}/transitions")
def list_stage_transitions(
    process_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """List stage transitions for a production process (for divert/rework verification)."""
    from app.models.production import StageTransition
    from app.services.production_service import ProductionService
    svc = ProductionService(db)
    proc = svc.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    transitions = (
        db.query(StageTransition)
        .filter(StageTransition.process_id == process_id)
        .order_by(StageTransition.transition_timestamp.asc())
        .all()
    )
    return [
        {
            "id": t.id,
            "from_stage_id": t.from_stage_id,
            "to_stage_id": t.to_stage_id,
            "transition_type": t.transition_type,
            "auto_transition": t.auto_transition,
            "reason": t.transition_reason,
            "initiated_by": t.initiated_by,
            "timestamp": t.transition_timestamp,
            "requires_approval": t.requires_approval,
            "approved_by": t.approved_by,
            "transition_notes": t.transition_notes,
        }
        for t in transitions
    ]

@router.get("/processes/{process_id}/audit-simple")
def get_process_audit_simple(
    process_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission_dependency("traceability:view"))
):
    """Simple audit bundle: stage transitions and divert logs."""
    from app.models.production import ProcessLog, LogEvent
    from app.services.production_service import ProductionService
    svc = ProductionService(db)
    proc = svc.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    # Transitions
    transitions = list_stage_transitions(process_id, db, current_user)
    # Divert logs
    diverts = (
        db.query(ProcessLog)
        .filter(ProcessLog.process_id == process_id, ProcessLog.event == LogEvent.DIVERT)
        .order_by(ProcessLog.timestamp.asc())
        .all()
    )
    return {
        "process_id": process_id,
        "transitions": transitions,
        "diverts": [
            {
                "id": d.id,
                "timestamp": d.timestamp,
                "measured_temp_c": d.measured_temp_c,
                "note": d.note,
                "auto_flag": d.auto_flag,
            }
            for d in diverts
        ],
    }

