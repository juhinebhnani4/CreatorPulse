"""Quick test of content routes."""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("Testing Content Routes:")
print("=" * 50)

# Test 1: GET should return 405
resp = client.get('/api/v1/content/scrape')
print(f"GET /api/v1/content/scrape: {resp.status_code} (expect 405)")

# Test 2: POST without auth should return 401 or 403
resp = client.post('/api/v1/content/scrape', json={'workspace_id': 'test'})
print(f"POST /api/v1/content/scrape (no auth): {resp.status_code} (expect 401/403)")
print(f"Response: {resp.json()}")

# Test 3: Check if route exists at all
print("\n Registered content routes:")
for route in app.routes:
    if hasattr(route, 'path') and 'content' in route.path:
        methods = ','.join(route.methods) if hasattr(route, 'methods') and route.methods else ''
        print(f"  {methods:10} {route.path}")
