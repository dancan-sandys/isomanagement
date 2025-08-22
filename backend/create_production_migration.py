# -*- coding: utf-8 -*-
"""
Database Migration Script for Enhanced Production System
"""

import sqlite3
import os

def create_production_tables():
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating enhanced production system tables...")
    
    try:
        # Create process_parameters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id INTEGER NOT NULL,
                step_id INTEGER,
                parameter_name VARCHAR(100) NOT NULL,
                parameter_value REAL NOT NULL,
                unit VARCHAR(20) NOT NULL,
                target_value REAL,
                tolerance_min REAL,
                tolerance_max REAL,
                is_within_tolerance BOOLEAN,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recorded_by INTEGER,
                notes TEXT,
                FOREIGN KEY (process_id) REFERENCES production_processes (id)
            )
        ''')
        
        # Create process_deviations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_deviations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id INTEGER NOT NULL,
                step_id INTEGER,
                parameter_id INTEGER,
                deviation_type VARCHAR(50) NOT NULL,
                expected_value REAL NOT NULL,
                actual_value REAL NOT NULL,
                deviation_percent REAL,
                severity VARCHAR(20) NOT NULL DEFAULT 'low',
                impact_assessment TEXT,
                corrective_action TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP,
                resolved_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (process_id) REFERENCES production_processes (id)
            )
        ''')
        
        # Create process_alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id INTEGER NOT NULL,
                alert_type VARCHAR(50) NOT NULL,
                alert_level VARCHAR(20) NOT NULL DEFAULT 'warning',
                message TEXT NOT NULL,
                parameter_value REAL,
                threshold_value REAL,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_at TIMESTAMP,
                acknowledged_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (process_id) REFERENCES production_processes (id)
            )
        ''')
        
        # Create process_templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name VARCHAR(100) NOT NULL,
                product_type VARCHAR(50) NOT NULL,
                description TEXT,
                steps TEXT NOT NULL,
                parameters TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                updated_at TIMESTAMP,
                updated_by INTEGER
            )
        ''')
        
        conn.commit()
        print("✅ Enhanced production system tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating production tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_production_tables()
