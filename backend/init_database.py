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
from app.models.equipment import Equipment, MaintenancePlan, MaintenanceWorkOrder, CalibrationPlan, CalibrationRecord
from app.models.management_review import ManagementReview, ReviewAgendaItem, ReviewAction
from app.models.risk import RiskRegisterItem, RiskAction
from app.models.food_safety_objectives import FoodSafetyObjective
from app.models.complaint import Complaint, ComplaintCommunication, ComplaintInvestigation
from app.models.allergen_label import ProductAllergenAssessment, LabelTemplate, LabelTemplateVersion, LabelTemplateApproval
from app.models.nonconformance import NonConformance, RootCauseAnalysis, CAPAAction, CAPAVerification, NonConformanceAttachment

def init_database():
    """Create all database tables"""
    print("🚀 Initializing database...")
    
    try:
        # Create all tables (ensure all model modules imported above)
        Base.metadata.create_all(bind=engine)
        print("✅ All database tables created successfully!")
        
        # List created tables (robust across dialects)
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print("📋 Created {} tables:".format(len(tables)))
            for table in sorted(tables):
                print("  - {}".format(table))
        except Exception as ie:
            print("(info) Skipping table list due to inspector error: {}".format(ie))
            
    except Exception as e:
        print("❌ Error creating database tables: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    init_database() 