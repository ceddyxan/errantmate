#!/usr/bin/env python3
"""
Test script to verify production management features are working
"""

import requests
import json

def test_production_management():
    """Test if management features work in production"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 Testing Production Management Features")
    print("=" * 50)
    
    # Test 1: Check if shelves API works
    print("\n1. Testing shelves API...")
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            shelves = response.json()
            print(f"   ✅ Shelves API working - Found {len(shelves)} shelves")
            
            # Check if new fields are present
            if shelves and len(shelves) > 0:
                first_shelf = shelves[0]
                new_fields = ['customerEmail', 'cardNumber', 'discount']
                missing_fields = [field for field in new_fields if field not in first_shelf]
                
                if missing_fields:
                    print(f"   ❌ Missing fields in API response: {missing_fields}")
                    print(f"   ❌ Migration may not have run in production")
                else:
                    print(f"   ✅ All new fields present: {new_fields}")
        else:
            print(f"   ❌ Shelves API failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error testing shelves API: {e}")
    
    # Test 2: Check update API (will fail without auth but should not be 500)
    print("\n2. Testing update API endpoint...")
    try:
        test_data = {
            "shelfId": "A-01",
            "customerName": "Test Customer",
            "customerEmail": "test@example.com"
        }
        
        response = requests.post(
            f"{base_url}/api/shelves/update", 
            json=test_data,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ❌ Update API returning 500 error - Migration issue")
            print(f"   Response: {response.text}")
        elif response.status_code == 403:
            print(f"   ✅ Update API working (403 = permission denied, expected)")
        elif response.status_code == 401:
            print(f"   ✅ Update API working (401 = not logged in, expected)")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error testing update API: {e}")
    
    # Test 3: Check end-rental API
    print("\n3. Testing end-rental API endpoint...")
    try:
        test_data = {"shelfId": "A-01"}
        
        response = requests.post(
            f"{base_url}/api/shelves/end-rental", 
            json=test_data,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ❌ End-rental API returning 500 error - Migration issue")
            print(f"   Response: {response.text}")
        elif response.status_code == 403:
            print(f"   ✅ End-rental API working (403 = permission denied, expected)")
        elif response.status_code == 401:
            print(f"   ✅ End-rental API working (401 = not logged in, expected)")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error testing end-rental API: {e}")
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("✅ If all APIs return 401/403 (auth errors) instead of 500, migration worked!")
    print("❌ If APIs return 500 errors, migration failed in production")
    print("🌐 Check Render.com dashboard for deployment status")

if __name__ == "__main__":
    test_production_management()
