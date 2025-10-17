# Quick API Reference - CreatorPulse

**Base URL:** `http://localhost:8000`
**API Version:** v1 (`/api/v1`)
**Docs:** http://localhost:8000/docs

---

## Authentication

All endpoints except `/auth/signup` and `/auth/login` require JWT token in header:
```
Authorization: Bearer <token>
```

### Sign Up
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "username": "myusername"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response:** Returns JWT token (expires in 30 minutes)

---

## Workspaces

### Create Workspace
```bash
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Newsletter",
    "description": "AI-powered newsletter"
  }'
```

### List Workspaces
```bash
curl -X GET http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer <token>"
```

### Get Workspace Config
```bash
curl -X GET http://localhost:8000/api/v1/workspaces/{workspace_id}/config \
  -H "Authorization: Bearer <token>"
```

---

## Content

### Trigger Scraping
```bash
curl -X POST http://localhost:8000/api/v1/content/scrape \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "sources": ["reddit", "rss"]
  }'
```

### Get Content Stats
```bash
curl -X GET http://localhost:8000/api/v1/content/workspaces/{workspace_id}/stats \
  -H "Authorization: Bearer <token>"
```

### List Content
```bash
curl -X GET "http://localhost:8000/api/v1/content/workspaces/{workspace_id}?days=7&limit=50" \
  -H "Authorization: Bearer <token>"
```

---

## Newsletters

### Generate Newsletter
```bash
curl -X POST http://localhost:8000/api/v1/newsletters/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "title": "Weekly AI Updates"
  }'
```

### List Newsletters
```bash
curl -X GET http://localhost:8000/api/v1/newsletters/workspaces/{workspace_id} \
  -H "Authorization: Bearer <token>"
```

### Get Newsletter
```bash
curl -X GET http://localhost:8000/api/v1/newsletters/{newsletter_id} \
  -H "Authorization: Bearer <token>"
```

---

## Subscribers

### Add Subscriber
```bash
curl -X POST http://localhost:8000/api/v1/subscribers \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "email": "subscriber@example.com",
    "name": "John Doe"
  }'
```

### List Subscribers
```bash
curl -X GET http://localhost:8000/api/v1/subscribers/workspaces/{workspace_id} \
  -H "Authorization: Bearer <token>"
```

### Bulk Import
```bash
curl -X POST http://localhost:8000/api/v1/subscribers/bulk \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "subscribers": [
      {"email": "user1@example.com", "name": "User 1"},
      {"email": "user2@example.com", "name": "User 2"}
    ]
  }'
```

---

## Delivery

### Send Newsletter (Async)
```bash
curl -X POST http://localhost:8000/api/v1/delivery/send \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletter_id": "<newsletter_id>",
    "test_mode": false
  }'
```

### Get Delivery History
```bash
curl -X GET http://localhost:8000/api/v1/delivery/workspaces/{workspace_id} \
  -H "Authorization: Bearer <token>"
```

---

## Scheduler

### Create Scheduled Job
```bash
curl -X POST http://localhost:8000/api/v1/scheduler \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "schedule_type": "weekly",
    "schedule_config": {
      "day_of_week": "monday",
      "hour": 9,
      "minute": 0
    }
  }'
```

### List Jobs
```bash
curl -X GET http://localhost:8000/api/v1/scheduler/workspaces/{workspace_id} \
  -H "Authorization: Bearer <token>"
```

### Pause Job
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/{job_id}/pause \
  -H "Authorization: Bearer <token>"
```

---

## Style Training

### Train Style Profile
```bash
curl -X POST http://localhost:8000/api/v1/style/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "samples": [
      "Sample newsletter 1 content...",
      "Sample newsletter 2 content...",
      "Sample newsletter 3 content..."
    ]
  }'
```

### Get Style Profile
```bash
curl -X GET http://localhost:8000/api/v1/style/{workspace_id} \
  -H "Authorization: Bearer <token>"
```

---

## Trends Detection

### Detect Trends
```bash
curl -X POST http://localhost:8000/api/v1/trends/detect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "days_back": 7,
    "max_trends": 10
  }'
```

### Get Active Trends
```bash
curl -X GET "http://localhost:8000/api/v1/trends/{workspace_id}?limit=5" \
  -H "Authorization: Bearer <token>"
```

---

## Feedback & Learning

### Create Content Feedback
```bash
curl -X POST http://localhost:8000/api/v1/feedback/items \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_item_id": "<content_id>",
    "rating": "high_value",
    "included_in_final": true
  }'
```

### Create Newsletter Feedback
```bash
curl -X POST http://localhost:8000/api/v1/feedback/newsletters \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletter_id": "<newsletter_id>",
    "overall_rating": 4,
    "time_to_finalize_minutes": 15,
    "would_recommend": true
  }'
```

---

## Analytics

### Record Event
```bash
curl -X POST http://localhost:8000/api/v1/analytics/events \
  -H "Content-Type: application/json" \
  -d '{
    "newsletter_id": "<newsletter_id>",
    "subscriber_id": "<subscriber_id>",
    "event_type": "opened"
  }'
```

### Get Workspace Analytics
```bash
curl -X GET http://localhost:8000/api/v1/analytics/workspaces/{workspace_id}/summary \
  -H "Authorization: Bearer <token>"
```

### Get Newsletter Analytics
```bash
curl -X GET http://localhost:8000/api/v1/analytics/newsletters/{newsletter_id} \
  -H "Authorization: Bearer <token>"
```

---

## Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "environment": "development",
    "timestamp": "2025-10-16T09:50:00.000000"
  }
}
```

---

## Response Format

All endpoints return consistent JSON format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

---

## Common HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Rate Limiting

- **Limit:** 60 requests per minute per IP
- **Header:** `X-RateLimit-Remaining` shows remaining requests
- **Reset:** Rate limit window resets every minute

---

## Testing with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# 1. Sign up
response = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": "test@example.com",
    "password": "password123",
    "username": "testuser"
})
data = response.json()
token = data['data']['token']

# 2. Create workspace
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/workspaces",
    headers=headers,
    json={
        "name": "My Newsletter",
        "description": "Test workspace"
    }
)
workspace_id = response.json()['data']['id']

# 3. Add subscriber
response = requests.post(f"{BASE_URL}/subscribers",
    headers=headers,
    json={
        "workspace_id": workspace_id,
        "email": "subscriber@example.com",
        "name": "Test Subscriber"
    }
)

print("Setup complete!")
```

---

## Environment Variables

Required in `.env` file:

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Security
SECRET_KEY=your-secret-key

# Optional API Keys
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
X_BEARER_TOKEN=...
YOUTUBE_API_KEY=...
```

---

## Need Help?

- **API Documentation:** http://localhost:8000/docs
- **Database Schema:** `scripts/supabase_schema.sql`
- **Full Documentation:** `DATABASE_CONFIGURATION_COMPLETE.md`
- **Setup Guide:** `SUPABASE_SETUP_GUIDE.md`
