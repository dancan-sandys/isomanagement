#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to clear and recreate documents with correct enum values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def recreate_documents():
    """Clear existing documents and recreate them with correct enum values"""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("Clearing existing documents...")
            
            # Clear existing documents
            conn.execute(text("DELETE FROM documents"))
            conn.commit()
            
            print("Creating documents with correct enum values...")
            
            documents_data = [
                {
                    "document_number": "DOC-001",
                    "title": "ISO 22000 Food Safety Manual",
                    "description": "Main food safety management system manual",
                    "document_type": "manual",
                    "category": "general",
                    "version": "1.0",
                    "status": "approved",
                    "created_by": 1
                },
                {
                    "document_number": "DOC-002",
                    "title": "HACCP Plan Development SOP",
                    "description": "Standard operating procedure for HACCP plan development",
                    "document_type": "procedure",
                    "category": "haccp",
                    "version": "2.1",
                    "status": "approved",
                    "created_by": 2
                },
                {
                    "document_number": "DOC-003",
                    "title": "Daily Sanitation Checklist",
                    "description": "Daily cleaning and sanitation verification checklist",
                    "document_type": "checklist",
                    "category": "prp",
                    "version": "1.0",
                    "status": "draft",
                    "created_by": 3
                },
                {
                    "document_number": "DOC-004",
                    "title": "Supplier Evaluation Procedure",
                    "description": "Procedure for evaluating and approving suppliers",
                    "document_type": "procedure",
                    "category": "supplier",
                    "version": "1.2",
                    "status": "approved",
                    "created_by": 2
                },
                {
                    "document_number": "DOC-005",
                    "title": "Corrective Action Form",
                    "description": "Form for documenting corrective actions",
                    "document_type": "form",
                    "category": "quality",
                    "version": "1.0",
                    "status": "approved",
                    "created_by": 1
                },
                {
                    "document_number": "DOC-006",
                    "title": "Internal Audit Checklist",
                    "description": "Checklist for conducting internal audits",
                    "document_type": "checklist",
                    "category": "audit",
                    "version": "1.1",
                    "status": "draft",
                    "created_by": 2
                },
                {
                    "document_number": "DOC-007",
                    "title": "Training Record Template",
                    "description": "Template for recording employee training",
                    "document_type": "form",
                    "category": "training",
                    "version": "1.0",
                    "status": "approved",
                    "created_by": 1
                },
                {
                    "document_number": "DOC-008",
                    "title": "Equipment Maintenance Log",
                    "description": "Log for recording equipment maintenance activities",
                    "document_type": "record",
                    "category": "maintenance",
                    "version": "1.0",
                    "status": "approved",
                    "created_by": 3
                }
            ]
            
            for doc_data in documents_data:
                conn.execute(text("""
                    INSERT INTO documents (
                        document_number, title, description, document_type, category, 
                        version, status, created_by, created_at, updated_at
                    ) VALUES (
                        :document_number, :title, :description, :document_type, :category,
                        :version, :status, :created_by, datetime('now'), datetime('now')
                    )
                """), doc_data)
            
            conn.commit()
            print("✅ Documents recreated successfully!")
            print("\n📊 Expected stats:")
            print("   - Total Documents: 8")
            print("   - Pending Approval (DRAFT): 2")
            print("   - Approved Documents: 6")
            print("   - Expired Documents: 0")
            
    except Exception as e:
        print(f"❌ Error recreating documents: {e}")

if __name__ == "__main__":
    recreate_documents()
