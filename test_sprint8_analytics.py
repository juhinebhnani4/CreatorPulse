"""
Test Script for Sprint 8: Analytics & Engagement Tracking

This script tests:
1. Database connection
2. Analytics service functionality
3. Tracking service functionality
4. API endpoints (requires server running)
"""

import sys
import os
import json
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test 1: Verify database connection and check if analytics tables exist."""
    print("\n" + "="*70)
    print("TEST 1: Database Connection & Tables")
    print("="*70)

    try:
        from backend.database import get_supabase_client
        supabase = get_supabase_client()

        print("✓ Supabase client initialized")

        # Check if analytics tables exist by querying them
        tables_to_check = [
            "email_analytics_events",
            "newsletter_analytics_summary",
            "content_performance"
        ]

        for table in tables_to_check:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"✓ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"✗ Table '{table}' error: {str(e)}")
                return False

        return True

    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("\nPlease ensure:")
        print("1. SUPABASE_URL and SUPABASE_KEY are set in .env")
        print("2. Migration 009 has been run on the database")
        return False


def test_analytics_service():
    """Test 2: Test analytics service functions."""
    print("\n" + "="*70)
    print("TEST 2: Analytics Service")
    print("="*70)

    try:
        from backend.services.analytics_service import AnalyticsService

        analytics = AnalyticsService()
        print("✓ AnalyticsService initialized")

        # Test methods exist
        methods = [
            'record_event',
            'get_newsletter_analytics',
            'get_workspace_analytics',
            'get_content_performance',
            'export_analytics_data'
        ]

        for method in methods:
            if hasattr(analytics, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing")
                return False

        return True

    except Exception as e:
        print(f"✗ Analytics service error: {str(e)}")
        return False


def test_tracking_service():
    """Test 3: Test tracking service functions."""
    print("\n" + "="*70)
    print("TEST 3: Tracking Service")
    print("="*70)

    try:
        from backend.services.tracking_service import TrackingService

        tracking = TrackingService()
        print("✓ TrackingService initialized")

        # Test generating tracking pixel URL
        test_newsletter_id = uuid4()
        test_email = "test@example.com"
        test_workspace_id = uuid4()

        pixel_url = tracking.generate_tracking_pixel_url(
            test_newsletter_id,
            test_email,
            test_workspace_id
        )

        if "/track/pixel/" in pixel_url and pixel_url.endswith(".png"):
            print(f"✓ Tracking pixel URL generated")
            print(f"  URL: {pixel_url[:80]}...")
        else:
            print(f"✗ Invalid tracking pixel URL: {pixel_url}")
            return False

        # Test generating tracked link
        original_url = "https://example.com/article"
        tracked_url = tracking.generate_tracked_link(
            original_url,
            test_newsletter_id,
            test_email,
            test_workspace_id
        )

        if "utm_source" in tracked_url or "/track/click/" in tracked_url:
            print(f"✓ Tracked link generated")
            print(f"  Original: {original_url}")
            print(f"  Tracked: {tracked_url[:80]}...")
        else:
            print(f"✗ Invalid tracked link: {tracked_url}")
            return False

        # Test decoding tracking params
        try:
            # Extract encoded part from pixel URL
            encoded = pixel_url.split("/track/pixel/")[1].replace(".png", "")
            decoded = tracking.decode_tracking_params(encoded)

            if decoded.get("r") == test_email:
                print(f"✓ Tracking params decode correctly")
            else:
                print(f"✗ Decoded params don't match")
                return False
        except Exception as e:
            print(f"✗ Error decoding params: {str(e)}")
            return False

        return True

    except Exception as e:
        print(f"✗ Tracking service error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_models():
    """Test 4: Test analytics models."""
    print("\n" + "="*70)
    print("TEST 4: Analytics Models")
    print("="*70)

    try:
        from backend.models.analytics_models import (
            EmailEventCreate,
            NewsletterMetrics,
            NewsletterRates,
            WorkspaceAggregateMetrics
        )

        print("✓ All analytics models imported successfully")

        # Test creating an event
        event = EmailEventCreate(
            workspace_id=uuid4(),
            newsletter_id=uuid4(),
            event_type="opened",
            recipient_email="test@example.com"
        )
        print(f"✓ EmailEventCreate model works")

        # Test metrics model
        metrics = NewsletterMetrics(
            sent_count=100,
            delivered_count=98,
            opened_count=50,
            unique_opens=45
        )
        print(f"✓ NewsletterMetrics model works")

        return True

    except Exception as e:
        print(f"✗ Models error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_record_test_event():
    """Test 5: Record a test analytics event."""
    print("\n" + "="*70)
    print("TEST 5: Record Test Analytics Event")
    print("="*70)

    try:
        from backend.services.analytics_service import AnalyticsService
        from backend.database import get_supabase_client
        import asyncio

        # First, we need a valid workspace and newsletter
        # Let's check if there are any workspaces
        supabase = get_supabase_client()
        workspaces = supabase.table("workspaces").select("id").limit(1).execute()

        if not workspaces.data:
            print("⚠ No workspaces found in database")
            print("  Please create a workspace first")
            return None

        workspace_id = workspaces.data[0]["id"]
        print(f"✓ Using workspace: {workspace_id}")

        # Check for newsletters
        newsletters = supabase.table("newsletters").select("id").eq("workspace_id", workspace_id).limit(1).execute()

        if not newsletters.data:
            print("⚠ No newsletters found")
            print("  Creating a test newsletter...")

            # Create a test newsletter
            test_newsletter = supabase.table("newsletters").insert({
                "workspace_id": workspace_id,
                "title": "Test Newsletter for Analytics",
                "status": "sent",
                "html_content": "<h1>Test</h1>",
                "plain_text_content": "Test"
            }).execute()

            if test_newsletter.data:
                newsletter_id = test_newsletter.data[0]["id"]
                print(f"✓ Created test newsletter: {newsletter_id}")
            else:
                print(f"✗ Failed to create test newsletter")
                return False
        else:
            newsletter_id = newsletters.data[0]["id"]
            print(f"✓ Using newsletter: {newsletter_id}")

        # Record a test event
        analytics = AnalyticsService()

        async def record_event():
            result = await analytics.record_event(
                workspace_id=workspace_id,
                newsletter_id=newsletter_id,
                event_type="opened",
                recipient_email="test@example.com",
                user_agent="Mozilla/5.0 (Test)",
                ip_address="192.168.1.100"
            )
            return result

        result = asyncio.run(record_event())

        if result:
            print(f"✓ Test event recorded successfully")
            print(f"  Event ID: {result.get('id')}")
            print(f"  Event Type: {result.get('event_type')}")
            print(f"  Recipient: {result.get('recipient_email')}")
            return True
        else:
            print(f"✗ Failed to record event")
            return False

    except Exception as e:
        print(f"✗ Error recording event: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def print_manual_tests():
    """Print manual test instructions."""
    print("\n" + "="*70)
    print("MANUAL TESTS (Run these separately)")
    print("="*70)

    print("""
To test the API endpoints, follow these steps:

1. START THE BACKEND SERVER:
   cd backend
   python -m uvicorn backend.main:app --reload --port 8000

2. GET AN AUTH TOKEN:
   POST http://localhost:8000/api/v1/auth/login
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }

   Save the "access_token" from the response.

3. TEST TRACKING PIXEL:
   # Open in browser (should return 1x1 PNG):
   http://localhost:8000/track/pixel/[encoded_params].png

   # Generate encoded_params using Python:
   import base64, json
   params = {"n": "newsletter-id", "r": "test@example.com", "w": "workspace-id"}
   encoded = base64.urlsafe_b64encode(json.dumps(params).encode()).decode()
   print(f"http://localhost:8000/track/pixel/{encoded}.png")

4. TEST CLICK TRACKING:
   # Open in browser (should redirect to target URL):
   http://localhost:8000/track/click/[encoded_params]

   # Generate encoded_params:
   params = {"n": "newsletter-id", "r": "test@example.com", "w": "workspace-id", "u": "https://example.com"}
   encoded = base64.urlsafe_b64encode(json.dumps(params).encode()).decode()
   print(f"http://localhost:8000/track/click/{encoded}")

5. TEST ANALYTICS ENDPOINTS:
   # Get newsletter analytics:
   GET http://localhost:8000/api/v1/analytics/newsletters/{newsletter_id}
   Header: Authorization: Bearer {your_token}

   # Get workspace summary:
   GET http://localhost:8000/api/v1/analytics/workspaces/{workspace_id}/summary
   Header: Authorization: Bearer {your_token}

   # Export analytics:
   GET http://localhost:8000/api/v1/analytics/workspaces/{workspace_id}/export?format=csv
   Header: Authorization: Bearer {your_token}

6. CHECK DATABASE:
   # Verify events were recorded:
   SELECT * FROM email_analytics_events ORDER BY created_at DESC LIMIT 10;

   # Check summary was calculated:
   SELECT * FROM newsletter_analytics_summary;
""")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("SPRINT 8: ANALYTICS & ENGAGEMENT TRACKING - TEST SUITE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Analytics Service", test_analytics_service()))
    results.append(("Tracking Service", test_tracking_service()))
    results.append(("Analytics Models", test_api_models()))

    # Optional: Record test event (requires database access)
    try:
        result = test_record_test_event()
        if result is not None:
            results.append(("Record Test Event", result))
    except Exception as e:
        print(f"\nSkipping test event recording: {str(e)}")

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Analytics system is working correctly.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")

    # Print manual test instructions
    print_manual_tests()

    print("\n" + "="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    main()
