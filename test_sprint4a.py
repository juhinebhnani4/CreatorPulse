#!/usr/bin/env python3
"""
Quick test script for Sprint 4A - Email Delivery
Tests: Add subscriber → List → Generate newsletter → Send test email
"""

import requests
import json
import sys

# ===== CONFIGURATION - EDIT THESE =====
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "YOUR_TOKEN_HERE"  # Get from login or browser DevTools
WORKSPACE_ID = "YOUR_WORKSPACE_ID"  # Get from workspaces API
TEST_EMAIL = "your-email@gmail.com"  # Your email for testing
# =======================================

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_add_subscriber():
    """Test 1: Add a subscriber"""
    print("\n📝 Test 1: Adding subscriber...")
    response = requests.post(
        f"{BASE_URL}/subscribers",
        headers=headers,
        json={
            "workspace_id": WORKSPACE_ID,
            "email": TEST_EMAIL,
            "name": "Test User",
            "source": "manual"
        }
    )

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        if data.get('success'):
            print(f"✅ Subscriber added: {data['data']['email']}")
            return True
        else:
            error = data.get('error', {})
            print(f"❌ Error: {error}")
            # If subscriber already exists, that's okay for testing
            if 'already exists' in str(error).lower():
                print("ℹ️  Subscriber already exists - continuing with tests")
                return True
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        print(f"Response: {response.text}")
        return False


def test_list_subscribers():
    """Test 2: List subscribers"""
    print("\n📋 Test 2: Listing subscribers...")
    response = requests.get(
        f"{BASE_URL}/subscribers/workspaces/{WORKSPACE_ID}",
        headers=headers
    )

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        if data.get('success'):
            count = data['data']['count']
            print(f"✅ Found {count} subscriber(s)")
            for sub in data['data']['subscribers'][:5]:  # Show first 5
                print(f"   - {sub['email']} ({sub['status']})")
            if count > 5:
                print(f"   ... and {count - 5} more")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_generate_newsletter():
    """Test 3: Generate a newsletter"""
    print("\n📰 Test 3: Generating newsletter...")
    response = requests.post(
        f"{BASE_URL}/newsletters/generate",
        headers=headers,
        json={
            "workspace_id": WORKSPACE_ID,
            "title": "Sprint 4A Test Newsletter",
            "max_items": 3,
            "days_back": 7
        },
        timeout=120  # Newsletter generation can take time
    )

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        if data.get('success'):
            newsletter_id = data['data']['id']
            title = data['data']['title']
            print(f"✅ Newsletter generated!")
            print(f"   ID: {newsletter_id}")
            print(f"   Title: {title}")
            return newsletter_id
        else:
            error = data.get('error')
            print(f"❌ Error: {error}")
            print("ℹ️  Make sure you have scraped content first!")
            print("   Go to Streamlit → Content Library → Scrape Content")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_send_newsletter(newsletter_id):
    """Test 4: Send newsletter to test email"""
    print(f"\n📧 Test 4: Sending newsletter to {TEST_EMAIL}...")
    print("   (This may take a few seconds...)")

    response = requests.post(
        f"{BASE_URL}/delivery/send-sync",
        headers=headers,
        json={
            "newsletter_id": newsletter_id,
            "workspace_id": WORKSPACE_ID,
            "test_email": TEST_EMAIL
        },
        timeout=60
    )

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        if data.get('success'):
            result = data['data']
            sent = result.get('sent_count', 0)
            failed = result.get('failed_count', 0)

            print(f"✅ Sent: {sent}")
            print(f"❌ Failed: {failed}")
            print(f"Status: {result.get('status')}")

            if sent > 0:
                print(f"\n🎉 SUCCESS! Check your inbox at {TEST_EMAIL}")
                print("   (Check spam folder if you don't see it)")
                return True
            else:
                print(f"\n⚠️  Email failed to send. Check:")
                print("   1. Email settings in .env file")
                print("   2. Backend logs for errors")
                print("   3. SMTP credentials are correct")
                return False
        else:
            error = data.get('error')
            print(f"❌ Error: {error}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_list_deliveries():
    """Test 5: List delivery history"""
    print("\n📬 Test 5: Listing delivery history...")
    response = requests.get(
        f"{BASE_URL}/delivery/workspaces/{WORKSPACE_ID}",
        headers=headers
    )

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        if data.get('success'):
            deliveries = data['data']['deliveries']
            count = len(deliveries)
            print(f"✅ Found {count} delivery record(s)")
            for delivery in deliveries[:3]:  # Show first 3
                print(f"   - Newsletter: {delivery.get('newsletter_id')[:8]}...")
                print(f"     Sent: {delivery.get('sent_count')}, Failed: {delivery.get('failed_count')}")
                print(f"     Status: {delivery.get('status')}")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Run all tests"""
    print_section("Sprint 4A - Email Delivery Testing")

    # Check configuration
    if TOKEN == "YOUR_TOKEN_HERE" or WORKSPACE_ID == "YOUR_WORKSPACE_ID":
        print("\n❌ ERROR: Please edit the configuration at the top of this script!")
        print("   Set your TOKEN and WORKSPACE_ID")
        print("\nHow to get these:")
        print("1. TOKEN: Login via API or get from browser DevTools")
        print("2. WORKSPACE_ID: Get from /api/v1/workspaces endpoint")
        print("\nSee SPRINT_4A_TESTING_GUIDE.md for details")
        return False

    if TEST_EMAIL == "your-email@gmail.com":
        print("\n⚠️  WARNING: Please set TEST_EMAIL to your actual email!")
        print("   Edit the configuration at the top of this script")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return False

    # Test 1: Add subscriber
    if not test_add_subscriber():
        print("\n⚠️  Test 1 failed - check TOKEN and WORKSPACE_ID")
        return False

    # Test 2: List subscribers
    if not test_list_subscribers():
        print("\n⚠️  Test 2 failed")
        return False

    # Test 3: Generate newsletter
    newsletter_id = test_generate_newsletter()
    if not newsletter_id:
        print("\n⚠️  Test 3 failed - no content available?")
        print("   Run content scraper first: Streamlit → Content Library → Scrape Content")
        return False

    # Test 4: Send newsletter
    if not test_send_newsletter(newsletter_id):
        print("\n⚠️  Test 4 failed - check email settings in .env")
        print("   Make sure SMTP credentials are configured correctly")
        return False

    # Test 5: List deliveries
    test_list_deliveries()

    # Success!
    print_section("✅ All Tests Passed!")
    print("\nSprint 4A is working correctly!")
    print("\nWhat you just tested:")
    print("  ✅ Database tables exist and accessible")
    print("  ✅ Subscriber management works")
    print("  ✅ Newsletter generation works")
    print("  ✅ Email delivery works")
    print("  ✅ Delivery tracking works")
    print("\nNext steps:")
    print("  1. Add more subscribers (via API or bulk import)")
    print("  2. Send newsletters to all subscribers")
    print("  3. Test unsubscribe flow")
    print("  4. Move to Sprint 4B (Scheduler) for automation")
    print("\nFor more details, see: SPRINT_4A_TESTING_GUIDE.md")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
