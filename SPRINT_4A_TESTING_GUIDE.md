# Sprint 4A Testing Guide - How to Add Subscribers & Send Newsletters

## Prerequisites Checklist

Before testing, ensure:

- [x] ✅ Backend running on http://localhost:8000
- [x] ✅ Frontend running on http://localhost:8502
- [ ] ⚠️ **Database migration run** (REQUIRED - see step 1 below)
- [ ] 📧 Email settings configured in `.env`

---

## Step 1: Run Database Migration (REQUIRED FIRST!)

**You must do this before anything else will work!**

### Option A: Using Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard:**
   - Go to https://supabase.com/dashboard
   - Select your project

2. **Go to SQL Editor:**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Copy & Run Migration:**
   - Open: `backend/migrations/004_create_subscribers_table.sql`
   - Copy entire contents
   - Paste into SQL Editor
   - Click "Run" or press Ctrl+Enter

4. **Verify Success:**
   - Should see: "Success. No rows returned"
   - Go to "Table Editor" → Should see new tables:
     - `subscribers`
     - `newsletter_deliveries`

### Option B: Using Supabase CLI (Alternative)

```bash
# From project root
supabase db push backend/migrations/004_create_subscribers_table.sql
```

---

## Step 2: Configure Email Settings

Edit your `.env` file (create from `.env.example` if needed):

### For Gmail (Easiest for testing):

```env
# Email Configuration
USE_SENDGRID=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Your Newsletter Name
```

**Important:** Use Gmail App Password, not your regular password:
1. Go to https://myaccount.google.com/apppasswords
2. Generate app password for "Mail"
3. Use that 16-character password

### For SendGrid (Production):

```env
USE_SENDGRID=true
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=your-verified-email@example.com
FROM_NAME=Your Newsletter Name
```

**After editing `.env`, restart backend:**
```bash
# Stop backend (Ctrl+C) and restart
cd "E:\Career coaching\100x\scraper-scripts"
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Step 3: Get Your Auth Token & Workspace ID

You need these for API calls:

### Method 1: From Browser (Easiest)

1. **Open browser DevTools:**
   - Open http://localhost:8502
   - Login
   - Press F12 (Developer Tools)
   - Go to "Network" tab

2. **Trigger a request:**
   - Click around in the app (any tab)
   - Look for any API request in Network tab
   - Click on it → "Headers" tab
   - Find `Authorization: Bearer eyJhbG...` (your token)

3. **Copy token:**
   - Copy everything after "Bearer " (the long JWT token)
   - Also note your workspace ID from the URL or response

### Method 2: Login via API

```bash
# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'

# Response includes token:
# {"success":true,"data":{"token":"eyJhbG...","user_id":"..."},...}

# Get workspaces
curl -X GET http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Response includes workspace_id:
# {"success":true,"data":{"workspaces":[{"id":"1839de43-ebf1-4cc0-bcb4-3f7a2cb37a7b",...}]},...}
```

**Save these for next steps:**
- `TOKEN`: Your JWT token
- `WORKSPACE_ID`: Your workspace UUID (e.g., `1839de43-ebf1-4cc0-bcb4-3f7a2cb37a7b`)

---

## Step 4: Add Subscribers

Now you can add subscribers using the API!

### Option A: Using curl (Command Line)

**Add Single Subscriber:**
```bash
curl -X POST http://localhost:8000/api/v1/subscribers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "YOUR_WORKSPACE_ID",
    "email": "subscriber@example.com",
    "name": "John Doe",
    "source": "manual"
  }'
```

**Add Multiple Subscribers:**
```bash
curl -X POST http://localhost:8000/api/v1/subscribers/bulk \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "YOUR_WORKSPACE_ID",
    "subscribers": [
      {"email": "subscriber1@example.com", "name": "Alice"},
      {"email": "subscriber2@example.com", "name": "Bob"},
      {"email": "your-email@gmail.com", "name": "You (for testing)"}
    ]
  }'
```

**List Subscribers:**
```bash
curl -X GET "http://localhost:8000/api/v1/subscribers/workspaces/YOUR_WORKSPACE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Option B: Using Swagger UI (Interactive)

1. **Open API Docs:**
   - Go to http://localhost:8000/docs
   - You'll see all API endpoints

2. **Authenticate:**
   - Click "Authorize" button (top right with lock icon)
   - Enter: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize" → "Close"

3. **Add Subscriber:**
   - Find "Subscribers" section
   - Click "POST /api/v1/subscribers"
   - Click "Try it out"
   - Fill in the request body:
     ```json
     {
       "workspace_id": "YOUR_WORKSPACE_ID",
       "email": "test@example.com",
       "name": "Test User",
       "source": "manual"
     }
     ```
   - Click "Execute"
   - See response below (should show success)

4. **List Subscribers:**
   - Find "GET /api/v1/subscribers/workspaces/{workspace_id}"
   - Click "Try it out"
   - Enter your workspace_id
   - Click "Execute"
   - See all subscribers

### Option C: Using Python Script

Create `test_subscribers.py`:

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "YOUR_TOKEN_HERE"
WORKSPACE_ID = "YOUR_WORKSPACE_ID"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Add subscriber
response = requests.post(
    f"{BASE_URL}/subscribers",
    headers=headers,
    json={
        "workspace_id": WORKSPACE_ID,
        "email": "test@example.com",
        "name": "Test User",
        "source": "manual"
    }
)

print("Add subscriber:", response.json())

# List subscribers
response = requests.get(
    f"{BASE_URL}/subscribers/workspaces/{WORKSPACE_ID}",
    headers=headers
)

print("Subscribers:", response.json())
```

Run: `python test_subscribers.py`

---

## Step 5: Generate a Newsletter

Before sending, you need a newsletter!

### Method 1: Via Streamlit UI (Easiest)

1. Go to http://localhost:8502
2. Login → Select workspace
3. Go to "📚 Content Library" tab
4. Click "🔄 Scrape Content" (wait for content to load)
5. Go to "📝 Newsletter Generator" tab
6. Configure settings (title, items, etc.)
7. Click "🎨 Generate Newsletter"
8. **Note the newsletter ID** from the response or history

### Method 2: Via API

```bash
curl -X POST http://localhost:8000/api/v1/newsletters/generate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "YOUR_WORKSPACE_ID",
    "title": "Test Newsletter",
    "max_items": 5,
    "days_back": 7,
    "tone": "professional",
    "language": "en"
  }'
```

Save the `newsletter_id` from the response!

---

## Step 6: Send Newsletter!

Now for the exciting part - actually sending emails!

### Test Send (Recommended First)

**Send to yourself first to test:**

```bash
curl -X POST http://localhost:8000/api/v1/delivery/send-sync \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletter_id": "YOUR_NEWSLETTER_ID",
    "workspace_id": "YOUR_WORKSPACE_ID",
    "test_email": "your-email@gmail.com"
  }'
```

**Check your email!** You should receive the newsletter within seconds.

### Send to All Subscribers

**Once test works, send to all:**

```bash
curl -X POST http://localhost:8000/api/v1/delivery/send \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletter_id": "YOUR_NEWSLETTER_ID",
    "workspace_id": "YOUR_WORKSPACE_ID"
  }'
```

This sends to ALL active subscribers (background process).

**Note:** `/send` runs in background (returns immediately), `/send-sync` waits for completion.

---

## Step 7: Check Delivery Status

### Via API

```bash
# Get delivery ID from send response, then:
curl -X GET "http://localhost:8000/api/v1/delivery/YOUR_DELIVERY_ID/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### List All Deliveries

```bash
curl -X GET "http://localhost:8000/api/v1/delivery/workspaces/YOUR_WORKSPACE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Shows:
- Total subscribers targeted
- Sent count
- Failed count
- Status (pending, sending, completed, failed)
- Errors (if any)

---

## Troubleshooting

### "Not authenticated" Error

**Problem:** API returns 401 Unauthorized

**Fix:**
- Make sure you're using `Bearer YOUR_TOKEN` format
- Token might have expired - login again to get fresh token
- Check Authorization header is correct

### "Database tables don't exist" Error

**Problem:** API returns error about missing tables

**Fix:**
- You haven't run the database migration!
- Go back to Step 1 and run the SQL migration

### Email Not Sending

**Problem:** No errors but emails aren't arriving

**Check:**
1. **Email settings in `.env`:**
   - Correct SMTP server?
   - Correct username/password?
   - Using app password for Gmail?

2. **Test SMTP connection:**
   ```python
   from ai_newsletter.delivery.email_sender import EmailSender
   from ai_newsletter.config.settings import get_settings

   settings = get_settings()
   sender = EmailSender(config=settings.email)

   # This will print if connection works
   ```

3. **Check spam folder!**

4. **Check backend logs:**
   - Look for error messages in terminal where backend is running

### "Subscriber already exists" Error

**Problem:** Can't add subscriber with same email twice

**Fix:**
- This is expected! One email per workspace
- Use bulk import to skip duplicates
- Or delete existing subscriber first

---

## Quick Test Script

Save as `test_sprint4a.py`:

```python
#!/usr/bin/env python3
"""Quick test script for Sprint 4A - Email Delivery"""

import requests
import json

# ===== CONFIGURATION - EDIT THESE =====
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "YOUR_TOKEN_HERE"  # Get from login
WORKSPACE_ID = "YOUR_WORKSPACE_ID"  # Get from workspaces API
TEST_EMAIL = "your-email@gmail.com"  # Your email for testing
# =======================================

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_add_subscriber():
    """Test 1: Add a subscriber"""
    print("Test 1: Adding subscriber...")
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
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.ok

def test_list_subscribers():
    """Test 2: List subscribers"""
    print("Test 2: Listing subscribers...")
    response = requests.get(
        f"{BASE_URL}/subscribers/workspaces/{WORKSPACE_ID}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        count = data['data']['count']
        print(f"Found {count} subscribers")
        for sub in data['data']['subscribers']:
            print(f"  - {sub['email']} ({sub['status']})")
    print()
    return response.ok

def test_generate_newsletter():
    """Test 3: Generate a newsletter"""
    print("Test 3: Generating newsletter...")
    response = requests.post(
        f"{BASE_URL}/newsletters/generate",
        headers=headers,
        json={
            "workspace_id": WORKSPACE_ID,
            "title": "Sprint 4A Test Newsletter",
            "max_items": 3,
            "days_back": 7
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        newsletter_id = data['data']['id']
        print(f"Newsletter generated: {newsletter_id}")
        print()
        return newsletter_id
    else:
        print(f"Error: {data.get('error')}\n")
        return None

def test_send_newsletter(newsletter_id):
    """Test 4: Send newsletter to test email"""
    print(f"Test 4: Sending newsletter to {TEST_EMAIL}...")
    response = requests.post(
        f"{BASE_URL}/delivery/send-sync",
        headers=headers,
        json={
            "newsletter_id": newsletter_id,
            "workspace_id": WORKSPACE_ID,
            "test_email": TEST_EMAIL
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        result = data['data']
        print(f"✅ Sent: {result['sent_count']}")
        print(f"❌ Failed: {result['failed_count']}")
        print(f"Status: {result['status']}")
        if result['sent_count'] > 0:
            print(f"\n🎉 SUCCESS! Check {TEST_EMAIL} for the newsletter!")
    else:
        print(f"Error: {data.get('error')}")
    print()
    return response.ok

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 4A - Email Delivery Testing")
    print("=" * 60 + "\n")

    # Run tests
    if not test_add_subscriber():
        print("⚠️  Test 1 failed - check token and workspace ID")
        exit(1)

    if not test_list_subscribers():
        print("⚠️  Test 2 failed")
        exit(1)

    newsletter_id = test_generate_newsletter()
    if not newsletter_id:
        print("⚠️  Test 3 failed - no content? Run scraper first!")
        exit(1)

    if not test_send_newsletter(newsletter_id):
        print("⚠️  Test 4 failed - check email settings in .env")
        exit(1)

    print("=" * 60)
    print("✅ All tests passed! Sprint 4A is working!")
    print("=" * 60)
```

**Run:** `python test_sprint4a.py`

---

## Summary: Where Things Happen

| Task | Where | Method |
|------|-------|--------|
| Run migration | Supabase Dashboard | SQL Editor |
| Configure email | `.env` file | Edit manually |
| Add subscribers | API or Swagger | POST /api/v1/subscribers |
| List subscribers | API or Swagger | GET /api/v1/subscribers/workspaces/{id} |
| Generate newsletter | Streamlit or API | UI or POST /newsletters/generate |
| Send newsletter | API or Swagger | POST /delivery/send |
| Check status | API or Swagger | GET /delivery/{id}/status |

**Remember:** Always run database migration first (Step 1)!

---

## Next Steps After Testing

Once everything works:

1. ✅ Add real subscribers (import from CSV, add via API, etc.)
2. ✅ Set up production email service (SendGrid recommended)
3. ✅ Test unsubscribe flow
4. ✅ Move to Sprint 4B (Scheduler) for automation!

Need help? Check:
- **API Docs:** http://localhost:8000/docs
- **Completion Doc:** SPRINT_4A_EMAIL_DELIVERY_COMPLETE.md
- **Backend logs:** Check terminal where uvicorn is running
