#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check risk table and populate with test data automatically
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.risk import RiskRegisterItem
from app.core.database import get_db
from sqlalchemy.orm import sessionmaker

def check_and_populate_risk_table():
    """Check if risk table exists and populate with test data"""
    print("🔍 Checking Risk Table and Data\n")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='risk_register'
            """))
            table_exists = result.fetchone() is not None
            
            if table_exists:
                print("✅ Risk register table exists")
                
                # Check for data
                result = conn.execute(text("SELECT COUNT(*) FROM risk_register"))
                count = result.fetchone()[0]
                print(f"📊 Table has {count} records")
                
                if count > 0:
                    # Show sample data
                    result = conn.execute(text("SELECT id, risk_number, title, item_type, category FROM risk_register LIMIT 5"))
                    records = result.fetchall()
                    print("📝 Sample records:")
                    for record in records:
                        print(f"   - ID: {record[0]}, Number: {record[1]}, Title: {record[2]}, Type: {record[3]}, Category: {record[4]}")
                else:
                    print("📝 No records found - will populate with test data")
                    
            else:
                print("❌ Risk register table does not exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False
    
    # Populate if empty
    try:
        # Get database session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if we already have data
        existing_count = db.query(RiskRegisterItem).count()
        if existing_count > 0:
            print(f"📊 Table already has {existing_count} records. No need to populate.")
            return True
        
        print("\n=== Populating Risk Table ===\n")
        
        # Create test risk items with correct enum values
        test_risks = [
            {
                "risk_number": "RISK-001",
                "title": "Equipment Failure Risk",
                "description": "Risk of critical equipment failure during production",
                "item_type": "risk",
                "category": "equipment",
                "severity": "high",
                "likelihood": "possible",
                "classification": "business",
                "status": "open",
                "created_by": 1  # Assuming admin user has ID 1
            },
            {
                "risk_number": "RISK-002",
                "title": "Supplier Quality Risk",
                "description": "Risk of receiving substandard materials from suppliers",
                "item_type": "risk",
                "category": "supplier",
                "severity": "medium",
                "likelihood": "likely",
                "classification": "business",
                "status": "open",
                "created_by": 1
            },
            {
                "risk_number": "RISK-003",
                "title": "Food Safety Compliance Risk",
                "description": "Risk of non-compliance with food safety regulations",
                "item_type": "risk",
                "category": "compliance",
                "severity": "high",
                "likelihood": "unlikely",
                "classification": "food_safety",
                "status": "open",
                "created_by": 1
            },
            {
                "risk_number": "OPP-001",
                "title": "Staff Training Opportunity",
                "description": "Opportunity to improve staff training and certification",
                "item_type": "opportunity",
                "category": "staff",
                "severity": "low",
                "likelihood": "likely",
                "classification": "business",
                "status": "open",
                "created_by": 1
            },
            {
                "risk_number": "OPP-002",
                "title": "Process Improvement Opportunity",
                "description": "Opportunity to optimize production processes",
                "item_type": "opportunity",
                "category": "process",
                "severity": "medium",
                "likelihood": "possible",
                "classification": "business",
                "status": "open",
                "created_by": 1
            }
        ]
        
        # Insert test data
        for risk_data in test_risks:
            risk_item = RiskRegisterItem(**risk_data)
            db.add(risk_item)
        
        db.commit()
        print(f"✅ Successfully added {len(test_risks)} test risk items")
        
        # Verify the data
        count = db.query(RiskRegisterItem).count()
        print(f"📊 Total records in table: {count}")
        
        # Show sample of inserted data
        sample_risks = db.query(RiskRegisterItem).limit(3).all()
        print("📝 Sample of inserted records:")
        for risk in sample_risks:
            print(f"   - ID: {risk.id}, Number: {risk.risk_number}, Title: {risk.title}, Type: {risk.item_type}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error populating table: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    check_and_populate_risk_table()
