"""
Test Sprint 1 API endpoints (Auth + Workspaces).
Run this to verify all endpoints are working.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_sprint1():
    """Test all Sprint 1 endpoints."""
    print("=" * 60)
    print("Testing Sprint 1: Auth & Workspaces")
    print("=" * 60)

    # Test 1: Health check
    print("\n[1/10] Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["success"] == True
    print("✅ Health check passed")

    # Test 2: Signup
    print("\n[2/10] Testing signup...")
    email = f"test_{datetime.now().timestamp()}@example.com"  # Unique email
    signup_data = {
        "email": email,
        "password": "password123",
        "username": "testuser"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)

    if response.status_code == 200:
        data = response.json()
        assert data["success"] == True
        assert "token" in data["data"]
        token = data["data"]["token"]
        user_id = data["data"]["user_id"]
        print(f"✅ Signup successful! User ID: {user_id[:8]}...")
    else:
        print(f"❌ Signup failed: {response.json()}")
        return

    # Test 3: Login
    print("\n[3/10] Testing login...")
    login_data = {
        "email": email,
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "token" in data["data"]
    print("✅ Login successful!")

    # Test 4: Get current user
    print("\n[4/10] Testing get current user...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == email
    print(f"✅ Got user: {data['data']['username']}")

    # Test 5: Create workspace
    print("\n[5/10] Testing create workspace...")
    workspace_data = {
        "name": f"Test Workspace {datetime.now().timestamp()}",
        "description": "Auto-generated test workspace"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/workspaces",
        headers=headers,
        json=workspace_data
    )
    assert response.status_code == 201
    data = response.json()
    workspace_id = data["data"]["id"]
    print(f"✅ Workspace created! ID: {workspace_id[:8]}...")

    # Test 6: List workspaces
    print("\n[6/10] Testing list workspaces...")
    response = requests.get(f"{BASE_URL}/api/v1/workspaces", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["count"] >= 1
    print(f"✅ Found {data['data']['count']} workspace(s)")

    # Test 7: Get workspace
    print("\n[7/10] Testing get workspace...")
    response = requests.get(
        f"{BASE_URL}/api/v1/workspaces/{workspace_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == workspace_id
    print(f"✅ Got workspace: {data['data']['name']}")

    # Test 8: Update workspace
    print("\n[8/10] Testing update workspace...")
    update_data = {
        "description": "Updated description"
    }
    response = requests.put(
        f"{BASE_URL}/api/v1/workspaces/{workspace_id}",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 200
    print("✅ Workspace updated!")

    # Test 9: Get workspace config
    print("\n[9/10] Testing get workspace config...")
    response = requests.get(
        f"{BASE_URL}/api/v1/workspaces/{workspace_id}/config",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "config" in data["data"]
    print("✅ Got workspace config")

    # Test 10: Save workspace config
    print("\n[10/10] Testing save workspace config...")
    config_data = {
        "config": {
            "reddit": {"enabled": True, "limit": 25},
            "rss": {"enabled": False}
        }
    }
    response = requests.put(
        f"{BASE_URL}/api/v1/workspaces/{workspace_id}/config",
        headers=headers,
        json=config_data
    )
    assert response.status_code == 200
    print("✅ Workspace config saved!")

    # Cleanup: Delete workspace
    print("\n[CLEANUP] Deleting test workspace...")
    response = requests.delete(
        f"{BASE_URL}/api/v1/workspaces/{workspace_id}",
        headers=headers
    )
    assert response.status_code == 200
    print("✅ Workspace deleted!")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Sprint 1 Backend is working!")
    print("=" * 60)
    print(f"\nTest Summary:")
    print(f"  - Email: {email}")
    print(f"  - User ID: {user_id}")
    print(f"  - Workspace ID: {workspace_id}")
    print(f"  - All 10 tests passed ✅")
    print(f"\nNext: Build Streamlit frontend (Sprint 1 part 2)")


if __name__ == "__main__":
    try:
        test_sprint1()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend.")
        print("Make sure the server is running:")
        print('  cd "e:\\Career coaching\\100x\\scraper-scripts"')
        print('  .venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload')
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
