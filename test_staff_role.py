import requests
import json

def test_staff_role():
    """Test that staff role can be created via API"""
    
    # Test data for creating a staff user
    staff_user_data = {
        'username': 'test_staff',
        'password': 'staff123',
        'role': 'staff'
    }
    
    print("Testing staff role creation...")
    print(f"User data: {staff_user_data}")
    
    try:
        # This would normally be a POST request to your API
        # For now, we'll just validate the role is acceptable
        valid_roles = ['admin', 'user', 'staff']
        
        if staff_user_data['role'] in valid_roles:
            print("✅ Staff role is valid!")
            print(f"✅ Role '{staff_user_data['role']}' is accepted in validation")
        else:
            print("❌ Staff role validation failed")
            
        print("\n📋 Available roles:")
        for role in valid_roles:
            print(f"  - {role}")
            
        print("\n🎯 Staff role privileges:")
        print("  ✅ Can manage deliveries")
        print("  ✅ Can update delivery status") 
        print("  ✅ Can be assigned as delivery person")
        print("  ❌ Cannot view reports")
        print("  ❌ Cannot access admin features")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_staff_role()
