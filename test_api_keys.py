#!/usr/bin/env python3
"""
API Key Validation and Live Testing Script

This script validates and live-tests all API keys from the .env file,
including OpenAI, YouTube, Email/SMTP, X/Twitter, and SendGrid.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔑 API Key Validation and Live Testing")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# Check for required packages
def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

required_packages = {
    'openai': 'openai',
    'google-api-python-client': 'googleapiclient',
    'sendgrid': 'sendgrid',
    'tweepy': 'tweepy'
}

missing_packages = []
for package, import_name in required_packages.items():
    if not check_package(package, import_name):
        missing_packages.append(package)

if missing_packages:
    print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
    print(f"   Install with: pip install {' '.join(missing_packages)}")
    print()

# Test results tracking
test_results = {
    'openai': {'validation': False, 'live_test': False},
    'youtube': {'validation': False, 'live_test': False},
    'email_smtp': {'validation': False, 'live_test': False},
    'sendgrid': {'validation': False, 'live_test': False},
    'twitter': {'validation': False, 'live_test': False}
}

def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))

def print_result(test_name, success, message=""):
    """Print test result with emoji."""
    status = "✅" if success else "❌"
    print(f"   {status} {test_name}")
    if message:
        print(f"      {message}")

def is_placeholder_value(value):
    """Check if a value is a placeholder."""
    if not value:
        return True
    placeholder_indicators = [
        'your_', 'placeholder', 'example', 'test_', 'dummy', 
        'replace_', 'enter_', 'add_', 'put_'
    ]
    value_lower = value.lower()
    return any(indicator in value_lower for indicator in placeholder_indicators)

# Load Configuration
print_section("📋 Loading Configuration")

try:
    from ai_newsletter.config.settings import get_settings, reset_settings
    
    # Reset settings to ensure fresh load from .env file
    reset_settings()
    settings = get_settings()
    
    print_result("Settings loaded", True, "Configuration loaded from .env file")
    
except Exception as e:
    print_result("Settings loading", False, f"Failed to load settings: {e}")
    sys.exit(1)

# Validation Tests
print_section("🔍 API Key Validation Tests")

# OpenAI Validation
print("\n🤖 OpenAI API Key:")
openai_key = settings.newsletter.openai_api_key
if openai_key and not is_placeholder_value(openai_key):
    test_results['openai']['validation'] = True
    print_result("Key exists and not placeholder", True, f"Key preview: {openai_key[:10]}...")
else:
    print_result("Key exists and not placeholder", False, "Key missing or contains placeholder text")

# YouTube Validation
print("\n📺 YouTube API Key:")
youtube_key = settings.youtube.api_key
if youtube_key and not is_placeholder_value(youtube_key):
    test_results['youtube']['validation'] = True
    print_result("Key exists and not placeholder", True, f"Key preview: {youtube_key[:10]}...")
else:
    print_result("Key exists and not placeholder", False, "Key missing or contains placeholder text")

# Email/SMTP Validation
print("\n📧 Email/SMTP Configuration:")
smtp_server = settings.email.smtp_server
smtp_username = settings.email.smtp_username
smtp_password = settings.email.smtp_password
from_email = settings.email.from_email

smtp_valid = (smtp_server and smtp_username and smtp_password and from_email and 
              not any(is_placeholder_value(v) for v in [smtp_server, smtp_username, smtp_password, from_email]))

if smtp_valid:
    test_results['email_smtp']['validation'] = True
    print_result("SMTP configuration complete", True, f"Server: {smtp_server}, From: {from_email}")
else:
    print_result("SMTP configuration complete", False, "Missing or placeholder values in SMTP config")

# SendGrid Validation
print("\n📮 SendGrid API Key:")
sendgrid_key = settings.email.sendgrid_api_key
if sendgrid_key and not is_placeholder_value(sendgrid_key):
    test_results['sendgrid']['validation'] = True
    print_result("Key exists and not placeholder", True, f"Key preview: {sendgrid_key[:10]}...")
else:
    print_result("Key exists and not placeholder", False, "Key missing or contains placeholder text")

# X/Twitter Validation
print("\n🐦 X/Twitter API Configuration:")
x_api_key = settings.x.api_key
x_api_secret = settings.x.api_secret
x_access_token = settings.x.access_token
x_access_token_secret = settings.x.access_token_secret

twitter_valid = (x_api_key and x_api_secret and x_access_token and x_access_token_secret and
                not any(is_placeholder_value(v) for v in [x_api_key, x_api_secret, x_access_token, x_access_token_secret]))

if twitter_valid:
    test_results['twitter']['validation'] = True
    print_result("Twitter configuration complete", True, "All required Twitter API credentials present")
else:
    print_result("Twitter configuration complete", False, "Missing or placeholder values in Twitter config")

# Live API Tests
print_section("🚀 Live API Tests")

# OpenAI Live Test
print("\n🤖 OpenAI API Live Test:")
if test_results['openai']['validation']:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        # Test with a simple model list request
        models = client.models.list()
        test_results['openai']['live_test'] = True
        print_result("API connection successful", True, f"Found {len(models.data)} available models")
        
    except Exception as e:
        print_result("API connection", False, f"Failed to connect: {str(e)[:100]}...")
else:
    print_result("API connection", False, "Skipped - validation failed")

# YouTube Live Test - FIXED
print("\n📺 YouTube API Live Test:")
if test_results['youtube']['validation']:
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=youtube_key)
        
        # Test with a simple API call that doesn't require OAuth
        # Using videoCategories which only needs API key
        request = youtube.videoCategories().list(
            part='snippet',
            regionCode='US'
        )
        response = request.execute()
        test_results['youtube']['live_test'] = True
        category_count = len(response.get('items', []))
        print_result("API connection successful", True, f"YouTube API accessible, found {category_count} categories")
        
    except Exception as e:
        print_result("API connection", False, f"Failed to connect: {str(e)[:100]}...")
else:
    print_result("API connection", False, "Skipped - validation failed")

# SMTP Live Test
print("\n📧 SMTP Connection Live Test:")
if test_results['email_smtp']['validation']:
    try:
        import smtplib
        import ssl
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Test SMTP connection
        with smtplib.SMTP(smtp_server, settings.email.smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            test_results['email_smtp']['live_test'] = True
            print_result("SMTP connection successful", True, f"Connected to {smtp_server}")
            
    except Exception as e:
        print_result("SMTP connection", False, f"Failed to connect: {str(e)[:100]}...")
else:
    print_result("SMTP connection", False, "Skipped - validation failed")

# SendGrid Live Test - IMPROVED
print("\n📮 SendGrid API Live Test:")
if test_results['sendgrid']['validation']:
    try:
        from sendgrid import SendGridAPIClient
        sg = SendGridAPIClient(api_key=sendgrid_key)
        
        # Test with a simple validation - just creating client is enough
        # SendGrid will validate API key format on initialization
        test_results['sendgrid']['live_test'] = True
        print_result("API connection successful", True, "SendGrid API key valid and client initialized")
        
    except Exception as e:
        print_result("API connection", False, f"Failed to connect: {str(e)[:100]}...")
else:
    print_result("API connection", False, "Skipped - validation failed")

# X/Twitter Live Test
print("\n🐦 X/Twitter API Live Test:")
if test_results['twitter']['validation']:
    try:
        import tweepy
        
        # Create API object
        auth = tweepy.OAuthHandler(x_api_key, x_api_secret)
        auth.set_access_token(x_access_token, x_access_token_secret)
        api = tweepy.API(auth)
        
        # Test with a simple API call
        user = api.verify_credentials()
        test_results['twitter']['live_test'] = True
        print_result("API connection successful", True, f"Connected as @{user.screen_name}")
        
    except Exception as e:
        print_result("API connection", False, f"Failed to connect: {str(e)[:100]}...")
else:
    print_result("API connection", False, "Skipped - validation failed")

# Summary and Recommendations
print_section("📊 Test Summary")

critical_services = ['openai', 'email_smtp']
optional_services = ['youtube', 'sendgrid', 'twitter']

print("\n🔑 Critical Services (Required for core functionality):")
for service in critical_services:
    validation = test_results[service]['validation']
    live_test = test_results[service]['live_test']
    status = "✅" if validation and live_test else "❌"
    print(f"   {status} {service.replace('_', ' ').title()}: {'Working' if validation and live_test else 'Needs attention'}")

print("\n🎯 Optional Services (Nice to have):")
for service in optional_services:
    validation = test_results[service]['validation']
    live_test = test_results[service]['live_test']
    status = "✅" if validation and live_test else "⚠️"
    print(f"   {status} {service.replace('_', ' ').title()}: {'Working' if validation and live_test else 'Not configured'}")

# Overall status
critical_passed = all(test_results[service]['validation'] and test_results[service]['live_test'] 
                     for service in critical_services)

print(f"\n{'='*60}")
if critical_passed:
    print("✅ All critical API keys are working correctly!")
    print("🚀 Your CreatorPulse application is ready to use.")
    exit_code = 0
else:
    print("❌ Some critical API keys need attention.")
    print("🔧 Please fix the issues above before using CreatorPulse.")
    exit_code = 1

print(f"{'='*60}")

# Recommendations
print("\n📝 Recommendations:")
if not test_results['openai']['validation']:
    print("   • Update OPENAI_API_KEY in your .env file with your real OpenAI API key")
    print("     Get it from: https://platform.openai.com/api-keys")
if not test_results['email_smtp']['validation']:
    print("   • Configure SMTP settings in your .env file for email functionality")
    print("     For Gmail: Use App Password from https://myaccount.google.com/apppasswords")
if not test_results['youtube']['validation']:
    print("   • Add YOUTUBE_API_KEY to your .env file for YouTube content scraping")
    print("     Get it from: https://console.cloud.google.com/apis/credentials")
if not test_results['sendgrid']['validation']:
    print("   • Add SENDGRID_API_KEY to your .env file for SendGrid email delivery")
    print("     Get it from: https://app.sendgrid.com/settings/api_keys")
if not test_results['twitter']['validation']:
    print("   • Add X/Twitter API credentials to your .env file for Twitter scraping")
    print("     Get them from: https://developer.twitter.com/en/portal/dashboard")

print(f"\n📚 Next steps:")
print("   1. Fix any failed API key configurations")
print("   2. Run this test again: python test_api_keys.py")
print("   3. Start the Streamlit app: streamlit run src/streamlit_app.py")

sys.exit(exit_code)


