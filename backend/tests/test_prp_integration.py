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
    def test_user(self, db: Session):
        """Create a test user for testing"""
        user = User(
            username="test_user",
            email="test@example.com",
            full_name="Test User",
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
            "category": "pest_control",
            "objective": "Control pest infestation",
            "scope": "Entire facility",
            "sop_reference": "SOP-PC-001",
            "frequency": "weekly",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program_id = response.json()["data"]["id"]
        
        # Create risk assessment for the program
        risk_data = {
            "hazard_identified": "Pest infestation",
            "hazard_description": "Risk of pest contamination",
            "likelihood_level": "Medium",
            "severity_level": "High",
            "existing_controls": "Regular pest control service",
            "additional_controls_required": "Enhanced monitoring",
            "control_effectiveness": "Effective with monitoring",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{program_id}/risk-assessments/", json=risk_data)
        assert response.status_code == 201
        
        # Verify the risk assessment is linked to the program
        response = client.get(f"/api/v1/prp/programs/{program_id}/risk-assessments/")
        assert response.status_code == 200
        assessments = response.json()["data"]["items"]
        assert len(assessments) == 1
        assert assessments[0]["hazard_identified"] == "Pest infestation"
    
    def test_risk_assessment_with_controls(self, db: Session, test_user, test_prp_program):
        """Test creating risk assessment with controls"""
        # Create risk assessment
        risk_data = {
            "hazard_identified": "Chemical contamination",
            "hazard_description": "Risk of chemical contamination",
            "likelihood_level": "Low",
            "severity_level": "High",
            "existing_controls": "Chemical storage procedures",
            "additional_controls_required": "Enhanced training",
            "control_effectiveness": "Effective with training",
            "next_review_date": (datetime.now() + timedelta(days=60)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/risk-assessments/", json=risk_data)
        assert response.status_code == 201
        risk_id = response.json()["data"]["id"]
        
        # Add risk control
        control_data = {
            "control_name": "Chemical Safety Training",
            "control_type": "administrative",
            "control_description": "Enhanced training for chemical handling",
            "implementation_status": "pending",
            "effectiveness_rating": 4,
            "responsible_person": "Safety Manager",
            "implementation_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "review_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "cost_estimate": 5000.0,
            "priority": "high"
        }
        
        response = client.post(f"/api/v1/prp/risk-assessments/{risk_id}/controls/", json=control_data)
        assert response.status_code == 201
        
        # Verify control is linked to risk assessment
        response = client.get(f"/api/v1/prp/risk-assessments/{risk_id}/controls/")
        assert response.status_code == 200
        controls = response.json()["data"]["items"]
        assert len(controls) == 1
        assert controls[0]["control_name"] == "Chemical Safety Training"
    
    def test_capa_integration(self, db: Session, test_user, test_prp_program):
        """Test CAPA integration with PRP programs"""
        # Create corrective action
        capa_data = {
            "title": "Improve Cleaning Procedures",
            "description": "Enhance cleaning procedures to prevent contamination",
            "root_cause": "Inadequate cleaning procedures",
            "action_type": "systemic",
            "priority": "high",
            "assigned_to": "Cleaning Supervisor",
            "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 2000.0,
            "verification_method": "Audit and testing",
            "program_id": test_prp_program.id
        }
        
        response = client.post("/api/v1/prp/corrective-actions/", json=capa_data)
        assert response.status_code == 201
        
        # Create preventive action
        preventive_data = {
            "title": "Preventive Maintenance Schedule",
            "description": "Implement preventive maintenance for cleaning equipment",
            "potential_issue": "Equipment failure leading to inadequate cleaning",
            "action_type": "preventive",
            "priority": "medium",
            "assigned_to": "Maintenance Manager",
            "start_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 3000.0,
            "verification_method": "Equipment performance monitoring",
            "program_id": test_prp_program.id
        }
        
        response = client.post("/api/v1/prp/preventive-actions/", json=preventive_data)
        assert response.status_code == 201
        
        # Test CAPA dashboard
        response = client.get("/api/v1/prp/capa/dashboard/")
        assert response.status_code == 200
        dashboard_data = response.json()["data"]
        assert dashboard_data["total_corrective_actions"] >= 1
        assert dashboard_data["total_preventive_actions"] >= 1
    
    def test_checklist_integration(self, db: Session, test_user, test_prp_program):
        """Test checklist integration with PRP programs"""
        # Create checklist
        checklist_data = {
            "checklist_code": "CHK-TEST-001",
            "name": "Daily Cleaning Checklist",
            "description": "Daily cleaning verification checklist",
            "scheduled_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(hours=8)).isoformat(),
            "assigned_to": test_user.id,
            "program_id": test_prp_program.id
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/checklists/", json=checklist_data)
        assert response.status_code == 201
        checklist_id = response.json()["data"]["id"]
        
        # Add checklist items
        item_data = {
            "item_text": "Check cleaning equipment",
            "item_type": "yes_no",
            "is_critical": True,
            "points": 10,
            "expected_response": "Yes",
            "order_number": 1
        }
        
        response = client.post(f"/api/v1/prp/checklists/{checklist_id}/items/", json=item_data)
        assert response.status_code == 201
        
        # Complete checklist
        completion_data = {
            "completed_date": datetime.now().isoformat(),
            "compliance_percentage": 95.0,
            "is_verified": True,
            "verified_by": test_user.id,
            "verification_date": datetime.now().isoformat()
        }
        
        response = client.put(f"/api/v1/prp/checklists/{checklist_id}", json=completion_data)
        assert response.status_code == 200
    
    def test_analytics_integration(self, db: Session, test_user, test_prp_program):
        """Test analytics and reporting integration"""
        # Test program analytics
        response = client.get(f"/api/v1/prp/programs/{test_prp_program.id}/analytics/")
        assert response.status_code == 200
        analytics_data = response.json()["data"]
        assert "program_info" in analytics_data
        assert "checklist_analytics" in analytics_data
        assert "risk_analytics" in analytics_data
        assert "capa_analytics" in analytics_data
        
        # Test performance trends
        response = client.get(f"/api/v1/prp/programs/{test_prp_program.id}/performance-trends/")
        assert response.status_code == 200
        
        # Test comprehensive reporting
        report_data = {
            "report_type": "comprehensive",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "include_analytics": True,
            "include_risks": True,
            "include_capa": True
        }
        
        response = client.post("/api/v1/prp/reports/comprehensive/", json=report_data)
        assert response.status_code == 200
    
    def test_notification_integration(self, db: Session, test_user, test_prp_program):
        """Test notification system integration"""
        # Create a high-risk assessment that should trigger notifications
        risk_data = {
            "hazard_identified": "Critical Safety Issue",
            "hazard_description": "Critical safety concern requiring immediate attention",
            "likelihood_level": "High",
            "severity_level": "Critical",
            "existing_controls": "Emergency procedures",
            "additional_controls_required": "Immediate action required",
            "control_effectiveness": "Insufficient",
            "next_review_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{test_prp_program.id}/risk-assessments/", json=risk_data)
        assert response.status_code == 201
        
        # Verify notification was created
        notifications = db.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.category == "risk_assessment"
        ).all()
        assert len(notifications) >= 1
    
    def test_document_template_integration(self, db: Session, test_user):
        """Test document template integration"""
        # Create PRP document template
        template_data = {
            "name": "PRP Program Template",
            "description": "Standard template for PRP programs",
            "document_type": "procedure",
            "category": "prp",
            "template_content": "Standard PRP program content template"
        }
        
        response = client.post("/api/v1/documents/templates/", json=template_data)
        assert response.status_code == 201
        
        # Verify template can be used for PRP programs
        response = client.get("/api/v1/documents/templates/?category=prp")
        assert response.status_code == 200
        templates = response.json()["data"]["items"]
        assert len(templates) >= 1
        assert templates[0]["name"] == "PRP Program Template"
    
    def test_data_export_integration(self, db: Session, test_user, test_prp_program):
        """Test data export functionality"""
        export_data = {
            "export_type": "comprehensive",
            "program_ids": [test_prp_program.id],
            "include_risks": True,
            "include_capa": True,
            "include_checklists": True,
            "format": "excel",
            "date_range": {
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        }
        
        response = client.post("/api/v1/prp/reports/export/", json=export_data)
        assert response.status_code == 200
        assert "download_url" in response.json()["data"]
    
    def test_bulk_operations(self, db: Session, test_user):
        """Test bulk operations functionality"""
        # Test bulk update
        bulk_update_data = {
            "program_ids": [1, 2, 3],
            "updates": {
                "status": "active",
                "frequency": "weekly"
            }
        }
        
        response = client.post("/api/v1/prp/bulk/update/", json=bulk_update_data)
        assert response.status_code == 200
        
        # Test bulk export
        bulk_export_data = {
            "program_ids": [1, 2, 3],
            "format": "excel",
            "include_related_data": True
        }
        
        response = client.post("/api/v1/prp/bulk/export/", json=bulk_export_data)
        assert response.status_code == 200
    
    def test_advanced_search(self, db: Session, test_user):
        """Test advanced search functionality"""
        search_data = {
            "query": "cleaning",
            "filters": {
                "category": "cleaning_and_sanitizing",
                "status": "active",
                "date_range": {
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now().isoformat()
                }
            },
            "include_risks": True,
            "include_capa": True
        }
        
        response = client.post("/api/v1/prp/search/advanced/", json=search_data)
        assert response.status_code == 200
        search_results = response.json()["data"]
        assert "programs" in search_results
        assert "risk_assessments" in search_results
        assert "corrective_actions" in search_results
    
    def test_performance_metrics(self, db: Session, test_user):
        """Test performance metrics and benchmarking"""
        # Test performance metrics
        response = client.get("/api/v1/prp/performance/metrics/")
        assert response.status_code == 200
        metrics_data = response.json()["data"]
        assert "compliance_rate" in metrics_data
        assert "risk_levels" in metrics_data
        assert "capa_effectiveness" in metrics_data
        
        # Test performance benchmarks
        response = client.get("/api/v1/prp/performance/benchmarks/")
        assert response.status_code == 200
        benchmarks_data = response.json()["data"]
        assert "industry_benchmarks" in benchmarks_data
        assert "internal_benchmarks" in benchmarks_data
    
    def test_automation_integration(self, db: Session, test_user):
        """Test automation and workflow integration"""
        # Test automation trigger
        automation_data = {
            "automation_type": "risk_escalation",
            "parameters": {
                "risk_threshold": "high",
                "escalation_level": "management"
            }
        }
        
        response = client.post("/api/v1/prp/automation/trigger/", json=automation_data)
        assert response.status_code == 200
        
        # Test automation status
        response = client.get("/api/v1/prp/automation/status/")
        assert response.status_code == 200
        status_data = response.json()["data"]
        assert "active_automations" in status_data
        assert "automation_history" in status_data

class TestPRPCompliance:
    """Compliance tests for ISO 22002-1:2025 requirements"""
    
    def test_iso_22002_2025_compliance(self, db: Session, test_user):
        """Test compliance with ISO 22002-1:2025 requirements"""
        # Test all 18 PRP categories are supported
        categories = [
            "construction_and_layout", "layout_of_premises", "supplies_of_utilities",
            "supporting_services", "suitability_of_equipment", "management_of_materials",
            "prevention_of_cross_contamination", "cleaning_and_sanitizing", "pest_control",
            "personnel_hygiene_facilities", "personnel_hygiene_practices", "reprocessing",
            "product_recall_procedures", "warehousing", "product_information",
            "food_defense", "control_of_nonconforming_product", "product_release"
        ]
        
        for category in categories:
            program_data = {
                "program_code": f"TEST-{category.upper()}",
                "name": f"Test {category.replace('_', ' ').title()} Program",
                "description": f"Test program for {category}",
                "category": category,
                "objective": f"Ensure compliance with {category} requirements",
                "scope": "Test scope",
                "sop_reference": f"SOP-{category.upper()}-001",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            assert response.status_code == 201
    
    def test_risk_assessment_compliance(self, db: Session, test_user):
        """Test risk assessment compliance requirements"""
        # Test risk assessment includes all required fields
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
        
        response = client.post("/api/v1/prp/programs/1/risk-assessments/", json=risk_data)
        assert response.status_code == 201
        
        risk_assessment = response.json()["data"]
        required_fields = [
            "hazard_identified", "likelihood_level", "severity_level", 
            "risk_level", "risk_score", "acceptability", "assessment_date"
        ]
        
        for field in required_fields:
            assert field in risk_assessment
    
    def test_capa_compliance(self, db: Session, test_user):
        """Test CAPA compliance requirements"""
        # Test corrective action includes all required fields
        capa_data = {
            "title": "Test Corrective Action",
            "description": "Test corrective action description",
            "root_cause": "Test root cause",
            "action_type": "systemic",
            "priority": "high",
            "assigned_to": "Test Person",
            "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "verification_method": "Test verification method",
            "program_id": 1
        }
        
        response = client.post("/api/v1/prp/corrective-actions/", json=capa_data)
        assert response.status_code == 201
        
        corrective_action = response.json()["data"]
        required_fields = [
            "title", "description", "root_cause", "action_type", 
            "priority", "assigned_to", "due_date", "verification_method"
        ]
        
        for field in required_fields:
            assert field in corrective_action

class TestPRPPerformance:
    """Performance tests for PRP module"""
    
    def test_large_dataset_performance(self, db: Session, test_user):
        """Test performance with large datasets"""
        # Create multiple programs
        for i in range(100):
            program_data = {
                "program_code": f"PERF-TEST-{i:03d}",
                "name": f"Performance Test Program {i}",
                "description": f"Performance test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Test objective {i}",
                "scope": f"Test scope {i}",
                "sop_reference": f"SOP-TEST-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            assert response.status_code == 201
        
        # Test listing programs with pagination
        response = client.get("/api/v1/prp/programs/?page=1&size=50")
        assert response.status_code == 200
        programs_data = response.json()["data"]
        assert len(programs_data["items"]) <= 50
        assert programs_data["total"] >= 100
    
    def test_concurrent_operations(self, db: Session, test_user):
        """Test concurrent operations performance"""
        import threading
        import time
        
        results = []
        
        def create_program(program_id):
            program_data = {
                "program_code": f"CONCURRENT-{program_id}",
                "name": f"Concurrent Program {program_id}",
                "description": f"Concurrent test program {program_id}",
                "category": "pest_control",
                "objective": f"Test objective {program_id}",
                "scope": f"Test scope {program_id}",
                "sop_reference": f"SOP-CONC-{program_id}",
                "frequency": "weekly",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_program, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        assert all(status == 201 for status in results)

if __name__ == "__main__":
    pytest.main([__file__])
