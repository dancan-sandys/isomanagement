# -*- coding: utf-8 -*-
"""
Test Script for Actions Log System
Phase 3: Test the actions log functionality
"""

import requests
import json
from datetime import datetime

def test_actions_log_api():
    """Test the actions log API endpoints"""
    
    base_url = "http://127.0.0.1:8000/api/v1/actions-log"
    
    print("🧪 Testing Actions Log API Endpoints...")
    
    try:
        # Test 1: Get analytics
        print("\n1. Testing Analytics...")
        response = requests.get(f"{base_url}/analytics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics retrieved successfully")
            print(f"   - Total actions: {data.get('total_actions', 0)}")
            print(f"   - Pending actions: {data.get('pending_actions', 0)}")
            print(f"   - Completed actions: {data.get('completed_actions', 0)}")
            print(f"   - Completion rate: {data.get('completion_rate', 0)}%")
        else:
            print(f"❌ Analytics failed: {response.status_code} - {response.text}")
        
        # Test 2: Get dashboard data
        print("\n2. Testing Dashboard Data...")
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data retrieved successfully")
            print(f"   - Recent actions: {len(data.get('recent_actions', []))}")
            print(f"   - Critical actions: {len(data.get('critical_actions', []))}")
        else:
            print(f"❌ Dashboard failed: {response.status_code} - {response.text}")
        
        # Test 3: List actions
        print("\n3. Testing List Actions...")
        response = requests.get(f"{base_url}/actions")
        if response.status_code == 200:
            actions = response.json()
            print(f"✅ Actions list retrieved successfully: {len(actions)} actions")
        else:
            print(f"❌ Actions list failed: {response.status_code} - {response.text}")
        
        # Test 4: Create a test action
        print("\n4. Testing Create Action...")
        test_action = {
            "title": "Test Action - Improve Customer Satisfaction",
            "description": "Implement customer feedback system to improve satisfaction scores",
            "action_source": "interested_party",
            "priority": "high",
            "assigned_by": 1,
            "due_date": "2025-02-15T10:00:00"
        }
        
        response = requests.post(f"{base_url}/actions", json=test_action)
        if response.status_code == 200:
            action = response.json()
            print(f"✅ Action created successfully")
            print(f"   - Action ID: {action.get('id')}")
            print(f"   - Title: {action.get('title')}")
            print(f"   - Status: {action.get('status')}")
            
            # Test 5: Get the created action
            print("\n5. Testing Get Action...")
            action_id = action.get('id')
            response = requests.get(f"{base_url}/actions/{action_id}")
            if response.status_code == 200:
                action_data = response.json()
                print(f"✅ Action retrieved successfully")
                print(f"   - Title: {action_data.get('title')}")
                print(f"   - Priority: {action_data.get('priority')}")
            else:
                print(f"❌ Get action failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Create action failed: {response.status_code} - {response.text}")
        
        print("\n🎉 Actions Log API testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_actions_log_api()
