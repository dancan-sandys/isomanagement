#!/usr/bin/env python3
"""
HACCP Data Migration Script - Phase 18

This script handles data migration and backfill for the HACCP system.
It ensures data integrity and populates necessary reference data.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db, engine
from app.models.haccp import (
    HACCPProduct, HACCPProcessFlow, HACCPHazard, HACCPCCP,
    CCPMonitoringLog, CCPVerificationLog, HACCPValidation
)
from app.models.user import User

def create_reference_data(db: Session):
    """Create reference data for HACCP system"""
    print("Creating HACCP reference data...")
    
    # Create sample users if they don't exist
    users_data = [
        {
            "username": "haccp_manager",
            "email": "haccp.manager@company.com",
            "full_name": "HACCP Manager",
            "is_active": True
        },
        {
            "username": "qa_supervisor", 
            "email": "qa.supervisor@company.com",
            "full_name": "QA Supervisor",
            "is_active": True
        },
        {
            "username": "production_operator",
            "email": "production.operator@company.com", 
            "full_name": "Production Operator",
            "is_active": True
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            user = User(**user_data)
            db.add(user)
            print(f"Created user: {user_data['username']}")
    
    db.commit()
    print("Reference data creation completed.")

def create_sample_haccp_data(db: Session):
    """Create sample HACCP data for testing and demonstration"""
    print("Creating sample HACCP data...")
    
    # Get users
    haccp_manager = db.query(User).filter(User.username == "haccp_manager").first()
    qa_supervisor = db.query(User).filter(User.username == "qa_supervisor").first()
    production_operator = db.query(User).filter(User.username == "production_operator").first()
    
    if not all([haccp_manager, qa_supervisor, production_operator]):
        print("Required users not found. Creating reference data first...")
        create_reference_data(db)
        haccp_manager = db.query(User).filter(User.username == "haccp_manager").first()
        qa_supervisor = db.query(User).filter(User.username == "qa_supervisor").first()
        production_operator = db.query(User).filter(User.username == "production_operator").first()
    
    # Create sample products
    products_data = [
        {
            "name": "Chicken Breast Fillets",
            "product_code": "CHK-001",
            "category": "Poultry",
            "description": "Fresh chicken breast fillets for retail sale",
            "created_by": haccp_manager.id,
            "status": "active"
        },
        {
            "name": "Ground Beef Patties",
            "product_code": "BEEF-001", 
            "category": "Beef",
            "description": "Ground beef patties for food service",
            "created_by": haccp_manager.id,
            "status": "active"
        },
        {
            "name": "Salmon Fillets",
            "product_code": "FISH-001",
            "category": "Seafood", 
            "description": "Fresh salmon fillets",
            "created_by": haccp_manager.id,
            "status": "active"
        }
    ]
    
    created_products = []
    for product_data in products_data:
        existing_product = db.query(HACCPProduct).filter(
            HACCPProduct.product_code == product_data["product_code"]
        ).first()
        
        if not existing_product:
            product = HACCPProduct(**product_data)
            db.add(product)
            created_products.append(product)
            print(f"Created product: {product_data['name']}")
    
    db.commit()
    
    # Create process flows for each product
    for product in created_products:
        if product.product_code == "CHK-001":
            process_steps = [
                {"step_number": 1, "step_name": "Receiving", "description": "Receive fresh chicken from approved suppliers"},
                {"step_number": 2, "step_name": "Storage", "description": "Store at 0-4°C in refrigerated storage"},
                {"step_number": 3, "step_name": "Processing", "description": "Cut, trim, and portion chicken breast"},
                {"step_number": 4, "step_name": "Cooking", "description": "Cook to internal temperature of 74°C"},
                {"step_number": 5, "step_name": "Cooling", "description": "Rapid cooling to 4°C within 4 hours"},
                {"step_number": 6, "step_name": "Packaging", "description": "Package in food-grade materials"}
            ]
        elif product.product_code == "BEEF-001":
            process_steps = [
                {"step_number": 1, "step_name": "Receiving", "description": "Receive ground beef from approved suppliers"},
                {"step_number": 2, "step_name": "Storage", "description": "Store at 0-4°C in refrigerated storage"},
                {"step_number": 3, "step_name": "Grinding", "description": "Grind beef to specified consistency"},
                {"step_number": 4, "step_name": "Patties Formation", "description": "Form into patties of specified weight"},
                {"step_number": 5, "step_name": "Cooking", "description": "Cook to internal temperature of 71°C"},
                {"step_number": 6, "step_name": "Packaging", "description": "Package in food-grade materials"}
            ]
        else:  # FISH-001
            process_steps = [
                {"step_number": 1, "step_name": "Receiving", "description": "Receive fresh salmon from approved suppliers"},
                {"step_number": 2, "step_name": "Storage", "description": "Store at 0-4°C in refrigerated storage"},
                {"step_number": 3, "step_name": "Filleting", "description": "Cut salmon into fillets"},
                {"step_number": 4, "step_name": "Cooking", "description": "Cook to internal temperature of 63°C"},
                {"step_number": 5, "step_name": "Cooling", "description": "Rapid cooling to 4°C within 4 hours"},
                {"step_number": 6, "step_name": "Packaging", "description": "Package in food-grade materials"}
            ]
        
        for step_data in process_steps:
            process_flow = HACCPProcessFlow(
                product_id=product.id,
                created_by=haccp_manager.id,
                **step_data
            )
            db.add(process_flow)
    
    db.commit()
    print("Sample HACCP data creation completed.")

def backfill_monitoring_data(db: Session):
    """Backfill historical monitoring data for demonstration"""
    print("Backfilling historical monitoring data...")
    
    # Get existing CCPs
    ccps = db.query(HACCPCCP).all()
    
    if not ccps:
        print("No CCPs found. Creating sample data first...")
        create_sample_haccp_data(db)
        ccps = db.query(HACCPCCP).all()
    
    # Generate historical monitoring logs for the last 30 days
    for ccp in ccps:
        for i in range(30):
            monitoring_date = datetime.now() - timedelta(days=i)
            
            # Generate realistic monitoring data
            if "temperature" in ccp.name.lower():
                base_temp = 75.0 if "cooking" in ccp.name.lower() else 3.0
                parameter_value = base_temp + (i % 5) - 2  # Vary by ±2 degrees
                unit = "°C"
                is_within_limits = 70 <= parameter_value <= 85 if "cooking" in ccp.name.lower() else 0 <= parameter_value <= 4
            else:
                parameter_value = 20.0 + (i % 10)  # Default values
                unit = "minutes"
                is_within_limits = True
            
            monitoring_log = CCPMonitoringLog(
                ccp_id=ccp.id,
                monitoring_date=monitoring_date,
                parameter_value=parameter_value,
                unit=unit,
                is_within_limits=is_within_limits,
                operator_notes=f"Routine monitoring - Day {i+1}",
                created_by=1  # Default user ID
            )
            db.add(monitoring_log)
    
    db.commit()
    print("Historical monitoring data backfill completed.")

def validate_data_integrity(db: Session):
    """Validate data integrity after migration"""
    print("Validating data integrity...")
    
    # Check for orphaned records
    orphaned_flows = db.execute(text("""
        SELECT pf.id FROM haccp_process_flows pf 
        LEFT JOIN haccp_products p ON pf.product_id = p.id 
        WHERE p.id IS NULL
    """)).fetchall()
    
    if orphaned_flows:
        print(f"Warning: Found {len(orphaned_flows)} orphaned process flows")
    else:
        print("✅ No orphaned process flows found")
    
    # Check for orphaned hazards
    orphaned_hazards = db.execute(text("""
        SELECT h.id FROM haccp_hazards h 
        LEFT JOIN haccp_products p ON h.product_id = p.id 
        WHERE p.id IS NULL
    """)).fetchall()
    
    if orphaned_hazards:
        print(f"Warning: Found {len(orphaned_hazards)} orphaned hazards")
    else:
        print("✅ No orphaned hazards found")
    
    # Check for orphaned CCPs
    orphaned_ccps = db.execute(text("""
        SELECT c.id FROM haccp_ccps c 
        LEFT JOIN haccp_products p ON c.product_id = p.id 
        WHERE p.id IS NULL
    """)).fetchall()
    
    if orphaned_ccps:
        print(f"Warning: Found {len(orphaned_ccps)} orphaned CCPs")
    else:
        print("✅ No orphaned CCPs found")
    
    # Check for orphaned monitoring logs
    orphaned_logs = db.execute(text("""
        SELECT ml.id FROM ccp_monitoring_logs ml 
        LEFT JOIN haccp_ccps c ON ml.ccp_id = c.id 
        WHERE c.id IS NULL
    """)).fetchall()
    
    if orphaned_logs:
        print(f"Warning: Found {len(orphaned_logs)} orphaned monitoring logs")
    else:
        print("✅ No orphaned monitoring logs found")
    
    print("Data integrity validation completed.")

def run_migration():
    """Run the complete migration process"""
    print("🚀 Starting HACCP Data Migration - Phase 18")
    print("=" * 60)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Step 1: Create reference data
        create_reference_data(db)
        
        # Step 2: Create sample HACCP data
        create_sample_haccp_data(db)
        
        # Step 3: Backfill historical data
        backfill_monitoring_data(db)
        
        # Step 4: Validate data integrity
        validate_data_integrity(db)
        
        print("\n✅ HACCP Data Migration Completed Successfully!")
        print("=" * 60)
        
        # Print summary
        product_count = db.query(HACCPProduct).count()
        hazard_count = db.query(HACCPHazard).count()
        ccp_count = db.query(HACCPCCP).count()
        monitoring_count = db.query(CCPMonitoringLog).count()
        
        print(f"📊 Migration Summary:")
        print(f"   Products: {product_count}")
        print(f"   Hazards: {hazard_count}")
        print(f"   CCPs: {ccp_count}")
        print(f"   Monitoring Logs: {monitoring_count}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
