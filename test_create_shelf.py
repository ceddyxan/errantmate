#!/usr/bin/env python3
"""
Test the Create Shelf functionality
"""

import requests
import json

def test_create_shelf():
    """Test the create shelf endpoint"""
    base_url = "https://errantmate.onrender.com"
    
    print("TESTING CREATE SHELF FUNCTIONALITY")
    print("=" * 50)
    
    # Test data
    test_shelf = {
        "shelfId": "TEST-001",
        "price": 800
    }
    
    try:
        print(f"Creating shelf: {test_shelf['shelfId']} with price KSh {test_shelf['price']}")
        
        response = requests.post(
            f"{base_url}/api/shelves/create",
            json=test_shelf,
            headers={
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            cookies=None,  # Will need to be authenticated
            allow_redirects=False
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("Redirect detected - need to login first")
            print("This is expected for unauthenticated requests")
        elif response.status_code == 200:
            result = response.json()
            print(f"Success: {result}")
        elif response.status_code == 403:
            print("Permission denied - need admin/staff login")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Network Error: {e}")
    
    print("\nMANUAL TEST STEPS:")
    print("1. Login as admin/staff")
    print("2. Go to /rent_shelf")
    print("3. Click 'Create New Shelf' button")
    print("4. Fill in Shelf ID (e.g., TEST-002)")
    print("5. Fill in Monthly Fee (e.g., 800)")
    print("6. Click 'Create Shelf'")
    print("7. Check if new shelf appears in the grid")

if __name__ == "__main__":
    test_create_shelf()
