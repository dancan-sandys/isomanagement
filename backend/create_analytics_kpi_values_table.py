# -*- coding: utf-8 -*-
"""
Analytics KPI Values Table Migration
Phase 4: Create analytics_kpi_values table
"""

import sqlite3
import os
from datetime import datetime

def create_analytics_kpi_values_table():
    """Create analytics_kpi_values table"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating analytics_kpi_values table...")
    
    try:
        # Create analytics_kpi_values table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_kpi_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kpi_id INTEGER NOT NULL,
                value REAL NOT NULL,
                department_id INTEGER,
                period_start TIMESTAMP,
                period_end TIMESTAMP,
                context_data TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_kpi_values_kpi_id ON analytics_kpi_values(kpi_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_kpi_values_calculated_at ON analytics_kpi_values(calculated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_kpi_values_department_id ON analytics_kpi_values(department_id)')
        
        conn.commit()
        print("✅ analytics_kpi_values table created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_analytics_kpi_values_table()
