"""
Sprint 8 Structure Test - Verify all files and code structure are correct.
This test doesn't require database connection or packages to be installed.
"""

import os
import sys
from pathlib import Path

def test_file_exists(file_path, description):
    """Check if a file exists."""
    full_path = Path(file_path)
    exists = full_path.exists()
    status = "[PASS]" if exists else "[FAIL]"
    print(f"{status} {description}: {file_path}")
    return exists

def test_file_contains(file_path, search_string, description):
    """Check if a file contains a specific string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            contains = search_string in content
            status = "[PASS]" if contains else "[FAIL]"
            print(f"{status} {description}")
            return contains
    except Exception as e:
        print(f"[FAIL] {description}: {e}")
        return False

def main():
    print("="*70)
    print("SPRINT 8: ANALYTICS & ENGAGEMENT TRACKING - STRUCTURE TEST")
    print("="*70)
    print()

    results = []

    # Test 1: Database Migration
    print("TEST 1: Database Migration File")
    print("-"*70)
    results.append(test_file_exists(
        "backend/migrations/009_create_analytics_tables.sql",
        "Migration 009 file"
    ))
    results.append(test_file_contains(
        "backend/migrations/009_create_analytics_tables.sql",
        "CREATE TABLE email_analytics_events",
        "Contains email_analytics_events table"
    ))
    results.append(test_file_contains(
        "backend/migrations/009_create_analytics_tables.sql",
        "CREATE TABLE newsletter_analytics_summary",
        "Contains newsletter_analytics_summary table"
    ))
    results.append(test_file_contains(
        "backend/migrations/009_create_analytics_tables.sql",
        "CREATE TABLE content_performance",
        "Contains content_performance table"
    ))
    print()

    # Test 2: Analytics Service
    print("TEST 2: Analytics Service")
    print("-"*70)
    results.append(test_file_exists(
        "backend/services/analytics_service.py",
        "Analytics service file"
    ))
    results.append(test_file_contains(
        "backend/services/analytics_service.py",
        "class AnalyticsService",
        "Contains AnalyticsService class"
    ))
    results.append(test_file_contains(
        "backend/services/analytics_service.py",
        "async def record_event",
        "Has record_event method"
    ))
    results.append(test_file_contains(
        "backend/services/analytics_service.py",
        "async def get_newsletter_analytics",
        "Has get_newsletter_analytics method"
    ))
    results.append(test_file_contains(
        "backend/services/analytics_service.py",
        "async def get_workspace_analytics",
        "Has get_workspace_analytics method"
    ))
    print()

    # Test 3: Tracking Service
    print("TEST 3: Tracking Service")
    print("-"*70)
    results.append(test_file_exists(
        "backend/services/tracking_service.py",
        "Tracking service file"
    ))
    results.append(test_file_contains(
        "backend/services/tracking_service.py",
        "class TrackingService",
        "Contains TrackingService class"
    ))
    results.append(test_file_contains(
        "backend/services/tracking_service.py",
        "def generate_tracking_pixel_url",
        "Has generate_tracking_pixel_url method"
    ))
    results.append(test_file_contains(
        "backend/services/tracking_service.py",
        "def generate_tracked_link",
        "Has generate_tracked_link method"
    ))
    results.append(test_file_contains(
        "backend/services/tracking_service.py",
        "def add_tracking_to_html",
        "Has add_tracking_to_html method"
    ))
    print()

    # Test 4: Analytics Models
    print("TEST 4: Analytics Models")
    print("-"*70)
    results.append(test_file_exists(
        "backend/models/analytics_models.py",
        "Analytics models file"
    ))
    results.append(test_file_contains(
        "backend/models/analytics_models.py",
        "class EmailEventCreate",
        "Contains EmailEventCreate model"
    ))
    results.append(test_file_contains(
        "backend/models/analytics_models.py",
        "class NewsletterAnalyticsResponse",
        "Contains NewsletterAnalyticsResponse model"
    ))
    results.append(test_file_contains(
        "backend/models/analytics_models.py",
        "class WorkspaceAnalyticsResponse",
        "Contains WorkspaceAnalyticsResponse model"
    ))
    print()

    # Test 5: Analytics API
    print("TEST 5: Analytics API Endpoints")
    print("-"*70)
    results.append(test_file_exists(
        "backend/api/v1/analytics.py",
        "Analytics API file"
    ))
    results.append(test_file_contains(
        "backend/api/v1/analytics.py",
        "@router.post",
        "Has POST endpoints"
    ))
    results.append(test_file_contains(
        "backend/api/v1/analytics.py",
        "async def record_analytics_event",
        "Has record_analytics_event endpoint"
    ))
    results.append(test_file_contains(
        "backend/api/v1/analytics.py",
        "async def get_newsletter_analytics",
        "Has get_newsletter_analytics endpoint"
    ))
    results.append(test_file_contains(
        "backend/api/v1/analytics.py",
        "async def get_workspace_analytics_summary",
        "Has get_workspace_analytics_summary endpoint"
    ))
    results.append(test_file_contains(
        "backend/api/v1/analytics.py",
        "async def export_analytics_data",
        "Has export_analytics_data endpoint"
    ))
    print()

    # Test 6: Tracking API
    print("TEST 6: Tracking API Endpoints")
    print("-"*70)
    results.append(test_file_exists(
        "backend/api/tracking.py",
        "Tracking API file"
    ))
    results.append(test_file_contains(
        "backend/api/tracking.py",
        "async def track_email_open",
        "Has track_email_open endpoint"
    ))
    results.append(test_file_contains(
        "backend/api/tracking.py",
        "async def track_link_click",
        "Has track_link_click endpoint"
    ))
    results.append(test_file_contains(
        "backend/api/tracking.py",
        "async def unsubscribe_page",
        "Has unsubscribe_page endpoint"
    ))
    results.append(test_file_contains(
        "backend/api/tracking.py",
        "TRACKING_PIXEL_PNG",
        "Has tracking pixel data"
    ))
    print()

    # Test 7: Main App Integration
    print("TEST 7: Main App Integration")
    print("-"*70)
    results.append(test_file_contains(
        "backend/main.py",
        "from backend.api.v1 import analytics",
        "Imports analytics router"
    ))
    results.append(test_file_contains(
        "backend/main.py",
        "from backend.api import tracking",
        "Imports tracking router"
    ))
    results.append(test_file_contains(
        "backend/main.py",
        'app.include_router(analytics.router',
        "Includes analytics router"
    ))
    results.append(test_file_contains(
        "backend/main.py",
        'app.include_router(tracking.router',
        "Includes tracking router"
    ))
    print()

    # Test 8: Documentation
    print("TEST 8: Documentation")
    print("-"*70)
    results.append(test_file_exists(
        "SPRINT_8_ANALYTICS_TRACKING.md",
        "Sprint 8 planning document"
    ))
    results.append(test_file_exists(
        "SPRINT_8_COMPLETE.md",
        "Sprint 8 completion document"
    ))
    print()

    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    print()

    if passed == total:
        print("[SUCCESS] All structure tests passed!")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install supabase beautifulsoup4")
        print("2. Configure .env file with SUPABASE_URL and SUPABASE_KEY")
        print("3. Run migration: psql < backend/migrations/009_create_analytics_tables.sql")
        print("4. Start backend: python -m uvicorn backend.main:app --reload")
        print("5. Test endpoints using the examples in SPRINT_8_COMPLETE.md")
    else:
        print("[WARNING] Some structure tests failed!")
        print("Please review the failed tests above.")

    print()
    print("="*70)

if __name__ == "__main__":
    main()
