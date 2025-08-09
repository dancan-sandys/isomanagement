import os
import shutil
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid
from datetime import datetime, timedelta
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus, DocumentCategory, DocumentVersion, DocumentChangeLog, DocumentTemplate
from app.schemas.common import ResponseModel, PaginatedResponse
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentFilter, DocumentResponse, 
    DocumentVersionResponse, DocumentChangeLogResponse, DocumentApprovalResponse,
    DocumentTemplateCreate, DocumentTemplateResponse, BulkDocumentAction, DocumentStats
)
from app.services.document_service import DocumentService
from app.core.config import settings

router = APIRouter()

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


@router.get("/")
async def get_documents(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[DocumentCategory] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    document_type: Optional[DocumentType] = Query(None),
    department: Optional[str] = Query(None),
    product_line: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    review_date_from: Optional[datetime] = Query(None),
    review_date_to: Optional[datetime] = Query(None),
    keywords: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of documents with advanced filtering
    """
    try:
        # Create filter object
        filters = DocumentFilter(
            search=search,
            category=category,
            status=status,
            document_type=document_type,
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
        
        # Convert to response format
        items = []
        for doc in result["items"]:
            # Get creator name
            creator = db.query(User).filter(User.id == doc.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            # Parse applicable_products
            applicable_products = None
            if doc.applicable_products:
                try:
                    applicable_products = json.loads(doc.applicable_products)
                except:
                    applicable_products = None
            
            items.append({
                "id": doc.id,
                "document_number": doc.document_number,
                "title": doc.title,
                "description": doc.description,
                "document_type": doc.document_type.value if doc.document_type else None,
                "category": doc.category.value if doc.category else None,
                "status": doc.status.value if doc.status else None,
                "version": doc.version,
                "file_path": doc.file_path,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "original_filename": doc.original_filename,
                "department": doc.department,
                "product_line": doc.product_line,
                "applicable_products": applicable_products,
                "keywords": doc.keywords,
                "created_by": creator_name,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
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
                "document_type": document.document_type.value if document.document_type else None,
                "category": document.category.value if document.category else None,
                "status": document.status.value if document.status else None,
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
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            file_type = file.content_type
            original_filename = file.filename
        
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
        
        return ResponseModel(
            success=True,
            message="Document created successfully",
            data={"id": document.id}
        )
        
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
        
        return ResponseModel(
            success=True,
            message="Document updated successfully"
        )
        
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
        
        # Generate unique filename for new version
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save new file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        file_type = file.content_type
        original_filename = file.filename
        
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
        
        return ResponseModel(
            success=True,
            message=f"New version {new_version} created successfully",
            data={
                "document_id": document.id,
                "new_version": new_version,
                "version_id": version.id
            }
        )
        
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
        
        return ResponseModel(
            success=True,
            message=f"Version {version.version_number} approved successfully"
        )
        
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
        
        return ResponseModel(
            success=True,
            message="Document deleted successfully"
        )
        
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
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        file_type = file.content_type
        original_filename = file.filename
        
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
        
        return ResponseModel(
            success=True,
            message=f"File uploaded successfully. New version: {new_version}",
            data={
                "document_id": document.id,
                "new_version": new_version,
                "version_id": version.id
            }
        )
        
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


