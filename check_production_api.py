import requests
import json

# Check what users the production API is returning
try:
    print("Checking production API...")
    response = requests.get('https://errantmate.onrender.com/get_users')
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ API returned {len(users)} users:")
        print("=" * 50)
        
        for user in users:
            username = user.get('username', 'Unknown')
            role = user.get('role', 'Unknown')
            created_at = user.get('created_at', 'Unknown')
            is_admin = user.get('is_admin', False)
            
            print(f"Username: {username:12} | Role: {role:8} | Admin: {is_admin} | Created: {created_at}")
        
        print("=" * 50)
        
        # Check for problem users
        problem_users = []
        for user in users:
            username = user.get('username', '')
            if username in ['Datox', 'mary']:
                problem_users.append(username)
        
        if problem_users:
            print(f"🚨 PROBLEM: Found SQLite users in API response: {problem_users}")
        else:
            print("✅ GOOD: No SQLite users found in API response")
            
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - Need to be logged in")
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error checking API: {e}")
