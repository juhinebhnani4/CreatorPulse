#!/usr/bin/env python3
"""
Quick OpenAI API Key Test with .env loading
Tests if the OpenAI API key from .env file works correctly
"""

import os
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] .env file loaded")
except ImportError:
    print("[WARNING] python-dotenv not installed, trying without it")

# Check if key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print(f"\nAPI Key Status:")
print(f"   - Key exists: {bool(api_key)}")
if api_key:
    print(f"   - Key preview: {api_key[:15]}...{api_key[-10:]}")
    print(f"   - Key length: {len(api_key)} characters")
else:
    print("   [ERROR] No API key found in environment")
    exit(1)

# Test OpenAI connection
print(f"\nTesting OpenAI Connection...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    # Test with a simple model list request
    models = client.models.list()
    model_count = len(models.data)

    print(f"   [SUCCESS] Connected to OpenAI API")
    print(f"   Found {model_count} available models")
    if model_count > 0:
        print(f"   First model: {models.data[0].id}")

except Exception as e:
    print(f"   [FAILED] {str(e)[:200]}")
    exit(1)

print(f"\n[SUCCESS] All tests passed! Your OpenAI API key is working correctly.")
