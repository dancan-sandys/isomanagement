#!/usr/bin/env python3
"""
Dairy Company Data Seeder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_dairy_data():
    """Create comprehensive data for DairyCo Processing Ltd"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("🏭 Creating data for DairyCo Processing Ltd...")
            
            # Create roles
            create_roles(conn)
            
            # Create users
            create_users(conn)
            
            # Create system settings
            create_settings(conn)
            
            # Create documents
            create_documents(conn)
            
            # Create products
            create_products(conn)
            
            print("✅ DairyCo Processing Ltd data created successfully!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

def create_roles(conn):
    """Create user roles"""
    print("👥 Creating roles...")
    
    roles = [
        ("ADMIN", "System Administrator"),
        ("QA_MANAGER", "Quality Assurance Manager"),
        ("PRODUCTION_MANAGER", "Production Manager"),
        ("MAINTENANCE", "Maintenance Staff")
    ]
    
    for name, description in roles:
        result = conn.execute(text("SELECT id FROM roles WHERE name = :name"), {"name": name})
        if not result.fetchone():
            conn.execute(text("""
                INSERT INTO roles (name, description, is_default, is_editable, is_active, created_at, updated_at)
                VALUES (:name, :description, false, true, true, datetime('now'), datetime('now'))
            """), {"name": name, "description": description})
    
    conn.commit()
    print("✅ Roles created")

def create_users(conn):
    """Create company users"""
    print("👥 Creating users...")
    
    # Get role IDs
    role_ids = {}
    for role_name in ["ADMIN", "QA_MANAGER", "PRODUCTION_MANAGER", "MAINTENANCE"]:
        result = conn.execute(text("SELECT id FROM roles WHERE name = :name"), {"name": role_name})
        role = result.fetchone()
        if role:
            role_ids[role_name] = role[0]
    
    users = [
        ("john.mwangi", "john.mwangi@dairyco.co.ke", "John Mwangi", "ADMIN", "Management", "General Manager"),
        ("sarah.kamau", "sarah.kamau@dairyco.co.ke", "Sarah Kamau", "ADMIN", "Quality Assurance", "Quality Manager"),
        ("peter.odhiambo", "peter.odhiambo@dairyco.co.ke", "Peter Odhiambo", "PRODUCTION_MANAGER", "Production", "Production Manager")
    ]
    
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq"
    
    for username, email, full_name, role_name, department, position in users:
        result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
        if not result.fetchone():
            conn.execute(text("""
                INSERT INTO users (username, email, hashed_password, full_name, role_id, status, department, position, is_active, created_at, updated_at)
                VALUES (:username, :email, :hashed_password, :full_name, :role_id, 'ACTIVE', :department, :position, true, datetime('now'), datetime('now'))
            """), {
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "full_name": full_name,
                "role_id": role_ids.get(role_name, 1),
                "department": department,
                "position": position
            })
    
    conn.commit()
    print("✅ Users created")

def create_settings(conn):
    """Create system settings"""
    print("⚙️ Creating settings...")
    
    settings = [
        ("company_name", "DairyCo Processing Ltd", "Company Name", "Company name", "COMPANY_INFO"),
        ("company_address", "P.O. Box 12345, Nairobi, Kenya", "Company Address", "Company address", "COMPANY_INFO"),
        ("iso_certification", "ISO 22000:2018", "ISO Certification", "ISO certification", "CERTIFICATION")
    ]
    
    for key, value, display_name, description, category in settings:
        result = conn.execute(text("SELECT id FROM application_settings WHERE key = :key"), {"key": key})
        if not result.fetchone():
            conn.execute(text("""
                INSERT INTO application_settings (key, value, display_name, description, category, setting_type, created_at, updated_at)
                VALUES (:key, :value, :display_name, :description, :category, 'STRING', datetime('now'), datetime('now'))
            """), {
                "key": key,
                "value": value,
                "display_name": display_name,
                "description": description,
                "category": category
            })
    
    conn.commit()
    print("✅ Settings created")

def create_documents(conn):
    """Create company documents"""
    print("📄 Creating documents...")
    
    documents = [
        ("FSMS-001", "Food Safety Management System Manual", "Main FSMS manual", "general", "manual", "2.0"),
        ("HACCP-001", "HACCP Plan - Milk Processing", "HACCP plan for milk processing", "haccp", "plan", "1.5"),
        ("SOP-001", "Good Manufacturing Practices (GMP)", "Standard operating procedures for GMP", "quality", "procedure", "3.0")
    ]
    
    for doc_num, title, description, category, doc_type, version in documents:
        result = conn.execute(text("SELECT id FROM documents WHERE document_number = :doc_num"), {"doc_num": doc_num})
        if not result.fetchone():
            conn.execute(text("""
                INSERT INTO documents (document_number, title, description, category, document_type, status, version, file_path, created_by, created_at, updated_at)
                VALUES (:doc_num, :title, :description, :category, :doc_type, 'approved', :version, :file_path, 1, datetime('now'), datetime('now'))
            """), {
                "doc_num": doc_num,
                "title": title,
                "description": description,
                "category": category,
                "doc_type": doc_type,
                "version": version,
                "file_path": f"documents/{doc_num.lower()}_v{version}.pdf"
            })
    
    conn.commit()
    print("✅ Documents created")

def create_products(conn):
    """Create HACCP products"""
    print("🥛 Creating products...")
    
    products = [
        ("MILK-001", "Fresh Milk", "Pasteurized fresh milk 3.25% fat", "Dairy", "2.0"),
        ("YOG-001", "Greek Yogurt", "Greek style yogurt 10% fat", "Fermented Dairy", "1.5"),
        ("CHEESE-001", "Cheddar Cheese", "Aged cheddar cheese 32% fat", "Cheese", "1.8")
    ]
    
    for product_code, name, description, category, version in products:
        result = conn.execute(text("SELECT id FROM products WHERE product_code = :code"), {"code": product_code})
        if not result.fetchone():
            conn.execute(text("""
                INSERT INTO products (product_code, name, description, category, haccp_plan_version, haccp_plan_approved, created_at, updated_at)
                VALUES (:code, :name, :description, :category, :version, true, datetime('now'), datetime('now'))
            """), {
                "code": product_code,
                "name": name,
                "description": description,
                "category": category,
                "version": version
            })
    
    conn.commit()
    print("✅ Products created")

if __name__ == "__main__":
    create_dairy_data()
