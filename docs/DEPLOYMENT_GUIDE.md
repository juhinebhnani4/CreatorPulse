# 🚀 Deployment Guide - Tasks 2-5 Integration

**Last Updated:** January 20, 2025
**Version:** 1.0.0
**Status:** ✅ All Tests Passing (6/6)

This guide explains how to use the newly implemented features from Tasks 2-5:
- **Task 2:** Trends Integration
- **Task 3:** Style Profiles Integration
- **Task 4:** Feedback Learning Integration
- **Task 5:** HMAC Authentication for Analytics

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Feature Overview](#feature-overview)
4. [Using Trend Integration](#using-trend-integration)
5. [Using Style Profiles](#using-style-profiles)
6. [Using Feedback Learning](#using-feedback-learning)
7. [Using HMAC Authentication](#using-hmac-authentication)
8. [Testing the Implementation](#testing-the-implementation)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.13+** (tested with 3.13.8)
- **Virtual Environment** (`.venv` activated)
- **Supabase Account** (for database)
- **OpenAI or OpenRouter API Key** (for newsletter generation)

### Required Packages
Run in your activated virtual environment:
```bash
pip install -r requirements.txt
```

Key packages:
- `fastapi` - API framework
- `pandas` - Data manipulation
- `nltk` - Natural language processing (Style Profiles)
- `numpy` - Numerical operations
- `scikit-learn` - Machine learning (Trends)
- `python-dotenv` - Environment variables

---

## Environment Setup

### 1. Configure `.env` File

Ensure your `.env` file has the following keys:

```bash
# Required for HMAC Authentication (Task 5)
ANALYTICS_SECRET_KEY=your-64-character-hex-string-here

# Required for Newsletter Generation (Tasks 2-4)
OPENAI_API_KEY=sk-...  # Or use OpenRouter below
OPENROUTER_API_KEY=sk-or-v1-...
USE_OPENROUTER=false  # Set to true to use OpenRouter

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

### 2. Generate ANALYTICS_SECRET_KEY

If you haven't already:

```python
import secrets
print(secrets.token_hex(32))  # Generates 64-character hex string
```

Add the output to your `.env` file:
```bash
ANALYTICS_SECRET_KEY=a7f3d8e9c2b1a4f6e8d7c3b5a9f1e4d2c6b8a3f7e9d1c4b6a8f3e7d9c2b5a1f4
```

### 3. Verify Environment

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run tests
python tests/test_integrations.py
```

**Expected output:**
```
Total: 6/6 tests passed
🎉 ALL TESTS PASSED! Implementation is working correctly.
```

---

## Feature Overview

### Task 2: Trends Integration

**What it does:**
- Automatically detects trending topics from workspace content
- Boosts content scores by 30% when related to trends
- Adds visual "🔥 Trending Topics" section to newsletters
- Passes trend context to AI for better content selection

**Files modified:**
- `backend/services/newsletter_service.py`
- `src/ai_newsletter/generators/newsletter_generator.py`

### Task 3: Style Profiles Integration

**What it does:**
- Fetches user's trained writing style profile
- Generates AI prompts matching user's tone, formality, and preferences
- Applies style guidance to newsletter generation
- Tracks style usage in metadata

**Files modified:**
- `backend/services/newsletter_service.py`
- `src/ai_newsletter/generators/newsletter_generator.py`

### Task 4: Feedback Learning Integration

**What it does:**
- Adjusts content scores based on user feedback patterns
- Applies source quality multipliers
- Boosts preferred sources by 20%
- Penalizes content below user's score threshold by 30%

**Files modified:**
- `backend/services/newsletter_service.py`

### Task 5: HMAC Authentication

**What it does:**
- Secures `/api/v1/analytics/events` endpoint
- Requires `X-Tracking-Token` header with valid HMAC signature
- Tokens expire after 30 days
- Prevents spam and abuse

**Files created:**
- `backend/utils/hmac_auth.py`

**Files modified:**
- `backend/api/v1/analytics.py`

---

## Using Trend Integration

### How It Works

When generating a newsletter, the system:

1. **Detects Trends** - Fetches up to 5 active trends for the workspace
2. **Boosts Content** - Content related to trends gets +30% score boost
3. **Adds Trending Section** - Top 3 trends displayed in newsletter
4. **Guides AI** - Trend context passed to AI model for better writing

###Example Usage

```python
from backend.services.newsletter_service import NewsletterService

service = NewsletterService()

result = await service.generate_newsletter(
    user_id="user-123",
    workspace_id="workspace-456",
    title="Weekly AI Newsletter",
    max_items=15,
    days_back=7
)

# Check if trends were applied
print(f"Trends applied: {result['trends_applied']}")
print(f"Trend-boosted items: {result['trend_boosted_items']}")
```

### What You'll See in Newsletters

```html
<div class="trending-section">
  <h2>🔥 Trending Topics</h2>

  <div class="trend">
    <strong>GPT-5 Rumors</strong> (Strength: 87%)
    <p>This topic is trending with 12 mentions across HackerNews, Reddit.
       It's showing rapid growth with a 145% increase in mentions.</p>
  </div>

  <!-- More trends... -->
</div>
```

### Metadata Tracked

```json
{
  "trends_used": ["GPT-5 Rumors", "AI Safety", "Claude 3"],
  "trend_boosted_items": 5
}
```

---

## Using Style Profiles

### How It Works

When generating a newsletter:

1. **Fetch Profile** - Loads user's trained style profile from database
2. **Generate Prompt** - Converts profile to AI instructions
3. **Apply Style** - AI generates content matching user's voice
4. **Track Usage** - Records style application in metadata

### Example Usage

```python
from backend.services.newsletter_service import NewsletterService

service = NewsletterService()

# Style profile is automatically applied if one exists
result = await service.generate_newsletter(
    user_id="user-123",
    workspace_id="workspace-456",
    title="Weekly Newsletter"
)

# Check if style was applied
print(f"Style applied: {result['style_profile_applied']}")
```

### Style Profile Elements

The system extracts and applies:

- **Tone** - Professional, casual, witty, etc.
- **Formality Level** - 0-100% formal
- **Sentence Length** - Average words per sentence
- **Question Frequency** - How often to ask questions
- **Favorite Phrases** - User's characteristic expressions
- **Avoided Words** - Words the user never uses
- **Emoji Usage** - Whether and how often to use emojis
- **Intro/Transition Styles** - User's typical sentence structures

### Example Style Prompt

```
Write in this specific style:
- Tone: witty (65% formal)
- Average sentence length: 15 words
- Question frequency: Include questions 20% of the time
- Use these characteristic phrases: "breaking down", "let's dive in", "here's the thing"
- Avoid these words: utilize, leverage, synergy, paradigm
- Intro style: starts with questions or bold statements
- Include emojis occasionally (about 15% of content)

Example intro: "Ever wondered why AI keeps surprising us?"
Example transition: "But here's where it gets interesting..."
```

### Metadata Tracked

```json
{
  "style_profile_applied": true,
  "style_tone": "witty"
}
```

---

## Using Feedback Learning

### How It Works

Content scoring is adjusted based on user feedback:

1. **Load Feedback Data** - Gets source quality scores and preferences
2. **Apply Quality Multipliers** - High-rated sources get boosted scores
3. **Apply Preference Filters** - Preferred sources get +20% boost
4. **Apply Threshold Penalties** - Low-scoring content gets -30% penalty
5. **Track Adjustments** - Records all changes in metadata

### Example Usage

```python
from backend.services.newsletter_service import NewsletterService

service = NewsletterService()

# Feedback adjustments are automatically applied
result = await service.generate_newsletter(
    user_id="user-123",
    workspace_id="workspace-456",
    title="Weekly Newsletter"
)

# Check feedback impact
print(f"Feedback-adjusted items: {result['feedback_adjusted_items']}")
```

### Scoring Pipeline

**Original Score** → **Source Quality Multiplier** → **Preference Boost** → **Threshold Penalty** → **Trend Boost** → **Final Score**

Example:
```python
# Original content item
item = {
    "title": "GPT-5 Release Date Leaked",
    "source": "HackerNews",
    "score": 100
}

# After feedback adjustments:
# 1. Source quality: 100 * 1.2 = 120 (HackerNews rated high)
# 2. Preferred source: 120 * 1.2 = 144 (+20% boost)
# 3. Threshold check: 144 > 50 (passes minimum, no penalty)
# 4. Trend boost: 144 * 1.3 = 187 (+30% for trending topic)

# Final score: 187
```

### Adjustments Tracked

Each item records its adjustments:
```python
{
  "original_score": 100,
  "adjusted_score": 187,
  "adjustments": [
    "source_quality:1.20",
    "preferred_source:+20%",
    "trending_topic:+30%"
  ]
}
```

### Metadata Tracked

```json
{
  "feedback_adjusted_items": 8
}
```

---

## Using HMAC Authentication

### How It Works

1. **Generate Token** - Create HMAC signature for newsletter + workspace
2. **Include in Requests** - Add `X-Tracking-Token` header
3. **Verify on Server** - Endpoint validates signature and timestamp
4. **Reject Invalid** - Returns 401 if token is missing/invalid/expired

### Generating Tokens

```python
from backend.utils.hmac_auth import generate_tracking_token
import os

# Get secret key
secret_key = os.getenv("ANALYTICS_SECRET_KEY")

# Generate token
token = generate_tracking_token(
    newsletter_id="550e8400-e29b-41d4-a716-446655440000",
    workspace_id="660e8400-e29b-41d4-a716-446655440000",
    secret_key=secret_key
)

print(f"Token: {token}")
# Output: 1760950000.a1b2c3d4e5f6...
```

### Making Authenticated Requests

```python
import requests

# Record analytics event
response = requests.post(
    "https://your-api.com/api/v1/analytics/events",
    headers={
        "X-Tracking-Token": token,
        "Content-Type": "application/json"
    },
    json={
        "workspace_id": "660e8400-e29b-41d4-a716-446655440000",
        "newsletter_id": "550e8400-e29b-41d4-a716-446655440000",
        "event_type": "opened",
        "recipient_email": "user@example.com"
    }
)

if response.status_code == 201:
    print("✅ Event recorded successfully")
else:
    print(f"❌ Failed: {response.json()}")
```

### Embedding in Email Tracking Pixels

```html
<!-- In newsletter HTML -->
<img src="https://your-api.com/api/v1/analytics/track-open?
    newsletter_id=550e8400-e29b-41d4-a716-446655440000&
    workspace_id=660e8400-e29b-41d4-a716-446655440000&
    token=1760950000.a1b2c3d4e5f6..."
    width="1" height="1" />
```

### Token Format

```
{timestamp}.{signature}
```

- **Timestamp**: Unix epoch seconds (e.g., `1760950000`)
- **Signature**: HMAC-SHA256 hex digest (e.g., `a1b2c3d4e5f6...`)

### Token Expiration

Tokens are valid for **30 days** by default. After that:

```json
{
  "detail": "Invalid token: Token expired (age: 2592001s)"
}
```

### Error Responses

**Missing Token:**
```json
HTTP 401 Unauthorized
{
  "detail": "Missing tracking token. Include X-Tracking-Token header."
}
```

**Invalid Signature:**
```json
HTTP 401 Unauthorized
{
  "detail": "Token verification failed: Invalid token signature"
}
```

**Expired Token:**
```json
HTTP 401 Unauthorized
{
  "detail": "Token verification failed: Token expired (age: 2700000s)"
}
```

---

## Testing the Implementation

### Run All Tests

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run integration tests
python tests/test_integrations.py
```

**Expected Output:**
```
================================================================================
INTEGRATION TESTS FOR TASKS 2-5
================================================================================

...

================================================================================
TEST SUMMARY
================================================================================
✅ PASSED: HMAC Authentication
✅ PASSED: Newsletter Service Integration
✅ PASSED: Newsletter Generator Parameters
✅ PASSED: Feedback Service Method
✅ PASSED: Style Service Method
✅ PASSED: Trend Service Method

Total: 6/6 tests passed

🎉 ALL TESTS PASSED! Implementation is working correctly.
```

### Manual Testing

#### Test Newsletter Generation with All Features

```python
from backend.services.newsletter_service import NewsletterService
import asyncio

async def test_newsletter():
    service = NewsletterService()

    result = await service.generate_newsletter(
        user_id="test-user",
        workspace_id="test-workspace",
        title="Test Newsletter with All Features",
        max_items=10,
        days_back=7,
        use_openrouter=True  # Or False for OpenAI
    )

    print("✅ Newsletter generated successfully!")
    print(f"   Content items: {result['content_items_count']}")
    print(f"   Trends applied: {result['trends_applied']}")
    print(f"   Trend-boosted items: {result['trend_boosted_items']}")
    print(f"   Style profile applied: {result['style_profile_applied']}")
    print(f"   Feedback-adjusted items: {result['feedback_adjusted_items']}")

asyncio.run(test_newsletter())
```

#### Test HMAC Authentication

```python
from backend.utils.hmac_auth import generate_tracking_token, verify_tracking_token
import os

# Load environment
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("ANALYTICS_SECRET_KEY")

# Generate and verify token
newsletter_id = "550e8400-e29b-41d4-a716-446655440000"
workspace_id = "660e8400-e29b-41d4-a716-446655440000"

token = generate_tracking_token(newsletter_id, workspace_id, secret_key)
print(f"Generated token: {token}")

try:
    is_valid = verify_tracking_token(token, newsletter_id, workspace_id, secret_key)
    print(f"✅ Token is valid: {is_valid}")
except ValueError as e:
    print(f"❌ Token invalid: {e}")
```

---

## Troubleshooting

### Common Issues

#### 1. "ANALYTICS_SECRET_KEY not found"

**Problem:** Environment variable not set

**Solution:**
```bash
# Generate key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env
echo "ANALYTICS_SECRET_KEY=<your-key-here>" >> .env

# Restart application
```

#### 2. "ModuleNotFoundError: No module named 'pandas'"

**Problem:** Dependencies not installed

**Solution:**
```bash
# Activate venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. "No trends found for workspace"

**Problem:** No trends detected or no recent content

**Solution:**
```python
# Manually detect trends
from backend.services.trend_service import TrendDetectionService

service = TrendDetectionService()
trends, summary = await service.detect_trends(
    workspace_id=workspace_id,
    days_back=7,
    max_trends=5
)

print(f"Trends detected: {len(trends)}")
print(f"Content analyzed: {summary['content_items_analyzed']}")
```

#### 4. "No style profile found"

**Problem:** User hasn't trained a style profile

**Solution:**
```python
# Train style profile first
from backend.services.style_service import StyleAnalysisService

service = StyleAnalysisService()
profile = await service.train_style_profile(
    workspace_id=workspace_id,
    content_texts=["Sample text 1", "Sample text 2", ...]
)

print(f"✅ Style profile created: {profile.tone}")
```

#### 5. "Token expired"

**Problem:** HMAC token older than 30 days

**Solution:**
```python
# Generate fresh token
token = generate_tracking_token(newsletter_id, workspace_id, secret_key)

# Use within 30 days
```

#### 6. "python-dotenv not loading .env"

**Problem:** .env file not in correct location or not loaded

**Solution:**
```python
from dotenv import load_dotenv
from pathlib import Path

# Load from specific path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Verify
import os
print(os.getenv("ANALYTICS_SECRET_KEY"))  # Should print your key
```

### Getting Help

If you encounter issues not covered here:

1. **Check logs** - Look for error messages in console output
2. **Run tests** - `python tests/test_integrations.py`
3. **Verify environment** - Ensure all required keys are in `.env`
4. **Check dependencies** - Reinstall with `pip install -r requirements.txt`

---

## Summary

You now have:

✅ **Trends Integration** - Automatic trending topic detection and content boosting
✅ **Style Profiles** - AI-generated content matching user's writing style
✅ **Feedback Learning** - Content scoring adjusted by user preferences
✅ **HMAC Authentication** - Secure analytics tracking endpoint

All features work together seamlessly in the newsletter generation pipeline!

---

**Next Steps:**
- Proceed with MEDIUM priority tasks (6-10) for code quality improvements
- Deploy to production environment
- Monitor analytics and trend detection performance
- Collect user feedback on style profile accuracy
