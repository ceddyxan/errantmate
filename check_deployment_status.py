#!/usr/bin/env python3
"""
Check if force restart endpoint is deployed
"""

import requests

def check_deployment_status():
    """Check if the latest deployment is ready"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔍 CHECKING DEPLOYMENT STATUS")
    print("=" * 40)
    
    # Check health
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ App is running")
        else:
            print(f"❌ App not healthy: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Check if force restart endpoint exists
    try:
        response = requests.post(f"{base_url}/force-restart", timeout=10)
        print(f"Force restart endpoint: {response.status_code}")
        
        if response.status_code == 500:
            print("✅ Force restart endpoint is ready!")
            return True
        elif response.status_code == 404:
            print("⏳ Force restart endpoint not ready - deployment in progress")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Force restart check failed: {e}")
        return False

if __name__ == "__main__":
    ready = check_deployment_status()
    
    print("\n" + "=" * 40)
    if ready:
        print("🎉 DEPLOYMENT READY!")
        print("✅ Force restart endpoint available")
        print("🚀 Ready to trigger production restart")
    else:
        print("⏳ DEPLOYMENT IN PROGRESS...")
        print("🔄 Wait 1-2 minutes and try again")
        print("🌐 Check Render.com dashboard for status")
