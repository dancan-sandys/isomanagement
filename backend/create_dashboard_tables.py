#!/usr/bin/env python3
"""
Create dashboard tables for ISO 22000 FSMS Master Dashboard
Run this script to add the new dashboard-related tables to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.database import get_db, engine
from app.models.dashboard import (
    DashboardConfiguration, KPIDefinition, KPIValue, DashboardWidget,
    DashboardAlert, ScheduledReport, DashboardAuditLog, Department
)
from app.core.database import Base

def create_dashboard_tables():
    """Create all dashboard-related tables"""
    print("Creating dashboard tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine, tables=[
            DashboardConfiguration.__table__,
            KPIDefinition.__table__,
            KPIValue.__table__,
            DashboardWidget.__table__,
            DashboardAlert.__table__,
            ScheduledReport.__table__,
            DashboardAuditLog.__table__,
            Department.__table__
        ])
        
        print("✅ Dashboard tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating dashboard tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up ISO 22000 FSMS Master Dashboard Database...")
    
    # Create tables
    if create_dashboard_tables():
        print("\n🎉 Dashboard database setup completed successfully!")
    else:
        print("\n❌ Dashboard setup failed")