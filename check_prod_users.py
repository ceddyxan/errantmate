import requests
import json

def check_production_users():
    try:
        print("🔍 Checking production debug endpoint...")
        response = requests.get('https://errantmate.onrender.com/debug/check_users', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Got data from production")
            print(json.dumps(data, indent=2))
            
            # Extract users if available
            if 'users' in data:
                users = data['users']
                print(f"\n📊 PRODUCTION USERS ({len(users)} found):")
                print("=" * 60)
                
                for user in users:
                    username = user.get('username', 'Unknown')
                    role = user.get('role', 'Unknown')
                    created_at = user.get('created_at', 'Unknown')
                    is_active = user.get('is_active', 'Unknown')
                    
                    status = '✅ Active' if is_active else '❌ Inactive'
                    print(f"Username: {username:12} | Role: {role:8} | Status: {status} | Created: {created_at}")
                
                print("=" * 60)
                
                # Check for problem users
                problem_users = []
                correct_users = []
                
                for user in users:
                    username = user.get('username', '')
                    if username in ['Datox', 'mary']:
                        problem_users.append(username)
                    elif username in ['admin', 'staff', 'marques']:
                        correct_users.append(username)
                
                if problem_users:
                    print(f"🚨 PROBLEM: Found SQLite users: {problem_users}")
                else:
                    print("✅ GOOD: No SQLite users found")
                    
                if correct_users:
                    print(f"✅ CORRECT: Found PostgreSQL users: {correct_users}")
                else:
                    print("❌ MISSING: No correct PostgreSQL users found")
            else:
                print("❌ No users data in response")
                
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Need login")
        elif response.status_code == 404:
            print("❌ 404 Not Found - Debug endpoint not available")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Production server not responding")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Cannot reach production server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_production_users()
