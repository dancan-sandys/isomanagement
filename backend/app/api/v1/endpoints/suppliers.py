from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.supplier_service import SupplierService
from app.models.supplier import Supplier, Material, SupplierEvaluation, EvaluationStatus, SupplierStatus
from app.schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierResponse, SupplierListResponse,
    MaterialCreate, MaterialUpdate, MaterialResponse, MaterialListResponse,
    SupplierEvaluationCreate, SupplierEvaluationUpdate, SupplierEvaluationResponse, EvaluationListResponse,
    IncomingDeliveryCreate, IncomingDeliveryUpdate, IncomingDeliveryResponse, DeliveryListResponse,
    SupplierDocumentCreate, SupplierDocumentUpdate, SupplierDocumentResponse, DocumentListResponse,
    SupplierFilter, MaterialFilter, EvaluationFilter, DeliveryFilter,
    BulkSupplierAction, BulkMaterialAction, SupplierDashboardStats,
    InspectionChecklistResponse, InspectionChecklistCreate, InspectionChecklistUpdate,
    InspectionChecklistItemResponse, InspectionChecklistItemCreate, InspectionChecklistItemUpdate
)
from app.schemas.common import ResponseModel
from app.utils.audit import audit_event

router = APIRouter()

# Analytics endpoints (must come before path parameter endpoints)
@router.get("/analytics/performance", response_model=ResponseModel[dict])
async def get_performance_analytics(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance analytics"""
    service = SupplierService(db)
    
    # Mock analytics data for now
    analytics_data = {
        "trends": [
            {"date": "2024-01", "average_score": 4.2},
            {"date": "2024-02", "average_score": 4.3},
            {"date": "2024-03", "average_score": 4.1},
            {"date": "2024-04", "average_score": 4.4}
        ],
        "category_performance": [
            {"category": "raw_milk", "average_score": 4.3},
            {"category": "additives", "average_score": 4.1},
            {"category": "packaging", "average_score": 4.2}
        ],
        "risk_distribution": [
            {"risk_level": "low", "count": 5},
            {"risk_level": "medium", "count": 2},
            {"risk_level": "high", "count": 1}
        ]
    }
    
    return ResponseModel(
        success=True,
        message="Performance analytics retrieved successfully",
        data=analytics_data
    )

@router.get("/analytics/risk-assessment", response_model=ResponseModel[dict])
async def get_risk_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get risk assessment analytics"""
    service = SupplierService(db)
    
    # Mock risk assessment data for now
    risk_data = {
        "risk_matrix": [
            {"risk_level": "low", "count": 5, "percentage": 62.5},
            {"risk_level": "medium", "count": 2, "percentage": 25.0},
            {"risk_level": "high", "count": 1, "percentage": 12.5}
        ],
        "high_risk_suppliers": [],
        "risk_trends": [
            {"date": "2024-01", "high_risk_count": 1},
            {"date": "2024-02", "high_risk_count": 1},
            {"date": "2024-03", "high_risk_count": 0},
            {"date": "2024-04", "high_risk_count": 1}
        ]
    }
    
    return ResponseModel(
        success=True,
        message="Risk assessment retrieved successfully",
        data=risk_data
    )

# Alerts endpoints (must come before path parameter endpoints)
@router.get("/alerts", response_model=ResponseModel[dict])
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    type: Optional[str] = Query(None, description="Filter by alert type"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts with filtering and pagination"""
    # Mock alerts data for now
    alerts_data = {
        "items": [
            {
                "id": 1,
                "type": "expired_certificate",
                "severity": "high",
                "title": "Certificate Expired",
                "description": "Supplier ABC's certificate has expired",
                "created_at": "2024-01-15T10:00:00",
                "resolved": False
            },
            {
                "id": 2,
                "type": "overdue_evaluation",
                "severity": "medium",
                "title": "Evaluation Overdue",
                "description": "Supplier XYZ evaluation is overdue",
                "created_at": "2024-01-14T09:00:00",
                "resolved": True
            }
        ],
        "total": 2,
        "page": page,
        "size": size,
        "pages": 1
    }
    
    return ResponseModel(
        success=True,
        message="Alerts retrieved successfully",
        data=alerts_data
    )

@router.post("/alerts/{alert_id}/resolve", response_model=ResponseModel[dict])
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve an alert"""
    # Mock resolution for now
    return ResponseModel(
        success=True,
        message="Alert resolved successfully",
        data={"message": "Alert resolved successfully"}
    )

# Statistics endpoints (must come before path parameter endpoints)
@router.get("/stats", response_model=ResponseModel[dict])
async def get_supplier_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier statistics"""
    service = SupplierService(db)
    
    # Get basic stats from service
    dashboard_stats = service.get_dashboard_stats()
    
    # Count suppliers by status
    suppliers_by_status = dashboard_stats.get("suppliers_by_status", [])
    pending_approval = len([s for s in suppliers_by_status if s.get("status") == "pending_approval"])
    suspended_suppliers = len([s for s in suppliers_by_status if s.get("status") == "suspended"])
    blacklisted_suppliers = len([s for s in suppliers_by_status if s.get("status") == "blacklisted"])
    
    stats_data = {
        "total_suppliers": dashboard_stats.get("total_suppliers", 0),
        "active_suppliers": dashboard_stats.get("active_suppliers", 0),
        "pending_approval": pending_approval,
        "suspended_suppliers": suspended_suppliers,
        "blacklisted_suppliers": blacklisted_suppliers,
        "overdue_evaluations": dashboard_stats.get("overdue_evaluations", 0),
        "upcoming_evaluations": 0,  # Mock data
        "recent_deliveries": len(dashboard_stats.get("recent_deliveries", [])),
        "quality_alerts": 0  # Mock data
    }
    
    return ResponseModel(
        success=True,
        message="Supplier statistics retrieved successfully",
        data=stats_data
    )



# Dashboard endpoints (must come before path parameter endpoints)
@router.get("/dashboard/stats", response_model=ResponseModel[SupplierDashboardStats])
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier dashboard statistics"""
    service = SupplierService(db)
    stats = service.get_dashboard_stats()
    
    return ResponseModel(
        success=True,
        message="Dashboard stats retrieved successfully",
        data=stats
    )


# Supplier endpoints
@router.get("/", response_model=ResponseModel[SupplierListResponse])
async def get_suppliers(
    search: Optional[str] = Query(None, description="Search by name, code, or contact person"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get suppliers with filtering and pagination"""
    filter_params = SupplierFilter(
        search=search,
        category=category,
        status=status,
        risk_level=risk_level,
        page=page,
        size=size
    )
    
    service = SupplierService(db)
    result = service.get_suppliers(filter_params)
    
    response_data = SupplierListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )

    return ResponseModel(
        success=True,
        message="Suppliers retrieved successfully",
        data=response_data
    )


@router.post("/", response_model=ResponseModel[SupplierResponse])
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new supplier"""
    service = SupplierService(db)
    
    # Check if supplier code already exists
    existing_supplier = service.db.query(service.db.query(Supplier).filter(
        Supplier.supplier_code == supplier_data.supplier_code
    ).exists()).scalar()
    
    if existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier code already exists"
        )
    
    supplier = service.create_supplier(supplier_data, current_user.id)
    try:
        audit_event(db, current_user.id, "supplier_created", "suppliers", str(supplier.id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Supplier created successfully",
        data=supplier
    )


<<<<<<< HEAD
# Material endpoints (must come before /{supplier_id} route)
=======
@router.put("/{supplier_id}", response_model=ResponseModel[SupplierResponse])
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update supplier"""
    service = SupplierService(db)
    supplier = service.update_supplier(supplier_id, supplier_data)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    try:
        audit_event(db, current_user.id, "supplier_updated", "suppliers", str(supplier.id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Supplier updated successfully",
        data=supplier
    )


@router.delete("/{supplier_id}", response_model=ResponseModel[dict])
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete supplier"""
    service = SupplierService(db)
    success = service.delete_supplier(supplier_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    try:
        audit_event(db, current_user.id, "supplier_deleted", "suppliers", str(supplier_id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Supplier deleted successfully",
        data={"message": "Supplier deleted successfully"}
    )


@router.post("/bulk/action", response_model=ResponseModel[dict])
async def bulk_update_suppliers(
    action_data: BulkSupplierAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update suppliers"""
    service = SupplierService(db)
    result = service.bulk_update_suppliers(action_data)
    
    return ResponseModel(
        success=True,
        message=f"Bulk action completed successfully",
        data=result
    )


# Material endpoints
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc
@router.get("/materials/", response_model=ResponseModel[MaterialListResponse])
async def get_materials(
    search: Optional[str] = Query(None, description="Search by name or code"),
    category: Optional[str] = Query(None, description="Filter by category"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    approval_status: Optional[str] = Query(None, description="Filter by approval status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get materials with filtering and pagination"""
    filter_params = MaterialFilter(
        search=search,
        category=category,
        supplier_id=supplier_id,
        approval_status=approval_status,
        page=page,
        size=size
    )
    
    service = SupplierService(db)
    result = service.get_materials(filter_params)
    
    response_data = MaterialListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )

    return ResponseModel(
        success=True,
        message="Materials retrieved successfully",
        data=response_data
    )


@router.get("/materials/{material_id}", response_model=ResponseModel[MaterialResponse])
async def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get material by ID"""
    service = SupplierService(db)
    material = service.get_material(material_id)
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return ResponseModel(
        success=True,
        message="Material retrieved successfully",
        data=material
    )


<<<<<<< HEAD
# Temporarily commented out to test route conflicts
# @router.post("/materials/", response_model=ResponseModel[MaterialResponse])
# async def create_material(
#     material_data: MaterialCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Create a new material"""
#     service = SupplierService(db)
#     
#     # Check if material code already exists for this supplier
#     existing_material = service.db.query(service.db.query(Material).filter(
#         Material.material_code == material_data.material_code,
#         Material.supplier_id == material_data.supplier_id
#     ).exists()).scalar()
#     
#     if existing_material:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Material code already exists for this supplier"
#         )
#     
#     material = service.create_material(material_data, current_user.id)
#     
#     return ResponseModel(
#         success=True,
#         message="Material created successfully",
#         data=material
#     )
=======
@router.post("/materials/", response_model=ResponseModel[MaterialResponse])
async def create_material(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new material"""
    service = SupplierService(db)
    
    # Check if material code already exists for this supplier
    existing_material = service.db.query(service.db.query(Material).filter(
        Material.material_code == material_data.material_code,
        Material.supplier_id == material_data.supplier_id
    ).exists()).scalar()
    
    if existing_material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material code already exists for this supplier"
        )
    
    material = service.create_material(material_data, current_user.id)
    try:
        audit_event(db, current_user.id, "material_created", "suppliers", str(material.id), {"supplier_id": material_data.supplier_id})
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Material created successfully",
        data=material
    )
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc


@router.put("/materials/{material_id}", response_model=ResponseModel[MaterialResponse])
async def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update material"""
    service = SupplierService(db)
    material = service.update_material(material_id, material_data)
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    try:
        audit_event(db, current_user.id, "material_updated", "suppliers", str(material.id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Material updated successfully",
        data=material
    )


@router.delete("/materials/{material_id}", response_model=ResponseModel[dict])
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete material"""
    service = SupplierService(db)
    success = service.delete_material(material_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    try:
        audit_event(db, current_user.id, "material_deleted", "suppliers", str(material_id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Material deleted successfully",
        data={"message": "Material deleted successfully"}
    )


# Evaluation endpoints (must come before /{supplier_id} route)
@router.get("/evaluations/", response_model=ResponseModel[EvaluationListResponse])
async def get_evaluations(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    evaluation_period: Optional[str] = Query(None, description="Filter by evaluation period"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Filter by start date"),
    date_to: Optional[str] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get evaluations with filtering and pagination"""
    filter_params = EvaluationFilter(
        supplier_id=supplier_id,
        evaluation_period=evaluation_period,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size
    )
    
    service = SupplierService(db)
    result = service.get_evaluations(filter_params)
    
    response_data = EvaluationListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )

    return ResponseModel(
        success=True,
        message="Evaluations retrieved successfully",
        data=response_data
    )


@router.get("/evaluations/{evaluation_id}", response_model=ResponseModel[SupplierEvaluationResponse])
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get evaluation by ID"""
    service = SupplierService(db)
    evaluation = service.get_evaluation(evaluation_id)
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    return ResponseModel(
        success=True,
        message="Evaluation retrieved successfully",
        data=evaluation
    )


@router.post("/evaluations/", response_model=ResponseModel[SupplierEvaluationResponse])
async def create_evaluation(
    evaluation_data: SupplierEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new evaluation"""
    service = SupplierService(db)
    evaluation = service.create_evaluation(evaluation_data, current_user.id)
    try:
        audit_event(db, current_user.id, "supplier_evaluation_created", "suppliers", str(evaluation.id), {"supplier_id": evaluation_data.supplier_id})
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Evaluation created successfully",
        data=evaluation
    )


@router.put("/evaluations/{evaluation_id}", response_model=ResponseModel[SupplierEvaluationResponse])
async def update_evaluation(
    evaluation_id: int,
    evaluation_data: SupplierEvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update evaluation"""
    service = SupplierService(db)
    evaluation = service.update_evaluation(evaluation_id, evaluation_data)
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    try:
        audit_event(db, current_user.id, "supplier_evaluation_updated", "suppliers", str(evaluation.id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Evaluation updated successfully",
        data=evaluation
    )


@router.delete("/evaluations/{evaluation_id}", response_model=ResponseModel[dict])
async def delete_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete evaluation"""
    service = SupplierService(db)
    success = service.delete_evaluation(evaluation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    try:
        audit_event(db, current_user.id, "supplier_evaluation_deleted", "suppliers", str(evaluation_id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Evaluation deleted successfully",
        data={"message": "Evaluation deleted successfully"}
    )


<<<<<<< HEAD
# Delivery endpoints (must come before /{supplier_id} route)
=======
# COA upload/download and delivery inspection endpoints
@router.post("/deliveries/{delivery_id}/coa", response_model=dict)
async def upload_delivery_coa(
    delivery_id: int,
    coa_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload Certificate of Analysis (COA) file for a delivery"""
    service = SupplierService(db)
    delivery = service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

    upload_dir = "uploads/deliveries/coa"
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = f"delivery_{delivery_id}_{int(datetime.utcnow().timestamp())}_{coa_file.filename}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(coa_file.file, buffer)

    # persist on delivery
    delivery.coa_file_path = file_path
    delivery.coa_number = delivery.coa_number or safe_name
    db.commit()
    db.refresh(delivery)

    try:
        audit_event(db, current_user.id, "delivery_coa_uploaded", "suppliers", str(delivery.id))
    except Exception:
        pass
    return {"file_path": file_path}


@router.get("/deliveries/{delivery_id}/coa/download")
async def download_delivery_coa(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the COA file for a delivery"""
    service = SupplierService(db)
    delivery = service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    if not delivery.coa_file_path or not os.path.exists(delivery.coa_file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COA file not found")

    # Stream file
    from fastapi.responses import FileResponse
    return FileResponse(delivery.coa_file_path, filename=os.path.basename(delivery.coa_file_path))


class InspectPayload(BaseModel):
    status: str
    comments: Optional[str] = None


@router.post("/deliveries/{delivery_id}/inspect", response_model=IncomingDeliveryResponse)
async def inspect_delivery(
    delivery_id: int,
    payload: InspectPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update inspection status; enforce COA for critical materials (e.g., raw milk, additives, cultures)."""
    service = SupplierService(db)
    delivery = service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

    # COA enforcement for critical categories
    critical_categories = {"raw_milk", "additives", "cultures"}
    material = service.get_material(delivery.material_id)
    status_value = (payload.status or "").lower()
    if status_value in ("passed", "released") and material and material.category and material.category.lower() in critical_categories:
        if not delivery.coa_file_path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="COA is required for this material category before passing inspection")

    # Persist inspection
    # Map 'under_review' to 'pending' for storage
    normalized_status = status_value if status_value != "under_review" else "pending"
    update = IncomingDeliveryUpdate(
        inspection_status=normalized_status,
        inspection_date=datetime.utcnow(),
        corrective_actions=payload.comments,
    )
    updated = service.update_delivery(delivery_id, update)
    try:
        audit_event(db, current_user.id, "delivery_inspected", "suppliers", str(delivery_id), {"status": normalized_status})
    except Exception:
        pass
    return updated


# Delivery -> Batch linkage
@router.post("/deliveries/{delivery_id}/create-batch", response_model=dict)
async def create_batch_from_delivery(
    delivery_id: int,
    link_to_batch_id: Optional[int] = Query(None, description="If provided, create a traceability link to this target batch"),
    link_relationship_type: Optional[str] = Query("ingredient"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Batch from a delivery and create traceability link to it."""
    # Load delivery
    supplier_service = SupplierService(db)
    delivery = supplier_service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")

    # Create batch using traceability service
    from app.services.traceability_service import TraceabilityService
    from app.schemas.traceability import BatchCreate, TraceabilityLinkCreate, BatchType
    trace_service = TraceabilityService(db)

    product_name = f"{delivery.material.name} - Received"
    batch_create = BatchCreate(
        batch_type=BatchType.INTERMEDIATE,
        product_name=product_name,
        quantity=delivery.quantity_received,
        unit=delivery.unit or "kg",
        production_date=delivery.delivery_date,
        expiry_date=None,
        lot_number=delivery.lot_number or delivery.batch_number,
        supplier_id=delivery.supplier_id,
        supplier_batch_number=delivery.batch_number,
        coa_number=delivery.coa_number,
        storage_location=delivery.storage_location,
        storage_conditions=delivery.storage_conditions,
    )

    # Map material category -> BatchType if possible
    try:
        category = (supplier_service.get_material(delivery.material_id).category or "").lower()
        category_map = {
            "raw_milk": BatchType.RAW_MILK,
            "additives": BatchType.ADDITIVE,
            "cultures": BatchType.CULTURE,
            "packaging": BatchType.PACKAGING,
        }
        batch_create.batch_type = category_map.get(category, BatchType.INTERMEDIATE)
    except Exception:
        pass

    batch = trace_service.create_batch(batch_create, current_user.id)

    link_id: Optional[int] = None
    if link_to_batch_id:
        # Create traceability link from ingredient (this batch) to target product batch
        link = trace_service.create_traceability_link(
            batch.id,
            TraceabilityLinkCreate(
                linked_batch_id=link_to_batch_id,
                relationship_type=link_relationship_type or "ingredient",
                quantity_used=delivery.quantity_received,
                unit=delivery.unit or "kg",
                usage_date=datetime.utcnow(),
                process_step="receiving",
            ),
            current_user.id,
        )
        link_id = link.id

    try:
        audit_event(db, current_user.id, "delivery_batch_created", "suppliers", str(delivery_id), {"batch_id": batch.id, "link_id": link_id})
    except Exception:
        pass
    return {"batch_id": batch.id, "link_id": link_id}


# Delivery endpoints
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc
@router.get("/deliveries/", response_model=DeliveryListResponse)
async def get_deliveries(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    delivery_date_from: Optional[str] = Query(None, description="Filter by delivery date from"),
    delivery_date_to: Optional[str] = Query(None, description="Filter by delivery date to"),
    status: Optional[str] = Query(None, description="Filter by status"),
    material_id: Optional[int] = Query(None, description="Filter by material"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get deliveries with filtering and pagination"""
    filter_params = DeliveryFilter(
        supplier_id=supplier_id,
        delivery_date_from=delivery_date_from,
        delivery_date_to=delivery_date_to,
        status=status,
        material_id=material_id,
        page=page,
        size=size
    )
    
    service = SupplierService(db)
    result = service.get_deliveries(filter_params)
    
    response_data = DeliveryListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )
    
    return response_data


@router.get("/deliveries/{delivery_id}", response_model=IncomingDeliveryResponse)
async def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get delivery by ID"""
    service = SupplierService(db)
    delivery = service.get_delivery(delivery_id)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    return delivery


@router.post("/deliveries/", response_model=IncomingDeliveryResponse)
async def create_delivery(
    delivery_data: IncomingDeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new delivery"""
    service = SupplierService(db)
    delivery = service.create_delivery(delivery_data, current_user.id)
<<<<<<< HEAD
    
=======
    try:
        audit_event(db, current_user.id, "delivery_created", "suppliers", str(delivery.id), {"supplier_id": delivery.supplier_id})
    except Exception:
        pass
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc
    return delivery


@router.put("/deliveries/{delivery_id}", response_model=IncomingDeliveryResponse)
async def update_delivery(
    delivery_id: int,
    delivery_data: IncomingDeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update delivery"""
    service = SupplierService(db)
    delivery = service.update_delivery(delivery_id, delivery_data)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    try:
        audit_event(db, current_user.id, "delivery_updated", "suppliers", str(delivery.id))
    except Exception:
        pass
    return delivery


@router.delete("/deliveries/{delivery_id}", response_model=ResponseModel[dict])
async def delete_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete delivery"""
    service = SupplierService(db)
    success = service.delete_delivery(delivery_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
<<<<<<< HEAD
    return ResponseModel(
        success=True,
        message="Delivery deleted successfully",
        data={"message": "Delivery deleted successfully"}
    )


# Now the generic supplier routes
# Temporarily commented out to test route conflicts
# @router.get("/{supplier_id}", response_model=ResponseModel[SupplierResponse])
# async def get_supplier(
#     supplier_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Get supplier by ID"""
#     service = SupplierService(db)
#     supplier = service.get_supplier(supplier_id)
#     
#     if not supplier:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Supplier not found"
#         )
#     
#     return ResponseModel(
#         success=True,
#         message="Supplier retrieved successfully",
#         data=supplier
#     )


@router.put("/{supplier_id}", response_model=ResponseModel[SupplierResponse])
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update supplier"""
    service = SupplierService(db)
    supplier = service.update_supplier(supplier_id, supplier_data)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return ResponseModel(
        success=True,
        message="Supplier updated successfully",
        data=supplier
    )


@router.delete("/{supplier_id}", response_model=ResponseModel[dict])
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete supplier"""
    service = SupplierService(db)
    success = service.delete_supplier(supplier_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return ResponseModel(
        success=True,
        message="Supplier deleted successfully",
        data={"message": "Supplier deleted successfully"}
    )


@router.post("/bulk/action", response_model=ResponseModel[dict])
async def bulk_update_suppliers(
    action_data: BulkSupplierAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update suppliers"""
    service = SupplierService(db)
    result = service.bulk_update_suppliers(action_data)
    
    return ResponseModel(
        success=True,
        message=f"Bulk action completed successfully",
        data=result
    )


@router.post("/materials/bulk/action", response_model=ResponseModel[dict])
async def bulk_update_materials(
    action_data: BulkMaterialAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update materials"""
    service = SupplierService(db)
    result = service.bulk_update_materials(action_data)
    
    return ResponseModel(
        success=True,
        message=f"Bulk material action completed successfully",
        data=result
    )
=======
    try:
        audit_event(db, current_user.id, "delivery_deleted", "suppliers", str(delivery_id))
    except Exception:
        pass
    return {"message": "Delivery deleted successfully"}
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc


# Document endpoints
@router.get("/{supplier_id}/documents/", response_model=DocumentListResponse)
async def get_supplier_documents(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents for a supplier"""
    service = SupplierService(db)
    documents = service.get_documents(supplier_id)
    
    return DocumentListResponse(
        items=documents,
        total=len(documents),
        page=1,
        size=len(documents),
        pages=1
    )


@router.get("/documents/{document_id}", response_model=SupplierDocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID"""
    service = SupplierService(db)
    document = service.get_document(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.post("/{supplier_id}/documents/", response_model=SupplierDocumentResponse)
async def create_document(
    supplier_id: int,
    document_type: str = Query(..., description="Document type"),
    document_name: str = Query(..., description="Document name"),
    document_number: Optional[str] = Query(None, description="Document number"),
    issue_date: Optional[datetime] = Query(None, description="Issue date"),
    expiry_date: Optional[datetime] = Query(None, description="Expiry date"),
    issuing_authority: Optional[str] = Query(None, description="Issuing authority"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for a supplier"""
    service = SupplierService(db)
    
    # Check if supplier exists
    supplier = service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/supplier_documents"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = f"{upload_dir}/{supplier_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    document_data = SupplierDocumentCreate(
        supplier_id=supplier_id,
        document_type=document_type,
        document_name=document_name,
        document_number=document_number,
        issue_date=issue_date,
        expiry_date=expiry_date,
        issuing_authority=issuing_authority,
        file_path=file_path,
        file_size=file.size,
        file_type=file.content_type,
        original_filename=file.filename
    )
    
    document = service.create_document(document_data, current_user.id)
    try:
        audit_event(db, current_user.id, "supplier_document_uploaded", "suppliers", str(document.id), {"supplier_id": supplier_id})
    except Exception:
        pass
    return document


@router.put("/documents/{document_id}", response_model=SupplierDocumentResponse)
async def update_document(
    document_id: int,
    document_data: SupplierDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document"""
    service = SupplierService(db)
    document = service.update_document(document_id, document_data)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        audit_event(db, current_user.id, "supplier_document_updated", "suppliers", str(document.id))
    except Exception:
        pass
    return document


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete document"""
    service = SupplierService(db)
    success = service.delete_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        audit_event(db, current_user.id, "supplier_document_deleted", "suppliers", str(document_id))
    except Exception:
        pass
    return {"message": "Document deleted successfully"}



@router.get("/alerts/expired-certificates")
async def get_expired_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get expired supplier certificates"""
    service = SupplierService(db)
    expired_certs = service.check_expired_certificates()
    return {"expired_certificates": expired_certs}


@router.get("/alerts/overdue-evaluations")
async def get_overdue_evaluations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get suppliers with overdue evaluations"""
    service = SupplierService(db)
    overdue_evaluations = service.get_overdue_evaluations()
    return {"overdue_evaluations": overdue_evaluations}


# Inspection Checklist endpoints
@router.get("/deliveries/{delivery_id}/checklists/", response_model=List[InspectionChecklistResponse])
async def get_delivery_checklists(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inspection checklists for a delivery"""
    service = SupplierService(db)
    checklists = service.get_inspection_checklists(delivery_id)
    return checklists


@router.get("/checklists/{checklist_id}", response_model=InspectionChecklistResponse)
async def get_inspection_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inspection checklist by ID"""
    service = SupplierService(db)
    checklist = service.get_inspection_checklist(checklist_id)
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection checklist not found"
        )
    
    return checklist


@router.post("/deliveries/{delivery_id}/checklists/", response_model=InspectionChecklistResponse)
async def create_inspection_checklist(
    delivery_id: int,
    checklist_data: InspectionChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new inspection checklist"""
    service = SupplierService(db)
    
    # Check if delivery exists
    delivery = service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    checklist_data.delivery_id = delivery_id
    checklist = service.create_inspection_checklist(checklist_data, current_user.id)
    try:
        audit_event(db, current_user.id, "inspection_checklist_created", "suppliers", str(checklist.id), {"delivery_id": delivery_id})
    except Exception:
        pass
    return checklist


@router.put("/checklists/{checklist_id}", response_model=InspectionChecklistResponse)
async def update_inspection_checklist(
    checklist_id: int,
    checklist_data: InspectionChecklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update inspection checklist"""
    service = SupplierService(db)
    checklist = service.update_inspection_checklist(checklist_id, checklist_data)
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection checklist not found"
        )
    
    try:
        audit_event(db, current_user.id, "inspection_checklist_updated", "suppliers", str(checklist.id))
    except Exception:
        pass
    return checklist


@router.delete("/checklists/{checklist_id}")
async def delete_inspection_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete inspection checklist"""
    service = SupplierService(db)
    success = service.delete_inspection_checklist(checklist_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection checklist not found"
        )
    
    try:
        audit_event(db, current_user.id, "inspection_checklist_deleted", "suppliers", str(checklist_id))
    except Exception:
        pass
    return {"message": "Inspection checklist deleted successfully"}


@router.get("/checklists/{checklist_id}/items/", response_model=List[InspectionChecklistItemResponse])
async def get_checklist_items(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get checklist items for a checklist"""
    service = SupplierService(db)
    items = service.get_checklist_items(checklist_id)
    return items


@router.post("/checklists/{checklist_id}/items/", response_model=InspectionChecklistItemResponse)
async def create_checklist_item(
    checklist_id: int,
    item_data: InspectionChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new checklist item"""
    service = SupplierService(db)
    
    # Check if checklist exists
    checklist = service.get_inspection_checklist(checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection checklist not found"
        )
    
    item_data.checklist_id = checklist_id
    item = service.create_checklist_item(item_data)
    return item


@router.put("/checklist-items/{item_id}", response_model=InspectionChecklistItemResponse)
async def update_checklist_item(
    item_id: int,
    item_data: InspectionChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update checklist item"""
    service = SupplierService(db)
    item = service.update_checklist_item(item_id, item_data, current_user.id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found"
        )
    
    return item


@router.post("/checklists/{checklist_id}/complete", response_model=InspectionChecklistResponse)
async def complete_inspection_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete an inspection checklist"""
    service = SupplierService(db)
    checklist = service.complete_checklist(checklist_id, current_user.id)
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection checklist not found"
        )
    
    return checklist

# end of checklist endpoints
# Noncompliant delivery alert endpoints
@router.get("/alerts/noncompliant-deliveries")
async def get_noncompliant_delivery_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts for noncompliant deliveries"""
    service = SupplierService(db)
    alerts = service.get_noncompliant_delivery_alerts()
    return {"noncompliant_deliveries": alerts}


@router.get("/alerts/delivery-summary")
async def get_delivery_alert_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary of delivery alerts"""
    service = SupplierService(db)
    summary = service.get_delivery_alert_summary()
    return summary 


# New lightweight analytics and stats endpoints (dict response_model to avoid strict validation issues)

@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_performance_analytics(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    supplier_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(SupplierEvaluation)
    if supplier_id:
        q = q.filter(SupplierEvaluation.supplier_id == supplier_id)
    if date_from:
        q = q.filter(SupplierEvaluation.evaluation_date >= date_from)
    if date_to:
        q = q.filter(SupplierEvaluation.evaluation_date <= date_to)

    evals = q.all()
    # Build daily average trend in Python to avoid backend-specific SQL
    from collections import defaultdict
    bucket: Dict[str, List[float]] = defaultdict(list)
    for e in evals:
        try:
            d = e.evaluation_date.date().isoformat()
        except Exception:
            continue
        bucket[d].append(e.overall_score or 0.0)
    trends = [
        {"date": d, "average_score": round(sum(scores) / max(1, len(scores)), 2)}
        for d, scores in sorted(bucket.items())
    ]

    # Category performance
    cat_rows = db.query(Supplier.category, func.avg(Supplier.overall_score)).group_by(Supplier.category).all()
    category_performance = [
        {"category": (cat.value if hasattr(cat, 'value') else str(cat) or 'unknown'), "average_score": float(avg or 0.0)}
        for cat, avg in cat_rows
    ]

    # Risk distribution
    risk_rows = db.query(Supplier.risk_level, func.count(Supplier.id)).group_by(Supplier.risk_level).all()
    risk_distribution = [
        {"risk_level": str(risk or 'unknown'), "count": int(count)} for risk, count in risk_rows
    ]

    return {
        "trends": trends,
        "category_performance": category_performance,
        "risk_distribution": risk_distribution,
    }


@router.get("/analytics/risk-assessment", response_model=Dict[str, Any])
async def get_risk_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    risk_rows = db.query(Supplier.risk_level, func.count(Supplier.id)).group_by(Supplier.risk_level).all()
    total = sum(int(c) for _, c in risk_rows) or 1
    risk_matrix = [
        {"risk_level": str(r or 'unknown'), "count": int(c), "percentage": round(100.0 * int(c) / total, 2)}
        for r, c in risk_rows
    ]
    high_risk = db.query(Supplier).filter(Supplier.risk_level == "high").limit(10).all()
    # Simple monthly trend using Python
    from collections import Counter
    cnt = Counter()
    for s in db.query(Supplier).filter(Supplier.risk_level == "high").all():
        try:
            key = s.created_at.strftime('%Y-%m')
            cnt[key] += 1
        except Exception:
            continue
    risk_trends = [{"date": k, "high_risk_count": v} for k, v in sorted(cnt.items())]
    return {
        "risk_matrix": risk_matrix,
        "high_risk_suppliers": [
            {"id": s.id, "name": s.name, "risk_level": s.risk_level} for s in high_risk
        ],
        "risk_trends": risk_trends,
    }


@router.get("/alerts", response_model=Dict[str, Any])
async def get_alerts(
    severity: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SupplierService(db)
    delivery_alerts = service.get_noncompliant_delivery_alerts()
    overdue = service.get_overdue_evaluations()

    items: List[Dict[str, Any]] = []
    for a in delivery_alerts:
        created_at = a.get("alert_date") or datetime.utcnow()
        title = (f"Noncompliant delivery {a.get('delivery_number', '')}").strip() or "Noncompliant delivery"
        description = f"{a.get('supplier_name', '')} - {a.get('material_name', '')} ({a.get('inspection_status', 'n/a')})"
        items.append({
            "id": f"delivery-{a.get('delivery_id')}",
            "type": "quality_alert",
            "severity": "high" if a.get("days_since_delivery", 0) > 7 else "medium",
            "title": title,
            "description": description,
            "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
            "resolved": False,
        })
    for o in overdue:
        created_at = o.get("next_evaluation_date") or datetime.utcnow()
        title = (f"Overdue evaluation: {o.get('supplier_name', '')}").strip() or "Overdue evaluation"
        description = f"Due {o.get('next_evaluation_date')}"
        items.append({
            "id": f"overdue-{o.get('supplier_id')}",
            "type": "overdue_evaluation",
            "severity": "medium",
            "title": title,
            "description": description,
            "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
            "resolved": False,
        })

    if severity:
        items = [i for i in items if i.get("severity") == severity]
    if type:
        items = [i for i in items if i.get("type") == type]
    if resolved is not None:
        items = [i for i in items if i.get("resolved") == resolved]

    total = len(items)
    start = (page - 1) * size
    end = start + size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }


@router.get("/stats", response_model=Dict[str, Any])
async def get_supplier_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SupplierService(db)
    dash = service.get_dashboard_stats()
    return {
        "total_suppliers": dash.get("total_suppliers", 0),
        "active_suppliers": dash.get("active_suppliers", 0),
        "pending_approval": int(db.query(Supplier).filter(Supplier.status == SupplierStatus.PENDING_APPROVAL).count()),
        "suspended_suppliers": int(db.query(Supplier).filter(Supplier.status == SupplierStatus.SUSPENDED).count()),
        "blacklisted_suppliers": int(db.query(Supplier).filter(Supplier.status == SupplierStatus.BLACKLISTED).count()),
        "overdue_evaluations": dash.get("overdue_evaluations", 0),
        "upcoming_evaluations": 0,
        "recent_deliveries": len(dash.get("recent_deliveries", [])),
        "quality_alerts": len(service.get_noncompliant_delivery_alerts()),
    }


@router.get("/materials/stats", response_model=Dict[str, Any])
async def get_material_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = int(db.query(Material).count())
    approved = int(db.query(Material).filter(Material.approval_status == "approved").count())
    pending = int(db.query(Material).filter(Material.approval_status == "pending").count())
    rejected = int(db.query(Material).filter(Material.approval_status == "rejected").count())
    by_category = db.query(Material.category, func.count(Material.id)).group_by(Material.category).all()
    by_supplier = db.query(Supplier.name, func.count(Material.id)).join(Supplier, Supplier.id == Material.supplier_id).group_by(Supplier.name).all()
    return {
        "total_materials": total,
        "approved_materials": approved,
        "pending_materials": pending,
        "rejected_materials": rejected,
        "materials_by_category": [{"category": str(cat or "unknown"), "count": int(cnt)} for cat, cnt in by_category],
        "materials_by_supplier": [{"supplier_name": name, "count": int(cnt)} for name, cnt in by_supplier],
    }


@router.get("/evaluations/stats", response_model=Dict[str, Any])
async def get_evaluation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = int(db.query(SupplierEvaluation).count())
    completed = int(db.query(SupplierEvaluation).filter(SupplierEvaluation.status == EvaluationStatus.COMPLETED).count())
    in_progress = int(db.query(SupplierEvaluation).filter(SupplierEvaluation.status == EvaluationStatus.IN_PROGRESS).count())
    scheduled = int(db.query(SupplierEvaluation).filter(SupplierEvaluation.status == EvaluationStatus.PENDING).count())
    overdue = int(db.query(Supplier).filter(and_(Supplier.next_evaluation_date < datetime.now(), Supplier.next_evaluation_date.isnot(None))).count())
    avg = float(db.query(func.avg(SupplierEvaluation.overall_score)).scalar() or 0.0)

    # Monthly histogram in Python
    from collections import Counter
    rows = db.query(SupplierEvaluation).all()
    c = Counter()
    for ev in rows:
        try:
            key = ev.evaluation_date.strftime('%Y-%m')
            c[key] += 1
        except Exception:
            continue
    by_month = [{"month": k, "count": v, "average_score": avg} for k, v in sorted(c.items())]

    return {
        "total_evaluations": total,
        "completed_evaluations": completed,
        "in_progress_evaluations": in_progress,
        "scheduled_evaluations": scheduled,
        "overdue_evaluations": overdue,
        "average_score": avg,
        "evaluations_by_month": by_month,
    }