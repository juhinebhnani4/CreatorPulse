"""
Test script for Sprint 7: Feedback & Learning API endpoints.

Tests all 10+ feedback-related endpoints:
1. Record content item feedback (positive/negative)
2. List feedback items with filters
3. Record newsletter feedback
4. Get newsletter feedback
5. List newsletter feedback
6. Get source quality scores
7. Get content preferences
8. Get feedback analytics
9. Apply learning to content
10. Recalculate source quality
11. Extract preferences manually
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# =============================================================================
# CONFIGURATION
# =============================================================================

# Backend URL
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Authentication token (from previous sprints)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDQ2NTY0OC1iMzU3LTRhZDEtYTVjYy1hODkyZDcyZjJmODUiLCJleHAiOjE3NjA1NTc5OTd9.4tPB5MSKsdgLayUmQn-17gsplRaRCf7uP3wki6VohMA"

# Test workspace and user IDs (from Sprint 1)
WORKSPACE_ID = "3353d8f1-4bec-465c-9518-91ccc35d2898"
USER_ID = "f0465648-b357-4ad1-a5cc-a892d72f2f85"

# Headers
HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# =============================================================================
# TEST UTILITIES
# =============================================================================

def print_header(title: str):
    """Print test section header."""
    print("\n" + "=" * 80)
    print(f"TEST: {title}")
    print("=" * 80)


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"Details: {details}")


def print_response(response: requests.Response, show_data: bool = True):
    """Print API response."""
    print(f"\nStatus: {response.status_code}")
    try:
        data = response.json()
        if show_data:
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None


# =============================================================================
# TEST: SERVER HEALTH
# =============================================================================

def test_server_health():
    """Check if server is running."""
    print_header("Server Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = print_response(response)

        if response.status_code == 200:
            print_result("Server Health", True, f"Server is running ({data.get('status')})")
            return True
        else:
            print_result("Server Health", False, f"Server returned {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_result("Server Health", False, "Server is not running. Start with: python -m uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print_result("Server Health", False, str(e))
        return False


# =============================================================================
# TEST 1: Record Content Item Feedback (Positive)
# =============================================================================

def test_record_positive_feedback(content_item_id: str) -> Dict[str, Any]:
    """Test recording positive feedback on a content item."""
    print_header("Record Positive Content Item Feedback")

    payload = {
        "content_item_id": content_item_id,
        "rating": "positive",
        "included_in_final": True,
        "feedback_notes": "Great content, very relevant!"
    }

    response = requests.post(
        f"{API_V1}/feedback/items",
        headers=HEADERS,
        json=payload
    )

    data = print_response(response)

    if response.status_code == 200:
        feedback_id = data.get('data', {}).get('id')
        print_result("Record Positive Feedback", True, f"Feedback ID: {feedback_id}")
        return data.get('data', {})
    else:
        print_result("Record Positive Feedback", False, data.get('message', 'Unknown error'))
        return {}


# =============================================================================
# TEST 2: Record Content Item Feedback (Negative)
# =============================================================================

def test_record_negative_feedback(content_item_id: str) -> Dict[str, Any]:
    """Test recording negative feedback on a content item."""
    print_header("Record Negative Content Item Feedback")

    payload = {
        "content_item_id": content_item_id,
        "rating": "negative",
        "included_in_final": False,
        "feedback_notes": "Not relevant to our audience"
    }

    response = requests.post(
        f"{API_V1}/feedback/items",
        headers=HEADERS,
        json=payload
    )

    data = print_response(response)

    if response.status_code == 200:
        print_result("Record Negative Feedback", True)
        return data.get('data', {})
    else:
        print_result("Record Negative Feedback", False, data.get('message'))
        return {}


# =============================================================================
# TEST 3: List Feedback Items
# =============================================================================

def test_list_feedback_items():
    """Test listing feedback items for workspace."""
    print_header("List Feedback Items")

    response = requests.get(
        f"{API_V1}/feedback/items/{WORKSPACE_ID}",
        headers=HEADERS,
        params={"page_size": 10}
    )

    data = print_response(response, show_data=False)

    if response.status_code == 200:
        items = data.get('data', {}).get('items', [])
        total = data.get('data', {}).get('total', 0)
        print_result("List Feedback Items", True, f"Found {total} feedback items")

        if items:
            print(f"\nSample items:")
            for item in items[:3]:
                print(f"  - {item.get('rating')} | Included: {item.get('included_in_final')} | {item.get('created_at')}")

        return items
    else:
        print_result("List Feedback Items", False, data.get('message'))
        return []


# =============================================================================
# TEST 4: Record Newsletter Feedback
# =============================================================================

def test_record_newsletter_feedback(newsletter_id: str) -> Dict[str, Any]:
    """Test recording feedback on a newsletter."""
    print_header("Record Newsletter Feedback")

    payload = {
        "newsletter_id": newsletter_id,
        "overall_rating": 4,
        "time_to_finalize_minutes": 15,
        "items_added": 2,
        "items_removed": 1,
        "items_edited": 3,
        "notes": "Good draft, needed minor adjustments",
        "would_recommend": True
    }

    response = requests.post(
        f"{API_V1}/feedback/newsletters",
        headers=HEADERS,
        json=payload
    )

    data = print_response(response)

    if response.status_code == 200:
        feedback_id = data.get('data', {}).get('id')
        acceptance_rate = data.get('data', {}).get('draft_acceptance_rate', 0)
        print_result("Record Newsletter Feedback", True, f"Acceptance rate: {acceptance_rate:.0%}")
        return data.get('data', {})
    else:
        print_result("Record Newsletter Feedback", False, data.get('message'))
        return {}


# =============================================================================
# TEST 5: Get Source Quality Scores
# =============================================================================

def test_get_source_quality_scores():
    """Test getting source quality scores."""
    print_header("Get Source Quality Scores")

    response = requests.get(
        f"{API_V1}/feedback/sources/{WORKSPACE_ID}",
        headers=HEADERS
    )

    data = print_response(response, show_data=False)

    if response.status_code == 200:
        scores = data.get('data', {}).get('items', [])
        total = data.get('data', {}).get('total', 0)
        print_result("Get Source Quality Scores", True, f"Found {total} sources")

        if scores:
            print("\nSource Quality Breakdown:")
            for score in scores:
                quality = score.get('quality_score', 0)
                label = score.get('quality_label', 'Unknown')
                source = score.get('source_name', 'Unknown')
                feedback_count = score.get('total_feedback_count', 0)
                print(f"  - {source}: {quality:.2f} ({label}) | {feedback_count} feedback")

        return scores
    else:
        print_result("Get Source Quality Scores", False, data.get('message'))
        return []


# =============================================================================
# TEST 6: Get Content Preferences
# =============================================================================

def test_get_content_preferences():
    """Test getting content preferences."""
    print_header("Get Content Preferences")

    response = requests.get(
        f"{API_V1}/feedback/preferences/{WORKSPACE_ID}",
        headers=HEADERS
    )

    data = print_response(response, show_data=False)

    if response.status_code == 200:
        preferences = data.get('data', {})

        if preferences:
            confidence = preferences.get('confidence_level', 0)
            confidence_label = preferences.get('confidence_label', 'Unknown')
            feedback_count = preferences.get('total_feedback_count', 0)
            preferred_sources = preferences.get('preferred_sources', [])

            print_result("Get Content Preferences", True, f"Confidence: {confidence_label} ({confidence:.0%})")
            print(f"Feedback count: {feedback_count}")
            print(f"Preferred sources: {', '.join(preferred_sources) if preferred_sources else 'None yet'}")

            return preferences
        else:
            print_result("Get Content Preferences", True, "No preferences extracted yet")
            return None
    else:
        print_result("Get Content Preferences", False, data.get('message'))
        return None


# =============================================================================
# TEST 7: Get Feedback Analytics
# =============================================================================

def test_get_feedback_analytics():
    """Test getting feedback analytics."""
    print_header("Get Feedback Analytics")

    response = requests.get(
        f"{API_V1}/feedback/analytics/{WORKSPACE_ID}",
        headers=HEADERS,
        params={
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
    )

    data = print_response(response, show_data=False)

    if response.status_code == 200:
        analytics = data.get('data', {})

        total_feedback = analytics.get('total_feedback_items', 0)
        positive = analytics.get('positive_count', 0)
        negative = analytics.get('negative_count', 0)
        positive_rate = analytics.get('positive_rate', 0)
        inclusion_rate = analytics.get('inclusion_rate', 0)

        print_result("Get Feedback Analytics", True)
        print(f"\nAnalytics Summary:")
        print(f"  Total feedback: {total_feedback}")
        print(f"  Positive: {positive} ({positive_rate:.0%})")
        print(f"  Negative: {negative}")
        print(f"  Inclusion rate: {inclusion_rate:.0%}")

        # Learning summary
        learning = analytics.get('learning_summary', {})
        if learning:
            status = learning.get('learning_status', 'Unknown')
            confidence = learning.get('preferences_confidence', 0)
            print(f"\nLearning Status: {status} (confidence: {confidence:.0%})")

        # Recommendations
        recommendations = analytics.get('recommendations', [])
        if recommendations:
            print(f"\nRecommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

        return analytics
    else:
        print_result("Get Feedback Analytics", False, data.get('message'))
        return {}


# =============================================================================
# TEST 8: Apply Learning to Content
# =============================================================================

def test_apply_learning(content_item_ids: List[str]):
    """Test applying learning to content items."""
    print_header("Apply Learning to Content")

    if not content_item_ids:
        print_result("Apply Learning", False, "No content items provided")
        return {}

    payload = {
        "content_item_ids": content_item_ids,
        "apply_source_quality": True,
        "apply_preferences": True
    }

    response = requests.post(
        f"{API_V1}/feedback/apply-learning/{WORKSPACE_ID}",
        headers=HEADERS,
        json=payload
    )

    data = print_response(response, show_data=False)

    if response.status_code == 200:
        result = data.get('data', {})
        adjusted_items = result.get('adjusted_items', [])
        adjustments_made = result.get('adjustments_made', 0)
        quality_scores = result.get('quality_scores_applied', {})

        print_result("Apply Learning", True, f"{adjustments_made} items adjusted")

        if quality_scores:
            print("\nQuality scores applied:")
            for source, score in quality_scores.items():
                print(f"  - {source}: {score:.2f}")

        if adjusted_items:
            print("\nSample adjustments:")
            for item in adjusted_items[:3]:
                orig = item.get('original_score', 0)
                adj = item.get('adjusted_score', 0)
                adjustments = item.get('adjustments', [])
                print(f"  - Score: {orig} → {adj} | {', '.join(adjustments)}")

        return result
    else:
        print_result("Apply Learning", False, data.get('message'))
        return {}


# =============================================================================
# TEST 9: Recalculate Source Quality
# =============================================================================

def test_recalculate_source_quality():
    """Test manually recalculating source quality."""
    print_header("Recalculate Source Quality")

    response = requests.post(
        f"{API_V1}/feedback/recalculate/{WORKSPACE_ID}",
        headers=HEADERS
    )

    data = print_response(response)

    if response.status_code == 200:
        count = data.get('data', {}).get('sources_recalculated', 0)
        print_result("Recalculate Source Quality", True, f"{count} sources recalculated")
        return True
    else:
        print_result("Recalculate Source Quality", False, data.get('message'))
        return False


# =============================================================================
# TEST 10: Extract Preferences Manually
# =============================================================================

def test_extract_preferences():
    """Test manually extracting content preferences."""
    print_header("Extract Content Preferences")

    response = requests.post(
        f"{API_V1}/feedback/extract-preferences/{WORKSPACE_ID}",
        headers=HEADERS
    )

    data = print_response(response, show_data=False)

    if response.status_code == 200:
        preferences = data.get('data', {})
        confidence = preferences.get('confidence_level', 0) if preferences else 0
        print_result("Extract Preferences", True, f"Confidence: {confidence:.0%}")
        return preferences
    else:
        print_result("Extract Preferences", False, data.get('message'))
        return None


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    """Run all feedback API tests."""
    print("\n" + "=" * 80)
    print("FEEDBACK & LEARNING API TEST SUITE - SPRINT 7")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Workspace ID: {WORKSPACE_ID}")
    print(f"User ID: {USER_ID}")

    # Check server health
    if not test_server_health():
        print("\n❌ Server is not running. Exiting tests.")
        return

    # Get some content items to test with
    print_header("Getting Test Content Items")
    try:
        response = requests.get(
            f"{API_V1}/content/{WORKSPACE_ID}",
            headers=HEADERS,
            params={"limit": 5}
        )
        content_items = response.json().get('data', {}).get('items', [])
        content_ids = [item['id'] for item in content_items]

        if not content_ids:
            print("⚠️  No content items found. Creating test content may be needed.")
            print("Note: Some tests may be skipped.")
        else:
            print(f"✅ Found {len(content_ids)} content items for testing")

    except Exception as e:
        print(f"❌ Failed to get content items: {e}")
        content_ids = []

    # Get newsletter ID
    newsletter_id = None
    try:
        response = requests.get(
            f"{API_V1}/newsletters/{WORKSPACE_ID}",
            headers=HEADERS,
            params={"limit": 1}
        )
        newsletters = response.json().get('data', {}).get('items', [])
        if newsletters:
            newsletter_id = newsletters[0]['id']
            print(f"✅ Found newsletter ID: {newsletter_id}")
        else:
            print("⚠️  No newsletters found. Newsletter tests may be skipped.")
    except Exception as e:
        print(f"⚠️  Failed to get newsletters: {e}")

    # Run tests
    test_results = []

    # Test 1 & 2: Record feedback
    if content_ids:
        test_record_positive_feedback(content_ids[0])
        if len(content_ids) > 1:
            test_record_negative_feedback(content_ids[1])

    # Test 3: List feedback
    test_list_feedback_items()

    # Test 4: Newsletter feedback
    if newsletter_id:
        test_record_newsletter_feedback(newsletter_id)

    # Test 5: Source quality scores
    test_get_source_quality_scores()

    # Test 6: Content preferences
    test_get_content_preferences()

    # Test 7: Analytics
    test_get_feedback_analytics()

    # Test 8: Apply learning
    if content_ids:
        test_apply_learning(content_ids[:3])

    # Test 9: Recalculate quality
    test_recalculate_source_quality()

    # Test 10: Extract preferences
    test_extract_preferences()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Run database migration in Supabase SQL Editor")
    print("2. Provide more feedback to improve learning confidence")
    print("3. Integrate feedback into content scraping and newsletter generation")
    print("4. Monitor source quality scores over time")


if __name__ == "__main__":
    main()
