#!/usr/bin/env python3
"""
Check what the APIs are actually returning
"""

import requests
import json

def check_api_responses():
    """Check what the management APIs are actually returning"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 CHECKING API RESPONSES")
    print("=" * 35)
    
    # Test update API
    print("\n1. Testing /api/shelves/update...")
    try:
        test_data = {
            "shelfId": "A-01",
            "customerName": "Test Customer",
            "customerEmail": "test@example.com"
        }
        
        response = requests.post(f"{base_url}/api/shelves/update", json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("   ✅ Update API working!")
            else:
                print(f"   ❌ Update API error: {data.get('error', 'Unknown')}")
                
        except json.JSONDecodeError:
            print(f"   ❌ Not JSON - first 300 chars:")
            print(f"   {response.text[:300]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test end-rental API
    print("\n2. Testing /api/shelves/end-rental...")
    try:
        response = requests.post(f"{base_url}/api/shelves/end-rental", json={"shelfId": "A-01"}, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("   ✅ End-rental API working!")
            else:
                print(f"   ❌ End-rental API error: {data.get('error', 'Unknown')}")
                
        except json.JSONDecodeError:
            print(f"   ❌ Not JSON - first 300 chars:")
            print(f"   {response.text[:300]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test shelves API
    print("\n3. Testing /api/shelves...")
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        try:
            data = response.json()
            print(f"   ✅ Shelves API working! Found {len(data)} shelves")
            
            if data and len(data) > 0:
                first_shelf = data[0]
                new_fields = ['customerEmail', 'cardNumber', 'discount']
                present_fields = [f for f in new_fields if f in first_shelf]
                missing_fields = [f for f in new_fields if f not in first_shelf]
                
                print(f"   ✅ New fields present: {present_fields}")
                if missing_fields:
                    print(f"   ❌ Still missing: {missing_fields}")
                else:
                    print(f"   🎉 All management fields available!")
                
        except json.JSONDecodeError:
            print(f"   ❌ Not JSON - first 300 chars:")
            print(f"   {response.text[:300]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 35)
    print("📊 CONCLUSION:")
    print("✅ If all APIs return proper JSON: Production is fixed!")
    print("❌ If APIs return HTML: Still need authentication")
    print("🎉 If management fields are present: Ready for testing!")

if __name__ == "__main__":
    check_api_responses()
