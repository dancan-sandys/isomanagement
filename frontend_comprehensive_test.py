#!/usr/bin/env python3
"""
Comprehensive Frontend Functionality Testing Script
Tests the ISO 22000 FSMS frontend application focusing on API integration and core functionality
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class FrontendTestResult:
    section: str
    test_name: str
    status: str
    response_time: float
    error: Optional[str] = None
    details: Optional[Dict] = None

class ComprehensiveFrontendTester:
    def __init__(self, base_url: str = "http://localhost:3000", api_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.api_url = api_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results: List[FrontendTestResult] = []
        
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """Login and get access token"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    self.access_token = data["data"].get("access_token")
                    self.refresh_token = data["data"].get("refresh_token")
                    
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
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_frontend_app_serving(self) -> FrontendTestResult:
        """Test if the React app is being served correctly"""
        start_time = time.time()
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text.lower()
                # Check if it's a React app (contains React-related content)
                if "react" in content or "root" in content or "app" in content:
                    status = "PASS"
                    error = None
                else:
                    status = "FAIL"
                    error = "Not a React application"
            else:
                status = "FAIL"
                error = f"HTTP {response.status_code}"
            
            return FrontendTestResult(
                section="Frontend",
                test_name="React App Serving",
                status=status,
                response_time=response_time,
                error=error,
                details={"url": self.base_url, "status_code": response.status_code}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return FrontendTestResult(
                section="Frontend",
                test_name="React App Serving",
                status="ERROR",
                response_time=response_time,
                error=str(e),
                details={"url": self.base_url}
            )
    
    def test_api_endpoint(self, endpoint: str, section: str, test_name: str) -> FrontendTestResult:
        """Test API endpoint functionality"""
        start_time = time.time()
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                status = "PASS"
                error = None
            else:
                status = "FAIL"
                error = f"HTTP {response.status_code}: {response.text}"
            
            return FrontendTestResult(
                section=section,
                test_name=test_name,
                status=status,
                response_time=response_time,
                error=error,
                details={"url": url, "status_code": response.status_code}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return FrontendTestResult(
                section=section,
                test_name=test_name,
                status="ERROR",
                response_time=response_time,
                error=str(e),
                details={"url": url}
            )
    
    def test_api_endpoint_post(self, endpoint: str, section: str, test_name: str) -> FrontendTestResult:
        """Test API endpoint functionality with POST method"""
        start_time = time.time()
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.post(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                status = "PASS"
                error = None
            else:
                status = "FAIL"
                error = f"HTTP {response.status_code}: {response.text}"
            
            return FrontendTestResult(
                section=section,
                test_name=test_name,
                status=status,
                response_time=response_time,
                error=error,
                details={"url": url, "status_code": response.status_code}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return FrontendTestResult(
                section=section,
                test_name=test_name,
                status="ERROR",
                response_time=response_time,
                error=str(e),
                details={"url": url}
            )
    
    def test_dashboard_functionality(self):
        """Test dashboard functionality"""
        print("\n🏠 Testing Dashboard Functionality...")
        
        # Test React app serving
        result = self.test_frontend_app_serving()
        self.test_results.append(result)
        
        # Test dashboard API
        result = self.test_api_endpoint("/dashboard/stats", "Dashboard", "Dashboard Stats API")
        self.test_results.append(result)
        
        # Test recent activity
        result = self.test_api_endpoint("/dashboard/recent-activity", "Dashboard", "Recent Activity API")
        self.test_results.append(result)
        
        # Test compliance metrics
        result = self.test_api_endpoint("/dashboard/compliance-metrics", "Dashboard", "Compliance Metrics API")
        self.test_results.append(result)
    
    def test_authentication_functionality(self):
        """Test authentication functionality"""
        print("\n🔐 Testing Authentication Functionality...")
        
        # Test current user API
        result = self.test_api_endpoint("/auth/me", "Authentication", "Current User API")
        self.test_results.append(result)
        
        # Test logout functionality (POST method)
        result = self.test_api_endpoint_post("/auth/logout", "Authentication", "Logout API")
        self.test_results.append(result)
    
    def test_user_management_functionality(self):
        """Test user management functionality"""
        print("\n👥 Testing User Management Functionality...")
        
        # Test users API
        result = self.test_api_endpoint("/users/", "Users", "Users List API")
        self.test_results.append(result)
        
        # Test user dashboard
        result = self.test_api_endpoint("/users/dashboard", "Users", "User Dashboard API")
        self.test_results.append(result)
    
    def test_document_management_functionality(self):
        """Test document management functionality"""
        print("\n📄 Testing Document Management Functionality...")
        
        # Test documents API
        result = self.test_api_endpoint("/documents", "Documents", "Documents List API")
        self.test_results.append(result)
        
        # Test document stats
        result = self.test_api_endpoint("/documents/stats/overview", "Documents", "Document Stats API")
        self.test_results.append(result)
        
        # Test approval users
        result = self.test_api_endpoint("/documents/approval-users", "Documents", "Approval Users API")
        self.test_results.append(result)
    
    def test_haccp_functionality(self):
        """Test HACCP functionality"""
        print("\n🥛 Testing HACCP Functionality...")
        
        # Test HACCP products API
        result = self.test_api_endpoint("/haccp/products", "HACCP", "HACCP Products API")
        self.test_results.append(result)
        
        # Test HACCP dashboard
        result = self.test_api_endpoint("/haccp/dashboard", "HACCP", "HACCP Dashboard API")
        self.test_results.append(result)
        
        # Test HACCP alerts
        result = self.test_api_endpoint("/haccp/alerts/summary?days=7", "HACCP", "HACCP Alerts API")
        self.test_results.append(result)
    
    def test_supplier_management_functionality(self):
        """Test supplier management functionality"""
        print("\n🏭 Testing Supplier Management Functionality...")
        
        # Test suppliers API
        result = self.test_api_endpoint("/suppliers", "Suppliers", "Suppliers List API")
        self.test_results.append(result)
        
        # Test supplier dashboard
        result = self.test_api_endpoint("/suppliers/dashboard/stats", "Suppliers", "Supplier Dashboard API")
        self.test_results.append(result)
    
    def test_traceability_functionality(self):
        """Test traceability functionality"""
        print("\n🔍 Testing Traceability Functionality...")
        
        # Test batches API
        result = self.test_api_endpoint("/traceability/batches", "Traceability", "Batches API")
        self.test_results.append(result)
        
        # Test recalls API
        result = self.test_api_endpoint("/traceability/recalls", "Traceability", "Recalls API")
        self.test_results.append(result)
        
        # Test traceability dashboard
        result = self.test_api_endpoint("/traceability/dashboard/enhanced", "Traceability", "Traceability Dashboard API")
        self.test_results.append(result)
    
    def test_audit_management_functionality(self):
        """Test audit management functionality"""
        print("\n📋 Testing Audit Management Functionality...")
        
        # Test audits API
        result = self.test_api_endpoint("/audits/", "Audits", "Audits List API")
        self.test_results.append(result)
        
        # Test audit stats
        result = self.test_api_endpoint("/audits/stats", "Audits", "Audit Stats API")
        self.test_results.append(result)
        
        # Test audit KPIs
        result = self.test_api_endpoint("/audits/kpis/overview", "Audits", "Audit KPIs API")
        self.test_results.append(result)
    
    def test_risk_management_functionality(self):
        """Test risk management functionality"""
        print("\n⚠️ Testing Risk Management Functionality...")
        
        # Test risk API
        result = self.test_api_endpoint("/risk", "Risk", "Risk List API")
        self.test_results.append(result)
        
        # Test risk stats
        result = self.test_api_endpoint("/risk/stats/overview", "Risk", "Risk Stats API")
        self.test_results.append(result)
    
    def test_nonconformance_functionality(self):
        """Test nonconformance management functionality"""
        print("\n❌ Testing Nonconformance Management Functionality...")
        
        # Test nonconformance API
        result = self.test_api_endpoint("/nonconformance/", "Nonconformance", "Nonconformance List API")
        self.test_results.append(result)
        
        # Test CAPA API
        result = self.test_api_endpoint("/nonconformance/capas/", "Nonconformance", "CAPA List API")
        self.test_results.append(result)
    
    def test_complaints_functionality(self):
        """Test complaints management functionality"""
        print("\n📞 Testing Complaints Management Functionality...")
        
        # Test complaints API
        result = self.test_api_endpoint("/complaints", "Complaints", "Complaints List API")
        self.test_results.append(result)
        
        # Test complaints trends
        result = self.test_api_endpoint("/complaints/reports/trends", "Complaints", "Complaints Trends API")
        self.test_results.append(result)
    
    def test_training_functionality(self):
        """Test training management functionality"""
        print("\n🎓 Testing Training Management Functionality...")
        
        # Test training programs API
        result = self.test_api_endpoint("/training/programs", "Training", "Training Programs API")
        self.test_results.append(result)
        
        # Test training matrix
        result = self.test_api_endpoint("/training/matrix/me", "Training", "Training Matrix API")
        self.test_results.append(result)
    
    def test_equipment_functionality(self):
        """Test equipment management functionality"""
        print("\n🔧 Testing Equipment Management Functionality...")
        
        # Test equipment API
        result = self.test_api_endpoint("/equipment", "Equipment", "Equipment List API")
        self.test_results.append(result)
        
        # Test equipment stats
        result = self.test_api_endpoint("/equipment/stats", "Equipment", "Equipment Stats API")
        self.test_results.append(result)
        
        # Test upcoming maintenance
        result = self.test_api_endpoint("/equipment/upcoming-maintenance", "Equipment", "Upcoming Maintenance API")
        self.test_results.append(result)
    
    def test_management_review_functionality(self):
        """Test management review functionality"""
        print("\n📊 Testing Management Review Functionality...")
        
        # Test management review API
        result = self.test_api_endpoint("/management-reviews", "Management Review", "Management Review API")
        self.test_results.append(result)
    
    def test_notifications_functionality(self):
        """Test notifications functionality"""
        print("\n🔔 Testing Notifications Functionality...")
        
        # Test notifications API
        result = self.test_api_endpoint("/notifications", "Notifications", "Notifications List API")
        self.test_results.append(result)
        
        # Test notification summary
        result = self.test_api_endpoint("/notifications/summary", "Notifications", "Notification Summary API")
        self.test_results.append(result)
    
    def test_settings_functionality(self):
        """Test settings functionality"""
        print("\n⚙️ Testing Settings Functionality...")
        
        # Test settings API
        result = self.test_api_endpoint("/settings", "Settings", "Settings API")
        self.test_results.append(result)
        
        # Test user preferences
        result = self.test_api_endpoint("/settings/preferences/me", "Settings", "User Preferences API")
        self.test_results.append(result)
    
    def test_allergen_label_functionality(self):
        """Test allergen label management functionality"""
        print("\n🏷️ Testing Allergen Label Management Functionality...")
        
        # Test allergen assessments API
        result = self.test_api_endpoint("/allergen-label/assessments", "Allergen Label", "Allergen Assessments API")
        self.test_results.append(result)
        
        # Test allergen templates API
        result = self.test_api_endpoint("/allergen-label/templates", "Allergen Label", "Allergen Templates API")
        self.test_results.append(result)
    
    def test_rbac_functionality(self):
        """Test RBAC functionality"""
        print("\n🔐 Testing RBAC Functionality...")
        
        # Test roles API
        result = self.test_api_endpoint("/rbac/roles", "RBAC", "Roles API")
        self.test_results.append(result)
        
        # Test permissions API
        result = self.test_api_endpoint("/rbac/permissions", "RBAC", "Permissions API")
        self.test_results.append(result)
    
    def test_search_functionality(self):
        """Test search functionality"""
        print("\n🔍 Testing Search Functionality...")
        
        # Test smart search API
        result = self.test_api_endpoint("/search/smart?q=test&limit=10", "Search", "Smart Search API")
        self.test_results.append(result)
    
    def run_all_tests(self):
        """Run all frontend functionality tests"""
        print("🚀 Starting Comprehensive Frontend Functionality Testing...")
        print(f"Frontend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without successful login")
            return
        
        # Run all test categories (excluding PRP as requested)
        self.test_dashboard_functionality()
        self.test_authentication_functionality()
        self.test_user_management_functionality()
        self.test_document_management_functionality()
        self.test_haccp_functionality()
        self.test_supplier_management_functionality()
        self.test_traceability_functionality()
        self.test_audit_management_functionality()
        self.test_risk_management_functionality()
        self.test_nonconformance_functionality()
        self.test_complaints_functionality()
        self.test_training_functionality()
        self.test_equipment_functionality()
        self.test_management_review_functionality()
        self.test_notifications_functionality()
        self.test_settings_functionality()
        self.test_allergen_label_functionality()
        self.test_rbac_functionality()
        self.test_search_functionality()
        
        self.print_results()
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE FRONTEND FUNCTIONALITY TEST RESULTS")
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
        
        # Group results by section
        sections = {}
        for result in self.test_results:
            if result.section not in sections:
                sections[result.section] = []
            sections[result.section].append(result)
        
        print(f"\n📋 RESULTS BY SECTION:")
        for section, results in sections.items():
            section_passed = len([r for r in results if r.status == "PASS"])
            section_total = len(results)
            section_rate = (section_passed/section_total)*100 if section_total > 0 else 0
            status_icon = "✅" if section_rate == 100 else "⚠️" if section_rate >= 80 else "❌"
            print(f"  {status_icon} {section}: {section_passed}/{section_total} ({section_rate:.1f}%)")
        
        # Show failed tests
        if failed_tests > 0 or error_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result.status in ["FAIL", "ERROR"]:
                    print(f"  {result.section} - {result.test_name}")
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
        filename = f"comprehensive_frontend_test_results_{timestamp}.json"
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "frontend_url": self.base_url,
            "api_url": self.api_url,
            "results": [
                {
                    "section": r.section,
                    "test_name": r.test_name,
                    "status": r.status,
                    "response_time": r.response_time,
                    "error": r.error,
                    "details": r.details
                }
                for r in self.test_results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {filename}")

def main():
    """Main function"""
    print("🔧 ISO 22000 FSMS Comprehensive Frontend Functionality Testing Tool")
    print("="*70)
    
    # Check if frontend is running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code != 200:
            print("❌ Frontend is not running or not accessible")
            print("Please start the frontend server first:")
            print("cd frontend && npm start")
            return
    except requests.exceptions.RequestException:
        print("❌ Frontend is not running or not accessible")
        print("Please start the frontend server first:")
        print("cd frontend && npm start")
        return
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running or not accessible")
            print("Please start the backend server first:")
            print("cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
            return
    except requests.exceptions.RequestException:
        print("❌ Backend is not running or not accessible")
        print("Please start the backend server first:")
        print("cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
        return
    
    print("✅ Frontend and Backend are running")
    
    # Run tests
    tester = ComprehensiveFrontendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
