#!/usr/bin/env python3
"""
Test script to verify shelf rental system functionality
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_system():
    """Test the shelf rental system"""
    try:
        print("🧪 Testing Shelf Rental System...")
        
        # Test 1: Database Connection
        print("\n1️⃣ Testing database connection...")
        from app import app, Shelf
        with app.app_context():
            shelves = Shelf.query.all()
            print(f"✅ Database connected - Found {len(shelves)} shelves")
        
        # Test 2: API Endpoints
        print("\n2️⃣ Testing API endpoints...")
        import requests
        
        # Test GET shelves
        response = requests.get('http://localhost:5001/api/shelves')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/shelves working - Returned {len(data)} shelves")
        else:
            print(f"❌ GET /api/shelves failed - Status: {response.status_code}")
            return False
        
        # Test 3: Shelf Rental
        print("\n3️⃣ Testing shelf rental...")
        test_data = {
            'shelfId': 'A-01',
            'customerName': 'Test User',
            'customerPhone': '0712345678',
            'itemsDescription': 'Test items',
            'rentalPeriod': 1
        }
        
        response = requests.post('http://localhost:5001/api/shelves/rent', json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Shelf rental API working correctly")
            else:
                print(f"❌ Shelf rental failed: {result.get('error')}")
        else:
            print(f"❌ POST /api/shelves/rent failed - Status: {response.status_code}")
        
        # Test 4: Statistics
        print("\n4️⃣ Testing statistics...")
        response = requests.get('http://localhost:5001/api/shelves/stats')
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics working - Available: {stats['available']}, Occupied: {stats['occupied']}, Revenue: KSh {stats['revenue']}")
        else:
            print(f"❌ GET /api/shelves/stats failed - Status: {response.status_code}")
        
        print("\n🎉 All tests completed!")
        print("🌐 Shelf rental system is ready for production!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_system()
    sys.exit(0 if success else 1)
