#!/usr/bin/env python3
"""
Automatic Hard Delete Endpoint for Errantmate Production
This script adds a hard delete endpoint to the application
"""

import requests
import json
import time
from datetime import datetime

class AutoHardDelete:
    def __init__(self, base_url="https://errantmate.onrender.com"):
        self.base_url = base_url
        self.target_users = ['ben', 'peter', 'tom']
        self.deletion_log = []
        
    def log_action(self, action, user, status, details=""):
        """Log deletion actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'user': user,
            'status': status,
            'details': details
        }
        self.deletion_log.append(log_entry)
        print(f"[{timestamp}] {action}: {user} - {status} {details}")
    
    def deploy_hard_delete_endpoint(self):
        """Deploy hard delete endpoint to production"""
        print("🚀 Deploying hard delete endpoint to production...")
        
        # This would require deployment access to the production environment
        # Since we can't directly deploy, we'll create the code and instructions
        
        endpoint_code = '''
@app.route('/auto_hard_delete_user', methods=['POST'])
@admin_required
@database_required
def auto_hard_delete_user():
    """Automatic hard delete user from database"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'error': 'Username required'})
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Delete all deliveries created by this user
        from app import Delivery
        deliveries_to_delete = Delivery.query.filter_by(created_by=user.id).all()
        delivery_count = len(deliveries_to_delete)
        
        for delivery in deliveries_to_delete:
            db.session.delete(delivery)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'User {username} and {delivery_count} deliveries hard deleted'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
'''
        
        self.log_action("DEPLOY", "endpoint", "CODE_READY", "Hard delete endpoint code prepared")
        return endpoint_code
    
    def execute_hard_delete(self):
        """Execute hard delete using the deployed endpoint"""
        print("🔨 Executing automatic hard delete...")
        
        # Login as admin
        session = requests.Session()
        login_data = {'username': 'admin', 'password': 'ErrantMate@24!'}
        
        try:
            login_response = session.post(f"{self.base_url}/login", data=login_data, timeout=10)
            if login_response.status_code != 200:
                self.log_action("LOGIN", "admin", "FAILED", "Cannot login")
                return False
        except:
            self.log_action("LOGIN", "admin", "ERROR", "Login failed")
            return False
        
        self.log_action("LOGIN", "admin", "SUCCESS", "Session obtained")
        
        success_count = 0
        for username in self.target_users:
            try:
                delete_data = {'username': username}
                response = session.post(
                    f"{self.base_url}/auto_hard_delete_user",
                    json=delete_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.log_action("HARD_DELETE", username, "SUCCESS", result.get('message', ''))
                        success_count += 1
                    else:
                        self.log_action("HARD_DELETE", username, "FAILED", result.get('error', ''))
                else:
                    self.log_action("HARD_DELETE", username, "FAILED", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_action("HARD_DELETE", username, "ERROR", str(e))
        
        return success_count == len(self.target_users)
    
    def create_deployment_script(self):
        """Create deployment script for the endpoint"""
        script_content = '''#!/usr/bin/env python3
"""
Deployment Script for Hard Delete Endpoint
"""

import requests
import json

def deploy_endpoint():
    """Deploy hard delete endpoint to production"""
    
    # This would need to be done through proper deployment channels
    # For now, we'll provide the code that needs to be added
    
    endpoint_code = """
@app.route('/auto_hard_delete_user', methods=['POST'])
@admin_required
@database_required
def auto_hard_delete_user():
    \"\"\"Automatic hard delete user from database\"\"\"
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'error': 'Username required'})
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Delete all deliveries created by this user
        from app import Delivery
        deliveries_to_delete = Delivery.query.filter_by(created_by=user.id).all()
        delivery_count = len(deliveries_to_delete)
        
        for delivery in deliveries_to_delete:
            db.session.delete(delivery)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'User {username} and {delivery_count} deliveries hard deleted'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
"""
    
    print("Add this endpoint to app.py:")
    print(endpoint_code)
    print("\\nThen redeploy the application to production")

if __name__ == "__main__":
    deploy_endpoint()
'''
        
        with open('deploy_hard_delete.py', 'w') as f:
            f.write(script_content)
        
        self.log_action("CREATE", "script", "SUCCESS", "Deployment script created")
    
    def run_auto_hard_delete(self):
        """Run complete automatic hard delete process"""
        print("🚨 AUTOMATIC HARD DELETE - PRODUCTION")
        print("=" * 60)
        print(f"Target users: {', '.join(self.target_users)}")
        print(f"Production: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Step 1: Create deployment script
        self.create_deployment_script()
        
        # Step 2: Deploy endpoint (simulation)
        endpoint_code = self.deploy_hard_delete_endpoint()
        
        # Step 3: Execute hard delete
        success = self.execute_hard_delete()
        
        # Step 4: Generate report
        self.generate_report(success)
        
        return success
    
    def generate_report(self, success):
        """Generate automatic hard delete report"""
        print("\n" + "=" * 60)
        print("📊 AUTOMATIC HARD DELETE REPORT")
        print("=" * 60)
        
        if success:
            print("🎉 SUCCESS: All target users hard deleted from production")
        else:
            print("⚠️  INCOMPLETE: Manual deployment required")
        
        print(f"Target users: {len(self.target_users)}")
        print("\n📋 Detailed Log:")
        for entry in self.deletion_log:
            status_icon = "✅" if entry['status'] in ["SUCCESS", "COMPLETED"] else "❌" if entry['status'] == "FAILED" else "⚠️"
            print(f"{status_icon} [{entry['timestamp']}] {entry['action']} - {entry['user']} - {entry['status']} {entry['details']}")
        
        # Save report
        report_file = f"AUTO_HARD_DELETE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(f"AUTOMATIC HARD DELETE REPORT\\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"Environment: {self.base_url}\\n")
            f.write(f"Target users: {', '.join(self.target_users)}\\n")
            f.write(f"Success: {success}\\n\\n")
            
            f.write("DETAILED LOG:\\n")
            for entry in self.deletion_log:
                f.write(f"[{entry['timestamp']}] {entry['action']} - {entry['user']} - {entry['status']} - {entry['details']}\\n")
        
        print(f"\\n📄 Report saved to: {report_file}")

def main():
    """Main execution"""
    print("🚨 AUTOMATIC HARD DELETE - PRODUCTION USERS")
    print("=" * 50)
    print("⚠️  This will automatically hard delete users from production")
    print("⚠️  Users to delete: ben, peter, tom")
    print("=" * 50)
    
    # Confirmation
    confirm = input("Type 'AUTO-HARD-DELETE' to confirm: ").strip()
    if confirm != 'AUTO-HARD-DELETE':
        print("❌ Operation cancelled")
        return
    
    deleter = AutoHardDelete()
    success = deleter.run_auto_hard_delete()
    
    if success:
        print("\\n🎉 AUTOMATIC HARD DELETE SUCCESSFUL")
    else:
        print("\\n⚠️  MANUAL DEPLOYMENT REQUIRED - See deploy_hard_delete.py")

if __name__ == "__main__":
    main()
