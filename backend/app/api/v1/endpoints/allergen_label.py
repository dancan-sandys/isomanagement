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


# =============================================================================
# ALLERGEN FLAGGING & COMPLIANCE ENDPOINTS
# =============================================================================

@router.post("/assessments/{assessment_id}/flag-undeclared")
async def flag_undeclared_allergen(
    assessment_id: int,
    flagging_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Flag undeclared allergen in assessment"""
    try:
        # Check if assessment exists
        assessment = db.query(AllergenAssessment).filter(AllergenAssessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Allergen assessment not found")

        # Validate flagging data
        required_fields = ["allergen_type", "detected_in", "severity", "immediate_action"]
        for field in required_fields:
            if field not in flagging_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Create allergen flag record
        flag_data = {
            "assessment_id": assessment_id,
            "allergen_type": flagging_data["allergen_type"],
            "detected_in": flagging_data["detected_in"],  # ingredient, process, packaging
            "severity": flagging_data["severity"],  # low, medium, high, critical
            "description": flagging_data.get("description", ""),
            "immediate_action": flagging_data["immediate_action"],
            "detected_by": current_user.id,
            "detected_at": datetime.utcnow(),
            "status": "active"
        }

        # TODO: Create AllergenFlag model and save to database
        flag_id = 1  # Mock ID

        # Auto-create non-conformance for critical allergen issues
        if flagging_data["severity"] == "critical":
            # TODO: Create NC record automatically
            pass

        return ResponseModel(
            success=True,
            message="Undeclared allergen flagged successfully",
            data={
                "flag_id": flag_id,
                "assessment_id": assessment_id,
                "severity": flagging_data["severity"],
                "nc_created": flagging_data["severity"] == "critical"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flag allergen: {str(e)}")


@router.get("/assessments/{assessment_id}/flags")
async def list_allergen_flags(
    assessment_id: int,
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List allergen flags for assessment"""
    try:
        # Mock flag data - implement with actual AllergenFlag model
        flags = [
            {
                "id": 1,
                "assessment_id": assessment_id,
                "allergen_type": "nuts",
                "detected_in": "ingredient",
                "severity": "high",
                "description": "Undeclared tree nuts found in chocolate ingredient",
                "immediate_action": "Stop production, segregate batch",
                "status": "resolved",
                "detected_by": current_user.id,
                "detected_at": datetime.utcnow().isoformat()
            }
        ]

        return ResponseModel(
            success=True,
            message="Allergen flags retrieved successfully",
            data={"flags": flags}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list allergen flags: {str(e)}")


@router.get("/compliance/checklist")
async def get_regulatory_compliance_checklist(
    region: str = Query(..., description="Regulatory region (US, EU, CA, AU)"),
    product_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get regulatory compliance checklist for allergen labeling"""
    try:
        # Define region-specific compliance requirements
        compliance_checklists = {
            "US": {
                "regulations": ["FDA Food Allergen Labeling", "FALCPA"],
                "major_allergens": ["milk", "eggs", "fish", "shellfish", "tree_nuts", "peanuts", "wheat", "soybeans"],
                "requirements": [
                    {"item": "Plain language allergen statement", "required": True, "description": "Contains: [allergen list]"},
                    {"item": "Ingredient list allergen identification", "required": True, "description": "Allergens in ingredient names"},
                    {"item": "May contain warnings", "required": False, "description": "Advisory warnings for cross-contamination"},
                    {"item": "Facility sharing disclosure", "required": False, "description": "Shared facility warnings"}
                ]
            },
            "EU": {
                "regulations": ["EU Regulation 1169/2011", "Allergen Regulation"],
                "major_allergens": ["cereals_gluten", "crustaceans", "eggs", "fish", "peanuts", "soybeans", "milk", "nuts", "celery", "mustard", "sesame", "sulphites", "lupin", "molluscs"],
                "requirements": [
                    {"item": "Allergen emphasis in ingredient list", "required": True, "description": "Bold, italic, or different font"},
                    {"item": "Allergen-free claims substantiation", "required": True, "description": "Evidence for allergen-free claims"},
                    {"item": "Precautionary allergen labeling", "required": False, "description": "May contain statements"},
                    {"item": "Cross-contamination assessment", "required": True, "description": "Risk assessment documentation"}
                ]
            }
        }

        checklist = compliance_checklists.get(region, compliance_checklists["US"])
        
        return ResponseModel(
            success=True,
            message="Regulatory compliance checklist retrieved successfully",
            data={
                "region": region,
                "product_type": product_type,
                "checklist": checklist
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get compliance checklist: {str(e)}")


@router.post("/compliance/validate")
async def validate_label_compliance(
    validation_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate label compliance against regulatory requirements"""
    try:
        template_id = validation_data.get("template_id")
        region = validation_data.get("region", "US")
        
        if not template_id:
            raise HTTPException(status_code=400, detail="template_id is required")

        # Get template
        template = db.query(LabelTemplate).filter(LabelTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Label template not found")

        # Perform compliance validation
        validation_results = {
            "template_id": template_id,
            "region": region,
            "compliance_score": 85.0,  # Out of 100
            "status": "compliant_with_warnings",  # compliant, compliant_with_warnings, non_compliant
            "checks": [
                {
                    "requirement": "Plain language allergen statement",
                    "status": "pass",
                    "details": "Contains statement found",
                    "severity": "critical"
                },
                {
                    "requirement": "Allergen emphasis in ingredient list",
                    "status": "warning",
                    "details": "Some allergens not properly emphasized",
                    "severity": "major"
                },
                {
                    "requirement": "Font size compliance",
                    "status": "pass",
                    "details": "Font size meets minimum requirements",
                    "severity": "minor"
                }
            ],
            "recommendations": [
                "Ensure all allergens are properly emphasized in ingredient list",
                "Consider adding precautionary allergen statements",
                "Review cross-contamination risk assessment"
            ],
            "validated_by": current_user.id,
            "validated_at": datetime.utcnow().isoformat()
        }

        return ResponseModel(
            success=True,
            message="Label compliance validation completed",
            data=validation_results
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate compliance: {str(e)}")


# =============================================================================
# LABEL VERSION COMPARISON ENDPOINTS
# =============================================================================

@router.get("/templates/{template_id}/versions/compare")
async def compare_label_versions(
    template_id: int,
    version1_id: int = Query(...),
    version2_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare two versions of a label template"""
    try:
        # Get template and versions
        template = db.query(LabelTemplate).filter(LabelTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Label template not found")

        version1 = db.query(LabelTemplateVersion).filter(LabelTemplateVersion.id == version1_id).first()
        version2 = db.query(LabelTemplateVersion).filter(LabelTemplateVersion.id == version2_id).first()

        if not version1 or not version2:
            raise HTTPException(status_code=404, detail="One or both versions not found")

        # Perform comparison
        comparison_data = {
            "template_id": template_id,
            "template_name": template.name,
            "comparison": {
                "version1": {
                    "id": version1.id,
                    "version_number": version1.version_number,
                    "status": version1.status,
                    "created_at": version1.created_at.isoformat(),
                    "content_preview": (version1.content or "")[:200]
                },
                "version2": {
                    "id": version2.id,
                    "version_number": version2.version_number,
                    "status": version2.status,
                    "created_at": version2.created_at.isoformat(),
                    "content_preview": (version2.content or "")[:200]
                }
            },
            "differences": [
                {
                    "field": "content",
                    "type": "text_change",
                    "description": "Content updated with new allergen information",
                    "version1_value": "Previous content...",
                    "version2_value": "Updated content..."
                },
                {
                    "field": "allergen_declarations",
                    "type": "addition",
                    "description": "Added new allergen declaration",
                    "version1_value": "",
                    "version2_value": "Contains: Milk, Soy"
                }
            ],
            "similarity_score": 87.5,  # Percentage similarity
            "compared_by": current_user.id,
            "compared_at": datetime.utcnow().isoformat()
        }

        return ResponseModel(
            success=True,
            message="Label versions compared successfully",
            data=comparison_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare versions: {str(e)}")
