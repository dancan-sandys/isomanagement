#!/usr/bin/env python3
"""
Script to create test users for the ISO 22000 FSMS system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash
from datetime import datetime

def create_test_users():
    """Create test users for demonstration"""
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Found {existing_users} existing users. Skipping user creation.")
            return
        
        # Create test users
        test_users = [
            {
                "username": "admin",
                "email": "admin@dairy.com",
                "full_name": "System Administrator",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "department": "IT",
                "position": "System Administrator",
                "phone": "+1234567890",
                "employee_id": "EMP001",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "qa_manager",
                "email": "qa.manager@dairy.com",
                "full_name": "Sarah Johnson",
                "password": "qa123",
                "role": UserRole.QA_MANAGER,
                "status": UserStatus.ACTIVE,
                "department": "Quality Assurance",
                "position": "QA Manager",
                "phone": "+1234567891",
                "employee_id": "EMP002",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "qa_specialist",
                "email": "qa.specialist@dairy.com",
                "full_name": "Michael Rodriguez",
                "password": "qa123",
                "role": UserRole.QA_SPECIALIST,
                "status": UserStatus.ACTIVE,
                "department": "Quality Assurance",
                "position": "QA Specialist",
                "phone": "+1234567892",
                "employee_id": "EMP003",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "prod_manager",
                "email": "prod.manager@dairy.com",
                "full_name": "Jennifer Lee",
                "password": "prod123",
                "role": UserRole.PRODUCTION_MANAGER,
                "status": UserStatus.ACTIVE,
                "department": "Production",
                "position": "Production Manager",
                "phone": "+1234567893",
                "employee_id": "EMP004",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "prod_operator1",
                "email": "operator1@dairy.com",
                "full_name": "Mike Chen",
                "password": "prod123",
                "role": UserRole.PRODUCTION_OPERATOR,
                "status": UserStatus.ACTIVE,
                "department": "Production",
                "position": "Production Operator",
                "phone": "+1234567894",
                "employee_id": "EMP005",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "prod_operator2",
                "email": "operator2@dairy.com",
                "full_name": "Lisa Thompson",
                "password": "prod123",
                "role": UserRole.PRODUCTION_OPERATOR,
                "status": UserStatus.ACTIVE,
                "department": "Production",
                "position": "Production Operator",
                "phone": "+1234567895",
                "employee_id": "EMP006",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "maintenance",
                "email": "maintenance@dairy.com",
                "full_name": "David Wilson",
                "password": "main123",
                "role": UserRole.MAINTENANCE,
                "status": UserStatus.ACTIVE,
                "department": "Maintenance",
                "position": "Maintenance Technician",
                "phone": "+1234567896",
                "employee_id": "EMP007",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "lab_tech",
                "email": "lab.tech@dairy.com",
                "full_name": "Emily Davis",
                "password": "lab123",
                "role": UserRole.LAB_TECHNICIAN,
                "status": UserStatus.ACTIVE,
                "department": "Laboratory",
                "position": "Lab Technician",
                "phone": "+1234567897",
                "employee_id": "EMP008",
                "is_active": True,
                "is_verified": True,
                "last_login": datetime.now()
            },
            {
                "username": "new_user",
                "email": "new.user@dairy.com",
                "full_name": "Alex Smith",
                "password": "new123",
                "role": UserRole.VIEWER,
                "status": UserStatus.PENDING_APPROVAL,
                "department": "Quality Assurance",
                "position": "Trainee",
                "phone": "+1234567898",
                "employee_id": "EMP009",
                "is_active": False,
                "is_verified": False,
                "last_login": None
            },
            {
                "username": "inactive_user",
                "email": "inactive@dairy.com",
                "full_name": "Robert Brown",
                "password": "inactive123",
                "role": UserRole.PRODUCTION_OPERATOR,
                "status": UserStatus.INACTIVE,
                "department": "Production",
                "position": "Former Operator",
                "phone": "+1234567899",
                "employee_id": "EMP010",
                "is_active": False,
                "is_verified": True,
                "last_login": None
            }
        ]
        
        # Create users
        for user_data in test_users:
            hashed_password = get_password_hash(user_data["password"])
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"],
                status=user_data["status"],
                department=user_data["department"],
                position=user_data["position"],
                phone=user_data["phone"],
                employee_id=user_data["employee_id"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"],
                last_login=user_data["last_login"],
                created_by=1  # Admin user
            )
            
            db.add(user)
            print(f"Created user: {user_data['full_name']} ({user_data['username']})")
        
        db.commit()
        print(f"\nSuccessfully created {len(test_users)} test users!")
        print("\nTest user credentials:")
        print("=" * 50)
        for user_data in test_users:
            print(f"Username: {user_data['username']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {user_data['role'].value}")
            print(f"Status: {user_data['status'].value}")
            print("-" * 30)
        
    except Exception as e:
        print(f"Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test users for ISO 22000 FSMS...")
    create_test_users()
    print("Done!") 