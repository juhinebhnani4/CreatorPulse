"""
Comprehensive test suite for all advanced features (34+ endpoints)
Tests: Style Training, Trends Detection, Feedback & Learning, Analytics, Email Tracking
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test user credentials - using timestamp to make it unique
import time
unique_suffix = str(int(time.time()))
TEST_USER = {
    "username": f"testuser_{unique_suffix}",
    "email": f"test_{unique_suffix}@example.com",
    "password": "TestPassword123!"
}

# Global state
auth_token = None
workspace_id = None
newsletter_id = None
subscriber_id = None
content_items = []
test_results = []


class TestResult:
    """Track test results"""
    def __init__(self, category: str, endpoint: str, method: str, status: str, details: str = ""):
        self.category = category
        self.endpoint = endpoint
        self.method = method
        self.status = status  # "PASS", "FAIL", "SKIP"
        self.details = details
        self.timestamp = datetime.now()


def log_result(category: str, endpoint: str, method: str, status: str, details: str = ""):
    """Log test result"""
    result = TestResult(category, endpoint, method, status, details)
    test_results.append(result)
    status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
    print(f"  {status_icon} {method:6s} {endpoint:50s} - {details}")


def get_headers(include_auth: bool = True) -> Dict[str, str]:
    """Get request headers"""
    headers = {"Content-Type": "application/json"}
    if include_auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


# =============================================================================
# SETUP: Authentication and Workspace
# =============================================================================

def setup_authentication():
    """Login and get auth token"""
    global auth_token

    print("\n=== SETUP: Authentication ===")

    # Try to login with email/password
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }

    response = requests.post(
        f"{API_BASE}/auth/login",
        json=login_data
    )

    if response.status_code == 200:
        data = response.json()
        # The token field might be "token" or "access_token"
        auth_token = data["data"].get("token") or data["data"].get("access_token")
        print(f"[OK] Logged in successfully")
        return True

    print(f"[WARN] Login failed with status {response.status_code}")

    # If login fails, try to signup
    signup_response = requests.post(
        f"{API_BASE}/auth/signup",
        json=TEST_USER
    )

    if signup_response.status_code in [200, 201]:
        data = signup_response.json()
        # The token field might be "token" or "access_token"
        auth_token = data["data"].get("token") or data["data"].get("access_token")
        print(f"[OK] Signed up successfully")
        return True

    print(f"[ERROR] Both login and signup failed")
    print(f"  Login error: {response.text[:150]}")
    print(f"  Signup error: {signup_response.text[:150]}")
    return False


def setup_workspace():
    """Create or get existing workspace"""
    global workspace_id

    print("\n=== SETUP: Workspace ===")

    # List existing workspaces
    response = requests.get(
        f"{API_BASE}/workspaces",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        workspaces = data.get("data", [])

        # Handle both list and dict responses
        if isinstance(workspaces, dict):
            workspaces = [workspaces]  # Convert dict to list

        if workspaces and len(workspaces) > 0:
            # The workspace might have "workspace_id" or "id"
            first_workspace = workspaces[0]
            workspace_id = first_workspace.get("id") or first_workspace.get("workspace_id")
            if workspace_id:
                print(f"[OK] Using existing workspace: {workspace_id}")
                return True
            else:
                print(f"[WARN] Workspace found but no ID field. Creating new one.")

    # Create new workspace with unique name
    response = requests.post(
        f"{API_BASE}/workspaces",
        headers=get_headers(),
        json={
            "name": f"Advanced Features Test Workspace {unique_suffix}",
            "description": "Testing all advanced features"
        }
    )

    if response.status_code in [200, 201]:
        data = response.json()
        workspace_id = data["data"]["id"]
        print(f"[OK] Created workspace: {workspace_id}")
        return True

    print(f"[ERROR] Workspace setup failed: {response.text}")
    return False


def setup_test_data():
    """Create test newsletter and content"""
    global newsletter_id, content_items, subscriber_id

    print("\n=== SETUP: Test Data ===")

    # Create subscriber for analytics tests
    response = requests.post(
        f"{API_BASE}/subscribers",
        headers=get_headers(),
        json={
            "workspace_id": workspace_id,
            "email": "subscriber@example.com",
            "name": "Test Subscriber"
        }
    )

    if response.status_code in [200, 201]:
        subscriber_id = response.json()["data"]["id"]
        print(f"[OK] Created subscriber: {subscriber_id}")

    # Get existing content items
    response = requests.get(
        f"{API_BASE}/content/workspaces/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        content_items = data.get("data", [])

        # Handle both list and dict responses
        if isinstance(content_items, dict):
            content_items = [content_items]

        print(f"[OK] Found {len(content_items)} content items")

    # Get or create newsletter
    response = requests.get(
        f"{API_BASE}/newsletters/workspaces/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        newsletters = data.get("data", [])

        # Handle both list and dict responses
        if isinstance(newsletters, dict):
            newsletters = [newsletters]

        if newsletters and len(newsletters) > 0:
            first_newsletter = newsletters[0]
            newsletter_id = first_newsletter.get("id") or first_newsletter.get("newsletter_id")
            if newsletter_id:
                print(f"[OK] Using existing newsletter: {newsletter_id}")
                return True

    # Generate newsletter if none exists
    print("  Creating newsletter for testing...")
    response = requests.post(
        f"{API_BASE}/newsletters/generate",
        headers=get_headers(),
        json={
            "workspace_id": workspace_id,
            "title": "Test Newsletter for Advanced Features"
        }
    )

    if response.status_code in [200, 201]:
        data = response.json()
        newsletter_id = data["data"]["id"]
        print(f"[OK] Created newsletter: {newsletter_id}")
        return True

    print(f"  [WARN] Newsletter creation failed, some tests may be skipped")
    return False


# =============================================================================
# STYLE TRAINING TESTS (6 endpoints)
# =============================================================================

def test_style_training():
    """Test all style training endpoints"""
    print("\n" + "="*80)
    print("CATEGORY: STYLE TRAINING (6 endpoints)")
    print("="*80)

    category = "Style Training"

    # 1. POST /api/v1/style/train - Train style profile
    sample_newsletters = [
        {
            "content": "Hey there! Welcome to this week's AI newsletter. We've got some exciting updates to share with you. Let's dive in!",
            "title": "Weekly AI Update #1"
        },
        {
            "content": "Hello everyone! Another week, another set of amazing AI breakthroughs. Here's what caught our attention this week.",
            "title": "Weekly AI Update #2"
        }
    ]

    response = requests.post(
        f"{API_BASE}/style/train",
        headers=get_headers(),
        json={
            "workspace_id": workspace_id,
            "sample_newsletters": sample_newsletters
        }
    )

    if response.status_code in [200, 201]:
        data = response.json()
        log_result(category, "/api/v1/style/train", "POST", "PASS",
                   f"Profile created with {len(data.get('data', {}).get('patterns', []))} patterns")
    else:
        log_result(category, "/api/v1/style/train", "POST", "FAIL",
                   f"Status {response.status_code}: {response.text[:100]}")

    # 2. GET /api/v1/style/{workspace_id} - Get style profile
    response = requests.get(
        f"{API_BASE}/style/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        profile = data.get("data", {})
        log_result(category, f"/api/v1/style/{'{workspace_id}'}", "GET", "PASS",
                   f"Retrieved profile with tone: {profile.get('tone', 'N/A')}")
    else:
        log_result(category, f"/api/v1/style/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 3. GET /api/v1/style/{workspace_id}/summary - Get style summary
    response = requests.get(
        f"{API_BASE}/style/{workspace_id}/summary",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        summary = data.get("data", {})
        log_result(category, f"/api/v1/style/{'{workspace_id}'}/summary", "GET", "PASS",
                   f"Summary: {summary.get('formality', 'N/A')} formality")
    else:
        log_result(category, f"/api/v1/style/{'{workspace_id}'}/summary", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 4. PUT /api/v1/style/{workspace_id} - Update style profile
    response = requests.put(
        f"{API_BASE}/style/{workspace_id}",
        headers=get_headers(),
        json={
            "tone": "professional",
            "formality": "formal"
        }
    )

    if response.status_code == 200:
        log_result(category, f"/api/v1/style/{'{workspace_id}'}", "PUT", "PASS",
                   "Profile updated successfully")
    else:
        log_result(category, f"/api/v1/style/{'{workspace_id}'}", "PUT", "FAIL",
                   f"Status {response.status_code}")

    # 5. POST /api/v1/style/prompt - Generate style-specific prompt
    response = requests.post(
        f"{API_BASE}/style/prompt",
        headers=get_headers(),
        json={
            "workspace_id": workspace_id,
            "base_prompt": "Generate a newsletter about AI trends"
        }
    )

    if response.status_code == 200:
        data = response.json()
        prompt = data.get("data", {}).get("enhanced_prompt", "")
        log_result(category, "/api/v1/style/prompt", "POST", "PASS",
                   f"Generated prompt ({len(prompt)} chars)")
    else:
        log_result(category, "/api/v1/style/prompt", "POST", "FAIL",
                   f"Status {response.status_code}")

    # 6. DELETE /api/v1/style/{workspace_id} - Delete style profile
    # Skip this for now to keep the profile for other tests
    log_result(category, f"/api/v1/style/{'{workspace_id}'}", "DELETE", "SKIP",
               "Skipped to preserve data for other tests")


# =============================================================================
# TRENDS DETECTION TESTS (6 endpoints)
# =============================================================================

def test_trends_detection():
    """Test all trends detection endpoints"""
    print("\n" + "="*80)
    print("CATEGORY: TRENDS DETECTION (6 endpoints)")
    print("="*80)

    category = "Trends Detection"
    trend_id = None

    # 1. POST /api/v1/trends/detect - Detect trends
    response = requests.post(
        f"{API_BASE}/trends/detect",
        headers=get_headers(),
        json={
            "workspace_id": workspace_id,
            "days_back": 30,
            "min_mentions": 2
        }
    )

    if response.status_code in [200, 201]:
        data = response.json()
        trends = data.get("data", {}).get("trends", [])
        if trends:
            trend_id = trends[0].get("id")
        log_result(category, "/api/v1/trends/detect", "POST", "PASS",
                   f"Detected {len(trends)} trends")
    else:
        log_result(category, "/api/v1/trends/detect", "POST", "FAIL",
                   f"Status {response.status_code}: {response.text[:100]}")

    # 2. GET /api/v1/trends/{workspace_id} - Get active trends
    response = requests.get(
        f"{API_BASE}/trends/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        trends = data.get("data", [])
        log_result(category, f"/api/v1/trends/{'{workspace_id}'}", "GET", "PASS",
                   f"Retrieved {len(trends)} active trends")
    else:
        log_result(category, f"/api/v1/trends/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 3. GET /api/v1/trends/{workspace_id}/history - Get trend history
    response = requests.get(
        f"{API_BASE}/trends/{workspace_id}/history",
        headers=get_headers(),
        params={"days": 30}
    )

    if response.status_code == 200:
        data = response.json()
        history = data.get("data", [])
        log_result(category, f"/api/v1/trends/{'{workspace_id}'}/history", "GET", "PASS",
                   f"Retrieved {len(history)} historical trends")
    else:
        log_result(category, f"/api/v1/trends/{'{workspace_id}'}/history", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 4. GET /api/v1/trends/{workspace_id}/summary - Get trend summary
    response = requests.get(
        f"{API_BASE}/trends/{workspace_id}/summary",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        summary = data.get("data", {})
        log_result(category, f"/api/v1/trends/{'{workspace_id}'}/summary", "GET", "PASS",
                   f"Total: {summary.get('total_trends', 0)}, Active: {summary.get('active_trends', 0)}")
    else:
        log_result(category, f"/api/v1/trends/{'{workspace_id}'}/summary", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 5. GET /api/v1/trends/trend/{trend_id} - Get specific trend
    if trend_id:
        response = requests.get(
            f"{API_BASE}/trends/trend/{trend_id}",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            trend = data.get("data", {})
            log_result(category, f"/api/v1/trends/trend/{'{trend_id}'}", "GET", "PASS",
                       f"Trend: {trend.get('topic', 'N/A')}")
        else:
            log_result(category, f"/api/v1/trends/trend/{'{trend_id}'}", "GET", "FAIL",
                       f"Status {response.status_code}")
    else:
        log_result(category, f"/api/v1/trends/trend/{'{trend_id}'}", "GET", "SKIP",
                   "No trends available to test")

    # 6. DELETE /api/v1/trends/trend/{trend_id} - Delete trend
    # Skip to preserve data
    log_result(category, f"/api/v1/trends/trend/{'{trend_id}'}", "DELETE", "SKIP",
               "Skipped to preserve data for other tests")


# =============================================================================
# FEEDBACK & LEARNING TESTS (11 endpoints)
# =============================================================================

def test_feedback_learning():
    """Test all feedback and learning endpoints"""
    print("\n" + "="*80)
    print("CATEGORY: FEEDBACK & LEARNING (11 endpoints)")
    print("="*80)

    category = "Feedback & Learning"

    # 1. POST /api/v1/feedback/items - Record content item feedback
    if content_items and len(content_items) > 0:
        first_item = content_items[0]
        content_id = first_item.get("id") or first_item.get("content_id")

        if content_id:
            response = requests.post(
                f"{API_BASE}/feedback/items",
                headers=get_headers(),
                json={
                    "content_id": content_id,
                    "workspace_id": workspace_id,
                    "rating": "positive",
                    "included_in_newsletter": True,
                    "notes": "Great content!"
                }
            )

            if response.status_code in [200, 201]:
                log_result(category, "/api/v1/feedback/items", "POST", "PASS",
                           "Content feedback recorded")
            else:
                log_result(category, "/api/v1/feedback/items", "POST", "FAIL",
                           f"Status {response.status_code}")
        else:
            log_result(category, "/api/v1/feedback/items", "POST", "SKIP",
                       "Content items have no ID field")
    else:
        log_result(category, "/api/v1/feedback/items", "POST", "SKIP",
                   "No content items available")

    # 2. GET /api/v1/feedback/items/{workspace_id} - List feedback items
    response = requests.get(
        f"{API_BASE}/feedback/items/{workspace_id}",
        headers=get_headers(),
        params={"limit": 10}
    )

    if response.status_code == 200:
        data = response.json()
        feedback = data.get("data", [])
        log_result(category, f"/api/v1/feedback/items/{'{workspace_id}'}", "GET", "PASS",
                   f"Retrieved {len(feedback)} feedback items")
    else:
        log_result(category, f"/api/v1/feedback/items/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 3. POST /api/v1/feedback/newsletters - Record newsletter feedback
    if newsletter_id:
        response = requests.post(
            f"{API_BASE}/feedback/newsletters",
            headers=get_headers(),
            json={
                "newsletter_id": newsletter_id,
                "workspace_id": workspace_id,
                "rating": 4,
                "comments": "Good newsletter!",
                "sections_liked": ["Introduction", "Main Content"],
                "sections_disliked": []
            }
        )

        if response.status_code in [200, 201]:
            log_result(category, "/api/v1/feedback/newsletters", "POST", "PASS",
                       "Newsletter feedback recorded")
        else:
            log_result(category, "/api/v1/feedback/newsletters", "POST", "FAIL",
                       f"Status {response.status_code}")
    else:
        log_result(category, "/api/v1/feedback/newsletters", "POST", "SKIP",
                   "No newsletter available")

    # 4. GET /api/v1/feedback/newsletters/{newsletter_id} - Get newsletter feedback
    if newsletter_id:
        response = requests.get(
            f"{API_BASE}/feedback/newsletters/{newsletter_id}",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            feedback = data.get("data", [])
            log_result(category, f"/api/v1/feedback/newsletters/{'{newsletter_id}'}", "GET", "PASS",
                       f"Retrieved {len(feedback)} feedback entries")
        else:
            log_result(category, f"/api/v1/feedback/newsletters/{'{newsletter_id}'}", "GET", "FAIL",
                       f"Status {response.status_code}")
    else:
        log_result(category, f"/api/v1/feedback/newsletters/{'{newsletter_id}'}", "GET", "SKIP",
                   "No newsletter available")

    # 5. GET /api/v1/feedback/newsletters/workspace/{workspace_id} - List workspace newsletter feedback
    response = requests.get(
        f"{API_BASE}/feedback/newsletters/workspace/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        feedback = data.get("data", [])
        log_result(category, f"/api/v1/feedback/newsletters/workspace/{'{workspace_id}'}", "GET", "PASS",
                   f"Retrieved {len(feedback)} newsletter feedback entries")
    else:
        log_result(category, f"/api/v1/feedback/newsletters/workspace/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 6. GET /api/v1/feedback/sources/{workspace_id} - Get source quality scores
    response = requests.get(
        f"{API_BASE}/feedback/sources/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        sources = data.get("data", {})
        log_result(category, f"/api/v1/feedback/sources/{'{workspace_id}'}", "GET", "PASS",
                   f"Retrieved quality scores for {len(sources)} sources")
    else:
        log_result(category, f"/api/v1/feedback/sources/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 7. GET /api/v1/feedback/preferences/{workspace_id} - Get learned preferences
    response = requests.get(
        f"{API_BASE}/feedback/preferences/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        prefs = data.get("data", {})
        log_result(category, f"/api/v1/feedback/preferences/{'{workspace_id}'}", "GET", "PASS",
                   f"Retrieved preferences: {len(prefs.get('topic_preferences', {}))} topics")
    else:
        log_result(category, f"/api/v1/feedback/preferences/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 8. GET /api/v1/feedback/analytics/{workspace_id} - Get comprehensive analytics
    response = requests.get(
        f"{API_BASE}/feedback/analytics/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        analytics = data.get("data", {})
        log_result(category, f"/api/v1/feedback/analytics/{'{workspace_id}'}", "GET", "PASS",
                   f"Total feedback: {analytics.get('total_feedback', 0)}")
    else:
        log_result(category, f"/api/v1/feedback/analytics/{'{workspace_id}'}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 9. POST /api/v1/feedback/apply-learning/{workspace_id} - Apply learned preferences
    response = requests.post(
        f"{API_BASE}/feedback/apply-learning/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        result = data.get("data", {})
        log_result(category, f"/api/v1/feedback/apply-learning/{'{workspace_id}'}", "POST", "PASS",
                   f"Updated {result.get('items_updated', 0)} items")
    else:
        log_result(category, f"/api/v1/feedback/apply-learning/{'{workspace_id}'}", "POST", "FAIL",
                   f"Status {response.status_code}")

    # 10. POST /api/v1/feedback/recalculate/{workspace_id} - Recalculate source quality
    response = requests.post(
        f"{API_BASE}/feedback/recalculate/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        result = data.get("data", {})
        log_result(category, f"/api/v1/feedback/recalculate/{'{workspace_id}'}", "POST", "PASS",
                   f"Recalculated {result.get('sources_updated', 0)} sources")
    else:
        log_result(category, f"/api/v1/feedback/recalculate/{'{workspace_id}'}", "POST", "FAIL",
                   f"Status {response.status_code}")

    # 11. POST /api/v1/feedback/extract-preferences/{workspace_id} - Extract preferences
    response = requests.post(
        f"{API_BASE}/feedback/extract-preferences/{workspace_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        result = data.get("data", {})
        log_result(category, f"/api/v1/feedback/extract-preferences/{'{workspace_id}'}", "POST", "PASS",
                   f"Extracted {len(result.get('topic_preferences', {}))} topic preferences")
    else:
        log_result(category, f"/api/v1/feedback/extract-preferences/{'{workspace_id}'}", "POST", "FAIL",
                   f"Status {response.status_code}")


# =============================================================================
# ANALYTICS TESTS (7 endpoints)
# =============================================================================

def test_analytics():
    """Test all analytics endpoints"""
    print("\n" + "="*80)
    print("CATEGORY: ANALYTICS (7 endpoints)")
    print("="*80)

    category = "Analytics"

    # 1. POST /api/v1/analytics/events - Record analytics event
    if newsletter_id and subscriber_id:
        # Record a "sent" event
        response = requests.post(
            f"{API_BASE}/analytics/events",
            headers=get_headers(),
            json={
                "newsletter_id": newsletter_id,
                "subscriber_id": subscriber_id,
                "event_type": "sent"
            }
        )

        if response.status_code in [200, 201]:
            log_result(category, "/api/v1/analytics/events", "POST", "PASS",
                       "Event 'sent' recorded")
        else:
            log_result(category, "/api/v1/analytics/events", "POST", "FAIL",
                       f"Status {response.status_code}")

        # Record an "opened" event
        time.sleep(0.5)
        response = requests.post(
            f"{API_BASE}/analytics/events",
            headers=get_headers(),
            json={
                "newsletter_id": newsletter_id,
                "subscriber_id": subscriber_id,
                "event_type": "opened"
            }
        )

        if response.status_code in [200, 201]:
            log_result(category, "/api/v1/analytics/events (opened)", "POST", "PASS",
                       "Event 'opened' recorded")
    else:
        log_result(category, "/api/v1/analytics/events", "POST", "SKIP",
                   "Missing newsletter or subscriber")

    # 2. GET /api/v1/analytics/newsletters/{newsletter_id} - Get newsletter analytics
    if newsletter_id:
        response = requests.get(
            f"{API_BASE}/analytics/newsletters/{newsletter_id}",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            analytics = data.get("data", {})
            log_result(category, f"/api/v1/analytics/newsletters/{'{newsletter_id}'}", "GET", "PASS",
                       f"Sent: {analytics.get('total_sent', 0)}, Opened: {analytics.get('total_opened', 0)}")
        else:
            log_result(category, f"/api/v1/analytics/newsletters/{'{newsletter_id}'}", "GET", "FAIL",
                       f"Status {response.status_code}")
    else:
        log_result(category, f"/api/v1/analytics/newsletters/{'{newsletter_id}'}", "GET", "SKIP",
                   "No newsletter available")

    # 3. POST /api/v1/analytics/newsletters/{newsletter_id}/recalculate - Recalculate analytics
    if newsletter_id:
        response = requests.post(
            f"{API_BASE}/analytics/newsletters/{newsletter_id}/recalculate",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            summary = data.get("data", {})
            log_result(category, f"/api/v1/analytics/newsletters/{'{newsletter_id}'}/recalculate", "POST", "PASS",
                       f"Recalculated: {summary.get('total_sent', 0)} sent")
        else:
            log_result(category, f"/api/v1/analytics/newsletters/{'{newsletter_id}'}/recalculate", "POST", "FAIL",
                       f"Status {response.status_code}")
    else:
        log_result(category, f"/api/v1/analytics/newsletters/{'{newsletter_id}'}/recalculate", "POST", "SKIP",
                   "No newsletter available")

    # 4. GET /api/v1/analytics/workspaces/{workspace_id}/summary - Get workspace summary
    response = requests.get(
        f"{API_BASE}/analytics/workspaces/{workspace_id}/summary",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        summary = data.get("data", {})
        log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/summary", "GET", "PASS",
                   f"Total sent: {summary.get('total_sent', 0)}, Avg open rate: {summary.get('avg_open_rate', 0):.1%}")
    else:
        log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/summary", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 5. GET /api/v1/analytics/workspaces/{workspace_id}/content-performance - Get content performance
    response = requests.get(
        f"{API_BASE}/analytics/workspaces/{workspace_id}/content-performance",
        headers=get_headers(),
        params={"limit": 10}
    )

    if response.status_code == 200:
        data = response.json()
        content = data.get("data", [])
        log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/content-performance", "GET", "PASS",
                   f"Retrieved {len(content)} top performing items")
    else:
        log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/content-performance", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 6. GET /api/v1/analytics/workspaces/{workspace_id}/export - Export analytics
    for export_format in ["json", "csv"]:
        response = requests.get(
            f"{API_BASE}/analytics/workspaces/{workspace_id}/export",
            headers=get_headers(),
            params={"format": export_format}
        )

        if response.status_code == 200:
            log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/export ({export_format})", "GET", "PASS",
                       f"Exported data in {export_format.upper()} format")
        else:
            log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/export ({export_format})", "GET", "FAIL",
                       f"Status {response.status_code}")

    # 7. GET /api/v1/analytics/workspaces/{workspace_id}/dashboard - Get dashboard analytics
    response = requests.get(
        f"{API_BASE}/analytics/workspaces/{workspace_id}/dashboard",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        dashboard = data.get("data", {})
        log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/dashboard", "GET", "PASS",
                   f"Dashboard data retrieved with {len(dashboard.get('recent_newsletters', []))} recent newsletters")
    else:
        log_result(category, f"/api/v1/analytics/workspaces/{'{workspace_id}'}/dashboard", "GET", "FAIL",
                   f"Status {response.status_code}")


# =============================================================================
# EMAIL TRACKING TESTS (5 endpoints)
# =============================================================================

def test_email_tracking():
    """Test email tracking endpoints"""
    print("\n" + "="*80)
    print("CATEGORY: EMAIL TRACKING (5 endpoints)")
    print("="*80)

    category = "Email Tracking"

    # Create encoded params for testing
    import base64
    params = {
        "newsletter_id": newsletter_id or "test-id",
        "subscriber_id": subscriber_id or "test-sub-id"
    }
    encoded = base64.b64encode(json.dumps(params).encode()).decode()

    # 1. GET /track/pixel/{encoded_params}.png - Tracking pixel
    response = requests.get(
        f"{BASE_URL}/track/pixel/{encoded}.png",
        allow_redirects=False
    )

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        if "image/png" in content_type:
            log_result(category, "/track/pixel/{encoded}.png", "GET", "PASS",
                       f"Tracking pixel returned (PNG, {len(response.content)} bytes)")
        else:
            log_result(category, "/track/pixel/{encoded}.png", "GET", "FAIL",
                       f"Wrong content type: {content_type}")
    else:
        log_result(category, "/track/pixel/{encoded}.png", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 2. GET /track/click/{encoded_params} - Click tracking
    # Note: This endpoint redirects, so we don't follow redirects
    params_with_url = {
        **params,
        "url": "https://example.com"
    }
    encoded_click = base64.b64encode(json.dumps(params_with_url).encode()).decode()

    response = requests.get(
        f"{BASE_URL}/track/click/{encoded_click}",
        allow_redirects=False
    )

    if response.status_code in [302, 307]:
        location = response.headers.get("Location", "")
        log_result(category, "/track/click/{encoded}", "GET", "PASS",
                   f"Redirect to: {location[:50]}...")
    else:
        log_result(category, "/track/click/{encoded}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 3. GET /unsubscribe/{encoded_params} - Unsubscribe page
    response = requests.get(
        f"{BASE_URL}/unsubscribe/{encoded}",
        allow_redirects=True
    )

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            log_result(category, "/unsubscribe/{encoded}", "GET", "PASS",
                       f"Unsubscribe page returned (HTML)")
        else:
            log_result(category, "/unsubscribe/{encoded}", "GET", "FAIL",
                       f"Wrong content type: {content_type}")
    else:
        log_result(category, "/unsubscribe/{encoded}", "GET", "FAIL",
                   f"Status {response.status_code}")

    # 4. POST /unsubscribe/{encoded_params} - Process unsubscribe
    # Skip this to avoid actually unsubscribing our test subscriber
    log_result(category, "/unsubscribe/{encoded}", "POST", "SKIP",
               "Skipped to avoid unsubscribing test subscriber")

    # 5. POST /list-unsubscribe - One-click unsubscribe
    # Skip this as well
    log_result(category, "/list-unsubscribe", "POST", "SKIP",
               "Skipped to avoid unsubscribing test subscriber")


# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    # Count results by category and status
    categories = {}
    total_pass = 0
    total_fail = 0
    total_skip = 0

    for result in test_results:
        if result.category not in categories:
            categories[result.category] = {"PASS": 0, "FAIL": 0, "SKIP": 0}

        categories[result.category][result.status] += 1

        if result.status == "PASS":
            total_pass += 1
        elif result.status == "FAIL":
            total_fail += 1
        else:
            total_skip += 1

    # Print category summaries
    for category, counts in categories.items():
        total = counts["PASS"] + counts["FAIL"] + counts["SKIP"]
        print(f"\n{category}:")
        print(f"  [PASS] Passed: {counts['PASS']}/{total}")
        print(f"  [FAIL] Failed: {counts['FAIL']}/{total}")
        print(f"  [SKIP] Skipped: {counts['SKIP']}/{total}")

    # Print overall summary
    total = total_pass + total_fail + total_skip
    print(f"\n{'='*80}")
    print(f"OVERALL RESULTS:")
    print(f"  Total Tests: {total}")
    print(f"  [PASS] Passed: {total_pass} ({total_pass/total*100:.1f}%)")
    print(f"  [FAIL] Failed: {total_fail} ({total_fail/total*100:.1f}%)")
    print(f"  [SKIP] Skipped: {total_skip} ({total_skip/total*100:.1f}%)")

    # Print failed tests details
    failed_tests = [r for r in test_results if r.status == "FAIL"]
    if failed_tests:
        print(f"\n{'='*80}")
        print("FAILED TESTS DETAILS:")
        for result in failed_tests:
            print(f"\n  {result.category} - {result.method} {result.endpoint}")
            print(f"    {result.details}")


def main():
    """Main test execution"""
    print("="*80)
    print("ADVANCED FEATURES COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Testing {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Setup
    if not setup_authentication():
        print("\n[ERROR] Authentication failed. Cannot proceed with tests.")
        return

    if not setup_workspace():
        print("\n[ERROR] Workspace setup failed. Cannot proceed with tests.")
        return

    setup_test_data()

    # Run all test suites
    test_style_training()
    test_trends_detection()
    test_feedback_learning()
    test_analytics()
    test_email_tracking()

    # Print summary
    print_summary()

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == "__main__":
    main()
