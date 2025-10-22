# Common Errors & Solutions

**Purpose**: Comprehensive catalog of known errors, their causes, and step-by-step solutions.

**When to use**: When debugging errors, investigating failures, or understanding error messages.

---

## Table of Contents

1. [Backend API Errors](#backend-api-errors)
2. [Frontend Errors](#frontend-errors)
3. [Database Errors](#database-errors)
4. [Integration Errors](#integration-errors)
5. [Deployment Errors](#deployment-errors)

---

## Backend API Errors

### 1. 500 - Newsletter Generation Failed

**Error Message**:
```json
{
  "success": false,
  "error": "Failed to generate newsletter",
  "message": "Internal server error"
}
```

**Symptoms**:
- `POST /api/v1/newsletters` returns 500
- Newsletter generation hangs then times out
- Backend logs show AI API errors

**Root Causes**:

#### Cause 1: No Content Items Available
**Diagnostic**:
```bash
# Check if workspace has content
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/content/workspaces/{workspace_id}?limit=1"

# Response: {"success": true, "data": []}  ← Empty!
```

**Solution**:
```bash
# Scrape content first
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "{workspace_id}"}' \
  "http://localhost:8000/api/v1/content/scrape"

# Wait for scraping to complete, then retry newsletter generation
```

**Prevention**: Add content availability check in frontend before allowing newsletter generation.

#### Cause 2: Missing AI API Keys
**Diagnostic**:
```bash
# Check backend logs
tail -f backend/logs/app.log

# Look for:
# ERROR: OpenAI API key not found
# ERROR: OpenRouter API key not found
```

**Solution**:
```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-proj-..." >> .env

# OR
echo "OPENROUTER_API_KEY=sk-or-v1-..." >> .env

# Restart backend
```

**Prevention**: Add environment variable validation at startup in `backend/main.py`.

#### Cause 3: AI API Rate Limit Exceeded
**Diagnostic**:
```bash
# Backend logs show:
# ERROR: OpenAI API error: Rate limit exceeded
# ERROR: OpenRouter API error: 429 Too Many Requests
```

**Solution**:
- Wait 60 seconds and retry
- Upgrade API plan for higher rate limits
- Switch to alternative provider (OpenRouter if using OpenAI, or vice versa)

**Prevention**: Implement retry logic with exponential backoff in `backend/services/newsletter_service.py`.

#### Cause 4: Malformed Workspace Config
**Diagnostic**:
```bash
# Check workspace config
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/workspaces/{workspace_id}/config"

# Response shows invalid JSON structure or missing required fields
```

**Solution**:
```bash
# Update config with valid structure
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "sources": [],
      "generation": {
        "model": "openai",
        "temperature": 0.7,
        "tone": "professional",
        "language": "en",
        "max_items": 10
      },
      "delivery": {
        "method": "smtp",
        "from_name": "Newsletter"
      }
    }
  }' \
  "http://localhost:8000/api/v1/workspaces/{workspace_id}/config"
```

**Prevention**: Add Zod/Pydantic validation for workspace config updates.

---

### 2. 401 - Unauthorized

**Error Message**:
```json
{
  "detail": "Not authenticated"
}
```

**Symptoms**:
- All API calls return 401
- User is redirected to login page
- Frontend shows "Session expired" message

**Root Causes**:

#### Cause 1: Token Expired
**Diagnostic**:
```typescript
// Frontend console
const token = localStorage.getItem('auth-token')
console.log('Token:', token?.substring(0, 20) + '...')

// If token is present but still getting 401, it's expired
```

**Solution**:
```typescript
// Option 1: Refresh token
const response = await axios.post('/api/v1/auth/refresh', { token })
localStorage.setItem('auth-token', response.data.data.token)

// Option 2: Re-login
await axios.post('/api/v1/auth/login', { email, password })
```

**Token Lifetime**: 30 minutes (configurable in `backend/settings.py`)

**Prevention**: Implement auto-refresh 5 minutes before expiry.

#### Cause 2: Missing Authorization Header
**Diagnostic**:
```typescript
// Check axios instance configuration
console.log(axiosInstance.defaults.headers.common['Authorization'])

// Should be: "Bearer eyJhbGciOiJIUzI1NiIs..."
// If undefined, header is missing
```

**Solution**:
```typescript
// In lib/utils/axios-instance.ts
const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

// Add interceptor to attach token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

#### Cause 3: Invalid Token Format
**Diagnostic**:
```bash
# Backend logs show:
# ERROR: Invalid token format
# ERROR: Token signature verification failed
```

**Causes**:
- Token corrupted in localStorage
- Token signed with wrong `SECRET_KEY`
- Token manually edited

**Solution**:
```typescript
// Clear corrupted token and re-login
localStorage.removeItem('auth-token')
// Redirect to login page
```

**Prevention**: Never expose `SECRET_KEY`, use environment variables only.

---

### 3. 403 - Workspace Access Denied

**Error Message**:
```json
{
  "success": false,
  "error": "Access denied",
  "message": "You do not have permission to access this workspace"
}
```

**Symptoms**:
- User can't access workspace data despite valid token
- Other workspaces work fine
- Error occurs for specific workspace only

**Root Cause**: User not in `user_workspaces` table for the requested workspace

**Diagnostic**:
```sql
-- Check workspace membership (via Supabase dashboard)
SELECT * FROM user_workspaces
WHERE user_id = '{user_id}' AND workspace_id = '{workspace_id}';

-- If empty, user is not a member
```

**Solution**:

Option 1: Add user to workspace (if they should have access)
```bash
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "{user_id}", "role": "editor"}' \
  "http://localhost:8000/api/v1/workspaces/{workspace_id}/members"
```

Option 2: Use a workspace where user is a member
```bash
# List user's workspaces
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/workspaces"
```

**Prevention**: Add workspace membership check in frontend before allowing access.

---

### 4. 422 - Validation Error

**Error Message**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Symptoms**:
- API rejects request with validation errors
- Required fields missing or malformed
- Frontend form validation passed but backend rejected

**Root Cause**: Request body doesn't match Pydantic model requirements

**Common Validation Errors**:

#### Missing Required Field
```json
// Request (missing 'email')
{
  "password": "123456"
}

// Error
{
  "detail": [{"loc": ["body", "email"], "msg": "field required"}]
}
```

**Solution**: Ensure all required fields are included.

#### Invalid Field Type
```json
// Request (temperature should be float, not string)
{
  "temperature": "0.7"
}

// Error
{
  "detail": [{"loc": ["body", "temperature"], "msg": "value is not a valid float"}]
}
```

**Solution**: Convert to correct type: `temperature: parseFloat("0.7")`.

#### Invalid Enum Value
```json
// Request (invalid tone value)
{
  "tone": "funny"  // Should be: professional | casual | technical | friendly
}

// Error
{
  "detail": [{"loc": ["body", "tone"], "msg": "value is not a valid enumeration member"}]
}
```

**Solution**: Use valid enum values only. Check backend Pydantic models for allowed values.

---

### 5. 429 - Rate Limit Exceeded

**Error Message**:
```json
{
  "error": "Rate limit exceeded",
  "message": "60 per 1 minute"
}
```

**Symptoms**:
- API requests blocked after multiple calls
- Error occurs after batch operations
- Returns after waiting 60 seconds

**Root Cause**: Rate limiting configured in `backend/middleware/rate_limiter.py` (default: 60 req/min)

**Solution**:

Immediate:
```typescript
// Implement retry with exponential backoff
async function retryRequest(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (error.response?.status === 429 && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000  // 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay))
      } else {
        throw error
      }
    }
  }
}
```

Long-term: Adjust rate limits per endpoint
```python
# backend/api/v1/content.py
from slowapi import Limiter

@router.post("/scrape")
@limiter.limit("10/minute")  # Lower limit for expensive operations
async def scrape_content(...):
    ...

@router.get("/workspaces/{workspace_id}")
@limiter.limit("100/minute")  # Higher limit for read operations
async def list_content(...):
    ...
```

---

## Frontend Errors

### 6. TypeError: Cannot read property 'content_html' of undefined

**Error Message** (Browser console):
```
TypeError: Cannot read property 'content_html' of undefined
  at NewsletterDisplay.tsx:45
```

**Symptoms**:
- Frontend crashes when displaying newsletter
- Error in browser console
- White screen or error boundary

**Root Causes**:

#### Cause 1: API Response Structure Mismatch
**Diagnostic**:
```typescript
// Check API response in browser devtools network tab
{
  "success": true,
  "data": {
    "id": "...",
    "content_html": "..."  // ✅ Field exists
  }
}

// But code expects:
newsletter.content_html  // ❌ newsletter is undefined
```

**Solution**:
```typescript
// ❌ WRONG - No null check
const html = newsletter.content_html

// ✅ CORRECT - Optional chaining
const html = newsletter?.content_html ?? '<p>No content</p>'
```

#### Cause 2: Using Old Field Names
**Diagnostic**:
```typescript
// Code uses old field name
const html = newsletter.html_content  // ❌ Field doesn't exist (renamed)

// API returns
{ "content_html": "..." }  // ✅ New name
```

**Solution**:
```typescript
// Update to new field name
const html = newsletter.content_html  // ✅ Correct
```

See: [FRONTEND_BACKEND_MAPPING.md](./FRONTEND_BACKEND_MAPPING.md) for complete field name reference.

---

### 7. Hydration Error (Next.js)

**Error Message**:
```
Unhandled Runtime Error
Error: Text content does not match server-rendered HTML.

Warning: Text content did not match. Server: "..." Client: "..."
```

**Symptoms**:
- Page flashes with different content on load
- Error in browser console
- Content appears then disappears then reappears

**Root Cause**: Client-side JavaScript renders different content than server-side HTML

**Common Scenarios**:

#### Scenario 1: Using localStorage in Server Component
```typescript
// ❌ WRONG - localStorage not available on server
const Component = () => {
  const token = localStorage.getItem('auth-token')  // Crashes on server
  return <div>{token}</div>
}
```

**Solution**:
```typescript
// ✅ CORRECT - Client-only rendering
'use client'
import { useEffect, useState } from 'react'

const Component = () => {
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    setToken(localStorage.getItem('auth-token'))
  }, [])

  if (!token) return null  // or loading state
  return <div>{token}</div>
}
```

#### Scenario 2: Date/Time Formatting
```typescript
// ❌ WRONG - Server and client timezone differ
const Component = ({ date }: { date: string }) => {
  return <div>{new Date(date).toLocaleString()}</div>  // Different on server/client
}
```

**Solution**:
```typescript
// ✅ CORRECT - Use suppressHydrationWarning or format consistently
const Component = ({ date }: { date: string }) => {
  return <div suppressHydrationWarning>{new Date(date).toLocaleString()}</div>
}

// OR format to ISO/UTC consistently
return <div>{new Date(date).toISOString()}</div>
```

---

### 8. CORS Error

**Error Message** (Browser console):
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/auth/login'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Symptoms**:
- API requests fail in browser
- Requests work in Postman/curl
- Error only occurs from frontend

**Root Cause**: Backend CORS middleware not allowing frontend origin

**Diagnostic**:
```bash
# Check current CORS configuration
cat backend/middleware/cors.py

# Check if frontend origin is in allowed list
```

**Solution**:

Update `backend/middleware/cors.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",           # ✅ Local dev (Next.js)
    "http://localhost:8000",           # ✅ Backend serving frontend
    "https://your-app.railway.app",    # ✅ Production
    os.getenv("FRONTEND_URL", ""),     # ✅ Environment-specific
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart backend after changes.

**Prevention**: Set `FRONTEND_URL` environment variable in deployment.

---

## Database Errors

### 9. RLS Policy Violation

**Error Message**:
```json
{
  "code": "PGRST204",
  "details": null,
  "hint": null,
  "message": "The result contains 0 rows"
}
```

**Symptoms**:
- Query returns empty despite data existing in database
- Same query works in Supabase SQL editor with service role
- Error only occurs in API, not in database UI

**Root Cause**: Row-Level Security (RLS) policy blocking access

**Diagnostic**:
```sql
-- Check if data exists (via Supabase dashboard with service role)
SELECT * FROM content_items WHERE workspace_id = '{workspace_id}';

-- If data exists, RLS is blocking access
```

**Causes**:

1. Using wrong Supabase client (user client for admin operations)
2. User not authenticated properly
3. RLS policy doesn't allow access for user's role

**Solution**:

#### Fix 1: Use Service Client for Access Verification
```python
# ❌ WRONG - User client for workspace access check
user_db = SupabaseManager(use_service_role=False, user_token=jwt_token)
workspace = user_db.client.table('workspaces').select('*').eq('id', workspace_id).single().execute()
# Returns empty due to RLS

# ✅ CORRECT - Service client for initial check
service_db = SupabaseManager(use_service_role=True)
workspace = service_db.client.table('workspaces').select('*').eq('id', workspace_id).single().execute()

# Then verify user membership
membership = service_db.client.table('user_workspaces') \
    .select('*') \
    .eq('user_id', user_id) \
    .eq('workspace_id', workspace_id) \
    .execute()

if len(membership.data) == 0:
    raise HTTPException(403, "Access denied")

# Now use user client for data access (RLS enforced correctly)
user_db = SupabaseManager(use_service_role=False, user_token=jwt_token)
content = user_db.client.table('content_items').select('*').eq('workspace_id', workspace_id).execute()
```

#### Fix 2: Update RLS Policy (if policy is incorrect)
```sql
-- Check current policy
SELECT * FROM pg_policies WHERE tablename = 'content_items';

-- Update policy to allow workspace members
CREATE POLICY "Users can view content in their workspaces"
ON content_items FOR SELECT
USING (
  workspace_id IN (
    SELECT workspace_id FROM user_workspaces
    WHERE user_id = auth.uid()
  )
);
```

**Prevention**: Always use service client for cross-workspace checks, user client for user-scoped data.

---

### 10. Unique Constraint Violation

**Error Message**:
```json
{
  "code": "23505",
  "details": "Key (workspace_id, source_url)=(xxx, yyy) already exists.",
  "message": "duplicate key value violates unique constraint"
}
```

**Symptoms**:
- Insert fails on `content_items` table
- Error occurs when scraping same content twice
- Duplicate content in database

**Root Cause**: Trying to insert content item with same `workspace_id + source_url` (unique constraint from migration 010)

**Diagnostic**:
```sql
-- Check if content already exists
SELECT * FROM content_items
WHERE workspace_id = '{workspace_id}' AND source_url = '{url}';
```

**Solution**:

#### Option 1: Use Upsert (Update if Exists)
```python
# In ContentService.scrape_content()
from supabase.client import PostgrestAPIError

try:
    # Try insert
    result = db.client.table('content_items').insert({
        'workspace_id': workspace_id,
        'source_url': url,
        'title': title,
        # ... other fields
    }).execute()
except PostgrestAPIError as e:
    if e.code == '23505':  # Unique constraint violation
        # Update existing item instead
        result = db.client.table('content_items') \
            .update({'title': title, 'scraped_at': datetime.utcnow()}) \
            .eq('workspace_id', workspace_id) \
            .eq('source_url', url) \
            .execute()
    else:
        raise
```

#### Option 2: Check Before Insert
```python
# Check if exists first
existing = db.client.table('content_items') \
    .select('id') \
    .eq('workspace_id', workspace_id) \
    .eq('source_url', url) \
    .execute()

if len(existing.data) > 0:
    # Skip or update
    logger.info(f"Content already exists: {url}")
    continue
else:
    # Insert new
    result = db.client.table('content_items').insert({...}).execute()
```

**Prevention**: Implement idempotent scraping logic (migration 010 already adds the constraint).

---

### 11. Foreign Key Constraint Violation

**Error Message**:
```json
{
  "code": "23503",
  "details": "Key (workspace_id)=(xxx) is not present in table \"workspaces\".",
  "message": "insert or update on table violates foreign key constraint"
}
```

**Symptoms**:
- Insert fails with foreign key error
- Referenced workspace/user doesn't exist
- Cascade delete failed

**Root Cause**: Trying to insert row referencing non-existent parent

**Solution**:

```python
# Always verify parent exists before inserting child
workspace = db.client.table('workspaces').select('id').eq('id', workspace_id).single().execute()

if not workspace.data:
    raise HTTPException(404, "Workspace not found")

# Now safe to insert child
content = db.client.table('content_items').insert({
    'workspace_id': workspace_id,  # ✅ Verified exists
    # ... other fields
}).execute()
```

---

## Integration Errors

### 12. OpenAI API Error

**Error Message**:
```json
{
  "error": {
    "message": "Rate limit exceeded",
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded"
  }
}
```

**Symptoms**:
- Newsletter generation fails
- Backend logs show OpenAI API error
- Error occurs intermittently

**Root Causes**:

#### Cause 1: Rate Limit Exceeded
**Solution**: Wait 60 seconds and retry, or upgrade OpenAI plan.

#### Cause 2: Invalid API Key
**Diagnostic**:
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If 401, key is invalid
```

**Solution**: Generate new API key from OpenAI dashboard.

#### Cause 3: Insufficient Credits
**Solution**: Add payment method to OpenAI account.

---

### 13. SMTP Email Delivery Failed

**Error Message**:
```python
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted.')
```

**Symptoms**:
- Email delivery fails
- Test email not received
- Backend logs show SMTP error

**Root Causes**:

#### Cause 1: Incorrect App Password (Gmail)
**Solution**:
1. Go to Google Account → Security → 2-Step Verification → App Passwords
2. Generate new app password
3. Update `.env`:
   ```bash
   SMTP_PASSWORD=your-16-char-app-password  # NOT your Google password
   ```

#### Cause 2: "Less Secure Apps" Disabled
**Solution**: Enable 2FA and use app passwords (see above).

#### Cause 3: Wrong SMTP Server/Port
**Solution**:
```bash
# Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Outlook
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

---

## Deployment Errors

### 14. Railway Deployment Failed

**Error Message** (Railway logs):
```
Error: Missing environment variable SUPABASE_URL
```

**Solution**:
1. Go to Railway project → Variables tab
2. Add all required environment variables (see `.env.example`)
3. Redeploy

---

### 15. Database Migration Not Applied

**Symptoms**:
- Table/column doesn't exist errors
- New features don't work after deployment
- SQL errors in logs

**Solution**:
```bash
# Apply migrations manually via Supabase dashboard
# Go to SQL Editor → New Query → Paste migration SQL → Run

# Or via psql
psql "postgres://..." < backend/migrations/010_add_content_unique_constraint.sql
```

---

## Quick Diagnostic Flowchart

```
Error → Check error code/message
  ├─ 401 → Check token (expired? missing? invalid?)
  ├─ 403 → Check workspace access (user_workspaces table)
  ├─ 422 → Check request body (validation error details)
  ├─ 429 → Wait 60s (rate limit)
  ├─ 500 → Check backend logs
  │   ├─ "No content items" → Scrape content first
  │   ├─ "API key not found" → Add to .env
  │   ├─ "Rate limit" → Wait or upgrade plan
  │   └─ Other → Debug service code
  └─ TypeError (frontend) → Check null/undefined, field names

CORS Error → Update backend/middleware/cors.py origins
Hydration Error → Add 'use client' + useEffect
RLS Error → Use service client for access checks
```

---

**END OF COMMON_ERRORS.md**