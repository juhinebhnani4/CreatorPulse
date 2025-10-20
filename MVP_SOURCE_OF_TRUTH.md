# CreatorPulse MVP - Source of Truth Document

**Last Updated:** 2025-10-17
**Status:** Implementation In Progress
**Version:** 1.1

---

## Product Vision

**What:** AI-powered newsletter curation tool with intelligent backend, simple frontend
**Who:** Individual creators + Agencies managing multiple clients
**Why:** Cut newsletter drafting from 2-3 hours to <20 minutes

---

## Core Philosophy: "Intelligent Backend, Simple Frontend"

**User Sees:** 3 simple pages (Dashboard, Content, Settings)
**Backend Does:** Trend detection, quality scoring, style learning, analytics (all invisible)
**Result:** Personalized, high-quality newsletters without complexity

---

## User Types & Journeys

### **Individual User**

**Setup (First Time):**
```
1. Register/Login
2. Dashboard → "Configure sources to get started"
3. Settings → Add sources:
   - Reddit: 2-3 subreddits
   - YouTube: 2-3 channels
   - RSS: 1-2 feeds
   - Twitter/X: 3-5 handles
4. Set delivery: email + time (8am)
5. Save → Backend starts scraping
```

**Daily Flow:**
```
8:00 AM - Email: "Your newsletter draft is ready"
         ↓
Login → Dashboard
         ↓
See: Newsletter preview + "20 new items scraped"
         ↓
Click "Review Content" → Content Library
         ↓
Browse content with thumbnails
         ↓
Give inline feedback: 👍 Keep | 👎 Skip
         ↓ (Backend learns invisibly)
Dashboard → "Generate Newsletter"
         ↓
Review draft → Send to subscribers
         ↓
Done in <20 minutes
```

### **Agency User**

**Setup:**
```
1. Register/Login (Agency account)
2. Create Workspace #1 (Client A)
   → Configure sources for Client A
3. Create Workspace #2 (Client B)
   → Configure different sources for Client B
4. Repeat for 5-10 clients
```

**Daily Flow:**
```
8:00 AM - Email: "5 newsletters ready"
         ↓
Login → Workspace Switcher
         ↓
Select "Client A" → Review → Feedback → Generate
         ↓
Switch "Client B" → Review → Feedback → Generate
         ↓
Manage 5+ clients in 1-2 hours
```

---

## Application Structure

### **3-Page MVP:**

#### **1. Dashboard**
**Purpose:** Newsletter preview + quick actions

**Shows:**
- Latest newsletter draft preview (first 3 items)
- Quick stats: "20 items scraped today" (invisible: quality scored, trend detected)
- CTA buttons:
  - "Review Content" → Content Library
  - "Generate Newsletter"
- Schedule status: "Next send: Tomorrow 8:00 AM"

**Agency View:**
- Workspace switcher dropdown at top
- Same dashboard scoped to selected workspace

**Design Elements:**
- ✅ Gradient header: `bg-gradient-to-r from-primary to-primary/60`
- ✅ Stats cards with hover: `hover:-translate-y-1`
- ✅ Gradient backgrounds: `bg-gradient-warm/10`
- ✅ Empty state: Encouraging copy + "Configure Sources" CTA

---

#### **2. Content Library**
**Purpose:** Browse scraped content + give inline feedback

**Shows:**
- Content cards with:
  - Thumbnail (or fallback icon with source color)
  - Title, source badge (🔴 Reddit, 🟠 RSS, 🔵 Twitter, 🟢 YouTube, 🟣 Blog)
  - Snippet/preview text
  - Inline feedback: 👍 Keep | 👎 Skip
- Filter tabs: All, Reddit, RSS, Twitter, YouTube, Blog
- Search bar
- Scrape button: "Scrape Now" with loading state

**Backend Intelligence (Invisible):**
- Quality score influences card sorting
- Trend detection marks "trending" items
- Feedback trains style learning
- Analytics tracks clicks

**Agency View:**
- Same, content scoped to current workspace

**Design Elements:**
- ✅ Gradient header text
- ✅ Thumbnails with fallback icons
- ✅ Source badges color-coded
- ✅ Staggered card animations: `animate-slide-up` with delay
- ✅ Shadow on hover: `shadow-md hover:shadow-lg`
- ✅ Success celebration: `animate-celebration` on scrape

**Already Implemented:** ✅

---

#### **3. Settings**
**Purpose:** Configure sources + delivery preferences

**3 Sections:**

**A. Sources** (Required - Product won't work without)
```
Reddit Sources
  [+] Add Subreddit
  - r/technology [Remove]
  - r/programming [Remove]

Twitter/X Sources
  [+] Add Handle
  - @elonmusk [Remove]
  - @sama [Remove]

YouTube Channels
  [+] Add Channel
  - Fireship [Remove]
  - Theo - t3.gg [Remove]

RSS Feeds
  [+] Add Feed
  - https://news.ycombinator.com/rss [Remove]

Blog URLs
  [+] Add Blog
  - https://paul.copplest.one/blog [Remove]
```

**B. Delivery Settings**
```
Email Recipients: [user@example.com]
Send Time: [08:00] AM
Frequency: [Daily ▼]
Newsletter Name: [Tech Digest]
```

**C. Account**
```
Change Password
Logout
```

**Agency View:**
- Same settings scoped to current workspace
- Each workspace has isolated source configuration

**Design Elements:**
- ✅ Tab navigation (not accordions)
- ✅ Visual icons per section
- ✅ Inline status: "3 subreddits connected"
- ✅ Preview cards for each source
- ✅ Warm gradient on save button

---

### **Sidebar Navigation:**

**Individual User:**
```
┌─────────────────────┐
│ [CP] CreatorPulse   │
├─────────────────────┤
│ 📊 Dashboard        │
│ 📚 Content Library  │
│ ⚙️  Settings        │
├─────────────────────┤
│ 👤 User Menu        │
└─────────────────────┘
```

**Agency User:**
```
┌─────────────────────┐
│ [CP] CreatorPulse   │
├─────────────────────┤
│ 📊 Dashboard        │
│ 📚 Content Library  │
│ ⚙️  Settings        │
├─────────────────────┤
│ 🔄 Workspace: [▼]   │ ← Dropdown to switch
│   • Client A        │
│   • Client B        │
│   • Client C        │
├─────────────────────┤
│ 👤 User Menu        │
└─────────────────────┘
```

---

### **Hidden Pages (Backend Routes Active, No UI Navigation):**

**These pages exist but are NOT in sidebar:**
- ❌ `/app/trends` - Trend detection (invisible intelligence)
- ❌ `/app/analytics` - Analytics dashboard (tracking happens silently)
- ❌ `/app/style` - Style training (learns from feedback invisibly)
- ❌ `/app/feedback` - Feedback management (use inline 👍/👎 instead)

**Backend API routes stay active:**
- ✅ `/api/v1/trends` - Used by scraper to adjust limits
- ✅ `/api/v1/analytics` - Tracks opens/clicks
- ✅ `/api/v1/style` - Updates GPT-4 prompts
- ✅ `/api/v1/feedback` - Processes inline feedback

---

## Backend Architecture

### **Wrapper: FastAPI (`backend/main.py`)**

**11 API Routers:**
```
/api/v1/auth          → JWT authentication
/api/v1/workspaces    → Multi-workspace (agency support)
/api/v1/content       → Scraping + retrieval
/api/v1/newsletters   → Newsletter generation
/api/v1/subscribers   → Subscriber management
/api/v1/delivery      → Email delivery
/api/v1/scheduler     → Automated scheduling
/api/v1/style         → Style learning (invisible)
/api/v1/trends        → Trend detection (invisible)
/api/v1/feedback      → Feedback processing (invisible)
/api/v1/analytics     → Analytics tracking (invisible)
```

---

### **Pipeline Orchestrator (`src/ai_newsletter/orchestrator/pipeline.py`)**

**Coordinates:** Scrape → Filter → Generate → Send

```python
NewsletterPipeline:
  1. Initialize 5 Scrapers
     - RedditScraper (PRAW)
     - RSSFeedScraper (feedparser)
     - YouTubeScraper (YouTube Data API v3)
     - TwitterScraper (Twitter API)
     - BlogScraper (BeautifulSoup + trafilatura)

  2. Scrape Content (parallel from all sources)
     → Returns ContentItem[] with thumbnails

  3. Filter & Sort
     - Last 7 days only
     - Sort by engagement: score + comments + views
     - Remove duplicates (title similarity)

  4. Generate Newsletter
     - GPT-4 via NewsletterGenerator
     - In-context learning from past newsletters
     - Style matching from feedback

  5. Send Email
     - SMTP or SendGrid
     - Tracking pixels for analytics
```

---

### **Invisible Backend Intelligence:**

| Operation | Trigger | User Visibility | Purpose |
|-----------|---------|----------------|---------|
| **Content Scraping** | Scheduled (daily) or manual | ✅ User sees items | Aggregate sources |
| **Trend Detection** | After scraping | ❌ Invisible | Smart limits, spike detection |
| **Quality Scoring** | After scraping | ❌ Invisible | Rank/filter content |
| **Inline Feedback** | User clicks 👍/👎 | ✅ Button visible | Learn preferences |
| **Style Learning** | After feedback | ❌ Invisible | Improve voice matching |
| **Newsletter Generation** | Scheduled or manual | ✅ User sees draft | Create email |
| **Email Delivery** | Scheduled 8am | ✅ User configures | Send to subscribers |
| **Analytics Tracking** | Every email | ❌ Invisible | Track opens/clicks |

---

## Design System: "MyMiraya-Inspired"

### **Color Palette:**
```css
Primary: #E17A5F (warm coral/peach) - Main CTAs, accents
Secondary: #5B8A8A (cool teal) - Balance & complement
Accent: Warm orange - Highlights
Success: #45A845 (green)
Warning: #F59E0B (amber)
Destructive: #DC2626 (red)

Gradients:
  --gradient-warm: coral → peach
  --gradient-cool: teal → darker teal
  --gradient-hero: coral → teal
```

### **Design Principles:**

**1. Visual Interest:**
- ✅ Warm gradient headers
- ✅ Micro-animations (slide-up, celebration, pulse)
- ✅ Hover effects (translate, shadow, color)

**2. Empty States:**
- ✅ Encouraging copy
- ✅ Actionable CTAs
- ✅ Visual guidance

**3. Typography Hierarchy:**
```
H1: text-4xl font-bold (gradient)
H2: text-2xl font-semibold
H3: text-lg font-semibold
Body: text-base (regular)
Muted: text-sm text-muted-foreground
Micro: text-xs uppercase tracking-wide
```

**4. Spacing:**
- Card padding: `p-6`, `p-12`
- Gaps: `gap-2`, `gap-4`
- Margins: `mb-2`, `mb-4`, `mb-8`

**5. Color Strategy:**
- Primary actions: Gradient warm
- Secondary actions: Cool teal
- Success/Warning/Error: Semantic colors
- Source badges: Color-coded (🔴🟠🔵🟢🟣)

**6. Micro-interactions:**
- Button loading states with spinner
- Card hover shadows
- Staggered animations
- Smooth transitions (200-300ms)

---

## Data Flow

### **User Action → Backend Intelligence → Result**

```
User configures sources (Settings)
         ↓
Scraper runs daily/on-demand
         ↓
Trend Detection analyzes spikes
  → Adjusts scraping limits for trending topics
         ↓
Quality Scoring ranks items
  → Filters low-engagement content
         ↓
Content appears in Content Library (sorted by quality)
         ↓
User gives 👍/👎 feedback
         ↓
Style Learning updates GPT-4 prompts
  → Future newsletters match user voice better
         ↓
Newsletter Generation uses top-quality items
         ↓
Email Delivery sends at 8am
         ↓
Analytics tracks opens/clicks (invisible to user)
```

---

## Implementation Tasks

### **Phase 1: Hide Advanced Pages** ✅ COMPLETE
- ✅ Remove navigation links for Trends, Analytics, Style, Feedback (app-header.tsx)
- ✅ Keep backend routes active
- ✅ Fixed: Dashboard "Save & Generate" now auto-generates newsletter
- [ ] Test: E2E test confirms simplified navigation

### **Phase 2: Dashboard Enhancement** ✅ ALREADY COMPLETE
- ✅ Newsletter preview component (with first 3 items)
- ✅ Quick stats cards (subscriber count, open rate, trends)
- ✅ CTAs: "Review Content", "Generate Newsletter", "Preview Draft", "Send Now"
- ✅ Schedule status display (Next run time)
- ✅ Empty state with "Configure Sources" CTA
- ✅ Welcome section with progress tracking
- [ ] Add workspace switcher for agencies (TODO)
- [ ] Test: E2E test for dashboard user journey

### **Phase 3: Settings Page Build** ✅ ALREADY COMPLETE
- ✅ Source configuration UI (Reddit, Twitter, YouTube, RSS, Blog)
- ✅ Delivery settings UI (email, schedule, frequency)
- ✅ Subscriber management UI
- ✅ Email configuration UI
- ✅ API Keys settings
- ✅ Advanced settings (Style, Trends, Analytics, Feedback) - marked isAdvanced
- ✅ Workspace settings UI
- [ ] Add workspace scoping for agencies (TODO)
- [ ] Test: E2E test for source configuration
- [ ] Test: E2E test for workspace isolation (agency)

### **Phase 4: Content Library Polish** ✅ ALREADY COMPLETE
- ✅ Thumbnails with fallback icons
- ✅ Source badges (color-coded)
- ✅ Inline feedback (👍 Keep | 👎 Skip)
- ✅ Filter tabs and search
- ✅ Staggered animations
- [ ] Test: E2E test for inline feedback
- [ ] Test: E2E test for thumbnail display

### **Phase 5: Integration Testing** 🔄 IN PROGRESS
- [ ] Test: Full user journey (setup → scrape → feedback → generate → send)
- [ ] Test: Agency user journey (multi-workspace)
- [ ] Test: Invisible intelligence verification (trend detection, quality scoring)

---

## Testing Strategy

**Comprehensive 3-Layer Testing Pyramid:**
- **E2E Tests (Playwright):** Critical user journeys (frontend → backend → database)
- **Backend Integration Tests:** API + database + pipeline orchestrator
- **Backend Unit Tests:** Business logic (trend detection, quality scoring, style learning)

---

### **Layer 1: E2E Tests (Playwright)**

**Purpose:** Test complete user journeys from UI interaction to database verification

**Framework:**
- Playwright (already configured with fixtures)
- Supabase helper for database verification
- Existing test user: juhinebhnani4@gmail.com / 12345678

---

#### **Journey 1: Individual User Onboarding (New User Flow)**

**File:** `frontend-nextjs/e2e/journey-mvp-individual-user.spec.ts`

**Test Steps:**
```typescript
1. Register new user (or login existing)
2. Land on Dashboard (empty state)
   → Verify: "Configure sources to get started" message
   → Verify: CTA button to Settings
3. Navigate to Settings
4. Configure sources:
   - Add Reddit subreddit: r/technology
   - Add YouTube channel: Fireship
   - Add RSS feed: https://news.ycombinator.com/rss
   - Set delivery: email + 8am
5. Save settings
   → Verify: Database updated (Supabase verification)
6. Trigger scraping (manual)
   → Verify: Content appears in Content Library
   → Verify: Thumbnails display correctly
7. Navigate to Content Library
8. Give inline feedback (👍 on 2 items, 👎 on 1 item)
   → Verify: Feedback saved to database
9. Navigate to Dashboard
10. Click "Generate Newsletter"
    → Verify: Newsletter preview appears
11. Verify email sent (check delivery logs)
```

**Database Verification:**
- User exists in `users` table
- Workspace created in `workspaces` table
- Sources saved in workspace config
- Content items in `content_items` table with `image_url`
- Feedback in `feedback` table with correct ratings

**Design Verification:**
- Verify gradient header: `bg-gradient-to-r from-primary to-primary/60`
- Verify animations: `animate-slide-up` on content cards
- Verify no CSS changes

---

#### **Journey 2: Agency Multi-Workspace (Agency User Flow)**

**File:** `frontend-nextjs/e2e/journey-mvp-agency-user.spec.ts`

**Test Steps:**
```typescript
1. Login as agency user
2. Create Workspace "Client A - Tech Newsletter"
   → Verify: Workspace switcher shows "Client A"
3. Configure sources for Client A:
   - Reddit: r/technology, r/programming
   - YouTube: Fireship, Theo
4. Save settings
5. Trigger scraping for Client A
   → Verify: Content appears scoped to Client A
6. Create Workspace "Client B - Marketing Newsletter"
   → Verify: Workspace switcher shows "Client A" + "Client B"
7. Switch to Client B workspace
8. Configure different sources for Client B:
   - Reddit: r/marketing, r/socialmedia
   - RSS: Marketing blogs
9. Save settings
10. Trigger scraping for Client B
    → Verify: Content appears scoped to Client B
11. Switch back to Client A
    → Verify: Content shows only Client A items (isolation)
12. Navigate to Content Library
    → Verify: Content filtered by workspace
13. Give feedback in Client A workspace
    → Verify: Feedback saved with correct workspace_id
14. Switch to Client B
    → Verify: Different content, different feedback
```

**Database Verification:**
- Multiple workspaces for same user
- Content items have correct `workspace_id`
- Feedback has correct `workspace_id`
- Workspace isolation (no cross-contamination)

---

#### **Journey 3: Invisible Intelligence Verification**

**File:** `frontend-nextjs/e2e/journey-invisible-intelligence.spec.ts`

**Test Steps:**
```typescript
1. Login
2. Configure sources with trending topic (e.g., "AI")
3. Trigger scraping
   → Wait for scraping to complete
4. Verify Trend Detection (Backend Intelligence):
   - Call API: GET /api/v1/trends?workspace_id=X
   - Verify: Trending topics detected
   - Verify: Spike detection ran (check response)
5. Verify Quality Scoring (Backend Intelligence):
   - Navigate to Content Library
   - Verify: Items sorted by quality (high engagement first)
   - Check first item: score + comments + views > 0
6. Give inline feedback (👍 on 3 items)
7. Verify Style Learning (Backend Intelligence):
   - Call API: GET /api/v1/style?workspace_id=X
   - Verify: Style preferences updated
   - Verify: Feedback count incremented
8. Generate newsletter
9. Verify Analytics Tracking (Backend Intelligence):
   - Call API: GET /api/v1/analytics?workspace_id=X
   - Verify: Newsletter generated event tracked
   - Verify: Timestamp recorded
10. Send newsletter
11. Verify Email Analytics:
    - Check tracking pixel in email HTML
    - Verify: Open/click tracking URLs present
```

**Backend API Verification:**
- `/api/v1/trends` returns trending topics
- `/api/v1/content?workspace_id=X` returns quality-sorted items
- `/api/v1/style?workspace_id=X` returns updated preferences
- `/api/v1/analytics?workspace_id=X` returns tracking data
- `/api/v1/feedback` saves ratings correctly

**Invisible Intelligence Checklist:**
- ✅ Trend detection runs after scraping
- ✅ Quality scoring sorts content
- ✅ Style learning updates from feedback
- ✅ Analytics tracks all actions

---

#### **Journey 4: Simplified Navigation**

**File:** `frontend-nextjs/e2e/journey-simplified-navigation.spec.ts`

**Test Steps:**
```typescript
1. Login
2. Verify sidebar shows ONLY:
   - Dashboard
   - Content Library
   - Settings
   - (Workspace switcher for agencies)
   - User Menu
3. Verify sidebar does NOT show:
   - Trends
   - Analytics
   - Style
   - Feedback
4. Attempt to navigate to hidden pages directly:
   - Navigate to /app/trends
   - Verify: Page loads (route exists)
   - Verify: No navigation link in sidebar
5. Verify backend routes still work:
   - Call API: GET /api/v1/trends
   - Verify: 200 OK response
   - Call API: GET /api/v1/analytics
   - Verify: 200 OK response
6. Trigger scraping
7. Verify invisible intelligence still runs:
   - Check content sorting (quality score)
   - Check API logs for trend detection
8. Give feedback
9. Verify style learning still runs:
   - Call /api/v1/style API
   - Verify: Preferences updated
```

**Navigation Verification:**
- ✅ Only 3 pages visible in sidebar
- ✅ Hidden pages not accessible via navigation
- ✅ Hidden page routes still work (direct URL)
- ✅ Backend intelligence runs independently

**Design Verification:**
- ✅ Sidebar styling unchanged
- ✅ Removed links don't break layout
- ✅ Gradients, animations, shadows intact

---

### **Layer 2: Backend Integration Tests**

**Purpose:** Test API + database + pipeline without frontend

---

#### **Integration Test 1: Pipeline Orchestrator**

**File:** `backend/tests/integration/test_pipeline_orchestrator.py`

**Test Steps:**
```python
def test_pipeline_full_flow():
    """Test complete pipeline: scrape → filter → generate → send"""

    # Setup
    workspace_id = create_test_workspace()
    configure_test_sources(workspace_id)

    # Run pipeline
    pipeline = NewsletterPipeline(workspace_id)
    result = pipeline.run_newsletter_pipeline()

    # Verify scraping
    assert result.items_scraped > 0
    assert result.success == True

    # Verify content saved to database
    content_items = db.get_content_items(workspace_id)
    assert len(content_items) > 0
    assert content_items[0].image_url is not None  # Thumbnails extracted

    # Verify quality scoring
    assert content_items[0].quality_score > 0

    # Verify newsletter generated
    assert result.newsletter_generated == True

    # Verify email sent
    assert result.email_sent == True

    # Cleanup
    db.cleanup_test_workspace(workspace_id)
```

---

#### **Integration Test 2: Invisible Intelligence**

**File:** `backend/tests/integration/test_invisible_intelligence.py`

**Test Steps:**
```python
def test_trend_detection():
    """Test trend detection after scraping"""

    # Setup
    workspace_id = create_test_workspace()
    scrape_content(workspace_id)

    # Run trend detection
    trends = TrendDetector.detect_trends(workspace_id)

    # Verify trends detected
    assert len(trends) > 0
    assert trends[0].spike_score > 0
    assert trends[0].topic is not None

def test_quality_scoring():
    """Test quality scoring on content"""

    # Setup
    content_items = scrape_test_content()

    # Run quality scoring
    scored_items = QualityScorer.score_items(content_items)

    # Verify scores assigned
    assert all(item.quality_score > 0 for item in scored_items)
    # Verify sorted by quality
    assert scored_items[0].quality_score >= scored_items[-1].quality_score

def test_style_learning():
    """Test style learning from feedback"""

    # Setup
    workspace_id = create_test_workspace()
    give_test_feedback(workspace_id, rating=5, count=10)

    # Run style learning
    StyleLearner.update_preferences(workspace_id)

    # Verify preferences updated
    style_profile = db.get_style_profile(workspace_id)
    assert style_profile.positive_feedback_count == 10
    assert style_profile.last_updated > initial_time
```

---

### **Layer 3: Backend Unit Tests**

**Purpose:** Test business logic in isolation

---

#### **Unit Test 1: Thumbnail Extraction**

**File:** `backend/tests/unit/test_thumbnail_extraction.py`

**Already Created:** ✅
- Tests YouTube thumbnail fallback (high → medium → default)
- Tests Reddit URL validation
- Tests Blog Open Graph extraction
- Tests RSS feed media extraction

---

#### **Unit Test 2: Trend Detection Algorithm**

**File:** `backend/tests/unit/test_trend_detection.py`

**Test Steps:**
```python
def test_spike_detection():
    """Test spike detection algorithm"""

    # Mock data: 10 items on day 1, 100 items on day 2 (spike!)
    content_history = [
        ContentBatch(date='2025-01-01', count=10),
        ContentBatch(date='2025-01-02', count=100),
    ]

    detector = TrendDetector()
    spike = detector.detect_spike(content_history)

    assert spike.detected == True
    assert spike.spike_ratio == 10.0  # 10x increase
    assert spike.topic is not None

def test_no_spike_detection():
    """Test no spike when content is stable"""

    content_history = [
        ContentBatch(date='2025-01-01', count=10),
        ContentBatch(date='2025-01-02', count=12),
    ]

    detector = TrendDetector()
    spike = detector.detect_spike(content_history)

    assert spike.detected == False
```

---

#### **Unit Test 3: Quality Scoring**

**File:** `backend/tests/unit/test_quality_scoring.py`

**Test Steps:**
```python
def test_quality_score_calculation():
    """Test quality score formula"""

    item = ContentItem(
        score=100,  # Reddit upvotes
        comments_count=50,
        views_count=1000,
    )

    scorer = QualityScorer()
    quality_score = scorer.calculate_score(item)

    # Formula: score + comments + (views / 10)
    expected_score = 100 + 50 + (1000 / 10) = 250
    assert quality_score == expected_score

def test_quality_sorting():
    """Test items sorted by quality"""

    items = [
        ContentItem(score=10, comments_count=5, views_count=100),
        ContentItem(score=100, comments_count=50, views_count=1000),
        ContentItem(score=50, comments_count=20, views_count=500),
    ]

    scorer = QualityScorer()
    sorted_items = scorer.sort_by_quality(items)

    # Highest quality first
    assert sorted_items[0].score == 100
    assert sorted_items[-1].score == 10
```

---

#### **Unit Test 4: Style Learning**

**File:** `backend/tests/unit/test_style_learning.py`

**Test Steps:**
```python
def test_style_preference_update():
    """Test style preferences update from feedback"""

    # Initial state
    style_profile = StyleProfile(positive_feedback_count=0)

    # User gives positive feedback
    feedback = Feedback(rating=5, content_type='technical')

    learner = StyleLearner()
    updated_profile = learner.update_preferences(style_profile, feedback)

    # Verify update
    assert updated_profile.positive_feedback_count == 1
    assert 'technical' in updated_profile.preferred_topics

def test_gpt4_prompt_adaptation():
    """Test GPT-4 prompt adapts to user preferences"""

    style_profile = StyleProfile(
        tone='casual',
        preferred_topics=['AI', 'startups'],
        positive_feedback_count=20
    )

    learner = StyleLearner()
    prompt = learner.generate_newsletter_prompt(style_profile)

    # Verify prompt includes preferences
    assert 'casual' in prompt.lower()
    assert 'AI' in prompt or 'startups' in prompt
```

---

### **Test Execution Plan**

**Order of Execution:**

1. **Backend Unit Tests** (fastest, no dependencies)
   ```bash
   cd backend
   ../.venv/Scripts/python.exe -m pytest tests/unit/ -v
   ```

2. **Backend Integration Tests** (requires database)
   ```bash
   cd backend
   ../.venv/Scripts/python.exe -m pytest tests/integration/ -v
   ```

3. **Frontend E2E Tests** (requires frontend + backend running)
   ```bash
   cd frontend-nextjs
   npm run test:e2e
   ```

**Success Criteria:**
- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ All E2E tests pass (100%)
- ✅ Design aesthetic preserved (verified in E2E tests)
- ✅ Invisible intelligence verified (backend tests + E2E Journey 3)

---

### **Test Coverage Goals**

- **Backend Unit Tests:** 80%+ code coverage
- **Backend Integration Tests:** 60%+ critical path coverage
- **E2E Tests:** 100% user journey coverage (4 journeys)

**Total Test Suite:**
- ~15 backend unit tests
- ~10 backend integration tests
- ~4 E2E journey tests
- **Total: ~30 comprehensive tests**

---

## Success Criteria

**MVP Launch:**
- ✅ 3-page UI (Dashboard, Content, Settings)
- ✅ Source configuration works (all 5 scrapers)
- ✅ Content scraping works with thumbnails
- ✅ Inline feedback (👍/👎) saves to database
- ✅ Newsletter generation works
- ✅ Email delivery works
- ✅ Workspace isolation for agencies
- ✅ Invisible intelligence runs (trend detection, quality scoring, style learning)
- ✅ Design aesthetic preserved (MyMiraya gradients, animations, shadows)

**KPIs (90 days):**
- Newsletter drafting time: ≤20 minutes
- Draft acceptance rate: ≥70%
- Engagement uplift: ≥2× baseline open rates

---

## Files to Modify

### **Frontend:**

**Navigation:**
- [ ] `frontend-nextjs/src/components/layout/app-sidebar.tsx` - Remove links to Trends/Analytics/Style/Feedback

**Dashboard:**
- [ ] `frontend-nextjs/src/app/app/page.tsx` - Build newsletter preview + stats + CTAs

**Settings:**
- [ ] `frontend-nextjs/src/app/app/settings/page.tsx` - Build source config + delivery settings

**Content Library:**
- ✅ Already complete with thumbnails + inline feedback

### **Backend:**
- ✅ No changes needed - all routes already exist
- ✅ Pipeline already orchestrates invisible intelligence

### **Tests:**
- [ ] `frontend-nextjs/e2e/journey-mvp-individual-user.spec.ts` - New
- [ ] `frontend-nextjs/e2e/journey-mvp-agency-user.spec.ts` - New
- [ ] `frontend-nextjs/e2e/journey-invisible-intelligence.spec.ts` - New
- [ ] `frontend-nextjs/e2e/journey-simplified-navigation.spec.ts` - New

---

## Design Constraints

**CRITICAL: Zero CSS Changes**

**What CANNOT Change:**
- ❌ Color palette (coral, teal, gradients)
- ❌ Animations (slide-up, celebration, pulse)
- ❌ Typography hierarchy
- ❌ Spacing system
- ❌ Shadow effects
- ❌ Hover states
- ❌ Transitions

**What CAN Change:**
- ✅ HTML elements (add/remove)
- ✅ Navigation links (remove 4 links)
- ✅ Page components (build Dashboard, Settings)
- ✅ Data-testid attributes (invisible to user)

---

## Questions & Decisions

**Q: Do individual users configure sources?**
**A:** YES - Required for product to work. Without source config → no content → no newsletter.

**Q: What's hidden from UI?**
**A:** Trends, Analytics, Style, Feedback pages. Backend routes stay active, intelligence runs invisibly.

**Q: How does agency isolation work?**
**A:** Workspaces. Each workspace has its own sources, content, newsletters. Workspace switcher in sidebar.

**Q: What's the simplest MVP?**
**A:** 3 pages: Dashboard (preview), Content (browse + feedback), Settings (sources + delivery).

**Q: How is backend intelligence maintained?**
**A:** All API routes stay active. Pipeline orchestrator runs on schedule. Invisible to user.

---

## Next Steps

1. **Create detailed todos** (this section)
2. **Build E2E test suite** (4 journey tests)
3. **Implement navigation simplification** (remove 4 links)
4. **Build Dashboard page** (preview + stats + CTAs)
5. **Build Settings page** (sources + delivery)
6. **Run full test suite** (verify everything works)
7. **Deploy MVP** (launch with 3-page UI)

---

**End of Source of Truth Document**
