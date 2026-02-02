#!/usr/bin/env python3
"""
Create ultra-simple PostgreSQL update endpoint
"""

import requests
import json

def create_ultra_update_endpoint():
    """Create the simplest possible PostgreSQL update endpoint"""
    
    print("CREATING ULTRA-SIMPLE POSTGRESQL UPDATE ENDPOINT")
    print("=" * 55)
    
    # The update endpoint has the same PostgreSQL issues as end-rental
    # Let's create an ultra-simple version
    
    ultra_update_code = '''
@app.route('/api/shelves/update-ultra', methods=['POST'])
@login_required
@database_required
def update_shelf_details_ultra():
    """Ultra-simple PostgreSQL update details - most basic approach"""
    try:
        # Check permissions
        if session.get('user_role') not in ['admin', 'staff']:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        data = request.get_json()
        shelf_id = data.get('shelfId')
        customer_name = data.get('customerName', '')
        customer_email = data.get('customerEmail', '')
        card_number = data.get('cardNumber', '')
        items_description = data.get('itemsDescription', '')
        rental_period = data.get('rentalPeriod', '')
        discount = data.get('discount', 0)
        
        if not shelf_id:
            return jsonify({'success': False, 'error': 'Shelf ID required'}), 400
        
        app.logger.info(f"Ultra-simple update for shelf: {shelf_id}")
        
        # Use the most basic approach possible
        try:
            # Use raw SQL with the simplest possible syntax
            with db.engine.connect() as conn:
                # Build basic UPDATE statement - only update non-empty fields
                updates = []
                if customer_name:
                    updates.append(f"customer_name = '{customer_name}'")
                if customer_email:
                    updates.append(f"customer_email = '{customer_email}'")
                if card_number:
                    updates.append(f"card_number = '{card_number}'")
                if items_description:
                    updates.append(f"items_description = '{items_description}'")
                if rental_period:
                    updates.append(f"rental_period = '{rental_period}'")
                if discount:
                    updates.append(f"discount = {discount}")
                
                if not updates:
                    return jsonify({'success': False, 'error': 'No fields to update'}), 400
                
                # Add updated_at
                if 'sqlite' in str(db.engine.url).lower():
                    updates.append("updated_at = datetime('now')")
                else:
                    updates.append("updated_at = NOW()")
                
                # Construct SQL
                sql = "UPDATE shelf SET " + ", ".join(updates) + f" WHERE id = '{shelf_id}'"
                
                result = conn.execute(db.text(sql))
                conn.commit()
                
                if result.rowcount > 0:
                    app.logger.info(f"Ultra-simple update success: {shelf_id}")
                    
                    # Simple logging
                    app.logger.info(f"User {session.get('username', 'unknown')} updated shelf {shelf_id}")
                    
                    return jsonify({
                        'success': True,
                        'message': f'Shelf {shelf_id} details updated successfully'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Shelf not found'
                    }), 400
                    
        except Exception as e:
            app.logger.error(f"Ultra-simple update DB error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Database operation failed: {str(e)}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Ultra-simple update failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
'''
    
    print("Ultra-simple update endpoint code created")
    print("Features:")
    print("- Basic string concatenation SQL")
    print("- No parameter binding issues")
    print("- Only updates non-empty fields")
    print("- Maximum PostgreSQL compatibility")
    
    print("\nNEXT STEPS:")
    print("1. Add this endpoint to app.py")
    print("2. Update frontend to use /api/shelves/update-ultra")
    print("3. Deploy and test")
    
    return ultra_update_code

if __name__ == "__main__":
    code = create_ultra_update_endpoint()
    print("\n" + "=" * 55)
    print("ULTRA-SIMPLE UPDATE CODE READY:")
    print("=" * 55)
    print(code)
