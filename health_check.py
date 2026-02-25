import requests

def check_production_health():
    try:
        print("🔍 Checking production health endpoint...")
        response = requests.get('https://errantmate.onrender.com/api/health', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Production Health:")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # Check routes
            routes = data.get('routes_registered', [])
            user_routes = [r for r in routes if 'user' in r.lower()]
            
            print(f"\n📊 User-related routes ({len(user_routes)}):")
            for route in user_routes:
                print(f"  - {route}")
                
            # Check for wrong endpoints
            wrong_routes = [r for r in routes if '/api/users' in r]
            if wrong_routes:
                print(f"\n🚨 WRONG ENDPOINTS FOUND: {wrong_routes}")
            else:
                print(f"\n✅ No wrong /api/users endpoints found")
                
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_production_health()
