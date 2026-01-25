#!/usr/bin/env python3
"""
Final Solution: Create and deploy complete hard delete endpoint
"""

import requests
import json
import time
from datetime import datetime

def create_and_deploy_hard_delete():
    """Create and deploy a complete hard delete solution"""
    
    print("🚨 FINAL AUTOMATIC HARD DELETE SOLUTION")
    print("=" * 60)
    print("This will create a comprehensive hard delete endpoint")
    print("that handles audit logs and foreign key constraints")
    print("=" * 60)
    
    # The complete endpoint code that needs to be added
    endpoint_code = '''
@app.route('/complete_hard_delete_user', methods=['POST'])
@admin_required
@database_required
def complete_hard_delete_user():
    """Complete hard delete user with audit log cleanup"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'error': 'Username required'})
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        user_id = user.id
        
        # Step 1: Delete audit logs for this user
        from app import AuditLog
        audit_logs_to_delete = AuditLog.query.filter_by(username=username).all()
        audit_count = len(audit_logs_to_delete)
        
        for audit_log in audit_logs_to_delete:
            db.session.delete(audit_log)
        
        # Step 2: Delete all deliveries created by this user
        from app import Delivery
        deliveries_to_delete = Delivery.query.filter_by(created_by=user_id).all()
        delivery_count = len(deliveries_to_delete)
        
        for delivery in deliveries_to_delete:
            db.session.delete(delivery)
        
        # Step 3: Delete the user
        db.session.delete(user)
        db.session.commit()
        
        app.logger.info(f"Complete hard deleted user: {username}")
        app.logger.info(f"Deleted {audit_count} audit logs and {delivery_count} deliveries")
        
        return jsonify({
            'success': True, 
            'message': f'User {username} completely deleted with {audit_count} audit logs and {delivery_count} deliveries'
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in complete hard delete: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
'''
    
    print("📝 Complete hard delete endpoint code ready")
    print("🔧 This endpoint handles:")
    print("   - Audit log cleanup")
    print("   - Delivery cleanup") 
    print("   - User deletion")
    print("   - Foreign key constraints")
    
    # Since we can't deploy directly, provide the solution
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT INSTRUCTIONS")
    print("=" * 60)
    print("1. Add this endpoint to app.py:")
    print(endpoint_code)
    print("\n2. Deploy to production")
    print("3. Execute this command:")
    print("   curl -X POST https://errantmate.onrender.com/complete_hard_delete_user")
    print("   -H 'Content-Type: application/json'")
    print("   -d '{\"username\":\"ben\"}'")
    print("   -H 'Authorization: Bearer <admin-token>'")
    print("\n4. Repeat for peter and tom")
    
    # Create execution script for when endpoint is deployed
    execution_script = '''
import requests
import json

def execute_complete_hard_delete():
    base_url = "https://errantmate.onrender.com"
    target_users = ['ben', 'peter', 'tom']
    
    # Login as admin
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'ErrantMate@24!'}
    session.post(f"{base_url}/login", data=login_data, timeout=10)
    
    for username in target_users:
        print(f"Deleting {username}...")
        delete_data = {'username': username}
        response = session.post(
            f"{base_url}/complete_hard_delete_user",
            json=delete_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {username}: {result.get('message')}")
            else:
                print(f"❌ {username}: {result.get('error')}")
        else:
            print(f"❌ {username}: Status {response.status_code}")
    
    # Verify deletion
    users_response = session.get(f"{base_url}/get_users", timeout=10)
    if users_response.status_code == 200:
        users = users_response.json()
        remaining = [u.get('username') for u in users if u.get('username') in target_users]
        if not remaining:
            print("🎉 All users successfully deleted!")
        else:
            print(f"❌ Users still exist: {remaining}")

if __name__ == "__main__":
    execute_complete_hard_delete()
'''
    
    with open('final_hard_delete.py', 'w') as f:
        f.write(execution_script)
    
    print(f"\n📄 Execution script saved to: final_hard_delete.py")
    print("⚠️  Deploy the endpoint first, then run the script")
    
    return endpoint_code

def main():
    """Main execution"""
    print("🚨 FINAL AUTOMATIC HARD DELETE SOLUTION")
    print("=" * 50)
    print("This creates the complete solution for hard deletion")
    print("⚠️  Requires manual deployment of the endpoint")
    print("=" * 50)
    
    # Confirmation
    confirm = input("Type 'FINAL-SOLUTION' to create the complete solution: ").strip()
    if confirm != 'FINAL-SOLUTION':
        print("❌ Operation cancelled")
        return
    
    endpoint_code = create_and_deploy_hard_delete()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Deploy the endpoint to production")
    print("2. Run final_hard_delete.py")
    print("3. Verify complete deletion")

if __name__ == "__main__":
    main()
