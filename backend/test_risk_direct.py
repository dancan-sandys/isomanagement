#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct test for risk database query
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.core.config import settings
from app.models.risk import RiskRegisterItem
from sqlalchemy.orm import sessionmaker

def test_risk_query():
    """Test direct risk query"""
    print("🔍 Testing Direct Risk Query\n")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Simple query without filters
        print("1. Testing simple query...")
        items = db.query(RiskRegisterItem).all()
        print(f"✅ Found {len(items)} risk items")
        
        for item in items:
            print(f"   - ID: {item.id}, Number: {item.risk_number}, Title: {item.title}")
            print(f"     Category: {item.category}, Classification: {item.classification}")
            print(f"     Likelihood: {item.likelihood}, Severity: {item.severity}, Status: {item.status}")
            print()
        
        # Test with specific filter
        print("2. Testing with item_type filter...")
        risk_items = db.query(RiskRegisterItem).filter(RiskRegisterItem.item_type == "risk").all()
        print(f"✅ Found {len(risk_items)} risk items (type=risk)")
        
        # Test with category filter
        print("3. Testing with category filter...")
        equipment_items = db.query(RiskRegisterItem).filter(RiskRegisterItem.category == "equipment").all()
        print(f"✅ Found {len(equipment_items)} equipment items")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db' in locals():
            db.close()
        return False

if __name__ == "__main__":
    test_risk_query()
