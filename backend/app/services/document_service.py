import os
import json
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid

from app.models.document import (
    Document, DocumentVersion, DocumentApproval, DocumentChangeLog, 
    DocumentTemplate, DocumentStatus, DocumentType, DocumentCategory
)
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentFilter
from app.core.config import settings


class DocumentService:
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = "uploads/documents"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def create_document(self, document_data: DocumentCreate, created_by: int, 
                       file_path: Optional[str] = None, file_size: Optional[int] = None, 
                       file_type: Optional[str] = None, original_filename: Optional[str] = None) -> Document:
        """Create a new document"""
        
        # Check if document number already exists
        existing_doc = self.db.query(Document).filter(
            Document.document_number == document_data.document_number
        ).first()
        
        if existing_doc:
            raise ValueError("Document number already exists")
        
        # Convert applicable_products to JSON string
        applicable_products_json = None
        if document_data.applicable_products:
            applicable_products_json = json.dumps(document_data.applicable_products)
        
        document = Document(
            document_number=document_data.document_number,
            title=document_data.title,
            description=document_data.description,
            document_type=document_data.document_type,
            category=document_data.category,
            status=DocumentStatus.DRAFT,
            version="1.0",
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            original_filename=original_filename,
            department=document_data.department,
            product_line=document_data.product_line,
            applicable_products=applicable_products_json,
            keywords=document_data.keywords,
            effective_date=document_data.effective_date,
            review_date=document_data.review_date,
            created_by=created_by
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # Create initial version record if file exists
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
                created_by=created_by
            )
            self.db.add(version)
            self.db.commit()
        
        # Create change log
        self._create_change_log(
            document_id=document.id,
            change_type="created",
            change_description="Document created",
            new_version="1.0",
            changed_by=created_by
        )
        
        return document
    
    def update_document(self, document_id: int, document_data: DocumentUpdate, 
                       updated_by: int) -> Document:
        """Update document metadata"""
        
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")
        
        old_version = document.version
        
        # Update fields
        update_data = document_data.dict(exclude_unset=True)
        
        # Handle applicable_products conversion
        if 'applicable_products' in update_data:
            if update_data['applicable_products']:
                update_data['applicable_products'] = json.dumps(update_data['applicable_products'])
            else:
                update_data['applicable_products'] = None
        
        for field, value in update_data.items():
            setattr(document, field, value)
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        
        # Create change log
        self._create_change_log(
            document_id=document.id,
            change_type="updated",
            change_description="Document metadata updated",
            old_version=old_version,
            new_version=document.version,
            changed_by=updated_by
        )
        
        return document
    
    def create_new_version(self, document_id: int, change_description: str, 
                          change_reason: str, file_path: str, file_size: int,
                          file_type: str, original_filename: str, created_by: int) -> DocumentVersion:
        """Create a new version of a document"""
        
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")
        
        # Calculate new version number
        old_version = document.version
        new_version = self._calculate_next_version(old_version)
        
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
            created_by=created_by
        )
        self.db.add(version)
        
        # Update main document
        document.version = new_version
        document.file_path = file_path
        document.file_size = file_size
        document.file_type = file_type
        document.original_filename = original_filename
        document.status = DocumentStatus.DRAFT  # Reset to draft for new version
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(version)
        
        # Create change log
        self._create_change_log(
            document_id=document.id,
            change_type="version_created",
            change_description=f"New version {new_version} created: {change_description}",
            old_version=old_version,
            new_version=new_version,
            changed_by=created_by
        )
        
        return version
    
    def get_documents(self, filters: DocumentFilter, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Get documents with filtering and pagination.

        IMPORTANT: Use column casts to String for enum columns to avoid runtime errors when
        legacy rows contain uppercase or unexpected enum strings (e.g., 'FORM').
        """
        from sqlalchemy import cast, String

        # Base selectable with safe string casts for enum columns
        base_query = self.db.query(
            Document.id,
            Document.document_number,
            Document.title,
            Document.description,
            cast(Document.document_type, String).label("document_type"),
            cast(Document.category, String).label("category"),
            cast(Document.status, String).label("status"),
            Document.version,
            Document.file_path,
            Document.file_size,
            Document.file_type,
            Document.original_filename,
            Document.department,
            Document.product_line,
            Document.applicable_products,
            Document.keywords,
            Document.created_by,
            Document.created_at,
            Document.updated_at,
        )

        # Apply filters (convert enums to their values)
        if filters.search:
            search_term = f"%{filters.search}%"
            base_query = base_query.filter(
                or_(
                    Document.title.ilike(search_term),
                    Document.document_number.ilike(search_term),
                    Document.description.ilike(search_term),
                    Document.keywords.ilike(search_term),
                )
            )

        if filters.category:
            base_query = base_query.filter(cast(Document.category, String) == filters.category.value)

        if filters.status:
            base_query = base_query.filter(cast(Document.status, String) == filters.status.value)

        if filters.document_type:
            base_query = base_query.filter(cast(Document.document_type, String) == filters.document_type.value)

        if filters.department:
            base_query = base_query.filter(Document.department == filters.department)

        if filters.product_line:
            base_query = base_query.filter(Document.product_line == filters.product_line)

        if filters.created_by:
            base_query = base_query.filter(Document.created_by == filters.created_by)

        if filters.date_from:
            base_query = base_query.filter(Document.created_at >= filters.date_from)

        if filters.date_to:
            base_query = base_query.filter(Document.created_at <= filters.date_to)

        if filters.review_date_from:
            base_query = base_query.filter(Document.review_date >= filters.review_date_from)

        if filters.review_date_to:
            base_query = base_query.filter(Document.review_date <= filters.review_date_to)

        if filters.keywords:
            keywords_term = f"%{filters.keywords}%"
            base_query = base_query.filter(Document.keywords.ilike(keywords_term))

        # Count total (subquery for performance correctness)
        total = base_query.count()

        # Pagination and ordering
        rows = (
            base_query.order_by(desc(Document.updated_at))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        # Normalize enum strings to lowercase for consistency
        items: List[Dict[str, Any]] = []
        for r in rows:
            # r is a KeyedTuple
            items.append({
                "id": r.id,
                "document_number": r.document_number,
                "title": r.title,
                "description": r.description,
                "document_type": (r.document_type or "").lower() or None,
                "category": (r.category or "").lower() or None,
                "status": (r.status or "").lower() or None,
                "version": r.version,
                "file_path": r.file_path,
                "file_size": r.file_size,
                "file_type": r.file_type,
                "original_filename": r.original_filename,
                "department": r.department,
                "product_line": r.product_line,
                "applicable_products": r.applicable_products,
                "keywords": r.keywords,
                "created_by": r.created_by,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get document statistics"""
        
        # Helper to safely get enum values
        def to_value(val: Any) -> str:
            try:
                if val is None:
                    return "unknown"
                return val.value if hasattr(val, "value") else str(val)
            except Exception:
                return "unknown"
        
        # Total documents
        total_documents = self.db.query(Document).count()
        
        # Documents by status
        status_counts = self.db.query(
            Document.status, func.count(Document.id)
        ).group_by(Document.status).all()
        documents_by_status = {to_value(status): count for status, count in status_counts}
        
        # Documents by category
        category_counts = self.db.query(
            Document.category, func.count(Document.id)
        ).group_by(Document.category).all()
        documents_by_category = {to_value(category): count for category, count in category_counts}
        
        # Documents by type
        type_counts = self.db.query(
            Document.document_type, func.count(Document.id)
        ).group_by(Document.document_type).all()
        documents_by_type = {to_value(doc_type): count for doc_type, count in type_counts}
        
        # Pending reviews (documents with review_date in the past)
        pending_reviews = self.db.query(Document).filter(
            and_(
                Document.review_date < datetime.utcnow(),
                Document.status.in_([DocumentStatus.APPROVED, DocumentStatus.UNDER_REVIEW])
            )
        ).count()
        
        # Expired documents (obsolete or archived)
        expired_documents = self.db.query(Document).filter(
            Document.status.in_([DocumentStatus.OBSOLETE, DocumentStatus.ARCHIVED])
        ).count()
        
        # Documents requiring approval (draft status)
        documents_requiring_approval = self.db.query(Document).filter(
            Document.status == DocumentStatus.DRAFT
        ).count()
        
        return {
            "total_documents": total_documents,
            "documents_by_status": documents_by_status,
            "documents_by_category": documents_by_category,
            "documents_by_type": documents_by_type,
            "pending_reviews": pending_reviews,
            "expired_documents": expired_documents,
            "documents_requiring_approval": documents_requiring_approval
        }
    
    def archive_obsolete_documents(self) -> int:
        """Automatically archive obsolete documents"""
        
        # Find documents that are obsolete and haven't been archived yet
        obsolete_documents = self.db.query(Document).filter(
            Document.status == DocumentStatus.OBSOLETE
        ).all()
        
        archived_count = 0
        for document in obsolete_documents:
            document.status = DocumentStatus.ARCHIVED
            document.updated_at = datetime.utcnow()
            
            # Create change log
            self._create_change_log(
                document_id=document.id,
                change_type="archived",
                change_description="Document automatically archived",
                new_version=document.version,
                changed_by=1  # System user
            )
            
            archived_count += 1
        
        self.db.commit()
        return archived_count
    
    def check_expired_documents(self) -> List[Document]:
        """Check for documents that need review"""
        
        # Find documents with review_date in the past
        expired_documents = self.db.query(Document).filter(
            and_(
                Document.review_date < datetime.utcnow(),
                Document.status.in_([DocumentStatus.APPROVED, DocumentStatus.UNDER_REVIEW])
            )
        ).all()
        
        return expired_documents
    
    def bulk_update_status(self, document_ids: List[int], new_status: DocumentStatus, 
                          reason: str, updated_by: int) -> int:
        """Bulk update document status"""
        
        documents = self.db.query(Document).filter(Document.id.in_(document_ids)).all()
        
        updated_count = 0
        for document in documents:
            old_status = document.status
            document.status = new_status
            document.updated_at = datetime.utcnow()
            
            # Create change log
            self._create_change_log(
                document_id=document.id,
                change_type="status_changed",
                change_description=f"Status changed from {old_status.value} to {new_status.value}: {reason}",
                new_version=document.version,
                changed_by=updated_by
            )
            
            updated_count += 1
        
        self.db.commit()
        return updated_count
    
    def _calculate_next_version(self, current_version: str) -> str:
        """Calculate the next version number"""
        if not current_version:
            return "1.0"
        
        # Parse version number (e.g., "1.0", "1.1", "2.0")
        import re
        match = re.match(r'^(\d+)\.(\d+)$', current_version)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            return f"{major}.{minor + 1}"
        
        # If version format is unexpected, start with 1.0
        return "1.0"
    
    def _create_change_log(self, document_id: int, change_type: str, 
                          change_description: str, old_version: str = None, 
                          new_version: str = None, changed_by: int = None):
        """Create a change log entry"""
        
        change_log = DocumentChangeLog(
            document_id=document_id,
            change_type=change_type,
            change_description=change_description,
            old_version=old_version,
            new_version=new_version,
            changed_by=changed_by
        )
        self.db.add(change_log)
        self.db.commit()
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document and all its files"""
        
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        try:
            # Delete all version files
            versions = self.db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).all()
            
            for version in versions:
                if version.file_path and os.path.exists(version.file_path):
                    os.remove(version.file_path)
            
            # Delete main document file
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete related records first to avoid foreign key issues
            # Delete change logs
            self.db.query(DocumentChangeLog).filter(
                DocumentChangeLog.document_id == document_id
            ).delete()
            
            # Delete approvals
            self.db.query(DocumentApproval).filter(
                DocumentApproval.document_id == document_id
            ).delete()
            
            # Delete versions
            self.db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).delete()
            
            # Finally delete the document
            self.db.delete(document)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting document {document_id}: {str(e)}")
            return False 