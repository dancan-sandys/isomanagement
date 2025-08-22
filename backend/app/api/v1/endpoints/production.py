from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
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
    ProcessAlertResponse, ProcessTemplateResponse, ProductionAnalytics
)
from app.schemas.production import ProcessSpecBindRequest, ReleaseCheckResponse, ReleaseRequest, ReleaseResponse
from app.models.production import ProductProcessType, ProcessStatus
from app.core.security import get_current_active_user
from app.core.permissions import require_permission_dependency

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


@router.get("/{process_id}")
def get_process(process_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:view"))):
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    return proc

# Enhanced Production Endpoints
@router.post("/processes", response_model=ProcessResponse)
def create_process_enhanced(payload: ProcessCreateEnhanced, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("traceability:create"))):
    """Create a new production process with enhanced features"""
    service = ProductionService(db)
    try:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    pt = ProductProcessType(process_type) if process_type else None
    st = ProcessStatus(status) if status else None
    return service.list_processes(pt, st, limit, offset)


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
        return updated
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
    return response


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
    c.showPage(); c.save(); buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=production_sheet_{process_id}.pdf"})

