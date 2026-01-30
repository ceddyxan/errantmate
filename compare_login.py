#!/usr/bin/env python3
"""
Compare test client vs requests
"""

from app import app
import requests

def compare_login_methods():
    with app.test_client() as client:
        # Test with Flask test client
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'ErrantMate@24!'
        }, follow_redirects=False)
        print(f'Flask test client POST status: {response.status_code}')
        print(f'Flask test client location: {response.location}')
        
        # Test with requests
        session = requests.Session()
        response = session.post('http://localhost:5000/login', data={
            'username': 'admin',
            'password': 'ErrantMate@24!'
        }, allow_redirects=False)
        print(f'Requests POST status: {response.status_code}')
        print(f'Requests location: {response.headers.get("Location", "None")}')

if __name__ == '__main__':
    compare_login_methods()
