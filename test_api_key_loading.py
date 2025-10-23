"""Test if Anthropic API key is being loaded correctly from .env"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 80)
print("API KEY DIAGNOSTIC TEST")
print("=" * 80)

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key:
    print(f"[OK] API key found in environment")
    print(f"  First 20 chars: {api_key[:20]}...")
    print(f"  Last 10 chars: ...{api_key[-10:]}")
    print(f"  Total length: {len(api_key)} characters")
    print(f"  Starts with 'sk-ant-': {api_key.startswith('sk-ant-')}")
else:
    print("[FAIL] NO API KEY FOUND IN ENVIRONMENT")
    print("  Check if .env file exists and has ANTHROPIC_API_KEY")

print("\n" + "=" * 80)
print("TESTING BACKEND SETTINGS MODULE")
print("=" * 80)

# Test backend settings
try:
    from backend.settings import settings

    if settings.anthropic_api_key:
        print(f"[OK] Settings loaded API key")
        print(f"  First 20 chars: {settings.anthropic_api_key[:20]}...")
        print(f"  Last 10 chars: ...{settings.anthropic_api_key[-10:]}")
        print(f"  Length: {len(settings.anthropic_api_key)} characters")
        print(f"  Model: {settings.anthropic_model}")
        print(f"  Max tokens: {settings.anthropic_max_tokens}")
    else:
        print("[FAIL] Settings did NOT load API key")
        print("  settings.anthropic_api_key is None or empty")
except Exception as e:
    print(f"[FAIL] Error loading settings: {e}")

print("\n" + "=" * 80)
print("TESTING ANTHROPIC API CALL")
print("=" * 80)

# Test actual API call
try:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    print("[OK] Anthropic client initialized")

    # Make test call with correct model name
    print("  Making test API call...")
    # Use Claude Sonnet 4.5 - the latest model!
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'API key works!'"}]
    )

    print(f"[SUCCESS] API CALL SUCCESSFUL!")
    print(f"  Response: {message.content[0].text}")

except Exception as e:
    print(f"[FAIL] API CALL FAILED!")
    print(f"  Error: {e}")
    print(f"\n  This confirms the API key is INVALID or REVOKED")
    print(f"  User needs to regenerate key from: https://console.anthropic.com/settings/keys")
