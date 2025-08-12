from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.management_review import (
    ManagementReviewCreate, ManagementReviewUpdate, ManagementReviewResponse,
    ReviewActionCreate, ReviewActionResponse
)
from app.services.management_review_service import ManagementReviewService

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_review(payload: ManagementReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        review = service.create(payload, current_user.id)
        return ResponseModel(success=True, message="Management review created", data=ManagementReviewResponse.model_validate(review))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create management review: {str(e)}")


@router.get("/", response_model=ResponseModel)
async def list_reviews(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        items, total = service.list(page, size)
        return ResponseModel(success=True, message="Management reviews retrieved", data={
            "items": [ManagementReviewResponse.model_validate(i) for i in items],
            "total": total, "page": page, "size": size, "pages": (total + size - 1) // size
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve management reviews: {str(e)}")


@router.get("/{review_id}", response_model=ResponseModel)
async def get_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = ManagementReviewService(db).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Management review not found")
    return ResponseModel(success=True, message="Management review retrieved", data=ManagementReviewResponse.model_validate(review))


@router.put("/{review_id}", response_model=ResponseModel)
async def update_review(review_id: int, payload: ManagementReviewUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        review = service.update(review_id, payload)
        return ResponseModel(success=True, message="Management review updated", data=ManagementReviewResponse.model_validate(review))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update management review: {str(e)}")


@router.delete("/{review_id}", response_model=ResponseModel)
async def delete_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        ok = ManagementReviewService(db).delete(review_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Management review not found")
        return ResponseModel(success=True, message="Management review deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete management review: {str(e)}")


@router.post("/{review_id}/actions", response_model=ResponseModel)
async def add_review_action(review_id: int, payload: ReviewActionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        action = ManagementReviewService(db).add_action(review_id, payload.title, payload.description, payload.assigned_to, payload.due_date)
        return ResponseModel(success=True, message="Action added", data=ReviewActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add action: {str(e)}")


@router.get("/{review_id}/actions", response_model=ResponseModel)
async def list_review_actions(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        actions = service.list_actions(review_id)
        return ResponseModel(success=True, message="Actions retrieved", data=[ReviewActionResponse.model_validate(a) for a in actions])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve actions: {str(e)}")


@router.post("/actions/{action_id}/complete", response_model=ResponseModel)
async def complete_review_action(action_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = ManagementReviewService(db)
        action = service.complete_action(action_id)
        return ResponseModel(success=True, message="Action completed", data=ReviewActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete action: {str(e)}")


