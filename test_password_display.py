#!/usr/bin/env python3
"""
Test script to verify password display functionality in User Management
"""

import requests
import json

def test_password_display():
    """Test if passwords are properly returned for admin users"""
    
    base_url = "https://errantmate.onrender.com"
    session = requests.Session()
    
    print("🔐 Testing Password Display Functionality")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'ErrantMate@24!'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Get users data
    print("\n2. Fetching users data...")
    try:
        response = session.get(f"{base_url}/api/users/public")
        print(f"Response status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print(f"✅ Got JSON response")
            print(f"Success: {data.get('success')}")
            
            if data.get('success') and data.get('users'):
                users = data.get('users')
                print(f"\n📊 Found {len(users)} users:")
                
                for user in users:
                    print(f"\n👤 {user.get('username')}")
                    print(f"   Role: {user.get('role')}")
                    print(f"   Can Edit: {user.get('can_edit')}")
                    print(f"   Show Password: {user.get('show_password')}")
                    
                    if user.get('show_password'):
                        password = user.get('password_hash', 'Not available')
                        print(f"   🔑 Password: {password}")
                    else:
                        print(f"   🔒 Password: Hidden (Admin or no permission)")
                        
            else:
                print(f"❌ No users found or error: {data.get('error')}")
        else:
            print(f"❌ Non-JSON response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
    
    # Step 3: Test reports page access
    print("\n3. Testing reports page access...")
    try:
        response = session.get(f"{base_url}/reports")
        if response.status_code == 200:
            print("✅ Reports page accessible")
            if 'User Management' in response.text:
                print("✅ User Management section found")
            else:
                print("❌ User Management section not found")
        else:
            print(f"❌ Reports page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Reports page error: {e}")

if __name__ == "__main__":
    test_password_display()
