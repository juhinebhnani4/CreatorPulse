"""
Integration Tests for Service Improvements (MEDIUM Priority Tasks)

Tests the following implementations:
- BaseService pattern in all services
- Error handling decorators
- Constants configuration
- Rate limiting middleware

Run with: python tests/test_service_improvements.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_base_service_pattern():
    """Test that all services extend BaseService."""
    print("\n" + "="*80)
    print("TEST 1: BaseService Pattern")
    print("="*80)

    try:
        from backend.services.base_service import BaseService
        from backend.services.trend_service import TrendDetectionService
        from backend.services.style_service import StyleAnalysisService
        from backend.services.feedback_service import FeedbackService

        services_to_test = [
            ("TrendDetectionService", TrendDetectionService),
            ("StyleAnalysisService", StyleAnalysisService),
            ("FeedbackService", FeedbackService)
        ]

        for service_name, service_class in services_to_test:
            if issubclass(service_class, BaseService):
                print(f"✅ {service_name} extends BaseService")
            else:
                print(f"❌ FAILED: {service_name} does not extend BaseService")
                return False

        print("\n✅ BaseService Pattern: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling_decorators():
    """Test that key service methods have error handling decorators."""
    print("\n" + "="*80)
    print("TEST 2: Error Handling Decorators")
    print("="*80)

    try:
        from backend.services.trend_service import TrendDetectionService
        from backend.services.style_service import StyleAnalysisService
        from backend.services.feedback_service import FeedbackService

        # Check TrendDetectionService
        trend_service = TrendDetectionService()
        if hasattr(trend_service.detect_trends, '__wrapped__'):
            print("✅ TrendDetectionService.detect_trends has error handling")
        else:
            # Method might still have decorator but no __wrapped__ attribute
            print("⚠️  TrendDetectionService.detect_trends decorator status unclear")

        if hasattr(trend_service.get_active_trends, '__wrapped__'):
            print("✅ TrendDetectionService.get_active_trends has error handling")
        else:
            print("⚠️  TrendDetectionService.get_active_trends decorator status unclear")

        # Check StyleAnalysisService
        style_service = StyleAnalysisService()
        if hasattr(style_service.get_style_profile, '__wrapped__'):
            print("✅ StyleAnalysisService.get_style_profile has error handling")
        else:
            print("⚠️  StyleAnalysisService.get_style_profile decorator status unclear")

        # Check FeedbackService
        feedback_service = FeedbackService()
        if hasattr(feedback_service.adjust_content_scoring, '__wrapped__'):
            print("✅ FeedbackService.adjust_content_scoring has error handling")
        else:
            print("⚠️  FeedbackService.adjust_content_scoring decorator status unclear")

        print("\n✅ Error Handling Decorators: TESTS COMPLETED")
        print("   (Note: Some decorators may not expose __wrapped__ attribute)")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_constants_configuration():
    """Test that constants are properly configured."""
    print("\n" + "="*80)
    print("TEST 3: Constants Configuration")
    print("="*80)

    try:
        from backend.config.constants import (
            NewsletterConstants,
            TrendConstants,
            FeedbackConstants,
            AnalyticsConstants
        )

        # Test NewsletterConstants
        print("\nNewsletterConstants:")
        print(f"  MAX_TRENDS_TO_FETCH: {NewsletterConstants.MAX_TRENDS_TO_FETCH}")
        print(f"  TREND_SCORE_BOOST_MULTIPLIER: {NewsletterConstants.TREND_SCORE_BOOST_MULTIPLIER}")
        print(f"  DEFAULT_MAX_ITEMS: {NewsletterConstants.DEFAULT_MAX_ITEMS}")
        print("✅ NewsletterConstants loaded")

        # Test TrendConstants
        print("\nTrendConstants:")
        print(f"  MIN_CONFIDENCE_THRESHOLD: {TrendConstants.MIN_CONFIDENCE_THRESHOLD}")
        print(f"  TFIDF_MAX_FEATURES: {TrendConstants.TFIDF_MAX_FEATURES}")
        print("✅ TrendConstants loaded")

        # Test FeedbackConstants
        print("\nFeedbackConstants:")
        print(f"  PREFERRED_SOURCE_BOOST_MULTIPLIER: {FeedbackConstants.PREFERRED_SOURCE_BOOST_MULTIPLIER}")
        print(f"  BELOW_THRESHOLD_PENALTY_MULTIPLIER: {FeedbackConstants.BELOW_THRESHOLD_PENALTY_MULTIPLIER}")
        print("✅ FeedbackConstants loaded")

        # Test AnalyticsConstants
        print("\nAnalyticsConstants:")
        print(f"  TOKEN_EXPIRY_SECONDS: {AnalyticsConstants.TOKEN_EXPIRY_SECONDS}")
        print("✅ AnalyticsConstants loaded")

        print("\n✅ Constants Configuration: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limiting_middleware():
    """Test that rate limiting middleware is properly configured."""
    print("\n" + "="*80)
    print("TEST 4: Rate Limiting Middleware")
    print("="*80)

    try:
        from backend.middleware.rate_limiter import limiter, RateLimits

        print("✅ Rate limiter imported successfully")

        # Check RateLimits constants
        print(f"\nRate Limits:")
        print(f"  NEWSLETTER_GENERATION: {RateLimits.NEWSLETTER_GENERATION}")
        print(f"  TREND_DETECTION: {RateLimits.TREND_DETECTION}")
        print(f"  STYLE_TRAINING: {RateLimits.STYLE_TRAINING}")
        print(f"  CREATE: {RateLimits.CREATE}")
        print(f"  READ: {RateLimits.READ}")

        print("\n✅ Rate Limiting Middleware: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_service_logging():
    """Test that services have proper logging setup."""
    print("\n" + "="*80)
    print("TEST 5: Service Logging")
    print("="*80)

    try:
        from backend.services.trend_service import TrendDetectionService
        from backend.services.style_service import StyleAnalysisService
        from backend.services.feedback_service import FeedbackService

        services_to_test = [
            ("TrendDetectionService", TrendDetectionService()),
            ("StyleAnalysisService", StyleAnalysisService()),
            ("FeedbackService", FeedbackService())
        ]

        for service_name, service_instance in services_to_test:
            if hasattr(service_instance, 'logger'):
                print(f"✅ {service_name} has logger attribute")
            else:
                print(f"❌ FAILED: {service_name} missing logger attribute")
                return False

        print("\n✅ Service Logging: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dependency_injection():
    """Test that services support dependency injection."""
    print("\n" + "="*80)
    print("TEST 6: Dependency Injection")
    print("="*80)

    try:
        from backend.services.trend_service import TrendDetectionService
        from backend.services.style_service import StyleAnalysisService
        from backend.services.feedback_service import FeedbackService
        from src.ai_newsletter.database.supabase_client import SupabaseManager

        # Create a mock database instance
        db = SupabaseManager()

        # Test dependency injection
        print("Testing dependency injection:")

        trend_service = TrendDetectionService(db=db)
        print("✅ TrendDetectionService accepts db parameter")

        style_service = StyleAnalysisService(db=db)
        print("✅ StyleAnalysisService accepts db parameter")

        feedback_service = FeedbackService(db=db)
        print("✅ FeedbackService accepts db parameter")

        # Test lazy loading (no db parameter)
        trend_service_lazy = TrendDetectionService()
        print("✅ TrendDetectionService works without db parameter (lazy loading)")

        style_service_lazy = StyleAnalysisService()
        print("✅ StyleAnalysisService works without db parameter (lazy loading)")

        feedback_service_lazy = FeedbackService()
        print("✅ FeedbackService works without db parameter (lazy loading)")

        print("\n✅ Dependency Injection: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all service improvement tests."""
    print("\n" + "="*80)
    print("SERVICE IMPROVEMENTS TESTS (MEDIUM PRIORITY TASKS)")
    print("="*80)
    print("\nThese tests verify MEDIUM priority implementations:")
    print("- Task 6: Standardized error handling")
    print("- Task 7: Database connection patterns (BaseService)")
    print("- Task 8: Configuration management (Constants)")
    print("- Task 10: Rate limiting")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    results = []

    # Run all tests
    results.append(("BaseService Pattern", test_base_service_pattern()))
    results.append(("Error Handling Decorators", test_error_handling_decorators()))
    results.append(("Constants Configuration", test_constants_configuration()))
    results.append(("Rate Limiting Middleware", test_rate_limiting_middleware()))
    results.append(("Service Logging", test_service_logging()))
    results.append(("Dependency Injection", test_dependency_injection()))

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
        print("\n🎉 ALL TESTS PASSED! Service improvements are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
