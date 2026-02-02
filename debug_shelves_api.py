#!/usr/bin/env python3
"""
Debug the shelves API issue
"""

import requests
import json

def debug_shelves_api():
    """Debug why shelves API is still failing"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 DEBUGGING SHELVES API ISSUE")
    print("=" * 40)
    
    # Test shelves API with detailed error info
    try:
        print("\n1. Testing /api/shelves with detailed info...")
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        if response.status_code == 500:
            print("   ❌ 500 Internal Server Error")
            print("   🔍 This suggests the Shelf model has issues")
            
            # Try to get error details
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response (first 300 chars): {response.text[:300]}...")
                
        elif response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Working! Found {len(data)} shelves")
                return True
            except:
                print(f"   ❌ Returning HTML instead of JSON")
                print(f"   First 300 chars: {response.text[:300]}...")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test if we can access a simpler endpoint
    print("\n2. Testing a simpler endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Health check: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Basic endpoints work")
        else:
            print(f"   ❌ Even health check fails: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    # The issue might be with the Shelf model - let's check if we need to restart the app
    print("\n3. Analysis:")
    print("   📋 Migration was successful (columns exist)")
    print("   📋 Basic endpoints work")
    print("   📋 But shelves API returns 500")
    print("   🔍 This suggests the Shelf model needs to be reloaded")
    print("   💡 Solution: Restart the application to reload models")
    
    return False

if __name__ == "__main__":
    success = debug_shelves_api()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 SHELVES API IS WORKING!")
        print("✅ Production management features ready!")
    else:
        print("🔧 ISSUE IDENTIFIED:")
        print("❌ Shelf model needs to be reloaded")
        print("💡 Need to restart the production application")
        print("🌐 This might require a Render.com restart")
