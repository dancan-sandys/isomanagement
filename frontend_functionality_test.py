#!/usr/bin/env python3
"""
Frontend Functionality Testing Script
Tests all major sections of the ISO 22000 FSMS frontend application
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
    page: str
    status: str
    response_time: float
    error: Optional[str] = None
    details: Optional[Dict] = None

class FrontendTester:
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
    
    def test_page_load(self, page_path: str, section: str, page_name: str) -> FrontendTestResult:
        """Test if a page loads successfully"""
        start_time = time.time()
        url = f"{self.base_url}{page_path}"
        
        try:
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check if page contains expected content
                content = response.text.lower()
                if "error" in content and ("500" in content or "internal server error" in content):
                    status = "FAIL"
                    error = "Page contains error messages"
                elif "compiled with problems" in content:
                    status = "FAIL"
                    error = "Page has compilation errors"
                elif "not found" in content or "404" in content:
                    status = "FAIL"
                    error = "Page not found (404)"
                else:
                    status = "PASS"
                    error = None
            else:
                status = "FAIL"
                error = f"HTTP {response.status_code}"
            
            return FrontendTestResult(
                section=section,
                page=page_name,
                status=status,
                response_time=response_time,
                error=error,
                details={"url": url, "status_code": response.status_code}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return FrontendTestResult(
                section=section,
                page=page_name,
                status="ERROR",
                response_time=response_time,
                error=str(e),
                details={"url": url}
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
                page=test_name,
                status=status,
                response_time=response_time,
                error=error,
                details={"url": url, "status_code": response.status_code}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return FrontendTestResult(
                section=section,
                page=test_name,
                status="ERROR",
                response_time=response_time,
                error=str(e),
                details={"url": url}
            )
    
    def test_dashboard(self):
        """Test dashboard functionality"""
        print("\n🏠 Testing Dashboard...")
        
        # Test main dashboard page
        result = self.test_page_load("/", "Dashboard", "Main Dashboard")
        self.test_results.append(result)
        
        # Test dashboard API
        result = self.test_api_endpoint("/dashboard/stats", "Dashboard", "Dashboard Stats API")
        self.test_results.append(result)
        
        # Test recent activity
        result = self.test_api_endpoint("/dashboard/recent-activity", "Dashboard", "Recent Activity API")
        self.test_results.append(result)
    
    def test_authentication(self):
        """Test authentication functionality"""
        print("\n🔐 Testing Authentication...")
        
        # Test login page
        result = self.test_page_load("/login", "Authentication", "Login Page")
        self.test_results.append(result)
        
        # Test auth API
        result = self.test_api_endpoint("/auth/me", "Authentication", "Current User API")
        self.test_results.append(result)
    
    def test_users(self):
        """Test user management"""
        print("\n👥 Testing User Management...")
        
        # Test users page (correct route)
        result = self.test_page_load("/users", "Users", "Users List Page")
        self.test_results.append(result)
        
        # Test users API
        result = self.test_api_endpoint("/users/", "Users", "Users API")
        self.test_results.append(result)
    
    def test_documents(self):
        """Test document management"""
        print("\n📄 Testing Document Management...")
        
        # Test documents page
        result = self.test_page_load("/documents", "Documents", "Documents List Page")
        self.test_results.append(result)
        
        # Test documents API
        result = self.test_api_endpoint("/documents", "Documents", "Documents API")
        self.test_results.append(result)
        
        # Test document stats
        result = self.test_api_endpoint("/documents/stats/overview", "Documents", "Document Stats API")
        self.test_results.append(result)
    
    def test_haccp(self):
        """Test HACCP functionality"""
        print("\n🥛 Testing HACCP...")
        
        # Test HACCP page
        result = self.test_page_load("/haccp", "HACCP", "HACCP Main Page")
        self.test_results.append(result)
        
        # Test HACCP API
        result = self.test_api_endpoint("/haccp/products", "HACCP", "HACCP Products API")
        self.test_results.append(result)
        
        # Test HACCP dashboard
        result = self.test_api_endpoint("/haccp/dashboard", "HACCP", "HACCP Dashboard API")
        self.test_results.append(result)
    
    def test_suppliers(self):
        """Test supplier management"""
        print("\n🏭 Testing Supplier Management...")
        
        # Test suppliers page
        result = self.test_page_load("/suppliers", "Suppliers", "Suppliers List Page")
        self.test_results.append(result)
        
        # Test suppliers API
        result = self.test_api_endpoint("/suppliers", "Suppliers", "Suppliers API")
        self.test_results.append(result)
        
        # Test supplier dashboard
        result = self.test_api_endpoint("/suppliers/dashboard/stats", "Suppliers", "Supplier Dashboard API")
        self.test_results.append(result)
    
    def test_traceability(self):
        """Test traceability functionality"""
        print("\n🔍 Testing Traceability...")
        
        # Test traceability page
        result = self.test_page_load("/traceability", "Traceability", "Traceability Main Page")
        self.test_results.append(result)
        
        # Test traceability API
        result = self.test_api_endpoint("/traceability/batches", "Traceability", "Batches API")
        self.test_results.append(result)
        
        # Test recalls API
        result = self.test_api_endpoint("/traceability/recalls", "Traceability", "Recalls API")
        self.test_results.append(result)
    
    def test_audits(self):
        """Test audit management"""
        print("\n📋 Testing Audit Management...")
        
        # Test audits page
        result = self.test_page_load("/audits", "Audits", "Audits List Page")
        self.test_results.append(result)
        
        # Test audits API
        result = self.test_api_endpoint("/audits/", "Audits", "Audits API")
        self.test_results.append(result)
        
        # Test audit stats
        result = self.test_api_endpoint("/audits/stats", "Audits", "Audit Stats API")
        self.test_results.append(result)
    
    def test_risk(self):
        """Test risk management"""
        print("\n⚠️ Testing Risk Management...")
        
        # Test risk page (correct route)
        result = self.test_page_load("/compliance/risks", "Risk", "Risk Management Page")
        self.test_results.append(result)
        
        # Test risk API
        result = self.test_api_endpoint("/risk", "Risk", "Risk API")
        self.test_results.append(result)
        
        # Test risk stats
        result = self.test_api_endpoint("/risk/stats/overview", "Risk", "Risk Stats API")
        self.test_results.append(result)
    
    def test_nonconformance(self):
        """Test nonconformance management"""
        print("\n❌ Testing Nonconformance Management...")
        
        # Test nonconformance page (correct route)
        result = self.test_page_load("/nonconformance", "Nonconformance", "NC/CAPA Page")
        self.test_results.append(result)
        
        # Test nonconformance API
        result = self.test_api_endpoint("/nonconformance/", "Nonconformance", "Nonconformance API")
        self.test_results.append(result)
        
        # Test CAPA API
        result = self.test_api_endpoint("/nonconformance/capas/", "Nonconformance", "CAPA API")
        self.test_results.append(result)
    
    def test_complaints(self):
        """Test complaints management"""
        print("\n📞 Testing Complaints Management...")
        
        # Test complaints page
        result = self.test_page_load("/complaints", "Complaints", "Complaints Page")
        self.test_results.append(result)
        
        # Test complaints API
        result = self.test_api_endpoint("/complaints", "Complaints", "Complaints API")
        self.test_results.append(result)
    
    def test_training(self):
        """Test training management"""
        print("\n🎓 Testing Training Management...")
        
        # Test training page
        result = self.test_page_load("/training", "Training", "Training Page")
        self.test_results.append(result)
        
        # Test training API
        result = self.test_api_endpoint("/training/programs", "Training", "Training Programs API")
        self.test_results.append(result)
        
        # Test training matrix
        result = self.test_api_endpoint("/training/matrix/me", "Training", "Training Matrix API")
        self.test_results.append(result)
    
    def test_equipment(self):
        """Test equipment management"""
        print("\n🔧 Testing Equipment Management...")
        
        # Test equipment page (correct route)
        result = self.test_page_load("/maintenance/equipment", "Equipment", "Equipment Page")
        self.test_results.append(result)
        
        # Test equipment API
        result = self.test_api_endpoint("/equipment", "Equipment", "Equipment API")
        self.test_results.append(result)
        
        # Test equipment stats
        result = self.test_api_endpoint("/equipment/stats", "Equipment", "Equipment Stats API")
        self.test_results.append(result)
    
    def test_management_review(self):
        """Test management review"""
        print("\n📊 Testing Management Review...")
        
        # Test management review page (correct route)
        result = self.test_page_load("/management-reviews", "Management Review", "Management Review Page")
        self.test_results.append(result)
        
        # Test management review API
        result = self.test_api_endpoint("/management-reviews", "Management Review", "Management Review API")
        self.test_results.append(result)
    
    def test_notifications(self):
        """Test notifications"""
        print("\n🔔 Testing Notifications...")
        
        # Test notifications API
        result = self.test_api_endpoint("/notifications", "Notifications", "Notifications API")
        self.test_results.append(result)
        
        # Test notification summary
        result = self.test_api_endpoint("/notifications/summary", "Notifications", "Notification Summary API")
        self.test_results.append(result)
    
    def test_settings(self):
        """Test settings"""
        print("\n⚙️ Testing Settings...")
        
        # Test settings page
        result = self.test_page_load("/settings", "Settings", "Settings Page")
        self.test_results.append(result)
        
        # Test settings API
        result = self.test_api_endpoint("/settings", "Settings", "Settings API")
        self.test_results.append(result)
    
    def test_allergen_label(self):
        """Test allergen label management"""
        print("\n🏷️ Testing Allergen Label Management...")
        
        # Test allergen label page (correct route)
        result = self.test_page_load("/compliance/allergen-label", "Allergen Label", "Allergen Label Page")
        self.test_results.append(result)
        
        # Test allergen label API
        result = self.test_api_endpoint("/allergen-label/assessments", "Allergen Label", "Allergen Assessments API")
        self.test_results.append(result)
    
    def test_rbac(self):
        """Test RBAC functionality"""
        print("\n🔐 Testing RBAC...")
        
        # Test RBAC API
        result = self.test_api_endpoint("/rbac/roles", "RBAC", "Roles API")
        self.test_results.append(result)
        
        # Test permissions API
        result = self.test_api_endpoint("/rbac/permissions", "RBAC", "Permissions API")
        self.test_results.append(result)
    
    def test_search(self):
        """Test search functionality"""
        print("\n🔍 Testing Search...")
        
        # Test search API
        result = self.test_api_endpoint("/search/smart?q=test&limit=10", "Search", "Smart Search API")
        self.test_results.append(result)
    
    def run_all_tests(self):
        """Run all frontend functionality tests"""
        print("🚀 Starting Frontend Functionality Testing...")
        print(f"Frontend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without successful login")
            return
        
        # Run all test categories (excluding PRP as requested)
        self.test_dashboard()
        self.test_authentication()
        self.test_users()
        self.test_documents()
        self.test_haccp()
        self.test_suppliers()
        self.test_traceability()
        self.test_audits()
        self.test_risk()
        self.test_nonconformance()
        self.test_complaints()
        self.test_training()
        self.test_equipment()
        self.test_management_review()
        self.test_notifications()
        self.test_settings()
        self.test_allergen_label()
        self.test_rbac()
        self.test_search()
        
        self.print_results()
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("📊 FRONTEND FUNCTIONALITY TEST RESULTS")
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
                    print(f"  {result.section} - {result.page}")
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
        filename = f"frontend_test_results_{timestamp}.json"
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "frontend_url": self.base_url,
            "api_url": self.api_url,
            "results": [
                {
                    "section": r.section,
                    "page": r.page,
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
    print("🔧 ISO 22000 FSMS Frontend Functionality Testing Tool")
    print("="*60)
    
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
    tester = FrontendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
