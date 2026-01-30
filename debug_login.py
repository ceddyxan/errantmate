#!/usr/bin/env python3
"""
Test login without JavaScript interference
"""

import requests

def test_simple_login():
    """Test login with minimal form data"""
    login_url = 'http://localhost:5000/login'
    
    try:
        session = requests.Session()
        
        # Get login page
        response = session.get(login_url)
        print(f'Login page status: {response.status_code}')
        
        # Test with minimal form data
        login_data = {
            'username': 'admin',
            'password': 'ErrantMate@24!'
        }
        
        # Add headers to mimic browser
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = session.post(login_url, data=login_data, headers=headers, allow_redirects=False)
        print(f'Login POST status: {response.status_code}')
        print(f'Headers: {dict(response.headers)}')
        
        # Check if there are any flash messages in the response
        if 'Invalid username or password' in response.text:
            print('Login failed - Invalid credentials message found')
        elif 'Signing in' in response.text:
            print('Login form is being processed but button disabled')
        else:
            print('No obvious error messages found')
            
        # Save response to file for debugging
        with open('login_response.html', 'w') as f:
            f.write(response.text)
        print('Response saved to login_response.html for inspection')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_simple_login()
