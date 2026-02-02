#!/usr/bin/env python3
"""
Create ultra-simple PostgreSQL end-rental endpoint
"""

import requests
import json

def create_ultra_simple_endpoint():
    """Create the simplest possible PostgreSQL endpoint"""
    
    print("CREATING ULTRA-SIMPLE POSTGRESQL ENDPOINT")
    print("=" * 50)
    
    # The issue might be with complex SQL or string formatting
    # Let's create the most basic approach possible
    
    ultra_simple_code = '''
@app.route('/api/shelves/end-rental-ultra', methods=['POST'])
@login_required
@database_required
def end_shelf_rental_ultra():
    """Ultra-simple PostgreSQL end rental - most basic approach"""
    try:
        # Check permissions
        if session.get('user_role') not in ['admin', 'staff']:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        data = request.get_json()
        shelf_id = data.get('shelfId')
        
        if not shelf_id:
            return jsonify({'success': False, 'error': 'Shelf ID required'}), 400
        
        app.logger.info(f"Ultra-simple end-rental for shelf: {shelf_id}")
        
        # Use the most basic approach possible
        try:
            # Use raw SQL with the simplest possible syntax
            with db.engine.connect() as conn:
                # Use the most basic UPDATE statement
                sql = "UPDATE shelf SET status = 'available' WHERE id = '" + shelf_id + "'"
                
                result = conn.execute(db.text(sql))
                conn.commit()
                
                if result.rowcount > 0:
                    app.logger.info(f"Ultra-simple end-rental success: {shelf_id}")
                    
                    # Log the action
                    log_action(
                        username=session.get('username', 'unknown'),
                        action=f"Ended rental for shelf {shelf_id} (ultra-simple method)",
                        details="Rental ended using ultra-simple SQL update"
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
            app.logger.error(f"Ultra-simple end-rental DB error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Database operation failed: {str(e)}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Ultra-simple end-rental failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
'''
    
    print("Ultra-simple endpoint code created")
    print("Features:")
    print("- Most basic SQL string concatenation")
    print("- No parameter binding issues")
    print("- Single field update (status only)")
    print("- Maximum PostgreSQL compatibility")
    
    print("\nNEXT STEPS:")
    print("1. Add this endpoint to app.py")
    print("2. Update frontend to use /api/shelves/end-rental-ultra")
    print("3. Deploy and test")
    
    return ultra_simple_code

if __name__ == "__main__":
    code = create_ultra_simple_endpoint()
    print("\n" + "=" * 50)
    print("ULTRA-SIMPLE CODE READY:")
    print("=" * 50)
    print(code)
