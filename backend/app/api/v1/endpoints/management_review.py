from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.management_review import ManagementReviewStatus, ManagementReviewType, ActionStatus
from app.schemas.common import ResponseModel
from app.schemas.management_review import (
    ManagementReviewCreate, ManagementReviewUpdate, ManagementReviewResponse,
    ReviewActionCreate, ReviewActionUpdate, ReviewActionResponse,
    ManagementReviewInputCreate, ManagementReviewInputResponse,
    ManagementReviewOutputCreate, ManagementReviewOutputResponse,
    ManagementReviewTemplateCreate, ManagementReviewTemplateResponse,
    DataCollectionRequest, ComplianceCheckResponse,
    ReviewParticipant, ReviewParticipantUpdate
)
from app.services.management_review_service import ManagementReviewService

router = APIRouter()

# ==================== CORE REVIEW MANAGEMENT ====================

@router.post("/", response_model=ResponseModel)
async def create_review(payload: ManagementReviewCreate, db: Session = Depends(get_db)):
    """Create a new management review with ISO compliance features"""
    try:
        service = ManagementReviewService(db)
        review = service.create(payload, 1)
        return ResponseModel(success=True, message="Management review created", data=ManagementReviewResponse.model_validate(review))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create management review: {str(e)}")


@router.post("/from-template/{template_id}", response_model=ResponseModel)
async def create_review_from_template(template_id: int, payload: ManagementReviewCreate, db: Session = Depends(get_db)):
    """Create a review from a template"""
    try:
        service = ManagementReviewService(db)
        review = service.create_from_template(template_id, payload, 1)
        return ResponseModel(success=True, message="Management review created from template", data=ManagementReviewResponse.model_validate(review))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create management review from template: {str(e)}")


@router.get("/", response_model=ResponseModel)
async def list_reviews(
    page: int = Query(1, ge=1), 
    size: int = Query(20, ge=1, le=100),
    status: Optional[ManagementReviewStatus] = Query(None),
    review_type: Optional[ManagementReviewType] = Query(None),
    db: Session = Depends(get_db)
):
    """List management reviews with enhanced filtering"""
    try:
        service = ManagementReviewService(db)
        items, total = service.list(page, size, status, review_type)
        return ResponseModel(success=True, message="Management reviews retrieved", data={
            "items": [ManagementReviewResponse.model_validate(i) for i in items],
            "total": total, "page": page, "size": size, "pages": (total + size - 1) // size
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve management reviews: {str(e)}")


@router.get("/{review_id}", response_model=ResponseModel)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get a management review by ID"""
    review = ManagementReviewService(db).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Management review not found")
    return ResponseModel(success=True, message="Management review retrieved", data=ManagementReviewResponse.model_validate(review))


@router.put("/{review_id}", response_model=ResponseModel)
async def update_review(review_id: int, payload: ManagementReviewUpdate, db: Session = Depends(get_db)):
    """Update a management review"""
    try:
        service = ManagementReviewService(db)
        review = service.update(review_id, payload)
        return ResponseModel(success=True, message="Management review updated", data=ManagementReviewResponse.model_validate(review))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update management review: {str(e)}")


@router.post("/{review_id}/complete", response_model=ResponseModel)
async def complete_review(review_id: int, db: Session = Depends(get_db)):
    """Mark a review as completed and calculate effectiveness"""
    try:
        service = ManagementReviewService(db)
        review = service.complete_review(review_id, 1)
        return ResponseModel(success=True, message="Management review completed", data=ManagementReviewResponse.model_validate(review))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete management review: {str(e)}")


@router.delete("/{review_id}", response_model=ResponseModel)
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a management review"""
    try:
        ok = ManagementReviewService(db).delete(review_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Management review not found")
        return ResponseModel(success=True, message="Management review deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete management review: {str(e)}")


# ==================== DATA COLLECTION AND INPUTS ====================

@router.post("/{review_id}/collect-inputs", response_model=ResponseModel)
async def collect_review_inputs(review_id: int, request: DataCollectionRequest, db: Session = Depends(get_db)):
    """Collect all required inputs for a management review"""
    try:
        service = ManagementReviewService(db)
        inputs_data = service.collect_review_inputs(review_id, request)
        return ResponseModel(success=True, message="Review inputs collected successfully", data=inputs_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect review inputs: {str(e)}")


@router.post("/{review_id}/inputs", response_model=ResponseModel)
async def add_manual_input(review_id: int, payload: ManagementReviewInputCreate, db: Session = Depends(get_db)):
    """Add manual input to a review"""
    try:
        service = ManagementReviewService(db)
        input_record = service.add_manual_input(review_id, payload)
        return ResponseModel(success=True, message="Manual input added", data=ManagementReviewInputResponse.model_validate(input_record))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add manual input: {str(e)}")


@router.get("/{review_id}/inputs", response_model=ResponseModel)
async def get_review_inputs(review_id: int, db: Session = Depends(get_db)):
    """Get all inputs for a review"""
    try:
        service = ManagementReviewService(db)
        inputs = service.get_review_inputs(review_id)
        return ResponseModel(success=True, message="Review inputs retrieved", data=[ManagementReviewInputResponse.model_validate(i) for i in inputs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve review inputs: {str(e)}")


# ==================== OUTPUTS AND DECISIONS ====================

@router.post("/{review_id}/outputs", response_model=ResponseModel)
async def add_review_output(review_id: int, payload: ManagementReviewOutputCreate, db: Session = Depends(get_db)):
    """Add a structured output/decision to a review"""
    try:
        service = ManagementReviewService(db)
        output_record = service.add_review_output(review_id, payload)
        return ResponseModel(success=True, message="Review output added", data=ManagementReviewOutputResponse.model_validate(output_record))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add review output: {str(e)}")


@router.get("/{review_id}/outputs", response_model=ResponseModel)
async def get_review_outputs(review_id: int, db: Session = Depends(get_db)):
    """Get all outputs for a review"""
    try:
        service = ManagementReviewService(db)
        outputs = service.get_review_outputs(review_id)
        return ResponseModel(success=True, message="Review outputs retrieved", data=[ManagementReviewOutputResponse.model_validate(o) for o in outputs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve review outputs: {str(e)}")


@router.put("/outputs/{output_id}/progress", response_model=ResponseModel)
async def update_output_progress(output_id: int, progress_percentage: float = Query(..., ge=0, le=100), progress_notes: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Update progress on a review output"""
    try:
        service = ManagementReviewService(db)
        output = service.update_output_progress(output_id, progress_percentage, progress_notes)
        return ResponseModel(success=True, message="Output progress updated", data=ManagementReviewOutputResponse.model_validate(output))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update output progress: {str(e)}")


# ==================== ENHANCED ACTION MANAGEMENT ====================

@router.post("/{review_id}/actions", response_model=ResponseModel)
async def add_review_action(review_id: int, payload: ReviewActionCreate, db: Session = Depends(get_db)):
    """Add an enhanced action to a review"""
    try:
        service = ManagementReviewService(db)
        action = service.add_action(review_id, payload)
        return ResponseModel(success=True, message="Action added", data=ReviewActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add action: {str(e)}")


@router.get("/{review_id}/actions", response_model=ResponseModel)
async def list_review_actions(review_id: int, status: Optional[ActionStatus] = Query(None), db: Session = Depends(get_db)):
    """List actions with filtering"""
    try:
        service = ManagementReviewService(db)
        actions = service.list_actions(review_id, status)
        return ResponseModel(success=True, message="Actions retrieved", data=[ReviewActionResponse.model_validate(a) for a in actions])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve actions: {str(e)}")


@router.put("/actions/{action_id}", response_model=ResponseModel)
async def update_action(action_id: int, payload: ReviewActionUpdate, db: Session = Depends(get_db)):
    """Update an action with enhanced tracking"""
    try:
        service = ManagementReviewService(db)
        action = service.update_action(action_id, payload)
        return ResponseModel(success=True, message="Action updated", data=ReviewActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update action: {str(e)}")


@router.post("/actions/{action_id}/complete", response_model=ResponseModel)
async def complete_review_action(action_id: int, db: Session = Depends(get_db)):
    """Complete an action with enhanced tracking"""
    try:
        service = ManagementReviewService(db)
        action = service.complete_action(action_id, 1)
        return ResponseModel(success=True, message="Action completed", data=ReviewActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete action: {str(e)}")


@router.get("/actions/overdue", response_model=ResponseModel)
async def get_overdue_actions(review_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Get overdue actions"""
    try:
        service = ManagementReviewService(db)
        actions = service.get_overdue_actions(review_id)
        return ResponseModel(success=True, message="Overdue actions retrieved", data=[ReviewActionResponse.model_validate(a) for a in actions])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve overdue actions: {str(e)}")


# ==================== ANALYTICS AND REPORTING ====================

@router.get("/{review_id}/analytics", response_model=ResponseModel)
async def get_review_analytics(review_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analytics for a review"""
    try:
        service = ManagementReviewService(db)
        analytics = service.get_review_analytics(review_id)
        return ResponseModel(success=True, message="Review analytics retrieved", data=analytics)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve review analytics: {str(e)}")


@router.get("/{review_id}/compliance-check", response_model=ResponseModel)
async def check_iso_compliance(review_id: int, db: Session = Depends(get_db)):
    """Check ISO 22000:2018 compliance for a review"""
    try:
        service = ManagementReviewService(db)
        compliance_check = service.check_iso_compliance(review_id)
        return ResponseModel(success=True, message="ISO compliance check completed", data=compliance_check)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check ISO compliance: {str(e)}")


# ==================== TEMPLATE MANAGEMENT ====================

@router.get("/templates", response_model=ResponseModel)
async def list_templates(active_only: bool = Query(True), db: Session = Depends(get_db)):
    """List available templates"""
    try:
        service = ManagementReviewService(db)
        templates = service.list_templates(active_only)
        return ResponseModel(success=True, message="Templates retrieved", data=[ManagementReviewTemplateResponse.model_validate(t) for t in templates])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve templates: {str(e)}")


@router.get("/templates/default", response_model=ResponseModel)
async def get_default_template(db: Session = Depends(get_db)):
    """Get the default template"""
    try:
        service = ManagementReviewService(db)
        template = service.get_default_template()
        if not template:
            raise HTTPException(status_code=404, detail="No default template found")
        return ResponseModel(success=True, message="Default template retrieved", data=ManagementReviewTemplateResponse.model_validate(template))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve default template: {str(e)}")


@router.get("/templates/{template_id}", response_model=ResponseModel)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a template by ID"""
    try:
        service = ManagementReviewService(db)
        template = service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return ResponseModel(success=True, message="Template retrieved", data=ManagementReviewTemplateResponse.model_validate(template))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve template: {str(e)}")


@router.post("/templates", response_model=ResponseModel)
async def create_template(payload: ManagementReviewTemplateCreate, db: Session = Depends(get_db)):
    """Create a review template"""
    try:
        service = ManagementReviewService(db)
        template = service.create_template(
            name=payload.name,
            description=payload.description,
            created_by=1,
            agenda_template=payload.agenda_template,
            input_checklist=payload.input_checklist
        )
        return ResponseModel(success=True, message="Template created", data=ManagementReviewTemplateResponse.model_validate(template))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


# ==================== ATTENDANCE REGISTER ====================

@router.get("/{review_id}/attendance", response_model=ResponseModel)
async def list_attendance(review_id: int, db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        attendees = service.list_attendees(review_id)
        return ResponseModel(success=True, message="Attendance retrieved", data=attendees)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve attendance: {str(e)}")


@router.post("/{review_id}/attendance", response_model=ResponseModel)
async def add_attendance(review_id: int, attendee: ReviewParticipant, db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        attendees = service.add_attendee(review_id, attendee.model_dump())
        return ResponseModel(success=True, message="Attendee added", data=attendees)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add attendee: {str(e)}")


@router.put("/{review_id}/attendance/{index}", response_model=ResponseModel)
async def update_attendance(review_id: int, index: int, updates: ReviewParticipantUpdate, db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        attendee = service.update_attendee(review_id, index, updates.model_dump(exclude_unset=True))
        return ResponseModel(success=True, message="Attendee updated", data=attendee)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update attendee: {str(e)}")


@router.delete("/{review_id}/attendance/{index}", response_model=ResponseModel)
async def delete_attendance(review_id: int, index: int, db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        ok = service.delete_attendee(review_id, index)
        if not ok:
            raise HTTPException(status_code=404, detail="Attendee not found")
        return ResponseModel(success=True, message="Attendee deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete attendee: {str(e)}")


