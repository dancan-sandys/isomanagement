#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix risk data enum values in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.risk import RiskRegisterItem
from sqlalchemy.orm import sessionmaker

def fix_risk_data():
    """Fix enum values in risk data"""
    print("🔧 Fixing Risk Data Enum Values\n")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all risk items
        risk_items = db.query(RiskRegisterItem).all()
        print(f"📊 Found {len(risk_items)} risk items to check")
        
        fixed_count = 0
        
        for item in risk_items:
            needs_update = False
            
            # Check and fix category
            if item.category not in ['process', 'supplier', 'staff', 'environment', 'haccp', 'prp', 'document', 'training', 'equipment', 'compliance', 'customer', 'other']:
                print(f"⚠️  Fixing category for item {item.id}: {item.category} -> equipment")
                item.category = 'equipment'
                needs_update = True
            
            # Check and fix classification
            if item.classification not in ['food_safety', 'business', 'customer']:
                print(f"⚠️  Fixing classification for item {item.id}: {item.classification} -> business")
                item.classification = 'business'
                needs_update = True
            
            # Check and fix likelihood
            if item.likelihood not in ['rare', 'unlikely', 'possible', 'likely', 'almost_certain']:
                print(f"⚠️  Fixing likelihood for item {item.id}: {item.likelihood} -> possible")
                item.likelihood = 'possible'
                needs_update = True
            
            # Check and fix severity
            if item.severity not in ['low', 'medium', 'high', 'critical']:
                print(f"⚠️  Fixing severity for item {item.id}: {item.severity} -> medium")
                item.severity = 'medium'
                needs_update = True
            
            # Check and fix status
            if item.status not in ['open', 'monitoring', 'mitigated', 'closed']:
                print(f"⚠️  Fixing status for item {item.id}: {item.status} -> open")
                item.status = 'open'
                needs_update = True
            
            if needs_update:
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            print(f"✅ Fixed {fixed_count} risk items")
        else:
            print("✅ All risk items already have correct enum values")
        
        # Show updated data
        print("\n📝 Updated risk items:")
        updated_items = db.query(RiskRegisterItem).all()
        for item in updated_items:
            print(f"   - ID: {item.id}, Number: {item.risk_number}, Title: {item.title}")
            print(f"     Category: {item.category}, Classification: {item.classification}")
            print(f"     Likelihood: {item.likelihood}, Severity: {item.severity}, Status: {item.status}")
            print()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing risk data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    fix_risk_data()
