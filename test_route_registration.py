"""Quick script to check if content routes are registered."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.main import app

# Get all routes
print("=== All Registered Routes ===\n")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ','.join(route.methods) if route.methods else 'N/A'
        print(f"{methods:10} {route.path}")

# Filter content routes
print("\n=== Content Routes ===\n")
content_routes = [r for r in app.routes if hasattr(r, 'path') and 'content' in r.path.lower()]
if content_routes:
    for route in content_routes:
        methods = ','.join(route.methods) if hasattr(route, 'methods') and route.methods else 'N/A'
        print(f"{methods:10} {route.path}")
else:
    print("NO CONTENT ROUTES FOUND!")

print(f"\nTotal routes: {len([r for r in app.routes if hasattr(r, 'path')])}")
print(f"Content routes: {len(content_routes)}")
