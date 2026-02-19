"""
HACCP Phase 17 Testing - Simple Test Suite

Basic tests for HACCP system functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_haccp_products_endpoint():
    """Test HACCP products endpoint"""
    response = client.get("/api/v1/haccp/products/")
    # Should either return data or require authentication
    assert response.status_code in [200, 401, 403]

def test_haccp_dashboard_endpoint():
    """Test HACCP dashboard endpoint"""
    response = client.get("/api/v1/haccp/dashboard/")
    assert response.status_code in [200, 401, 403]

def test_haccp_reports_endpoint():
    """Test HACCP reports endpoint"""
    response = client.get("/api/v1/haccp/reports/")
    assert response.status_code in [200, 401, 403]

def test_haccp_compliance_endpoint():
    """Test HACCP compliance endpoint"""
    response = client.get("/api/v1/haccp/compliance/")
    assert response.status_code in [200, 401, 403]

def test_api_documentation():
    """Test API documentation accessibility"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    """Test OpenAPI schema accessibility"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
