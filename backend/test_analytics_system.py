# -*- coding: utf-8 -*-
"""
Test Script for Analytics System
Phase 4: Test the analytics functionality
"""

import requests
import json
from datetime import datetime

def test_analytics_api():
    """Test the analytics API endpoints"""
    
    base_url = "http://127.0.0.1:8000/api/v1/analytics"
    
    print("🧪 Testing Analytics API Endpoints...")
    
    try:
        # Test 1: Get analytics summary
        print("\n1. Testing Analytics Summary...")
        response = requests.get(f"{base_url}/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics summary retrieved successfully")
            print(f"   - Total reports: {data.get('total_reports', 0)}")
            print(f"   - Total KPIs: {data.get('total_kpis', 0)}")
            print(f"   - Total dashboards: {data.get('total_dashboards', 0)}")
            print(f"   - Active trend analyses: {data.get('active_trend_analyses', 0)}")
        else:
            print(f"❌ Analytics summary failed: {response.status_code} - {response.text}")
        
        # Test 2: Get system health
        print("\n2. Testing System Health...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System health retrieved successfully")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Uptime: {data.get('uptime')}")
            print(f"   - Version: {data.get('version')}")
        else:
            print(f"❌ System health failed: {response.status_code} - {response.text}")
        
        # Test 3: Create a test KPI
        print("\n3. Testing Create KPI...")
        test_kpi = {
            "name": "customer_satisfaction_score",
            "display_name": "Customer Satisfaction Score",
            "description": "Overall customer satisfaction rating",
            "category": "customer",
            "module": "quality",
            "calculation_method": "average",
            "unit": "%",
            "target_value": 85.0,
            "warning_threshold": 80.0,
            "critical_threshold": 75.0,
            "created_by": 1
        }
        
        response = requests.post(f"{base_url}/kpis", json=test_kpi)
        if response.status_code == 200:
            kpi = response.json()
            print(f"✅ KPI created successfully")
            print(f"   - KPI ID: {kpi.get('id')}")
            print(f"   - Name: {kpi.get('display_name')}")
            print(f"   - Category: {kpi.get('category')}")
            
            kpi_id = kpi.get('id')
            
            # Test 4: Calculate KPI value
            print("\n4. Testing KPI Calculation...")
            response = requests.post(f"{base_url}/kpis/{kpi_id}/calculate")
            if response.status_code == 200:
                calc_data = response.json()
                print(f"✅ KPI calculation successful")
                print(f"   - Value: {calc_data.get('value')}")
                print(f"   - Calculated at: {calc_data.get('calculated_at')}")
            else:
                print(f"❌ KPI calculation failed: {response.status_code} - {response.text}")
            
            # Test 5: Get KPI trend
            print("\n5. Testing KPI Trend...")
            response = requests.get(f"{base_url}/kpis/{kpi_id}/trend")
            if response.status_code == 200:
                trend_data = response.json()
                print(f"✅ KPI trend retrieved successfully")
                print(f"   - Trend: {trend_data.get('trend')}")
                print(f"   - Percentage change: {trend_data.get('percentage_change')}%")
            else:
                print(f"❌ KPI trend failed: {response.status_code} - {response.text}")
            
            # Test 6: Get KPI analytics
            print("\n6. Testing KPI Analytics...")
            response = requests.get(f"{base_url}/kpis/{kpi_id}/analytics")
            if response.status_code == 200:
                analytics_data = response.json()
                print(f"✅ KPI analytics retrieved successfully")
                print(f"   - Current value: {analytics_data.get('current_value')}")
                print(f"   - Performance status: {analytics_data.get('performance_status')}")
                print(f"   - Trend percentage: {analytics_data.get('trend_percentage')}%")
            else:
                print(f"❌ KPI analytics failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Create KPI failed: {response.status_code} - {response.text}")
        
        # Test 7: List KPIs
        print("\n7. Testing List KPIs...")
        response = requests.get(f"{base_url}/kpis")
        if response.status_code == 200:
            kpis = response.json()
            print(f"✅ KPIs list retrieved successfully: {len(kpis)} KPIs")
        else:
            print(f"❌ KPIs list failed: {response.status_code} - {response.text}")
        
        # Test 8: Create a test dashboard
        print("\n8. Testing Create Dashboard...")
        test_dashboard = {
            "name": "Quality Management Dashboard",
            "description": "Dashboard for quality metrics and KPIs",
            "layout_config": {"columns": 12, "rows": 6},
            "theme": "light",
            "refresh_interval": 300,
            "is_public": True,
            "created_by": 1
        }
        
        response = requests.post(f"{base_url}/dashboards", json=test_dashboard)
        if response.status_code == 200:
            dashboard = response.json()
            print(f"✅ Dashboard created successfully")
            print(f"   - Dashboard ID: {dashboard.get('id')}")
            print(f"   - Name: {dashboard.get('name')}")
            print(f"   - Theme: {dashboard.get('theme')}")
            
            dashboard_id = dashboard.get('id')
            
            # Test 9: Create a widget
            print("\n9. Testing Create Widget...")
            test_widget = {
                "dashboard_id": dashboard_id,
                "widget_type": "kpi_card",
                "title": "Customer Satisfaction",
                "description": "Current customer satisfaction score",
                "position_x": 0,
                "position_y": 0,
                "width": 4,
                "height": 2,
                "data_source": "kpi",
                "data_config": {"kpi_id": kpi_id if 'kpi_id' in locals() else 1}
            }
            
            response = requests.post(f"{base_url}/widgets", json=test_widget)
            if response.status_code == 200:
                widget = response.json()
                print(f"✅ Widget created successfully")
                print(f"   - Widget ID: {widget.get('id')}")
                print(f"   - Type: {widget.get('widget_type')}")
                print(f"   - Position: ({widget.get('position_x')}, {widget.get('position_y')})")
            else:
                print(f"❌ Widget creation failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Dashboard creation failed: {response.status_code} - {response.text}")
        
        # Test 10: List dashboards
        print("\n10. Testing List Dashboards...")
        response = requests.get(f"{base_url}/dashboards")
        if response.status_code == 200:
            dashboards = response.json()
            print(f"✅ Dashboards list retrieved successfully: {len(dashboards)} dashboards")
        else:
            print(f"❌ Dashboards list failed: {response.status_code} - {response.text}")
        
        print("\n🎉 Analytics API testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_analytics_api()
