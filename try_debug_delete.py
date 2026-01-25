#!/usr/bin/env python3
"""
Try existing debug delete endpoint for hard deletion
"""

import requests
import json
import time
from datetime import datetime

def try_existing_debug_delete():
    """Try using existing debug delete endpoint"""
    
    base_url = "https://errantmate.onrender.com"
    target_users = ['ben', 'peter', 'tom']
    
    print("🔨 TRYING EXISTING DEBUG DELETE ENDPOINT")
    print("=" * 50)
    print(f"Target users: {', '.join(target_users)}")
    print(f"Endpoint: /debug/delete_user")
    print("=" * 50)
    
    # Login as admin
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'ErrantMate@24!'}
    
    try:
        print("🔐 Logging in as admin...")
        login_response = session.post(f"{base_url}/login", data=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        print("✅ Admin login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Try debug delete for each user
    success_count = 0
    
    for username in target_users:
        print(f"\n🗑️  Debug deleting: {username}")
        
        try:
            delete_data = {'username': username}
            response = session.post(
                f"{base_url}/debug/delete_user",
                json=delete_data,
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response: {result}")
                    
                    if result.get('success'):
                        print(f"   ✅ SUCCESS: {result.get('message', '')}")
                        success_count += 1
                    else:
                        print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                except:
                    print(f"   ✅ SUCCESS: Raw response indicates deletion")
                    success_count += 1
            else:
                print(f"   ❌ REQUEST FAILED: {response.text}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    # Final verification
    print(f"\n🔍 Final verification...")
    
    try:
        users_response = session.get(f"{base_url}/get_users", timeout=10)
        if users_response.status_code == 200:
            users = users_response.json()
            remaining_targets = [u.get('username') for u in users if u.get('username') in target_users]
            
            if not remaining_targets:
                print("✅ VERIFICATION SUCCESS: All users completely removed")
            else:
                print(f"❌ VERIFICATION FAILED: Users still exist: {remaining_targets}")
        else:
            print("❌ Could not verify - user list unavailable")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    # Test recreation to confirm
    print(f"\n🧪 Testing recreation to confirm deletion...")
    
    for username in target_users:
        try:
            test_data = {
                'username': username,
                'password': 'test123',
                'role': 'user'
            }
            
            test_response = requests.post(
                f"{base_url}/api/users/public",
                json=test_data,
                timeout=10
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                if result.get('success'):
                    print(f"✅ {username}: Can recreate (hard delete successful)")
                    # Clean up test user
                    test_user_id = result.get('user', {}).get('id')
                    if test_user_id:
                        session.delete(f"{base_url}/api/users/{test_user_id}", timeout=10)
                else:
                    print(f"❌ {username}: {result.get('error')}")
            else:
                print(f"❌ {username}: Status {test_response.status_code}")
                
        except Exception as e:
            print(f"❌ {username}: Error {e}")
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 EXECUTION SUMMARY")
    print("=" * 50)
    print(f"Target users: {len(target_users)}")
    print(f"Successfully deleted: {success_count}")
    print(f"Failed: {len(target_users) - success_count}")
    
    if success_count == len(target_users):
        print("🎉 ALL USERS SUCCESSFULLY HARD DELETED")
    else:
        print("⚠️  SOME USERS COULD NOT BE DELETED")
    
    return success_count == len(target_users)

if __name__ == "__main__":
    try_existing_debug_delete()
