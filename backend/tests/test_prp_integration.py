"""
Integration Tests for PRP Module - ISO 22002-1:2025 Compliance

This module contains comprehensive integration tests for the PRP module,
testing all major components and their interactions to ensure proper
functionality and ISO 22002-1:2025 compliance.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, RiskAssessment, 
    RiskControl, CorrectiveAction, PreventiveAction, RiskMatrix
)
from app.models.user import User
from app.models.document import DocumentTemplate
from app.models.notification import Notification
from app.core.database import get_db
from app.core.config import settings

client = TestClient(app)

class TestPRPIntegration:
    """Integration tests for PRP module components"""
    
    @pytest.fixture
    def test_role(self, db: Session):
        """Create a test role for testing"""
        from app.models.rbac import Role
        
        role = Role(
            name="Test Role",
            description="Test role for integration testing",
            is_default=True,
            is_editable=True,
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @pytest.fixture
    def test_user(self, db: Session, test_role):
        """Create a test user for testing"""
        from app.core.security import get_password_hash
        
        user = User(
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("testpassword"),
            role_id=test_role.id,  # Use the created role ID
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @pytest.fixture
    def test_prp_program(self, db: Session, test_user):
        """Create a test PRP program"""
        program = PRPProgram(
            program_code="TEST-PRP-001",
            name="Test PRP Program",
            description="Test program for integration testing",
            category="cleaning_and_sanitizing",
            objective="Ensure proper cleaning and sanitizing",
            scope="Production area",
            sop_reference="SOP-CS-001",
            frequency="daily",
            status="active",
            assigned_to=test_user.id,
            created_by=test_user.id
        )
        db.add(program)
        db.commit()
        db.refresh(program)
        return program
    
    def test_prp_program_creation_with_risk_assessment(self, db: Session, test_user):
        """Test creating a PRP program with associated risk assessment"""
        # Create PRP program
        program_data = {
            "program_code": "TEST-PRP-002",
            "name": "Test Program with Risk Assessment",
            "description": "Test program with risk assessment",
            "category": "cleaning_and_sanitizing",
            "objective": "Ensure proper cleaning and sanitizing",
            "scope": "Production area",
            "sop_reference": "SOP-CS-002",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Create risk assessment for the program
        risk_data = {
            "hazard_identified": "Chemical contamination",
            "hazard_description": "Risk of chemical contamination during cleaning",
            "likelihood_level": "Medium",
            "severity_level": "High",
            "existing_controls": "PPE, training",
            "additional_controls_required": "Enhanced monitoring",
            "control_effectiveness": "Good",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/risk-assessments", json=risk_data)
        assert response.status_code == 201
        risk_assessment = response.json()
        
        # Verify risk assessment was created correctly
        assert risk_assessment["hazard_identified"] == "Chemical contamination"
        assert risk_assessment["program_id"] == program["id"]
    
    def test_risk_assessment_with_controls(self, db: Session, test_user, test_prp_program):
        """Test risk assessment with associated controls"""
        # Create risk assessment
        risk_data = {
            "hazard_identified": "Biological contamination",
            "hazard_description": "Risk of biological contamination",
            "likelihood_level": "High",
            "severity_level": "High",
            "existing_controls": "Sanitization procedures",
            "additional_controls_required": "Enhanced monitoring",
            "control_effectiveness": "Effective",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/risk-assessments", json=risk_data)
        assert response.status_code == 201
        risk_assessment = response.json()
        
        # Add risk control
        control_data = {
            "control_name": "Enhanced Sanitization Protocol",
            "control_type": "preventive",
            "control_description": "Enhanced sanitization procedures",
            "implementation_status": "implemented",
            "effectiveness_rating": 4,
            "responsible_person": "Sanitation Supervisor",
            "implementation_date": datetime.now().isoformat(),
            "review_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "cost_estimate": 5000.0,
            "priority": "high"
        }
        
        response = client.post(f"/api/v1/prp/risk-assessments/{risk_assessment['id']}/controls", json=control_data)
        assert response.status_code == 201
        control = response.json()
        
        # Verify control was created correctly
        assert control["control_name"] == "Enhanced Sanitization Protocol"
        assert control["risk_assessment_id"] == risk_assessment["id"]
    
    def test_capa_integration(self, db: Session, test_user, test_prp_program):
        """Test CAPA integration with PRP programs"""
        # Create corrective action
        capa_data = {
            "title": "Address Sanitization Issue",
            "description": "Corrective action for sanitization procedure",
            "root_cause": "Inadequate training",
            "action_type": "immediate",
            "priority": "high",
            "assigned_to": "Sanitation Team",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "effectiveness_rating": 3,
            "cost_estimate": 2000.0,
            "verification_method": "Observation and testing",
            "program_id": test_prp_program.id
        }
        
        response = client.post("/api/v1/prp/corrective-actions", json=capa_data)
        assert response.status_code == 201
        corrective_action = response.json()
        
        # Verify corrective action was created correctly
        assert corrective_action["title"] == "Address Sanitization Issue"
        assert corrective_action["program_id"] == test_prp_program.id
        
        # Create preventive action
        preventive_data = {
            "title": "Prevent Future Sanitization Issues",
            "description": "Preventive action to avoid future issues",
            "potential_issue": "Similar sanitization problems",
            "action_type": "long_term",
            "priority": "medium",
            "assigned_to": "Training Department",
            "start_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 3000.0,
            "verification_method": "Training assessment",
            "program_id": test_prp_program.id
        }
        
        response = client.post("/api/v1/prp/preventive-actions", json=preventive_data)
        assert response.status_code == 201
        preventive_action = response.json()
        
        # Verify preventive action was created correctly
        assert preventive_action["title"] == "Prevent Future Sanitization Issues"
        assert preventive_action["program_id"] == test_prp_program.id
    
    def test_checklist_integration(self, db: Session, test_user, test_prp_program):
        """Test checklist integration with PRP programs"""
        # Create checklist
        checklist_data = {
            "checklist_code": "CL-001",
            "name": "Daily Sanitization Checklist",
            "description": "Daily sanitization verification checklist",
            "scheduled_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(hours=8)).isoformat(),
            "assigned_to": test_user.id
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/checklists", json=checklist_data)
        assert response.status_code == 201
        checklist = response.json()
        
        # Add checklist items
        item_data = {
            "item_text": "Verify sanitization solution concentration",
            "item_type": "verification",
            "required_response": True,
            "expected_response": "Yes",
            "order_number": 1
        }
        
        response = client.post(f"/api/v1/prp/checklists/{checklist['id']}/items", json=item_data)
        assert response.status_code == 201
        item = response.json()
        
        # Verify checklist item was created correctly
        assert item["item_text"] == "Verify sanitization solution concentration"
        assert item["checklist_id"] == checklist["id"]
    
    def test_analytics_integration(self, db: Session, test_user, test_prp_program):
        """Test analytics integration with PRP programs"""
        # Get program analytics
        response = client.get(f"/api/v1/prp/programs/{test_prp_program.id}/analytics")
        assert response.status_code == 200
        analytics = response.json()
        
        # Verify analytics structure
        assert "program_info" in analytics
        assert "period" in analytics
        assert "checklist_analytics" in analytics
        assert "risk_analytics" in analytics
        assert "capa_analytics" in analytics
    
    def test_notification_integration(self, db: Session, test_user, test_prp_program):
        """Test notification integration with PRP programs"""
        # Create a risk assessment that should trigger notification
        risk_data = {
            "hazard_identified": "Critical Safety Issue",
            "hazard_description": "Critical safety issue requiring immediate attention",
            "likelihood_level": "Very High",
            "severity_level": "Very High",
            "existing_controls": "None",
            "additional_controls_required": "Immediate action required",
            "control_effectiveness": "None",
            "next_review_date": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/risk-assessments", json=risk_data)
        assert response.status_code == 201
        risk_assessment = response.json()
        
        # Verify notification was created for high-risk assessment
        notifications = db.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.category == "prp_risk"
        ).all()
        
        assert len(notifications) > 0
    
    def test_document_template_integration(self, db: Session, test_user):
        """Test document template integration with PRP"""
        # Create PRP document template
        template_data = {
            "name": "PRP Program Template",
            "description": "Standard template for PRP programs",
            "document_type": "procedure",
            "category": "prp",
            "template_content": "Standard PRP program content"
        }
        
        response = client.post("/api/v1/documents/templates/", json=template_data)
        assert response.status_code == 201
        template = response.json()
        
        # Verify template was created correctly
        assert template["name"] == "PRP Program Template"
        assert template["category"] == "prp"
    
    def test_data_export_integration(self, db: Session, test_user, test_prp_program):
        """Test data export functionality"""
        # Export PRP data
        export_data = {
            "export_type": "comprehensive",
            "format": "json",
            "date_range": {
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "include_attachments": False
        }
        
        response = client.post("/api/v1/prp/reports/export", json=export_data)
        assert response.status_code == 200
        export_result = response.json()
        
        # Verify export was successful
        assert "download_url" in export_result or "data" in export_result
    
    def test_bulk_operations_integration(self, db: Session, test_user):
        """Test bulk operations functionality"""
        # Bulk update programs
        bulk_update_data = {
            "program_ids": [1, 2, 3],
            "updates": {
                "status": "active",
                "frequency": "weekly"
            }
        }
        
        response = client.post("/api/v1/prp/bulk/update", json=bulk_update_data)
        assert response.status_code == 200
        bulk_result = response.json()
        
        # Verify bulk update was successful
        assert "updated_count" in bulk_result
    
    def test_advanced_search_integration(self, db: Session, test_user):
        """Test advanced search functionality"""
        # Advanced search
        search_data = {
            "query": "sanitization",
            "filters": {
                "category": "cleaning_and_sanitizing",
                "status": "active",
                "date_range": {
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now().isoformat()
                }
            },
            "sort_by": "created_at",
            "sort_order": "desc"
        }
        
        response = client.post("/api/v1/prp/search/advanced", json=search_data)
        assert response.status_code == 200
        search_result = response.json()
        
        # Verify search was successful
        assert "items" in search_result
        assert "total" in search_result


class TestPRPCompliance:
    """Compliance tests for ISO 22002-1:2025 requirements"""
    
    def test_iso_22002_2025_categories_compliance(self, db: Session):
        """Test that all ISO 22002-1:2025 categories are supported"""
        from app.models.prp import PRPCategory
        
        required_categories = [
            "construction_and_layout",
            "layout_of_premises",
            "supplies_of_air_water_energy",
            "supporting_services",
            "suitability_cleaning_maintenance",
            "management_of_purchased_materials",
            "prevention_of_cross_contamination",
            "cleaning_and_sanitizing",
            "pest_control",
            "personnel_hygiene_facilities",
            "personnel_hygiene_practices",
            "reprocessing",
            "product_recall_procedures",
            "warehousing",
            "product_information_consumer_awareness",
            "food_defense_biovigilance_bioterrorism",
            "control_of_nonconforming_product",
            "product_release"
        ]
        
        for category in required_categories:
            assert hasattr(PRPCategory, category.upper()), f"Missing category: {category}"
    
    def test_risk_assessment_required_fields(self, db: Session, test_user, test_prp_program):
        """Test that risk assessments include all required fields"""
        risk_data = {
            "hazard_identified": "Test Hazard",
            "hazard_description": "Test hazard description",
            "likelihood_level": "Medium",
            "severity_level": "High",
            "existing_controls": "Test controls",
            "additional_controls_required": "Additional controls",
            "control_effectiveness": "Effective",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/risk-assessments", json=risk_data)
        assert response.status_code == 201
        risk_assessment = response.json()
        
        # Verify required fields are present
        required_fields = [
            "hazard_identified", "likelihood_level", "severity_level", 
            "risk_level", "risk_score", "acceptability"
        ]
        
        for field in required_fields:
            assert field in risk_assessment, f"Missing required field: {field}"
    
    def test_capa_required_fields(self, db: Session, test_user, test_prp_program):
        """Test that CAPA includes all required fields"""
        capa_data = {
            "title": "Test CAPA",
            "description": "Test CAPA description",
            "root_cause": "Test root cause",
            "action_type": "immediate",
            "priority": "high",
            "assigned_to": "Test User",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "verification_method": "Test verification",
            "program_id": test_prp_program.id
        }
        
        response = client.post("/api/v1/prp/corrective-actions", json=capa_data)
        assert response.status_code == 201
        capa = response.json()
        
        # Verify required fields are present
        required_fields = [
            "title", "description", "root_cause", "action_type", 
            "priority", "assigned_to", "due_date", "verification_method"
        ]
        
        for field in required_fields:
            assert field in capa, f"Missing required field: {field}"


class TestPRPPerformance:
    """Performance tests for PRP module"""
    
    def test_large_dataset_performance(self, db: Session, test_user):
        """Test performance with large datasets"""
        # Create multiple programs
        programs = []
        for i in range(100):
            program_data = {
                "program_code": f"PERF-PRP-{i:03d}",
                "name": f"Performance Test Program {i}",
                "description": f"Performance test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {i}",
                "scope": f"Scope {i}",
                "sop_reference": f"SOP-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            assert response.status_code == 201
            programs.append(response.json())
        
        # Test listing programs with pagination
        start_time = datetime.now()
        response = client.get("/api/v1/prp/programs/?page=1&size=50")
        end_time = datetime.now()
        
        assert response.status_code == 200
        assert (end_time - start_time).total_seconds() < 2.0  # Should complete within 2 seconds
    
    def test_concurrent_operations(self, db: Session, test_user):
        """Test concurrent operations performance"""
        import threading
        import time
        
        results = []
        
        def create_program(program_id):
            program_data = {
                "program_code": f"CONC-PRP-{program_id:03d}",
                "name": f"Concurrent Test Program {program_id}",
                "description": f"Concurrent test program {program_id}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {program_id}",
                "scope": f"Scope {program_id}",
                "sop_reference": f"SOP-{program_id:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            results.append(response.status_code == 201)
        
        # Create 10 threads to create programs concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_program, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations were successful
        assert all(results), "All concurrent operations should succeed"


if __name__ == "__main__":
    pytest.main([__file__])
