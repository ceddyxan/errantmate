import requests

def check_debug_response():
    try:
        print("🔍 Checking debug endpoint raw response...")
        response = requests.get('https://errantmate.onrender.com/debug/check_users', timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Raw Response: {repr(response.text[:500])}")
        
        if response.status_code == 200:
            try:
                import json
                data = response.json()
                print(f"\n✅ Parsed JSON: {json.dumps(data, indent=2)}")
            except:
                print("❌ Response is not valid JSON")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_debug_response()
