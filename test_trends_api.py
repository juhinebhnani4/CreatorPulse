"""
Test script for Trends Detection API endpoints.

Tests all trend-related endpoints:
- Detect trends from content
- Get active trends
- Get trend history
- Get trend summary
- Get specific trend
- Delete trend
"""

import requests
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Replace with your actual JWT token and workspace ID
# Get token by logging in: POST /api/v1/auth/login
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDQ2NTY0OC1iMzU3LTRhZDEtYTVjYy1hODkyZDcyZjJmODUiLCJleHAiOjE3NjA1NTc5OTd9.4tPB5MSKsdgLayUmQn-17gsplRaRCf7uP3wki6VohMA"
WORKSPACE_ID = "3353d8f1-4bec-465c-9518-91ccc35d2898"

# Will be set after detection
DETECTED_TREND_ID = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_request(method, endpoint, data=None, params=None):
    """Make API request with authentication."""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{API_V1}{endpoint}"

    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return response


def print_result(test_name, response):
    """Print test result."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")

    try:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    except:
        print(f"Response: {response.text}")

    success = response.status_code in [200, 201]
    print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")

    return success, result if success else None


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_detect_trends():
    """Test 1: Detect trends from content."""
    global DETECTED_TREND_ID

    data = {
        "workspace_id": WORKSPACE_ID,
        "days_back": 7,
        "max_trends": 5,
        "min_confidence": 0.5,
        "sources": None  # All sources
    }

    response = make_request("POST", "/trends/detect", data=data)
    success, result = print_result("Detect Trends", response)

    # Save first trend ID for later tests
    if success and result.get('data', {}).get('trends'):
        trends = result['data']['trends']
        if trends:
            DETECTED_TREND_ID = trends[0]['id']
            print(f"\n[INFO] Saved trend ID for later tests: {DETECTED_TREND_ID}")

    return success


def test_get_active_trends():
    """Test 2: Get active trends."""
    response = make_request("GET", f"/trends/{WORKSPACE_ID}", params={"limit": 5})
    return print_result("Get Active Trends", response)[0]


def test_get_trend_history():
    """Test 3: Get trend history."""
    response = make_request("GET", f"/trends/{WORKSPACE_ID}/history", params={"days_back": 30})
    return print_result("Get Trend History", response)[0]


def test_get_trend_summary():
    """Test 4: Get trend summary."""
    response = make_request("GET", f"/trends/{WORKSPACE_ID}/summary", params={"days_back": 7})
    return print_result("Get Trend Summary", response)[0]


def test_get_specific_trend():
    """Test 5: Get specific trend by ID."""
    if not DETECTED_TREND_ID:
        print("\n⚠️  Skipping: No trend ID available (detection may have failed)")
        return True  # Don't fail if no trends detected

    response = make_request("GET", f"/trends/trend/{DETECTED_TREND_ID}")
    return print_result("Get Specific Trend", response)[0]


def test_delete_trend():
    """Test 6: Delete a trend."""
    if not DETECTED_TREND_ID:
        print("\n⚠️  Skipping: No trend ID available (detection may have failed)")
        return True  # Don't fail if no trends detected

    response = make_request("DELETE", f"/trends/trend/{DETECTED_TREND_ID}")
    return print_result("Delete Trend", response)[0]


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all trends API tests."""
    print("\n" + "="*80)
    print("TRENDS DETECTION API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Workspace ID: {WORKSPACE_ID}")

    results = []

    # Test sequence
    tests = [
        ("1. Detect Trends", test_detect_trends),
        ("2. Get Active Trends", test_get_active_trends),
        ("3. Get Trend History", test_get_trend_history),
        ("4. Get Trend Summary", test_get_trend_summary),
        ("5. Get Specific Trend", test_get_specific_trend),
        ("6. Delete Trend", test_delete_trend),
    ]

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    print("\n" + "="*80)
    print("NOTES")
    print("="*80)
    print("- Trend detection requires existing content items in the workspace")
    print("- If detection fails, verify you have scraped content recently")
    print("- Minimum 5 content items required for detection")
    print("- Cross-source validation requires content from 2+ sources")
    print("- Run content scraping first if tests fail")

    return passed == total


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
        print("Start server with: python -m uvicorn backend.main:app --reload")
        exit(1)

    # Run tests
    success = run_all_tests()
    exit(0 if success else 1)
