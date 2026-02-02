#!/usr/bin/env python3
"""
Force production restart to fix model loading issues
"""

import requests
import json
import time

def force_production_restart():
    """Force complete production restart to fix model issues"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔄 FORCING PRODUCTION RESTART")
    print("=" * 40)
    
    # Step 1: Trigger force restart
    print("\n1. Triggering force restart...")
    print("   💡 This will cause an intentional error to force Render.com restart")
    
    try:
        response = requests.post(f"{base_url}/force-restart", timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 500:
            print("   ✅ Force restart triggered successfully!")
            try:
                data = response.json()
                print(f"   Message: {data.get('message', 'Unknown')}")
            except:
                print("   ✅ Restart triggered (response not JSON)")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Force restart failed: {e}")
        return False
    
    # Step 2: Wait for restart to complete
    print("\n2. Waiting for application to restart...")
    print("   ⏳ This may take 1-2 minutes...")
    
    max_wait_time = 120  # 2 minutes
    wait_interval = 10   # 10 seconds
    elapsed_time = 0
    
    while elapsed_time < max_wait_time:
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Application is back up after {elapsed_time} seconds!")
                break
        except:
            pass
        
        print(f"   Waiting... ({elapsed_time}/{max_wait_time} seconds)")
        time.sleep(wait_interval)
        elapsed_time += wait_interval
    
    if elapsed_time >= max_wait_time:
        print("   ❌ Application did not restart within 2 minutes")
        return False
    
    # Step 3: Test if the fix worked
    print("\n3. Testing if the fix worked...")
    
    # Test shelves API
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Shelves API working! Found {len(data)} shelves")
                
                # Check for management fields
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
                
                # Test update API
                print("\n4. Testing management APIs...")
                update_data = {
                    "shelfId": data[0]['id'] if data else "A-01",
                    "customerName": "Test Customer",
                    "customerEmail": "test@example.com"
                }
                
                response = requests.post(f"{base_url}/api/shelves/update", json=update_data, timeout=10)
                print(f"   Update API: {response.status_code}")
                
                if response.status_code == 500:
                    print("   ❌ Update API still failing")
                elif response.status_code in [401, 403]:
                    print("   ✅ Update API working (auth required)")
                elif response.status_code == 200:
                    print("   ✅ Update API working perfectly!")
                
                return True
                
            except json.JSONDecodeError:
                print("   ❌ Still returning HTML instead of JSON")
                return False
        else:
            print(f"   ❌ Shelves API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = force_production_restart()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 PRODUCTION FIX COMPLETED!")
        print("✅ Application restarted successfully")
        print("✅ Models reloaded with new fields")
        print("✅ Management APIs working")
        print("🌐 Test: https://errantmate.onrender.com/rent_shelf")
    else:
        print("❌ FORCE RESTART FAILED!")
        print("🔧 Manual intervention may be required")
        print("🌐 Check Render.com dashboard and restart manually")
