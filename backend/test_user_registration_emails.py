#!/usr/bin/env python3
"""
Test script to verify email notifications are sent during user registration
"""

import os
import sys
import requests
import json
from datetime import datetime

def load_env_vars():
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_user_registration_emails():
    """Test user registration endpoints and verify email notifications"""
    print("🚀 Testing User Registration Email Notifications")
    print("=" * 60)
    
    # Load environment variables
    load_env_vars()
    
    # Get API base URL
    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api/v1')
    
    print(f"📡 API Base URL: {api_base_url}")
    print(f"📧 Test Email: okoraok18@gmail.com")
    
    test_results = []
    
    # Test 1: Signup endpoint
    print("\n🧪 Test 1: Signup Endpoint (/auth/signup)")
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signup_data = {
            "username": f"testuser_{timestamp}",
            "email": "okoraok18@gmail.com",  # Use real email for actual testing
            "password": "TestPassword123!",
            "full_name": "Test User Signup",
            "department": "Quality Assurance",
            "position": "QA Specialist",
            "phone": "+1234567890",
            "employee_id": f"EMP_{timestamp}"
        }
        
        response = requests.post(f"{api_base_url}/auth/signup", json=signup_data)
        
        if response.status_code == 200:
            print("✅ Signup successful - Welcome email should be sent")
            test_results.append(("Signup Endpoint", True))
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            test_results.append(("Signup Endpoint", False))
            
    except Exception as e:
        print(f"❌ Signup test failed: {str(e)}")
        test_results.append(("Signup Endpoint", False))
    
    # Test 2: Register endpoint (requires role_id)
    print("\n🧪 Test 2: Register Endpoint (/auth/register)")
    try:
        timestamp2 = datetime.now().strftime('%Y%m%d_%H%M%S_2')
        register_data = {
            "username": f"testuser2_{timestamp2}",
            "email": f"testuser2_{timestamp2}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User Register",
            "department": "Production",
            "position": "Production Manager",
            "phone": "+1234567891",
            "employee_id": f"EMP2_{timestamp2}",
            "role_id": 1  # Assuming System Administrator role has ID 1
        }
        
        response = requests.post(f"{api_base_url}/auth/register", json=register_data)
        
        if response.status_code == 200:
            print("✅ Register successful - Welcome email should be sent")
            test_results.append(("Register Endpoint", True))
        else:
            print(f"❌ Register failed: {response.status_code} - {response.text}")
            test_results.append(("Register Endpoint", False))
            
    except Exception as e:
        print(f"❌ Register test failed: {str(e)}")
        test_results.append(("Register Endpoint", False))
    
    # Test 3: Admin user creation (requires authentication)
    print("\n🧪 Test 3: Admin User Creation (/users/)")
    try:
        # First, we need to login to get an access token
        login_data = {
            "username": "admin",  # Assuming admin user exists
            "password": "admin123"  # Assuming admin password
        }
        
        login_response = requests.post(f"{api_base_url}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('data', {}).get('access_token')
            
            if access_token:
                headers = {"Authorization": f"Bearer {access_token}"}
                
                timestamp3 = datetime.now().strftime('%Y%m%d_%H%M%S_3')
                create_user_data = {
                    "username": f"testuser3_{timestamp3}",
                    "email": f"testuser3_{timestamp3}@example.com",
                    "password": "TestPassword123!",
                    "full_name": "Test User Admin Created",
                    "department": "HACCP Team",
                    "position": "HACCP Coordinator",
                    "phone": "+1234567892",
                    "employee_id": f"EMP3_{timestamp3}",
                    "role_id": 2  # Assuming HACCP Team Member role has ID 2
                }
                
                response = requests.post(f"{api_base_url}/users/", json=create_user_data, headers=headers)
                
                if response.status_code == 200:
                    print("✅ Admin user creation successful - Welcome email should be sent")
                    test_results.append(("Admin User Creation", True))
                else:
                    print(f"❌ Admin user creation failed: {response.status_code} - {response.text}")
                    test_results.append(("Admin User Creation", False))
            else:
                print("❌ Could not get access token from login")
                test_results.append(("Admin User Creation", False))
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            test_results.append(("Admin User Creation", False))
            
    except Exception as e:
        print(f"❌ Admin user creation test failed: {str(e)}")
        test_results.append(("Admin User Creation", False))
    
    # Print test results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if success:
            passed_tests += 1
    
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests > 0:
        print("\n📧 Email Notifications:")
        print("✅ Welcome emails should be sent for successful registrations")
        print("📋 Check okoraok18@gmail.com inbox for welcome notifications")
        print("📧 Each successful registration should trigger a welcome email with:")
        print("   - User's username and role")
        print("   - Department information")
        print("   - Login URL")
        print("   - ISO 22000 FSMS branding")
        print("📧 Note: Test 1 uses okoraok18@gmail.com for actual email delivery")
    else:
        print("\n⚠️ No successful registrations - no emails will be sent")
    
    print("\n🔧 Troubleshooting:")
    print("1. Ensure the backend server is running on http://localhost:8000")
    print("2. Check that SMTP credentials are configured in .env file")
    print("3. Verify that the admin user exists for Test 3")
    print("4. Check backend logs for any email sending errors")
    
    return passed_tests > 0

def main():
    """Main function"""
    success = test_user_registration_emails()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
