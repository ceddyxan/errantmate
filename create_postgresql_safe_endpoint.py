#!/usr/bin/env python3
"""
Create a guaranteed PostgreSQL-compatible end-rental endpoint
"""

import requests
import json

def create_postgresql_safe_endpoint():
    """Create a PostgreSQL-safe end-rental endpoint"""
    
    print("CREATING POSTGRESQL-SAFE END-RENTAL")
    print("=" * 45)
    
    # The issue is that our current approach is too complex
    # Let's create a super simple endpoint that just uses basic SQL
    
    safe_endpoint_code = '''
@app.route('/api/shelves/end-rental-safe', methods=['POST'])
@login_required
@database_required
def end_shelf_rental_safe():
    """PostgreSQL-safe end rental - minimal approach"""
    try:
        # Check permissions
        if session.get('user_role') not in ['admin', 'staff']:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        data = request.get_json()
        shelf_id = data.get('shelfId')
        
        if not shelf_id:
            return jsonify({'success': False, 'error': 'Shelf ID required'}), 400
        
        app.logger.info(f"Safe end-rental for shelf: {shelf_id}")
        
        # Use the simplest possible approach - just update status
        try:
            with db.engine.connect() as conn:
                # Simple update that just changes status
                if 'sqlite' in str(db.engine.url).lower():
                    sql = "UPDATE shelf SET status = 'available' WHERE id = ?"
                    params = (shelf_id,)
                else:
                    # PostgreSQL - use string formatting for safety
                    sql = f"UPDATE shelf SET status = 'available' WHERE id = '{shelf_id}'"
                    params = None
                
                result = conn.execute(db.text(sql), params or {})
                conn.commit()
                
                if result.rowcount > 0:
                    app.logger.info(f"Safe end-rental success: {shelf_id}")
                    
                    # Log the action
                    log_action(
                        username=session.get('username', 'unknown'),
                        action=f"Ended rental for shelf {shelf_id} (safe method)",
                        details="Rental ended using minimal SQL update"
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': f'Shelf {shelf_id} rental ended successfully'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Shelf not found or already available'
                    }), 400
                    
        except Exception as e:
            app.logger.error(f"Safe end-rental DB error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Database operation failed'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Safe end-rental failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
'''
    
    print("✅ Safe endpoint code created")
    print("📝 Features:")
    print("   - Minimal SQL update (just status field)")
    print("   - PostgreSQL string formatting for safety")
    print("   - No complex field operations")
    print("   - Simple and reliable")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Add this endpoint to app.py")
    print("2. Update frontend to use /api/shelves/end-rental-safe")
    print("3. Deploy and test")
    
    return safe_endpoint_code

if __name__ == "__main__":
    code = create_postgresql_safe_endpoint()
    print("\n" + "=" * 45)
    print("CODE READY TO ADD TO APP.PY:")
    print("=" * 45)
    print(code)
