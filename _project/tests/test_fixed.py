import requests

BASE_URL = "http://127.0.0.1:8000"

def test_fixed_endpoints():
    print("=== PROBANDO ENDPOINTS CORREGIDOS ===")
    
    endpoints = [
        ("GET", "/api/auth/users/", "Listar usuarios"),
        ("GET", "/api/schema/", "Schema OpenAPI"),
    ]
    
    for method, path, desc in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"⚠️ {response.status_code}"
            print(f"{status} [{method}] {path} - {desc}")
            
            if response.status_code != 200:
                print(f"   Error: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ ERROR [{method}] {path} - {desc}")
            print(f"   Exception: {str(e)}")

if __name__ == "__main__":
    test_fixed_endpoints()