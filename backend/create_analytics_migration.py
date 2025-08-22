# -*- coding: utf-8 -*-
"""
Analytics System Database Migration
Phase 4: Create tables for analytics, reporting, and business intelligence
"""

import sqlite3
import os
from datetime import datetime

def create_analytics_tables():
    """Create analytics system tables"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating Analytics System tables...")
    
    try:
        # Create analytics_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                report_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'draft',
                report_config TEXT NOT NULL,
                chart_configs TEXT,
                export_formats TEXT,
                is_public BOOLEAN DEFAULT 0,
                department_id INTEGER,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                published_at TIMESTAMP
            )
        ''')
        
        # Create kpis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                display_name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100) NOT NULL,
                module VARCHAR(100) NOT NULL,
                calculation_method VARCHAR(50) NOT NULL,
                calculation_query TEXT,
                data_sources TEXT,
                aggregation_type VARCHAR(50),
                unit VARCHAR(50),
                decimal_places INTEGER DEFAULT 2,
                target_value REAL,
                min_value REAL,
                max_value REAL,
                warning_threshold REAL,
                critical_threshold REAL,
                alert_enabled BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                refresh_interval INTEGER DEFAULT 3600,
                last_calculation_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                created_by INTEGER NOT NULL
            )
        ''')
        
        # Create kpi_values table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpi_values (
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
        
        # Create analytics_dashboards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_dashboards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                layout_config TEXT NOT NULL,
                theme VARCHAR(50) DEFAULT 'light',
                refresh_interval INTEGER DEFAULT 300,
                is_public BOOLEAN DEFAULT 0,
                department_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                is_default BOOLEAN DEFAULT 0,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create dashboard_widgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_widgets (
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
        
        # Create trend_analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                analysis_type VARCHAR(50) NOT NULL,
                data_source VARCHAR(100) NOT NULL,
                time_period VARCHAR(50) NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                confidence_level REAL DEFAULT 0.95,
                trend_direction VARCHAR(20),
                trend_strength REAL,
                forecast_values TEXT,
                confidence_intervals TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_reports_type ON analytics_reports(report_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_reports_status ON analytics_reports(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_reports_created_at ON analytics_reports(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_reports_created_by ON analytics_reports(created_by)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpis_category ON kpis(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpis_module ON kpis(module)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpis_is_active ON kpis(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpis_name ON kpis(name)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpi_values_kpi_id ON kpi_values(kpi_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpi_values_calculated_at ON kpi_values(calculated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpi_values_department_id ON kpi_values(department_id)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_dashboards_is_active ON analytics_dashboards(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_dashboards_created_at ON analytics_dashboards(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_dashboards_created_by ON analytics_dashboards(created_by)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dashboard_widgets_dashboard_id ON dashboard_widgets(dashboard_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dashboard_widgets_position ON dashboard_widgets(position_y, position_x)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trend_analyses_is_active ON trend_analyses(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trend_analyses_analysis_type ON trend_analyses(analysis_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trend_analyses_created_at ON trend_analyses(created_at)')
        
        conn.commit()
        print("✅ Analytics System tables created successfully!")
        
        # Show table count
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%analytics%' OR name LIKE '%kpi%' OR name LIKE '%dashboard%' OR name LIKE '%trend%'")
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
    create_analytics_tables()
