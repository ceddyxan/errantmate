#!/usr/bin/env python3
"""
Simple fix for end-rental 500 error
"""

import requests
import json

def fix_end_rental_api():
    """Fix the end-rental API 500 error"""
    
    base_url = "https://errantmate.onrender.com"
    
    print("🔧 FIXING END-RENTAL 500 ERROR")
    print("=" * 40)
    
    # The issue is that the Shelf model doesn't recognize the new fields
    # Let's create a simple end-rental endpoint that bypasses the model issues
    
    print("\n1. Testing current end-rental API...")
    
    # First, let's see what shelves are available
    try:
        response = requests.get(f"{base_url}/api/shelves", timeout=10)
        
        if response.status_code == 200:
            try:
                shelves = response.json()
                print(f"   ✅ Found {len(shelves)} shelves")
                
                # Find an occupied shelf
                occupied_shelves = [s for s in shelves if s.get('status') == 'occupied']
                print(f"   ✅ Found {len(occupied_shelves)} occupied shelves")
                
                if occupied_shelves:
                    test_shelf = occupied_shelves[0]
                    shelf_id = test_shelf.get('id')
                    print(f"   ✅ Testing with occupied shelf: {shelf_id}")
                    
                    # Test end-rental API
                    response = requests.post(f"{base_url}/api/shelves/end-rental", json={"shelfId": shelf_id}, timeout=10)
                    print(f"   End-rental API: {response.status_code}")
                    
                    if response.status_code == 500:
                        print("   ❌ 500 error confirmed")
                        try:
                            error_data = response.json()
                            print(f"   Error: {error_data.get('error', 'Unknown')}")
                        except:
                            print(f"   Response: {response.text[:300]}...")
                            
                        # The issue is model-related - we need a simple fix
                        print("\n2. Creating simple end-rental fix...")
                        return create_simple_end_rental_fix(base_url)
                        
                    elif response.status_code == 200:
                        try:
                            result = response.json()
                            if result.get('success'):
                                print("   ✅ End-rental working!")
                                return True
                            else:
                                print(f"   ⚠️  Error: {result.get('error', 'Unknown')}")
                        except:
                            print("   ⚠️  Unexpected response format")
                    else:
                        print(f"   ⚠️  Status: {response.status_code}")
                else:
                    print("   ⚠️  No occupied shelves found")
                    
            except json.JSONDecodeError:
                print("   ❌ Shelves API returning HTML")
                
        else:
            print(f"   ❌ Shelves API failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    return False

def create_simple_end_rental_fix(base_url):
    """Create a simple end-rental endpoint that bypasses model issues"""
    
    print("   💡 Creating simple end-rental endpoint...")
    
    # We need to add a simple endpoint that directly updates the database
    # without using the Shelf model that has field recognition issues
    
    simple_endpoint_code = '''
@app.route('/api/shelves/end-rental-simple', methods=['POST'])
@login_required
@database_required
def end_shelf_rental_simple():
    """Simple end rental that bypasses model issues"""
    try:
        # Check if user has permission
        if session.get('user_role') not in ['admin', 'staff']:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        data = request.get_json()
        shelf_id = data.get('shelfId')
        
        if not shelf_id:
            return jsonify({'success': False, 'error': 'Shelf ID required'}), 400
        
        # Direct database update without using Shelf model
        try:
            # Update shelf directly using SQL
            if 'sqlite' in str(db.engine.url).lower():
                # SQLite
                sql = """
                UPDATE shelf 
                SET status = 'available',
                    customer_name = NULL,
                    customer_phone = NULL,
                    customer_email = NULL,
                    card_number = NULL,
                    items_description = NULL,
                    rental_period = NULL,
                    discount = NULL,
                    rented_date = NULL,
                    maintenance_reason = NULL,
                    updated_at = datetime('now')
                WHERE id = ?
                """
            else:
                # PostgreSQL
                sql = """
                UPDATE shelf 
                SET status = 'available',
                    customer_name = NULL,
                    customer_phone = NULL,
                    customer_email = NULL,
                    card_number = NULL,
                    items_description = NULL,
                    rental_period = NULL,
                    discount = NULL,
                    rented_date = NULL,
                    maintenance_reason = NULL,
                    updated_at = NOW()
                WHERE id = %s
                """
            
            with db.engine.connect() as conn:
                if 'sqlite' in str(db.engine.url).lower():
                    result = conn.execute(db.text(sql), (shelf_id,))
                else:
                    result = conn.execute(db.text(sql), (shelf_id,))
                conn.commit()
            
            if result.rowcount > 0:
                # Log the action
                log_action(
                    username=session.get('username', 'unknown'),
                    action=f"Ended rental for shelf {shelf_id} (simple method)",
                    details="Rental ended using direct SQL update"
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
            app.logger.error(f"Simple end-rental error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Database update failed'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Simple end-rental failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
'''
    
    print("   ✅ Simple endpoint code prepared")
    print("   📝 Need to add this to app.py and deploy")
    
    return True

if __name__ == "__main__":
    success = fix_end_rental_api()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 END-RENTAL FIX IDENTIFIED!")
        print("✅ Need to deploy simple end-rental endpoint")
        print("🔧 This will bypass model field recognition issues")
        print("🌐 Will provide immediate shelf availability")
    else:
        print("❌ FIX INCOMPLETE!")
        print("🔧 Need to deploy simple end-rental solution")
