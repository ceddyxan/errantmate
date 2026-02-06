#!/usr/bin/env python3
"""
Shelf Creation Diagnostic Tool
This script will diagnose why shelf creation is failing in production.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://errantmate.onrender.com"

def login_and_get_session():
    """Login to get authenticated session"""
    try:
        session = requests.Session()
        response = session.post(
            f"{PRODUCTION_URL}/login",
            data={"username": "admin", "password": "ErrantMate@24!"},
            timeout=15
        )
        
        if response.status_code == 200 and "dashboard" in response.text.lower():
            return session
        else:
            return None
    except:
        return None

def diagnose_shelf_table(session):
    """Diagnose shelf table structure and issues"""
    print("🔍 Diagnosing Shelf Table Issues")
    print("=" * 50)
    
    if not session:
        print("❌ No authenticated session")
        return
    
    # Test 1: Check database status
    print("\n📊 Test 1: Database Status")
    print("-" * 30)
    
    try:
        response = session.get(f"{PRODUCTION_URL}/check-db", timeout=15)
        if response.status_code == 200:
            db_status = response.json()
            print(f"✅ Database Status: {db_status.get('status')}")
            print(f"📋 Tables: {db_status.get('tables', [])}")
            print(f"👥 Users: {db_status.get('users', 0)}")
            print(f"📦 Deliveries: {db_status.get('deliveries', 0)}")
        else:
            print(f"❌ Database check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database check error: {e}")
    
    # Test 2: Check shelf table structure
    print("\n🗄️  Test 2: Shelf Table Structure")
    print("-" * 30)
    
    try:
        response = session.get(f"{PRODUCTION_URL}/check-db-status", timeout=15)
        if response.status_code == 200:
            table_details = response.json()
            print(f"✅ Table details retrieved")
            
            if 'table_details' in table_details and 'shelf' in table_details['table_details']:
                shelf_info = table_details['table_details']['shelf']
                print(f"📋 Shelf columns: {shelf_info.get('columns', [])}")
                print(f"📊 Column count: {shelf_info.get('column_count', 0)}")
            else:
                print("⚠️  Shelf table details not found")
        else:
            print(f"❌ Table structure check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Table structure check error: {e}")
    
    # Test 3: Try to list shelves
    print("\n📋 Test 3: List Shelves")
    print("-" * 30)
    
    try:
        response = session.get(f"{PRODUCTION_URL}/api/shelves", timeout=15)
        if response.status_code == 200:
            shelves = response.json()
            print(f"✅ Shelf listing successful: {len(shelves)} shelves")
            if shelves:
                print(f"📊 Sample shelf: {shelves[0]}")
        else:
            print(f"❌ Shelf listing failed: {response.status_code}")
            print(f"📄 Error: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Shelf listing error: {e}")
    
    # Test 4: Test database connection
    print("\n🔌 Test 4: Database Connection")
    print("-" * 30)
    
    try:
        response = session.get(f"{PRODUCTION_URL}/test-database", timeout=15)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Database test successful")
            print(f"📊 Result: {result}")
        else:
            print(f"❌ Database test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database test error: {e}")

def test_simple_shelf_creation(session):
    """Test shelf creation with detailed error logging"""
    print("\n🧪 Test 5: Simple Shelf Creation")
    print("-" * 30)
    
    if not session:
        print("❌ No authenticated session")
        return
    
    test_data = {
        "shelfId": "DIAG-01",
        "price": 800
    }
    
    print(f"📤 Sending request: {test_data}")
    
    try:
        response = session.post(
            f"{PRODUCTION_URL}/api/shelves/create",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 500:
            print("🚨 500 Error detected - checking for detailed error info...")
            
            # Try to get more detailed error information
            try:
                error_response = response.json()
                print(f"🚨 Error Details: {error_response}")
            except:
                print("🚨 Could not parse error response as JSON")
        
    except Exception as e:
        print(f"❌ Shelf creation error: {e}")

def check_shelf_model_compatibility():
    """Check if shelf model might have compatibility issues"""
    print("\n🔍 Test 6: Shelf Model Compatibility")
    print("-" * 30)
    
    # Check if we can access the shelf model directly
    try:
        session = login_and_get_session()
        if session:
            # Try to trigger a shelf model test
            response = session.get(f"{PRODUCTION_URL}/restart-app", timeout=15)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Shelf model test: {result}")
            else:
                print(f"❌ Shelf model test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Shelf model compatibility error: {e}")

def main():
    """Main diagnostic function"""
    print("🔧 ErrantMate Shelf Creation Diagnostic Tool")
    print("=" * 60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: {PRODUCTION_URL}")
    print()
    
    # Get authenticated session
    session = login_and_get_session()
    
    if not session:
        print("❌ Cannot authenticate - check admin credentials")
        return
    
    print("✅ Authentication successful")
    print()
    
    # Run diagnostics
    diagnose_shelf_table(session)
    test_simple_shelf_creation(session)
    check_shelf_model_compatibility()
    
    print("\n📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("🔍 Check the output above for specific issues")
    print("💡 Common problems:")
    print("   1. Missing table columns")
    print("   2. Database connection issues")
    print("   3. Permission problems")
    print("   4. Model compatibility issues")
    print()
    print("🎯 Next Steps:")
    print("   1. Check Render.com logs for detailed errors")
    print("   2. Run database migration if needed")
    print("   3. Verify table structure matches model")

if __name__ == "__main__":
    main()
