#!/usr/bin/env python3
"""
Script to check document status in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.document import Document, DocumentApproval

def check_document_status():
    """Check document status in the database"""
    db = SessionLocal()
    try:
        # Get all documents
        documents = db.query(Document).all()
        print(f"Found {len(documents)} documents:")
        print("-" * 80)
        
        for doc in documents:
            # Get approval steps for this document
            approvals = db.query(DocumentApproval).filter(DocumentApproval.document_id == doc.id).all()
            pending_approvals = [a for a in approvals if a.status == "pending"]
            
            print(f"Document ID: {doc.id}")
            print(f"Title: {doc.title}")
            print(f"Status: {doc.status}")
            print(f"Total approval steps: {len(approvals)}")
            print(f"Pending approval steps: {len(pending_approvals)}")
            print(f"Approved steps: {len([a for a in approvals if a.status == 'approved'])}")
            print(f"Rejected steps: {len([a for a in approvals if a.status == 'rejected'])}")
            
            # Check if all steps are approved
            if len(approvals) > 0 and len(pending_approvals) == 0:
                print("✅ All approval steps completed - document should be APPROVED")
                if doc.status != "approved":
                    print(f"❌ BUT document status is '{doc.status}' instead of 'approved'")
                else:
                    print("✅ Document status is correctly set to 'approved'")
            elif len(approvals) > 0:
                print(f"⏳ Still has {len(pending_approvals)} pending approval steps")
            else:
                print("📝 No approval steps defined")
            
            print("-" * 80)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_document_status()
