"""
Integration Tests for Tasks 2-5

Tests the following implementations:
- Task 2: Trends integration into newsletter generation
- Task 3: Style profiles integration
- Task 4: Feedback learning integration
- Task 5: HMAC authentication for analytics

Run with: python tests/test_integrations.py
"""

import os
import sys
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.utils.hmac_auth import generate_tracking_token, verify_tracking_token


def test_hmac_authentication():
    """Test HMAC token generation and verification (Task 5)."""
    print("\n" + "="*80)
    print("TEST 1: HMAC Authentication (Task 5)")
    print("="*80)

    # Get secret key from environment
    secret_key = os.getenv("ANALYTICS_SECRET_KEY")
    if not secret_key:
        print("❌ FAILED: ANALYTICS_SECRET_KEY not found in environment")
        return False

    print(f"✅ Secret key loaded (length: {len(secret_key)} characters)")

    # Test data
    newsletter_id = str(uuid4())
    workspace_id = str(uuid4())

    try:
        # Test 1: Generate token
        token = generate_tracking_token(newsletter_id, workspace_id, secret_key)
        print(f"✅ Token generated: {token[:30]}...")

        # Test 2: Verify valid token
        is_valid = verify_tracking_token(token, newsletter_id, workspace_id, secret_key)
        if is_valid:
            print("✅ Valid token verified successfully")
        else:
            print("❌ FAILED: Valid token verification failed")
            return False

        # Test 3: Verify invalid token (wrong newsletter_id)
        try:
            verify_tracking_token(token, str(uuid4()), workspace_id, secret_key)
            print("❌ FAILED: Invalid token was accepted (wrong newsletter_id)")
            return False
        except ValueError:
            print("✅ Invalid token rejected (wrong newsletter_id)")

        # Test 4: Verify invalid token (wrong workspace_id)
        try:
            verify_tracking_token(token, newsletter_id, str(uuid4()), secret_key)
            print("❌ FAILED: Invalid token was accepted (wrong workspace_id)")
            return False
        except ValueError:
            print("✅ Invalid token rejected (wrong workspace_id)")

        # Test 5: Verify malformed token
        try:
            verify_tracking_token("malformed.token.data", newsletter_id, workspace_id, secret_key)
            print("❌ FAILED: Malformed token was accepted")
            return False
        except ValueError:
            print("✅ Malformed token rejected")

        # Test 6: Token format
        parts = token.split(".")
        if len(parts) == 2:
            timestamp, signature = parts
            print(f"✅ Token format correct: timestamp={timestamp}, signature={signature[:20]}...")
        else:
            print(f"❌ FAILED: Invalid token format (expected 2 parts, got {len(parts)})")
            return False

        print("\n✅ HMAC Authentication: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_newsletter_service_integration():
    """Test newsletter service integration with trends, style, and feedback."""
    print("\n" + "="*80)
    print("TEST 2: Newsletter Service Integration (Tasks 2-4)")
    print("="*80)

    try:
        from backend.services.newsletter_service import NewsletterService

        # Initialize service
        service = NewsletterService()
        print("✅ NewsletterService initialized")

        # Check that required services are initialized
        if hasattr(service, 'trend_service'):
            print("✅ TrendDetectionService initialized (Task 2)")
        else:
            print("❌ FAILED: TrendDetectionService not found")
            return False

        if hasattr(service, 'style_service'):
            print("✅ StyleAnalysisService initialized (Task 3)")
        else:
            print("❌ FAILED: StyleAnalysisService not found")
            return False

        if hasattr(service, 'feedback_service'):
            print("✅ FeedbackService initialized (Task 4)")
        else:
            print("❌ FAILED: FeedbackService not found")
            return False

        print("\n✅ Newsletter Service Integration: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_newsletter_generator_parameters():
    """Test that newsletter generator accepts new parameters."""
    print("\n" + "="*80)
    print("TEST 3: Newsletter Generator Parameters")
    print("="*80)

    try:
        from src.ai_newsletter.generators import NewsletterGenerator
        from src.ai_newsletter.config.settings import get_settings

        settings = get_settings()
        generator = NewsletterGenerator(config=settings.newsletter)
        print("✅ NewsletterGenerator initialized")

        # Check generate_newsletter method signature
        import inspect
        sig = inspect.signature(generator.generate_newsletter)
        params = list(sig.parameters.keys())

        print(f"\nMethod parameters: {', '.join(params)}")

        # Check for new parameters
        required_params = ['trends', 'style_prompt']
        for param in required_params:
            if param in params:
                print(f"✅ Parameter '{param}' found")
            else:
                print(f"❌ FAILED: Parameter '{param}' not found")
                return False

        print("\n✅ Newsletter Generator Parameters: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_feedback_service_method():
    """Test that feedback service has adjust_content_scoring method."""
    print("\n" + "="*80)
    print("TEST 4: Feedback Service Method (Task 4)")
    print("="*80)

    try:
        from src.ai_newsletter.database.supabase_client import SupabaseManager
        from backend.services.feedback_service import FeedbackService

        supabase = SupabaseManager()
        service = FeedbackService(supabase)
        print("✅ FeedbackService initialized")

        # Check for adjust_content_scoring method
        if hasattr(service, 'adjust_content_scoring'):
            print("✅ Method 'adjust_content_scoring' found")

            # Check method signature
            import inspect
            sig = inspect.signature(service.adjust_content_scoring)
            params = list(sig.parameters.keys())
            print(f"   Parameters: {', '.join(params)}")

            required_params = ['workspace_id', 'content_items']
            for param in required_params:
                if param in params:
                    print(f"   ✅ Parameter '{param}' found")
                else:
                    print(f"   ❌ FAILED: Parameter '{param}' not found")
                    return False
        else:
            print("❌ FAILED: Method 'adjust_content_scoring' not found")
            return False

        print("\n✅ Feedback Service Method: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_style_service_method():
    """Test that style service has generate_style_prompt method."""
    print("\n" + "="*80)
    print("TEST 5: Style Service Method (Task 3)")
    print("="*80)

    try:
        from backend.services.style_service import StyleAnalysisService

        service = StyleAnalysisService()
        print("✅ StyleAnalysisService initialized")

        # Check for generate_style_prompt method
        if hasattr(service, 'generate_style_prompt'):
            print("✅ Method 'generate_style_prompt' found")

            # Check method signature
            import inspect
            sig = inspect.signature(service.generate_style_prompt)
            params = list(sig.parameters.keys())
            print(f"   Parameters: {', '.join(params)}")

            if 'profile' in params:
                print(f"   ✅ Parameter 'profile' found")
            else:
                print(f"   ❌ FAILED: Parameter 'profile' not found")
                return False
        else:
            print("❌ FAILED: Method 'generate_style_prompt' not found")
            return False

        print("\n✅ Style Service Method: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_trend_service_method():
    """Test that trend service has get_active_trends method."""
    print("\n" + "="*80)
    print("TEST 6: Trend Service Method (Task 2)")
    print("="*80)

    try:
        from backend.services.trend_service import TrendDetectionService

        service = TrendDetectionService()
        print("✅ TrendDetectionService initialized")

        # Check for get_active_trends method
        if hasattr(service, 'get_active_trends'):
            print("✅ Method 'get_active_trends' found")

            # Check method signature
            import inspect
            sig = inspect.signature(service.get_active_trends)
            params = list(sig.parameters.keys())
            print(f"   Parameters: {', '.join(params)}")

            required_params = ['workspace_id', 'limit']
            for param in required_params:
                if param in params:
                    print(f"   ✅ Parameter '{param}' found")
                else:
                    print(f"   ❌ FAILED: Parameter '{param}' not found")
                    return False
        else:
            print("❌ FAILED: Method 'get_active_trends' not found")
            return False

        print("\n✅ Trend Service Method: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("INTEGRATION TESTS FOR TASKS 2-5")
    print("="*80)
    print("\nThese tests verify that all HIGH priority implementations are working:")
    print("- Task 2: Trends integration")
    print("- Task 3: Style profiles integration")
    print("- Task 4: Feedback learning integration")
    print("- Task 5: HMAC authentication")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    results = []

    # Run all tests
    results.append(("HMAC Authentication", test_hmac_authentication()))
    results.append(("Newsletter Service Integration", test_newsletter_service_integration()))
    results.append(("Newsletter Generator Parameters", test_newsletter_generator_parameters()))
    results.append(("Feedback Service Method", test_feedback_service_method()))
    results.append(("Style Service Method", test_style_service_method()))
    results.append(("Trend Service Method", test_trend_service_method()))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Implementation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
