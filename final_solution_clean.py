#!/usr/bin/env python3
"""
Final Hard Delete Solution - Clean Version
"""

import requests
import json
import time
from datetime import datetime

def create_final_solution():
    """Create the final hard delete solution"""
    
    print("FINAL HARD DELETE SOLUTION")
    print("=" * 50)
    
    # The complete endpoint code
    endpoint_code = '''@app.route('/complete_hard_delete_user', methods=['POST'])
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
        
        return jsonify({
            'success': True, 
            'message': f'User {username} completely deleted with {audit_count} audit logs and {delivery_count} deliveries'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
'''
    
    print("Endpoint code created successfully")
    print("This endpoint handles:")
    print("  - Audit log cleanup")
    print("  - Delivery cleanup")
    print("  - User deletion")
    print("  - Foreign key constraints")
    
    # Save endpoint to file
    with open('hard_delete_endpoint.py', 'w') as f:
        f.write(endpoint_code)
    
    print("Endpoint saved to: hard_delete_endpoint.py")
    
    return endpoint_code

def main():
    print("FINAL HARD DELETE SOLUTION")
    print("=" * 50)
    print("This creates the complete solution for hard deletion")
    print("=" * 50)
    
    endpoint_code = create_final_solution()
    
    print("\nNEXT STEPS:")
    print("1. Add the endpoint from hard_delete_endpoint.py to app.py")
    print("2. Deploy to production")
    print("3. Execute the deletion")
    
    print("\nWhen deployed, use this to delete users:")
    print("curl -X POST https://errantmate.onrender.com/complete_hard_delete_user")
    print("-H 'Content-Type: application/json'")
    print("-d '{\"username\":\"ben\"}'")
    print("(with admin authentication)")

if __name__ == "__main__":
    main()
