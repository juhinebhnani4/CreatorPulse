"""
Test script for Style Training API endpoints.

Tests all style-related endpoints:
- Train style profile from samples
- Get style profile
- Get style summary
- Generate style prompt
- Update style profile
- Delete style profile
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

# Sample newsletter texts for training
SAMPLE_NEWSLETTERS = [
    """
    Hey everyone! Ever wonder why AI agents are suddenly everywhere? Let's dive in.

    The short answer: they actually work now. Here's what's changed in the last year.
    Companies are seeing real ROI, not just hype. We're talking 40% efficiency gains
    in customer service, automated workflows that actually make sense, and AI that
    can handle complex tasks without constant hand-holding.

    But here's the thing - it's not magic. The secret sauce is better training data
    and smarter prompt engineering. Quick tip: focus on your use case first, then
    build the agent around it.

    That's all for today. Stay curious!
    """,
    """
    Quick thought on the latest AI developments: we're at an inflection point.

    Remember when everyone said AI would replace programmers? Well, it's more nuanced.
    AI is becoming a coding partner, not a replacement. Think pair programming with
    an infinitely patient colleague who knows every programming language.

    Here's what I'm seeing in the wild: teams using AI for boilerplate code, documentation,
    and bug fixes. The real humans? They're focusing on architecture and creative problem-solving.
    It's a beautiful division of labor.

    My two cents: embrace it early. The learning curve is steep but worth it.
    """,
    """
    Let's talk about something nobody's discussing: AI safety theater.

    Companies are adding "AI ethics" teams like they're collecting Pokemon cards. But here's
    the reality - most of these initiatives are smoke and mirrors. Real AI safety requires
    technical depth, not PR departments.

    What actually matters? Red team testing. Adversarial inputs. Failure mode analysis.
    The boring stuff that doesn't make headlines but prevents disasters.

    If your AI safety plan fits on a PowerPoint slide, you don't have a plan. You have
    a marketing campaign. Do better.
    """,
    """
    Ever notice how AI news cycles work? Here's the pattern I've spotted.

    Week 1: New model drops, everyone freaks out about capabilities.
    Week 2: Researchers find edge cases where it fails spectacularly.
    Week 3: Think pieces about how it's "not really intelligent."
    Week 4: Silent integration into products we use daily.

    Rinse and repeat. It's predictable at this point. But that Week 4 part? That's where
    the real revolution happens. Nobody notices until it's everywhere.

    Watch the integration phase, not the announcement phase. That's where value gets created.
    """,
    """
    Hot take: most AI demos are designed to impress, not inform.

    You've seen them - carefully curated examples showing flawless performance. But reality?
    It's messier. AI works great on textbook problems and struggles with edge cases your
    users will definitely encounter.

    Here's my litmus test: if the demo doesn't show failure cases, it's not ready for
    production. Good AI products acknowledge limitations. Great ones design around them.

    Don't believe the hype without verification. Test it yourself, on your data, with your
    use cases. That's the only truth that matters.
    """,
    """
    Let me tell you about the AI adoption curve I'm seeing in enterprises.

    Stage 1: Excitement and pilot projects everywhere. Everyone wants an AI strategy.
    Stage 2: Reality check. Most pilots fail or deliver mediocre results.
    Stage 3: The survivors double down, learn from failures, and build something real.

    We're currently between Stage 2 and 3. The hype bubble is deflating, but serious
    work is ramping up. This is when the winners separate from the wannabes.

    If you're in Stage 1, skip to Stage 3. Learn from other people's mistakes. There's
    enough public failure data now that you don't need to repeat it.
    """,
    """
    Quick insight on AI model selection: bigger isn't always better.

    I see companies defaulting to GPT-4 for everything. But here's the secret - smaller,
    fine-tuned models often outperform on specific tasks. Plus they're faster and cheaper.

    Think of it like hiring. You wouldn't hire a CEO to answer customer support tickets.
    Same logic applies to AI models. Match the model to the task complexity.

    For simple classification? A fine-tuned BERT crushes GPT-4 at 1/100th the cost.
    For complex reasoning? Sure, go big. But be strategic about it.

    Work smarter, not more expensive.
    """
]

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
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
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

    return success


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_train_style_profile():
    """Test 1: Train style profile from samples."""
    data = {
        "workspace_id": WORKSPACE_ID,
        "samples": SAMPLE_NEWSLETTERS,
        "retrain": False
    }

    response = make_request("POST", "/style/train", data=data)
    return print_result("Train Style Profile", response)


def test_get_style_profile():
    """Test 2: Get complete style profile."""
    response = make_request("GET", f"/style/{WORKSPACE_ID}")
    return print_result("Get Style Profile", response)


def test_get_style_summary():
    """Test 3: Get style profile summary."""
    response = make_request("GET", f"/style/{WORKSPACE_ID}/summary")
    return print_result("Get Style Summary", response)


def test_generate_style_prompt():
    """Test 4: Generate style-specific prompt."""
    data = {
        "workspace_id": WORKSPACE_ID
    }

    response = make_request("POST", "/style/prompt", data=data)
    return print_result("Generate Style Prompt", response)


def test_update_style_profile():
    """Test 5: Update style profile fields."""
    data = {
        "formality_level": 0.4,
        "uses_emojis": False,
        "section_count": 5
    }

    response = make_request("PUT", f"/style/{WORKSPACE_ID}", data=data)
    return print_result("Update Style Profile", response)


def test_retrain_style_profile():
    """Test 6: Retrain existing profile (with retrain=True)."""
    data = {
        "workspace_id": WORKSPACE_ID,
        "samples": SAMPLE_NEWSLETTERS[:5],  # Use fewer samples
        "retrain": True
    }

    response = make_request("POST", "/style/train", data=data)
    return print_result("Retrain Style Profile", response)


def test_delete_style_profile():
    """Test 7: Delete style profile."""
    response = make_request("DELETE", f"/style/{WORKSPACE_ID}")
    return print_result("Delete Style Profile", response)


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all style API tests."""
    print("\n" + "="*80)
    print("STYLE TRAINING API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Workspace ID: {WORKSPACE_ID}")
    print(f"Number of sample newsletters: {len(SAMPLE_NEWSLETTERS)}")

    results = []

    # Test sequence
    tests = [
        ("1. Train Style Profile", test_train_style_profile),
        ("2. Get Style Profile", test_get_style_profile),
        ("3. Get Style Summary", test_get_style_summary),
        ("4. Generate Style Prompt", test_generate_style_prompt),
        ("5. Update Style Profile", test_update_style_profile),
        ("6. Retrain Style Profile", test_retrain_style_profile),
        ("7. Delete Style Profile", test_delete_style_profile),
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
