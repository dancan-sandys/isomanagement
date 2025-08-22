#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database migration script for Objectives Management System
Adds new tables and enhances existing ones for Phase 1 implementation
"""

import sqlite3
import os
from datetime import datetime
import sys

def create_migration():
    """Create the database migration for objectives management"""
    
    # Database file path
    db_path = "iso22000_fsms.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found!")
        return False
    
    print(f"Starting Objectives Management migration...")
    print(f"Database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        print("Step 1: Creating departments table...")
        
        # Drop existing departments table if it exists
        cursor.execute("DROP TABLE IF EXISTS departments")
        
        # Create departments table
        cursor.execute("""
            CREATE TABLE departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_code VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                parent_department_id INTEGER,
                manager_id INTEGER,
                status VARCHAR(20) DEFAULT 'active',
                color_code VARCHAR(7),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL
            )
        """)
        
        print("Step 2: Creating department_users table...")
        
        # Drop existing department_users table if it exists
        cursor.execute("DROP TABLE IF EXISTS department_users")
        
        # Create department_users table
        cursor.execute("""
            CREATE TABLE department_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role VARCHAR(100),
                assigned_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_until TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL
            )
        """)
        
        print("Step 3: Adding department_id to users table...")
        
        # Add department_id column to users table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN department_id INTEGER")
            print("   SUCCESS: Added department_id column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   INFO: department_id column already exists")
            else:
                raise e
        
        # Add department_name column for backward compatibility
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN department_name VARCHAR(100)")
            print("   SUCCESS: Added department_name column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   INFO: department_name column already exists")
            else:
                raise e
        
        print("Step 4: Enhancing food_safety_objectives table...")
        
        # Add new columns to food_safety_objectives table
        new_columns = [
            ("objective_type", "VARCHAR(50) DEFAULT 'operational'"),
            ("hierarchy_level", "VARCHAR(50) DEFAULT 'operational'"),
            ("parent_objective_id", "INTEGER"),
            ("department_id", "INTEGER"),
            ("baseline_value", "REAL"),
            ("weight", "REAL DEFAULT 1.0"),
            ("measurement_frequency", "VARCHAR(100)"),
            ("trend_direction", "VARCHAR(50)"),
            ("performance_color", "VARCHAR(20)"),
            ("automated_calculation", "BOOLEAN DEFAULT 0"),
            ("data_source", "VARCHAR(50) DEFAULT 'manual'"),
            ("last_updated_by", "INTEGER"),
            ("last_updated_at", "TIMESTAMP"),
            # ISO 6.2 fields
            ("owner_user_id", "INTEGER"),
            ("sponsor_user_id", "INTEGER"),
            ("method_of_evaluation", "VARCHAR(100)"),
            ("acceptance_criteria", "TEXT"),
            ("resource_plan", "TEXT"),
            ("budget_estimate", "REAL"),
            ("budget_currency", "VARCHAR(10)"),
            ("communication_plan", "TEXT"),
            ("linked_risk_ids", "TEXT"),
            ("linked_control_ids", "TEXT"),
            ("linked_document_ids", "TEXT"),
            ("management_review_refs", "TEXT"),
            ("version", "INTEGER DEFAULT 1"),
            ("superseded_by_id", "INTEGER"),
            ("change_reason", "TEXT")
        ]
        
        for column_name, column_def in new_columns:
            try:
                cursor.execute(f"ALTER TABLE food_safety_objectives ADD COLUMN {column_name} {column_def}")
                print(f"   SUCCESS: Added {column_name} column")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   INFO: {column_name} column already exists")
                else:
                    raise e
        
        print("Step 5: Creating indexes...")
        
        # Create indexes
        indexes = [
            ("ix_departments_hierarchy", "departments (parent_department_id, status)"),
            ("ix_departments_manager", "departments (manager_id, status)"),
            ("ix_department_users_active", "department_users (department_id, user_id, is_active)"),
            ("ix_department_users_period", "department_users (assigned_from, assigned_until)"),
            ("ix_objectives_hierarchy", "food_safety_objectives (parent_objective_id, objective_type)"),
            ("ix_objectives_department", "food_safety_objectives (department_id, objective_type)"),
            ("ix_objectives_type_level", "food_safety_objectives (objective_type, hierarchy_level)")
        ]
        
        for index_name, index_def in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
                print(f"   SUCCESS: Created index {index_name}")
            except sqlite3.OperationalError as e:
                print(f"   INFO: Index {index_name} already exists")
        
        print("Step 6: Inserting sample departments...")
        
        # Insert sample departments
        sample_departments = [
            ("CORP", "Corporate", "Corporate level objectives and strategic goals", None, None, "active", "#1976D2"),
            ("PROD", "Production", "Production department objectives", None, None, "active", "#388E3C"),
            ("QA", "Quality Assurance", "Quality assurance and food safety objectives", None, None, "active", "#D32F2F"),
            ("MAINT", "Maintenance", "Equipment maintenance and reliability objectives", None, None, "active", "#FF9800"),
            ("LAB", "Laboratory", "Laboratory testing and analysis objectives", None, None, "active", "#9C27B0"),
            ("SUPPLY", "Supply Chain", "Supply chain and procurement objectives", None, None, "active", "#607D8B")
        ]
        
        for dept_code, name, description, parent_id, manager_id, status, color in sample_departments:
            try:
                cursor.execute("""
                    INSERT INTO departments (department_code, name, description, parent_department_id, manager_id, status, color_code, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (dept_code, name, description, parent_id, manager_id, status, color, 1))
                print(f"   SUCCESS: Added department: {name}")
            except sqlite3.IntegrityError as e:
                print(f"   INFO: Department {name} already exists")
        
        print("Step 7: Inserting sample corporate objectives...")
        
        # Insert sample corporate objectives
        sample_objectives = [
            ("OBJ-001", "Zero Food Safety Incidents", "Achieve zero food safety incidents across all products", "corporate", "strategic", None, 1, 95.0, 100.0, "percentage", 1.0, "monthly", "manual"),
            ("OBJ-002", "Customer Satisfaction", "Maintain customer satisfaction above 95%", "corporate", "strategic", None, 1, 90.0, 95.0, "percentage", 1.0, "quarterly", "manual"),
            ("OBJ-003", "Production Efficiency", "Improve production efficiency by 10%", "departmental", "tactical", 1, 2, 85.0, 95.0, "percentage", 1.0, "monthly", "system"),
            ("OBJ-004", "Quality Compliance", "Maintain 100% regulatory compliance", "departmental", "tactical", 1, 3, 98.0, 100.0, "percentage", 1.0, "monthly", "manual"),
            ("OBJ-005", "Equipment Uptime", "Maintain equipment uptime above 95%", "operational", "operational", 1, 4, 90.0, 95.0, "percentage", 1.0, "weekly", "system")
        ]
        
        for obj_code, title, description, obj_type, hierarchy, parent_id, dept_id, baseline, target, unit, weight, freq, source in sample_objectives:
            try:
                cursor.execute("""
                    INSERT INTO food_safety_objectives (
                        objective_code, title, description, objective_type, hierarchy_level,
                        parent_objective_id, department_id, baseline_value, target_value,
                        measurement_unit, weight, measurement_frequency, data_source, created_by
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (obj_code, title, description, obj_type, hierarchy, parent_id, dept_id, baseline, target, unit, weight, freq, source, 1))
                print(f"   SUCCESS: Added objective: {title}")
            except sqlite3.IntegrityError as e:
                print(f"   INFO: Objective {title} already exists")
        
        # Commit transaction
        conn.commit()
        print("SUCCESS: Migration completed successfully!")
        
        # Verify the changes
        print("\nVerification:")
        
        # Check departments table
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        print(f"   Departments: {dept_count}")
        
        # Check objectives table
        cursor.execute("SELECT COUNT(*) FROM food_safety_objectives")
        obj_count = cursor.fetchone()[0]
        print(f"   Objectives: {obj_count}")
        
        # Check new columns
        cursor.execute("PRAGMA table_info(food_safety_objectives)")
        columns = [col[1] for col in cursor.fetchall()]
        new_columns_check = ["objective_type", "hierarchy_level", "department_id", "weight", "trend_direction"]
        for col in new_columns_check:
            if col in columns:
                print(f"   SUCCESS: Column {col}: Present")
            else:
                print(f"   ERROR: Column {col}: Missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = create_migration()
    if success:
        print("\nSUCCESS: Objectives Management migration completed successfully!")
        print("Ready to proceed with Phase 1 implementation!")
    else:
        print("\nERROR: Migration failed. Please check the error messages above.")
        sys.exit(1)
