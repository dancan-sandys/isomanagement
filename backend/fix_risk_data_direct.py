#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix risk data enum values directly in the database using SQL
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_risk_data_direct():
    """Fix enum values directly in the database"""
    print("🔧 Fixing Risk Data Enum Values Directly\n")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check current data
            result = conn.execute(text("SELECT id, risk_number, title, category, classification, likelihood, severity, status FROM risk_register"))
            records = result.fetchall()
            
            print(f"📊 Found {len(records)} risk items")
            print("📝 Current data:")
            for record in records:
                print(f"   - ID: {record[0]}, Number: {record[1]}, Title: {record[2]}")
                print(f"     Category: {record[3]}, Classification: {record[4]}")
                print(f"     Likelihood: {record[5]}, Severity: {record[6]}, Status: {record[7]}")
                print()
            
            # Fix enum values directly
            print("🔧 Updating enum values...")
            
            # Update categories
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'equipment' 
                WHERE category NOT IN ('process', 'supplier', 'staff', 'environment', 'haccp', 'prp', 'document', 'training', 'equipment', 'compliance', 'customer', 'other')
            """))
            
            # Update classifications
            conn.execute(text("""
                UPDATE risk_register 
                SET classification = 'business' 
                WHERE classification NOT IN ('food_safety', 'business', 'customer')
            """))
            
            # Update likelihood
            conn.execute(text("""
                UPDATE risk_register 
                SET likelihood = 'possible' 
                WHERE likelihood NOT IN ('rare', 'unlikely', 'possible', 'likely', 'almost_certain')
            """))
            
            # Update severity
            conn.execute(text("""
                UPDATE risk_register 
                SET severity = 'medium' 
                WHERE severity NOT IN ('low', 'medium', 'high', 'critical')
            """))
            
            # Update status
            conn.execute(text("""
                UPDATE risk_register 
                SET status = 'open' 
                WHERE status NOT IN ('open', 'monitoring', 'mitigated', 'closed')
            """))
            
            conn.commit()
            print("✅ Database updated successfully")
            
            # Show updated data
            print("\n📝 Updated data:")
            result = conn.execute(text("SELECT id, risk_number, title, category, classification, likelihood, severity, status FROM risk_register"))
            records = result.fetchall()
            for record in records:
                print(f"   - ID: {record[0]}, Number: {record[1]}, Title: {record[2]}")
                print(f"     Category: {record[3]}, Classification: {record[4]}")
                print(f"     Likelihood: {record[5]}, Severity: {record[6]}, Status: {record[7]}")
                print()
                
    except Exception as e:
        print(f"❌ Error fixing risk data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_risk_data_direct()
