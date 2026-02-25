import requests
import json
import time

def check_public_users():
    try:
        print("🔍 Checking NEW public endpoint...")
        response = requests.get('https://errantmate.onrender.com/public_check_users', timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Got production users!")
            print(json.dumps(data, indent=2))
            
            users = data.get('users', [])
            print(f"\n📊 PRODUCTION DATABASE USERS ({len(users)} total):")
            print("=" * 70)
            
            for user in users:
                username = user.get('username', 'Unknown')
                role = user.get('role', 'Unknown')
                is_active = user.get('is_active', False)
                created_at = user.get('created_at', 'Unknown')
                
                status = '✅ Active' if is_active else '❌ Inactive'
                print(f"Username: {username:12} | Role: {role:8} | Status: {status} | Created: {created_at}")
            
            print("=" * 70)
            
            # Analysis
            problem_users = []
            correct_users = []
            
            for user in users:
                username = user.get('username', '')
                if username in ['Datox', 'mary']:
                    problem_users.append(username)
                elif username in ['admin', 'staff', 'marques']:
                    correct_users.append(username)
            
            print(f"\n🔍 ANALYSIS:")
            print(f"Problem users (SQLite): {problem_users}")
            print(f"Correct users (PostgreSQL): {correct_users}")
            
            if problem_users:
                print(f"\n🚨 ISSUE FOUND: SQLite users still in production database!")
                print("These need to be removed from PostgreSQL.")
            else:
                print(f"\n✅ GOOD: No SQLite users in production database!")
                
        elif response.status_code == 404:
            print("❌ 404 - Endpoint not deployed yet")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Server still deploying...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_public_users()
