#!/usr/bin/env python3
"""
Test the frontend password display by simulating the JavaScript template
"""

def test_frontend_template():
    """Test the frontend template logic"""
    
    # Simulate the user data from backend
    users = [
        {
            'id': 1,
            'username': 'admin',
            'role': 'admin',
            'created_at': '2026-02-01 10:00',
            'is_admin': True,
            'can_edit': False,
            'show_password': None,
            'password_hash': None
        },
        {
            'id': 2,
            'username': 'mary',
            'role': 'staff',
            'created_at': '2026-02-06 15:45',
            'is_admin': False,
            'can_edit': True,
            'show_password': True,
            'password_hash': '112233'
        }
    ]
    
    print("🧪 Testing Frontend Template Logic")
    print("=" * 40)
    
    for user in users:
        print(f"\n👤 User: {user['username']}")
        print(f"   Role: {user['role']}")
        print(f"   Show Password: {user['show_password']}")
        print(f"   Password: {user['password_hash']}")
        
        # Simulate the template logic
        password_section = ""
        if user['show_password']:
            password_section = f"""
                <div class="text-xs text-gray-400 mt-1">
                    <span class="text-gray-600 font-medium">Password:</span>
                    <span class="font-mono bg-green-100 text-green-800 px-2 py-0.5 rounded border border-green-200" id="hash-{user['id']}">
                        {user['password_hash']}
                    </span>
                    <button onclick="copyPassword({user['id']}, '{user['password_hash']}')" 
                            class="ml-2 text-green-600 hover:text-green-800 text-xs underline font-medium">
                        <i class="fas fa-copy mr-1"></i>Copy
                    </button>
                </div>
            """
            print("   ✅ Password section WOULD be displayed")
            print(f"   📝 HTML: {password_section.strip()}")
        else:
            print("   ❌ Password section would NOT be displayed")

if __name__ == "__main__":
    test_frontend_template()
