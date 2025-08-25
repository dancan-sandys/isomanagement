# -*- coding: utf-8 -*-
"""
Actions Log System Database Migration
Phase 3: Create tables for action tracking and management
"""

import sqlite3
import os
from datetime import datetime

def create_actions_log_tables():
    """Create actions log system tables"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating Actions Log System tables...")
    
    try:
        # Create action_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                action_source VARCHAR(50) NOT NULL,
                source_id INTEGER,
                risk_id INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(20) DEFAULT 'medium',
                assigned_to INTEGER,
                assigned_by INTEGER NOT NULL,
                department_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                progress_percent REAL DEFAULT 0.0,
                estimated_hours REAL,
                actual_hours REAL,
                tags TEXT,
                attachments TEXT,
                notes TEXT
            )
        ''')
        
        # Create action_progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER NOT NULL,
                update_type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                progress_percent REAL,
                hours_spent REAL,
                updated_by INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create action_relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER NOT NULL,
                related_action_id INTEGER NOT NULL,
                relationship_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create interested_parties table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interested_parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                contact_person VARCHAR(255),
                contact_email VARCHAR(255),
                contact_phone VARCHAR(50),
                address TEXT,
                satisfaction_level INTEGER,
                last_assessment_date TIMESTAMP,
                next_assessment_date TIMESTAMP,
                description TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create party_expectations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS party_expectations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                party_id INTEGER NOT NULL,
                expectation_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                importance_level INTEGER NOT NULL,
                current_satisfaction INTEGER,
                target_satisfaction INTEGER NOT NULL,
                assessment_date TIMESTAMP,
                assessment_notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create party_actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS party_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                party_id INTEGER NOT NULL,
                expectation_id INTEGER,
                action_log_id INTEGER NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                expected_impact TEXT,
                success_metrics TEXT,
                impact_assessment TEXT,
                satisfaction_improvement INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create swot_analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swot_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                analysis_date TIMESTAMP NOT NULL,
                next_review_date TIMESTAMP,
                scope VARCHAR(255),
                context TEXT,
                status VARCHAR(20) DEFAULT 'active',
                is_current BOOLEAN DEFAULT 0,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create swot_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swot_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                category VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                impact_level INTEGER NOT NULL,
                probability INTEGER,
                urgency INTEGER,
                is_active BOOLEAN DEFAULT 1,
                is_addressed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create swot_actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swot_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                item_id INTEGER,
                action_log_id INTEGER NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                expected_outcome TEXT,
                success_criteria TEXT,
                effectiveness INTEGER,
                assessment_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create pestel_analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pestel_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                analysis_date TIMESTAMP NOT NULL,
                next_review_date TIMESTAMP,
                scope VARCHAR(255),
                context TEXT,
                status VARCHAR(20) DEFAULT 'active',
                is_current BOOLEAN DEFAULT 0,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create pestel_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pestel_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                category VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                impact_level INTEGER NOT NULL,
                probability INTEGER,
                timeframe VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                is_addressed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create pestel_actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pestel_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                item_id INTEGER,
                action_log_id INTEGER NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                expected_outcome TEXT,
                success_criteria TEXT,
                effectiveness INTEGER,
                assessment_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_status ON action_logs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_priority ON action_logs(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_source ON action_logs(action_source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_risk_id ON action_logs(risk_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_assigned_to ON action_logs(assigned_to)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_department_id ON action_logs(department_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_created_at ON action_logs(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_logs_due_date ON action_logs(due_date)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_progress_action_id ON action_progress(action_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_progress_updated_at ON action_progress(updated_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interested_parties_category ON interested_parties(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interested_parties_is_active ON interested_parties(is_active)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_swot_analyses_status ON swot_analyses(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_swot_analyses_is_current ON swot_analyses(is_current)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pestel_analyses_status ON pestel_analyses(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pestel_analyses_is_current ON pestel_analyses(is_current)')
        
        conn.commit()
        print("✅ Actions Log System tables created successfully!")
        
        # Show table count
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%action%' OR name LIKE '%party%' OR name LIKE '%swot%' OR name LIKE '%pestel%'")
        tables = cursor.fetchall()
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_actions_log_tables()
