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

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

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
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        print("Step 1: Creating departments table...")
        
        # Create departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
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
                created_by INTEGER NOT NULL,
                FOREIGN KEY (parent_department_id) REFERENCES departments (id),
                FOREIGN KEY (manager_id) REFERENCES users (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        
        # Create indexes for departments
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_departments_hierarchy 
            ON departments (parent_department_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_departments_manager 
            ON departments (manager_id, status)
        """)
        
        print("Step 2: Creating department_users table...")
        
        # Create department_users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS department_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role VARCHAR(100),
                assigned_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_until TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        
        # Create indexes for department_users
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_department_users_active 
            ON department_users (department_id, user_id, is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_department_users_period 
            ON department_users (assigned_from, assigned_until)
        """)
        
        print("Step 3: Adding department_id to users table...")
        
        # Add department_id column to users table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN department_id INTEGER REFERENCES departments (id)")
            print("   SUCCESS: Added department_id column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   INFO: department_id column already exists")
            else:
                raise e
        
        # Rename existing department column to department_name for backward compatibility
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN department_name VARCHAR(100)")
            print("   ✅ Added department_name column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ℹ️  department_name column already exists")
            else:
                raise e
        
        print("📋 Step 4: Enhancing food_safety_objectives table...")
        
        # Add new columns to food_safety_objectives table
        new_columns = [
            ("objective_type", "VARCHAR(50) DEFAULT 'operational'"),
            ("hierarchy_level", "VARCHAR(50) DEFAULT 'operational'"),
            ("parent_objective_id", "INTEGER REFERENCES food_safety_objectives (id)"),
            ("department_id", "INTEGER REFERENCES departments (id)"),
            ("baseline_value", "REAL"),
            ("weight", "REAL DEFAULT 1.0"),
            ("measurement_frequency", "VARCHAR(100)"),
            ("trend_direction", "VARCHAR(50)"),
            ("performance_color", "VARCHAR(20)"),
            ("automated_calculation", "BOOLEAN DEFAULT 0"),
            ("data_source", "VARCHAR(50) DEFAULT 'manual'"),
            ("last_updated_by", "INTEGER REFERENCES users (id)"),
            ("last_updated_at", "TIMESTAMP")
        ]
        
        for column_name, column_def in new_columns:
            try:
                cursor.execute(f"ALTER TABLE food_safety_objectives ADD COLUMN {column_name} {column_def}")
                print(f"   ✅ Added {column_name} column")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ℹ️  {column_name} column already exists")
                else:
                    raise e
        
        # Change target_value from TEXT to REAL
        try:
            cursor.execute("""
                CREATE TABLE food_safety_objectives_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    objective_code VARCHAR(50) UNIQUE NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    category VARCHAR(100),
                    objective_type VARCHAR(50) DEFAULT 'operational',
                    hierarchy_level VARCHAR(50) DEFAULT 'operational',
                    parent_objective_id INTEGER,
                    department_id INTEGER,
                    baseline_value REAL,
                    target_value REAL,
                    measurement_unit VARCHAR(50),
                    weight REAL DEFAULT 1.0,
                    measurement_frequency VARCHAR(100),
                    trend_direction VARCHAR(50),
                    performance_color VARCHAR(20),
                    automated_calculation BOOLEAN DEFAULT 0,
                    data_source VARCHAR(50) DEFAULT 'manual',
                    frequency VARCHAR(100),
                    responsible_person_id INTEGER,
                    review_frequency VARCHAR(100),
                    last_review_date TIMESTAMP,
                    next_review_date TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active',
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated_by INTEGER,
                    last_updated_at TIMESTAMP,
                    FOREIGN KEY (parent_objective_id) REFERENCES food_safety_objectives (id),
                    FOREIGN KEY (department_id) REFERENCES departments (id),
                    FOREIGN KEY (responsible_person_id) REFERENCES users (id),
                    FOREIGN KEY (created_by) REFERENCES users (id),
                    FOREIGN KEY (last_updated_by) REFERENCES users (id)
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO food_safety_objectives_new 
                SELECT id, objective_code, title, description, category,
                       COALESCE(objective_type, 'operational') as objective_type,
                       COALESCE(hierarchy_level, 'operational') as hierarchy_level,
                       parent_objective_id, department_id, baseline_value,
                       CAST(target_value AS REAL) as target_value,
                       measurement_unit, COALESCE(weight, 1.0) as weight,
                       measurement_frequency, trend_direction, performance_color,
                       COALESCE(automated_calculation, 0) as automated_calculation,
                       COALESCE(data_source, 'manual') as data_source,
                       frequency, responsible_person_id, review_frequency,
                       last_review_date, next_review_date, status, created_by,
                       created_at, updated_at, last_updated_by, last_updated_at
                FROM food_safety_objectives
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE food_safety_objectives")
            cursor.execute("ALTER TABLE food_safety_objectives_new RENAME TO food_safety_objectives")
            print("   ✅ Converted target_value to REAL type")
            
        except sqlite3.OperationalError as e:
            print(f"   ℹ️  Table structure already updated: {e}")
        
        print("📋 Step 5: Creating indexes for objectives...")
        
        # Create indexes for food_safety_objectives
        indexes = [
            ("ix_objectives_hierarchy", "food_safety_objectives (parent_objective_id, objective_type)"),
            ("ix_objectives_department", "food_safety_objectives (department_id, objective_type)"),
            ("ix_objectives_type_level", "food_safety_objectives (objective_type, hierarchy_level)"),
            ("ix_objective_target_department", "objective_targets (department_id, period_start)"),
            ("ix_objective_progress_department", "objective_progress (department_id, period_start)"),
            ("ix_objective_progress_status", "objective_progress (status, period_start)")
        ]
        
        for index_name, index_def in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
                print(f"   ✅ Created index {index_name}")
            except sqlite3.OperationalError as e:
                print(f"   ℹ️  Index {index_name} already exists: {e}")
        
        print("📋 Step 6: Inserting sample departments...")
        
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
                print(f"   ✅ Added department: {name}")
            except sqlite3.IntegrityError as e:
                print(f"   ℹ️  Department {name} already exists")
        
        print("📋 Step 7: Inserting sample corporate objectives...")
        
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
                print(f"   ✅ Added objective: {title}")
            except sqlite3.IntegrityError as e:
                print(f"   ℹ️  Objective {title} already exists")
        
        # Commit transaction
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the changes
        print("\n📊 Verification:")
        
        # Check departments table
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        print(f"   📁 Departments: {dept_count}")
        
        # Check objectives table
        cursor.execute("SELECT COUNT(*) FROM food_safety_objectives")
        obj_count = cursor.fetchone()[0]
        print(f"   🎯 Objectives: {obj_count}")
        
        # Check new columns
        cursor.execute("PRAGMA table_info(food_safety_objectives)")
        columns = [col[1] for col in cursor.fetchall()]
        new_columns_check = ["objective_type", "hierarchy_level", "department_id", "weight", "trend_direction"]
        for col in new_columns_check:
            if col in columns:
                print(f"   ✅ Column {col}: Present")
            else:
                print(f"   ❌ Column {col}: Missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = create_migration()
    if success:
        print("\n🎉 Objectives Management migration completed successfully!")
        print("🚀 Ready to proceed with Phase 1 implementation!")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        sys.exit(1)
