#!/usr/bin/env python3
"""
Detailed test to see what the production APIs are actually returning
"""

import requests
import json

def detailed_production_test():
    """Detailed test of production APIs"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 DETAILED PRODUCTION API TEST")
    print("=" * 40)
    
    # Test shelves API with detailed response
    print("\n1. Testing /api/shelves (detailed)...")
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Response length: {len(response.text)} characters")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Valid JSON response")
                print(f"   ✅ Data type: {type(data)}")
                print(f"   ✅ Data length: {len(data) if isinstance(data, list) else 'Not a list'}")
                
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    print(f"   ✅ First item keys: {list(first_item.keys())}")
                    
                    # Check for our new fields
                    new_fields = ['customerEmail', 'cardNumber', 'discount']
                    for field in new_fields:
                        if field in first_item:
                            print(f"   ✅ {field}: {first_item[field]}")
                        else:
                            print(f"   ❌ {field}: MISSING")
                
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON - showing first 200 chars:")
                print(f"   {response.text[:200]}...")
                
        else:
            print(f"   ❌ Error response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")
    
    # Test update API with detailed response
    print("\n2. Testing /api/shelves/update (detailed)...")
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
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        try:
            data = response.json()
            print(f"   ✅ JSON response: {data}")
        except:
            print(f"   ❌ Not JSON - first 200 chars:")
            print(f"   {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")
    
    print("\n" + "=" * 40)
    print("📋 ANALYSIS:")
    print("✅ If APIs return proper JSON with new fields - Migration worked!")
    print("❌ If APIs return HTML or missing fields - Migration issue!")
    print("⚠️  If APIs return 200 without auth - Security issue!")

if __name__ == "__main__":
    detailed_production_test()
