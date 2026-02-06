#!/usr/bin/env python3
"""
Shelf Creation Test Suite with Authentication
This script will test the Create New Shelf functionality with proper authentication.
"""

import requests
import json
import time
from datetime import datetime

# Production URL
PRODUCTION_URL = "https://errantmate.onrender.com"

def login_and_get_session():
    """Login to get authenticated session"""
    print("🔐 Logging in to get session...")
    
    login_data = {
        "username": "admin",
        "password": "ErrantMate@24!"
    }
    
    try:
        session = requests.Session()
        response = session.post(
            f"{PRODUCTION_URL}/login",
            data=login_data,
            timeout=15
        )
        
        if response.status_code == 200:
            # Check if login was successful by looking for redirect or success indicator
            if "dashboard" in response.text.lower() or "errantmate" in response.text.lower():
                print("✅ Login successful")
                return session
            else:
                print("❌ Login failed - check credentials")
                return None
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_shelf_creation_with_auth(session):
    """Test shelf creation with authenticated session"""
    print("\n🧪 Testing Shelf Creation with Authentication")
    print("-" * 50)
    
    if not session:
        print("❌ No authenticated session available")
        return {}
    
    # Test data - use unique IDs for each test
    test_shelves = [
        {"shelfId": "TEST-01", "price": 800},
        {"shelfId": "TEST-02", "price": 1200},
        {"shelfId": "TEST-03", "price": 1500},
        {"shelfId": "TEST-04", "price": 1000}
    ]
    
    # Endpoints to test
    creation_endpoints = [
        ("/api/shelves/create", "Standard Create"),
        ("/api/shelves/create-orm", "ORM Create"),
        ("/api/shelves/create-simple", "Simple Create"),
        ("/api/shelves/create-ultra", "Ultra Create")
    ]
    
    results = {}
    
    for i, (endpoint, description) in enumerate(creation_endpoints):
        print(f"\n📡 Testing: {description}")
        print(f"   Endpoint: {endpoint}")
        
        if i < len(test_shelves):
            test_shelf = test_shelves[i]
        else:
            test_shelf = {"shelfId": f"TEST-{i+1:02d}", "price": 1000}
        
        try:
            response = session.post(
                f"{PRODUCTION_URL}{endpoint}",
                json=test_shelf,
                timeout=15,
                headers={"Content-Type": "application/json"}
            )
            
            results[endpoint] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.text[:500] if response.text else "No content"
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   📊 Success: {data.get('success', False)}")
                    print(f"   📄 Message: {data.get('message', 'No message')}")
                except:
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   📄 Response: {response.text[:200]}...")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📄 Error: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Request took too long")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': 'Timeout'}
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': str(e)}
        
        time.sleep(1)  # Rate limiting
    
    return results

def test_shelf_listing_with_auth(session):
    """Test shelf listing with authentication"""
    print("\n📋 Testing Shelf Listing with Authentication")
    print("-" * 50)
    
    if not session:
        print("❌ No authenticated session available")
        return []
    
    try:
        response = session.get(f"{PRODUCTION_URL}/api/shelves", timeout=15)
        
        if response.status_code == 200:
            shelves = response.json()
            print(f"✅ Shelf listing successful")
            print(f"📊 Total shelves: {len(shelves)}")
            
            # Group by status
            status_counts = {}
            for shelf in shelves:
                status = shelf.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("📈 Shelf Status Breakdown:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
            
            # Show test shelves we created
            test_shelves = [s for s in shelves if s.get('id', '').startswith('TEST-')]
            if test_shelves:
                print(f"\n🧪 Test shelves created: {len(test_shelves)}")
                for shelf in test_shelves:
                    print(f"   {shelf.get('id')}: {shelf.get('status')} - KSh {shelf.get('price')}")
            
            return shelves
        else:
            print(f"❌ Shelf listing failed: {response.status_code}")
            print(f"📄 Error: {response.text[:200]}...")
            return []
            
    except Exception as e:
        print(f"❌ Error testing shelf listing: {e}")
        return []

def test_shelf_page_access_with_auth(session):
    """Test shelf page access with authentication"""
    print("\n🌐 Testing Page Access with Authentication")
    print("-" * 50)
    
    if not session:
        print("❌ No authenticated session available")
        return
    
    pages = [
        ("/rent_shelf", "Rent Shelf Page"),
        ("/", "Main Dashboard")
    ]
    
    for page, description in pages:
        try:
            response = session.get(f"{PRODUCTION_URL}{page}", timeout=15)
            
            if response.status_code == 200:
                print(f"✅ {description}: Accessible")
                # Check if shelf-related content is present
                if 'shelf' in response.text.lower():
                    print(f"   📄 Contains shelf content")
                else:
                    print(f"   ⚠️  No shelf content detected")
            else:
                print(f"❌ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error accessing {description}: {e}")

def test_manual_shelf_creation_flow():
    """Test the manual shelf creation flow as a user would experience it"""
    print("\n🧪 Testing Manual Shelf Creation Flow")
    print("-" * 50)
    
    try:
        session = requests.Session()
        
        # Step 1: Login
        print("🔐 Step 1: Logging in...")
        login_response = session.post(
            f"{PRODUCTION_URL}/login",
            data={"username": "admin", "password": "ErrantMate@24!"},
            timeout=15
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
        
        # Step 2: Access rent shelf page
        print("📄 Step 2: Accessing rent shelf page...")
        page_response = session.get(f"{PRODUCTION_URL}/rent_shelf", timeout=15)
        
        if page_response.status_code == 200:
            print("✅ Rent shelf page accessible")
            
            # Check for create shelf functionality
            if 'create' in page_response.text.lower() and 'shelf' in page_response.text.lower():
                print("✅ Create shelf functionality found in page")
            else:
                print("⚠️  Create shelf functionality not clearly visible")
        else:
            print(f"❌ Rent shelf page not accessible: {page_response.status_code}")
        
        # Step 3: Test shelf creation API
        print("🔧 Step 3: Testing shelf creation API...")
        test_shelf = {"shelfId": "MANUAL-TEST", "price": 1000}
        
        create_response = session.post(
            f"{PRODUCTION_URL}/api/shelves/create",
            json=test_shelf,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if create_response.status_code == 200:
            try:
                result = create_response.json()
                if result.get('success'):
                    print("✅ Manual shelf creation successful")
                    print(f"   Shelf ID: {test_shelf['shelfId']}")
                    print(f"   Price: KSh {test_shelf['price']}")
                else:
                    print(f"❌ Shelf creation failed: {result.get('error', 'Unknown error')}")
            except:
                print("⚠️  Could not parse response")
        else:
            print(f"❌ Shelf creation API failed: {create_response.status_code}")
        
        # Step 4: Verify shelf was created
        print("🔍 Step 4: Verifying shelf was created...")
        shelves_response = session.get(f"{PRODUCTION_URL}/api/shelves", timeout=15)
        
        if shelves_response.status_code == 200:
            shelves = shelves_response.json()
            created_shelf = next((s for s in shelves if s.get('id') == test_shelf['shelfId']), None)
            
            if created_shelf:
                print(f"✅ Shelf found in system: {created_shelf['id']}")
                print(f"   Status: {created_shelf['status']}")
                print(f"   Price: KSh {created_shelf['price']}")
            else:
                print("❌ Created shelf not found in system")
        
    except Exception as e:
        print(f"❌ Error in manual flow test: {e}")

def main():
    """Main test function"""
    print("🧪 ErrantMate Shelf Creation Test Suite (Authenticated)")
    print("=" * 60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing URL: {PRODUCTION_URL}")
    print()
    
    # Get authenticated session
    session = login_and_get_session()
    
    if not session:
        print("❌ Cannot proceed without authentication")
        print("💡 Please check admin credentials and try again")
        return
    
    # Run tests
    creation_results = test_shelf_creation_with_auth(session)
    shelves = test_shelf_listing_with_auth(session)
    test_shelf_page_access_with_auth(session)
    test_manual_shelf_creation_flow()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    
    if creation_results:
        successful_creations = sum(1 for r in creation_results.values() if r['success'])
        total_creation_tests = len(creation_results)
        
        print(f"🔧 Creation Tests: {successful_creations}/{total_creation_tests} successful")
        
        for endpoint, result in creation_results.items():
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {endpoint}: {result['status_code']}")
    else:
        print("🔧 Creation Tests: No results")
    
    print(f"\n📊 Total Shelves in System: {len(shelves)}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if creation_results and sum(1 for r in creation_results.values() if r['success']) > 0:
        print("✅ Shelf creation functionality is working!")
        print("🎯 Ready for production use.")
    else:
        print("⚠️  Shelf creation may have issues.")
        print("🔧 Check authentication and permissions.")
    
    print("\n🎯 NEXT STEPS")
    print("-" * 40)
    print("1. 🧪 Test shelf creation manually in browser")
    print("2. 👤 Verify admin/staff permissions")
    print("3. 📊 Test shelf rental workflow")
    print("4. 💰 Verify pricing calculations")

if __name__ == "__main__":
    main()
