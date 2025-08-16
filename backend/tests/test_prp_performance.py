"""
Performance Tests for PRP Module

This module contains comprehensive performance tests to ensure the PRP module
meets performance requirements and can handle large datasets efficiently.
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import psutil
import os

from app.main import app
from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, RiskAssessment, 
    RiskControl, CorrectiveAction, PreventiveAction
)
from app.models.user import User
from app.core.database import get_db

client = TestClient(app)

class TestPRPPerformance:
    """Performance tests for PRP module"""
    
    @pytest.fixture
    def test_user(self, db: Session):
        """Create a test user for performance testing"""
        user = User(
            username="perf_user",
            email="perf@example.com",
            full_name="Performance Test User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def test_program_creation_performance(self, db: Session, test_user):
        """Test PRP program creation performance"""
        start_time = time.time()
        
        program_data = {
            "program_code": "PERF-PRG-001",
            "name": "Performance Test Program",
            "description": "Test program for performance testing",
            "category": "cleaning_and_sanitizing",
            "objective": "Test objective",
            "scope": "Test scope",
            "sop_reference": "SOP-PERF-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
    
    def test_bulk_program_creation_performance(self, db: Session, test_user):
        """Test bulk PRP program creation performance"""
        start_time = time.time()
        
        programs_created = 0
        for i in range(100):
            program_data = {
                "program_code": f"BULK-PRG-{i:03d}",
                "name": f"Bulk Performance Program {i}",
                "description": f"Bulk performance test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {i}",
                "scope": f"Scope {i}",
                "sop_reference": f"SOP-BULK-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            if response.status_code == 201:
                programs_created += 1
        
        end_time = time.time()
        
        assert programs_created == 100, "All programs should be created successfully"
        assert (end_time - start_time) < 30.0  # Should complete within 30 seconds
        print(f"Created {programs_created} programs in {end_time - start_time:.2f} seconds")
    
    def test_program_listing_performance(self, db: Session, test_user):
        """Test PRP program listing performance with pagination"""
        # First create some programs
        for i in range(50):
            program_data = {
                "program_code": f"LIST-PRG-{i:03d}",
                "name": f"Listing Performance Program {i}",
                "description": f"Listing performance test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {i}",
                "scope": f"Scope {i}",
                "sop_reference": f"SOP-LIST-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            client.post("/api/v1/prp/programs/", json=program_data)
        
        # Test listing performance
        start_time = time.time()
        response = client.get("/api/v1/prp/programs/?page=1&size=25")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
        
        data = response.json()
        assert len(data.get("items", [])) <= 25
        print(f"Listed programs in {end_time - start_time:.2f} seconds")
    
    def test_risk_assessment_performance(self, db: Session, test_user):
        """Test risk assessment creation and retrieval performance"""
        # Create a program first
        program_data = {
            "program_code": "RISK-PERF-001",
            "name": "Risk Performance Test",
            "description": "Test program for risk assessment performance",
            "category": "pest_control",
            "objective": "Test objective",
            "scope": "Test scope",
            "sop_reference": "SOP-RISK-PERF-001",
            "frequency": "weekly",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Test risk assessment creation performance
        start_time = time.time()
        
        risk_data = {
            "hazard_identified": "Performance Test Hazard",
            "hazard_description": "Test hazard for performance testing",
            "likelihood_level": "Medium",
            "severity_level": "High",
            "existing_controls": "Test controls",
            "additional_controls_required": "Additional test controls",
            "control_effectiveness": "Effective",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/risk-assessments", json=risk_data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
        
        risk_assessment = response.json()
        
        # Test risk assessment retrieval performance
        start_time = time.time()
        response = client.get(f"/api/v1/prp/risk-assessments/{risk_assessment['id']}")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.5  # Should complete within 0.5 seconds
    
    def test_capa_performance(self, db: Session, test_user):
        """Test CAPA creation and management performance"""
        # Create a program first
        program_data = {
            "program_code": "CAPA-PERF-001",
            "name": "CAPA Performance Test",
            "description": "Test program for CAPA performance",
            "category": "personnel_hygiene_practices",
            "objective": "Test objective",
            "scope": "Test scope",
            "sop_reference": "SOP-CAPA-PERF-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Test corrective action creation performance
        start_time = time.time()
        
        capa_data = {
            "title": "Performance Test CAPA",
            "description": "Test CAPA for performance testing",
            "root_cause": "Performance test root cause",
            "action_type": "immediate",
            "priority": "high",
            "assigned_to": "Test User",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "effectiveness_rating": 4,
            "cost_estimate": 1000.0,
            "verification_method": "Performance testing",
            "program_id": program["id"]
        }
        
        response = client.post("/api/v1/prp/corrective-actions", json=capa_data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
        
        capa = response.json()
        
        # Test CAPA dashboard performance
        start_time = time.time()
        response = client.get("/api/v1/prp/capa/dashboard")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
    
    def test_checklist_performance(self, db: Session, test_user):
        """Test checklist creation and completion performance"""
        # Create a program first
        program_data = {
            "program_code": "CHK-PERF-001",
            "name": "Checklist Performance Test",
            "description": "Test program for checklist performance",
            "category": "cleaning_and_sanitizing",
            "objective": "Test objective",
            "scope": "Test scope",
            "sop_reference": "SOP-CHK-PERF-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Test checklist creation performance
        start_time = time.time()
        
        checklist_data = {
            "checklist_code": "PERF-CHK-001",
            "name": "Performance Test Checklist",
            "description": "Test checklist for performance testing",
            "scheduled_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(hours=8)).isoformat(),
            "assigned_to": test_user.id
        }
        
        response = client.post(f"/api/v1/prp/programs/{program['id']}/checklists", json=checklist_data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
        
        checklist = response.json()
        
        # Test checklist item creation performance
        start_time = time.time()
        
        item_data = {
            "item_text": "Performance test item",
            "item_type": "verification",
            "required_response": True,
            "expected_response": "Yes",
            "order_number": 1
        }
        
        response = client.post(f"/api/v1/prp/checklists/{checklist['id']}/items", json=item_data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 0.5  # Should complete within 0.5 seconds
    
    def test_analytics_performance(self, db: Session, test_user):
        """Test analytics and reporting performance"""
        # Create a program first
        program_data = {
            "program_code": "ANALYTICS-PERF-001",
            "name": "Analytics Performance Test",
            "description": "Test program for analytics performance",
            "category": "cleaning_and_sanitizing",
            "objective": "Test objective",
            "scope": "Test scope",
            "sop_reference": "SOP-ANALYTICS-PERF-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Test analytics performance
        start_time = time.time()
        response = client.get(f"/api/v1/prp/programs/{program['id']}/analytics")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0  # Should complete within 3 seconds
        
        # Test performance trends
        start_time = time.time()
        response = client.get(f"/api/v1/prp/programs/{program['id']}/performance-trends")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
    
    def test_search_performance(self, db: Session, test_user):
        """Test advanced search performance"""
        # Create some programs for search testing
        for i in range(20):
            program_data = {
                "program_code": f"SEARCH-PRG-{i:03d}",
                "name": f"Search Performance Program {i}",
                "description": f"Search performance test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Search objective {i}",
                "scope": f"Search scope {i}",
                "sop_reference": f"SOP-SEARCH-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            client.post("/api/v1/prp/programs/", json=program_data)
        
        # Test search performance
        start_time = time.time()
        
        search_data = {
            "query": "performance",
            "filters": {
                "category": "cleaning_and_sanitizing",
                "status": "active"
            },
            "sort_by": "created_at",
            "sort_order": "desc"
        }
        
        response = client.post("/api/v1/prp/search/advanced", json=search_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
        
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_concurrent_operations_performance(self, db: Session, test_user):
        """Test concurrent operations performance"""
        results = []
        errors = []
        
        def create_program(program_id):
            try:
                program_data = {
                    "program_code": f"CONC-PRG-{program_id:03d}",
                    "name": f"Concurrent Program {program_id}",
                    "description": f"Concurrent test program {program_id}",
                    "category": "cleaning_and_sanitizing",
                    "objective": f"Objective {program_id}",
                    "scope": f"Scope {program_id}",
                    "sop_reference": f"SOP-CONC-{program_id:03d}",
                    "frequency": "daily",
                    "status": "active",
                    "assigned_to": test_user.id
                }
                
                response = client.post("/api/v1/prp/programs/", json=program_data)
                results.append(response.status_code == 201)
            except Exception as e:
                errors.append(str(e))
        
        # Create 10 threads to create programs concurrently
        threads = []
        start_time = time.time()
        
        for i in range(10):
            thread = threading.Thread(target=create_program, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent operations failed: {errors}"
        assert all(results), "All concurrent operations should succeed"
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds
        
        print(f"Completed {len(results)} concurrent operations in {end_time - start_time:.2f} seconds")
    
    def test_memory_usage_performance(self, db: Session, test_user):
        """Test memory usage during operations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple programs to test memory usage
        for i in range(50):
            program_data = {
                "program_code": f"MEM-PRG-{i:03d}",
                "name": f"Memory Test Program {i}",
                "description": f"Memory test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {i}",
                "scope": f"Scope {i}",
                "sop_reference": f"SOP-MEM-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            client.post("/api/v1/prp/programs/", json=program_data)
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (increase: {memory_increase:.2f}MB)")
        
        # Memory increase should be reasonable (less than 100MB for 50 programs)
        assert memory_increase < 100.0, f"Memory usage increased too much: {memory_increase:.2f}MB"
    
    def test_database_query_performance(self, db: Session, test_user):
        """Test database query performance"""
        # Create programs for testing
        for i in range(100):
            program_data = {
                "program_code": f"DB-PRG-{i:03d}",
                "name": f"Database Test Program {i}",
                "description": f"Database test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {i}",
                "scope": f"Scope {i}",
                "sop_reference": f"SOP-DB-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            client.post("/api/v1/prp/programs/", json=program_data)
        
        # Test different query patterns
        queries = [
            ("/api/v1/prp/programs/?page=1&size=10", "Basic pagination"),
            ("/api/v1/prp/programs/?category=cleaning_and_sanitizing", "Category filter"),
            ("/api/v1/prp/programs/?status=active", "Status filter"),
            ("/api/v1/prp/programs/?page=1&size=50&category=cleaning_and_sanitizing&status=active", "Complex filter")
        ]
        
        for query_url, description in queries:
            start_time = time.time()
            response = client.get(query_url)
            end_time = time.time()
            
            assert response.status_code == 200
            query_time = end_time - start_time
            
            print(f"{description}: {query_time:.3f} seconds")
            assert query_time < 2.0, f"{description} took too long: {query_time:.3f} seconds"
    
    def test_api_response_time_performance(self, db: Session, test_user):
        """Test API response time performance"""
        # Create a test program
        program_data = {
            "program_code": "RESPONSE-PERF-001",
            "name": "Response Time Performance Test",
            "description": "Test program for response time performance",
            "category": "cleaning_and_sanitizing",
            "objective": "Test objective",
            "scope": "Test scope",
            "sop_reference": "SOP-RESPONSE-PERF-001",
            "frequency": "daily",
            "status": "active",
            "assigned_to": test_user.id
        }
        
        response = client.post("/api/v1/prp/programs/", json=program_data)
        assert response.status_code == 201
        program = response.json()
        
        # Test various API endpoints for response time
        endpoints = [
            ("/api/v1/prp/programs/", "GET", None, "List programs"),
            (f"/api/v1/prp/programs/{program['id']}", "GET", None, "Get program"),
            (f"/api/v1/prp/programs/{program['id']}/analytics", "GET", None, "Program analytics"),
            ("/api/v1/prp/capa/dashboard", "GET", None, "CAPA dashboard"),
            ("/api/v1/prp/performance/metrics", "GET", None, "Performance metrics")
        ]
        
        for endpoint, method, data, description in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code in [200, 201], f"{description} failed: {response.status_code}"
            print(f"{description}: {response_time:.3f} seconds")
            
            # Response time should be under 2 seconds for most operations
            max_time = 3.0 if "analytics" in description else 2.0
            assert response_time < max_time, f"{description} took too long: {response_time:.3f} seconds"


class TestLoadTesting:
    """Load testing for PRP module"""
    
    def test_high_load_program_creation(self, db: Session, test_user):
        """Test high load program creation"""
        start_time = time.time()
        
        # Create 500 programs under high load
        programs_created = 0
        for i in range(500):
            program_data = {
                "program_code": f"LOAD-PRG-{i:03d}",
                "name": f"Load Test Program {i}",
                "description": f"Load test program {i}",
                "category": "cleaning_and_sanitizing",
                "objective": f"Objective {i}",
                "scope": f"Scope {i}",
                "sop_reference": f"SOP-LOAD-{i:03d}",
                "frequency": "daily",
                "status": "active",
                "assigned_to": test_user.id
            }
            
            response = client.post("/api/v1/prp/programs/", json=program_data)
            if response.status_code == 201:
                programs_created += 1
        
        end_time = time.time()
        
        success_rate = (programs_created / 500) * 100
        print(f"Created {programs_created}/500 programs ({success_rate:.1f}% success rate) in {end_time - start_time:.2f} seconds")
        
        assert success_rate >= 95.0, f"Success rate too low: {success_rate:.1f}%"
        assert (end_time - start_time) < 120.0, f"Load test took too long: {end_time - start_time:.2f} seconds"
    
    def test_concurrent_user_simulation(self, db: Session):
        """Test concurrent user simulation"""
        # Create multiple test users
        users = []
        for i in range(5):
            user_data = {
                "username": f"load_user_{i}",
                "email": f"load_user_{i}@example.com",
                "full_name": f"Load Test User {i}",
                "is_active": True
            }
            # Note: In a real test, you'd need to create users through the API
            users.append(user_data)
        
        results = []
        
        def simulate_user_activity(user_id):
            try:
                # Simulate user creating programs
                for i in range(10):
                    program_data = {
                        "program_code": f"USER-{user_id}-PRG-{i:03d}",
                        "name": f"User {user_id} Program {i}",
                        "description": f"User {user_id} test program {i}",
                        "category": "cleaning_and_sanitizing",
                        "objective": f"Objective {i}",
                        "scope": f"Scope {i}",
                        "sop_reference": f"SOP-USER-{user_id}-{i:03d}",
                        "frequency": "daily",
                        "status": "active",
                        "assigned_to": user_id
                    }
                    
                    response = client.post("/api/v1/prp/programs/", json=program_data)
                    results.append(response.status_code == 201)
            except Exception as e:
                results.append(False)
        
        # Simulate 5 concurrent users
        threads = []
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=simulate_user_activity, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        success_rate = (sum(results) / len(results)) * 100 if results else 0
        print(f"Concurrent user simulation: {success_rate:.1f}% success rate in {end_time - start_time:.2f} seconds")
        
        assert success_rate >= 90.0, f"Concurrent user success rate too low: {success_rate:.1f}%"


if __name__ == "__main__":
    pytest.main([__file__])
