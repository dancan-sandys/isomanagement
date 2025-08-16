#!/usr/bin/env python3
"""
Test script for audit program model
"""
from app.core.database import engine
from app.models.audit_mgmt import AuditProgram, Audit
from sqlalchemy import text

def test_audit_program():
    """Test that the audit program model works"""
    
    with engine.connect() as conn:
        # Check if audit_programs table exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_programs'"))
        table_exists = result.fetchone() is not None
        print(f"audit_programs table exists: {table_exists}")
        
        # Check if program_id column exists in audits table
        result = conn.execute(text("PRAGMA table_info(audits)"))
        columns = [row[1] for row in result.fetchall()]
        program_id_exists = 'program_id' in columns
        print(f"program_id column exists in audits table: {program_id_exists}")
        
        # Test creating an audit program
        if table_exists:
            try:
                # Insert a test audit program
                conn.execute(text("""
                    INSERT INTO audit_programs (
                        name, objectives, scope, year, manager_id, 
                        risk_method, status, created_by
                    ) VALUES (
                        'Test Program', 'Test objectives', 'Test scope', 
                        2024, 1, 'qualitative', 'draft', 1
                    )
                """))
                conn.commit()
                print("Successfully created test audit program")
                
                # Query it back
                result = conn.execute(text("SELECT * FROM audit_programs WHERE name = 'Test Program'"))
                program = result.fetchone()
                if program:
                    print(f"Retrieved audit program: {program}")
                
            except Exception as e:
                print(f"Error creating test audit program: {e}")

if __name__ == "__main__":
    test_audit_program()
