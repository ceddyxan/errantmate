#!/usr/bin/env python3
"""
Test login with curl-like headers
"""

import requests

def test_login_curl_like():
    # Test a simple GET request first
    response = requests.get('http://127.0.0.1:5000/login')
    print(f'GET status: {response.status_code}')
    
    # Test POST with curl-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    response = requests.post('http://127.0.0.1:5000/login', 
                           data='username=admin&password=ErrantMate@24!',
                           headers=headers,
                           allow_redirects=False)
    print(f'POST status: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type")}')

if __name__ == '__main__':
    test_login_curl_like()
