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


@router.post("/batches", response_model=dict)
async def create_batch(
    batch_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new batch"""
    try:
        # Generate unique batch number
        batch_number = f"BATCH-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Generate barcode
        barcode = f"BC-{batch_number}"
        
        batch = Batch(
            batch_number=batch_number,
            batch_type=batch_data.get("batch_type"),
            status=BatchStatus.IN_PRODUCTION,
            product_name=batch_data.get("product_name"),
            quantity=batch_data.get("quantity"),
            unit=batch_data.get("unit"),
            production_date=datetime.fromisoformat(batch_data.get("production_date")) if batch_data.get("production_date") else datetime.now(),
            expiry_date=datetime.fromisoformat(batch_data.get("expiry_date")) if batch_data.get("expiry_date") else None,
            lot_number=batch_data.get("lot_number"),
            supplier_id=batch_data.get("supplier_id"),
            supplier_batch_number=batch_data.get("supplier_batch_number"),
            coa_number=batch_data.get("coa_number"),
            storage_location=batch_data.get("storage_location"),
            storage_conditions=batch_data.get("storage_conditions"),
            created_by=current_user.id
        )
        
        db.add(batch)
        db.commit()
        db.refresh(batch)
        
        return {
            "id": batch.id,
            "batch_number": batch.batch_number,
            "barcode": batch.barcode,
            "message": "Batch created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/batches/{batch_id}", response_model=dict)
async def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Get traceability links
    incoming_links = db.query(TraceabilityLink).filter(TraceabilityLink.linked_batch_id == batch_id).all()
    outgoing_links = db.query(TraceabilityLink).filter(TraceabilityLink.batch_id == batch_id).all()
    
    return {
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
        "supplier_id": batch.supplier_id,
        "supplier_batch_number": batch.supplier_batch_number,
        "coa_number": batch.coa_number,
        "quality_status": batch.quality_status,
        "test_results": batch.test_results,
        "storage_location": batch.storage_location,
        "storage_conditions": batch.storage_conditions,
        "barcode": batch.barcode,
        "incoming_links": [
            {
                "id": link.id,
                "batch_id": link.batch_id,
                "relationship_type": link.relationship_type,
                "quantity_used": link.quantity_used,
                "unit": link.unit,
                "usage_date": link.usage_date,
                "process_step": link.process_step
            }
            for link in incoming_links
        ],
        "outgoing_links": [
            {
                "id": link.id,
                "linked_batch_id": link.linked_batch_id,
                "relationship_type": link.relationship_type,
                "quantity_used": link.quantity_used,
                "unit": link.unit,
                "usage_date": link.usage_date,
                "process_step": link.process_step
            }
            for link in outgoing_links
        ],
        "created_at": batch.created_at
    }


# Dashboard Endpoints
@router.get("/dashboard", response_model=dict)
async def get_traceability_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get traceability dashboard statistics"""
    try:
        # Total batches by type
        batch_counts = {}
        for batch_type in BatchType:
            count = db.query(Batch).filter(Batch.batch_type == batch_type).count()
            batch_counts[batch_type.value] = count
        
        # Total batches by status
        status_counts = {}
        for status in BatchStatus:
            count = db.query(Batch).filter(Batch.status == status).count()
            status_counts[status.value] = count
        
        # Recent batches (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_batches = db.query(Batch).filter(Batch.created_at >= thirty_days_ago).count()
        
        # Active recalls
        active_recalls = db.query(Recall).filter(
            Recall.status.in_([RecallStatus.INITIATED, RecallStatus.IN_PROGRESS])
        ).count()
        
        # Recent traceability reports (last 30 days)
        recent_reports = db.query(TraceabilityReport).filter(
            TraceabilityReport.created_at >= thirty_days_ago
        ).count()
        
        # Quality status breakdown
        quality_counts = db.query(Batch.quality_status, db.func.count(Batch.id)).group_by(Batch.quality_status).all()
        quality_breakdown = {status: count for status, count in quality_counts}
        
        return {
            "batch_counts": batch_counts,
            "status_counts": status_counts,
            "recent_batches": recent_batches,
            "active_recalls": active_recalls,
            "recent_reports": recent_reports,
            "quality_breakdown": quality_breakdown
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Traceability Link Endpoints
@router.post("/batches/{batch_id}/links", response_model=dict)
async def create_traceability_link(
    batch_id: int,
    link_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a traceability link between batches"""
    # Verify both batches exist
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    linked_batch = db.query(Batch).filter(Batch.id == link_data.get("linked_batch_id")).first()
    
    if not batch or not linked_batch:
        raise HTTPException(status_code=404, detail="One or both batches not found")
    
    try:
        link = TraceabilityLink(
            batch_id=batch_id,
            linked_batch_id=link_data.get("linked_batch_id"),
            relationship_type=link_data.get("relationship_type"),
            quantity_used=link_data.get("quantity_used"),
            unit=link_data.get("unit"),
            usage_date=datetime.fromisoformat(link_data.get("usage_date")) if link_data.get("usage_date") else datetime.now(),
            process_step=link_data.get("process_step"),
            created_by=current_user.id
        )
        
        db.add(link)
        db.commit()
        db.refresh(link)
        
        return {
            "id": link.id,
            "message": "Traceability link created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Recall Management Endpoints
@router.get("/recalls", response_model=dict)
async def get_recalls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[RecallStatus] = None,
    recall_type: Optional[RecallType] = None,
    search: Optional[str] = None
):
    """Get recalls with filtering and pagination"""
    query = db.query(Recall)
    
    if status:
        query = query.filter(Recall.status == status)
    if recall_type:
        query = query.filter(Recall.recall_type == recall_type)
    if search:
        query = query.filter(
            (Recall.recall_number.ilike(f"%{search}%")) |
            (Recall.title.ilike(f"%{search}%"))
        )
    
    total = query.count()
    recalls = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": recall.id,
                "recall_number": recall.recall_number,
                "recall_type": recall.recall_type,
                "status": recall.status,
                "title": recall.title,
                "reason": recall.reason,
                "issue_discovered_date": recall.issue_discovered_date,
                "recall_initiated_date": recall.recall_initiated_date,
                "total_quantity_affected": recall.total_quantity_affected,
                "quantity_recalled": recall.quantity_recalled,
                "assigned_to": recall.assigned_to,
                "created_at": recall.created_at
            }
            for recall in recalls
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/recalls", response_model=dict)
async def create_recall(
    recall_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recall"""
    try:
        # Generate unique recall number
        recall_number = f"RECALL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        recall = Recall(
            recall_number=recall_number,
            recall_type=recall_data.get("recall_type"),
            status=RecallStatus.DRAFT,
            title=recall_data.get("title"),
            description=recall_data.get("description"),
            reason=recall_data.get("reason"),
            hazard_description=recall_data.get("hazard_description"),
            affected_products=json.dumps(recall_data.get("affected_products", [])),
            affected_batches=json.dumps(recall_data.get("affected_batches", [])),
            date_range_start=datetime.fromisoformat(recall_data.get("date_range_start")) if recall_data.get("date_range_start") else None,
            date_range_end=datetime.fromisoformat(recall_data.get("date_range_end")) if recall_data.get("date_range_end") else None,
            total_quantity_affected=recall_data.get("total_quantity_affected"),
            quantity_in_distribution=recall_data.get("quantity_in_distribution"),
            issue_discovered_date=datetime.fromisoformat(recall_data.get("issue_discovered_date")) if recall_data.get("issue_discovered_date") else datetime.now(),
            regulatory_notification_required=recall_data.get("regulatory_notification_required", False),
            assigned_to=recall_data.get("assigned_to"),
            created_by=current_user.id
        )
        
        db.add(recall)
        db.commit()
        db.refresh(recall)
        
        return {
            "id": recall.id,
            "recall_number": recall.recall_number,
            "message": "Recall created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recalls/{recall_id}", response_model=dict)
async def get_recall(
    recall_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific recall"""
    recall = db.query(Recall).filter(Recall.id == recall_id).first()
    if not recall:
        raise HTTPException(status_code=404, detail="Recall not found")
    
    # Get recall entries and actions
    entries = db.query(RecallEntry).filter(RecallEntry.recall_id == recall_id).all()
    actions = db.query(RecallAction).filter(RecallAction.recall_id == recall_id).all()
    
    return {
        "id": recall.id,
        "recall_number": recall.recall_number,
        "recall_type": recall.recall_type,
        "status": recall.status,
        "title": recall.title,
        "description": recall.description,
        "reason": recall.reason,
        "hazard_description": recall.hazard_description,
        "affected_products": json.loads(recall.affected_products) if recall.affected_products else [],
        "affected_batches": json.loads(recall.affected_batches) if recall.affected_batches else [],
        "date_range_start": recall.date_range_start,
        "date_range_end": recall.date_range_end,
        "total_quantity_affected": recall.total_quantity_affected,
        "quantity_in_distribution": recall.quantity_in_distribution,
        "quantity_recalled": recall.quantity_recalled,
        "quantity_disposed": recall.quantity_disposed,
        "issue_discovered_date": recall.issue_discovered_date,
        "recall_initiated_date": recall.recall_initiated_date,
        "recall_completed_date": recall.recall_completed_date,
        "regulatory_notification_required": recall.regulatory_notification_required,
        "regulatory_notification_date": recall.regulatory_notification_date,
        "regulatory_reference": recall.regulatory_reference,
        "assigned_to": recall.assigned_to,
        "approved_by": recall.approved_by,
        "approved_at": recall.approved_at,
        "entries": [
            {
                "id": entry.id,
                "batch_id": entry.batch_id,
                "quantity_affected": entry.quantity_affected,
                "quantity_recalled": entry.quantity_recalled,
                "quantity_disposed": entry.quantity_disposed,
                "location": entry.location,
                "customer": entry.customer,
                "status": entry.status,
                "completion_date": entry.completion_date
            }
            for entry in entries
        ],
        "actions": [
            {
                "id": action.id,
                "action_type": action.action_type,
                "description": action.description,
                "assigned_to": action.assigned_to,
                "due_date": action.due_date,
                "completed_date": action.completed_date,
                "status": action.status,
                "results": action.results
            }
            for action in actions
        ],
        "created_at": recall.created_at
    }


@router.put("/recalls/{recall_id}/status", response_model=dict)
async def update_recall_status(
    recall_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update recall status"""
    recall = db.query(Recall).filter(Recall.id == recall_id).first()
    if not recall:
        raise HTTPException(status_code=404, detail="Recall not found")
    
    new_status = status_data.get("status")
    if new_status not in [status.value for status in RecallStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    recall.status = new_status
    
    # Update dates based on status
    if new_status == RecallStatus.INITIATED:
        recall.recall_initiated_date = datetime.now()
    elif new_status == RecallStatus.COMPLETED:
        recall.recall_completed_date = datetime.now()
    
    db.commit()
    
    return {
        "id": recall.id,
        "status": recall.status,
        "message": "Recall status updated successfully"
    }


# Traceability Report Endpoints
@router.post("/trace", response_model=dict)
async def create_traceability_report(
    trace_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a traceability report (forward/backward trace)"""
    try:
        starting_batch_id = trace_data.get("starting_batch_id")
        report_type = trace_data.get("report_type", "full_trace")
        trace_depth = trace_data.get("trace_depth", 5)
        
        # Verify starting batch exists
        starting_batch = db.query(Batch).filter(Batch.id == starting_batch_id).first()
        if not starting_batch:
            raise HTTPException(status_code=404, detail="Starting batch not found")
        
        # Generate report number
        report_number = f"TRACE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Perform traceability analysis
        traced_batches = []
        trace_path = {}
        
        if report_type in ["backward_trace", "full_trace"]:
            # Trace backward (ingredients)
            traced_batches.extend(await _trace_backward(db, starting_batch_id, trace_depth))
        
        if report_type in ["forward_trace", "full_trace"]:
            # Trace forward (products)
            traced_batches.extend(await _trace_forward(db, starting_batch_id, trace_depth))
        
        # Remove duplicates
        traced_batches = list(set(traced_batches))
        
        # Create trace path visualization
        trace_path = await _build_trace_path(db, starting_batch_id, traced_batches)
        
        # Generate summary
        trace_summary = f"Trace report for batch {starting_batch.batch_number}. Found {len(traced_batches)} related batches."
        
        report = TraceabilityReport(
            report_number=report_number,
            report_type=report_type,
            starting_batch_id=starting_batch_id,
            trace_date=datetime.now(),
            trace_depth=trace_depth,
            traced_batches=json.dumps(traced_batches),
            trace_path=json.dumps(trace_path),
            trace_summary=trace_summary,
            created_by=current_user.id
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return {
            "id": report.id,
            "report_number": report.report_number,
            "traced_batches": traced_batches,
            "trace_path": trace_path,
            "trace_summary": trace_summary,
            "message": "Traceability report created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trace/reports", response_model=dict)
async def get_traceability_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get traceability reports"""
    query = db.query(TraceabilityReport)
    total = query.count()
    reports = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": report.id,
                "report_number": report.report_number,
                "report_type": report.report_type,
                "starting_batch_id": report.starting_batch_id,
                "trace_date": report.trace_date,
                "trace_depth": report.trace_depth,
                "trace_summary": report.trace_summary,
                "created_at": report.created_at
            }
            for report in reports
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


# Helper functions for traceability analysis
async def _trace_backward(db: Session, batch_id: int, depth: int) -> List[int]:
    """Trace backward to find ingredient batches"""
    traced = []
    to_trace = [batch_id]
    current_depth = 0
    
    while to_trace and current_depth < depth:
        next_level = []
        for bid in to_trace:
            links = db.query(TraceabilityLink).filter(TraceabilityLink.linked_batch_id == bid).all()
            for link in links:
                if link.batch_id not in traced:
                    traced.append(link.batch_id)
                    next_level.append(link.batch_id)
        to_trace = next_level
        current_depth += 1
    
    return traced


async def _trace_forward(db: Session, batch_id: int, depth: int) -> List[int]:
    """Trace forward to find product batches"""
    traced = []
    to_trace = [batch_id]
    current_depth = 0
    
    while to_trace and current_depth < depth:
        next_level = []
        for bid in to_trace:
            links = db.query(TraceabilityLink).filter(TraceabilityLink.batch_id == bid).all()
            for link in links:
                if link.linked_batch_id not in traced:
                    traced.append(link.linked_batch_id)
                    next_level.append(link.linked_batch_id)
        to_trace = next_level
        current_depth += 1
    
    return traced


async def _build_trace_path(db: Session, starting_batch_id: int, traced_batches: List[int]) -> dict:
    """Build a visual trace path"""
    # Get all batches involved
    all_batch_ids = [starting_batch_id] + traced_batches
    batches = db.query(Batch).filter(Batch.id.in_(all_batch_ids)).all()
    
    # Get all links
    links = db.query(TraceabilityLink).filter(
        (TraceabilityLink.batch_id.in_(all_batch_ids)) |
        (TraceabilityLink.linked_batch_id.in_(all_batch_ids))
    ).all()
    
    # Build path structure
    path = {
        "nodes": [
            {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "type": batch.batch_type,
                "product_name": batch.product_name,
                "is_starting": batch.id == starting_batch_id
            }
            for batch in batches
        ],
        "links": [
            {
                "source": link.batch_id,
                "target": link.linked_batch_id,
                "relationship_type": link.relationship_type,
                "quantity_used": link.quantity_used,
                "unit": link.unit,
                "process_step": link.process_step
            }
            for link in links
        ]
    }
    
    return path 