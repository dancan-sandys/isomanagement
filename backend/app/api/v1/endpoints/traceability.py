from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import json
from datetime import datetime, timedelta
import uuid
import base64
import os
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.traceability import (
    Batch, TraceabilityLink, Recall, RecallEntry, RecallAction, TraceabilityReport,
    BatchType, BatchStatus, RecallStatus, RecallType,
    RootCauseAnalysisRecord, PreventiveMeasureRecord, VerificationPlanRecord, EffectivenessReviewRecord,
    TraceabilityNode, RecallClassification, RecallCommunication, RecallEffectiveness
)
from app.models.user import User
from app.schemas.traceability import (
    BatchCreate, BatchUpdate, RecallCreate, RecallUpdate, TraceabilityLinkCreate,
    RecallEntryCreate, RecallActionCreate, TraceabilityReportCreate,
    BatchFilter, RecallFilter, TraceabilityReportRequest,
    EnhancedBatchSearch, BarcodePrintData, RecallSimulationRequest,
    RecallSimulationResponse, RecallReportRequest, RecallReportResponse,
    RootCauseAnalysis, PreventiveMeasure, VerificationPlan, EffectivenessReview
)
from app.services.traceability_service import TraceabilityService
from app.schemas.common import ResponseModel
from app.utils.audit import audit_event

router = APIRouter()


# Batch Management Endpoints
@router.get("/batches", response_model=ResponseModel)
async def get_batches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    batch_type: Optional[BatchType] = None,
    status: Optional[BatchStatus] = None,
    product_name: Optional[str] = None,
    search: Optional[str] = None,
    product_id: Optional[int] = Query(None, description="Filter batches by associated product ID")
):
    """Get batches with filtering and pagination (robust to enum mismatches)."""
    from sqlalchemy import cast, String, func as sa_func
    # Project columns and cast enum columns to String to avoid coercion errors on bad rows
    query = db.query(
        Batch.id.label("id"),
        Batch.batch_number.label("batch_number"),
        cast(Batch.batch_type, String).label("batch_type"),
        cast(Batch.status, String).label("status"),
        Batch.product_name.label("product_name"),
        Batch.quantity.label("quantity"),
        Batch.unit.label("unit"),
        Batch.production_date.label("production_date"),
        Batch.expiry_date.label("expiry_date"),
        Batch.lot_number.label("lot_number"),
        Batch.quality_status.label("quality_status"),
        Batch.storage_location.label("storage_location"),
        Batch.barcode.label("barcode"),
        Batch.created_at.label("created_at"),
    )
    
    if batch_type:
        # Accept both enum and raw strings; compare case-insensitively on the stored enum value
        try:
            target = batch_type.value if hasattr(batch_type, "value") else str(batch_type)
        except Exception:
            target = str(batch_type)
        target_normalized = (target or "").strip().lower()
        query = query.filter(sa_func.lower(cast(Batch.batch_type, String)) == target_normalized)
    if status:
        query = query.filter(Batch.status == status)
    if product_name:
        query = query.filter(Batch.product_name.ilike(f"%{product_name}%"))
    if product_id is not None:
        query = query.filter(Batch.product_id == product_id)
    if search:
        query = query.filter(
            (Batch.batch_number.ilike(f"%{search}%")) |
            (Batch.product_name.ilike(f"%{search}%")) |
            (Batch.lot_number.ilike(f"%{search}%"))
        )
    
    total = query.count()
    batches = query.order_by(desc(Batch.created_at)).offset(skip).limit(limit).all()
    
    return ResponseModel(
        success=True,
        message="Batches retrieved successfully",
        data={
        "items": [
            {
                "id": row.id,
                "batch_number": row.batch_number,
                "batch_type": (row.batch_type or None),
                "status": (row.status or None),
                "product_name": row.product_name,
                "quantity": row.quantity,
                "unit": row.unit,
                "production_date": row.production_date.isoformat() if row.production_date else None,
                "expiry_date": row.expiry_date.isoformat() if row.expiry_date else None,
                "lot_number": row.lot_number,
                "quality_status": row.quality_status,
                "storage_location": row.storage_location,
                "barcode": row.barcode,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in batches
        ],
        "total": total,
        "skip": skip,
            "limit": limit,
        },
    )


@router.get("/batches/{batch_id}", response_model=ResponseModel)
async def get_batch(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific batch by id"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

    return ResponseModel(
        success=True,
        message="Batch retrieved successfully",
        data={
            "id": batch.id,
            "batch_number": batch.batch_number,
            "batch_type": batch.batch_type.value,
            "status": batch.status.value,
            "product_name": batch.product_name,
            "quantity": batch.quantity,
            "unit": batch.unit,
            "production_date": batch.production_date.isoformat() if batch.production_date else None,
            "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
            "lot_number": batch.lot_number,
            "quality_status": batch.quality_status,
            "storage_location": batch.storage_location,
            "barcode": batch.barcode,
            "qr_code_path": batch.qr_code_path,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "updated_at": batch.updated_at.isoformat() if batch.updated_at else None,
        }
    )


# Enhanced Search Endpoint
@router.post("/batches/search/enhanced", response_model=ResponseModel)
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


# Barcode and QR Code data endpoints
@router.get("/batches/{batch_id}/barcode", response_model=ResponseModel)
async def get_batch_barcode(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get barcode data for a batch"""
    try:
        traceability_service = TraceabilityService(db)
        data = traceability_service.generate_barcode_print_data(batch_id)
        
        # Convert image path to base64 if exists
        barcode_image_base64 = None
        if data.get("barcode_image") and os.path.exists(data["barcode_image"]):
            try:
                with open(data["barcode_image"], "rb") as image_file:
                    barcode_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to read barcode image: {str(e)}")
        
        # Enrich with client-friendly fields
        data_enriched = {
            "batch_id": batch_id,
            "barcode": data.get("barcode"),
            "barcode_type": "Code128",
            "barcode_image": f"data:image/png;base64,{barcode_image_base64}" if barcode_image_base64 else None,
            "generated_at": data.get("print_timestamp"),
            "product_name": data.get("product_name"),
            "batch_number": data.get("batch_number"),
            "quantity": data.get("quantity"),
            "unit": data.get("unit"),
        }
        return ResponseModel(success=True, message="Barcode data retrieved", data=data_enriched)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get barcode data: {str(e)}")


@router.get("/batches/{batch_id}/qrcode", response_model=ResponseModel)
async def get_batch_qrcode(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QR code data for a batch"""
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

        # Provide minimal payload using stored fields
        payload = {
            "batch_number": batch.batch_number,
            "batch_type": batch.batch_type.value,
            "product_name": batch.product_name,
            "production_date": batch.production_date.isoformat() if batch.production_date else None,
            "quantity": batch.quantity,
            "unit": batch.unit,
        }

        # Convert QR code image to base64 if exists
        qr_code_image_base64 = None
        if batch.qr_code_path and os.path.exists(batch.qr_code_path):
            try:
                with open(batch.qr_code_path, "rb") as image_file:
                    qr_code_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to read QR code image: {str(e)}")

        data = {
            "batch_id": batch.id,
            "qr_code": json.dumps(payload),  # QR code content
            "qr_code_image": f"data:image/png;base64,{qr_code_image_base64}" if qr_code_image_base64 else None,
            "data_payload": json.dumps(payload),
            "generated_at": batch.created_at.isoformat() if batch.created_at else None,
        }

        return ResponseModel(success=True, message="QR code data retrieved", data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get QR code data: {str(e)}")


# Barcode Generation Endpoint
@router.get("/batches/{batch_id}/barcode/print", response_model=ResponseModel)
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
@router.post("/recalls/simulate", response_model=ResponseModel)
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
@router.post("/recalls/{recall_id}/report/with-corrective-action", response_model=ResponseModel)
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
@router.get("/batches/{batch_id}/trace/backward", response_model=ResponseModel)
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


@router.get("/batches/{batch_id}/trace/forward", response_model=ResponseModel)
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


# Traceability Chain endpoint
@router.get("/batches/{batch_id}/trace/chain", response_model=ResponseModel)
async def get_traceability_chain(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get combined traceability chain (incoming and outgoing links) for a batch"""
    try:
        service = TraceabilityService(db)
        chain = service.get_traceability_chain(batch_id)

        # Normalize response
        return ResponseModel(
            success=True,
            message="Traceability chain retrieved successfully",
            data={
                "starting_batch_id": chain["starting_batch"].id,
                "incoming_links": [
                    {
                        "id": link.id,
                        "source": link.batch_id,
                        "target": link.linked_batch_id,
                        "relationship_type": link.relationship_type,
                        "quantity_used": link.quantity_used,
                        "unit": link.unit,
                        "process_step": link.process_step,
                    }
                    for link in chain["incoming_links"]
                ],
                "outgoing_links": [
                    {
                        "id": link.id,
                        "source": link.batch_id,
                        "target": link.linked_batch_id,
                        "relationship_type": link.relationship_type,
                        "quantity_used": link.quantity_used,
                        "unit": link.unit,
                        "process_step": link.process_step,
                    }
                    for link in chain["outgoing_links"]
                ],
                "trace_path": chain["trace_path"],
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get traceability chain: {str(e)}")


# Optional Full Trace endpoint (combined backward & forward)
@router.get("/batches/{batch_id}/trace/full", response_model=ResponseModel)
async def get_full_trace(
    batch_id: int,
    depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = TraceabilityService(db)
        backward = service._trace_backward(batch_id, depth)
        forward = service._trace_forward(batch_id, depth)
        return ResponseModel(
            success=True,
            message="Full trace retrieved successfully",
            data={
                "starting_batch_id": batch_id,
                "trace_depth": depth,
                "backward": backward,
                "forward": forward,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get full trace: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get traceability chain: {str(e)}")


# Enhanced Batch Management Endpoints
@router.post("/batches", response_model=ResponseModel)
async def create_batch(
    batch_data: BatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new batch with validation"""
    try:
        traceability_service = TraceabilityService(db)
        batch = traceability_service.create_batch(batch_data, current_user.id)
        
        resp = ResponseModel(
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
        try:
            audit_event(db, current_user.id, "traceability_batch_created", "traceability", str(batch.id))
        except Exception:
            pass
        return resp
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


@router.put("/batches/{batch_id}", response_model=ResponseModel)
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
        
        resp = ResponseModel(
            success=True,
            message="Batch updated successfully",
            data={
                "id": batch.id,
                "batch_number": batch.batch_number,
                "status": batch.status.value,
                "message": "Batch updated successfully"
            }
        )
        try:
            audit_event(db, current_user.id, "traceability_batch_updated", "traceability", str(batch.id))
        except Exception:
            pass
        return resp
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


@router.delete("/batches/{batch_id}", response_model=ResponseModel)
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
        
        try:
            audit_event(db, current_user.id, "traceability_batch_deleted", "traceability", str(batch_id))
        except Exception:
            pass
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
@router.post("/recalls", response_model=ResponseModel)
async def create_recall(
    recall_data: RecallCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recall with validation"""
    try:
        traceability_service = TraceabilityService(db)
        recall = traceability_service.create_recall(recall_data, current_user.id)
        
        resp = ResponseModel(
            success=True,
            message="Recall created successfully",
            data={
                "id": recall.id,
                "recall_number": recall.recall_number,
                "message": "Recall created successfully"
            }
        )
        try:
            audit_event(db, current_user.id, "traceability_recall_created", "traceability", str(recall.id))
        except Exception:
            pass
        return resp
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


@router.put("/recalls/{recall_id}", response_model=ResponseModel)
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
        
        resp = ResponseModel(
            success=True,
            message="Recall updated successfully",
            data={
                "id": recall.id,
                "recall_number": recall.recall_number,
                "status": recall.status.value,
                "message": "Recall updated successfully"
            }
        )
        try:
            audit_event(db, current_user.id, "traceability_recall_updated", "traceability", str(recall.id))
        except Exception:
            pass
        return resp
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recall: {str(e)}"
        )


@router.get("/recalls", response_model=ResponseModel)
async def list_recalls(
    status_filter: Optional[RecallStatus] = Query(None),
    recall_type: Optional[RecallType] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List recalls with basic filtering and pagination"""
    try:
        service = TraceabilityService(db)
        filters = RecallFilter(
            status=status_filter,
            recall_type=recall_type,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        recalls, total = service.get_recalls(filters, skip=(page - 1) * size, limit=size)

        items = [
            {
                "id": r.id,
                "recall_number": r.recall_number,
                "recall_type": str(r.recall_type),
                "status": str(r.status),
                "title": r.title,
                "reason": r.reason,
                "issue_discovered_date": r.issue_discovered_date.isoformat() if r.issue_discovered_date else None,
                "total_quantity_affected": r.total_quantity_affected,
                "quantity_recalled": r.quantity_recalled,
                "assigned_to": r.assigned_to,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in recalls
        ]

        return ResponseModel(
            success=True,
            message="Recalls retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve recalls: {str(e)}")


@router.get("/recalls/{recall_id}", response_model=ResponseModel)
async def get_recall(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single recall by id"""
    try:
        recall = db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recall not found")

        return ResponseModel(
            success=True,
            message="Recall retrieved successfully",
            data={
                "id": recall.id,
                "recall_number": recall.recall_number,
                "recall_type": str(recall.recall_type),
                "status": str(recall.status),
                "title": recall.title,
                "description": recall.description,
                "reason": recall.reason,
                "hazard_description": recall.hazard_description,
                "issue_discovered_date": recall.issue_discovered_date.isoformat() if recall.issue_discovered_date else None,
                "recall_initiated_date": recall.recall_initiated_date.isoformat() if getattr(recall, "recall_initiated_date", None) else None,
                "total_quantity_affected": recall.total_quantity_affected,
                "quantity_in_distribution": recall.quantity_in_distribution,
                "quantity_recalled": recall.quantity_recalled,
                "assigned_to": recall.assigned_to,
                "created_at": recall.created_at.isoformat() if recall.created_at else None,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve recall: {str(e)}")


# Enhanced Traceability Report Endpoints
@router.post("/reports", response_model=ResponseModel)
async def create_traceability_report(
    report_data: TraceabilityReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a traceability report with validation"""
    try:
        traceability_service = TraceabilityService(db)
        report = traceability_service.create_traceability_report(report_data, current_user.id)
        
        resp = ResponseModel(
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
        try:
            audit_event(db, current_user.id, "traceability_report_created", "traceability", str(report.id))
        except Exception:
            pass
        return resp
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


@router.get("/reports", response_model=ResponseModel)
async def list_traceability_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    report_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List traceability reports with optional filters"""
    try:
        query = db.query(TraceabilityReport)
        if search:
            query = query.filter(TraceabilityReport.report_number.ilike(f"%{search}%"))
        if report_type:
            query = query.filter(TraceabilityReport.report_type == report_type)

        total = query.count()
        reports = query.order_by(desc(TraceabilityReport.created_at)).offset((page - 1) * size).limit(size).all()

        items = [
            {
                "id": r.id,
                "report_number": r.report_number,
                "report_type": r.report_type,
                "starting_batch_id": r.starting_batch_id,
                "trace_date": r.trace_date.isoformat() if r.trace_date else None,
                "trace_depth": r.trace_depth,
                "trace_summary": r.trace_summary,
            }
            for r in reports
        ]

        return ResponseModel(
            success=True,
            message="Traceability reports retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve reports: {str(e)}")


@router.get("/reports/{report_id}", response_model=ResponseModel)
async def get_traceability_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single traceability report by id"""
    try:
        report = db.query(TraceabilityReport).filter(TraceabilityReport.id == report_id).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        return ResponseModel(
            success=True,
            message="Traceability report retrieved successfully",
            data={
                "id": report.id,
                "report_number": report.report_number,
                "report_type": report.report_type,
                "starting_batch_id": report.starting_batch_id,
                "trace_date": report.trace_date.isoformat() if report.trace_date else None,
                "trace_depth": report.trace_depth,
                "traced_batches": json.loads(report.traced_batches) if report.traced_batches else [],
                "trace_path": json.loads(report.trace_path) if report.trace_path else {},
                "trace_summary": report.trace_summary,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve report: {str(e)}")


# Enhanced Dashboard Endpoint
@router.get("/dashboard/enhanced", response_model=ResponseModel)
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


# Dashboard Statistics
@router.get("/dashboard", response_model=ResponseModel)
async def get_traceability_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get traceability dashboard statistics"""
    try:
        service = TraceabilityService(db)
        stats = service.get_dashboard_stats()
        return ResponseModel(
            success=True,
            message="Dashboard statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard statistics: {str(e)}")


# Recall Entry Management
@router.post("/recalls/{recall_id}/entries", response_model=ResponseModel)
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
        
        resp = ResponseModel(
            success=True,
            message="Recall entry created successfully",
            data={
                "id": entry.id,
                "recall_id": entry.recall_id,
                "batch_id": entry.batch_id,
                "message": "Recall entry created successfully"
            }
        )
        try:
            audit_event(db, current_user.id, "traceability_recall_entry_created", "traceability", str(entry.id), {"recall_id": recall_id})
        except Exception:
            pass
        return resp
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
@router.post("/recalls/{recall_id}/actions", response_model=ResponseModel)
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
        
        resp = ResponseModel(
            success=True,
            message="Recall action created successfully",
            data={
                "id": action.id,
                "recall_id": action.recall_id,
                "action_type": action.action_type,
                "message": "Recall action created successfully"
            }
        )
        try:
            audit_event(db, current_user.id, "traceability_recall_action_created", "traceability", str(action.id), {"recall_id": recall_id})
        except Exception:
            pass
        return resp
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


# Corrective Action Suite Endpoints
@router.get("/recalls/{recall_id}/corrective-actions", response_model=ResponseModel)
async def get_corrective_actions(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        actions = db.query(RecallAction).filter(RecallAction.recall_id == recall_id).all()
        items = [
            {
                "id": a.id,
                "action_type": a.action_type,
                "description": a.description,
                "assigned_to": a.assigned_to,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "completed_date": a.completed_date.isoformat() if a.completed_date else None,
                "status": a.status,
                "results": a.results,
            }
            for a in actions
        ]
        return ResponseModel(success=True, message="Corrective actions retrieved", data={"items": items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve corrective actions: {str(e)}")


@router.post("/recalls/{recall_id}/corrective-actions", response_model=ResponseModel)
async def create_corrective_action(
    recall_id: int,
    action: RecallActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = TraceabilityService(db)
        created = service.create_recall_action(recall_id, action, current_user.id)
        return ResponseModel(success=True, message="Corrective action created", data={"id": created.id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create corrective action: {str(e)}")


@router.put("/recalls/{recall_id}/corrective-actions/{action_id}", response_model=ResponseModel)
async def update_corrective_action(
    recall_id: int,
    action_id: int,
    action: RecallActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        a = db.query(RecallAction).filter(RecallAction.id == action_id, RecallAction.recall_id == recall_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Action not found")
        a.action_type = action.action_type
        a.description = action.description
        a.assigned_to = action.assigned_to
        a.due_date = action.due_date
        db.commit()
        return ResponseModel(success=True, message="Corrective action updated", data={"id": a.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update corrective action: {str(e)}")


@router.delete("/recalls/{recall_id}/corrective-actions/{action_id}", response_model=ResponseModel)
async def delete_corrective_action(
    recall_id: int,
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        a = db.query(RecallAction).filter(RecallAction.id == action_id, RecallAction.recall_id == recall_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Action not found")
        db.delete(a)
        db.commit()
        return ResponseModel(success=True, message="Corrective action deleted", data={"id": action_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete corrective action: {str(e)}")


@router.delete("/recalls/{recall_id}/preventive-measures/{measure_id}", response_model=ResponseModel)
async def delete_preventive_measure(
    recall_id: int,
    measure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        m = db.query(PreventiveMeasureRecord).filter(PreventiveMeasureRecord.id == measure_id, PreventiveMeasureRecord.recall_id == recall_id).first()
        if not m:
            raise HTTPException(status_code=404, detail="Measure not found")
        db.delete(m)
        db.commit()
        return ResponseModel(success=True, message="Preventive measure deleted", data={"id": measure_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete preventive measure: {str(e)}")


@router.delete("/recalls/{recall_id}/verification-plans/{plan_id}", response_model=ResponseModel)
async def delete_verification_plan(
    recall_id: int,
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        p = db.query(VerificationPlanRecord).filter(VerificationPlanRecord.id == plan_id, VerificationPlanRecord.recall_id == recall_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Verification plan not found")
        db.delete(p)
        db.commit()
        return ResponseModel(success=True, message="Verification plan deleted", data={"id": plan_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete verification plan: {str(e)}")


@router.delete("/recalls/{recall_id}/effectiveness-reviews/{review_id}", response_model=ResponseModel)
async def delete_effectiveness_review(
    recall_id: int,
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        r = db.query(EffectivenessReviewRecord).filter(EffectivenessReviewRecord.id == review_id, EffectivenessReviewRecord.recall_id == recall_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Effectiveness review not found")
        db.delete(r)
        db.commit()
        return ResponseModel(success=True, message="Effectiveness review deleted", data={"id": review_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete effectiveness review: {str(e)}")


@router.get("/recalls/{recall_id}/root-cause-analysis", response_model=ResponseModel)
async def get_root_cause_analysis(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        rca = db.query(RootCauseAnalysisRecord).filter(RootCauseAnalysisRecord.recall_id == recall_id).order_by(desc(RootCauseAnalysisRecord.created_at)).first()
        return ResponseModel(success=True, message="Root cause analysis retrieved", data=(
            {
                "id": rca.id,
                "immediate_cause": rca.immediate_cause,
                "underlying_cause": rca.underlying_cause,
                "systemic_cause": rca.systemic_cause,
                "analysis_date": rca.analysis_date.isoformat(),
                "analyzed_by": rca.analyzed_by,
            } if rca else None
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve root cause analysis: {str(e)}")


@router.post("/recalls/{recall_id}/root-cause-analysis", response_model=ResponseModel)
async def create_root_cause_analysis(
    recall_id: int,
    payload: RootCauseAnalysis,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        record = RootCauseAnalysisRecord(
            recall_id=recall_id,
            immediate_cause=payload.immediate_cause,
            underlying_cause=payload.underlying_cause,
            systemic_cause=payload.systemic_cause,
            analysis_date=payload.analysis_date,
            analyzed_by=payload.analyzed_by,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return ResponseModel(success=True, message="Root cause analysis saved", data={"id": record.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save root cause analysis: {str(e)}")


@router.get("/recalls/{recall_id}/preventive-measures", response_model=ResponseModel)
async def get_preventive_measures(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        measures = db.query(PreventiveMeasureRecord).filter(PreventiveMeasureRecord.recall_id == recall_id).order_by(desc(PreventiveMeasureRecord.created_at)).all()
        items = [
            {
                "id": m.id,
                "measure_type": m.measure_type,
                "description": m.description,
                "implementation_date": m.implementation_date.isoformat() if m.implementation_date else None,
                "responsible_person": m.responsible_person,
            }
            for m in measures
        ]
        return ResponseModel(success=True, message="Preventive measures retrieved", data={"items": items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preventive measures: {str(e)}")


@router.post("/recalls/{recall_id}/preventive-measures", response_model=ResponseModel)
async def create_preventive_measure(
    recall_id: int,
    payload: PreventiveMeasure,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        record = PreventiveMeasureRecord(
            recall_id=recall_id,
            measure_type=payload.measure_type,
            description=payload.description,
            implementation_date=payload.implementation_date,
            responsible_person=payload.responsible_person,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return ResponseModel(success=True, message="Preventive measure saved", data={"id": record.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save preventive measure: {str(e)}")


@router.get("/recalls/{recall_id}/verification-plans", response_model=ResponseModel)
async def get_verification_plans(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        plans = db.query(VerificationPlanRecord).filter(VerificationPlanRecord.recall_id == recall_id).order_by(desc(VerificationPlanRecord.created_at)).all()
        items = [
            {
                "id": p.id,
                "verification_methods": p.verification_methods,
                "verification_schedule": p.verification_schedule,
                "responsible_person": p.responsible_person,
                "success_criteria": p.success_criteria,
            }
            for p in plans
        ]
        return ResponseModel(success=True, message="Verification plans retrieved", data={"items": items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve verification plans: {str(e)}")


@router.post("/recalls/{recall_id}/verification-plans", response_model=ResponseModel)
async def create_verification_plan(
    recall_id: int,
    payload: VerificationPlan,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        record = VerificationPlanRecord(
            recall_id=recall_id,
            verification_methods=payload.verification_methods,
            verification_schedule=payload.verification_schedule,
            responsible_person=payload.responsible_person,
            success_criteria=payload.success_criteria,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return ResponseModel(success=True, message="Verification plan saved", data={"id": record.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save verification plan: {str(e)}")


@router.get("/recalls/{recall_id}/effectiveness-reviews", response_model=ResponseModel)
async def get_effectiveness_reviews(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        reviews = db.query(EffectivenessReviewRecord).filter(EffectivenessReviewRecord.recall_id == recall_id).order_by(desc(EffectivenessReviewRecord.created_at)).all()
        items = [
            {
                "id": r.id,
                "review_date": r.review_date.isoformat(),
                "reviewed_by": r.reviewed_by,
                "effectiveness_score": r.effectiveness_score,
                "additional_actions_required": r.additional_actions_required,
                "review_notes": r.review_notes,
            }
            for r in reviews
        ]
        return ResponseModel(success=True, message="Effectiveness reviews retrieved", data={"items": items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve effectiveness reviews: {str(e)}")


@router.post("/recalls/{recall_id}/effectiveness-reviews", response_model=ResponseModel)
async def create_effectiveness_review(
    recall_id: int,
    payload: EffectivenessReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        record = EffectivenessReviewRecord(
            recall_id=recall_id,
            review_date=payload.review_date,
            reviewed_by=payload.reviewed_by,
            effectiveness_score=payload.effectiveness_score,
            additional_actions_required=payload.additional_actions_required,
            review_notes=payload.review_notes,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return ResponseModel(success=True, message="Effectiveness review saved", data={"id": record.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save effectiveness review: {str(e)}")


# Traceability Links CRUD
@router.post("/batches/{batch_id}/links", response_model=ResponseModel)
async def create_traceability_link(
    batch_id: int,
    payload: TraceabilityLinkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = TraceabilityService(db)
        link = service.create_traceability_link(batch_id, payload, current_user.id)
        return ResponseModel(success=True, message="Traceability link created", data={"id": link.id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create traceability link: {str(e)}")


@router.get("/batches/{batch_id}/links", response_model=ResponseModel)
async def list_traceability_links(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        links = db.query(TraceabilityLink).filter((TraceabilityLink.batch_id == batch_id) | (TraceabilityLink.linked_batch_id == batch_id)).order_by(desc(TraceabilityLink.created_at)).all()
        items = [
            {
                "id": l.id,
                "batch_id": l.batch_id,
                "linked_batch_id": l.linked_batch_id,
                "relationship_type": l.relationship_type,
                "quantity_used": l.quantity_used,
                "unit": l.unit,
                "usage_date": l.usage_date.isoformat() if l.usage_date else None,
                "process_step": l.process_step,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in links
        ]
        return ResponseModel(success=True, message="Traceability links retrieved", data={"items": items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve traceability links: {str(e)}")


@router.delete("/links/{link_id}", response_model=ResponseModel)
async def delete_traceability_link(
    link_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        link = db.query(TraceabilityLink).filter(TraceabilityLink.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Traceability link not found")
        db.delete(link)
        db.commit()
        return ResponseModel(success=True, message="Traceability link deleted", data={"id": link_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete traceability link: {str(e)}")


# Batch Status Update
@router.put("/batches/{batch_id}/status", response_model=ResponseModel)
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


# ============================================================================
# PHASE 1.3.1: ENHANCED TRACEABILITY ENDPOINTS
# ============================================================================

# One-Up, One-Back Traceability Endpoint
@router.get("/batches/{batch_id}/trace/one-up-one-back", response_model=ResponseModel)
async def get_one_up_one_back_trace(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get one-up, one-back traceability for a batch (ISO 22005:2007 compliant)"""
    try:
        service = TraceabilityService(db)
        trace_data = service.get_one_up_one_back_trace(batch_id)
        
        return ResponseModel(
            success=True,
            message="One-up, one-back traceability retrieved successfully",
            data=trace_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve traceability: {str(e)}"
        )


# Traceability Node Endpoints
@router.post("/traceability-nodes", response_model=ResponseModel)
async def create_traceability_node(
    node_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new traceability node"""
    try:
        service = TraceabilityService(db)
        node = service.create_traceability_node(node_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Traceability node created successfully",
            data={
                "id": node.id,
                "node_name": node.node_name,
                "node_type": node.node_type,
                "location": node.location,
                "contact_person": node.contact_person,
                "contact_email": node.contact_email,
                "contact_phone": node.contact_phone,
                "verification_status": node.verification_status,
                "created_at": node.created_at.isoformat() if node.created_at else None
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create traceability node: {str(e)}"
        )


@router.get("/traceability-nodes", response_model=ResponseModel)
async def get_traceability_nodes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    node_type: Optional[str] = None,
    verification_status: Optional[str] = None
):
    """Get all traceability nodes with filtering"""
    try:
        service = TraceabilityService(db)
        nodes = service.get_traceability_nodes(
            skip=skip,
            limit=limit,
            node_type=node_type,
            verification_status=verification_status
        )
        
        return ResponseModel(
            success=True,
            message="Traceability nodes retrieved successfully",
            data={
                "items": [
                    {
                        "id": node.id,
                        "node_name": node.node_name,
                        "node_type": node.node_type,
                        "location": node.location,
                        "contact_person": node.contact_person,
                        "contact_email": node.contact_email,
                        "contact_phone": node.contact_phone,
                        "verification_status": node.verification_status,
                        "last_verified": node.last_verified.isoformat() if node.last_verified else None,
                        "created_at": node.created_at.isoformat() if node.created_at else None
                    }
                    for node in nodes
                ],
                "total": len(nodes),
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve traceability nodes: {str(e)}"
        )


@router.get("/traceability-nodes/{node_id}", response_model=ResponseModel)
async def get_traceability_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific traceability node"""
    try:
        service = TraceabilityService(db)
        node = service.get_traceability_node(node_id)
        
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Traceability node not found"
            )
        
        return ResponseModel(
            success=True,
            message="Traceability node retrieved successfully",
            data={
                "id": node.id,
                "node_name": node.node_name,
                "node_type": node.node_type,
                "location": node.location,
                "contact_person": node.contact_person,
                "contact_email": node.contact_email,
                "contact_phone": node.contact_phone,
                "verification_status": node.verification_status,
                "last_verified": node.last_verified.isoformat() if node.last_verified else None,
                "verification_notes": node.verification_notes,
                "created_at": node.created_at.isoformat() if node.created_at else None,
                "updated_at": node.updated_at.isoformat() if node.updated_at else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve traceability node: {str(e)}"
        )


@router.put("/traceability-nodes/{node_id}", response_model=ResponseModel)
async def update_traceability_node(
    node_id: int,
    node_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a traceability node"""
    try:
        service = TraceabilityService(db)
        node = service.update_traceability_node(node_id, node_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Traceability node updated successfully",
            data={
                "id": node.id,
                "node_name": node.node_name,
                "node_type": node.node_type,
                "location": node.location,
                "contact_person": node.contact_person,
                "contact_email": node.contact_email,
                "contact_phone": node.contact_phone,
                "verification_status": node.verification_status,
                "updated_at": node.updated_at.isoformat() if node.updated_at else None
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update traceability node: {str(e)}"
        )


@router.delete("/traceability-nodes/{node_id}", response_model=ResponseModel)
async def delete_traceability_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a traceability node"""
    try:
        service = TraceabilityService(db)
        service.delete_traceability_node(node_id, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Traceability node deleted successfully",
            data={"id": node_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete traceability node: {str(e)}"
        )


# Traceability Verification Endpoints
@router.post("/traceability-nodes/{node_id}/verify", response_model=ResponseModel)
async def verify_traceability_node(
    node_id: int,
    verification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a traceability node"""
    try:
        service = TraceabilityService(db)
        verification_result = service.verify_traceability_node(
            node_id, 
            verification_data, 
            current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Traceability node verification completed",
            data=verification_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify traceability node: {str(e)}"
        )


@router.get("/batches/{batch_id}/trace/completeness", response_model=ResponseModel)
async def get_trace_completeness(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get traceability completeness score for a batch"""
    try:
        service = TraceabilityService(db)
        completeness_data = service._calculate_trace_completeness(batch_id)
        
        return ResponseModel(
            success=True,
            message="Traceability completeness calculated successfully",
            data=completeness_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate traceability completeness: {str(e)}"
        )


@router.get("/batches/{batch_id}/trace/verification-status", response_model=ResponseModel)
async def get_trace_verification_status(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get verification status for a batch's traceability chain"""
    try:
        service = TraceabilityService(db)
        verification_status = service._get_verification_status(batch_id)
        
        return ResponseModel(
            success=True,
            message="Traceability verification status retrieved successfully",
            data=verification_status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve verification status: {str(e)}"
        )


@router.get("/ccp/traceability-alerts", response_model=ResponseModel)
async def get_ccp_traceability_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get CCP-related traceability alerts"""
    try:
        service = TraceabilityService(db)
        alerts = service.get_ccp_traceability_alerts(skip=skip, limit=limit)
        
        return ResponseModel(
            success=True,
            message="CCP traceability alerts retrieved successfully",
            data={
                "items": alerts,
                "total": len(alerts),
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CCP alerts: {str(e)}"
        )


@router.post("/haccp/compliance-report", response_model=ResponseModel)
async def generate_haccp_compliance_report(
    report_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate HACCP compliance report for traceability"""
    try:
        service = TraceabilityService(db)
        report = service.generate_haccp_compliance_report(report_data)
        
        return ResponseModel(
            success=True,
            message="HACCP compliance report generated successfully",
            data=report
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate HACCP compliance report: {str(e)}"
        )


# ============================================================================
# PHASE 1.3.2: ENHANCED RECALL ENDPOINTS
# ============================================================================

# Recall Classification Endpoints
@router.post("/recalls/{recall_id}/classify", response_model=ResponseModel)
async def classify_recall(
    recall_id: int,
    classification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Classify a recall with health risk assessment"""
    try:
        service = TraceabilityService(db)
        classification_result = service.classify_recall(recall_id, classification_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall classified successfully",
            data=classification_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify recall: {str(e)}"
        )


@router.get("/recalls/{recall_id}/classification", response_model=ResponseModel)
async def get_recall_classification(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recall classification details"""
    try:
        classification = db.query(RecallClassification).filter(
            RecallClassification.recall_id == recall_id
        ).first()
        
        if not classification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recall classification not found"
            )
        
        return ResponseModel(
            success=True,
            message="Recall classification retrieved successfully",
            data={
                "id": classification.id,
                "recall_id": classification.recall_id,
                "health_risk_level": classification.health_risk_level,
                "risk_score": classification.risk_score,
                "affected_population": classification.affected_population,
                "severity_assessment": classification.severity_assessment,
                "urgency_level": classification.urgency_level,
                "regulatory_implications": classification.regulatory_implications,
                "classification_notes": classification.classification_notes,
                "classified_by": classification.classified_by,
                "classification_date": classification.classification_date.isoformat() if classification.classification_date else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recall classification: {str(e)}"
        )


# Recall Communication Endpoints
@router.post("/recalls/{recall_id}/communications", response_model=ResponseModel)
async def create_recall_communication(
    recall_id: int,
    communication_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a recall communication"""
    try:
        service = TraceabilityService(db)
        communication = service.create_recall_communication(recall_id, communication_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall communication created successfully",
            data={
                "id": communication.id,
                "recall_id": communication.recall_id,
                "stakeholder_type": communication.stakeholder_type,
                "communication_type": communication.communication_type,
                "subject": communication.subject,
                "message_content": communication.message_content,
                "priority": communication.priority,
                "status": communication.status,
                "created_at": communication.created_at.isoformat() if communication.created_at else None
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recall communication: {str(e)}"
        )


@router.post("/recalls/communications/{communication_id}/send", response_model=ResponseModel)
async def send_recall_communication(
    communication_id: int,
    send_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a recall communication"""
    try:
        service = TraceabilityService(db)
        send_result = service.send_communication(communication_id, send_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall communication sent successfully",
            data=send_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send recall communication: {str(e)}"
        )


@router.get("/recalls/{recall_id}/communications", response_model=ResponseModel)
async def get_recall_communications(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all communications for a recall"""
    try:
        communications = db.query(RecallCommunication).filter(
            RecallCommunication.recall_id == recall_id
        ).order_by(desc(RecallCommunication.created_at)).offset(skip).limit(limit).all()
        
        return ResponseModel(
            success=True,
            message="Recall communications retrieved successfully",
            data={
                "items": [
                    {
                        "id": comm.id,
                        "stakeholder_type": comm.stakeholder_type,
                        "communication_type": comm.communication_type,
                        "subject": comm.subject,
                        "message_content": comm.message_content,
                        "priority": comm.priority,
                        "status": comm.status,
                        "sent_at": comm.sent_at.isoformat() if comm.sent_at else None,
                        "response_received": comm.response_received,
                        "response_time_hours": comm.response_time_hours,
                        "created_at": comm.created_at.isoformat() if comm.created_at else None
                    }
                    for comm in communications
                ],
                "total": len(communications),
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recall communications: {str(e)}"
        )


# Recall Effectiveness Endpoints
@router.post("/recalls/{recall_id}/effectiveness", response_model=ResponseModel)
async def track_recall_effectiveness(
    recall_id: int,
    effectiveness_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track recall effectiveness"""
    try:
        service = TraceabilityService(db)
        effectiveness_result = service.track_recall_effectiveness(recall_id, effectiveness_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall effectiveness tracked successfully",
            data=effectiveness_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track recall effectiveness: {str(e)}"
        )


@router.get("/recalls/{recall_id}/effectiveness", response_model=ResponseModel)
async def get_recall_effectiveness(
    recall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recall effectiveness data"""
    try:
        effectiveness = db.query(RecallEffectiveness).filter(
            RecallEffectiveness.recall_id == recall_id
        ).first()
        
        if not effectiveness:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recall effectiveness data not found"
            )
        
        return ResponseModel(
            success=True,
            message="Recall effectiveness retrieved successfully",
            data={
                "id": effectiveness.id,
                "recall_id": effectiveness.recall_id,
                "effectiveness_score": effectiveness.effectiveness_score,
                "products_recovered": effectiveness.products_recovered,
                "recovery_percentage": effectiveness.recovery_percentage,
                "response_time_hours": effectiveness.response_time_hours,
                "stakeholder_cooperation": effectiveness.stakeholder_cooperation,
                "communication_effectiveness": effectiveness.communication_effectiveness,
                "verification_status": effectiveness.verification_status,
                "effectiveness_notes": effectiveness.effectiveness_notes,
                "tracked_by": effectiveness.tracked_by,
                "tracking_date": effectiveness.tracking_date.isoformat() if effectiveness.tracking_date else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recall effectiveness: {str(e)}"
        )


# Recall Reporting Endpoints
@router.get("/recalls/stakeholder-notification-matrix", response_model=ResponseModel)
async def get_stakeholder_notification_matrix(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stakeholder notification matrix for recalls"""
    try:
        service = TraceabilityService(db)
        matrix = service.get_stakeholder_notification_matrix()
        
        return ResponseModel(
            success=True,
            message="Stakeholder notification matrix retrieved successfully",
            data=matrix
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stakeholder notification matrix: {str(e)}"
        )


@router.post("/recalls/effectiveness-report", response_model=ResponseModel)
async def generate_recall_effectiveness_report(
    report_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive recall effectiveness report"""
    try:
        service = TraceabilityService(db)
        report = service.get_recall_effectiveness_report(report_data)
        
        return ResponseModel(
            success=True,
            message="Recall effectiveness report generated successfully",
            data=report
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recall effectiveness report: {str(e)}"
        )


# ============================================================================
# PHASE 1.3.3: ENHANCED BATCH MANAGEMENT ENDPOINTS
# ============================================================================

# Enhanced Batch Creation Endpoint
@router.post("/batches/enhanced", response_model=ResponseModel)
async def create_enhanced_batch(
    batch_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new batch with enhanced GS1-compliant fields"""
    try:
        service = TraceabilityService(db)
        batch = service.create_enhanced_batch(batch_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Enhanced batch created successfully",
            data={
                "id": batch.id,
                "batch_number": batch.batch_number,
                "batch_type": batch.batch_type.value,
                "status": batch.status.value,
                "product_name": batch.product_name,
                "quantity": batch.quantity,
                "unit": batch.unit,
                "production_date": batch.production_date.isoformat() if batch.production_date else None,
                "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                "lot_number": batch.lot_number,
                "gtin": batch.gtin,
                "sscc": batch.sscc,
                "hierarchical_lot_number": batch.hierarchical_lot_number,
                "supplier_information": batch.supplier_information,
                "customer_information": batch.customer_information,
                "distribution_location": batch.distribution_location,
                "barcode": batch.barcode,
                "qr_code_path": batch.qr_code_path,
                "created_at": batch.created_at.isoformat() if batch.created_at else None
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create enhanced batch: {str(e)}"
        )


# Enhanced Batch Update Endpoint
@router.put("/batches/{batch_id}/enhanced", response_model=ResponseModel)
async def update_enhanced_batch(
    batch_id: int,
    batch_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a batch with enhanced GS1-compliant fields"""
    try:
        service = TraceabilityService(db)
        batch = service.update_enhanced_batch(batch_id, batch_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Enhanced batch updated successfully",
            data={
                "id": batch.id,
                "batch_number": batch.batch_number,
                "batch_type": batch.batch_type.value,
                "status": batch.status.value,
                "product_name": batch.product_name,
                "quantity": batch.quantity,
                "unit": batch.unit,
                "production_date": batch.production_date.isoformat() if batch.production_date else None,
                "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                "lot_number": batch.lot_number,
                "gtin": batch.gtin,
                "sscc": batch.sscc,
                "hierarchical_lot_number": batch.hierarchical_lot_number,
                "supplier_information": batch.supplier_information,
                "customer_information": batch.customer_information,
                "distribution_location": batch.distribution_location,
                "barcode": batch.barcode,
                "qr_code_path": batch.qr_code_path,
                "updated_at": batch.updated_at.isoformat() if batch.updated_at else None
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update enhanced batch: {str(e)}"
        )


# Enhanced Batch Search Endpoint
@router.post("/batches/search/enhanced-gs1", response_model=ResponseModel)
async def search_enhanced_batches_gs1(
    search_criteria: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Enhanced batch search with GS1-compliant fields"""
    try:
        service = TraceabilityService(db)
        batches = service.search_enhanced_batches_gs1(search_criteria, skip, limit)
        
        return ResponseModel(
            success=True,
            message="Enhanced GS1 batch search completed successfully",
            data={
                "items": [
                    {
                        "id": batch.id,
                        "batch_number": batch.batch_number,
                        "batch_type": batch.batch_type.value,
                        "status": batch.status.value,
                        "product_name": batch.product_name,
                        "quantity": batch.quantity,
                        "unit": batch.unit,
                        "production_date": batch.production_date.isoformat() if batch.production_date else None,
                        "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                        "lot_number": batch.lot_number,
                        "gtin": batch.gtin,
                        "sscc": batch.sscc,
                        "hierarchical_lot_number": batch.hierarchical_lot_number,
                        "supplier_information": batch.supplier_information,
                        "customer_information": batch.customer_information,
                        "distribution_location": batch.distribution_location,
                        "barcode": batch.barcode,
                        "qr_code_path": batch.qr_code_path,
                        "created_at": batch.created_at.isoformat() if batch.created_at else None
                    }
                    for batch in batches
                ],
                "total": len(batches),
                "skip": skip,
                "limit": limit
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search enhanced batches: {str(e)}"
        )


# Batch GS1 Information Endpoint
@router.get("/batches/{batch_id}/gs1-info", response_model=ResponseModel)
async def get_batch_gs1_info(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get GS1-compliant information for a batch"""
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        return ResponseModel(
            success=True,
            message="GS1 information retrieved successfully",
            data={
                "id": batch.id,
                "batch_number": batch.batch_number,
                "gtin": batch.gtin,
                "sscc": batch.sscc,
                "hierarchical_lot_number": batch.hierarchical_lot_number,
                "supplier_information": batch.supplier_information,
                "customer_information": batch.customer_information,
                "distribution_location": batch.distribution_location,
                "barcode": batch.barcode,
                "qr_code_path": batch.qr_code_path
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve GS1 information: {str(e)}"
        )


# ============================================================================
# PHASE 1.3.4: INTEGRATION ENDPOINTS
# ============================================================================

# Supplier Integration Endpoints
@router.get("/integration/suppliers/{supplier_id}/information", response_model=ResponseModel)
async def get_supplier_information(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive supplier information and performance metrics"""
    try:
        service = TraceabilityService(db)
        supplier_info = service.get_supplier_information(supplier_id)
        
        return ResponseModel(
            success=True,
            message="Supplier information retrieved successfully",
            data=supplier_info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve supplier information: {str(e)}"
        )


@router.post("/integration/suppliers/{supplier_id}/notifications", response_model=ResponseModel)
async def send_supplier_notification(
    supplier_id: int,
    notification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send traceability/recall notification to supplier"""
    try:
        service = TraceabilityService(db)
        notification_result = service.send_supplier_notification(supplier_id, notification_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Supplier notification sent successfully",
            data=notification_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send supplier notification: {str(e)}"
        )


@router.get("/integration/suppliers/{supplier_id}/responses", response_model=ResponseModel)
async def track_supplier_response(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Track supplier responses to notifications"""
    try:
        service = TraceabilityService(db)
        responses = service.track_supplier_response(supplier_id, skip, limit)
        
        return ResponseModel(
            success=True,
            message="Supplier responses retrieved successfully",
            data={
                "items": responses,
                "total": len(responses),
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve supplier responses: {str(e)}"
        )


# Customer Integration Endpoints
@router.get("/integration/customers/{customer_id}/information", response_model=ResponseModel)
async def get_customer_information(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive customer information and batch history"""
    try:
        service = TraceabilityService(db)
        customer_info = service.get_customer_information(customer_id)
        
        return ResponseModel(
            success=True,
            message="Customer information retrieved successfully",
            data=customer_info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve customer information: {str(e)}"
        )


@router.post("/integration/customers/{customer_id}/notifications", response_model=ResponseModel)
async def send_customer_notification(
    customer_id: int,
    notification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send recall/traceability notification to customer"""
    try:
        service = TraceabilityService(db)
        notification_result = service.send_customer_notification(customer_id, notification_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Customer notification sent successfully",
            data=notification_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send customer notification: {str(e)}"
        )


@router.get("/integration/customers/{customer_id}/feedback", response_model=ResponseModel)
async def track_customer_feedback(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Track customer feedback and product returns"""
    try:
        service = TraceabilityService(db)
        feedback = service.track_customer_feedback(customer_id, skip, limit)
        
        return ResponseModel(
            success=True,
            message="Customer feedback retrieved successfully",
            data={
                "items": feedback,
                "total": len(feedback),
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve customer feedback: {str(e)}"
        )


# Regulatory Integration Endpoints
@router.post("/integration/regulatory/reports", response_model=ResponseModel)
async def generate_regulatory_report(
    report_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate compliance reports for regulatory bodies"""
    try:
        service = TraceabilityService(db)
        report = service.generate_regulatory_report(report_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Regulatory report generated successfully",
            data=report
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate regulatory report: {str(e)}"
        )


@router.post("/integration/regulatory/notifications", response_model=ResponseModel)
async def send_regulatory_notification(
    regulatory_body: str,
    notification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send automated notification to regulatory bodies"""
    try:
        service = TraceabilityService(db)
        notification_result = service.send_regulatory_notification(regulatory_body, notification_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Regulatory notification sent successfully",
            data=notification_result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send regulatory notification: {str(e)}"
        )


@router.get("/integration/regulatory/compliance", response_model=ResponseModel)
async def track_regulatory_compliance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track overall regulatory compliance status"""
    try:
        service = TraceabilityService(db)
        compliance_data = {
            "traceability_compliance": {"score": 95, "status": "compliant"},
            "recall_management_compliance": {"score": 92, "status": "compliant"},
            "haccp_compliance": {"score": 88, "status": "compliant"}
        }
        compliance_status = service.track_regulatory_compliance(compliance_data)
        
        return ResponseModel(
            success=True,
            message="Regulatory compliance status retrieved successfully",
            data=compliance_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve regulatory compliance: {str(e)}"
        )