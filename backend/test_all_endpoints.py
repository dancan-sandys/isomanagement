#!/usr/bin/env python3
"""
Comprehensive endpoint testing script
"""
import requests
import json
import time
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, expected_status: int = 200, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers or {})
        elif method.upper() == "POST":
            response = requests.post(url, json=data or {}, headers=headers or {})
        elif method.upper() == "PUT":
            response = requests.put(url, json=data or {}, headers=headers or {})
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers or {})
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "success": response.status_code == expected_status,
            "response": response.text[:200] if response.text else "No response body",
            "headers": dict(response.headers)
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": "ERROR",
            "expected_status": expected_status,
            "success": False,
            "error": str(e)
        }

def test_authentication_endpoints() -> List[Dict]:
    """Test authentication endpoints"""
    print("🔐 Testing Authentication Endpoints...")
    results = []
    
    # Test login endpoint (should return 422 for missing credentials)
    results.append(test_endpoint("POST", "/api/v1/auth/login", 422))
    
    # Test signup endpoint (should return 422 for missing data)
    results.append(test_endpoint("POST", "/api/v1/auth/signup", 422))
    
    return results

def test_supplier_endpoints() -> List[Dict]:
    """Test supplier endpoints"""
    print("🏭 Testing Supplier Endpoints...")
    results = []
    
    # Test GET suppliers (should work without auth)
    results.append(test_endpoint("GET", "/api/v1/suppliers", 200))
    
    # Test GET suppliers with query params
    results.append(test_endpoint("GET", "/api/v1/suppliers?page=1&size=10", 200))
    
    # Test POST supplier (should return 422 for missing data)
    results.append(test_endpoint("POST", "/api/v1/suppliers", 422))
    
    # Test supplier materials
    results.append(test_endpoint("GET", "/api/v1/suppliers/materials", 200))
    
    # Test supplier evaluations
    results.append(test_endpoint("GET", "/api/v1/suppliers/evaluations", 200))
    
    # Test supplier deliveries
    results.append(test_endpoint("GET", "/api/v1/suppliers/deliveries", 200))
    
    # Test supplier stats
    results.append(test_endpoint("GET", "/api/v1/suppliers/stats", 200))
    
    # Test supplier dashboard
    results.append(test_endpoint("GET", "/api/v1/suppliers/dashboard/stats", 200))
    
    return results

def test_user_endpoints() -> List[Dict]:
    """Test user endpoints"""
    print("👥 Testing User Endpoints...")
    results = []
    
    # Test GET users (should work without auth)
    results.append(test_endpoint("GET", "/api/v1/users", 200))
    
    # Test user dashboard
    results.append(test_endpoint("GET", "/api/v1/users/dashboard", 200))
    
    return results

def test_document_endpoints() -> List[Dict]:
    """Test document endpoints"""
    print("📄 Testing Document Endpoints...")
    results = []
    
    # Test GET documents
    results.append(test_endpoint("GET", "/api/v1/documents", 200))
    
    # Test document stats
    results.append(test_endpoint("GET", "/api/v1/documents/stats", 200))
    
    return results

def test_haccp_endpoints() -> List[Dict]:
    """Test HACCP endpoints"""
    print("🥛 Testing HACCP Endpoints...")
    results = []
    
    # Test GET products
    results.append(test_endpoint("GET", "/api/v1/haccp/products", 200))
    
    # Test GET hazards
    results.append(test_endpoint("GET", "/api/v1/haccp/hazards", 200))
    
    # Test GET CCPs
    results.append(test_endpoint("GET", "/api/v1/haccp/ccps", 200))
    
    return results

def test_prp_endpoints() -> List[Dict]:
    """Test PRP endpoints"""
    print("🛡️ Testing PRP Endpoints...")
    results = []
    
    # Test GET PRP programs
    results.append(test_endpoint("GET", "/api/v1/prp/programs", 200))
    
    # Test GET PRP checklists
    results.append(test_endpoint("GET", "/api/v1/prp/checklists", 200))
    
    return results

def test_risk_endpoints() -> List[Dict]:
    """Test risk endpoints"""
    print("⚠️ Testing Risk Endpoints...")
    results = []
    
    # Test GET risk register
    results.append(test_endpoint("GET", "/api/v1/risk/register", 200))
    
    # Test GET risk actions
    results.append(test_endpoint("GET", "/api/v1/risk/actions", 200))
    
    return results

def test_audit_endpoints() -> List[Dict]:
    """Test audit endpoints"""
    print("🔍 Testing Audit Endpoints...")
    results = []
    
    # Test GET audits
    results.append(test_endpoint("GET", "/api/v1/audits", 200))
    
    # Test GET audit programs
    results.append(test_endpoint("GET", "/api/v1/audits/programs", 200))
    
    return results

def test_equipment_endpoints() -> List[Dict]:
    """Test equipment endpoints"""
    print("🔧 Testing Equipment Endpoints...")
    results = []
    
    # Test GET equipment
    results.append(test_endpoint("GET", "/api/v1/equipment", 200))
    
    # Test GET maintenance plans
    results.append(test_endpoint("GET", "/api/v1/equipment/maintenance-plans", 200))
    
    return results

def test_production_endpoints() -> List[Dict]:
    """Test production endpoints"""
    print("🏭 Testing Production Endpoints...")
    results = []
    
    # Test GET production processes
    results.append(test_endpoint("GET", "/api/v1/production/processes", 200))
    
    # Test GET production templates
    results.append(test_endpoint("GET", "/api/v1/production/templates", 200))
    
    return results

def test_complaints_endpoints() -> List[Dict]:
    """Test complaints endpoints"""
    print("📝 Testing Complaints Endpoints...")
    results = []
    
    # Test GET complaints
    results.append(test_endpoint("GET", "/api/v1/complaints", 200))
    
    return results

def test_dashboard_endpoints() -> List[Dict]:
    """Test dashboard endpoints"""
    print("📊 Testing Dashboard Endpoints...")
    results = []
    
    # Test GET dashboard
    results.append(test_endpoint("GET", "/api/v1/dashboard", 200))
    
    return results

def test_settings_endpoints() -> List[Dict]:
    """Test settings endpoints"""
    print("⚙️ Testing Settings Endpoints...")
    results = []
    
    # Test GET settings
    results.append(test_endpoint("GET", "/api/v1/settings", 200))
    
    return results

def test_notifications_endpoints() -> List[Dict]:
    """Test notifications endpoints"""
    print("🔔 Testing Notifications Endpoints...")
    results = []
    
    # Test GET notifications
    results.append(test_endpoint("GET", "/api/v1/notifications", 200))
    
    return results

def test_traceability_endpoints() -> List[Dict]:
    """Test traceability endpoints"""
    print("🔗 Testing Traceability Endpoints...")
    results = []
    
    # Test GET batches
    results.append(test_endpoint("GET", "/api/v1/traceability/batches", 200))
    
    # Test GET traceability links
    results.append(test_endpoint("GET", "/api/v1/traceability/links", 200))
    
    return results

def test_training_endpoints() -> List[Dict]:
    """Test training endpoints"""
    print("🎓 Testing Training Endpoints...")
    results = []
    
    # Test GET training programs
    results.append(test_endpoint("GET", "/api/v1/training/programs", 200))
    
    # Test GET training sessions
    results.append(test_endpoint("GET", "/api/v1/training/sessions", 200))
    
    return results

def test_management_review_endpoints() -> List[Dict]:
    """Test management review endpoints"""
    print("📋 Testing Management Review Endpoints...")
    results = []
    
    # Test GET management reviews
    results.append(test_endpoint("GET", "/api/v1/management-reviews", 200))
    
    return results

def test_objectives_endpoints() -> List[Dict]:
    """Test objectives endpoints"""
    print("🎯 Testing Objectives Endpoints...")
    results = []
    
    # Test GET objectives
    results.append(test_endpoint("GET", "/api/v1/objectives", 200))
    
    return results

def test_analytics_endpoints() -> List[Dict]:
    """Test analytics endpoints"""
    print("📈 Testing Analytics Endpoints...")
    results = []
    
    # Test GET analytics reports
    results.append(test_endpoint("GET", "/api/v1/analytics/reports", 200))
    
    return results

def test_actions_log_endpoints() -> List[Dict]:
    """Test actions log endpoints"""
    print("📝 Testing Actions Log Endpoints...")
    results = []
    
    # Test GET actions log
    results.append(test_endpoint("GET", "/api/v1/actions-log", 200))
    
    return results

def test_rbac_endpoints() -> List[Dict]:
    """Test RBAC endpoints"""
    print("🔐 Testing RBAC Endpoints...")
    results = []
    
    # Test GET roles
    results.append(test_endpoint("GET", "/api/v1/rbac/roles", 200))
    
    # Test GET permissions
    results.append(test_endpoint("GET", "/api/v1/rbac/permissions", 200))
    
    return results

def test_search_endpoints() -> List[Dict]:
    """Test search endpoints"""
    print("🔍 Testing Search Endpoints...")
    results = []
    
    # Test search
    results.append(test_endpoint("GET", "/api/v1/search", 200))
    
    return results

def test_profile_endpoints() -> List[Dict]:
    """Test profile endpoints"""
    print("👤 Testing Profile Endpoints...")
    results = []
    
    # Test GET profile
    results.append(test_endpoint("GET", "/api/v1/profile", 200))
    
    return results

def test_nonconformance_endpoints() -> List[Dict]:
    """Test nonconformance endpoints"""
    print("❌ Testing Nonconformance Endpoints...")
    results = []
    
    # Test GET nonconformances
    results.append(test_endpoint("GET", "/api/v1/nonconformance", 200))
    
    return results

def test_allergen_label_endpoints() -> List[Dict]:
    """Test allergen label endpoints"""
    print("🏷️ Testing Allergen Label Endpoints...")
    results = []
    
    # Test GET allergen labels
    results.append(test_endpoint("GET", "/api/v1/allergen-label", 200))
    
    return results

def main():
    """Run all endpoint tests"""
    print("🚀 Starting Comprehensive Endpoint Testing...")
    print("=" * 60)
    
    all_results = []
    
    # Test all endpoint categories
    test_functions = [
        test_authentication_endpoints,
        test_supplier_endpoints,
        test_user_endpoints,
        test_document_endpoints,
        test_haccp_endpoints,
        test_prp_endpoints,
        test_risk_endpoints,
        test_audit_endpoints,
        test_equipment_endpoints,
        test_production_endpoints,
        test_complaints_endpoints,
        test_dashboard_endpoints,
        test_settings_endpoints,
        test_notifications_endpoints,
        test_traceability_endpoints,
        test_training_endpoints,
        test_management_review_endpoints,
        test_objectives_endpoints,
        test_analytics_endpoints,
        test_actions_log_endpoints,
        test_rbac_endpoints,
        test_search_endpoints,
        test_profile_endpoints,
        test_nonconformance_endpoints,
        test_allergen_label_endpoints,
    ]
    
    for test_func in test_functions:
        try:
            results = test_func()
            all_results.extend(results)
            time.sleep(0.1)  # Small delay between tests
        except Exception as e:
            print(f"❌ Error in {test_func.__name__}: {e}")
    
    # Analyze results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    successful = [r for r in all_results if r.get("success", False)]
    failed = [r for r in all_results if not r.get("success", False)]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📈 Success Rate: {len(successful)/(len(successful)+len(failed))*100:.1f}%")
    
    if failed:
        print("\n❌ FAILED ENDPOINTS:")
        for result in failed:
            print(f"  {result['method']} {result['endpoint']} - Status: {result['status_code']}")
            if 'error' in result:
                print(f"    Error: {result['error']}")
            elif 'response' in result:
                print(f"    Response: {result['response'][:100]}...")
    
    print("\n✅ WORKING ENDPOINTS:")
    for result in successful:
        print(f"  {result['method']} {result['endpoint']}")
    
    # Save detailed results
    with open("endpoint_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: endpoint_test_results.json")

if __name__ == "__main__":
    main()


