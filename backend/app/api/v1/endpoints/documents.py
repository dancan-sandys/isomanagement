import os
import shutil
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, String
import uuid
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from datetime import datetime, timedelta
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.haccp import Product
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.document import (
    Document, DocumentType, DocumentStatus, DocumentCategory, DocumentVersion,
    DocumentChangeLog, DocumentTemplate, DocumentApproval,
    DocumentTemplateVersion, DocumentTemplateApproval
)
from app.schemas.common import ResponseModel, PaginatedResponse
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentFilter, DocumentResponse, 
    DocumentVersionResponse, DocumentChangeLogResponse, DocumentApprovalResponse,
    DocumentTemplateCreate, DocumentTemplateResponse, BulkDocumentAction, DocumentStats,
    DocumentApprovalCreate, DocumentTemplateVersionCreate, DocumentTemplateVersionResponse, DocumentTemplateApprovalCreate
)
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
from app.core.config import settings
from app.core.security import verify_password, require_permission
from app.utils.audit import audit_event

router = APIRouter()
# Helper to safely extract enum values even if DB stores raw strings
def enum_value(v):
    try:
        return v.value if hasattr(v, "value") else (str(v) if v is not None else None)
    except Exception:
        return None

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Document Templates endpoints (must come before /{document_id} routes)
@router.get("/templates/")
async def get_document_templates(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    document_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document templates
    """
    try:
        query = db.query(DocumentTemplate).filter(DocumentTemplate.is_active == True)
        
        # Handle document_type filter
        if document_type:
            try:
                doc_type_enum = DocumentType(document_type)
                query = query.filter(DocumentTemplate.document_type == doc_type_enum)
            except ValueError:
                # Invalid document type, return empty result
                pass
        
        # Handle category filter
        if category:
            try:
                category_enum = DocumentCategory(category)
                query = query.filter(DocumentTemplate.category == category_enum)
            except ValueError:
                # Invalid category, return empty result
                pass
        
        total = query.count()
        templates = query.order_by(DocumentTemplate.name).offset((page - 1) * size).limit(size).all()
        
        items = []
        for template in templates:
            # Get creator name
            creator = db.query(User).filter(User.id == template.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            items.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "document_type": template.document_type.value,
                "category": template.category.value,
                "template_file_path": template.template_file_path,
                "template_content": template.template_content,
                "is_active": template.is_active,
                "created_by": creator_name,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            })
        
        return ResponseModel(
            success=True,
            message="Document templates retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document templates: {str(e)}"
        )


@router.post("/templates/")
async def create_document_template(
    template_data: DocumentTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document template
    """
    try:
        # Check permissions
        if not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create templates"
            )
        
        template = DocumentTemplate(
            name=template_data.name,
            description=template_data.description,
            document_type=template_data.document_type,
            category=template_data.category,
            template_content=template_data.template_content,
            created_by=current_user.id
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return ResponseModel(
            success=True,
            message="Document template created successfully",
            data={"id": template.id}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document template: {str(e)}"
        )


@router.get("/templates/{template_id}")
async def get_document_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document template
    """
    try:
        template = db.query(DocumentTemplate).filter(
            DocumentTemplate.id == template_id,
            DocumentTemplate.is_active == True
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document template not found"
            )
        
        # Get creator name
        creator = db.query(User).filter(User.id == template.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        return ResponseModel(
            success=True,
            message="Document template retrieved successfully",
            data={
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "document_type": template.document_type.value,
                "category": template.category.value,
                "template_file_path": template.template_file_path,
                "template_content": template.template_content,
                "is_active": template.is_active,
                "created_by": creator_name,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document template: {str(e)}"
        )


@router.delete("/templates/{template_id}")
async def delete_document_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document template (soft delete by setting is_active to False)
    """
    try:
        # Check permissions
        if not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete templates"
            )
        
        template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document template not found"
            )
        
        template.is_active = False
        template.updated_at = datetime.utcnow()
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Document template deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document template: {str(e)}"
        )


@router.post("/templates/{template_id}/versions")
async def create_template_version(
    template_id: int,
    payload: DocumentTemplateVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id, DocumentTemplate.is_active == True).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # determine next version
        last = db.query(DocumentTemplateVersion).filter(DocumentTemplateVersion.template_id == template_id).order_by(desc(DocumentTemplateVersion.created_at)).first()
        next_version = "1.0"
        if last:
            import re
            m = re.match(r"^(\d+)\.(\d+)$", last.version_number or "")
            if m:
                next_version = f"{int(m.group(1))}.{int(m.group(2))+1}"

        row = DocumentTemplateVersion(
            template_id=template_id,
            version_number=next_version,
            template_content=payload.template_content or template.template_content,
            change_description=payload.change_description,
            created_by=current_user.id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

        audit_event(db, current_user.id, "template_version_created", "documents", str(template_id), {"version": next_version})
        return ResponseModel(success=True, message="Template version created", data={"id": row.id, "version": next_version})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template version: {str(e)}")


@router.get("/templates/{template_id}/versions")
async def list_template_versions(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        rows = db.query(DocumentTemplateVersion).filter(DocumentTemplateVersion.template_id == template_id).order_by(desc(DocumentTemplateVersion.created_at)).all()
        items = [
            {
                "id": r.id,
                "version_number": r.version_number,
                "change_description": r.change_description,
                "approved_by": r.approved_by,
                "approved_at": r.approved_at.isoformat() if r.approved_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
        return ResponseModel(success=True, message="Template versions retrieved", data={"items": items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list template versions: {str(e)}")


@router.post("/templates/{template_id}/approvals")
async def create_template_approvals(
    template_id: int,
    approvals: List[DocumentTemplateApprovalCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id, DocumentTemplate.is_active == True).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Clear existing pending approvals
        db.query(DocumentTemplateApproval).filter(DocumentTemplateApproval.template_id == template_id, DocumentTemplateApproval.status == "pending").delete()

        seen = set()
        for ap in approvals:
            if ap.approval_order in seen:
                raise HTTPException(status_code=400, detail="Duplicate approval_order")
            seen.add(ap.approval_order)
            db.add(DocumentTemplateApproval(
                template_id=template_id,
                approver_id=ap.approver_id,
                approval_order=ap.approval_order,
                status="pending",
                comments=ap.comments,
            ))
        db.commit()
        audit_event(db, current_user.id, "template_submitted_for_approval", "documents", str(template_id), {"approvals": len(approvals)})
        return ResponseModel(success=True, message="Template submitted for approval")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template approvals: {str(e)}")


def _template_gate_ready(db: Session, template_id: int, order: int) -> bool:
    return db.query(DocumentTemplateApproval).filter(DocumentTemplateApproval.template_id == template_id, DocumentTemplateApproval.approval_order < order, DocumentTemplateApproval.status != "approved").count() == 0


@router.post("/templates/{template_id}/approvals/{approval_id}/approve")
async def approve_template(
    template_id: int,
    approval_id: int,
    comments: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        step = db.query(DocumentTemplateApproval).filter(DocumentTemplateApproval.id == approval_id, DocumentTemplateApproval.template_id == template_id).first()
        if not step:
            raise HTTPException(status_code=404, detail="Template approval step not found")
        if step.approver_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned approver")
        if step.status != "pending":
            raise HTTPException(status_code=400, detail="Approval step not pending")
        if not _template_gate_ready(db, template_id, step.approval_order):
            raise HTTPException(status_code=400, detail="Previous steps must be approved")

        if password and not verify_password(password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password for e-signature")

        step.status = "approved"
        step.comments = comments
        step.approved_at = datetime.utcnow()
        db.commit()

        # Set latest version approved_by when chain completes
        remaining = db.query(DocumentTemplateApproval).filter(DocumentTemplateApproval.template_id == template_id, DocumentTemplateApproval.status == "pending").count()
        if remaining == 0:
            latest = db.query(DocumentTemplateVersion).filter(DocumentTemplateVersion.template_id == template_id).order_by(desc(DocumentTemplateVersion.created_at)).first()
            if latest:
                latest.approved_by = current_user.id
                latest.approved_at = datetime.utcnow()
                db.commit()

        audit_event(db, current_user.id, "template_approval_step_approved", "documents", str(template_id), {"approval_id": approval_id})
        return ResponseModel(success=True, message="Approval recorded", data={"remaining": remaining})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve template: {str(e)}")


@router.post("/templates/{template_id}/approvals/{approval_id}/reject")
async def reject_template(
    template_id: int,
    approval_id: int,
    comments: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        step = db.query(DocumentTemplateApproval).filter(DocumentTemplateApproval.id == approval_id, DocumentTemplateApproval.template_id == template_id).first()
        if not step:
            raise HTTPException(status_code=404, detail="Template approval step not found")
        if step.approver_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned approver")
        if step.status != "pending":
            raise HTTPException(status_code=400, detail="Approval step not pending")

        step.status = "rejected"
        step.comments = comments
        step.approved_at = datetime.utcnow()
        db.commit()

        audit_event(db, current_user.id, "template_approval_step_rejected", "documents", str(template_id), {"approval_id": approval_id})
        return ResponseModel(success=True, message="Rejection recorded")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject template: {str(e)}")
def calculate_next_version(current_version: str) -> str:
    """Calculate the next version number based on current version"""
    if not current_version:
        return "1.0"
    
    # Parse version number (e.g., "1.0", "1.1", "2.0")
    match = re.match(r'^(\d+)\.(\d+)$', current_version)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        return f"{major}.{minor + 1}"
    
    # If version format is unexpected, start with 1.0
    return "1.0"


def create_change_log(db: Session, document_id: int, change_type: str, 
                     change_description: str, old_version: str = None, 
                     new_version: str = None, changed_by: int = None):
    """Create a change log entry for document changes"""
    change_log = DocumentChangeLog(
        document_id=document_id,
        change_type=change_type,
        change_description=change_description,
        old_version=old_version,
        new_version=new_version,
        changed_by=changed_by
    )
    db.add(change_log)
    db.commit()


# -------- Export helpers --------
def _export_documents_pdf(items: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 40
    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Documents Export")
    y -= 20
    c.setFont("Helvetica", 10)
    for doc in items:
        line = f"#{doc['id']} | {doc.get('document_number','')} | {doc.get('title','')} | {doc.get('status','')} | v{doc.get('version','')}"
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)
        c.drawString(x, y, line[:110])
        y -= 14
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _export_documents_xlsx(items: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Documents"
    headers = ["ID", "Number", "Title", "Status", "Version", "Category", "Type", "Department", "Created By", "Created At"]
    ws.append(headers)
    for doc in items:
        ws.append([
            doc.get("id"),
            doc.get("document_number"),
            doc.get("title"),
            doc.get("status"),
            doc.get("version"),
            doc.get("category"),
            doc.get("document_type"),
            doc.get("department"),
            doc.get("created_by"),
            doc.get("created_at"),
        ])
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream.read()


def _export_rows_pdf(title: str, rows: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 40
    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title)
    y -= 20
    c.setFont("Helvetica", 10)
    for row in rows:
        line = " | ".join(str(row.get(k, "")) for k in row.keys())
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)
        c.drawString(x, y, line[:110])
        y -= 14
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _export_rows_xlsx(sheet_name: str, headers: list, rows: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h, None) for h in headers])
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream.read()


@router.get("/")
async def get_documents(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    doc_status: Optional[str] = Query(None, alias="status"),
    document_type: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    product_line: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    review_date_from: Optional[datetime] = Query(None),
    review_date_to: Optional[datetime] = Query(None),
    keywords: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of documents with advanced filtering
    """
    try:
        # Normalize enum query params to accept case-insensitive values
        cat_enum = None
        status_enum = None
        type_enum = None
        try:
            if isinstance(category, str) and category.strip():
                cat_enum = DocumentCategory(category.strip().lower())
        except Exception:
            cat_enum = None
        try:
            if isinstance(doc_status, str) and doc_status.strip():
                status_enum = DocumentStatus(doc_status.strip().lower())
        except Exception:
            status_enum = None
        try:
            if isinstance(document_type, str) and document_type.strip():
                type_enum = DocumentType(document_type.strip().lower())
        except Exception:
            type_enum = None

        # Create filter object
        filters = DocumentFilter(
            search=search,
            category=cat_enum,
            status=status_enum,
            document_type=type_enum,
            department=department,
            product_line=product_line,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
            review_date_from=review_date_from,
            review_date_to=review_date_to,
            keywords=keywords
        )
        
        # Use document service
        document_service = DocumentService(db)
        result = document_service.get_documents(filters, page, size)
        
        # Convert to response format (supports rows as ORM objects or dicts)
        def getv(o, key):
            if isinstance(o, dict):
                return o.get(key)
            return getattr(o, key, None)

        items = []
        for doc in result["items"]:
            created_by_id = getv(doc, "created_by")
            creator_name = None
            if created_by_id is not None:
                try:
                    creator = db.query(User).filter(User.id == created_by_id).first()
                    creator_name = (creator.full_name if creator else None)
                except Exception:
                    creator_name = None
            
            # Parse applicable_products
            applicable_products = None
            ap = getv(doc, "applicable_products")
            if ap:
                if isinstance(ap, str):
                    try:
                        applicable_products = json.loads(ap)
                    except Exception:
                        applicable_products = None
                else:
                    applicable_products = ap

            created_at = getv(doc, "created_at")
            updated_at = getv(doc, "updated_at")
            
            items.append({
                "id": getv(doc, "id"),
                "document_number": getv(doc, "document_number"),
                "title": getv(doc, "title"),
                "description": getv(doc, "description"),
                "document_type": enum_value(getv(doc, "document_type")),
                "category": enum_value(getv(doc, "category")),
                "status": enum_value(getv(doc, "status")),
                "version": getv(doc, "version"),
                "file_path": getv(doc, "file_path"),
                "file_size": getv(doc, "file_size"),
                "file_type": getv(doc, "file_type"),
                "original_filename": getv(doc, "original_filename"),
                "department": getv(doc, "department"),
                "product_line": getv(doc, "product_line"),
                "applicable_products": applicable_products,
                "keywords": getv(doc, "keywords"),
                "created_by": creator_name or created_by_id,
                "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
                "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
            })
        
        return ResponseModel(
            success=True,
            message="Documents retrieved successfully",
            data={
                "items": items,
                "total": result["total"],
                "page": result["page"],
                "size": result["size"],
                "pages": result["pages"]
            }
        )
        
    except Exception as e:
        from starlette import status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific document with its details
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get creator name
        creator = db.query(User).filter(User.id == document.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        # Get approver name if exists
        approver_name = None
        if document.approved_by:
            approver = db.query(User).filter(User.id == document.approved_by).first()
            approver_name = approver.full_name if approver else "Unknown"
        
        return ResponseModel(
            success=True,
            message="Document retrieved successfully",
            data={
                "id": document.id,
                "document_number": document.document_number,
                "title": document.title,
                "description": document.description,
                "document_type": enum_value(document.document_type),
                "category": enum_value(document.category),
                "status": enum_value(document.status),
                "version": document.version,
                "file_path": document.file_path,
                "file_size": document.file_size,
                "file_type": document.file_type,
                "original_filename": document.original_filename,
                "department": document.department,
                "created_by": creator_name,
                "approved_by": approver_name,
                "approved_at": document.approved_at.isoformat() if document.approved_at else None,
                "effective_date": document.effective_date.isoformat() if document.effective_date else None,
                "review_date": document.review_date.isoformat() if document.review_date else None,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "updated_at": document.updated_at.isoformat() if document.updated_at else None,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.post("/")
async def create_document(
    title: str = Form(...),
    document_number: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: str = Form(...),
    category: str = Form(...),
    department: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document
    """
    try:
        # Check if document number already exists
        existing_doc = db.query(Document).filter(Document.document_number == document_number).first()
        if existing_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document number already exists"
            )
        
        # Handle file upload
        file_path = None
        file_size = None
        file_type = None
        original_filename = None
        
        if file:
            # Validate file type
            allowed_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png']
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Save via storage service (local filesystem)
            storage = StorageService(base_upload_dir="uploads")
            file_path, file_size, file_type, original_filename = storage.save_upload(file, subdir="documents")
        
        # Create document
        document = Document(
            document_number=document_number,
            title=title,
            description=description,
            document_type=DocumentType(document_type),
            category=DocumentCategory(category),
            status=DocumentStatus.DRAFT,
            version="1.0",
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            original_filename=original_filename,
            department=department,
            created_by=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create initial version record
        if file_path:
            version = DocumentVersion(
                document_id=document.id,
                version_number="1.0",
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                original_filename=original_filename,
                change_description="Initial version",
                change_reason="Document creation",
                created_by=current_user.id
            )
            db.add(version)
            db.commit()
        
        # Create change log
        create_change_log(
            db=db,
            document_id=document.id,
            change_type="created",
            change_description="Document created",
            new_version="1.0",
            changed_by=current_user.id
        )
        
        resp = ResponseModel(
            success=True,
            message="Document created successfully",
            data={"id": document.id}
        )
        try:
            audit_event(db, current_user.id, "document_created", "documents", str(document.id), {"document_number": document.document_number})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}"
        )


@router.put("/{document_id}")
async def update_document(
    document_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing document (metadata only, use version endpoint for file changes)
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        old_version = document.version
        
        # Update fields
        if title is not None:
            document.title = title
        if description is not None:
            document.description = description
        if document_type is not None:
            document.document_type = DocumentType(document_type)
        if category is not None:
            document.category = DocumentCategory(category)
        if status is not None:
            document.status = DocumentStatus(status)
        if department is not None:
            document.department = department
        
        document.updated_at = datetime.utcnow()
        db.commit()
        
        # Create change log for metadata update
        create_change_log(
            db=db,
            document_id=document.id,
            change_type="updated",
            change_description="Document metadata updated",
            old_version=old_version,
            new_version=document.version,
            changed_by=current_user.id
        )
        
        resp = ResponseModel(
            success=True,
            message="Document updated successfully"
        )
        try:
            audit_event(db, current_user.id, "document_updated", "documents", str(document.id))
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}"
        )


@router.post("/{document_id}/versions")
async def create_new_version(
    document_id: int,
    change_description: str = Form(...),
    change_reason: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new version of a document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Validate file type
        allowed_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Calculate new version number
        old_version = document.version
        new_version = calculate_next_version(old_version)
        
        # Save new file via storage service (local filesystem)
        storage = StorageService(base_upload_dir="uploads")
        file_path, file_size, file_type, original_filename = storage.save_upload(file, subdir="documents")
        
        # Create new version record
        version = DocumentVersion(
            document_id=document.id,
            version_number=new_version,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            original_filename=original_filename,
            change_description=change_description,
            change_reason=change_reason,
            created_by=current_user.id
        )
        db.add(version)
        
        # Update main document
        document.version = new_version
        document.file_path = file_path
        document.file_size = file_size
        document.file_type = file_type
        document.original_filename = original_filename
        document.status = DocumentStatus.DRAFT  # Reset to draft for new version
        document.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Create change log
        create_change_log(
            db=db,
            document_id=document.id,
            change_type="version_created",
            change_description=f"New version {new_version} created: {change_description}",
            old_version=old_version,
            new_version=new_version,
            changed_by=current_user.id
        )
        
        resp = ResponseModel(
            success=True,
            message=f"New version {new_version} created successfully",
            data={
                "document_id": document.id,
                "new_version": new_version,
                "version_id": version.id
            }
        )
        try:
            audit_event(db, current_user.id, "document_version_created", "documents", str(document.id), {"new_version": new_version})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create new version: {str(e)}"
        )


@router.get("/{document_id}/versions")
async def get_version_history(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get version history for a document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get all versions
        versions = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(desc(DocumentVersion.created_at)).all()
        
        items = []
        for version in versions:
            # Get creator name
            creator = db.query(User).filter(User.id == version.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            # Get approver name if exists
            approver_name = None
            if version.approved_by:
                approver = db.query(User).filter(User.id == version.approved_by).first()
                approver_name = approver.full_name if approver else "Unknown"
            
            items.append({
                "id": version.id,
                "version_number": version.version_number,
                "file_path": version.file_path,
                "file_size": version.file_size,
                "file_type": version.file_type,
                "original_filename": version.original_filename,
                "change_description": version.change_description,
                "change_reason": version.change_reason,
                "created_by": creator_name,
                "approved_by": approver_name,
                "approved_at": version.approved_at.isoformat() if version.approved_at else None,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "is_current": version.version_number == document.version
            })
        
        return ResponseModel(
            success=True,
            message="Version history retrieved successfully",
            data={
                "document_id": document.id,
                "current_version": document.version,
                "versions": items
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve version history: {str(e)}"
        )


@router.get("/{document_id}/versions/{version_id}")
async def get_specific_version(
    document_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific version of a document
    """
    try:
        version = db.query(DocumentVersion).filter(
            DocumentVersion.id == version_id,
            DocumentVersion.document_id == document_id
        ).first()
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        # Get creator name
        creator = db.query(User).filter(User.id == version.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        # Get approver name if exists
        approver_name = None
        if version.approved_by:
            approver = db.query(User).filter(User.id == version.approved_by).first()
            approver_name = approver.full_name if approver else "Unknown"
        
        return ResponseModel(
            success=True,
            message="Version retrieved successfully",
            data={
                "id": version.id,
                "version_number": version.version_number,
                "file_path": version.file_path,
                "file_size": version.file_size,
                "file_type": version.file_type,
                "original_filename": version.original_filename,
                "change_description": version.change_description,
                "change_reason": version.change_reason,
                "created_by": creator_name,
                "approved_by": approver_name,
                "approved_at": version.approved_at.isoformat() if version.approved_at else None,
                "created_at": version.created_at.isoformat() if version.created_at else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve version: {str(e)}"
        )


@router.post("/{document_id}/versions/{version_id}/approve")
async def approve_version(
    document_id: int,
    version_id: int,
    comments: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a specific version of a document
    """
    try:
        version = db.query(DocumentVersion).filter(
            DocumentVersion.id == version_id,
            DocumentVersion.document_id == document_id
        ).first()
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        # Check if user has approval permissions
        if not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve documents"
            )

        # Optional e-signature by password verification in dev
        if password:
            if not verify_password(password, current_user.hashed_password):
                raise HTTPException(status_code=400, detail="Invalid password for e-signature")
        
        # Approve the version
        version.approved_by = current_user.id
        version.approved_at = datetime.utcnow()
        
        # Update main document status
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.APPROVED
            document.approved_by = current_user.id
            document.approved_at = datetime.utcnow()
            document.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Create change log
        create_change_log(
            db=db,
            document_id=document_id,
            change_type="approved",
            change_description=f"Version {version.version_number} approved",
            new_version=version.version_number,
            changed_by=current_user.id
        )
        
        resp = ResponseModel(
            success=True,
            message=f"Version {version.version_number} approved successfully"
        )
        try:
            audit_event(db, current_user.id, "document_version_approved", "documents", str(document_id), {"version_id": version_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve version: {str(e)}"
        )


@router.get("/{document_id}/change-log")
async def get_change_log(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get change log for a document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get change logs
        change_logs = db.query(DocumentChangeLog).filter(
            DocumentChangeLog.document_id == document_id
        ).order_by(desc(DocumentChangeLog.created_at)).all()
        
        items = []
        for log in change_logs:
            # Get user name
            user = db.query(User).filter(User.id == log.changed_by).first()
            user_name = user.full_name if user else "Unknown"
            
            items.append({
                "id": log.id,
                "change_type": log.change_type,
                "change_description": log.change_description,
                "old_version": log.old_version,
                "new_version": log.new_version,
                "changed_by": user_name,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Change log retrieved successfully",
            data={
                "document_id": document_id,
                "changes": items
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve change log: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check permissions
        if not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete documents"
            )
        
        # Delete all version files
        versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).all()
        for version in versions:
            if version.file_path and os.path.exists(version.file_path):
                os.remove(version.file_path)
        
        # Delete main document file
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database (cascade will handle related records)
        db.delete(document)
        db.commit()
        
        resp = ResponseModel(
            success=True,
            message="Document deleted successfully"
        )
        try:
            audit_event(db, current_user.id, "document_deleted", "documents", str(document_id))
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download the current version of a document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if not document.file_path or not os.path.exists(document.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found"
            )
        
        return FileResponse(
            path=document.file_path,
            filename=document.original_filename or f"document_{document_id}.pdf",
            media_type=document.file_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download document: {str(e)}"
        )


@router.get("/{document_id}/versions/{version_id}/download")
async def download_version(
    document_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download a specific version of a document
    """
    try:
        version = db.query(DocumentVersion).filter(
            DocumentVersion.id == version_id,
            DocumentVersion.document_id == document_id
        ).first()
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        if not version.file_path or not os.path.exists(version.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version file not found"
            )
        
        return FileResponse(
            path=version.file_path,
            filename=version.original_filename or f"document_v{version.version_number}.pdf",
            media_type=version.file_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download version: {str(e)}"
        )


@router.post("/{document_id}/upload")
async def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file for an existing document (creates new version)
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Validate file type
        allowed_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Calculate new version number
        old_version = document.version
        new_version = calculate_next_version(old_version)
        
        # Save file via storage service (local filesystem)
        storage = StorageService(base_upload_dir="uploads")
        file_path, file_size, file_type, original_filename = storage.save_upload(file, subdir="documents")
        
        # Create new version record
        version = DocumentVersion(
            document_id=document.id,
            version_number=new_version,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            original_filename=original_filename,
            change_description="File uploaded",
            change_reason="Document file update",
            created_by=current_user.id
        )
        db.add(version)
        
        # Update main document
        document.version = new_version
        document.file_path = file_path
        document.file_size = file_size
        document.file_type = file_type
        document.original_filename = original_filename
        document.status = DocumentStatus.DRAFT
        document.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Create change log
        create_change_log(
            db=db,
            document_id=document.id,
            change_type="file_uploaded",
            change_description=f"New file uploaded for version {new_version}",
            old_version=old_version,
            new_version=new_version,
            changed_by=current_user.id
        )
        
        resp = ResponseModel(
            success=True,
            message=f"File uploaded successfully. New version: {new_version}",
            data={
                "document_id": document.id,
                "new_version": new_version,
                "version_id": version.id
            }
        )
        try:
            audit_event(db, current_user.id, "document_file_uploaded", "documents", str(document.id), {"new_version": new_version})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/stats/overview")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document statistics and overview
    """
    try:
        document_service = DocumentService(db)
        stats = document_service.get_document_stats()
        
        return ResponseModel(
            success=True,
            message="Document statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document statistics: {str(e)}"
        )


@router.post("/bulk/status")
async def bulk_update_document_status(
    action: BulkDocumentAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk update document status (archive, obsolete, activate, etc.)
    """
    try:
        # Check permissions
        if not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for bulk operations"
            )
        
        document_service = DocumentService(db)
        
        # Map action to status
        status_mapping = {
            "archive": DocumentStatus.ARCHIVED,
            "obsolete": DocumentStatus.OBSOLETE,
            "activate": DocumentStatus.APPROVED,
            "delete": None  # Special case for deletion
        }
        
        if action.action == "delete":
            # Handle deletion
            deleted_count = 0
            for doc_id in action.document_ids:
                try:
                    if document_service.delete_document(doc_id):
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting document {doc_id}: {str(e)}")
                    continue
            
            return ResponseModel(
                success=True,
                message=f"Successfully deleted {deleted_count} documents",
                data={"deleted_count": deleted_count}
            )
        else:
            # Handle status updates
            new_status = status_mapping.get(action.action)
            if not new_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid action"
                )
            
            updated_count = document_service.bulk_update_status(
                action.document_ids, 
                new_status, 
                action.reason or f"Bulk {action.action}", 
                current_user.id
            )
            
            return ResponseModel(
                success=True,
                message=f"Successfully updated {updated_count} documents",
                data={"updated_count": updated_count}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk operation: {str(e)}"
        )


@router.post("/maintenance/archive-obsolete")
async def archive_obsolete_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger archiving of obsolete documents
    """
    try:
        # Check permissions
        if not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for maintenance operations"
            )
        
        document_service = DocumentService(db)
        archived_count = document_service.archive_obsolete_documents()
        
        return ResponseModel(
            success=True,
            message=f"Successfully archived {archived_count} obsolete documents",
            data={"archived_count": archived_count}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to archive obsolete documents: {str(e)}"
        )


@router.get("/maintenance/expired")
async def get_expired_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get documents that need review (expired review dates)
    """
    try:
        document_service = DocumentService(db)
        expired_documents = document_service.check_expired_documents()
        
        items = []
        for doc in expired_documents:
            # Get creator name
            creator = db.query(User).filter(User.id == doc.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            items.append({
                "id": doc.id,
                "document_number": doc.document_number,
                "title": doc.title,
                "status": doc.status.value,
                "review_date": doc.review_date.isoformat() if doc.review_date else None,
                "created_by": creator_name,
                "days_overdue": (datetime.utcnow() - doc.review_date).days if doc.review_date else 0
            })
        
        return ResponseModel(
            success=True,
            message="Expired documents retrieved successfully",
            data={
                "expired_documents": items,
                "count": len(items)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve expired documents: {str(e)}"
        )


# -------- Document ↔ Products Linking --------

@router.get("/{document_id}/products")
async def get_document_products(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    ids = []
    if doc.applicable_products:
        try:
            ids = json.loads(doc.applicable_products)
        except Exception:
            ids = []
    products = []
    if ids:
        rows = db.query(Product).filter(Product.id.in_(ids)).all()
        products = [{"id": p.id, "product_code": p.product_code, "name": p.name} for p in rows]
    return ResponseModel(success=True, message="Linked products retrieved", data={"items": products})


@router.post("/{document_id}/products")
async def link_document_products(
    document_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product_ids = payload.get("product_ids", [])
    if not isinstance(product_ids, list):
        raise HTTPException(status_code=400, detail="product_ids must be a list")
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Validate existence
    if product_ids:
        exists = db.query(Product.id).filter(Product.id.in_(product_ids)).all()
        exist_ids = {e[0] for e in exists}
        missing = [i for i in product_ids if i not in exist_ids]
        if missing:
            raise HTTPException(status_code=400, detail=f"Unknown product ids: {missing}")
    current = []
    if doc.applicable_products:
        try:
            current = json.loads(doc.applicable_products)
        except Exception:
            current = []
    merged = sorted(list(set(current).union(set(product_ids))))
    doc.applicable_products = json.dumps(merged) if merged else None
    doc.updated_at = datetime.utcnow()
    db.commit()
    create_change_log(db, document_id, "linked_products", f"Linked products: {merged}", changed_by=current_user.id)
    try:
        audit_event(db, current_user.id, "document_products_linked", "documents", str(document_id), {"product_ids": merged})
    except Exception:
        pass
    return ResponseModel(success=True, message="Products linked", data={"product_ids": merged})


@router.delete("/{document_id}/products/{product_id}")
async def unlink_document_product(
    document_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    current = []
    if doc.applicable_products:
        try:
            current = json.loads(doc.applicable_products)
        except Exception:
            current = []
    if product_id in current:
        current.remove(product_id)
    doc.applicable_products = json.dumps(current) if current else None
    doc.updated_at = datetime.utcnow()
    db.commit()
    create_change_log(db, document_id, "unlinked_product", f"Unlinked product: {product_id}", changed_by=current_user.id)
    try:
        audit_event(db, current_user.id, "document_product_unlinked", "documents", str(document_id), {"product_id": product_id})
    except Exception:
        pass
    return ResponseModel(success=True, message="Product unlinked", data={"product_ids": current})


# -------- Status transitions with reasons --------

def _set_status_with_reason(db: Session, doc: Document, new_status: DocumentStatus, reason: Optional[str], user_id: int):
    old = doc.status
    doc.status = new_status
    doc.updated_at = datetime.utcnow()
    db.commit()
    create_change_log(db, doc.id, "status_changed", f"{old.value} -> {new_status.value}. Reason: {reason or 'n/a'}", new_version=doc.version, changed_by=user_id)


@router.post("/{document_id}/status/obsolete")
async def mark_obsolete(
    document_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    reason = payload.get("reason")
    _set_status_with_reason(db, doc, DocumentStatus.OBSOLETE, reason, current_user.id)
    try:
        audit_event(db, current_user.id, "document_marked_obsolete", "documents", str(document_id), {"reason": reason})
    except Exception:
        pass
    return ResponseModel(success=True, message="Document marked obsolete")


@router.post("/{document_id}/status/archive")
async def mark_archived(
    document_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    reason = payload.get("reason")
    _set_status_with_reason(db, doc, DocumentStatus.ARCHIVED, reason, current_user.id)
    try:
        audit_event(db, current_user.id, "document_archived", "documents", str(document_id), {"reason": reason})
    except Exception:
        pass
    return ResponseModel(success=True, message="Document archived")


@router.post("/{document_id}/status/activate")
async def mark_active(
    document_id: int,
    payload: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    reason = (payload or {}).get("reason") if payload else None
    _set_status_with_reason(db, doc, DocumentStatus.APPROVED, reason, current_user.id)
    try:
        audit_event(db, current_user.id, "document_activated", "documents", str(document_id), {"reason": reason})
    except Exception:
        pass
    return ResponseModel(success=True, message="Document activated")


# -------- Controlled distribution --------

@router.post("/{document_id}/distribute")
async def distribute_document(
    document_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    user_ids = payload.get("user_ids", []) or []
    departments = payload.get("departments", []) or []
    notes = payload.get("notes")
    notified = 0
    distribution_rows = []
    for uid in user_ids:
        try:
            # Record distribution row
            from app.models.document import DocumentDistribution
            dist = DocumentDistribution(document_id=doc.id, user_id=uid, copy_number=None, notes=notes)
            db.add(dist)
            distribution_rows.append(dist)
            n = Notification(
                user_id=uid,
                title=f"Document Distributed: {doc.title}",
                message=f"You have been assigned document '{doc.title}' ({doc.document_number}).",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.DOCUMENT,
                notification_data={"document_id": doc.id, "document_number": doc.document_number, "notes": notes},
            )
            db.add(n)
            notified += 1
        except Exception:
            continue
    db.commit()
    create_change_log(db, doc.id, "distributed", f"Distributed to users: {user_ids}, depts: {departments}. Notes: {notes}", changed_by=current_user.id)
    try:
        audit_event(db, current_user.id, "document_distributed", "documents", str(document_id), {"user_ids": user_ids, "departments": departments})
    except Exception:
        pass
    return ResponseModel(success=True, message=f"Distribution recorded (notified {notified} users)")


@router.post("/{document_id}/distribution/{user_id}/acknowledge")
async def acknowledge_distribution(
    document_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id and (not current_user.role or current_user.role.name not in ["System Administrator", "QA Manager"]):
        raise HTTPException(status_code=403, detail="Not permitted to acknowledge for this user")
    from app.models.document import DocumentDistribution
    row = db.query(DocumentDistribution).filter(DocumentDistribution.document_id == document_id, DocumentDistribution.user_id == user_id).order_by(desc(DocumentDistribution.distributed_at)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Distribution record not found")
    row.acknowledged_at = datetime.utcnow()
    db.commit()
    try:
        audit_event(db, current_user.id, "document_acknowledged", "documents", str(document_id), {"user_id": user_id})
    except Exception:
        pass
    return ResponseModel(success=True, message="Acknowledgement recorded")

# -------- Export Endpoints --------

@router.post("/export")
async def export_documents(
    format: str = Query("pdf", pattern="^(pdf|xlsx)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export current documents snapshot to PDF or XLSX."""
    try:
        # Reuse the listing query with defaults
        document_service = DocumentService(db)
        result = document_service.get_documents(DocumentFilter(), 1, 1000)
        items = []
        for doc in result["items"]:
            creator = db.query(User).filter(User.id == doc.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            items.append({
                "id": doc.id,
                "document_number": doc.document_number,
                "title": doc.title,
                "document_type": doc.document_type.value if doc.document_type else None,
                "category": doc.category.value if doc.category else None,
                "status": doc.status.value if doc.status else None,
                "version": doc.version,
                "department": doc.department,
                "created_by": creator_name,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
            })

        if format == "pdf":
            content = _export_documents_pdf(items)
            filename = f"documents_export.pdf"
            media = "application/pdf"
        else:
            content = _export_documents_xlsx(items)
            filename = f"documents_export.xlsx"
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        try:
            audit_event(db, current_user.id, "documents_exported", "documents", None, {"format": format, "count": len(items)})
        except Exception:
            pass

        return StreamingResponse(io.BytesIO(content), media_type=media, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export documents: {str(e)}")


@router.get("/{document_id}/change-log/export")
async def export_change_log(
    document_id: int,
    format: str = Query("pdf", pattern="^(pdf|xlsx)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export change log for a document."""
    try:
        logs = db.query(DocumentChangeLog).filter(DocumentChangeLog.document_id == document_id).order_by(desc(DocumentChangeLog.created_at)).all()
        rows = [
            {
                "id": log.id,
                "change_type": log.change_type,
                "description": log.change_description,
                "old_version": log.old_version,
                "new_version": log.new_version,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
        if format == "pdf":
            content = _export_rows_pdf("Document Change Log", rows)
            filename = f"document_{document_id}_changelog.pdf"
            media = "application/pdf"
        else:
            headers = ["id", "change_type", "description", "old_version", "new_version", "created_at"]
            content = _export_rows_xlsx("ChangeLog", headers, rows)
            filename = f"document_{document_id}_changelog.xlsx"
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        try:
            audit_event(db, current_user.id, "document_changelog_exported", "documents", str(document_id), {"format": format, "count": len(rows)})
        except Exception:
            pass

        return StreamingResponse(io.BytesIO(content), media_type=media, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export change log: {str(e)}")


@router.get("/{document_id}/versions/export")
async def export_version_history(
    document_id: int,
    format: str = Query("pdf", pattern="^(pdf|xlsx)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export version history for a document."""
    try:
        versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).order_by(desc(DocumentVersion.created_at)).all()
        rows = [
            {
                "id": v.id,
                "version": v.version_number,
                "filename": v.original_filename,
                "file_type": v.file_type,
                "file_size": v.file_size,
                "approved_by": v.approved_by,
                "approved_at": v.approved_at.isoformat() if v.approved_at else None,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in versions
        ]
        if format == "pdf":
            content = _export_rows_pdf("Document Version History", rows)
            filename = f"document_{document_id}_versions.pdf"
            media = "application/pdf"
        else:
            headers = ["id", "version", "filename", "file_type", "file_size", "approved_by", "approved_at", "created_at"]
            content = _export_rows_xlsx("Versions", headers, rows)
            filename = f"document_{document_id}_versions.xlsx"
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        try:
            audit_event(db, current_user.id, "document_versions_exported", "documents", str(document_id), {"format": format, "count": len(rows)})
        except Exception:
            pass

        return StreamingResponse(io.BytesIO(content), media_type=media, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export version history: {str(e)}")

# --- Multi-step Approval Workflow Endpoints ---

@router.post("/{document_id}/approvals")
async def create_document_approvals(
    document_id: int,
    approvals: List[DocumentApprovalCreate],
    _perm: User = Depends(require_permission("DOCUMENTS:UPDATE")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a sequential approval chain for a document and move it to UNDER_REVIEW.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if document.status not in [DocumentStatus.DRAFT, DocumentStatus.UNDER_REVIEW]:
            raise HTTPException(status_code=400, detail="Document cannot be submitted for approval in current status")

        # Remove existing pending approvals (if resubmitting)
        db.query(DocumentApproval).filter(DocumentApproval.document_id == document_id, DocumentApproval.status == "pending").delete()

        # Insert new approvals
        seen_orders = set()
        created = []
        for ap in approvals:
            if ap.approval_order in seen_orders:
                raise HTTPException(status_code=400, detail="Duplicate approval_order in approvals")
            seen_orders.add(ap.approval_order)
            row = DocumentApproval(
                document_id=document_id,
                approver_id=ap.approver_id,
                approval_order=ap.approval_order,
                status="pending",
                comments=ap.comments,
            )
            db.add(row)
            created.append(row)

        # Transition document to UNDER_REVIEW
        document.status = DocumentStatus.UNDER_REVIEW
        document.updated_at = datetime.utcnow()
        db.commit()

        create_change_log(
            db=db,
            document_id=document.id,
            change_type="submitted",
            change_description=f"Document submitted for approval to {len(created)} approver(s)",
            new_version=document.version,
            changed_by=current_user.id,
        )

        try:
            audit_event(db, current_user.id, "document_submitted_for_approval", "documents", str(document_id), {"approvals": len(created)})
        except Exception:
            pass

        return ResponseModel(success=True, message="Approval chain created and document submitted", data={"approvals": len(created)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create approvals: {str(e)}")


@router.get("/approvals/pending")
async def get_my_pending_approvals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pending list shows:
      1) Approvals assigned to the current user with status 'pending'
      2) All documents whose status is anything other than 'approved'
    Combined and de-duplicated by document_id.
    """
    try:
        # 1) Approvals assigned to the current user
        approvals_q = db.query(DocumentApproval).filter(
            DocumentApproval.approver_id == current_user.id,
            DocumentApproval.status == "pending",
        )
        approval_rows = approvals_q.order_by(DocumentApproval.approval_order).all()

        items_by_doc: dict[int, dict] = {}
        for row in approval_rows:
            # Project only needed columns; cast enum to string to avoid invalid enum coercion
            doc_row = (
                db.query(
                    Document.id.label("id"),
                    Document.document_number.label("document_number"),
                    Document.title.label("title"),
                    Document.version.label("version"),
                    cast(Document.status, String).label("status"),
                    Document.created_at.label("created_at"),
                )
                .filter(Document.id == row.document_id)
                .first()
            )
            if not doc_row:
                continue
            items_by_doc[doc_row.id] = {
                "id": row.id,  # expose as 'id' for frontend convenience
                "approval_id": row.id,
                "document_id": doc_row.id,
                "document_number": doc_row.document_number,
                "title": doc_row.title,
                "version": doc_row.version,
                "approval_order": row.approval_order,
                "status": (doc_row.status or "pending"),
                "submitted_at": doc_row.created_at.isoformat() if getattr(doc_row.created_at, "isoformat", None) else doc_row.created_at,
            }

        # Pagination over combined results
        combined = list(items_by_doc.values())
        total = len(combined)
        start = (page - 1) * size
        end = start + size
        page_items = combined[start:end]

        return ResponseModel(
            success=True,
            message="Pending items retrieved",
            data={"items": page_items, "total": total, "page": page, "size": size},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pending items: {str(e)}")


def _is_current_approval_gate(db: Session, document_id: int, approval_order: int) -> bool:
    """Return True if all lower-order approvals are approved (or none exist)."""
    lower = db.query(DocumentApproval).filter(
        DocumentApproval.document_id == document_id,
        DocumentApproval.approval_order < approval_order,
        DocumentApproval.status != "approved",
    ).count()
    return lower == 0


@router.get("/{document_id}/approvals")
async def get_document_approvals(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return approval workflow for a document with current step resolved.

    Shape matches frontend expectations: { steps: [...], current_step, status }
    where steps[].status is one of: completed | in_progress | pending | rejected
    and steps[].assigned_to is a user-friendly name.
    """
    try:
        # Project only safe fields and cast enum to String to avoid enum coercion errors
        doc_row = (
            db.query(
                Document.id.label("id"),
                cast(Document.status, String).label("status"),
                Document.created_at.label("created_at"),
                Document.updated_at.label("updated_at"),
                Document.created_by.label("created_by"),
            )
            .filter(Document.id == document_id)
            .first()
        )
        if not doc_row:
            raise HTTPException(status_code=404, detail="Document not found")

        # Fetch approval rows ordered by approval_order
        approvals: list[DocumentApproval] = (
            db.query(DocumentApproval)
            .filter(DocumentApproval.document_id == document_id)
            .order_by(DocumentApproval.approval_order.asc())
            .all()
        )

        steps_db = []
        current_step_index = None
        for ap in approvals:
            approver = db.query(User).filter(User.id == ap.approver_id).first()
            approver_name = approver.full_name if approver and approver.full_name else (approver.username if approver else "")

            # Map DB status to workflow status
            if ap.status == "approved":
                mapped_status = "completed"
            elif ap.status == "rejected":
                mapped_status = "rejected"
            else:
                mapped_status = "pending"

            step = {
                "id": ap.id,
                "name": f"Step {ap.approval_order}",
                "status": mapped_status,
                "assigned_to": approver_name or "",
                "assigned_at": ap.created_at.isoformat() if ap.created_at else None,
                "completed_at": ap.approved_at.isoformat() if ap.approved_at else None,
                "comments": ap.comments,
                "order": ap.approval_order,
            }
            steps_db.append(step)

        # Determine current step = first step that is not completed and not rejected, with all prior completed
        for idx, step in enumerate(steps_db):
            if step["status"] in ("pending",):
                # verify gate
                if _is_current_approval_gate(db, document_id, step["order"]):
                    steps_db[idx]["status"] = "in_progress"
                    current_step_index = idx
                    break

        if current_step_index is None:
            # All steps completed or rejected; infer from document status string
            status_str = (doc_row.status or "").lower()
            if status_str == "approved":
                current_step_index = len(steps_db)
            else:
                # No approvals configured; treat as first step pending
                current_step_index = 0

        # Prepend a synthetic "Document Creation" step for visualization
        creator = db.query(User).filter(User.id == doc_row.created_by).first() if getattr(doc_row, "created_by", None) else None
        creator_name = creator.full_name if creator and creator.full_name else (creator.username if creator else "")
        creation_step = {
            "id": 0,
            "name": "Document Creation",
            "status": "completed",
            "assigned_to": creator_name,
            "assigned_at": doc_row.created_at.isoformat() if doc_row.created_at else None,
            "completed_at": doc_row.created_at.isoformat() if doc_row.created_at else None,
            "comments": None,
            "order": 0,
        }
        steps = [creation_step] + steps_db
        # Shift current step by +1 to account for the creation step
        current_step_display = (current_step_index + 2) if current_step_index is not None else (1 if steps else 0)

        data = {
            "document_id": document_id,
            "current_step": current_step_display,
            "status": (doc_row.status or "draft"),
            "created_at": doc_row.created_at.isoformat() if getattr(doc_row, "created_at", None) else None,
            "updated_at": doc_row.updated_at.isoformat() if getattr(doc_row, "updated_at", None) else None,
            "steps": steps,
        }
        return ResponseModel(success=True, message="Document approvals retrieved", data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve approvals: {str(e)}")

@router.post("/{document_id}/approvals/{approval_id}/approve")
async def approve_document_step(
    document_id: int,
    approval_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve current step; when last step is approved, document becomes APPROVED.
    """
    try:
        row = db.query(DocumentApproval).filter(DocumentApproval.id == approval_id, DocumentApproval.document_id == document_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Approval step not found")
        if row.approver_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned approver")
        if row.status != "pending":
            raise HTTPException(status_code=400, detail="Approval step is not pending")
        if not _is_current_approval_gate(db, document_id, row.approval_order):
            raise HTTPException(status_code=400, detail="Previous approval steps must be completed first")

        # Extract payload accepting either multipart form-data or JSON
        parsed_comments: Optional[str] = None
        parsed_password: Optional[str] = None
        try:
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("multipart/form-data"):
                form = await request.form()
                parsed_comments = form.get("comments")
                parsed_password = form.get("password")
            else:
                data = await request.json()
                if isinstance(data, dict):
                    parsed_comments = data.get("comments")
                    parsed_password = data.get("password")
        except Exception:
            # Ignore parsing errors; treat as no additional data
            pass

        # Optional e-signature verification
        if parsed_password:
            if not verify_password(parsed_password, current_user.hashed_password):
                raise HTTPException(status_code=400, detail="Invalid password for e-signature")

        # Approve step
        row.status = "approved"
        row.comments = parsed_comments
        row.approved_at = datetime.utcnow()
        db.commit()

        # If all steps approved -> approve document
        remaining = db.query(DocumentApproval).filter(DocumentApproval.document_id == document_id, DocumentApproval.status == "pending").count()
        document = db.query(Document).filter(Document.id == document_id).first()
        if document and remaining == 0:
            document.status = DocumentStatus.APPROVED
            document.approved_by = current_user.id
            document.approved_at = datetime.utcnow()
            document.updated_at = datetime.utcnow()
            db.commit()

            create_change_log(
                db=db,
                document_id=document_id,
                change_type="approved",
                change_description="All approval steps completed",
                new_version=document.version,
                changed_by=current_user.id,
            )

        try:
            audit_event(db, current_user.id, "document_approval_step_approved", "documents", str(document_id), {"approval_id": approval_id})
        except Exception:
            pass

        return ResponseModel(success=True, message="Approval recorded", data={"remaining": remaining})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve: {str(e)}")


@router.post("/{document_id}/approvals/{approval_id}/reject")
async def reject_document_step(
    document_id: int,
    approval_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject current step; document returns to DRAFT.
    """
    try:
        row = db.query(DocumentApproval).filter(DocumentApproval.id == approval_id, DocumentApproval.document_id == document_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Approval step not found")
        if row.approver_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned approver")
        if row.status != "pending":
            raise HTTPException(status_code=400, detail="Approval step is not pending")

        # Extract optional comments from either multipart or JSON
        parsed_comments: Optional[str] = None
        try:
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("multipart/form-data"):
                form = await request.form()
                parsed_comments = form.get("comments")
            else:
                data = await request.json()
                if isinstance(data, dict):
                    parsed_comments = data.get("comments")
        except Exception:
            parsed_comments = None

        row.status = "rejected"
        row.comments = parsed_comments
        row.approved_at = datetime.utcnow()
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.DRAFT
            document.updated_at = datetime.utcnow()
        db.commit()

        create_change_log(
            db=db,
            document_id=document_id,
            change_type="rejected",
            change_description="Approval step rejected",
            new_version=document.version if document else None,
            changed_by=current_user.id,
        )

        try:
            audit_event(db, current_user.id, "document_approval_step_rejected", "documents", str(document_id), {"approval_id": approval_id})
        except Exception:
            pass

        return ResponseModel(success=True, message="Rejection recorded")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject: {str(e)}")

