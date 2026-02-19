#!/usr/bin/env python3
"""
Phase 2: Performance Optimization Script
Comprehensive database and API performance optimization
"""

import sqlite3
import os
from datetime import datetime
import time

def optimize_database_performance():
    """Optimize database performance with indexes and query improvements"""
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Starting Phase 2: Performance Optimization...")
        
        # 1. Database Indexing for Performance
        print("\n📊 1. Creating Performance Indexes...")
        
        # Critical indexes for frequently queried tables
        performance_indexes = [
            # User and authentication indexes
            ("idx_users_username", "users(username)"),
            ("idx_users_email", "users(email)"),
            ("idx_user_sessions_token", "user_sessions(session_token)"),
            ("idx_user_sessions_user_id", "user_sessions(user_id)"),
            
            # Document indexes
            ("idx_documents_status", "documents(status)"),
            ("idx_documents_category", "documents(category)"),
            ("idx_documents_created_by", "documents(created_by)"),
            ("idx_documents_created_at", "documents(created_at)"),
            ("idx_document_versions_document_id", "document_versions(document_id)"),
            
            # HACCP indexes
            ("idx_haccp_plans_status", "haccp_plans(status)"),
            ("idx_ccps_plan_id", "ccps(plan_id)"),
            ("idx_ccp_monitoring_logs_ccp_id", "ccp_monitoring_logs(ccp_id)"),
            ("idx_ccp_monitoring_logs_created_at", "ccp_monitoring_logs(created_at)"),
            
            # PRP indexes
            ("idx_prp_programs_status", "prp_programs(status)"),
            ("idx_prp_checklists_program_id", "prp_checklists(program_id)"),
            ("idx_prp_risk_assessments_program_id", "prp_risk_assessments(program_id)"),
            
            # Supplier indexes
            ("idx_suppliers_status", "suppliers(status)"),
            ("idx_supplier_evaluations_supplier_id", "supplier_evaluations(supplier_id)"),
            ("idx_supplier_evaluations_evaluation_date", "supplier_evaluations(evaluation_date)"),
            
            # Traceability indexes
            ("idx_batches_batch_number", "batches(batch_number)"),
            ("idx_batches_status", "batches(status)"),
            ("idx_batches_production_date", "batches(production_date)"),
            ("idx_recalls_recall_number", "recalls(recall_number)"),
            ("idx_recalls_status", "recalls(status)"),
            
            # Audit indexes (already created in Phase 1)
            ("idx_audits_program_id", "audits(program_id)"),
            ("idx_audits_status", "audits(status)"),
            ("idx_audits_audit_type", "audits(audit_type)"),
            ("idx_audits_created_by", "audits(created_by)"),
            ("idx_audits_start_date", "audits(start_date)"),
            ("idx_audits_end_date", "audits(end_date)"),
            ("idx_audits_risk_register_item_id", "audits(risk_register_item_id)"),
            
            # Equipment indexes
            ("idx_equipment_equipment_type", "equipment(equipment_type)"),
            ("idx_equipment_is_active", "equipment(is_active)"),
            ("idx_maintenance_plans_equipment_id", "maintenance_plans(equipment_id)"),
            ("idx_maintenance_plans_next_due_at", "maintenance_plans(next_due_at)"),
            ("idx_calibration_plans_equipment_id", "calibration_plans(equipment_id)"),
            ("idx_calibration_plans_next_due_at", "calibration_plans(next_due_at)"),
            
            # Training indexes
            ("idx_training_programs_status", "training_programs(status)"),
            ("idx_training_sessions_program_id", "training_sessions(program_id)"),
            ("idx_training_attendance_session_id", "training_attendance(session_id)"),
            
            # Risk management indexes
            ("idx_risk_register_status", "risk_register(status)"),
            ("idx_risk_register_risk_level", "risk_register(risk_level)"),
            ("idx_risk_actions_risk_id", "risk_actions(risk_id)"),
            
            # Non-conformance indexes
            ("idx_non_conformances_status", "non_conformances(status)"),
            ("idx_non_conformances_source", "non_conformances(source)"),
            ("idx_non_conformances_created_at", "non_conformances(created_at)"),
            ("idx_capa_actions_nc_id", "capa_actions(nc_id)"),
            ("idx_capa_actions_status", "capa_actions(status)"),
            
            # Management review indexes
            ("idx_management_reviews_status", "management_reviews(status)"),
            ("idx_management_reviews_review_date", "management_reviews(review_date)"),
            
            # Notification indexes
            ("idx_notifications_user_id", "notifications(user_id)"),
            ("idx_notifications_read", "notifications(read)"),
            ("idx_notifications_created_at", "notifications(created_at)"),
            
            # Composite indexes for complex queries
            ("idx_documents_status_created_at", "documents(status, created_at)"),
            ("idx_audits_status_start_date", "audits(status, start_date)"),
            ("idx_non_conformances_status_created_at", "non_conformances(status, created_at)"),
            ("idx_supplier_evaluations_supplier_id_date", "supplier_evaluations(supplier_id, evaluation_date)"),
            ("idx_ccp_monitoring_logs_ccp_id_date", "ccp_monitoring_logs(ccp_id, created_at)"),
        ]
        
        created_indexes = 0
        existing_indexes = 0
        
        for index_name, index_def in performance_indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
                if cursor.rowcount > 0:
                    print(f"✅ Created index: {index_name}")
                    created_indexes += 1
                else:
                    print(f"✅ Index already exists: {index_name}")
                    existing_indexes += 1
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"✅ Index already exists: {index_name}")
                    existing_indexes += 1
                else:
                    print(f"⚠️ Could not create index {index_name}: {e}")
        
        print(f"\n📈 Index Summary: Created {created_indexes} new indexes, {existing_indexes} already existed")
        
        # 2. Database Statistics and Optimization
        print("\n🔧 2. Optimizing Database Statistics...")
        
        # Update database statistics for query planner
        cursor.execute("ANALYZE")
        print("✅ Updated database statistics")
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        print("✅ Enabled WAL mode for better concurrency")
        
        # Set cache size for better performance
        cursor.execute("PRAGMA cache_size=10000")
        print("✅ Set cache size to 10MB")
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        print("✅ Enabled foreign key constraints")
        
        # 3. Performance Monitoring Setup
        print("\n📊 3. Setting up Performance Monitoring...")
        
        # Create performance monitoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY,
                endpoint_name VARCHAR(255),
                response_time_ms INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        """)
        
        # Create index on performance metrics
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_metrics_endpoint ON performance_metrics(endpoint_name)")
        
        print("✅ Created performance monitoring table and indexes")
        
        # 4. Query Performance Analysis
        print("\n🔍 4. Analyzing Query Performance...")
        
        # Test some common queries for performance
        test_queries = [
            ("Dashboard Stats", "SELECT COUNT(*) FROM documents WHERE status = 'active'"),
            ("Recent Audits", "SELECT COUNT(*) FROM audits WHERE created_at >= date('now', '-30 days')"),
            ("Active Suppliers", "SELECT COUNT(*) FROM suppliers WHERE status = 'active'"),
            ("Pending CAPAs", "SELECT COUNT(*) FROM capa_actions WHERE status = 'pending'"),
            ("Overdue Calibrations", "SELECT COUNT(*) FROM calibration_plans WHERE next_due_at < datetime('now')"),
        ]
        
        query_times = []
        for query_name, query in test_queries:
            start_time = time.time()
            cursor.execute(query)
            result = cursor.fetchone()
            end_time = time.time()
            query_time_ms = (end_time - start_time) * 1000
            query_times.append((query_name, query_time_ms, result[0]))
            print(f"⏱️ {query_name}: {query_time_ms:.2f}ms (result: {result[0]})")
        
        # Calculate average query time
        avg_query_time = sum(time for _, time, _ in query_times) / len(query_times)
        print(f"\n📊 Average query time: {avg_query_time:.2f}ms")
        
        # 5. Database Size Analysis
        print("\n💾 5. Database Size Analysis...")
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        db_size_mb = (page_count * page_size) / (1024 * 1024)
        
        print(f"📊 Database Statistics:")
        print(f"   - Tables: {table_count}")
        print(f"   - Size: {db_size_mb:.2f} MB")
        print(f"   - Pages: {page_count}")
        print(f"   - Page size: {page_size} bytes")
        
        # 6. Performance Recommendations
        print("\n💡 6. Performance Recommendations...")
        
        recommendations = []
        
        if avg_query_time > 100:
            recommendations.append("Consider implementing query result caching")
        
        if db_size_mb > 100:
            recommendations.append("Consider implementing data archiving strategy")
        
        if len(query_times) > 0:
            slowest_query = max(query_times, key=lambda x: x[1])
            if slowest_query[1] > 50:
                recommendations.append(f"Optimize slowest query: {slowest_query[0]} ({slowest_query[1]:.2f}ms)")
        
        if recommendations:
            print("🔧 Performance Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("✅ No immediate performance optimizations needed")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Phase 2: Database Performance Optimization completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during performance optimization: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def create_performance_monitoring_middleware():
    """Create performance monitoring middleware for FastAPI"""
    
    middleware_code = '''
from fastapi import Request
import time
import sqlite3
from datetime import datetime

async def performance_monitoring_middleware(request: Request, call_next):
    """Middleware to monitor API performance"""
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate response time
    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)
    
    # Log performance metrics
    try:
        conn = sqlite3.connect("iso22000_fsms.db")
        cursor = conn.cursor()
        
        endpoint_name = request.url.path
        user_id = getattr(request.state, 'user_id', None)
        success = 200 <= response.status_code < 400
        error_message = None if success else f"HTTP {response.status_code}"
        
        cursor.execute("""
            INSERT INTO performance_metrics 
            (endpoint_name, response_time_ms, user_id, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (endpoint_name, response_time_ms, user_id, success, error_message))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error logging performance metrics: {e}")
    
    return response
'''
    
    # Write middleware to file
    with open("backend/app/middleware/performance_monitoring.py", "w") as f:
        f.write(middleware_code)
    
    print("✅ Created performance monitoring middleware")

if __name__ == "__main__":
    print("🚀 Phase 2: Performance Optimization")
    print("=" * 50)
    
    # Create middleware directory if it doesn't exist
    os.makedirs("backend/app/middleware", exist_ok=True)
    
    # Run database optimization
    success = optimize_database_performance()
    
    if success:
        # Create performance monitoring middleware
        create_performance_monitoring_middleware()
        
        print("\n🎉 Phase 2: Performance Optimization completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Restart the server to apply optimizations")
        print("2. Monitor performance metrics")
        print("3. Implement caching strategy if needed")
        print("4. Move to Phase 3: User Experience Enhancements")
    else:
        print("\n💥 Phase 2: Performance Optimization failed!")

