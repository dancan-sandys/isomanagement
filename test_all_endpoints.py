#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints from the frontend perspective to ensure they work end-to-end.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TestResult:
    endpoint: str
    method: str
    status: str
    response_time: float
    error: Optional[str] = None
    response_data: Optional[Dict] = None

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_results: List[TestResult] = []
        
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """Login and get access token"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle the actual response format from the backend
                if data.get("success") and data.get("data"):
                    self.access_token = data["data"].get("access_token")
                    self.refresh_token = data["data"].get("refresh_token")
                else:
                    # Fallback for different response format
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                
                if self.access_token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    print(f"✅ Login successful for user: {username}")
                    return True
                else:
                    print(f"❌ No access token in response: {data}")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, expected_status: int = 200) -> TestResult:
        """Test a single endpoint"""
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                status = "PASS"
                error = None
            else:
                status = "FAIL"
                error = f"Expected {expected_status}, got {response.status_code}: {response.text}"
            
            return TestResult(
                endpoint=endpoint,
                method=method,
                status=status,
                response_time=response_time,
                error=error,
                response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status="ERROR",
                response_time=response_time,
                error=str(e)
            )
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test login
        result = self.test_endpoint("POST", "/auth/login", 
                                  data={"username": "admin", "password": "admin123"})
        self.test_results.append(result)
        
        # Test get current user
        result = self.test_endpoint("GET", "/auth/me")
        self.test_results.append(result)
        
        # Test logout
        result = self.test_endpoint("POST", "/auth/logout")
        self.test_results.append(result)
    
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        endpoints = [
            ("GET", "/dashboard/stats"),
            ("GET", "/dashboard/recent-activity"),
            ("GET", "/dashboard/compliance-metrics"),
            ("GET", "/dashboard/system-status"),
            ("GET", "/dashboard/cross-module-kpis"),
            ("GET", "/dashboard/fsms-compliance-score"),
            ("GET", "/dashboard/iso-summary"),
            ("GET", "/dashboard/overview"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_users_endpoints(self):
        """Test users endpoints"""
        print("\n👥 Testing Users Endpoints...")
        
        endpoints = [
            ("GET", "/users/"),
            ("GET", "/users/", {"page": 1, "size": 10}),
        ]
        
        for endpoint_data in endpoints:
            if len(endpoint_data) == 2:
                method, endpoint = endpoint_data
                result = self.test_endpoint(method, endpoint)
            elif len(endpoint_data) == 3:
                method, endpoint, params = endpoint_data
                result = self.test_endpoint(method, endpoint, params=params)
            self.test_results.append(result)
    
    def test_documents_endpoints(self):
        """Test documents endpoints"""
        print("\n📄 Testing Documents Endpoints...")
        
        endpoints = [
            ("GET", "/documents"),
            ("GET", "/documents", {"page": 1, "size": 10}),
            ("GET", "/documents/stats/overview"),
            ("GET", "/documents/approval-users"),
            ("GET", "/documents/approvals/pending"),
        ]
        
        for endpoint_data in endpoints:
            if len(endpoint_data) == 2:
                method, endpoint = endpoint_data
                result = self.test_endpoint(method, endpoint)
            elif len(endpoint_data) == 3:
                method, endpoint, params = endpoint_data
                result = self.test_endpoint(method, endpoint, params=params)
            self.test_results.append(result)
    
    def test_haccp_endpoints(self):
        """Test HACCP endpoints"""
        print("\n🥛 Testing HACCP Endpoints...")
        
        endpoints = [
            ("GET", "/haccp/products"),
            ("GET", "/haccp/dashboard"),
            ("GET", "/haccp/dashboard/enhanced"),
            ("GET", "/haccp/alerts/summary", {"days": 7}),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_prp_endpoints(self):
        """Test PRP endpoints"""
        print("\n🔧 Testing PRP Endpoints...")
        
        endpoints = [
            ("GET", "/prp/programs"),
            ("GET", "/prp/dashboard"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_suppliers_endpoints(self):
        """Test suppliers endpoints"""
        print("\n🏭 Testing Suppliers Endpoints...")
        
        endpoints = [
            ("GET", "/suppliers"),
            ("GET", "/suppliers", {"page": 1, "size": 10}),
            ("GET", "/suppliers/dashboard/stats"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_traceability_endpoints(self):
        """Test traceability endpoints"""
        print("\n🔍 Testing Traceability Endpoints...")
        
        endpoints = [
            ("GET", "/traceability/batches"),
            ("GET", "/traceability/batches", {"page": 1, "size": 10}),
            ("GET", "/traceability/dashboard/enhanced"),
            ("GET", "/traceability/recalls"),
            ("GET", "/traceability/reports"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_audits_endpoints(self):
        """Test audits endpoints"""
        print("\n📋 Testing Audits Endpoints...")
        
        endpoints = [
            ("GET", "/audits/"),
            ("GET", "/audits/", {"page": 1, "size": 10}),
            ("GET", "/audits/stats"),
            ("GET", "/audits/kpis/overview"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_risk_endpoints(self):
        """Test risk endpoints"""
        print("\n⚠️ Testing Risk Endpoints...")
        
        endpoints = [
            ("GET", "/risk"),
            ("GET", "/risk", {"page": 1, "size": 10}),
            ("GET", "/risk/stats/overview"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_nonconformance_endpoints(self):
        """Test nonconformance endpoints"""
        print("\n❌ Testing Nonconformance Endpoints...")
        
        endpoints = [
            ("GET", "/nonconformance/"),
            ("GET", "/nonconformance/", {"page": 1, "size": 10}),
            ("GET", "/nonconformance/capas/"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_complaints_endpoints(self):
        """Test complaints endpoints"""
        print("\n📞 Testing Complaints Endpoints...")
        
        endpoints = [
            ("GET", "/complaints"),
            ("GET", "/complaints", {"page": 1, "size": 10}),
            ("GET", "/complaints/reports/trends"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_training_endpoints(self):
        """Test training endpoints"""
        print("\n🎓 Testing Training Endpoints...")
        
        endpoints = [
            ("GET", "/training/programs"),
            ("GET", "/training/matrix/me"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_equipment_endpoints(self):
        """Test equipment endpoints"""
        print("\n🔧 Testing Equipment Endpoints...")
        
        endpoints = [
            ("GET", "/equipment"),
            ("GET", "/equipment/stats"),
            ("GET", "/equipment/upcoming-maintenance"),
            ("GET", "/equipment/overdue-calibrations"),
            ("GET", "/equipment/alerts"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_management_review_endpoints(self):
        """Test management review endpoints"""
        print("\n📊 Testing Management Review Endpoints...")
        
        endpoints = [
            ("GET", "/management-reviews"),
            ("GET", "/management-reviews", {"page": 1, "size": 10}),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_notifications_endpoints(self):
        """Test notifications endpoints"""
        print("\n🔔 Testing Notifications Endpoints...")
        
        endpoints = [
            ("GET", "/notifications"),
            ("GET", "/notifications", {"page": 1, "size": 10}),
            ("GET", "/notifications/unread"),
            ("GET", "/notifications/summary"),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_settings_endpoints(self):
        """Test settings endpoints"""
        print("\n⚙️ Testing Settings Endpoints...")
        
        endpoints = [
            ("GET", "/settings"),
            ("GET", "/settings/preferences/me"),
            ("GET", "/settings/system-info"),
            ("GET", "/settings/backup-status"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_allergen_label_endpoints(self):
        """Test allergen label endpoints"""
        print("\n🏷️ Testing Allergen Label Endpoints...")
        
        endpoints = [
            ("GET", "/allergen-label/assessments"),
            ("GET", "/allergen-label/templates"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_rbac_endpoints(self):
        """Test RBAC endpoints"""
        print("\n🔐 Testing RBAC Endpoints...")
        
        endpoints = [
            ("GET", "/rbac/roles"),
            ("GET", "/rbac/permissions"),
        ]
        
        for method, endpoint in endpoints:
            result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def test_search_endpoints(self):
        """Test search endpoints"""
        print("\n🔍 Testing Search Endpoints...")
        
        endpoints = [
            ("GET", "/search/smart", {"q": "test", "limit": 10}),
        ]
        
        for method, endpoint in endpoints:
            if isinstance(endpoint, tuple):
                endpoint, params = endpoint
                result = self.test_endpoint(method, endpoint, params=params)
            else:
                result = self.test_endpoint(method, endpoint)
            self.test_results.append(result)
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Comprehensive API Endpoint Testing...")
        print(f"Base URL: {self.base_url}")
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without successful login")
            return
        
        # Run all test categories
        self.test_auth_endpoints()
        self.test_dashboard_endpoints()
        self.test_users_endpoints()
        self.test_documents_endpoints()
        self.test_haccp_endpoints()
        self.test_prp_endpoints()
        self.test_suppliers_endpoints()
        self.test_traceability_endpoints()
        self.test_audits_endpoints()
        self.test_risk_endpoints()
        self.test_nonconformance_endpoints()
        self.test_complaints_endpoints()
        self.test_training_endpoints()
        self.test_equipment_endpoints()
        self.test_management_review_endpoints()
        self.test_notifications_endpoints()
        self.test_settings_endpoints()
        self.test_allergen_label_endpoints()
        self.test_rbac_endpoints()
        self.test_search_endpoints()
        
        self.print_results()
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        error_tests = len([r for r in self.test_results if r.status == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests
        if failed_tests > 0 or error_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result.status in ["FAIL", "ERROR"]:
                    print(f"  {result.method} {result.endpoint}")
                    print(f"    Error: {result.error}")
                    print()
        
        # Show response times
        avg_response_time = sum(r.response_time for r in self.test_results) / total_tests
        max_response_time = max(r.response_time for r in self.test_results)
        print(f"\n⏱️ Performance:")
        print(f"  Average Response Time: {avg_response_time:.3f}s")
        print(f"  Max Response Time: {max_response_time:.3f}s")
        
        # Save detailed results to file
        self.save_results()
    
    def save_results(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_results_{timestamp}.json"
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status": r.status,
                    "response_time": r.response_time,
                    "error": r.error,
                    "response_data": r.response_data
                }
                for r in self.test_results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {filename}")

def main():
    """Main function"""
    print("🔧 ISO 22000 FSMS API Endpoint Testing Tool")
    print("="*50)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running or not accessible")
            print("Please start the backend server first:")
            print("cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Backend is not running or not accessible")
        print("Please start the backend server first:")
        print("cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
        sys.exit(1)
    
    print("✅ Backend is running")
    
    # Run tests
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
