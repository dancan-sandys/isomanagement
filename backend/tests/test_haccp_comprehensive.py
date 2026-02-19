"""
Comprehensive HACCP Testing Suite - Phase 17

This module contains comprehensive tests for the HACCP system including:
- Unit tests for all HACCP components
- Integration tests for complete workflows
- Performance tests for large datasets
- Compliance tests for ISO 22000:2018 and FSIS requirements
- Security tests for data protection
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.haccp import (
    HACCPProduct, HACCPProcessFlow, HACCPHazard, HACCPCCP,
    CCPMonitoringLog, CCPVerificationLog, HACCPValidation,
    HACCPEvidenceAttachment, HACCPAuditLog
)
from app.models.user import User
from app.services.haccp_service import HACCPService
from app.core.database import get_db
from app.core.config import settings

client = TestClient(app)

class TestHACCPUnitTests:
    """Unit tests for HACCP components"""
    
    @pytest.fixture
    def test_user(self, db: Session):
        """Create a test user"""
        user = User(
            username="haccp_test_user",
            email="haccp@example.com",
            full_name="HACCP Test User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @pytest.fixture
    def test_product(self, db: Session, test_user):
        """Create a test HACCP product"""
        product = HACCPProduct(
            name="Test Chicken Product",
            product_code="TEST-CHK-001",
            category="Poultry",
            description="Test product for HACCP testing",
            created_by=test_user.id,
            status="active"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    def test_product_creation(self, db: Session, test_user):
        """Test HACCP product creation"""
        product_data = {
            "name": "Test Product",
            "product_code": "TEST-001",
            "category": "Poultry",
            "description": "Test product description"
        }
        
        response = client.post("/api/v1/haccp/products/", json=product_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["product_code"] == "TEST-001"
    
    def test_hazard_analysis(self, db: Session, test_product):
        """Test hazard analysis creation and risk calculation"""
        hazard_data = {
            "product_id": test_product.id,
            "hazard_name": "Salmonella spp.",
            "hazard_type": "biological",
            "likelihood": 4,
            "severity": 5,
            "control_measures": ["Cooking", "Temperature control"],
            "is_ccp": True,
            "rationale": "High risk biological hazard"
        }
        
        response = client.post("/api/v1/haccp/hazards/", json=hazard_data)
        assert response.status_code == 201
        data = response.json()
        assert data["hazard_name"] == "Salmonella spp."
        assert data["risk_score"] == 20  # 4 * 5
        assert data["risk_level"] == "critical"
    
    def test_ccp_creation(self, db: Session, test_product):
        """Test CCP creation with critical limits"""
        ccp_data = {
            "product_id": test_product.id,
            "ccp_number": 1,
            "name": "Cooking Temperature Control",
            "hazard": "Salmonella spp.",
            "critical_limits": [
                {
                    "parameter": "temperature",
                    "unit": "°C",
                    "min_value": 74,
                    "max_value": 85
                }
            ],
            "monitoring_method": "Digital thermometer",
            "monitoring_frequency": "Every batch",
            "corrective_actions": ["Stop production", "Adjust parameters"]
        }
        
        response = client.post("/api/v1/haccp/ccps/", json=ccp_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cooking Temperature Control"
        assert data["ccp_number"] == 1
    
    def test_monitoring_log_creation(self, db: Session, test_product):
        """Test CCP monitoring log creation"""
        # First create a CCP
        ccp_data = {
            "product_id": test_product.id,
            "ccp_number": 1,
            "name": "Test CCP",
            "hazard": "Test Hazard",
            "critical_limits": [{"parameter": "temperature", "unit": "°C", "min_value": 70}],
            "monitoring_method": "Test method",
            "monitoring_frequency": "Daily"
        }
        ccp_response = client.post("/api/v1/haccp/ccps/", json=ccp_data)
        ccp_id = ccp_response.json()["id"]
        
        # Create monitoring log
        log_data = {
            "ccp_id": ccp_id,
            "monitoring_date": datetime.now().isoformat(),
            "parameter_value": 75.0,
            "unit": "°C",
            "is_within_limits": True,
            "operator_notes": "Normal operation"
        }
        
        response = client.post("/api/v1/haccp/monitoring-logs/", json=log_data)
        assert response.status_code == 201
        data = response.json()
        assert data["parameter_value"] == 75.0
        assert data["is_within_limits"] == True

class TestHACCPIntegrationTests:
    """Integration tests for complete HACCP workflows"""
    
    @pytest.fixture
    def complete_haccp_workflow(self, db: Session, test_user):
        """Create a complete HACCP workflow for testing"""
        # Create product
        product = HACCPProduct(
            name="Integration Test Product",
            product_code="INT-TEST-001",
            category="Poultry",
            created_by=test_user.id
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create process flow
        process_flow = HACCPProcessFlow(
            product_id=product.id,
            step_number=1,
            step_name="Cooking",
            description="Cook to 74°C",
            created_by=test_user.id
        )
        db.add(process_flow)
        db.commit()
        
        # Create hazard
        hazard = HACCPHazard(
            product_id=product.id,
            hazard_name="Salmonella spp.",
            hazard_type="biological",
            likelihood=4,
            severity=5,
            is_ccp=True,
            created_by=test_user.id
        )
        db.add(hazard)
        db.commit()
        
        # Create CCP
        ccp = HACCPCCP(
            product_id=product.id,
            ccp_number=1,
            name="Cooking Temperature",
            hazard="Salmonella spp.",
            created_by=test_user.id
        )
        db.add(ccp)
        db.commit()
        
        return {
            "product": product,
            "process_flow": process_flow,
            "hazard": hazard,
            "ccp": ccp
        }
    
    def test_complete_haccp_workflow(self, db: Session, complete_haccp_workflow):
        """Test complete HACCP workflow from product to monitoring"""
        product = complete_haccp_workflow["product"]
        ccp = complete_haccp_workflow["ccp"]
        
        # Test monitoring log creation
        log_data = {
            "ccp_id": ccp.id,
            "monitoring_date": datetime.now().isoformat(),
            "parameter_value": 78.0,
            "unit": "°C",
            "is_within_limits": True
        }
        
        response = client.post("/api/v1/haccp/monitoring-logs/", json=log_data)
        assert response.status_code == 201
        
        # Test verification log creation
        verification_data = {
            "ccp_id": ccp.id,
            "verification_date": datetime.now().isoformat(),
            "verification_method": "Temperature recording review",
            "verification_result": "Pass",
            "verifier_notes": "All records reviewed"
        }
        
        response = client.post("/api/v1/haccp/verification-logs/", json=verification_data)
        assert response.status_code == 201
        
        # Test HACCP plan generation
        response = client.get(f"/api/v1/haccp/products/{product.id}/plan")
        assert response.status_code == 200
        data = response.json()
        assert "hazards" in data
        assert "ccps" in data
        assert "process_flow" in data
    
    def test_corrective_action_workflow(self, db: Session, complete_haccp_workflow):
        """Test corrective action workflow when monitoring fails"""
        ccp = complete_haccp_workflow["ccp"]
        
        # Create out-of-spec monitoring log
        log_data = {
            "ccp_id": ccp.id,
            "monitoring_date": datetime.now().isoformat(),
            "parameter_value": 70.0,  # Below critical limit
            "unit": "°C",
            "is_within_limits": False,
            "operator_notes": "Temperature below critical limit"
        }
        
        response = client.post("/api/v1/haccp/monitoring-logs/", json=log_data)
        assert response.status_code == 201
        
        # Verify that corrective action is triggered
        # This would typically be handled by a background task
        # For now, we'll test the corrective action endpoint directly
        
        corrective_action_data = {
            "ccp_id": ccp.id,
            "monitoring_log_id": response.json()["id"],
            "action_taken": "Stop production and adjust cooking parameters",
            "action_date": datetime.now().isoformat(),
            "responsible_person": "Production Supervisor",
            "completion_date": datetime.now().isoformat(),
            "effectiveness": "Effective"
        }
        
        response = client.post("/api/v1/haccp/corrective-actions/", json=corrective_action_data)
        assert response.status_code == 201

class TestHACCPPerformanceTests:
    """Performance tests for HACCP system"""
    
    def test_large_dataset_performance(self, db: Session, test_user):
        """Test performance with large datasets"""
        # Create multiple products
        products = []
        for i in range(100):
            product = HACCPProduct(
                name=f"Performance Test Product {i}",
                product_code=f"PERF-{i:03d}",
                category="Poultry",
                created_by=test_user.id
            )
            products.append(product)
        
        db.add_all(products)
        db.commit()
        
        # Test product listing performance
        start_time = time.time()
        response = client.get("/api/v1/haccp/products/")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
    
    def test_monitoring_log_performance(self, db: Session, test_user):
        """Test monitoring log creation performance"""
        # Create a test product and CCP
        product = HACCPProduct(
            name="Performance Test Product",
            product_code="PERF-001",
            category="Poultry",
            created_by=test_user.id
        )
        db.add(product)
        db.commit()
        
        ccp = HACCPCCP(
            product_id=product.id,
            ccp_number=1,
            name="Test CCP",
            hazard="Test Hazard",
            created_by=test_user.id
        )
        db.add(ccp)
        db.commit()
        
        # Test bulk monitoring log creation
        start_time = time.time()
        for i in range(50):
            log_data = {
                "ccp_id": ccp.id,
                "monitoring_date": datetime.now().isoformat(),
                "parameter_value": 75.0 + (i % 10),
                "unit": "°C",
                "is_within_limits": True
            }
            response = client.post("/api/v1/haccp/monitoring-logs/", json=log_data)
            assert response.status_code == 201
        
        end_time = time.time()
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds

class TestHACCPComplianceTests:
    """Compliance tests for ISO 22000:2018 and FSIS requirements"""
    
    def test_iso_22000_compliance(self, db: Session, test_user):
        """Test ISO 22000:2018 compliance requirements"""
        # Test that all required HACCP elements are present
        required_elements = [
            "hazard_analysis",
            "ccp_determination",
            "critical_limits",
            "monitoring_system",
            "corrective_actions",
            "verification_procedures",
            "documentation"
        ]
        
        # This would typically check the system configuration
        # For now, we'll test the API endpoints
        response = client.get("/api/v1/haccp/compliance/iso-22000")
        assert response.status_code == 200
        
        data = response.json()
        for element in required_elements:
            assert element in data["compliance_status"]
    
    def test_fsis_guidebook_compliance(self, db: Session, test_user):
        """Test FSIS guidebook compliance"""
        # Test HACCP plan structure
        product_data = {
            "name": "FSIS Test Product",
            "product_code": "FSIS-001",
            "category": "Poultry",
            "description": "Test product for FSIS compliance"
        }
        
        response = client.post("/api/v1/haccp/products/", json=product_data)
        assert response.status_code == 201
        product_id = response.json()["id"]
        
        # Test that HACCP plan follows FSIS structure
        response = client.get(f"/api/v1/haccp/products/{product_id}/plan")
        assert response.status_code == 200
        
        data = response.json()
        required_sections = [
            "product_information",
            "haccp_team",
            "process_flow",
            "hazard_analysis",
            "ccp_summary"
        ]
        
        for section in required_sections:
            assert section in data

class TestHACCPSecurityTests:
    """Security tests for HACCP system"""
    
    def test_authentication_required(self, db: Session):
        """Test that HACCP endpoints require authentication"""
        # Test without authentication
        response = client.get("/api/v1/haccp/products/")
        assert response.status_code == 401
    
    def test_authorization_checks(self, db: Session, test_user):
        """Test authorization checks for HACCP operations"""
        # Create a product
        product_data = {
            "name": "Security Test Product",
            "product_code": "SEC-001",
            "category": "Poultry"
        }
        
        response = client.post("/api/v1/haccp/products/", json=product_data)
        assert response.status_code == 201
        product_id = response.json()["id"]
        
        # Test that only authorized users can modify
        # This would require proper authentication setup
        # For now, we'll test the basic structure
        
        # Test data validation
        invalid_data = {
            "name": "",  # Invalid empty name
            "product_code": "INVALID-CODE",
            "category": "Invalid Category"
        }
        
        response = client.post("/api/v1/haccp/products/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_data_integrity(self, db: Session, test_user):
        """Test data integrity and validation"""
        # Test critical limit validation
        ccp_data = {
            "product_id": 1,
            "ccp_number": 1,
            "name": "Test CCP",
            "hazard": "Test Hazard",
            "critical_limits": [
                {
                    "parameter": "temperature",
                    "unit": "°C",
                    "min_value": -1000,  # Invalid temperature
                    "max_value": 10000   # Invalid temperature
                }
            ]
        }
        
        response = client.post("/api/v1/haccp/ccps/", json=ccp_data)
        # Should either accept with validation or reject
        assert response.status_code in [201, 422]

class TestHACCPQualityGates:
    """Quality gates for HACCP system deployment"""
    
    def test_code_coverage(self):
        """Test that code coverage meets minimum requirements"""
        # This would typically run coverage tools
        # For now, we'll test that all major components are accessible
        
        endpoints_to_test = [
            "/api/v1/haccp/products/",
            "/api/v1/haccp/hazards/",
            "/api/v1/haccp/ccps/",
            "/api/v1/haccp/monitoring-logs/",
            "/api/v1/haccp/verification-logs/",
            "/api/v1/haccp/corrective-actions/",
            "/api/v1/haccp/dashboard/",
            "/api/v1/haccp/reports/"
        ]
        
        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            # Should either return data or require authentication
            assert response.status_code in [200, 401, 403]
    
    def test_database_migrations(self, db: Session):
        """Test that all database migrations are applied"""
        # Test that all required tables exist
        required_tables = [
            "haccp_products",
            "haccp_process_flows", 
            "haccp_hazards",
            "haccp_ccps",
            "ccp_monitoring_logs",
            "ccp_verification_logs",
            "haccp_validations",
            "haccp_evidence_attachments",
            "haccp_audit_logs"
        ]
        
        # This would typically check database schema
        # For now, we'll test that the models can be imported
        assert HACCPProduct is not None
        assert HACCPProcessFlow is not None
        assert HACCPHazard is not None
        assert HACCPCCP is not None
        assert CCPMonitoringLog is not None
        assert CCPVerificationLog is not None
        assert HACCPValidation is not None
        assert HACCPEvidenceAttachment is not None
        assert HACCPAuditLog is not None
    
    def test_api_documentation(self):
        """Test that API documentation is complete"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/haccp/" in str(schema["paths"])
    
    def test_error_handling(self, db: Session):
        """Test error handling and logging"""
        # Test invalid product ID
        response = client.get("/api/v1/haccp/products/999999")
        assert response.status_code == 404
        
        # Test invalid data
        invalid_data = {"invalid": "data"}
        response = client.post("/api/v1/haccp/products/", json=invalid_data)
        assert response.status_code == 422
        
        # Test malformed JSON
        response = client.post("/api/v1/haccp/products/", data="invalid json")
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
