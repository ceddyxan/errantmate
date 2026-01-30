#!/usr/bin/env python3
"""
Test Login Form Submission
Test the actual login form submission to the running server
"""

import requests

def test_form_login():
    """Test login form submission"""
    login_url = 'http://localhost:5000/login'
    
    try:
        # Test admin login
        session = requests.Session()
        
        # First get the login page
        response = session.get(login_url)
        print(f'Login page status: {response.status_code}')
        
        # Test admin login
        login_data = {
            'username': 'admin',
            'password': 'ErrantMate@24!'
        }
        
        response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f'Admin login POST status: {response.status_code}')
        print(f'Location header: {response.headers.get("Location", "None")}')
        
        if response.status_code == 302:
            print('Admin login successful - redirect detected')
            # Follow redirect
            redirect_response = session.get(response.headers['Location'])
            print(f'Redirect status: {redirect_response.status_code}')
            print(f'Redirect URL: {response.headers["Location"]}')
        else:
            print('Admin login failed or returned different status')
            print(f'Response preview: {response.text[:300]}...')
            
        # Test regular user login
        session2 = requests.Session()
        response2 = session2.get(login_url)
        
        user_login_data = {
            'username': 'directtest2',
            'password': 'User123@'
        }
        
        response2 = session2.post(login_url, data=user_login_data, allow_redirects=False)
        print(f'\\nUser login POST status: {response2.status_code}')
        print(f'Location header: {response2.headers.get("Location", "None")}')
        
        if response2.status_code == 302:
            print('User login successful - redirect detected')
        else:
            print('User login failed or returned different status')
            print(f'Response preview: {response2.text[:300]}...')
            
    except requests.exceptions.ConnectionError:
        print('Cannot connect to server. Make sure the Flask app is running on localhost:5000')
    except Exception as e:
        print(f'Error testing login: {e}')

if __name__ == '__main__':
    test_form_login()
