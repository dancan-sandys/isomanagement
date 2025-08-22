# -*- coding: utf-8 -*-
"""
Analytics Dashboard Widgets Table Migration
Phase 4: Create analytics_dashboard_widgets table
"""

import sqlite3
import os
from datetime import datetime

def create_analytics_dashboard_widgets_table():
    """Create analytics_dashboard_widgets table"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating analytics_dashboard_widgets table...")
    
    try:
        # Create analytics_dashboard_widgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_dashboard_widgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dashboard_id INTEGER NOT NULL,
                widget_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                position_x INTEGER NOT NULL,
                position_y INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                data_source VARCHAR(100),
                data_config TEXT,
                chart_config TEXT,
                refresh_interval INTEGER,
                is_visible BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_dashboard_widgets_dashboard_id ON analytics_dashboard_widgets(dashboard_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_dashboard_widgets_position ON analytics_dashboard_widgets(position_y, position_x)')
        
        conn.commit()
        print("✅ analytics_dashboard_widgets table created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_analytics_dashboard_widgets_table()
