import httpx
import sys

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    print("--- Starting Auth Verification ---")
    
    # 1. Register (or Login if exists) to get token
    email = "test_auth_user" # Using name field as username
    password = "password123"
    
    print(f"1. Attempting Register/Login for user: {email}")
    payload = {"name": email, "password": password}
    
    # Try register first
    response = httpx.post(f"{BASE_URL}/register", json=payload)
    if response.status_code == 400: # Already exists
        print("   User exists, logging in...")
        response = httpx.post(f"{BASE_URL}/login", json=payload)
    
    if response.status_code != 200:
        print(f"FAILED: Could not register/ignore. Status: {response.status_code}, Body: {response.text}")
        sys.exit(1)
        
    data = response.json()
    if "access_token" not in data:
         print(f"FAILED: No access_token in response. Body: {data}")
         sys.exit(1)
         
    token = data["access_token"]
    print("   SUCCESS: Got access token.")
    
    # 2. Access Protected Route WITHOUT Token
    print("2. Testing Protected Route (No Token)...")
    try:
        # Using a simple GET route that requires auth. 
        # list_materials uses Depends(get_current_user)
        # We need the user's ID for correct logic, but if we don't send token, it should fail at Dependency.
        resp = httpx.get(f"{BASE_URL}/materials")
    except Exception as e:
         print(f"   Request failed: {e}")
         
    if resp.status_code == 401 or resp.status_code == 403:
        print("   SUCCESS: Request denied as expected.")
    else:
        print(f"FAILED: Request should have been denied. Status: {resp.status_code}")
        sys.exit(1)

    # 3. Access Protected Route WITH Token
    print("3. Testing Protected Route (With Token)...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = httpx.get(f"{BASE_URL}/materials", headers=headers)
    
    if resp.status_code == 200:
        print("   SUCCESS: Request authorized.")
        print(f"   Materials: {resp.json()}")
    else:
        print(f"FAILED: Authorized request failed. Status: {resp.status_code}, Body: {resp.text}")
        sys.exit(1)
        
    print("--- Verification PASSED ---")

if __name__ == "__main__":
    test_auth_flow()
