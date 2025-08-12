#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify document stats calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.document_service import DocumentService

def test_document_stats():
    """Test document stats calculation"""
    
    db = SessionLocal()
    try:
        print("Testing document stats calculation...")
        
        # Get raw counts
        total_docs = db.query(Document).count()
        print(f"Total documents in database: {total_docs}")
        
        # Get documents by status
        draft_docs = db.query(Document).filter(Document.status == DocumentStatus.DRAFT).count()
        approved_docs = db.query(Document).filter(Document.status == DocumentStatus.APPROVED).count()
        obsolete_docs = db.query(Document).filter(Document.status == DocumentStatus.OBSOLETE).count()
        archived_docs = db.query(Document).filter(Document.status == DocumentStatus.ARCHIVED).count()
        
        print(f"Draft documents: {draft_docs}")
        print(f"Approved documents: {approved_docs}")
        print(f"Obsolete documents: {obsolete_docs}")
        print(f"Archived documents: {archived_docs}")
        
        # Test the service method
        document_service = DocumentService(db)
        stats = document_service.get_document_stats()
        
        print("\nStats from service:")
        print(f"total_documents: {stats['total_documents']}")
        print(f"documents_requiring_approval: {stats['documents_requiring_approval']}")
        print(f"expired_documents: {stats['expired_documents']}")
        print(f"documents_by_status: {stats['documents_by_status']}")
        
        # Show all documents
        print("\nAll documents:")
        documents = db.query(Document).all()
        for doc in documents:
            print(f"  {doc.document_number}: {doc.title} - Status: {doc.status.value}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_document_stats()
