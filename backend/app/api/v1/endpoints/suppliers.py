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

router = APIRouter()


# Supplier endpoints
@router.get("/", response_model=SupplierListResponse)
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
    
    return SupplierListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier by ID"""
    service = SupplierService(db)
    supplier = service.get_supplier(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return supplier


@router.post("/", response_model=SupplierResponse)
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
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
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
    
    return supplier


@router.delete("/{supplier_id}")
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
    
    return {"message": "Supplier deleted successfully"}


@router.post("/bulk/action")
async def bulk_update_suppliers(
    action_data: BulkSupplierAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update suppliers"""
    service = SupplierService(db)
    result = service.bulk_update_suppliers(action_data)
    
    return {
        "message": f"Updated {result['updated_count']} out of {result['total_requested']} suppliers",
        "updated_count": result["updated_count"],
        "total_requested": result["total_requested"]
    }


# Material endpoints
@router.get("/materials/", response_model=MaterialListResponse)
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
    
    return MaterialListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/materials/{material_id}", response_model=MaterialResponse)
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
    
    return material


@router.post("/materials/", response_model=MaterialResponse)
async def create_material(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new material"""
    service = SupplierService(db)
    
    # Check if material code already exists
    existing_material = service.db.query(service.db.query(Material).filter(
        Material.material_code == material_data.material_code
    ).exists()).scalar()
    
    if existing_material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material code already exists"
        )
    
    material = service.create_material(material_data, current_user.id)
    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse)
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
    
    return material


@router.delete("/materials/{material_id}")
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
    
    return {"message": "Material deleted successfully"}


@router.post("/materials/bulk/action")
async def bulk_update_materials(
    action_data: BulkMaterialAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update materials"""
    service = SupplierService(db)
    result = service.bulk_update_materials(action_data)
    
    return {
        "message": f"Updated {result['updated_count']} out of {result['total_requested']} materials",
        "updated_count": result["updated_count"],
        "total_requested": result["total_requested"]
    }


# Evaluation endpoints
@router.get("/evaluations/", response_model=EvaluationListResponse)
async def get_evaluations(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get evaluations with filtering and pagination"""
    filter_params = EvaluationFilter(
        supplier_id=supplier_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size
    )
    
    service = SupplierService(db)
    result = service.get_evaluations(filter_params)
    
    return EvaluationListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/evaluations/{evaluation_id}", response_model=SupplierEvaluationResponse)
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
    
    return evaluation


@router.post("/evaluations/", response_model=SupplierEvaluationResponse)
async def create_evaluation(
    evaluation_data: SupplierEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new supplier evaluation"""
    service = SupplierService(db)
    evaluation = service.create_evaluation(evaluation_data, current_user.id)
    return evaluation


@router.put("/evaluations/{evaluation_id}", response_model=SupplierEvaluationResponse)
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
    
    return evaluation


@router.delete("/evaluations/{evaluation_id}")
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
    
    return {"message": "Evaluation deleted successfully"}


# Delivery endpoints
@router.get("/deliveries/", response_model=DeliveryListResponse)
async def get_deliveries(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    material_id: Optional[int] = Query(None, description="Filter by material"),
    inspection_status: Optional[str] = Query(None, description="Filter by inspection status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get deliveries with filtering and pagination"""
    filter_params = DeliveryFilter(
        supplier_id=supplier_id,
        material_id=material_id,
        inspection_status=inspection_status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size
    )
    
    service = SupplierService(db)
    result = service.get_deliveries(filter_params)
    
    return DeliveryListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


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
    """Create a new incoming delivery"""
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


@router.delete("/deliveries/{delivery_id}")
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
    
    return {"message": "Delivery deleted successfully"}


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


# Dashboard endpoints
@router.get("/dashboard/stats", response_model=SupplierDashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier dashboard statistics"""
    service = SupplierService(db)
    stats = service.get_dashboard_stats()
    return stats


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