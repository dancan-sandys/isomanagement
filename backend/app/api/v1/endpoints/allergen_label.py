from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.allergen_label import (
    ProductAllergenAssessment, AllergenRiskLevel,
    LabelTemplate, LabelTemplateVersion, LabelVersionStatus,
    LabelTemplateApproval, ApprovalStatus,
)
from app.schemas.allergen_label import (
    ProductAllergenAssessmentCreate, ProductAllergenAssessmentUpdate, ProductAllergenAssessmentResponse,
    LabelTemplateCreate, LabelTemplateResponse,
    LabelTemplateVersionCreate, LabelTemplateVersionResponse,
    LabelTemplateApprovalCreate, LabelTemplateApprovalResponse,
)
from app.utils.audit import audit_event
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


router = APIRouter()


# Allergen Assessment
@router.get("/assessments", response_model=List[ProductAllergenAssessmentResponse])
async def list_assessments(
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(ProductAllergenAssessment)
    if product_id:
        q = q.filter(ProductAllergenAssessment.product_id == product_id)
    return q.order_by(ProductAllergenAssessment.updated_at.desc()).all()


@router.post("/assessments", response_model=ProductAllergenAssessmentResponse)
async def create_assessment(
    payload: ProductAllergenAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pa = ProductAllergenAssessment(
        product_id=payload.product_id,
        inherent_allergens=(payload.inherent_allergens and ",".join(payload.inherent_allergens)) or None,
        cross_contact_sources=(payload.cross_contact_sources and ",".join(payload.cross_contact_sources)) or None,
        risk_level=AllergenRiskLevel(payload.risk_level or "low"),
        precautionary_labeling=payload.precautionary_labeling,
        control_measures=payload.control_measures,
        validation_verification=payload.validation_verification,
        reviewed_by=payload.reviewed_by,
        created_by=current_user.id,
    )
    db.add(pa)
    db.commit()
    db.refresh(pa)
    try:
        audit_event(db, current_user.id, "allergen_assessment_created", "allergen_label", str(pa.id), {"product_id": payload.product_id})
    except Exception:
        pass
    return pa


@router.put("/assessments/{assessment_id}", response_model=ProductAllergenAssessmentResponse)
async def update_assessment(
    assessment_id: int,
    payload: ProductAllergenAssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pa = db.query(ProductAllergenAssessment).get(assessment_id)
    if not pa:
        raise HTTPException(status_code=404, detail="Assessment not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {"inherent_allergens", "cross_contact_sources"} and isinstance(value, list):
            value = ",".join(value)
        if field == "risk_level" and value is not None:
            value = AllergenRiskLevel(value)
        setattr(pa, field, value)
    pa.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(pa)
    try:
        audit_event(db, current_user.id, "allergen_assessment_updated", "allergen_label", str(assessment_id))
    except Exception:
        pass
    return pa


# Label Templates & Versioning
@router.get("/templates", response_model=List[LabelTemplateResponse])
async def list_templates(include_inactive: bool = Query(False), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(LabelTemplate)
    if not include_inactive:
        q = q.filter(LabelTemplate.is_active == True)
    return q.order_by(LabelTemplate.created_at.desc()).all()


@router.post("/templates", response_model=LabelTemplateResponse)
async def create_template(payload: LabelTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = LabelTemplate(
        name=payload.name,
        description=payload.description,
        product_id=payload.product_id,
        is_active=payload.is_active if payload.is_active is not None else True,
        created_by=current_user.id,
    )
    db.add(t); db.commit(); db.refresh(t)
    try:
        audit_event(db, current_user.id, "label_template_created", "allergen_label", str(t.id))
    except Exception:
        pass
    return t


@router.post("/templates/{template_id}/versions", response_model=LabelTemplateVersionResponse)
async def create_template_version(template_id: int, payload: LabelTemplateVersionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = db.query(LabelTemplate).get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    # Next version number
    last_version = db.query(LabelTemplateVersion).filter(LabelTemplateVersion.template_id == template_id).order_by(LabelTemplateVersion.version_number.desc()).first()
    next_num = (last_version.version_number + 1) if last_version else 1
    v = LabelTemplateVersion(
        template_id=template_id,
        version_number=next_num,
        content=payload.content,
        change_description=payload.change_description,
        change_reason=payload.change_reason,
        created_by=current_user.id,
        status=LabelVersionStatus.DRAFT,
    )
    db.add(v); db.commit(); db.refresh(v)
    try:
        audit_event(db, current_user.id, "label_template_version_created", "allergen_label", str(v.id), {"template_id": template_id, "version": next_num})
    except Exception:
        pass
    return v


@router.post("/templates/{template_id}/approvals", response_model=List[LabelTemplateApprovalResponse])
async def submit_template_approvals(template_id: int, approvers: List[LabelTemplateApprovalCreate], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Target latest draft/under_review version
    version = db.query(LabelTemplateVersion).filter(LabelTemplateVersion.template_id == template_id).order_by(LabelTemplateVersion.version_number.desc()).first()
    if not version:
        raise HTTPException(status_code=404, detail="No version to approve")
    version.status = LabelVersionStatus.UNDER_REVIEW
    created: List[LabelTemplateApproval] = []
    for ap in approvers:
        a = LabelTemplateApproval(version_id=version.id, approver_id=ap.approver_id, approval_order=ap.approval_order)
        db.add(a)
        created.append(a)
    db.commit()
    for a in created:
        db.refresh(a)
    try:
        audit_event(db, current_user.id, "label_template_approval_flow_submitted", "allergen_label", str(version.id))
    except Exception:
        pass
    return created


@router.post("/templates/{template_id}/approvals/{approval_id}/approve", response_model=LabelTemplateVersionResponse)
async def approve_template(template_id: int, approval_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    a = db.query(LabelTemplateApproval).get(approval_id)
    if not a:
        raise HTTPException(status_code=404, detail="Approval not found")
    v = db.query(LabelTemplateVersion).get(a.version_id)
    if not v or v.template_id != template_id:
        raise HTTPException(status_code=400, detail="Approval/version mismatch")
    a.status = ApprovalStatus.APPROVED; a.decided_at = datetime.utcnow()
    # If all approved, mark version approved
    pending = db.query(LabelTemplateApproval).filter(LabelTemplateApproval.version_id == v.id, LabelTemplateApproval.status == ApprovalStatus.PENDING).count()
    if pending == 0:
        v.status = LabelVersionStatus.APPROVED
    db.commit(); db.refresh(v)
    try:
        audit_event(db, current_user.id, "label_template_approval_approved", "allergen_label", str(approval_id))
    except Exception:
        pass
    return v


@router.post("/templates/{template_id}/approvals/{approval_id}/reject", response_model=LabelTemplateVersionResponse)
async def reject_template(template_id: int, approval_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    a = db.query(LabelTemplateApproval).get(approval_id)
    if not a:
        raise HTTPException(status_code=404, detail="Approval not found")
    v = db.query(LabelTemplateVersion).get(a.version_id)
    if not v or v.template_id != template_id:
        raise HTTPException(status_code=400, detail="Approval/version mismatch")
    a.status = ApprovalStatus.REJECTED; a.decided_at = datetime.utcnow()
    v.status = LabelVersionStatus.REJECTED
    db.commit(); db.refresh(v)
    try:
        audit_event(db, current_user.id, "label_template_approval_rejected", "allergen_label", str(approval_id))
    except Exception:
        pass
    return v


# Listing: versions and approvals
@router.get("/templates/{template_id}/versions", response_model=list[LabelTemplateVersionResponse])
async def list_template_versions(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = db.query(LabelTemplate).get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    versions = (
        db.query(LabelTemplateVersion)
        .filter(LabelTemplateVersion.template_id == template_id)
        .order_by(LabelTemplateVersion.version_number.desc())
        .all()
    )
    return versions


@router.get("/templates/{template_id}/versions/{version_id}/approvals", response_model=list[LabelTemplateApprovalResponse])
async def list_version_approvals(template_id: int, version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(LabelTemplateVersion).get(version_id)
    if not v or v.template_id != template_id:
        raise HTTPException(status_code=404, detail="Version not found")
    approvals = (
        db.query(LabelTemplateApproval)
        .filter(LabelTemplateApproval.version_id == version_id)
        .order_by(LabelTemplateApproval.approval_order.asc())
        .all()
    )
    return approvals


# Export version PDF (with draft watermark if not approved)
@router.get("/templates/{template_id}/versions/{version_id}/export")
async def export_label_version(template_id: int, version_id: int, format: str = Query("pdf", pattern="^(pdf)$"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(LabelTemplateVersion).get(version_id)
    if not v or v.template_id != template_id:
        raise HTTPException(status_code=404, detail="Version not found")
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    # Watermark if draft/under_review/rejected
    if v.status != LabelVersionStatus.APPROVED:
        c.saveState()
        c.setFont("Helvetica-Bold", 60)
        c.setFillGray(0.9)
        c.translate(width/2, height/2)
        c.rotate(30)
        c.drawCentredString(0, 0, "DRAFT")
        c.restoreState()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 60, "Label Template Version")
    c.setFont("Helvetica", 10)
    y = height - 80
    c.drawString(40, y, f"Template ID: {template_id}  Version: {v.version_number}  Status: {v.status.value}"); y -= 16
    c.drawString(40, y, f"Created By: {v.created_by}  Created At: {v.created_at}"); y -= 16
    c.drawString(40, y, f"Change Description: {(v.change_description or '')[:80]}"); y -= 16
    c.drawString(40, y, f"Change Reason: {(v.change_reason or '')[:80]}"); y -= 20
    # Content block
    content = (v.content or "").splitlines() or [""]
    c.setFont("Courier", 9)
    for line in content:
        if y < 60:
            c.showPage(); y = height - 80
            if v.status != LabelVersionStatus.APPROVED:
                c.saveState(); c.setFont("Helvetica-Bold", 60); c.setFillGray(0.9); c.translate(width/2, height/2); c.rotate(30); c.drawCentredString(0, 0, "DRAFT"); c.restoreState()
        c.drawString(40, y, line[:100])
        y -= 12
    c.showPage(); c.save(); buf.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=label_template_{template_id}_v{v.version_number}.pdf"}
    return StreamingResponse(buf, media_type="application/pdf", headers=headers)


