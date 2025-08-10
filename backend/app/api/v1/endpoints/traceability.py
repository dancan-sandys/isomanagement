from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.traceability import (
    Batch, TraceabilityLink, Recall, RecallEntry, RecallAction, TraceabilityReport,
    BatchType, BatchStatus, RecallStatus, RecallType
)
from app.models.user import User
from app.schemas.traceability import (
    BatchCreate, BatchUpdate, RecallCreate, RecallUpdate, TraceabilityLinkCreate,
    RecallEntryCreate, RecallActionCreate, TraceabilityReportCreate,
    BatchFilter, RecallFilter, TraceabilityReportRequest,
    EnhancedBatchSearch, BarcodePrintData, RecallSimulationRequest,
    RecallSimulationResponse, RecallReportRequest, RecallReportResponse
)
from app.services.traceability_service import TraceabilityService
from app.schemas.common import ResponseModel

router = APIRouter()


# Batch Management Endpoints
@router.get("/batches", response_model=dict)
async def get_batches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    batch_type: Optional[BatchType] = None,
    status: Optional[BatchStatus] = None,
    product_name: Optional[str] = None,
    search: Optional[str] = None
):
    """Get batches with filtering and pagination"""
    query = db.query(Batch)
    
    if batch_type:
        query = query.filter(Batch.batch_type == batch_type)
    if status:
        query = query.filter(Batch.status == status)
    if product_name:
        query = query.filter(Batch.product_name.ilike(f"%{product_name}%"))
    if search:
        query = query.filter(
            (Batch.batch_number.ilike(f"%{search}%")) |
            (Batch.product_name.ilike(f"%{search}%")) |
            (Batch.lot_number.ilike(f"%{search}%"))
        )
    
    total = query.count()
    batches = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "batch_type": batch.batch_type,
                "status": batch.status,
                "product_name": batch.product_name,
                "quantity": batch.quantity,
                "unit": batch.unit,
                "production_date": batch.production_date,
                "expiry_date": batch.expiry_date,
                "lot_number": batch.lot_number,
                "quality_status": batch.quality_status,
                "storage_location": batch.storage_location,
                "barcode": batch.barcode,
                "created_at": batch.created_at
            }
            for batch in batches
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


# Enhanced Search Endpoint
@router.post("/batches/search/enhanced", response_model=dict)
async def search_batches_enhanced(
    search_criteria: EnhancedBatchSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced search by batch ID, date, or product"""
    try:
        traceability_service = TraceabilityService(db)
        search_dict = search_criteria.model_dump(exclude_none=True)
        batches = traceability_service.search_batches_enhanced(search_dict)
        
        return ResponseModel(
            success=True,
            message="Enhanced batch search completed successfully",
            data={
                "batches": [
                    {
                        "id": batch.id,
                        "batch_number": batch.batch_number,
                        "batch_type": batch.batch_type.value,
                        "status": batch.status.value,
                        "product_name": batch.product_name,
                        "quantity": batch.quantity,
                        "unit": batch.unit,
                        "production_date": batch.production_date.isoformat(),
                        "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                        "lot_number": batch.lot_number,
                        "quality_status": batch.quality_status,
                        "barcode": batch.barcode,
                        "qr_code_path": batch.qr_code_path,
                        "created_at": batch.created_at.isoformat()
                    }
                    for batch in batches
                ],
                "total_found": len(batches)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced search failed: {str(e)}"
        )


# Barcode Generation Endpoint
@router.get("/batches/{batch_id}/barcode/print", response_model=dict)
async def generate_barcode_print_data(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate barcode print data for a batch"""
    try:
        traceability_service = TraceabilityService(db)
        print_data = traceability_service.generate_barcode_print_data(batch_id)
        
        return ResponseModel(
            success=True,
            message="Barcode print data generated successfully",
            data=print_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate barcode print data: {str(e)}"
        )


# Recall Simulation Endpoint
@router.post("/recalls/simulate", response_model=dict)
async def simulate_recall(
    simulation_data: RecallSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate a product recall"""
    try:
        traceability_service = TraceabilityService(db)
        simulation_dict = simulation_data.model_dump(exclude_none=True)
        simulation_result = traceability_service.simulate_recall(simulation_dict)
        
        return ResponseModel(
            success=True,
            message="Recall simulation completed successfully",
            data=simulation_result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recall simulation failed: {str(e)}"
        )


# Recall Report with Corrective Action Endpoint
@router.post("/recalls/{recall_id}/report/with-corrective-action", response_model=dict)
async def generate_recall_report_with_corrective_action(
    recall_id: int,
    report_request: RecallReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate recall report with corrective action form"""
    try:
        traceability_service = TraceabilityService(db)
        report = traceability_service.generate_recall_report_with_corrective_action(recall_id)
        
        return ResponseModel(
            success=True,
            message="Recall report with corrective action generated successfully",
            data=report
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recall report: {str(e)}"
        )


# Enhanced Trace Backward and Forward Endpoints
@router.get("/batches/{batch_id}/trace/backward", response_model=dict)
async def trace_backward_enhanced(
    batch_id: int,
    depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced backward trace (ingredients)"""
    try:
        traceability_service = TraceabilityService(db)
        traced_batches = traceability_service._trace_backward(batch_id, depth)
        
        # Get batch details for traced batches
        batches = db.query(Batch).filter(Batch.id.in_(traced_batches)).all()
        
        return ResponseModel(
            success=True,
            message="Backward trace completed successfully",
            data={
                "starting_batch_id": batch_id,
                "trace_depth": depth,
                "traced_batches": [
                    {
                        "id": batch.id,
                        "batch_number": batch.batch_number,
                        "batch_type": batch.batch_type.value,
                        "product_name": batch.product_name,
                        "quantity": batch.quantity,
                        "unit": batch.unit,
                        "production_date": batch.production_date.isoformat(),
                        "quality_status": batch.quality_status
                    }
                    for batch in batches
                ],
                "total_ingredients_found": len(traced_batches)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backward trace failed: {str(e)}"
        )


@router.get("/batches/{batch_id}/trace/forward", response_model=dict)
async def trace_forward_enhanced(
    batch_id: int,
    depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced forward trace (distribution)"""
    try:
        traceability_service = TraceabilityService(db)
        traced_batches = traceability_service._trace_forward(batch_id, depth)
        
        # Get batch details for traced batches
        batches = db.query(Batch).filter(Batch.id.in_(traced_batches)).all()
        
        return ResponseModel(
            success=True,
            message="Forward trace completed successfully",
            data={
                "starting_batch_id": batch_id,
                "trace_depth": depth,
                "traced_batches": [
                    {
                        "id": batch.id,
                        "batch_number": batch.batch_number,
                        "batch_type": batch.batch_type.value,
                        "product_name": batch.product_name,
                        "quantity": batch.quantity,
                        "unit": batch.unit,
                        "production_date": batch.production_date.isoformat(),
                        "quality_status": batch.quality_status,
                        "status": batch.status.value
                    }
                    for batch in batches
                ],
                "total_products_found": len(traced_batches)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forward trace failed: {str(e)}"
        )


# Enhanced Batch Management Endpoints
@router.post("/batches", response_model=dict)
async def create_batch(
    batch_data: BatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new batch with validation"""
    try:
        traceability_service = TraceabilityService(db)
        batch = traceability_service.create_batch(batch_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Batch created successfully",
            data={
                "id": batch.id,
                "batch_number": batch.batch_number,
                "barcode": batch.barcode,
                "qr_code_path": batch.qr_code_path,
                "message": "Batch created successfully"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch: {str(e)}"
        )


@router.put("/batches/{batch_id}", response_model=dict)
async def update_batch(
    batch_id: int,
    batch_data: BatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a batch"""
    try:
        traceability_service = TraceabilityService(db)
        batch = traceability_service.update_batch(batch_id, batch_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Batch updated successfully",
            data={
                "id": batch.id,
                "batch_number": batch.batch_number,
                "status": batch.status.value,
                "message": "Batch updated successfully"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update batch: {str(e)}"
        )


@router.delete("/batches/{batch_id}", response_model=dict)
async def delete_batch(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a batch"""
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        db.delete(batch)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Batch deleted successfully",
            data={"id": batch_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete batch: {str(e)}"
        )


# Enhanced Recall Management Endpoints
@router.post("/recalls", response_model=dict)
async def create_recall(
    recall_data: RecallCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recall with validation"""
    try:
        traceability_service = TraceabilityService(db)
        recall = traceability_service.create_recall(recall_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall created successfully",
            data={
                "id": recall.id,
                "recall_number": recall.recall_number,
                "message": "Recall created successfully"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recall: {str(e)}"
        )


@router.put("/recalls/{recall_id}", response_model=dict)
async def update_recall(
    recall_id: int,
    recall_data: RecallUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a recall"""
    try:
        recall = db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recall not found"
            )
        
        # Update fields
        if recall_data.status is not None:
            recall.status = recall_data.status
        if recall_data.title is not None:
            recall.title = recall_data.title
        if recall_data.description is not None:
            recall.description = recall_data.description
        if recall_data.reason is not None:
            recall.reason = recall_data.reason
        if recall_data.hazard_description is not None:
            recall.hazard_description = recall_data.hazard_description
        if recall_data.affected_products is not None:
            recall.affected_products = json.dumps(recall_data.affected_products)
        if recall_data.affected_batches is not None:
            recall.affected_batches = json.dumps(recall_data.affected_batches)
        if recall_data.date_range_start is not None:
            recall.date_range_start = recall_data.date_range_start
        if recall_data.date_range_end is not None:
            recall.date_range_end = recall_data.date_range_end
        if recall_data.total_quantity_affected is not None:
            recall.total_quantity_affected = recall_data.total_quantity_affected
        if recall_data.quantity_in_distribution is not None:
            recall.quantity_in_distribution = recall_data.quantity_in_distribution
        if recall_data.regulatory_notification_required is not None:
            recall.regulatory_notification_required = recall_data.regulatory_notification_required
        if recall_data.assigned_to is not None:
            recall.assigned_to = recall_data.assigned_to
        
        recall.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(recall)
        
        return ResponseModel(
            success=True,
            message="Recall updated successfully",
            data={
                "id": recall.id,
                "recall_number": recall.recall_number,
                "status": recall.status.value,
                "message": "Recall updated successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recall: {str(e)}"
        )


# Enhanced Traceability Report Endpoints
@router.post("/reports", response_model=dict)
async def create_traceability_report(
    report_data: TraceabilityReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a traceability report with validation"""
    try:
        traceability_service = TraceabilityService(db)
        report = traceability_service.create_traceability_report(report_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Traceability report created successfully",
            data={
                "id": report.id,
                "report_number": report.report_number,
                "traced_batches": json.loads(report.traced_batches) if report.traced_batches else [],
                "trace_path": json.loads(report.trace_path) if report.trace_path else {},
                "trace_summary": report.trace_summary,
                "message": "Traceability report created successfully"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create traceability report: {str(e)}"
        )


# Enhanced Dashboard Endpoint
@router.get("/dashboard/enhanced", response_model=dict)
async def get_enhanced_traceability_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced traceability dashboard statistics"""
    try:
        traceability_service = TraceabilityService(db)
        stats = traceability_service.get_dashboard_stats()
        
        return ResponseModel(
            success=True,
            message="Enhanced traceability dashboard data retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve enhanced dashboard data: {str(e)}"
        )


# Recall Entry Management
@router.post("/recalls/{recall_id}/entries", response_model=dict)
async def create_recall_entry(
    recall_id: int,
    entry_data: RecallEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a recall entry"""
    try:
        traceability_service = TraceabilityService(db)
        entry = traceability_service.create_recall_entry(recall_id, entry_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall entry created successfully",
            data={
                "id": entry.id,
                "recall_id": entry.recall_id,
                "batch_id": entry.batch_id,
                "message": "Recall entry created successfully"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recall entry: {str(e)}"
        )


# Recall Action Management
@router.post("/recalls/{recall_id}/actions", response_model=dict)
async def create_recall_action(
    recall_id: int,
    action_data: RecallActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a recall action"""
    try:
        traceability_service = TraceabilityService(db)
        action = traceability_service.create_recall_action(recall_id, action_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall action created successfully",
            data={
                "id": action.id,
                "recall_id": action.recall_id,
                "action_type": action.action_type,
                "message": "Recall action created successfully"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recall action: {str(e)}"
        )


# Batch Status Update
@router.put("/batches/{batch_id}/status", response_model=dict)
async def update_batch_status(
    batch_id: int,
    status_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update batch status"""
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        new_status = status_data.get("status")
        if new_status not in [status.value for status in BatchStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        batch.status = new_status
        batch.updated_at = datetime.utcnow()
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Batch status updated successfully",
            data={
                "id": batch.id,
                "status": batch.status,
                "message": "Batch status updated successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update batch status: {str(e)}"
        ) 