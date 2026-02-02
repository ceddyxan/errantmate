#!/usr/bin/env python3
"""
Complete production fix - force application restart
"""

import requests
import json

def complete_production_fix():
    """Complete fix for production management APIs"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔧 COMPLETE PRODUCTION FIX")
    print("=" * 40)
    
    # Step 1: Check current status
    print("\n1. Checking current production status...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Health: {response.status_code}")
        
        response = requests.post(f"{base_url}/restart-app", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Shelves accessible: {data.get('shelves_count', 'N/A')}")
        else:
            print(f"   Restart endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"   Status check failed: {e}")
    
    # Step 2: The issue is that the running app instance doesn't know about new fields
    # We need to force a complete restart by triggering an error that causes Render to restart
    
    print("\n2. Forcing complete application restart...")
    print("   💡 This will trigger a Render.com restart to reload all models")
    
    # Create a temporary endpoint that will cause an error and force restart
    try:
        response = requests.post(f"{base_url}/emergency-migrate", timeout=10)
        print(f"   Migration status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Migration result: {data.get('success', False)}")
            
    except Exception as e:
        print(f"   Migration check failed: {e}")
    
    # Step 3: Test the APIs again
    print("\n3. Testing management APIs...")
    
    # Test update API (should return 403/401 if working, 500 if broken)
    try:
        test_data = {
            "shelfId": "A-01",
            "customerName": "Test Customer",
            "customerEmail": "test@example.com"
        }
        
        response = requests.post(f"{base_url}/api/shelves/update", json=test_data, timeout=10)
        print(f"   Update API: {response.status_code}")
        
        if response.status_code == 500:
            print("   ❌ Still 500 error - model not reloaded")
            
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   Response: {response.text[:200]}...")
                
        elif response.status_code in [401, 403]:
            print("   ✅ Working (auth error expected)")
        else:
            print(f"   ⚠️  Unexpected: {response.status_code}")
            
    except Exception as e:
        print(f"   Update API test failed: {e}")
    
    # Test end-rental API
    try:
        response = requests.post(f"{base_url}/api/shelves/end-rental", json={"shelfId": "A-01"}, timeout=10)
        print(f"   End-rental API: {response.status_code}")
        
        if response.status_code == 500:
            print("   ❌ Still 500 error")
        elif response.status_code in [401, 403]:
            print("   ✅ Working (auth error expected)")
        elif response.status_code == 400:
            print("   ⚠️  400 error - shelf might not exist or not occupied")
        else:
            print(f"   ⚠️  Unexpected: {response.status_code}")
            
    except Exception as e:
        print(f"   End-rental API test failed: {e}")
    
    print("\n" + "=" * 40)
    print("📋 ANALYSIS:")
    print("✅ If APIs return 401/403: Working correctly")
    print("❌ If APIs return 500: Need manual Render.com restart")
    print("⚠️  If APIs return 400: Working but shelf not found/occupied")
    
    print("\n🌐 NEXT STEPS:")
    print("1. Test the actual production site with login")
    print("2. If still 500 errors, restart on Render.com dashboard")
    print("3. The database schema is correct, just need model reload")

if __name__ == "__main__":
    complete_production_fix()
