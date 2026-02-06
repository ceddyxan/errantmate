#!/usr/bin/env python3
"""
Shelf Creation Test Suite
This script will test the Create New Shelf functionality comprehensively.
"""

import requests
import json
import time
from datetime import datetime

# Production URL
PRODUCTION_URL = "https://errantmate.onrender.com"

def test_shelf_creation_endpoints():
    """Test all shelf creation endpoints"""
    print("🔧 Shelf Creation Functionality Test")
    print("=" * 60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing URL: {PRODUCTION_URL}")
    print()
    
    # Test data
    test_shelves = [
        {"shelfId": "TEST-01", "price": 800},
        {"shelfId": "TEST-02", "price": 1200},
        {"shelfId": "TEST-03", "price": 1500}
    ]
    
    # Endpoints to test
    creation_endpoints = [
        ("/api/shelves/create", "Standard Create"),
        ("/api/shelves/create-orm", "ORM Create"),
        ("/api/shelves/create-secure", "Secure Create"),
        ("/api/shelves/create-simple", "Simple Create"),
        ("/api/shelves/create-ultra", "Ultra Create")
    ]
    
    results = {}
    
    print("🧪 Testing Shelf Creation Endpoints")
    print("-" * 40)
    
    for endpoint, description in creation_endpoints:
        print(f"\n📡 Testing: {description}")
        print(f"   Endpoint: {endpoint}")
        
        # Test with unique shelf ID for each endpoint
        test_shelf = test_shelves[creation_endpoints.index((endpoint, description))]
        
        try:
            response = requests.post(
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
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error: Could not connect")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': 'Connection Error'}
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[endpoint] = {'status_code': 0, 'success': False, 'response': str(e)}
        
        time.sleep(1)  # Rate limiting
    
    return results

def test_shelf_listing():
    """Test shelf listing functionality"""
    print("\n📋 Testing Shelf Listing")
    print("-" * 40)
    
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/shelves", timeout=15)
        
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

def test_shelf_management():
    """Test shelf management functionality"""
    print("\n🔧 Testing Shelf Management")
    print("-" * 40)
    
    try:
        # Get shelves to find a test shelf
        response = requests.get(f"{PRODUCTION_URL}/api/shelves", timeout=15)
        
        if response.status_code == 200:
            shelves = response.json()
            test_shelf = next((s for s in shelves if s.get('id', '').startswith('TEST-')), None)
            
            if test_shelf:
                shelf_id = test_shelf['id']
                print(f"🧪 Testing with shelf: {shelf_id}")
                
                # Test update endpoint
                update_data = {
                    "shelfId": shelf_id,
                    "customerName": "Test Customer",
                    "customerEmail": "test@example.com",
                    "cardNumber": "1234567890123456",
                    "itemsDescription": "Test items for storage",
                    "rentalPeriod": 3
                }
                
                update_response = requests.post(
                    f"{PRODUCTION_URL}/api/shelves/update-ultra",
                    json=update_data,
                    timeout=15,
                    headers={"Content-Type": "application/json"}
                )
                
                if update_response.status_code == 200:
                    result = update_response.json()
                    print(f"✅ Shelf update successful: {result.get('success', False)}")
                else:
                    print(f"❌ Shelf update failed: {update_response.status_code}")
                    print(f"📄 Error: {update_response.text[:200]}...")
                
            else:
                print("⚠️  No test shelves found for management testing")
        
    except Exception as e:
        print(f"❌ Error testing shelf management: {e}")

def test_page_access():
    """Test shelf page access"""
    print("\n🌐 Testing Page Access")
    print("-" * 40)
    
    pages = [
        ("/rent_shelf", "Rent Shelf Page"),
        ("/", "Main Dashboard")
    ]
    
    for page, description in pages:
        try:
            response = requests.get(f"{PRODUCTION_URL}{page}", timeout=15)
            
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

def cleanup_test_shelves():
    """Clean up test shelves (if needed)"""
    print("\n🧹 Cleanup Test Shelves")
    print("-" * 40)
    
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/shelves", timeout=15)
        
        if response.status_code == 200:
            shelves = response.json()
            test_shelves = [s for s in shelves if s.get('id', '').startswith('TEST-')]
            
            if test_shelves:
                print(f"🧪 Found {len(test_shelves)} test shelves")
                print("⚠️  Note: Manual cleanup may be needed via admin interface")
                for shelf in test_shelves:
                    print(f"   {shelf.get('id')}: {shelf.get('status')}")
            else:
                print("✅ No test shelves to clean up")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def main():
    """Main test function"""
    print("🧪 ErrantMate Shelf Creation Test Suite")
    print("=" * 60)
    
    # Run tests
    creation_results = test_shelf_creation_endpoints()
    shelves = test_shelf_listing()
    test_shelf_management()
    test_page_access()
    cleanup_test_shelves()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    
    successful_creations = sum(1 for r in creation_results.values() if r['success'])
    total_creation_tests = len(creation_results)
    
    print(f"🔧 Creation Tests: {successful_creations}/{total_creation_tests} successful")
    
    for endpoint, result in creation_results.items():
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {endpoint}: {result['status_code']}")
    
    print(f"\n📊 Total Shelves in System: {len(shelves)}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if successful_creations == total_creation_tests:
        print("✅ All shelf creation endpoints working perfectly!")
        print("🎯 Shelf functionality is ready for production use.")
    elif successful_creations > 0:
        print("⚠️  Some shelf creation endpoints working.")
        print("🔧 Check failed endpoints for specific issues.")
    else:
        print("❌ No shelf creation endpoints working.")
        print("🚨 Immediate attention needed for shelf functionality.")
    
    print("\n🎯 NEXT STEPS")
    print("-" * 40)
    print("1. 🧪 Test shelf creation manually in production")
    print("2. 👤 Verify admin/staff permissions work correctly")
    print("3. 📊 Test shelf rental and management workflows")
    print("4. 💰 Verify pricing and payment calculations")

if __name__ == "__main__":
    main()
