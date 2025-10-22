#!/usr/bin/env python3
"""Test AI newsletter generation directly."""

import sys
sys.path.insert(0, ".")

from src.ai_newsletter.generators.newsletter_generator import NewsletterGenerator
from src.ai_newsletter.config.settings import get_settings
from src.ai_newsletter.database.supabase_client import SupabaseManager

print("="*60)
print("Testing AI Newsletter Generation")
print("="*60 + "\n")

# Load settings
settings = get_settings()
print(f"[1] Settings loaded:")
print(f"    - Model: {settings.newsletter.model}")
print(f"    - Use OpenRouter: {settings.newsletter.use_openrouter}")
print(f"    - OpenAI Key: {settings.newsletter.openai_api_key[:20]}..." if settings.newsletter.openai_api_key else "    - OpenAI Key: None")
print(f"    - OpenRouter Key: {settings.newsletter.openrouter_api_key[:20]}..." if settings.newsletter.openrouter_api_key else "    - OpenRouter Key: None")

# Load some content
print(f"\n[2] Loading content...")
db = SupabaseManager()
content_items = db.load_content_items(
    workspace_id="a378d938-c330-4060-82a4-17579dc8bb3f",
    days=7,
    limit=5
)
print(f"    - Loaded {len(content_items)} items")

# Initialize generator
print(f"\n[3] Initializing NewsletterGenerator...")
try:
    generator = NewsletterGenerator(config=settings.newsletter)
    print(f"    - Generator initialized successfully")
    print(f"    - Model: {generator.model}")
except Exception as e:
    print(f"    - ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Generate newsletter
print(f"\n[4] Generating newsletter...")
try:
    html = generator.generate_newsletter(
        content_items=content_items,
        title="Test Newsletter",
        max_items=3
    )
    print(f"    - Generation completed")
    print(f"    - HTML length: {len(html)} characters")
    print(f"    - Preview (first 500 chars):")
    print(f"      {html[:500]}")

    if len(html) < 100:
        print(f"\n    WARNING: HTML is very short, likely using fallback")
    else:
        print(f"\n    SUCCESS: HTML generated properly")

except Exception as e:
    print(f"    - ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("Test completed")
print("="*60)
