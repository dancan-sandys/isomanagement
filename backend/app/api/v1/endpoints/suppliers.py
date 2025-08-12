from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.supplier_service import SupplierService
from app.models.supplier import Supplier, Material
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
    
    return ResponseModel(
        success=True,
        message="Supplier created successfully",
        data=supplier
    )


# Material endpoints (must come before /{supplier_id} route)
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
    
    return ResponseModel(
        success=True,
        message="Evaluation deleted successfully",
        data={"message": "Evaluation deleted successfully"}
    )


# Delivery endpoints (must come before /{supplier_id} route)
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
    
    return {"message": "Document deleted successfully"}


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