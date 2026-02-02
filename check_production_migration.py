#!/usr/bin/env python3
"""
Simple test to check if production migration worked
"""

import requests
import json

def check_production_migration():
    """Check if migration worked by testing API responses"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 Checking Production Migration Status")
    print("=" * 45)
    
    # Test shelves API
    print("\n1. Testing /api/shelves...")
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ API returns JSON (good!)")
                print(f"   ✅ Found {len(data)} shelves")
                
                # Check for new fields in first shelf
                if data and len(data) > 0:
                    shelf = data[0]
                    new_fields = ['customerEmail', 'cardNumber', 'discount']
                    present_fields = [f for f in new_fields if f in shelf]
                    missing_fields = [f for f in new_fields if f not in shelf]
                    
                    print(f"   ✅ New fields present: {present_fields}")
                    if missing_fields:
                        print(f"   ❌ Missing fields: {missing_fields}")
                    else:
                        print(f"   🎉 All new fields present!")
                
            except json.JSONDecodeError:
                print(f"   ❌ API returns HTML instead of JSON")
                print(f"   ❌ This means migration might not have run")
        else:
            print(f"   ❌ API status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test update API (should return 401/403, not 500)
    print("\n2. Testing /api/shelves/update...")
    try:
        response = requests.post(
            f"{base_url}/api/shelves/update", 
            json={"shelfId": "A-01"},
            timeout=10
        )
        
        if response.status_code == 500:
            print(f"   ❌ 500 error - Migration failed!")
            print(f"   ❌ Response: {response.text[:200]}...")
        elif response.status_code in [401, 403]:
            print(f"   ✅ {response.status_code} - Migration worked!")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test end-rental API
    print("\n3. Testing /api/shelves/end-rental...")
    try:
        response = requests.post(
            f"{base_url}/api/shelves/end-rental", 
            json={"shelfId": "A-01"},
            timeout=10
        )
        
        if response.status_code == 500:
            print(f"   ❌ 500 error - Migration failed!")
        elif response.status_code in [401, 403]:
            print(f"   ✅ {response.status_code} - Migration worked!")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 45)
    print("📊 CONCLUSION:")
    print("✅ If you see 'Migration worked!' above - production is ready!")
    print("❌ If you see 'Migration failed!' - need to check Render.com")
    print("\n🌐 Next: Check your Render.com dashboard deployment status")

if __name__ == "__main__":
    check_production_migration()
