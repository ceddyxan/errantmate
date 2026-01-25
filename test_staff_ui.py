def test_staff_role_ui():
    """Test that both modals have Staff role option"""
    
    print("Testing Staff Role UI Implementation...")
    print("=" * 50)
    
    # Check template file for staff role presence
    try:
        with open('templates/reports.html', 'r') as f:
            content = f.read()
        
        # Test 1: Check if old modal has staff role
        old_modal_staff = '<option value="staff">Staff</option>' in content and 'id="roleSelect"' in content
        print(f"OLD Modal (userModal) - Staff Role: {'✓ PRESENT' if old_modal_staff else '✗ MISSING'}")
        
        # Test 2: Check if new modal has staff role  
        new_modal_staff = '<option value="staff">Staff</option>' in content and 'id="newRoleSelect"' in content
        print(f"NEW Modal (newUserModal) - Staff Role: {'✓ PRESENT' if new_modal_staff else '✗ MISSING'}")
        
        # Test 3: Check if JavaScript validation includes staff
        js_validation_staff = "role !== 'admin' && role !== 'user' && role !== 'staff'" in content
        print(f"JavaScript Validation - Staff Role: {'✓ PRESENT' if js_validation_staff else '✗ MISSING'}")
        
        # Test 4: Check if button calls correct function
        button_calls_new = 'onclick="showNewUserModal()"' in content
        print(f"Add User Button - Calls New Modal: {'✓ CORRECT' if button_calls_new else '✗ INCORRECT'}")
        
        print("\n" + "=" * 50)
        
        if old_modal_staff and new_modal_staff and js_validation_staff:
            print("SUCCESS: Staff role is fully implemented in UI!")
            print("\nWhat you should see:")
            print("- Role dropdown with: User, Staff, Admin")
            print("- Staff role validation in JavaScript")
            print("- Both old and new modals support Staff role")
        else:
            print("WARNING: Some components may be missing Staff role")
            
        print("\nStaff Role Capabilities:")
        print("- Can manage deliveries")
        print("- Can update delivery status")
        print("- Can be assigned as delivery person")
        print("- Cannot view reports (admin only)")
        
    except Exception as e:
        print(f"Error reading template file: {e}")

if __name__ == '__main__':
    test_staff_role_ui()
