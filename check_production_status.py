#!/usr/bin/env python3
"""
Quick production status check
"""

import requests

def check_production_status():
    """Check if production deployment is ready"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 PRODUCTION DEPLOYMENT STATUS")
    print("=" * 40)
    
    # Check health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ App is running and healthy")
            
            # Check emergency endpoint
            try:
                response = requests.post(f"{base_url}/emergency-migrate", timeout=10, json={})
                print(f"Emergency endpoint: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Emergency endpoint is ready!")
                    return True
                elif response.status_code == 404:
                    print("⏳ Emergency endpoint not ready yet - deployment in progress")
                else:
                    print(f"⚠️  Emergency endpoint status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Emergency endpoint error: {e}")
                
        else:
            print(f"❌ App not healthy: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cannot reach app: {e}")
    
    return False

if __name__ == "__main__":
    ready = check_production_status()
    
    print("\n" + "=" * 40)
    if ready:
        print("🎉 PRODUCTION IS READY!")
        print("✅ Emergency migration can be triggered")
        print("🚀 Ready to fix the database!")
    else:
        print("⏳ DEPLOYMENT IN PROGRESS...")
        print("🔄 Wait 2-3 minutes and try again")
        print("🌐 Check Render.com dashboard for status")
