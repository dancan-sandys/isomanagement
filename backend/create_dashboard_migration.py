#!/usr/bin/env python3
"""
Dashboard Database Migration Script
Creates all dashboard-related tables and seeds initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db, engine, Base
from app.models.dashboard import (
    DashboardConfiguration, KPIDefinition, KPIValue, DashboardWidget,
    DashboardAlert, ScheduledReport, DashboardAuditLog, Department
)
from app.models.user import User
from app.models.rbac import Role

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_dashboard_tables():
    """Create all dashboard-related tables"""
    print("🔄 Creating dashboard tables...")
    
    try:
        # List of tables to create
        tables_to_create = [
            (Department.__table__, "departments"),
            (DashboardConfiguration.__table__, "dashboard_configurations"),
            (KPIDefinition.__table__, "kpi_definitions"),
            (KPIValue.__table__, "kpi_values"),
            (DashboardWidget.__table__, "dashboard_widgets"),
            (DashboardAlert.__table__, "dashboard_alerts"),
            (ScheduledReport.__table__, "scheduled_reports"),
            (DashboardAuditLog.__table__, "dashboard_audit_logs")
        ]
        
        created_tables = []
        existing_tables = []
        
        for table_obj, table_name in tables_to_create:
            if check_table_exists(table_name):
                existing_tables.append(table_name)
                print(f"  ✅ Table '{table_name}' already exists")
            else:
                Base.metadata.create_all(bind=engine, tables=[table_obj])
                created_tables.append(table_name)
                print(f"  ✨ Created table '{table_name}'")
        
        if created_tables:
            print(f"\n🎉 Successfully created {len(created_tables)} new tables:")
            for table in created_tables:
                print(f"    - {table}")
        
        if existing_tables:
            print(f"\n📋 {len(existing_tables)} tables already existed:")
            for table in existing_tables:
                print(f"    - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating dashboard tables: {e}")
        return False

def create_performance_indexes():
    """Create performance indexes for dashboard queries"""
    print("\n🚀 Creating performance indexes...")
    
    indexes = [
        # KPI Values indexes
        ("idx_kpi_values_period", "CREATE INDEX IF NOT EXISTS idx_kpi_values_period ON kpi_values(period_start, period_end);"),
        ("idx_kpi_values_kpi_id", "CREATE INDEX IF NOT EXISTS idx_kpi_values_kpi_id ON kpi_values(kpi_definition_id);"),
        ("idx_kpi_values_department", "CREATE INDEX IF NOT EXISTS idx_kpi_values_department ON kpi_values(department_id, period_start);"),
        ("idx_kpi_values_calculated_at", "CREATE INDEX IF NOT EXISTS idx_kpi_values_calculated_at ON kpi_values(calculated_at DESC);"),
        
        # Dashboard configurations indexes
        ("idx_dashboard_user_role", "CREATE INDEX IF NOT EXISTS idx_dashboard_user_role ON dashboard_configurations(user_id, role_id);"),
        ("idx_dashboard_active", "CREATE INDEX IF NOT EXISTS idx_dashboard_active ON dashboard_configurations(is_active, is_default);"),
        
        # Dashboard alerts indexes
        ("idx_dashboard_alerts_active", "CREATE INDEX IF NOT EXISTS idx_dashboard_alerts_active ON dashboard_alerts(is_active, kpi_definition_id);"),
        ("idx_dashboard_alerts_triggered", "CREATE INDEX IF NOT EXISTS idx_dashboard_alerts_triggered ON dashboard_alerts(last_triggered_at DESC);"),
        
        # Audit log indexes
        ("idx_audit_log_user_action", "CREATE INDEX IF NOT EXISTS idx_audit_log_user_action ON dashboard_audit_logs(user_id, action, created_at);"),
        ("idx_audit_log_resource", "CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON dashboard_audit_logs(resource_type, resource_id);"),
        ("idx_audit_log_created_at", "CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON dashboard_audit_logs(created_at DESC);"),
        
        # KPI definitions indexes
        ("idx_kpi_definitions_category", "CREATE INDEX IF NOT EXISTS idx_kpi_definitions_category ON kpi_definitions(category, is_active);"),
        ("idx_kpi_definitions_module", "CREATE INDEX IF NOT EXISTS idx_kpi_definitions_module ON kpi_definitions(module, is_active);"),
        
        # Departments indexes
        ("idx_departments_active", "CREATE INDEX IF NOT EXISTS idx_departments_active ON departments(is_active);"),
        ("idx_departments_parent", "CREATE INDEX IF NOT EXISTS idx_departments_parent ON departments(parent_id);"),
    ]
    
    try:
        with engine.connect() as conn:
            created_indexes = []
            for index_name, sql in indexes:
                try:
                    conn.execute(text(sql))
                    created_indexes.append(index_name)
                    print(f"  ✨ Created index '{index_name}'")
                except Exception as e:
                    print(f"  ⚠️  Index '{index_name}' may already exist or failed: {str(e)[:50]}...")
            
            conn.commit()
            print(f"\n🎯 Successfully processed {len(created_indexes)} indexes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False

def seed_departments():
    """Seed initial department data"""
    print("\n🏢 Seeding department data...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        departments = [
            {"name": "Quality Assurance", "code": "QA", "description": "Quality Assurance Department", "level": 0},
            {"name": "Production", "code": "PROD", "description": "Production Department", "level": 0},
            {"name": "Maintenance", "code": "MAINT", "description": "Maintenance Department", "level": 0},
            {"name": "Purchasing", "code": "PURCH", "description": "Purchasing Department", "level": 0},
            {"name": "Laboratory", "code": "LAB", "description": "Quality Control Laboratory", "level": 0},
            {"name": "Warehouse", "code": "WH", "description": "Warehouse Operations", "level": 0},
            {"name": "Food Safety", "code": "FS", "description": "Food Safety Team", "level": 0},
            {"name": "Engineering", "code": "ENG", "description": "Engineering Department", "level": 0},
        ]
        
        created_count = 0
        for dept_data in departments:
            existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
            if not existing:
                dept = Department(**dept_data)
                db.add(dept)
                created_count += 1
                print(f"  ✨ Created department: {dept_data['name']}")
            else:
                print(f"  ✅ Department already exists: {dept_data['name']}")
        
        db.commit()
        print(f"\n🏢 Department seeding completed: {created_count} new departments created")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding departments: {e}")
        return False
    finally:
        db.close()

def seed_kpi_definitions():
    """Seed core KPI definitions"""
    print("\n📊 Seeding KPI definitions...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        kpi_definitions = [
            {
                "name": "ccp_compliance_rate",
                "display_name": "CCP Compliance Rate",
                "description": "Percentage of CCP monitoring points meeting critical limits",
                "category": "haccp_compliance",
                "module": "haccp",
                "calculation_formula": """
                    SELECT 
                        COALESCE(
                            (COUNT(CASE WHEN within_limits = true THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)),
                            0
                        ) as value
                    FROM ccp_monitoring_logs 
                    WHERE created_at >= :period_start AND created_at <= :period_end
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "%",
                "target_value": 98.0,
                "target_operator": ">=",
                "requires_department_filter": True
            },
            {
                "name": "nc_count_monthly",
                "display_name": "Non-Conformances (Monthly)",
                "description": "Total number of non-conformances reported this month",
                "category": "nc_capa",
                "module": "nc_capa",
                "calculation_formula": """
                    SELECT COUNT(*) as value
                    FROM non_conformances 
                    WHERE created_at >= :period_start AND created_at <= :period_end
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "count",
                "target_value": 5.0,
                "target_operator": "<=",
                "requires_department_filter": True
            },
            {
                "name": "capa_closure_rate",
                "display_name": "CAPA Closure Rate",
                "description": "Percentage of corrective actions completed on time",
                "category": "nc_capa",
                "module": "nc_capa",
                "calculation_formula": """
                    SELECT 
                        COALESCE(
                            (COUNT(CASE WHEN status = 'completed' AND completed_date <= due_date THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)),
                            0
                        ) as value
                    FROM capa_actions 
                    WHERE created_at >= :period_start AND created_at <= :period_end
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "%",
                "target_value": 90.0,
                "target_operator": ">=",
                "requires_department_filter": True
            },
            {
                "name": "supplier_approval_rate",
                "display_name": "Supplier Approval Rate",
                "description": "Percentage of suppliers with approved status",
                "category": "supplier_performance",
                "module": "suppliers",
                "calculation_formula": """
                    SELECT 
                        COALESCE(
                            (COUNT(CASE WHEN approval_status = 'approved' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)),
                            0
                        ) as value
                    FROM suppliers
                    WHERE is_active = true
                """,
                "unit": "%",
                "target_value": 95.0,
                "target_operator": ">=",
                "requires_department_filter": False
            },
            {
                "name": "training_completion_rate",
                "display_name": "Training Completion Rate",
                "description": "Percentage of required training completed",
                "category": "training_competency",
                "module": "training",
                "calculation_formula": """
                    SELECT 
                        COALESCE(
                            (COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)),
                            0
                        ) as value
                    FROM training_attendance
                    WHERE created_at >= :period_start AND created_at <= :period_end
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "%",
                "target_value": 95.0,
                "target_operator": ">=",
                "requires_department_filter": True
            },
            {
                "name": "document_currency_rate",
                "display_name": "Document Currency Rate",
                "description": "Percentage of documents that are current and approved",
                "category": "document_control",
                "module": "documents",
                "calculation_formula": """
                    SELECT 
                        COALESCE(
                            (COUNT(CASE WHEN status = 'approved' AND is_current = true THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)),
                            0
                        ) as value
                    FROM documents
                    WHERE is_active = true
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "%",
                "target_value": 98.0,
                "target_operator": ">=",
                "requires_department_filter": True
            },
            {
                "name": "prp_compliance_score",
                "display_name": "PRP Compliance Score",
                "description": "Average compliance score across all PRP programs",
                "category": "prp_performance",
                "module": "prp",
                "calculation_formula": """
                    SELECT 
                        COALESCE(AVG(compliance_score), 0) as value
                    FROM prp_programs 
                    WHERE is_active = true
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "score",
                "target_value": 95.0,
                "target_operator": ">=",
                "requires_department_filter": True
            },
            {
                "name": "audit_findings_open",
                "display_name": "Open Audit Findings",
                "description": "Number of open audit findings requiring action",
                "category": "audit_management",
                "module": "audits",
                "calculation_formula": """
                    SELECT COUNT(*) as value
                    FROM audit_findings 
                    WHERE status IN ('open', 'in_progress')
                    AND (:department_id IS NULL OR department_id = :department_id)
                """,
                "unit": "count",
                "target_value": 3.0,
                "target_operator": "<=",
                "requires_department_filter": True
            }
        ]
        
        created_count = 0
        for kpi_data in kpi_definitions:
            existing = db.query(KPIDefinition).filter(KPIDefinition.name == kpi_data["name"]).first()
            if not existing:
                kpi = KPIDefinition(**kpi_data)
                db.add(kpi)
                created_count += 1
                print(f"  ✨ Created KPI: {kpi_data['display_name']}")
            else:
                print(f"  ✅ KPI already exists: {kpi_data['display_name']}")
        
        db.commit()
        print(f"\n📊 KPI definitions seeding completed: {created_count} new KPIs created")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding KPI definitions: {e}")
        return False
    finally:
        db.close()

def seed_dashboard_widgets():
    """Seed default dashboard widgets"""
    print("\n🧩 Seeding dashboard widgets...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        widgets = [
            {
                "name": "kpi_card_widget",
                "display_name": "KPI Card",
                "description": "Display single KPI value with trend indicator",
                "component_name": "KPICardWidget",
                "category": "kpis",
                "widget_type": "kpi_card",
                "required_permissions": ["dashboard:view"],
                "default_size": "small",
                "min_size": {"w": 1, "h": 1},
                "max_size": {"w": 2, "h": 2},
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "kpi_id": {"type": "integer"},
                        "show_trend": {"type": "boolean", "default": True},
                        "show_target": {"type": "boolean", "default": True},
                        "title": {"type": "string"}
                    },
                    "required": ["kpi_id"]
                }
            },
            {
                "name": "line_chart_widget",
                "display_name": "Trend Chart",
                "description": "Line chart showing KPI trends over time",
                "component_name": "LineChartWidget",
                "category": "charts",
                "widget_type": "line_chart",
                "required_permissions": ["dashboard:view"],
                "default_size": "large",
                "min_size": {"w": 2, "h": 2},
                "max_size": {"w": 4, "h": 4},
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "kpi_ids": {"type": "array", "items": {"type": "integer"}},
                        "period_days": {"type": "integer", "default": 30},
                        "show_target_line": {"type": "boolean", "default": True},
                        "title": {"type": "string"}
                    },
                    "required": ["kpi_ids"]
                }
            },
            {
                "name": "compliance_gauge_widget",
                "display_name": "Compliance Gauge",
                "description": "Gauge chart showing compliance score",
                "component_name": "ComplianceGaugeWidget",
                "category": "charts",
                "widget_type": "gauge_chart",
                "required_permissions": ["dashboard:view"],
                "default_size": "medium",
                "min_size": {"w": 2, "h": 2},
                "max_size": {"w": 3, "h": 3},
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "compliance_type": {"type": "string", "enum": ["overall", "haccp", "prp"]},
                        "department_filter": {"type": "boolean", "default": True},
                        "title": {"type": "string"}
                    },
                    "required": ["compliance_type"]
                }
            },
            {
                "name": "alert_feed_widget",
                "display_name": "Alert Feed",
                "description": "Live feed of system alerts and notifications",
                "component_name": "AlertFeedWidget",
                "category": "alerts",
                "widget_type": "alert_feed",
                "required_permissions": ["dashboard:view", "notifications:view"],
                "default_size": "medium",
                "min_size": {"w": 2, "h": 2},
                "max_size": {"w": 4, "h": 4},
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "max_items": {"type": "integer", "default": 10},
                        "alert_levels": {"type": "array", "items": {"type": "string"}, "default": ["critical", "warning"]},
                        "auto_refresh": {"type": "boolean", "default": True},
                        "title": {"type": "string"}
                    }
                }
            },
            {
                "name": "bar_chart_widget",
                "display_name": "Bar Chart",
                "description": "Bar chart for comparing multiple KPIs",
                "component_name": "BarChartWidget",
                "category": "charts",
                "widget_type": "bar_chart",
                "required_permissions": ["dashboard:view"],
                "default_size": "large",
                "min_size": {"w": 2, "h": 2},
                "max_size": {"w": 4, "h": 3},
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "kpi_ids": {"type": "array", "items": {"type": "integer"}},
                        "chart_orientation": {"type": "string", "enum": ["horizontal", "vertical"], "default": "vertical"},
                        "show_values": {"type": "boolean", "default": True},
                        "title": {"type": "string"}
                    },
                    "required": ["kpi_ids"]
                }
            },
            {
                "name": "table_widget",
                "display_name": "Data Table",
                "description": "Tabular display of KPI data with sorting and filtering",
                "component_name": "TableWidget",
                "category": "tables",
                "widget_type": "data_table",
                "required_permissions": ["dashboard:view"],
                "default_size": "xlarge",
                "min_size": {"w": 3, "h": 2},
                "max_size": {"w": 4, "h": 4},
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "data_source": {"type": "string", "enum": ["kpis", "alerts", "recent_activity"]},
                        "columns": {"type": "array", "items": {"type": "string"}},
                        "page_size": {"type": "integer", "default": 10},
                        "sortable": {"type": "boolean", "default": True},
                        "filterable": {"type": "boolean", "default": True},
                        "title": {"type": "string"}
                    },
                    "required": ["data_source"]
                }
            }
        ]
        
        created_count = 0
        for widget_data in widgets:
            existing = db.query(DashboardWidget).filter(DashboardWidget.name == widget_data["name"]).first()
            if not existing:
                widget = DashboardWidget(**widget_data)
                db.add(widget)
                created_count += 1
                print(f"  ✨ Created widget: {widget_data['display_name']}")
            else:
                print(f"  ✅ Widget already exists: {widget_data['display_name']}")
        
        db.commit()
        print(f"\n🧩 Dashboard widgets seeding completed: {created_count} new widgets created")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding dashboard widgets: {e}")
        return False
    finally:
        db.close()

def main():
    """Main migration function"""
    print("🚀 Starting ISO 22000 FSMS Dashboard Database Setup...")
    print("=" * 60)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Create tables
    if create_dashboard_tables():
        success_count += 1
    
    # Step 2: Create indexes
    if create_performance_indexes():
        success_count += 1
    
    # Step 3: Seed departments
    if seed_departments():
        success_count += 1
    
    # Step 4: Seed KPI definitions
    if seed_kpi_definitions():
        success_count += 1
    
    # Step 5: Seed dashboard widgets
    if seed_dashboard_widgets():
        success_count += 1
    
    print("\n" + "=" * 60)
    if success_count == total_steps:
        print("🎉 Dashboard database setup completed successfully!")
        print("\n✅ Summary:")
        print("   - Database tables created/verified")
        print("   - Performance indexes created")
        print("   - Departments seeded")
        print("   - KPI definitions seeded")
        print("   - Dashboard widgets seeded")
        print("\n🚀 Next steps:")
        print("   1. Start the backend server: python -m uvicorn app.main:app --reload")
        print("   2. Check dashboard endpoints at http://localhost:8000/docs")
        print("   3. Test the new dashboard API endpoints")
    else:
        print(f"⚠️  Dashboard setup partially completed: {success_count}/{total_steps} steps successful")
        print("   Please check the errors above and retry")

if __name__ == "__main__":
    main()