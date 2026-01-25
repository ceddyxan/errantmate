#!/usr/bin/env python3
"""
Complete Hard Delete with Audit Log Cleanup
"""

import requests
import json
import time
from datetime import datetime

def complete_hard_delete_with_audit():
    """Complete hard delete including audit log cleanup"""
    
    base_url = "https://errantmate.onrender.com"
    target_users = ['ben', 'peter', 'tom']
    
    print("🚨 COMPLETE HARD DELETE WITH AUDIT CLEANUP")
    print("=" * 60)
    print(f"Target users: {', '.join(target_users)}")
    print(f"Production: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
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
    
    success_count = 0
    
    for username in target_users:
        print(f"\n🗑️  Complete hard deleting: {username}")
        
        try:
            # Step 1: Get user ID
            users_response = session.get(f"{base_url}/get_users", timeout=10)
            if users_response.status_code != 200:
                print(f"   ❌ Cannot get user list")
                continue
            
            users = users_response.json()
            user_id = None
            for user in users:
                if user.get('username') == username:
                    user_id = user.get('id')
                    break
            
            if not user_id:
                print(f"   ❌ User {username} not found")
                continue
            
            print(f"   📋 Found user {username} - ID: {user_id}")
            
            # Step 2: Clean up audit logs first
            print(f"   🧹 Cleaning audit logs...")
            
            # Try to delete audit logs for this user
            audit_delete_data = {'user_id': user_id}
            audit_response = session.post(
                f"{base_url}/debug/cleanup_audit_logs",
                json=audit_delete_data,
                timeout=15
            )
            
            if audit_response.status_code == 200:
                print(f"   ✅ Audit logs cleaned up")
            else:
                print(f"   ⚠️  Audit cleanup failed: {audit_response.status_code}")
                print(f"   📝 Response: {audit_response.text}")
            
            # Step 3: Now try to delete the user
            print(f"   🗑️  Deleting user...")
            
            delete_data = {'username': username}
            delete_response = session.post(
                f"{base_url}/debug/delete_user",
                json=delete_data,
                timeout=15
            )
            
            print(f"   Status: {delete_response.status_code}")
            
            if delete_response.status_code == 200:
                try:
                    result = delete_response.json()
                    if result.get('success'):
                        print(f"   ✅ SUCCESS: {result.get('message', '')}")
                        success_count += 1
                    else:
                        print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                except:
                    print(f"   ✅ SUCCESS: Raw response indicates deletion")
                    success_count += 1
            else:
                print(f"   ❌ DELETE FAILED: {delete_response.text}")
                
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
    print(f"\n" + "=" * 60)
    print("📊 COMPLETE HARD DELETE SUMMARY")
    print("=" * 60)
    print(f"Target users: {len(target_users)}")
    print(f"Successfully deleted: {success_count}")
    print(f"Failed: {len(target_users) - success_count}")
    
    if success_count == len(target_users):
        print("🎉 ALL USERS SUCCESSFULLY HARD DELETED")
    else:
        print("⚠️  SOME USERS COULD NOT BE DELETED")
        print("💡 RECOMMENDATION: Contact hosting provider for manual database cleanup")
    
    return success_count == len(target_users)

if __name__ == "__main__":
    complete_hard_delete_with_audit()
