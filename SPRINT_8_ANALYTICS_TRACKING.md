# Sprint 8: Analytics & Engagement Tracking

**Status:** In Progress
**Started:** 2025-01-20
**Goal:** Implement comprehensive email engagement tracking and analytics dashboard

---

## Overview

Sprint 8 implements the final major feature from the roadmap: **Analytics & Engagement Tracking**. This enables CreatorPulse to:
- Track email open rates via tracking pixels
- Track link click-through rates via UTM parameters
- Provide analytics dashboards with key metrics
- Export analytics data for reporting
- Prove ROI with 2× engagement uplift KPI

---

## Success Criteria

- [ ] Track email open events (tracking pixel)
- [ ] Track link click events (UTM + redirect tracking)
- [ ] Store analytics events in Supabase
- [ ] Provide analytics API endpoints
- [ ] Calculate key metrics (open rate, CTR, CTOR)
- [ ] Support analytics filtering by date range
- [ ] Export analytics data to CSV/JSON
- [ ] Integrate tracking with existing email delivery
- [ ] Privacy-compliant tracking (GDPR/CAN-SPAM)

---

## Architecture

### Database Schema (Migration 009)

**Table: email_analytics_events**
```sql
CREATE TABLE email_analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    newsletter_id UUID NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'unsubscribed')),
    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Recipient
    recipient_email VARCHAR(255) NOT NULL,
    subscriber_id UUID REFERENCES subscribers(id) ON DELETE SET NULL,

    -- Click tracking
    clicked_url TEXT,
    content_item_id UUID REFERENCES content_items(id) ON DELETE SET NULL,

    -- Context
    user_agent TEXT,
    ip_address VARCHAR(45),
    location_city VARCHAR(100),
    location_country VARCHAR(100),
    device_type VARCHAR(50),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_analytics_workspace_newsletter ON email_analytics_events(workspace_id, newsletter_id);
CREATE INDEX idx_analytics_event_type ON email_analytics_events(event_type);
CREATE INDEX idx_analytics_event_time ON email_analytics_events(event_time DESC);
CREATE INDEX idx_analytics_recipient ON email_analytics_events(recipient_email);
CREATE INDEX idx_analytics_newsletter_recipient ON email_analytics_events(newsletter_id, recipient_email);
```

**Table: newsletter_analytics_summary**
```sql
CREATE TABLE newsletter_analytics_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    newsletter_id UUID NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,

    -- Calculated metrics (updated periodically)
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    bounced_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    unique_opens INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    unique_clicks INTEGER DEFAULT 0,
    unsubscribed_count INTEGER DEFAULT 0,

    -- Rates
    open_rate DECIMAL(5,4) DEFAULT 0.0,
    click_rate DECIMAL(5,4) DEFAULT 0.0,
    click_to_open_rate DECIMAL(5,4) DEFAULT 0.0,
    bounce_rate DECIMAL(5,4) DEFAULT 0.0,

    -- Timing
    avg_time_to_open_seconds INTEGER,
    avg_time_to_click_seconds INTEGER,

    -- Metadata
    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(newsletter_id)
);
```

### API Endpoints (backend/api/v1/analytics.py)

```python
# POST /api/v1/analytics/events
# - Record analytics events (sent, opened, clicked, etc.)
# - Called by tracking server

# GET /api/v1/analytics/newsletters/{newsletter_id}
# - Get analytics for specific newsletter
# - Returns: opens, clicks, rates, top links

# GET /api/v1/analytics/workspace/{workspace_id}/summary
# - Get aggregate analytics for workspace
# - Query params: start_date, end_date
# - Returns: total sends, avg open rate, avg CTR, trends

# GET /api/v1/analytics/workspace/{workspace_id}/export
# - Export analytics data as CSV or JSON
# - Query params: format (csv/json), start_date, end_date

# GET /api/v1/analytics/content-item/{content_item_id}/performance
# - Get performance metrics for specific content item
# - Returns: times included, clicks, engagement rate
```

### Tracking Endpoints (backend/api/tracking.py)

```python
# GET /track/pixel/{encoded_params}.png
# - Tracking pixel for email opens
# - Returns: 1x1 transparent PNG
# - Records 'opened' event in database

# GET /track/click/{encoded_params}
# - Click tracking redirect
# - Records 'clicked' event in database
# - Redirects to original URL
```

---

## Implementation Tasks

### Task 1: Database Migration (2 hours)

**File:** `backend/migrations/009_create_analytics_tables.sql`

- Create `email_analytics_events` table
- Create `newsletter_analytics_summary` table
- Add indexes for performance
- Add RLS policies
- Create trigger to update summary on event insert
- Create function to recalculate analytics summary

### Task 2: Analytics Service (4 hours)

**File:** `backend/services/analytics_service.py`

```python
class AnalyticsService:
    async def record_event(
        workspace_id: UUID,
        newsletter_id: UUID,
        event_type: str,
        recipient_email: str,
        **kwargs
    ) -> UUID:
        """Record an analytics event."""

    async def get_newsletter_analytics(
        newsletter_id: UUID
    ) -> NewsletterAnalyticsSummary:
        """Get analytics for a newsletter."""

    async def get_workspace_analytics(
        workspace_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> WorkspaceAnalyticsSummary:
        """Get aggregate analytics for workspace."""

    async def recalculate_summary(
        newsletter_id: UUID
    ) -> None:
        """Recalculate analytics summary for newsletter."""
```

### Task 3: Tracking Service (4 hours)

**File:** `backend/services/tracking_service.py`

```python
class TrackingService:
    def generate_tracking_pixel_url(
        newsletter_id: UUID,
        recipient_email: str,
        workspace_id: UUID
    ) -> str:
        """Generate tracking pixel URL."""

    def generate_tracked_link(
        original_url: str,
        newsletter_id: UUID,
        recipient_email: str,
        content_item_id: Optional[UUID] = None
    ) -> str:
        """Add tracking to link (UTM + redirect)."""

    def add_tracking_to_html(
        html_content: str,
        newsletter_id: UUID,
        recipient_email: str,
        content_items: List[ContentItem]
    ) -> str:
        """Add tracking pixel and link tracking to HTML."""
```

### Task 4: Analytics API Endpoints (4 hours)

**File:** `backend/api/v1/analytics.py`

Implement all analytics API endpoints:
- Record events
- Get newsletter analytics
- Get workspace summary
- Export data

### Task 5: Tracking API Endpoints (3 hours)

**File:** `backend/api/tracking.py`

Implement tracking endpoints:
- Pixel tracking (`/track/pixel/<params>.png`)
- Click tracking (`/track/click/<params>`)

### Task 6: Email Delivery Integration (3 hours)

**Modify:** `backend/services/email_service.py`

```python
async def send_newsletter_email(
    newsletter_id: UUID,
    recipient: Subscriber,
    html_content: str
) -> bool:
    # Add tracking pixel
    tracking_service = TrackingService()
    html_with_tracking = tracking_service.add_tracking_to_html(
        html_content,
        newsletter_id,
        recipient.email,
        content_items
    )

    # Send email
    success = await self._send_email(recipient.email, subject, html_with_tracking)

    # Record 'sent' event
    if success:
        await analytics_service.record_event(
            workspace_id=workspace_id,
            newsletter_id=newsletter_id,
            event_type='sent',
            recipient_email=recipient.email
        )

    return success
```

### Task 7: Analytics Models & Schemas (2 hours)

**Files:**
- `backend/models/analytics_models.py` - Pydantic schemas
- `backend/schemas/analytics.py` - API request/response schemas

### Task 8: Analytics Export (2 hours)

Implement CSV/JSON export:
- Filter by date range
- Include all metrics
- Support both event-level and summary-level exports

### Task 9: Testing (4 hours)

**Files:**
- `tests/unit/test_analytics_service.py`
- `tests/unit/test_tracking_service.py`
- `tests/integration/test_analytics_api.py`
- `tests/integration/test_tracking_endpoints.py`

Test coverage:
- [ ] Tracking pixel generates correctly
- [ ] Tracking pixel records open events
- [ ] Links have tracking parameters
- [ ] Click tracking records events
- [ ] Analytics calculations are accurate
- [ ] Date filtering works
- [ ] Export functionality works
- [ ] RLS policies enforce workspace isolation

### Task 10: Documentation (2 hours)

**File:** `SPRINT_8_COMPLETE.md`

Document:
- API endpoints
- Tracking implementation
- Privacy compliance notes
- Testing guide
- Deployment notes

---

## Technical Details

### Tracking Pixel Implementation

```python
def generate_tracking_pixel_url(newsletter_id, recipient_email, workspace_id):
    params = {
        'n': str(newsletter_id),
        'r': recipient_email,
        'w': str(workspace_id)
    }

    # Encode params
    encoded = base64.urlsafe_b64encode(
        json.dumps(params).encode()
    ).decode()

    # Generate URL
    return f"{settings.backend_url}/track/pixel/{encoded}.png"
```

### Link Tracking Implementation

```python
def generate_tracked_link(original_url, newsletter_id, recipient_email, content_item_id):
    parsed = urlparse(original_url)
    params = parse_qs(parsed.query)

    # Add UTM parameters
    params.update({
        'utm_source': 'newsletter',
        'utm_medium': 'email',
        'utm_campaign': str(newsletter_id),
        'utm_content': str(content_item_id) if content_item_id else 'link'
    })

    # Add tracking redirect
    track_data = {
        'n': str(newsletter_id),
        'r': recipient_email,
        'c': str(content_item_id) if content_item_id else None,
        'u': original_url
    }

    encoded = base64.urlsafe_b64encode(
        json.dumps(track_data).encode()
    ).decode()

    # Return redirect URL
    return f"{settings.backend_url}/track/click/{encoded}"
```

### Privacy & Compliance

**GDPR Compliance:**
- Track only necessary data (no PII beyond email)
- Provide unsubscribe mechanism in all emails
- Allow users to request data deletion
- Store IP addresses in anonymized form (last octet masked)

**CAN-SPAM Compliance:**
- Include physical address in emails
- Honor unsubscribe requests within 10 days
- Clear sender identification
- Accurate subject lines

---

## Example Responses

### GET /api/v1/analytics/newsletters/{newsletter_id}

```json
{
  "success": true,
  "data": {
    "newsletter_id": "uuid",
    "workspace_id": "uuid",
    "sent_at": "2025-01-20T10:00:00Z",
    "metrics": {
      "sent_count": 1000,
      "delivered_count": 980,
      "bounced_count": 20,
      "opened_count": 450,
      "unique_opens": 420,
      "clicked_count": 120,
      "unique_clicks": 110,
      "unsubscribed_count": 5
    },
    "rates": {
      "open_rate": 0.4286,
      "click_rate": 0.1122,
      "click_to_open_rate": 0.2619,
      "bounce_rate": 0.0204
    },
    "timing": {
      "avg_time_to_open_seconds": 3600,
      "avg_time_to_click_seconds": 7200
    },
    "top_links": [
      {
        "url": "https://example.com/article-1",
        "clicks": 45,
        "unique_clicks": 42
      }
    ]
  }
}
```

### GET /api/v1/analytics/workspace/{workspace_id}/summary

```json
{
  "success": true,
  "data": {
    "workspace_id": "uuid",
    "date_range": {
      "start": "2025-01-01T00:00:00Z",
      "end": "2025-01-31T23:59:59Z"
    },
    "aggregate_metrics": {
      "total_newsletters": 4,
      "total_sent": 4000,
      "total_delivered": 3920,
      "total_opened": 1800,
      "total_clicked": 480,
      "avg_open_rate": 0.4592,
      "avg_click_rate": 0.1224,
      "engagement_score": 0.85
    },
    "trends": {
      "open_rate_trend": "+12.5%",
      "click_rate_trend": "+8.3%"
    },
    "top_performing_content": [
      {
        "content_item_id": "uuid",
        "title": "AI Agents Tutorial",
        "clicks": 120,
        "engagement_rate": 0.35
      }
    ]
  }
}
```

---

## Testing Guide

### Manual Testing

1. **Setup Test Environment:**
```bash
# Start backend server
cd backend
.venv/Scripts/python.exe -m uvicorn backend.main:app --reload

# Run migrations
psql -h <host> -U postgres -d creatorpulse < migrations/009_create_analytics_tables.sql
```

2. **Test Tracking Pixel:**
```bash
# Send test email with tracking
POST http://localhost:8000/api/v1/delivery/send-newsletter

# Verify tracking pixel URL in email HTML
# Open email in browser and check network tab for pixel load

# Query analytics
GET http://localhost:8000/api/v1/analytics/newsletters/{newsletter_id}
```

3. **Test Click Tracking:**
```bash
# Click link in test email
# Verify redirect works
# Check that click event was recorded in database

# Query analytics to verify click count
```

### Automated Testing

```bash
# Run all tests
pytest tests/

# Run analytics tests only
pytest tests/unit/test_analytics_service.py
pytest tests/integration/test_analytics_api.py

# Generate coverage report
pytest --cov=backend --cov-report=html
```

---

## Deployment Notes

### Environment Variables

Add to `.env`:
```env
# Analytics tracking
TRACKING_DOMAIN=https://yourdomain.com
TRACKING_PIXEL_ENABLED=true

# IP geolocation (optional)
IPAPI_KEY=your_ipapi_key_here
```

### Database Migration

```sql
-- Run migration
psql -h <host> -U postgres -d creatorpulse < migrations/009_create_analytics_tables.sql

-- Verify tables created
\dt email_analytics_events
\dt newsletter_analytics_summary
```

### Enable Analytics Routes

**Modify:** `backend/main.py`
```python
# Uncomment:
from backend.api.v1 import analytics
from backend.api import tracking

app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}/analytics", tags=["Analytics"])
app.include_router(tracking.router, prefix="/track", tags=["Tracking"])
```

---

## Timeline

**Estimated Effort:** 30 hours (~4 days)

| Task | Hours | Status |
|------|-------|--------|
| Database migration | 2 | Pending |
| Analytics service | 4 | Pending |
| Tracking service | 4 | Pending |
| Analytics API | 4 | Pending |
| Tracking API | 3 | Pending |
| Email integration | 3 | Pending |
| Models & schemas | 2 | Pending |
| Export functionality | 2 | Pending |
| Testing | 4 | Pending |
| Documentation | 2 | Pending |
| **TOTAL** | **30** | **In Progress** |

---

## Success Metrics

After Sprint 8 completion:

- [ ] Email open tracking works for 100% of sent emails
- [ ] Click tracking works for all links
- [ ] Analytics dashboard shows accurate metrics
- [ ] Export functionality works for CSV and JSON
- [ ] Response time < 500ms for analytics queries
- [ ] Privacy-compliant tracking (GDPR/CAN-SPAM)
- [ ] All tests pass with >80% coverage

---

## Next Steps (Post-Sprint 8)

After Sprint 8, the core CreatorPulse features are complete:

1. **Frontend Development** (Sprint 9?)
   - Next.js dashboard
   - Analytics visualizations
   - Real-time metrics

2. **Advanced Features** (Sprint 10+)
   - A/B testing for subject lines
   - Send-time optimization
   - Predictive analytics
   - Recommendation engine

3. **Scale & Optimization**
   - CDN for tracking pixel
   - Analytics data archiving
   - Performance optimization

---

## References

- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Overall product roadmap
- [SPRINT_7_FEEDBACK_LOOP_COMPLETE.md](SPRINT_7_FEEDBACK_LOOP_COMPLETE.md) - Previous sprint
- Backend architecture: `backend/README.md`
- Supabase schema: `backend/migrations/`

---

**Status:** In Progress
**Started:** 2025-01-20
**Target Completion:** 2025-01-24
