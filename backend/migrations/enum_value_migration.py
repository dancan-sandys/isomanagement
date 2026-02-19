#!/usr/bin/env python3
"""
Database Migration Script for Enum Value Updates
ISO 22000 FSMS Platform

This script migrates existing enum values from uppercase to lowercase
to ensure consistency between backend and frontend.

IMPORTANT: Always backup your database before running this migration!
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine, SessionLocal
from app.models.nonconformance import NonConformance, NonConformanceSource, NonConformanceStatus
from app.models.haccp import RiskLevel, HazardType, CCPStatus
from app.models.user import UserStatus
from sqlalchemy import text

def backup_database():
    """Create a backup of the database before migration"""
    db_path = "iso22000_fsms.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"iso22000_fsms_backup_{timestamp}.db"
        
        # Copy the database file
        with open(db_path, 'rb') as source:
            with open(backup_path, 'wb') as target:
                target.write(source.read())
        
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    else:
        print("❌ Database file not found!")
        return None

def migrate_nonconformance_status():
    """Migrate NonConformance status values from uppercase to lowercase"""
    print("\n🔄 Migrating NonConformance status values...")
    
    db = SessionLocal()
    try:
        # Update status values
        status_mapping = {
            'OPEN': 'open',
            'UNDER_INVESTIGATION': 'under_investigation',
            'ROOT_CAUSE_IDENTIFIED': 'root_cause_identified',
            'CAPA_ASSIGNED': 'capa_assigned',
            'IN_PROGRESS': 'in_progress',
            'COMPLETED': 'completed',
            'VERIFIED': 'verified',
            'CLOSED': 'closed'
        }
        
        for old_status, new_status in status_mapping.items():
            result = db.execute(
                text("UPDATE non_conformances SET status = :new_status WHERE status = :old_status"),
                {"new_status": new_status, "old_status": old_status}
            )
            if result.rowcount > 0:
                print(f"  ✅ Updated {result.rowcount} records: {old_status} → {new_status}")
        
        # Update source values
        source_mapping = {
            'PRP': 'prp',
            'AUDIT': 'audit',
            'COMPLAINT': 'complaint',
            'PRODUCTION_DEVIATION': 'production_deviation',
            'SUPPLIER': 'supplier',
            'HACCP': 'haccp',
            'DOCUMENT': 'document',
            'INSPECTION': 'inspection',
            'OTHER': 'other'
        }
        
        for old_source, new_source in source_mapping.items():
            result = db.execute(
                text("UPDATE non_conformances SET source = :new_source WHERE source = :old_source"),
                {"new_source": new_source, "old_source": old_source}
            )
            if result.rowcount > 0:
                print(f"  ✅ Updated {result.rowcount} records: {old_source} → {new_source}")
        
        db.commit()
        print("✅ NonConformance migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during NonConformance migration: {e}")
        raise
    finally:
        db.close()

def migrate_haccp_enums():
    """Migrate HACCP enum values from uppercase to lowercase"""
    print("\n🔄 Migrating HACCP enum values...")
    
    db = SessionLocal()
    try:
        # Update RiskLevel values in HACCP-related tables
        risk_level_mapping = {
            'LOW': 'low',
            'MEDIUM': 'medium',
            'HIGH': 'high',
            'CRITICAL': 'critical'
        }
        
        # Update in products table (if risk_level column exists)
        try:
            for old_level, new_level in risk_level_mapping.items():
                result = db.execute(
                    text("UPDATE products SET risk_level = :new_level WHERE risk_level = :old_level"),
                    {"new_level": new_level, "old_level": old_level}
                )
                if result.rowcount > 0:
                    print(f"  ✅ Updated {result.rowcount} product records: {old_level} → {new_level}")
        except Exception as e:
            print(f"  ⚠️  Products table update skipped: {e}")
        
        # Update in ccp_points table (if status column exists)
        try:
            ccp_status_mapping = {
                'ACTIVE': 'active',
                'INACTIVE': 'inactive',
                'SUSPENDED': 'suspended'
            }
            
            for old_status, new_status in ccp_status_mapping.items():
                result = db.execute(
                    text("UPDATE ccp_points SET status = :new_status WHERE status = :old_status"),
                    {"new_status": new_status, "old_status": old_status}
                )
                if result.rowcount > 0:
                    print(f"  ✅ Updated {result.rowcount} CCP records: {old_status} → {new_status}")
        except Exception as e:
            print(f"  ⚠️  CCP points table update skipped: {e}")
        
        # Update in hazards table (if hazard_type column exists)
        try:
            hazard_type_mapping = {
                'BIOLOGICAL': 'biological',
                'CHEMICAL': 'chemical',
                'PHYSICAL': 'physical',
                'ALLERGEN': 'allergen'
            }
            
            for old_type, new_type in hazard_type_mapping.items():
                result = db.execute(
                    text("UPDATE hazards SET hazard_type = :new_type WHERE hazard_type = :old_type"),
                    {"new_type": new_type, "old_type": old_type}
                )
                if result.rowcount > 0:
                    print(f"  ✅ Updated {result.rowcount} hazard records: {old_type} → {new_type}")
        except Exception as e:
            print(f"  ⚠️  Hazards table update skipped: {e}")
        
        db.commit()
        print("✅ HACCP migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during HACCP migration: {e}")
        raise
    finally:
        db.close()

def migrate_user_status():
    """Migrate User status values from uppercase to lowercase"""
    print("\n🔄 Migrating User status values...")
    
    db = SessionLocal()
    try:
        # Update status values
        status_mapping = {
            'ACTIVE': 'active',
            'INACTIVE': 'inactive',
            'SUSPENDED': 'suspended',
            'PENDING_APPROVAL': 'pending_approval'
        }
        
        for old_status, new_status in status_mapping.items():
            result = db.execute(
                text("UPDATE users SET status = :new_status WHERE status = :old_status"),
                {"new_status": new_status, "old_status": old_status}
            )
            if result.rowcount > 0:
                print(f"  ✅ Updated {result.rowcount} user records: {old_status} → {new_status}")
        
        db.commit()
        print("✅ User status migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during User status migration: {e}")
        raise
    finally:
        db.close()

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    db = SessionLocal()
    try:
        # Check NonConformance status values
        result = db.execute(text("SELECT DISTINCT status FROM non_conformances"))
        statuses = [row[0] for row in result.fetchall()]
        
        invalid_statuses = [s for s in statuses if s and s.isupper()]
        if invalid_statuses:
            print(f"❌ Found invalid uppercase statuses: {invalid_statuses}")
        else:
            print("✅ All NonConformance statuses are lowercase")
        
        # Check NonConformance source values
        result = db.execute(text("SELECT DISTINCT source FROM non_conformances"))
        sources = [row[0] for row in result.fetchall()]
        
        invalid_sources = [s for s in sources if s and s.isupper()]
        if invalid_sources:
            print(f"❌ Found invalid uppercase sources: {invalid_sources}")
        else:
            print("✅ All NonConformance sources are lowercase")
        
        # Check HACCP-related values
        try:
            result = db.execute(text("SELECT DISTINCT risk_level FROM products WHERE risk_level IS NOT NULL"))
            risk_levels = [row[0] for row in result.fetchall()]
            
            invalid_levels = [l for l in risk_levels if l and l.isupper()]
            if invalid_levels:
                print(f"❌ Found invalid uppercase risk levels: {invalid_levels}")
            else:
                print("✅ All product risk levels are lowercase")
        except Exception as e:
            print(f"  ⚠️  Products table verification skipped: {e}")
        
        # Check User status values
        try:
            result = db.execute(text("SELECT DISTINCT status FROM users"))
            statuses = [row[0] for row in result.fetchall()]
            
            invalid_statuses = [s for s in statuses if s and s.isupper()]
            if invalid_statuses:
                print(f"❌ Found invalid uppercase user statuses: {invalid_statuses}")
            else:
                print("✅ All user statuses are lowercase")
        except Exception as e:
            print(f"  ⚠️  Users table verification skipped: {e}")
        
        print("✅ Migration verification completed!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        raise
    finally:
        db.close()

def main():
    """Main migration function"""
    print("🚀 Starting Enum Value Migration")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("iso22000_fsms.db"):
        print("❌ Database file not found in current directory!")
        print("Please run this script from the backend directory.")
        return
    
    # Create backup
    backup_path = backup_database()
    if not backup_path:
        return
    
    try:
        # Run migrations
        migrate_nonconformance_status()
        migrate_haccp_enums()
        migrate_user_status()
        
        # Verify migration
        verify_migration()
        
        print("\n🎉 Migration completed successfully!")
        print(f"📁 Backup created at: {backup_path}")
        print("\n⚠️  IMPORTANT: Test your application thoroughly before deploying to production!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please restore from backup and check the error.")
        return

if __name__ == "__main__":
    main()
