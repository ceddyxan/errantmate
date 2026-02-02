#!/usr/bin/env python3
"""
Trigger emergency migration on production
"""

import requests
import json

def trigger_emergency_migration():
    """Trigger the emergency migration on production"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🚨 TRIGGERING EMERGENCY PRODUCTION MIGRATION")
    print("=" * 55)
    
    try:
        print("\n1. Triggering emergency migration...")
        response = requests.post(f"{base_url}/emergency-migrate", timeout=30)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print(f"   ✅ Migration successful!")
                print(f"   ✅ Added columns: {data.get('added_columns', [])}")
                print(f"   ✅ Total columns: {data.get('total_columns', 'N/A')}")
            else:
                print(f"   ❌ Migration failed: {data.get('error', 'Unknown error')}")
                
        except json.JSONDecodeError:
            print(f"   ❌ Not JSON response:")
            print(f"   {response.text[:500]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test if shelves API works now
    print("\n2. Testing shelves API after migration...")
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        
        if response.status_code == 200:
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
                
                return True
                
            except json.JSONDecodeError:
                print(f"   ❌ Still returning HTML instead of JSON")
                return False
        else:
            print(f"   ❌ API still failing: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = trigger_emergency_migration()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 PRODUCTION MIGRATION COMPLETED SUCCESSFULLY!")
        print("✅ Management features should now work in production!")
        print("🌐 Test: https://errantmate.onrender.com/rent_shelf")
    else:
        print("❌ MIGRATION FAILED!")
        print("🔧 Check Render.com logs for more details")
        print("🌐 May need to check deployment status")
