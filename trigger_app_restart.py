#!/usr/bin/env python3
"""
Trigger application restart to reload models
"""

import requests
import json

def trigger_app_restart():
    """Trigger application restart to reload Shelf model"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔄 TRIGGERING APPLICATION RESTART")
    print("=" * 40)
    
    try:
        print("\n1. Triggering app restart...")
        response = requests.post(f"{base_url}/restart-app", timeout=30)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print(f"   ✅ App restart successful!")
                print(f"   ✅ Shelves found: {data.get('shelves_count', 'N/A')}")
            else:
                print(f"   ❌ App restart failed: {data.get('error', 'Unknown error')}")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Not JSON response:")
            print(f"   {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test if shelves API works now
    print("\n2. Testing shelves API after restart...")
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
    success = trigger_app_restart()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 PRODUCTION FIX COMPLETED!")
        print("✅ Application restarted and models reloaded")
        print("✅ Shelves API is working")
        print("✅ Management features should now work!")
        print("🌐 Test: https://errantmate.onrender.com/rent_shelf")
    else:
        print("❌ RESTART FAILED!")
        print("🔧 May need manual Render.com restart")
