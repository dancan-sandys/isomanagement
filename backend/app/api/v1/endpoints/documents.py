import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus, DocumentCategory
from app.schemas.common import ResponseModel, PaginatedResponse
from app.core.config import settings

router = APIRouter()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
async def get_documents(
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of documents with filtering
    """
    try:
        query = db.query(Document)
        
        # Apply filters
        if search:
            query = query.filter(
                Document.title.contains(search) |
                Document.document_number.contains(search) |
                Document.description.contains(search)
            )
        
        if category:
            query = query.filter(Document.category == category)
        
        if status:
            query = query.filter(Document.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        documents = query.order_by(desc(Document.updated_at)).offset((page - 1) * size).limit(size).all()
        
        # Convert to response format
        items = []
        for doc in documents:
            # Get creator name
            creator = db.query(User).filter(User.id == doc.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
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
                "created_by": creator_name,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
            })
        
        return ResponseModel(
            success=True,
            message="Documents retrieved successfully",
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
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
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
    Create a new document with optional file upload
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
    Update an existing document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
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
        
        # Handle file upload
        if file:
            # Delete old file if exists
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
            
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
            
            document.file_path = file_path
            document.file_size = os.path.getsize(file_path)
            document.file_type = file.content_type
            document.original_filename = file.filename
        
        document.updated_at = datetime.utcnow()
        db.commit()
        
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
        
        # Delete file if exists
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
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
    Download a document file
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
            document.file_path,
            filename=document.original_filename or f"document_{document_id}",
            media_type=document.file_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download document: {str(e)}"
        )


@router.post("/{document_id}/upload")
async def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file for an existing document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete old file if exists
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
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
        
        # Update document
        document.file_path = file_path
        document.file_size = os.path.getsize(file_path)
        document.file_type = file.content_type
        document.original_filename = file.filename
        document.updated_at = datetime.utcnow()
        
        db.commit()
        
        return ResponseModel(
            success=True,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        ) 