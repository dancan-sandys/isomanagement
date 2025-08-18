#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix risk enum values to match the enum definition exactly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_risk_enum_values():
    """Fix enum values to match the enum definition exactly"""
    print("🔧 Fixing Risk Enum Values to Match Definition\n")
    
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
            
            # The issue is that the enum values in the database are lowercase
            # but SQLAlchemy expects them to match the enum definition exactly
            # Let me check what the actual enum definition expects
            
            print("🔧 The issue is enum value mismatch. Let me check the actual enum definition...")
            
            # Let me try a different approach - let's see what the actual enum values should be
            # by checking the model definition
            
            print("📋 Expected enum values from model:")
            print("   RiskCategory: PROCESS, SUPPLIER, STAFF, ENVIRONMENT, HACCP, PRP, DOCUMENT, TRAINING, EQUIPMENT, COMPLIANCE, CUSTOMER, OTHER, STRATEGIC, FINANCIAL, REPUTATIONAL, BUSINESS_CONTINUITY, REGULATORY")
            print("   RiskClassification: FOOD_SAFETY, BUSINESS, CUSTOMER")
            print("   RiskLikelihood: RARE, UNLIKELY, POSSIBLE, LIKELY, ALMOST_CERTAIN")
            print("   RiskSeverity: LOW, MEDIUM, HIGH, CRITICAL")
            print("   RiskStatus: OPEN, MONITORING, MITIGATED, CLOSED")
            
            # The issue is that the enum values in the database are lowercase
            # but the enum definition expects them to be the enum names (uppercase)
            # Let me fix this by updating the database to use the correct enum values
            
            print("\n🔧 Updating enum values to match enum definition...")
            
            # Update categories to use enum names
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'EQUIPMENT' 
                WHERE category = 'equipment'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'SUPPLIER' 
                WHERE category = 'supplier'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'COMPLIANCE' 
                WHERE category = 'compliance'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'STAFF' 
                WHERE category = 'staff'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET category = 'PROCESS' 
                WHERE category = 'process'
            """))
            
            # Update classifications
            conn.execute(text("""
                UPDATE risk_register 
                SET classification = 'BUSINESS' 
                WHERE classification = 'business'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET classification = 'FOOD_SAFETY' 
                WHERE classification = 'food_safety'
            """))
            
            # Update likelihood
            conn.execute(text("""
                UPDATE risk_register 
                SET likelihood = 'POSSIBLE' 
                WHERE likelihood = 'possible'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET likelihood = 'LIKELY' 
                WHERE likelihood = 'likely'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET likelihood = 'UNLIKELY' 
                WHERE likelihood = 'unlikely'
            """))
            
            # Update severity
            conn.execute(text("""
                UPDATE risk_register 
                SET severity = 'HIGH' 
                WHERE severity = 'high'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET severity = 'MEDIUM' 
                WHERE severity = 'medium'
            """))
            
            conn.execute(text("""
                UPDATE risk_register 
                SET severity = 'LOW' 
                WHERE severity = 'low'
            """))
            
            # Update status
            conn.execute(text("""
                UPDATE risk_register 
                SET status = 'OPEN' 
                WHERE status = 'open'
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
    fix_risk_enum_values()
