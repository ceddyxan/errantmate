#!/usr/bin/env python3
"""
Production Deployment Status Checker
This script will check if the production deployment is working correctly.
"""

import requests
import json
import time
from datetime import datetime

# You'll need to replace this with your actual production URL
PRODUCTION_URL = "https://errantmate.onrender.com"  # Replace with your actual URL

def check_production_status():
    """Check production deployment status"""
    print("🚀 Production Deployment Status Check")
    print("=" * 60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing URL: {PRODUCTION_URL}")
    print()
    
    # Test endpoints
    endpoints = [
        ("/", "Main Dashboard"),
        ("/health", "Health Check"),
        ("/check-db", "Database Status"),
        ("/check-db-status", "Detailed DB Status"),
        ("/init-db", "Database Initialization"),
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        url = f"{PRODUCTION_URL}{endpoint}"
        print(f"📡 Testing: {description}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            status_code = response.status_code
            results[endpoint] = {
                'status_code': status_code,
                'success': 200 <= status_code < 300,
                'response': response.text[:500] if response.text else "No content"
            }
            
            if status_code == 200:
                print(f"   ✅ Status: {status_code}")
                try:
                    data = response.json()
                    print(f"   📊 Response: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   📄 Content: {response.text[:200]}...")
            else:
                print(f"   ❌ Status: {status_code}")
                print(f"   📄 Error: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Request took too long")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': 'Timeout'}
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error: Could not connect")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': 'Connection Error'}
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': str(e)}
        
        print()
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("📋 SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"✅ Successful endpoints: {successful}/{total}")
    print()
    
    for endpoint, result in results.items():
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {endpoint}: {result['status_code']}")
    
    # Database status analysis
    if '/check-db' in results and results['/check-db']['success']:
        print("\n🗄️  DATABASE ANALYSIS")
        print("-" * 40)
        try:
            db_response = requests.get(f"{PRODUCTION_URL}/check-db", timeout=10).json()
            
            if db_response.get('status') == 'ready':
                print("✅ Database is ready!")
                print(f"📋 Tables: {db_response.get('tables', [])}")
                print(f"👥 Users: {db_response.get('users', 0)}")
                print(f"📦 Deliveries: {db_response.get('deliveries', 0)}")
            elif db_response.get('status') == 'incomplete':
                print("⚠️  Database incomplete!")
                print(f"❌ Missing tables: {db_response.get('missing_tables', [])}")
                print("💡 Run: /force-init-db?confirm=FORCE_INIT_CONFIRMED")
            else:
                print("❌ Database error!")
                print(f"🚨 Error: {db_response.get('error', 'Unknown error')}")
                
        except:
            print("❌ Could not parse database response")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if successful == total:
        print("✅ All endpoints working! Production deployment successful.")
        print("🎯 Your database fixes are live and working.")
    elif successful > 0:
        print("⚠️  Some endpoints working. Partial deployment.")
        print("🔄 Wait a few more minutes for full deployment.")
    else:
        print("❌ No endpoints working. Deployment failed.")
        print("🔧 Check Render dashboard for deployment errors.")
    
    # Next steps
    print("\n🎯 NEXT STEPS")
    print("-" * 40)
    
    if '/check-db' in results and not results['/check-db']['success']:
        print("1. 🗄️  Fix database:")
        print(f"   {PRODUCTION_URL}/force-init-db?confirm=FORCE_INIT_CONFIRMED")
        print("   OR")
        print(f"   {PRODUCTION_URL}/complete-db-fix")
    
    if successful < total:
        print("2. 📊 Check Render dashboard:")
        print("   https://dashboard.render.com/")
        print("   Look for deployment errors or logs")
    
    print("3. 🧪 Test application functionality:")
    print(f"   {PRODUCTION_URL}/")
    print("   Try logging in with admin credentials")

def get_render_deployment_info():
    """Get information about how to check Render deployment"""
    print("\n📱 RENDER DEPLOYMENT CHECK")
    print("=" * 60)
    print("1. 🌐 Open Render Dashboard:")
    print("   https://dashboard.render.com/")
    print()
    print("2. 🔍 Find your ErrantMate service")
    print("   Look for your web service")
    print()
    print("3. 📋 Check Deployments tab:")
    print("   Look for commit: 5b39f0e")
    print("   Status should be 'Live'")
    print()
    print("4. 📊 View Logs if needed:")
    print("   Click on your service > Logs")
    print("   Look for any error messages")
    print()
    print("5. ⚡ Manual deploy if needed:")
    print("   Click 'Manual Deploy' > 'Deploy Latest Commit'")

if __name__ == "__main__":
    print("🔍 ErrantMate Production Deployment Checker")
    print("=" * 60)
    
    # Check if user needs to update URL
    print("⚠️  IMPORTANT: Make sure to update PRODUCTION_URL in this script")
    print("   Current URL:", PRODUCTION_URL)
    print("   Replace with your actual Render.com URL")
    print()
    
    input("Press Enter to continue with current URL...")
    
    check_production_status()
    get_render_deployment_info()
