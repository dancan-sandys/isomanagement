#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check all table schemas and identify missing columns
"""
import sqlite3
import os

def check_all_schemas():
    """Check all table schemas for missing columns"""
    print("Checking all table schemas...")
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables: {tables}")
        
        # Check each table
        for table in tables:
            print(f"\n--- Checking table: {table} ---")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Columns: {columns}")
            
            # Check for common missing columns based on models
            if table == "supplier_evaluations":
                expected_columns = [
                    'id', 'supplier_id', 'evaluation_period', 'evaluation_date', 'status',
                    'quality_score', 'delivery_score', 'price_score', 'communication_score',
                    'technical_support_score', 'hygiene_score', 'overall_score',
                    'quality_comments', 'delivery_comments', 'price_comments',
                    'communication_comments', 'technical_support_comments', 'hygiene_comments',
                    'issues_identified', 'improvement_actions', 'follow_up_required',
                    'follow_up_date', 'evaluated_by', 'reviewed_by', 'reviewed_at',
                    'created_at', 'updated_at'
                ]
                
                missing = [col for col in expected_columns if col not in columns]
                if missing:
                    print(f"❌ Missing columns: {missing}")
                else:
                    print("✅ All expected columns present")
            
            elif table == "suppliers":
                expected_columns = [
                    'id', 'supplier_code', 'name', 'status', 'category',
                    'contact_person', 'email', 'phone', 'website',
                    'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
                    'business_registration_number', 'tax_identification_number', 'company_type', 'year_established',
                    'certifications', 'certification_expiry_dates',
                    'overall_score', 'last_evaluation_date', 'next_evaluation_date',
                    'risk_level', 'risk_factors', 'notes',
                    'created_at', 'updated_at', 'created_by'
                ]
                
                missing = [col for col in expected_columns if col not in columns]
                if missing:
                    print(f"❌ Missing columns: {missing}")
                else:
                    print("✅ All expected columns present")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking schemas: {e}")

if __name__ == "__main__":
    check_all_schemas()
