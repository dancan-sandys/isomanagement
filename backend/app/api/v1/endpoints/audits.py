from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import os
import shutil

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit_mgmt import (
    Audit as AuditModel, AuditStatus, AuditType,
    AuditChecklistTemplate, AuditChecklistItem, ChecklistResponse,
    AuditFinding, FindingSeverity, FindingStatus,
    AuditAttachment, AuditItemAttachment, AuditFindingAttachment, AuditAuditee,
)
from app.schemas.audit import (
    AuditCreate, AuditUpdate, AuditResponse, AuditListResponse,
    ChecklistTemplateCreate, ChecklistTemplateResponse,
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse,
    FindingCreate, FindingUpdate, FindingResponse,
    AuditItemAttachmentResponse, AuditFindingAttachmentResponse,
    AuditStatsResponse, AuditeeResponse,
)
from app.utils.audit import audit_event
from app.schemas.nonconformance import NonConformanceCreate, NonConformanceResponse
from app.models.nonconformance import NonConformance as NCModel, NonConformanceSource, NonConformanceStatus
from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter()


@router.get("/", response_model=AuditListResponse)
async def list_audits(
    search: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(AuditModel)
    if audit_type:
        q = q.filter(AuditModel.audit_type == AuditType(audit_type))
    if status:
        q = q.filter(AuditModel.status == AuditStatus(status))
    if search:
        like = f"%{search}%"
        q = q.filter(AuditModel.title.ilike(like))
    total = q.count()
    items = q.order_by(AuditModel.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return AuditListResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.post("/", response_model=AuditResponse)
async def create_audit(
    payload: AuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    audit = AuditModel(
        title=payload.title,
        audit_type=AuditType(payload.audit_type),
        scope=payload.scope,
        objectives=payload.objectives,
        criteria=payload.criteria,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=AuditStatus(payload.status or "planned"),
        auditor_id=payload.auditor_id,
        lead_auditor_id=payload.lead_auditor_id,
        auditee_department=payload.auditee_department,
        created_by=current_user.id,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    try:
        audit_event(db, current_user.id, "audit_created", "audits", str(audit.id))
    except Exception:
        pass
    return audit


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.put("/{audit_id}", response_model=AuditResponse)
async def update_audit(audit_id: int, payload: AuditUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {"audit_type", "status"} and value is not None:
            value = (AuditType(value) if field == "audit_type" else AuditStatus(value))
        setattr(audit, field, value)
    db.commit()
    db.refresh(audit)
    try:
        audit_event(db, current_user.id, "audit_updated", "audits", str(audit.id))
    except Exception:
        pass
    return audit


@router.delete("/{audit_id}")
async def delete_audit(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    db.delete(audit)
    db.commit()
    try:
        audit_event(db, current_user.id, "audit_deleted", "audits", str(audit_id))
    except Exception:
        pass
    return {"message": "Audit deleted"}


# Checklist template endpoints
@router.post("/templates", response_model=ChecklistTemplateResponse)
async def create_template(payload: ChecklistTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = AuditChecklistTemplate(
        name=payload.name,
        clause_ref=payload.clause_ref,
        question=payload.question,
        requirement=payload.requirement,
        category=payload.category,
        is_active=payload.is_active if payload.is_active is not None else True,
        created_by=current_user.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=List[ChecklistTemplateResponse])
async def list_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(AuditChecklistTemplate).filter(AuditChecklistTemplate.is_active == True).order_by(AuditChecklistTemplate.created_at.desc()).all()


# Checklist items
@router.get("/{audit_id}/checklist", response_model=List[ChecklistItemResponse])
async def list_checklist_items(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    items = db.query(AuditChecklistItem).filter(AuditChecklistItem.audit_id == audit_id).order_by(AuditChecklistItem.created_at.asc()).all()
    return items
@router.post("/{audit_id}/checklist", response_model=ChecklistItemResponse)
async def add_checklist_item(audit_id: int, payload: ChecklistItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    item = AuditChecklistItem(
        audit_id=audit_id,
        template_id=payload.template_id,
        clause_ref=payload.clause_ref,
        question=payload.question,
        response=ChecklistResponse(payload.response) if payload.response else None,
        evidence_text=payload.evidence_text,
        responsible_person_id=payload.responsible_person_id,
        due_date=payload.due_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/checklist/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(item_id: int, payload: ChecklistItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(AuditChecklistItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "response" and value is not None:
            value = ChecklistResponse(value)
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


# Findings
@router.get("/{audit_id}/findings", response_model=List[FindingResponse])
async def list_findings(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    f = db.query(AuditFinding).filter(AuditFinding.audit_id == audit_id).order_by(AuditFinding.created_at.asc()).all()
    return f
@router.post("/{audit_id}/findings", response_model=FindingResponse)
async def add_finding(audit_id: int, payload: FindingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    finding = AuditFinding(
        audit_id=audit_id,
        clause_ref=payload.clause_ref,
        description=payload.description,
        severity=FindingSeverity(payload.severity),
        corrective_action=payload.corrective_action,
        responsible_person_id=payload.responsible_person_id,
        target_completion_date=payload.target_completion_date,
        status=FindingStatus(payload.status or "open"),
        related_nc_id=payload.related_nc_id,
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


@router.put("/findings/{finding_id}", response_model=FindingResponse)
async def update_finding(finding_id: int, payload: FindingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    finding = db.query(AuditFinding).get(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "severity" and value is not None:
            value = FindingSeverity(value)
        if field == "status" and value is not None:
            value = FindingStatus(value)
        setattr(finding, field, value)
    db.commit()
    db.refresh(finding)
    return finding


# Attachments
@router.post("/{audit_id}/attachments", response_model=dict)
async def upload_attachment(audit_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    upload_dir = "uploads/audits"
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = f"audit_{audit_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    attachment = AuditAttachment(
        audit_id=audit_id,
        file_path=file_path,
        filename=file.filename,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    try:
        audit_event(db, current_user.id, "audit_attachment_uploaded", "audits", str(audit_id))
    except Exception:
        pass
    return {"file_path": file_path}


# Upload attachment for a checklist item
@router.post("/checklist/{item_id}/attachments", response_model=AuditItemAttachmentResponse)
async def upload_item_attachment(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(AuditChecklistItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    upload_dir = "uploads/audits/items"
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = f"item_{item_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    attachment = AuditItemAttachment(
        item_id=item_id,
        file_path=file_path,
        filename=file.filename,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    try:
        audit_event(db, current_user.id, "audit_item_attachment_uploaded", "audits", str(item.audit_id))
    except Exception:
        pass
    return attachment


# Upload attachment for a finding
@router.post("/findings/{finding_id}/attachments", response_model=AuditFindingAttachmentResponse)
async def upload_finding_attachment(
    finding_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(AuditFinding).get(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    upload_dir = "uploads/audits/findings"
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = f"finding_{finding_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    attachment = AuditFindingAttachment(
        finding_id=finding_id,
        file_path=file_path,
        filename=file.filename,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    try:
        audit_event(db, current_user.id, "audit_finding_attachment_uploaded", "audits", str(finding.audit_id))
    except Exception:
        pass
    return attachment


# List/download/delete attachments for checklist item
@router.get("/checklist/{item_id}/attachments", response_model=List[AuditItemAttachmentResponse])
async def list_item_attachments(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(AuditChecklistItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return db.query(AuditItemAttachment).filter(AuditItemAttachment.item_id == item_id).order_by(AuditItemAttachment.uploaded_at.desc()).all()


@router.get("/checklist/attachments/{attachment_id}/download")
async def download_item_attachment(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    att = db.query(AuditItemAttachment).get(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return FileResponse(att.file_path, filename=att.filename)


@router.delete("/checklist/attachments/{attachment_id}")
async def delete_item_attachment(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    att = db.query(AuditItemAttachment).get(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    db.delete(att)
    db.commit()
    return {"message": "Attachment deleted"}


# List/download/delete attachments for finding
@router.get("/findings/{finding_id}/attachments", response_model=List[AuditFindingAttachmentResponse])
async def list_finding_attachments(finding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    f = db.query(AuditFinding).get(finding_id)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    return db.query(AuditFindingAttachment).filter(AuditFindingAttachment.finding_id == finding_id).order_by(AuditFindingAttachment.uploaded_at.desc()).all()


@router.get("/findings/attachments/{attachment_id}/download")
async def download_finding_attachment(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    att = db.query(AuditFindingAttachment).get(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return FileResponse(att.file_path, filename=att.filename)


@router.delete("/findings/attachments/{attachment_id}")
async def delete_finding_attachment(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    att = db.query(AuditFindingAttachment).get(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    db.delete(att)
    db.commit()
    return {"message": "Attachment deleted"}


# Create Non-Conformance from a finding
@router.post("/findings/{finding_id}/create-nc", response_model=NonConformanceResponse)
async def create_nc_from_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(AuditFinding).get(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Build NC data from finding
    nc_payload = NonConformanceCreate(
        title=f"Audit Finding NC - {finding.clause_ref or 'No Clause'}",
        description=finding.description,
        source=NonConformanceSource.AUDIT,
        severity=finding.severity.value if hasattr(finding.severity, 'value') else str(finding.severity),
        impact_area="food safety",
        category="audit",
        target_resolution_date=finding.target_completion_date,
    )

    # Create NC
    nc = NCModel(
        nc_number=f"NC-{int(datetime.utcnow().timestamp())}",
        title=nc_payload.title,
        description=nc_payload.description,
        source=NonConformanceSource.AUDIT,
        batch_reference=None,
        product_reference=None,
        process_reference=None,
        location=None,
        severity=nc_payload.severity,
        impact_area=nc_payload.impact_area,
        category=nc_payload.category,
        status=NonConformanceStatus.OPEN,
        reported_date=datetime.utcnow(),
        target_resolution_date=nc_payload.target_resolution_date,
        reported_by=current_user.id,
    )
    db.add(nc)
    db.commit()
    db.refresh(nc)

    # Link NC back to finding
    finding.related_nc_id = nc.id
    db.commit()

    try:
        audit_event(db, current_user.id, "nc_created_from_finding", "audits", str(finding.audit_id), {"nc_id": nc.id, "finding_id": finding_id})
    except Exception:
        pass

    return nc


# Stats endpoint
@router.get("/stats", response_model=AuditStatsResponse)
async def get_audit_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(AuditModel)
    total = q.count()
    by_status = {s.value: db.query(AuditModel).filter(AuditModel.status == s).count() for s in AuditStatus}
    by_type = {t.value: db.query(AuditModel).filter(AuditModel.audit_type == t).count() for t in AuditType}
    recent = (
        db.query(AuditModel.id, AuditModel.title, AuditModel.created_at)
        .order_by(AuditModel.created_at.desc())
        .limit(10)
        .all()
    )
    recent_created = [
        {"id": str(r.id), "title": r.title, "created_at": r.created_at.isoformat() if r.created_at else ""}
        for r in recent
    ]
    return AuditStatsResponse(total=total, by_status=by_status, by_type=by_type, recent_created=recent_created)


# Export list to PDF or XLSX
@router.post("/export")
async def export_audits(
    format: str = Query("pdf", pattern="^(pdf|xlsx)$"),
    search: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(AuditModel)
    if audit_type:
        q = q.filter(AuditModel.audit_type == AuditType(audit_type))
    if status:
        q = q.filter(AuditModel.status == AuditStatus(status))
    if search:
        like = f"%{search}%"
        q = q.filter(AuditModel.title.ilike(like))
    items = q.order_by(AuditModel.created_at.desc()).all()

    if format == "xlsx":
        wb = Workbook(); ws = wb.active; ws.title = "Audits"
        ws.append(["ID", "Title", "Type", "Status", "Start", "End", "Lead Auditor", "Auditee Dept"]) 
        for a in items:
            ws.append([a.id, a.title, a.audit_type.value, a.status.value, str(a.start_date or ''), str(a.end_date or ''), a.lead_auditor_id or '', a.auditee_department or ''])
        buf = BytesIO(); wb.save(buf); buf.seek(0)
        headers = {"Content-Disposition": "attachment; filename=audits.xlsx"}
        return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
    else:
        buf = BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
        x, y = 40, 800
        c.setFont("Helvetica-Bold", 14); c.drawString(x, y, "Audit List"); y -= 20; c.setFont("Helvetica", 10)
        for a in items:
            line = f"#{a.id} {a.title} | {a.audit_type.value} | {a.status.value}"
            c.drawString(x, y, line)
            y -= 14
            if y < 60: c.showPage(); y = 800
        c.showPage(); c.save(); buf.seek(0)
        headers = {"Content-Disposition": "attachment; filename=audits.pdf"}
        return StreamingResponse(buf, media_type="application/pdf", headers=headers)


# Single audit report export
@router.get("/{audit_id}/report")
async def export_audit_report(
    audit_id: int,
    format: str = Query("pdf", pattern="^(pdf|xlsx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    items = db.query(AuditChecklistItem).filter(AuditChecklistItem.audit_id == audit_id).all()
    findings = db.query(AuditFinding).filter(AuditFinding.audit_id == audit_id).all()

    if format == "xlsx":
        wb = Workbook(); ws = wb.active; ws.title = "Audit Report"
        ws.append(["Audit", audit.title])
        ws.append(["Type", audit.audit_type.value]); ws.append(["Status", audit.status.value])
        ws.append([]); ws.append(["Checklist Items"])
        ws.append(["Clause", "Question", "Response", "Score", "Comment", "Responsible", "Due Date"])
        for i in items:
            ws.append([i.clause_ref or '', (i.question or '')[:100], i.response.value if i.response else '', i.score or '', i.comment or '', i.responsible_person_id or '', str(i.due_date or '')])
        ws.append([]); ws.append(["Findings"])
        ws.append(["Clause", "Description", "Severity", "Status", "Target Date", "Related NC"])
        for f in findings:
            ws.append([f.clause_ref or '', (f.description or '')[:120], f.severity.value, f.status.value, str(f.target_completion_date or ''), f.related_nc_id or ''])
        buf = BytesIO(); wb.save(buf); buf.seek(0)
        headers = {"Content-Disposition": f"attachment; filename=audit_{audit_id}.xlsx"}
        return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
    else:
        buf = BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
        x, y = 40, 800
        c.setFont("Helvetica-Bold", 14); c.drawString(x, y, f"Audit Report: {audit.title}"); y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(x, y, f"Type: {audit.audit_type.value} | Status: {audit.status.value}"); y -= 16
        c.drawString(x, y, "Checklist Items:"); y -= 14
        for i in items:
            line = f"[{i.clause_ref or '-'}] {(i.question or '')[:70]} | {i.response.value if i.response else ''} | score={i.score or ''}"
            c.drawString(x, y, line); y -= 12
            if y < 60: c.showPage(); y = 800
        if y < 100: c.showPage(); y = 800
        c.drawString(40, y, "Findings:"); y -= 14
        for f in findings:
            line = f"[{f.clause_ref or '-'}] {(f.description or '')[:70]} | sev={f.severity.value} | status={f.status.value} | NC={f.related_nc_id or ''}"
            c.drawString(40, y, line); y -= 12
            if y < 60: c.showPage(); y = 800
        c.showPage(); c.save(); buf.seek(0)
        headers = {"Content-Disposition": f"attachment; filename=audit_{audit_id}.pdf"}
        return StreamingResponse(buf, media_type="application/pdf", headers=headers)


# Auditees
@router.get("/{audit_id}/auditees", response_model=List[AuditeeResponse])
async def list_auditees(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return db.query(AuditAuditee).filter(AuditAuditee.audit_id == audit_id).order_by(AuditAuditee.added_at.desc()).all()


@router.post("/{audit_id}/auditees", response_model=AuditeeResponse)
async def add_auditee(audit_id: int, user_id: int = Query(...), role: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(AuditModel).get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    aa = AuditAuditee(audit_id=audit_id, user_id=user_id, role=role)
    db.add(aa)
    db.commit()
    db.refresh(aa)
    try:
        audit_event(db, current_user.id, "audit_auditee_added", "audits", str(audit_id), {"user_id": user_id})
    except Exception:
        pass
    return aa


@router.delete("/auditees/{id}")
async def remove_auditee(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    aa = db.query(AuditAuditee).get(id)
    if not aa:
        raise HTTPException(status_code=404, detail="Auditee not found")
    audit_id = aa.audit_id
    db.delete(aa)
    db.commit()
    try:
        audit_event(db, current_user.id, "audit_auditee_removed", "audits", str(audit_id), {"auditee_id": id})
    except Exception:
        pass
    return {"message": "Auditee removed"}


