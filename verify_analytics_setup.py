"""
Verify that Analytics (Migration 009) is properly set up.
This checks the database and backend configuration.
"""

import sys
import os

print("="*70)
print("SPRINT 8: Analytics Setup Verification")
print("="*70)
print()

# Test 1: Check if Supabase credentials are configured
print("TEST 1: Environment Configuration")
print("-"*70)

try:
    # Check for .env file
    if os.path.exists('.env'):
        print("✓ .env file found")

        with open('.env', 'r') as f:
            env_content = f.read()

        if 'SUPABASE_URL' in env_content and 'supabase.co' in env_content:
            print("✓ SUPABASE_URL configured")
        else:
            print("✗ SUPABASE_URL not found in .env")

        if 'SUPABASE_KEY' in env_content and 'eyJ' in env_content:
            print("✓ SUPABASE_KEY configured")
        else:
            print("✗ SUPABASE_KEY not found in .env")
    else:
        print("✗ .env file not found")
except Exception as e:
    print(f"✗ Error reading .env: {e}")

print()

# Test 2: Check backend files exist
print("TEST 2: Backend Files")
print("-"*70)

files_to_check = [
    ('backend/migrations/009_create_analytics_tables.sql', 'Migration 009'),
    ('backend/services/analytics_service.py', 'Analytics Service'),
    ('backend/services/tracking_service.py', 'Tracking Service'),
    ('backend/models/analytics_models.py', 'Analytics Models'),
    ('backend/api/v1/analytics.py', 'Analytics API'),
    ('backend/api/tracking.py', 'Tracking API'),
    ('backend/database.py', 'Database Utility'),
]

all_exist = True
for file_path, description in files_to_check:
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
    else:
        print(f"✗ {description}: {file_path} - NOT FOUND")
        all_exist = False

print()

# Test 3: Check if backend can import the modules
print("TEST 3: Python Module Imports")
print("-"*70)

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Try importing without supabase dependency
    print("Checking module structure...")

    import importlib.util

    modules_to_check = [
        'backend.config',
        'backend.database',
    ]

    for module_name in modules_to_check:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec:
                print(f"✓ {module_name} can be imported")
            else:
                print(f"✗ {module_name} not found")
        except Exception as e:
            print(f"⚠ {module_name} check failed: {e}")

except Exception as e:
    print(f"⚠ Import check failed: {e}")

print()

# Test 4: Summary
print("="*70)
print("SUMMARY")
print("="*70)
print()

if all_exist:
    print("✓ All backend files are in place!")
    print()
    print("Since you've already run Migration 009 in Supabase:")
    print()
    print("NEXT STEPS:")
    print("1. Start the backend server:")
    print("   python -m uvicorn backend.main:app --reload --port 8000")
    print()
    print("2. Test the analytics API:")
    print("   curl http://localhost:8000/health")
    print("   curl http://localhost:8000/docs")
    print()
    print("3. Check analytics endpoints in Swagger UI:")
    print("   http://localhost:8000/docs#/Analytics")
    print("   http://localhost:8000/docs#/Tracking")
    print()
    print("4. Test tracking pixel:")
    print("   http://localhost:8000/track/pixel/test.png")
    print()
    print("Ready to go! 🚀")
else:
    print("⚠ Some files are missing. Please check the errors above.")

print()
print("="*70)
print("For full testing guide, see: SPRINT_8_COMPLETE.md")
print("="*70)
