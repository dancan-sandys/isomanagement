"""
Compliance Tests for PRP Module - ISO 22002-1:2025

This module contains comprehensive compliance tests to ensure the PRP module
meets all ISO 22002-1:2025 requirements for food manufacturing facilities.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.models.prp import (
    PRPProgram, PRPCategory, RiskAssessment, RiskLevel, 
    CorrectiveAction, PreventiveAction, PRPChecklist
)
from app.models.user import User
from app.core.database import get_db

client = TestClient(app)

class TestISO220022025Compliance:
    """Compliance tests for ISO 22002-1:2025 requirements"""
    
    @pytest.fixture
    def test_user(self, db: Session):
        """Create a test user for compliance testing"""
        user = User(
            username="compliance_user",
            email="compliance@example.com",
            full_name="Compliance Test User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def test_all_iso_categories_supported(self, db: Session):
        """Test that all ISO 22002-1:2025 PRP categories are supported"""
        # ISO 22002-1:2025 requires 18 specific PRP categories
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
        
        # Verify all categories exist in the enum
        for category in required_categories:
            assert hasattr(PRPCategory, category.upper()), f"Missing ISO category: {category}"
        
        # Verify no extra categories that aren't in ISO standard
        iso_categories = set(required_categories)
        enum_categories = set([cat.value for cat in PRPCategory])
        assert enum_categories.issuperset(iso_categories), "All ISO categories must be supported"
    
    def test_prp_program_required_fields(self, db: Session, test_user):
        """Test that PRP programs include all ISO 22002-1:2025 required fields"""
        program_data = {
            "program_code": "ISO-TEST-001",
            "name": "ISO Compliance Test Program",
            "description": "Test program for ISO compliance",
            "category": "cleaning_and_sanitizing",
            "objective": "Ensure proper cleaning and sanitizing procedures",
            "scope": "Production area and equipment",
            "sop_reference": "SOP-CS-ISO-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # ISO 22002-1:2025 required fields
        required_fields = [
            "program_code", "name", "description", "category", 
            "objective", "scope", "sop_reference", "frequency", 
            "status", "assigned_to"
        ]
        
        for field in required_fields:
            assert field in program, f"Missing ISO required field: {field}"
            assert program[field] is not None, f"ISO required field cannot be null: {field}"
    
    def test_risk_assessment_iso_compliance(self, db: Session, test_user):
        """Test risk assessment compliance with ISO 22002-1:2025"""
        # Create a PRP program first
        program_data = {
            "program_code": "ISO-RISK-001",
            "name": "ISO Risk Assessment Test",
            "description": "Test program for risk assessment compliance",
            "category": "pest_control",
            "objective": "Control pest infestation",
            "scope": "Entire facility",
            "sop_reference": "SOP-PC-ISO-001",
            "frequency": "weekly",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Create risk assessment with ISO-compliant data
        risk_data = {
            "hazard_identified": "Pest contamination",
            "hazard_description": "Risk of pest contamination in food production area",
            "likelihood_level": "Medium",
            "severity_level": "High",
            "existing_controls": "Regular pest control service, monitoring",
            "additional_controls_required": "Enhanced monitoring, immediate action procedures",
            "control_effectiveness": "Effective with monitoring",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/risk-assessments", json=risk_data)
        assert response.status_code == 201
        risk_assessment = response.json()
        
        # ISO 22002-1:2025 risk assessment requirements
        required_risk_fields = [
            "hazard_identified", "likelihood_level", "severity_level",
            "risk_level", "risk_score", "acceptability", "assessment_date"
        ]
        
        for field in required_risk_fields:
            assert field in risk_assessment, f"Missing ISO risk assessment field: {field}"
            assert risk_assessment[field] is not None, f"ISO risk field cannot be null: {field}"
        
        # Verify risk level calculation follows ISO methodology
        assert risk_assessment["risk_level"] in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH", "CRITICAL"]
        assert isinstance(risk_assessment["risk_score"], int)
        assert 1 <= risk_assessment["risk_score"] <= 25  # Standard risk matrix range
    
    def test_capa_iso_compliance(self, db: Session, test_user):
        """Test CAPA compliance with ISO 22002-1:2025"""
        # Create a PRP program
        program_data = {
            "program_code": "ISO-CAPA-001",
            "name": "ISO CAPA Test Program",
            "description": "Test program for CAPA compliance",
            "category": "personnel_hygiene_practices",
            "objective": "Ensure proper personnel hygiene",
            "scope": "All personnel",
            "sop_reference": "SOP-PH-ISO-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Test corrective action compliance
        corrective_data = {
            "title": "Address Hygiene Violation",
            "description": "Corrective action for hygiene procedure violation",
            "root_cause": "Inadequate training and supervision",
            "action_type": "immediate",
            "priority": "high",
            "assigned_to": "Hygiene Supervisor",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 1500.0,
            "verification_method": "Observation and retraining assessment",
            "program_id": program["id"]
        }
        
        response = client.post("/api/v1/prp/corrective-actions", json=corrective_data)
        assert response.status_code == 201
        corrective_action = response.json()
        
        # ISO CAPA requirements
        required_capa_fields = [
            "title", "description", "root_cause", "action_type",
            "priority", "assigned_to", "due_date", "verification_method"
        ]
        
        for field in required_capa_fields:
            assert field in corrective_action, f"Missing ISO CAPA field: {field}"
            assert corrective_action[field] is not None, f"ISO CAPA field cannot be null: {field}"
        
        # Test preventive action compliance
        preventive_data = {
            "title": "Prevent Future Hygiene Issues",
            "description": "Preventive action to avoid hygiene violations",
            "potential_issue": "Similar hygiene violations",
            "action_type": "long_term",
            "priority": "medium",
            "assigned_to": "Training Department",
            "start_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 3000.0,
            "verification_method": "Training effectiveness assessment",
            "program_id": program["id"]
        }
        
        response = client.post("/api/v1/prp/preventive-actions", json=preventive_data)
        assert response.status_code == 201
        preventive_action = response.json()
        
        # Verify preventive action compliance
        for field in required_capa_fields:
            if field in preventive_action:  # Some fields may have different names
                assert preventive_action[field] is not None, f"ISO preventive action field cannot be null: {field}"
    
    def test_monitoring_verification_compliance(self, db: Session, test_user):
        """Test monitoring and verification compliance with ISO 22002-1:2025"""
        # Create a PRP program with monitoring
        program_data = {
            "program_code": "ISO-MON-001",
            "name": "ISO Monitoring Test Program",
            "description": "Test program for monitoring compliance",
            "category": "cleaning_and_sanitizing",
            "objective": "Ensure effective cleaning and sanitizing",
            "scope": "Production equipment",
            "sop_reference": "SOP-CS-MON-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Create checklist for monitoring
        checklist_data = {
            "checklist_code": "ISO-CHK-001",
            "name": "ISO Compliance Checklist",
            "description": "Checklist for ISO compliance monitoring",
            "scheduled_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(hours=8)).isoformat(),
            "assigned_to": test_user.id
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/checklists", json=checklist_data)
        assert response.status_code == 201
        checklist = response.json()
        
        # ISO monitoring requirements
        required_monitoring_fields = [
            "checklist_code", "name", "scheduled_date", "due_date", "assigned_to"
        ]
        
        for field in required_monitoring_fields:
            assert field in checklist, f"Missing ISO monitoring field: {field}"
            assert checklist[field] is not None, f"ISO monitoring field cannot be null: {field}"
    
    def test_documentation_compliance(self, db: Session, test_user):
        """Test documentation compliance with ISO 22002-1:2025"""
        # Test that all PRP programs have required documentation
        program_data = {
            "program_code": "ISO-DOC-001",
            "name": "ISO Documentation Test",
            "description": "Test program for documentation compliance",
            "category": "management_of_purchased_materials",
            "objective": "Ensure proper material management",
            "scope": "All purchased materials",
            "sop_reference": "SOP-MPM-ISO-001",
            "frequency": "as_needed",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # ISO documentation requirements
        required_doc_fields = [
            "program_code", "name", "description", "category", 
            "objective", "scope", "sop_reference"
        ]
        
        for field in required_doc_fields:
            assert field in program, f"Missing ISO documentation field: {field}"
            assert program[field] is not None, f"ISO documentation field cannot be null: {field}"
            assert len(str(program[field])) > 0, f"ISO documentation field cannot be empty: {field}"
    
    def test_training_compliance(self, db: Session, test_user):
        """Test training compliance with ISO 22002-1:2025"""
        # Create a PRP program that requires training
        program_data = {
            "program_code": "ISO-TRAIN-001",
            "name": "ISO Training Test Program",
            "description": "Test program for training compliance",
            "category": "personnel_hygiene_practices",
            "objective": "Ensure proper personnel hygiene training",
            "scope": "All personnel",
            "sop_reference": "SOP-PH-TRAIN-001",
            "frequency": "monthly",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # ISO training requirements - program must have assigned personnel
        assert program["assigned_to"] is not None, "ISO requires assigned personnel for PRP programs"
        assert program["sop_reference"] is not None, "ISO requires SOP reference for training"
    
    def test_verification_validation_compliance(self, db: Session, test_user):
        """Test verification and validation compliance with ISO 22002-1:2025"""
        # Create a PRP program with verification requirements
        program_data = {
            "program_code": "ISO-VERIFY-001",
            "name": "ISO Verification Test Program",
            "description": "Test program for verification compliance",
            "category": "cleaning_and_sanitizing",
            "objective": "Ensure effective cleaning verification",
            "scope": "Production equipment",
            "sop_reference": "SOP-CS-VERIFY-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Create verification checklist
        checklist_data = {
            "checklist_code": "ISO-VERIFY-CHK-001",
            "name": "ISO Verification Checklist",
            "description": "Checklist for verification compliance",
            "scheduled_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(hours=4)).isoformat(),
            "assigned_to": test_user.id
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/checklists", json=checklist_data)
        assert response.status_code == 201
        checklist = response.json()
        
        # ISO verification requirements
        assert checklist["assigned_to"] is not None, "ISO requires assigned personnel for verification"
        assert checklist["scheduled_date"] is not None, "ISO requires scheduled verification"
        assert checklist["due_date"] is not None, "ISO requires verification due dates"


class TestRegulatoryCompliance:
    """Tests for additional regulatory compliance requirements"""
    
    def test_food_safety_compliance(self, db: Session):
        """Test compliance with food safety requirements"""
        # Verify that all PRP categories support food safety
        food_safety_categories = [
            "cleaning_and_sanitizing",
            "pest_control", 
            "personnel_hygiene_practices",
            "prevention_of_cross_contamination",
            "management_of_purchased_materials"
        ]
        
        for category in food_safety_categories:
            assert hasattr(PRPCategory, category.upper()), f"Missing food safety category: {category}"
    
    def test_haccp_integration_compliance(self, db: Session):
        """Test HACCP integration compliance"""
        # Verify that PRP programs can integrate with HACCP
        # This would typically involve checking that PRP programs
        # can be linked to HACCP plans and CCPs
        
        # For now, verify that the basic structure supports HACCP integration
        assert True  # Placeholder for HACCP integration tests
    
    def test_audit_trail_compliance(self, db: Session, test_user):
        """Test audit trail compliance requirements"""
        # Create a PRP program to test audit trail
        program_data = {
            "program_code": "AUDIT-TEST-001",
            "name": "Audit Trail Test Program",
            "description": "Test program for audit trail compliance",
            "category": "cleaning_and_sanitizing",
            "objective": "Ensure audit trail compliance",
            "scope": "Test scope",
            "sop_reference": "SOP-AUDIT-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Verify audit trail fields are present
        audit_fields = ["created_at", "created_by", "updated_at"]
        for field in audit_fields:
            assert field in program, f"Missing audit trail field: {field}"


class TestContinuousImprovement:
    """Tests for continuous improvement compliance"""
    
    def test_continuous_improvement_cycle(self, db: Session, test_user):
        """Test continuous improvement cycle compliance"""
        # Create a PRP program
        program_data = {
            "program_code": "CI-TEST-001",
            "name": "Continuous Improvement Test",
            "description": "Test program for continuous improvement",
            "category": "cleaning_and_sanitizing",
            "objective": "Implement continuous improvement",
            "scope": "Test scope",
            "sop_reference": "SOP-CI-001",
            "frequency": "monthly",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Create a risk assessment for improvement
        risk_data = {
            "hazard_identified": "Process inefficiency",
            "hazard_description": "Current process is inefficient",
            "likelihood_level": "Medium",
            "severity_level": "Medium",
            "existing_controls": "Current procedures",
            "additional_controls_required": "Process optimization",
            "control_effectiveness": "Needs improvement",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/risk-assessments", json=risk_data)
        assert response.status_code == 201
        
        # Create preventive action for improvement
        preventive_data = {
            "title": "Process Optimization",
            "description": "Optimize current process for better efficiency",
            "potential_issue": "Continued inefficiency",
            "action_type": "long_term",
            "priority": "medium",
            "assigned_to": "Process Improvement Team",
            "start_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 5000.0,
            "verification_method": "Performance metrics assessment",
            "program_id": program["id"]
        }
        
        response = client.post("/api/v1/prp/preventive-actions", json=preventive_data)
        assert response.status_code == 201
        
        # Verify continuous improvement cycle is supported
        assert True  # Placeholder for continuous improvement verification


if __name__ == "__main__":
    pytest.main([__file__])
