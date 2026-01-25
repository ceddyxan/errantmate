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
        
        return jsonify({
            'success': True, 
            'message': f'User {username} completely deleted with {audit_count} audit logs and {delivery_count} deliveries'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
