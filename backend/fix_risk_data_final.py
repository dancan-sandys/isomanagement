#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix risk data with correct enum values
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_risk_data_final():
    """Fix risk data with correct enum values"""
    print("🔧 Fixing Risk Data with Correct Enum Values\n")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Update with correct enum values
            print("🔧 Updating with correct enum values...")
            
            # Update specific records with proper values
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'equipment', classification = 'business', likelihood = 'possible', severity = 'high', status = 'open'
                WHERE id = 1
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'supplier', classification = 'business', likelihood = 'likely', severity = 'medium', status = 'open'
                WHERE id = 2
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'compliance', classification = 'food_safety', likelihood = 'unlikely', severity = 'high', status = 'open'
                WHERE id = 3
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'staff', classification = 'business', likelihood = 'likely', severity = 'low', status = 'open'
                WHERE id = 4
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'process', classification = 'business', likelihood = 'possible', severity = 'medium', status = 'open'
                WHERE id = 5
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
    fix_risk_data_final()
