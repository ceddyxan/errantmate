#!/usr/bin/env python3
"""
Render.com Deployment Trigger Script
This script will help trigger and monitor the deployment process.
"""

import requests
import time
import json
from datetime import datetime

def check_deployment_status():
    """Check the current deployment status"""
    # You would need your Render API key and service ID for this
    # For now, we'll provide instructions for manual checking
    
    print("🚀 Render.com Deployment Instructions")
    print("=" * 50)
    print()
    print("1. Automatic Deployment:")
    print("   - Render.com should automatically detect the GitHub push")
    print("   - Check your Render dashboard for deployment status")
    print("   - Wait for the deployment to complete (usually 2-5 minutes)")
    print()
    print("2. Manual Deployment Check:")
    print("   - Go to: https://dashboard.render.com/")
    print("   - Navigate to your ErrantMate service")
    print("   - Check the 'Deployments' tab")
    print("   - Look for the latest commit: 5b39f0e")
    print()
    print("3. Production URLs to test after deployment:")
    print("   - Main app: https://your-app.onrender.com/")
    print("   - DB check: https://your-app.onrender.com/check-db")
    print("   - Force init: https://your-app.onrender.com/force-init-db?confirm=FORCE_INIT_CONFIRMED")
    print("   - Complete fix: https://your-app.onrender.com/complete-db-fix")
    print()
    print("4. Expected Results:")
    print("   - /check-db should show: {'status': 'ready', 'missing_tables': []}")
    print("   - Main dashboard should load without database errors")
    print("   - Login should work with admin/ErrantMate@24!")
    print()
    print("5. If issues persist:")
    print("   - Use /complete-db-fix for comprehensive fixes")
    print("   - Check Render logs for specific error messages")
    print("   - Verify DATABASE_URL environment variable")

def test_production_endpoints(base_url):
    """Test production endpoints after deployment"""
    endpoints = [
        "/health",
        "/check-db",
        "/check-db-status"
    ]
    
    print(f"🧪 Testing production endpoints at {base_url}")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 Testing: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Failed: {str(e)}")
        
        time.sleep(1)  # Rate limiting

if __name__ == "__main__":
    print("🚀 ErrantMate Production Deployment Helper")
    print("=" * 50)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Show deployment instructions
    check_deployment_status()
    
    # Uncomment below to test endpoints (replace with your actual URL)
    # test_production_endpoints("https://your-app.onrender.com")
