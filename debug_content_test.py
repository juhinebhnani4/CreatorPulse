"""Debug why content test returns 404."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from backend.main import app
import json

# Create client
client = TestClient(app)

# Create test user
signup_resp = client.post("/api/v1/auth/signup", json={
    "email": "debugtest@example.com",
    "username": "debuguser",
    "password": "TestPass123!"
})

print(f"Signup: {signup_resp.status_code}")
if signup_resp.status_code == 200:
    token = signup_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create workspace
    workspace_resp = client.post("/api/v1/workspaces", headers=headers, json={
        "name": "Debug Workspace",
        "description": "Test"
    })
    print(f"Workspace: {workspace_resp.status_code}")

    if workspace_resp.status_code == 201:
        workspace_id = workspace_resp.json()["data"]["id"]

        # Try scraping
        scrape_resp = client.post("/api/v1/content/scrape", headers=headers, json={
            "workspace_id": workspace_id,
            "sources": ["reddit"],
            "limit_per_source": 5
        })

        print(f"\nScrape Response:")
        print(f"Status: {scrape_resp.status_code}")
        print(f"Body: {json.dumps(scrape_resp.json(), indent=2)}")
