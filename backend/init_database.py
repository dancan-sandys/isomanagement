#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to initialize the database with all tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models.user import User, UserSession, PasswordReset
from app.models.document import Document, DocumentVersion, DocumentApproval, DocumentChangeLog, DocumentTemplate
from app.models.haccp import Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog
from app.models.prp import PRPProgram, PRPChecklist, PRPChecklistItem, PRPTemplate, PRPSchedule
from app.models.supplier import Supplier, SupplierDocument, SupplierEvaluation
from app.models.traceability import Batch, TraceabilityLink, RecallEntry
from app.models.notification import Notification
from app.models.rbac import Role, Permission, UserPermission

def init_database():
    """Create all database tables"""
    print("🚀 Initializing database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All database tables created successfully!")
        
        # List created tables
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        print(f"📋 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 