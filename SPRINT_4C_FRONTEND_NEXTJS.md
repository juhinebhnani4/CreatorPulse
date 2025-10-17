# Sprint 4C: Next.js Frontend - Complete User Experience

## Overview
Build production-ready Next.js 14 frontend with **landing page**, **authentication**, **product dashboard**, and **extensibility for future features** (trends, style training, analytics, feedback).

**Status:** 🚧 In Progress

**Based On:**
- [frontend.txt](frontend.txt) - Design principles
- [frontend-review.txt](frontend-review.txt) - UX review & critical fixes
- [create.md](create.md) - Product requirements
- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Feature roadmap

---

## Key Decisions from UX Review

### 🔴 Critical Architecture Changes

1. **Draft Editor = Modal, NOT separate page**
   - ❌ OLD: User clicks button → navigates to `/app/draft/[id]` → sees editor
   - ✅ NEW: User clicks button → modal slides up → edits in place → stays in context
   - **Why:** Faster perceived performance, maintains mental model, modern pattern

2. **Dashboard Shows Draft Preview**
   - ❌ OLD: "Review & Send" button hides draft behind click
   - ✅ NEW: Show 3-5 article cards directly on dashboard
   - **Why:** Users want to SEE value immediately, not hunt for it

3. **Settings Ordered by Frequency**
   - ❌ OLD: Email first (one-time setup)
   - ✅ NEW: Sources first (modified 2-3x/week)
   - **Why:** Power users (80% of value) shouldn't scroll to frequent tasks

4. **Quick Actions on Dashboard**
   - ❌ OLD: Must go to Settings → Sources → Add Source (3 clicks)
   - ✅ NEW: "Add Source" button on dashboard (1 click opens modal)
   - **Why:** Most frequent task should be easiest

---

## Pages Structure (5 Total)

### Public Pages (2)

#### 1. Landing Page (`/`)
**Purpose:** Show value before asking for signup

**Content:**
- Hero: "AI Newsletter Drafts Every Morning"
- 3 benefits with icons
- Demo GIF or screenshot
- "Start Free Trial" CTA (no credit card)
- Social proof (if available)
- Footer links

**Routing Logic:**
```tsx
// If user is logged in → redirect to /app
// If user is logged out → show landing page
```

#### 2. Auth Pages (`/login`, `/register`)
**Purpose:** Simple authentication flow

**Content:**
- Login: Email + Password + "Continue with Google" (optional)
- Register: Email + Password + Name
- Password reset link
- Redirect to `/app` after success

**Tech:** NextAuth.js for auth handling

---

### Product Pages (3) - Require Auth

#### 3. Dashboard (`/app`) ⭐ **MAIN SCREEN**
**Purpose:** Daily entry point - see draft status and send

**Layout:**
```
[Header with workspace selector]

[Draft Status Card]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: "Ready to send" / "Generating... 45 sec" / "Next at 8 AM tomorrow"

[Subject Line Preview]
Daily AI Digest - October 16

[Article Preview Cards - 3 visible]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 GPT-4 Turbo Hits New Reasoning Milestone
OpenAI announces breakthrough in reasoning capabilities...
[Edit inline on hover]

📌 Why AI Agents Will Replace 40% of Jobs
New study reveals shocking timeline for automation...
[Edit inline on hover]

📌 The Surprising Truth About LLM Context Windows
Research shows bigger isn't always better...
[Edit inline on hover]

[Primary Actions]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Preview Full Draft]  [Send Now]

[Quick Source Manager]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Your Sources
✓ Reddit (r/MachineLearning) - 5 items  [⏸ Pause]
✓ Hacker News - 4 items  [⏸ Pause]
✓ Twitter (@OpenAI) - 3 items  [⏸ Pause]
[+ Add Source]

[Stats Overview - Below Fold]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1,234 Subscribers | Last sent: Oct 15 | Open rate: 34% ↑
```

**Key Features:**
- Draft preview visible immediately (no hidden content)
- Inline editing on hover (pencil icon appears)
- Quick source management (add/pause without Settings)
- Primary action clear: "Send Now" button
- Empty state for new users: "First draft tomorrow at 8 AM. Add sources now →"

**Modals Triggered:**
- Click "Preview Full Draft" → Opens Draft Editor Modal
- Click "Send Now" → Opens Send Confirmation Modal
- Click "Add Source" → Opens Quick Add Source Modal

---

#### 4. Settings (`/app/settings`)
**Purpose:** ALL configuration in ONE page

**Layout:**
```
[Search Settings]
[Search box at top - filters accordions]

[Accordion Sections - Ordered by Frequency]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▼ 📱 Content Sources (FIRST - modified 2-3x/week)
  - Reddit: Subreddits, limits
  - RSS: Feed URLs
  - X/Twitter: Handles, hashtags
  - YouTube: Channel URLs
  - Blogs: URLs with crawling settings
  [Save] button at bottom

▼ ⏰ Schedule Settings (SECOND - modified 1x/month)
  - Daily time: 8:00 AM
  - Timezone: America/New_York
  - Frequency: Daily / Weekly / Custom
  [Save]

▼ 👥 Subscribers (THIRD - occasional)
  - Import CSV
  - Export CSV
  - Manual add/remove
  - Subscriber list table
  [Import] [Export]

▼ 📧 Email Configuration (one-time setup)
  - Provider: SMTP / SendGrid
  - SMTP: Host, Port, Username, Password
  - SendGrid: API Key
  - From email, From name
  [Test Email] [Save]

▼ 🔑 API Keys (one-time setup)
  - OpenAI API Key
  - OpenRouter API Key
  - YouTube API Key (optional)
  - X API Keys (optional)
  [Save]

▼ 🏢 Workspace Management (one-time)
  - Workspace name: [editable]
  - Create new workspace
  - Delete workspace (if not default)
  [Save]

▼ ✍️ Writing Style [FUTURE - Sprint 5C]
  - Upload past newsletter samples
  - Train style model
  - View style profile
  [Collapsed by default, disabled until backend ready]

▼ 🔥 Trends Detection [FUTURE - Sprint 5B]
  - Enable/disable trends section
  - Min confidence level
  - Max trends per newsletter
  [Collapsed by default, disabled until backend ready]

▼ 📊 Analytics [FUTURE - Sprint 5A]
  - Tracking pixel settings
  - UTM parameters
  - Analytics provider integration
  [Collapsed by default, disabled until backend ready]

▼ 💬 Feedback Loop [FUTURE - Sprint 6]
  - Enable feedback tracking
  - Auto-learning settings
  [Collapsed by default, disabled until backend ready]
```

**Key Features:**
- Search box filters accordions (type "email" → shows only Email Configuration)
- Frequency-based ordering (most used first)
- Future sections present but collapsed/disabled (shows roadmap)
- Auto-save on change (no submit button hunting)

---

#### 5. History (`/app/history`)
**Purpose:** View past newsletters and performance

**Layout:**
```
[Date Range Selector]
[Last 7 days ▼] [Last 30 days] [Custom Range]

[Newsletter Cards - List View]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily AI Digest - October 15
Sent to 1,234 subscribers at 8:00 AM

34% open rate  ↑ +3% from last week
12 clicks      ↓ -2 from last week
2 unsubscribes

[View Full Newsletter] [Duplicate] [Resend]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily AI Digest - October 14
...
```

**Key Features:**
- Trend indicators (↑↓) with delta
- Performance comparison (vs last week)
- Actions: View, Duplicate, Resend

---

### Modals (Not Separate Pages)

#### Draft Editor Modal
**Triggered by:** "Preview Full Draft" button on dashboard

**Content:**
- Full newsletter preview (all items, not just 3)
- Subject line editor at top (inline editable)
- Mobile/Desktop toggle
- Inline editing for each article
- Trending section (if enabled)
- Footer actions: [Send Test] [Send Later ▼] [Send Now]
- Auto-save status bar at bottom

**Tech:** Radix UI Dialog (handles focus trap, accessibility, Escape key)

#### Send Confirmation Modal
**Triggered by:** "Send Now" button

**Content:**
```
Send Newsletter?

You're about to send to 1,234 subscribers.
This action cannot be undone.

[Cancel] [Send to 1,234 Subscribers]
```

**Why:** Email is destructive/irreversible, requires confirmation

#### Quick Add Source Modal
**Triggered by:** "Add Source" button on dashboard

**Content:**
```
Add Content Source

[Reddit] [RSS] [X/Twitter] [YouTube] [Blog]

Selected: Reddit
Subreddit: [r/MachineLearning]
Max items: [10]

[Cancel] [Add Source]
```

**After save:** Closes modal, regenerates draft with new source

#### Schedule Send Modal
**Triggered by:** "Send Later" dropdown

**Content:**
```
Schedule Newsletter

Send at:
⚬ In 1 hour (2:30 PM today)
⚬ Tomorrow at 8:00 AM
⚬ Custom: [Date Picker] [Time Picker]

[Cancel] [Schedule Send]
```

---

## Component Architecture

### Core Components

#### 1. Article Card (`components/dashboard/article-card.tsx`)
**Purpose:** Display newsletter item with inline editing

**States:**
- Default: Read-only view
- Hover: Shows pencil icon
- Edit: Inline form for headline, summary, link
- Saving: Shows "Saving..." indicator
- Saved: Shows "Saved ✓" confirmation

**Props:**
```tsx
interface ArticleCardProps {
  item: ContentItem;
  editable: boolean;
  onEdit: (item: ContentItem) => Promise<void>;
}
```

**Behavior:**
- Hover → pencil icon appears
- Click pencil → edit mode (headline, summary, link fields)
- Edit → auto-save with 1s debounce
- Save → "Saved ✓" toast

#### 2. Draft Status Card (`components/dashboard/draft-status-card.tsx`)
**Purpose:** Show current draft status

**States:**
- Ready: "Your newsletter is ready to send!"
- Generating: "Generating your draft... 45 seconds" (progress bar)
- Scheduled: "Next draft arrives tomorrow at 8:00 AM"
- Empty: "No draft yet. Add sources to get started →"

**Props:**
```tsx
interface DraftStatusCardProps {
  status: 'ready' | 'generating' | 'scheduled' | 'empty';
  nextRunAt?: Date;
  progress?: number; // 0-100 for generating state
}
```

#### 3. Quick Source Manager (`components/dashboard/quick-source-manager.tsx`)
**Purpose:** Manage sources without going to Settings

**Features:**
- List active sources with item counts
- [⏸ Pause] button per source (pause for 24 hours)
- [+ Add Source] button (opens modal)
- Shows which sources contributed to current draft

**Props:**
```tsx
interface QuickSourceManagerProps {
  sources: Source[];
  onPause: (sourceId: string) => Promise<void>;
  onAdd: () => void; // Opens modal
}
```

#### 4. Draft Editor Modal (`components/modals/draft-editor-modal.tsx`)
**Purpose:** Full draft editing experience

**Sections:**
- Header: Subject line editor + Mobile/Desktop toggle
- Body: All article cards (inline editable)
- Trending: Trending topics section (editable)
- Footer: Auto-save status + Action buttons

**Props:**
```tsx
interface DraftEditorModalProps {
  open: boolean;
  onClose: () => void;
  draftId: string;
}
```

**Features:**
- Escape key closes modal
- Cmd+S manual save
- Cmd+Enter sends newsletter
- Auto-save every 1s (debounced)

#### 5. Subject Line Editor (`components/draft/subject-line-editor.tsx`)
**Purpose:** Edit subject line with character count

**Features:**
- Inline editable text
- Character count (optimal: 40-60 chars)
- Color indicator (red < 40, green 40-60, yellow > 60)
- AI-generated suggestion (if available)

---

## Technical Stack

### Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",

    "tailwindcss": "^3.4.0",
    "@tailwindcss/typography": "^0.5.10",

    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",

    "react-hook-form": "^7.49.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.4",

    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.2",

    "zustand": "^4.4.7",

    "next-auth": "^4.24.5",

    "date-fns": "^3.0.0",
    "react-hot-toast": "^2.4.1",
    "use-debounce": "^10.0.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "eslint": "^8.55.0",
    "eslint-config-next": "^14.0.0"
  }
}
```

### Why These Libraries?

**Radix UI:**
- Unstyled, accessible components
- Used by shadcn/ui
- Handles focus management, keyboard nav, ARIA automatically

**React Hook Form + Zod:**
- Best-in-class form handling
- Type-safe validation
- Minimal re-renders

**TanStack Query:**
- Server state management
- Auto caching, refetching, invalidation
- Loading/error states built-in

**Zustand:**
- Lightweight global state
- For UI state only (auth, workspace switching)
- No boilerplate

**NextAuth:**
- Industry-standard auth for Next.js
- JWT tokens, session management
- OAuth providers ready

**use-debounce:**
- Auto-save without hammering API
- 1s delay for text input

---

## File Structure

```
frontend-nextjs/
├── src/
│   ├── app/
│   │   ├── (marketing)/
│   │   │   ├── layout.tsx              # Marketing layout (no sidebar)
│   │   │   └── page.tsx                # Landing page
│   │   │
│   │   ├── (auth)/
│   │   │   ├── layout.tsx              # Auth layout (centered form)
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (product)/
│   │   │   ├── layout.tsx              # Product layout (header + auth check)
│   │   │   └── app/
│   │   │       ├── page.tsx            # Dashboard
│   │   │       ├── settings/
│   │   │       │   └── page.tsx        # Settings (ONE page)
│   │   │       └── history/
│   │   │           └── page.tsx        # History
│   │   │
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...nextauth]/
│   │   │           └── route.ts        # NextAuth config
│   │   │
│   │   ├── layout.tsx                  # Root layout
│   │   ├── globals.css                 # Global styles
│   │   └── not-found.tsx               # 404 page
│   │
│   ├── components/
│   │   ├── ui/                         # Radix UI components (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── accordion.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── select.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   └── skeleton.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── header.tsx              # App header
│   │   │   ├── workspace-dropdown.tsx  # Workspace switcher
│   │   │   ├── footer.tsx              # App footer
│   │   │   └── navigation.tsx          # Main nav
│   │   │
│   │   ├── dashboard/
│   │   │   ├── draft-status-card.tsx
│   │   │   ├── article-card.tsx
│   │   │   ├── quick-source-manager.tsx
│   │   │   ├── stats-overview.tsx
│   │   │   └── empty-state.tsx
│   │   │
│   │   ├── draft/
│   │   │   ├── subject-line-editor.tsx
│   │   │   ├── trending-section.tsx
│   │   │   ├── edit-form.tsx
│   │   │   └── mobile-preview-toggle.tsx
│   │   │
│   │   ├── modals/
│   │   │   ├── draft-editor-modal.tsx
│   │   │   ├── send-confirmation-modal.tsx
│   │   │   ├── add-source-modal.tsx
│   │   │   └── schedule-send-modal.tsx
│   │   │
│   │   ├── settings/
│   │   │   ├── sources-settings.tsx
│   │   │   ├── schedule-settings.tsx
│   │   │   ├── subscribers-settings.tsx
│   │   │   ├── email-settings.tsx
│   │   │   ├── api-keys-settings.tsx
│   │   │   ├── workspace-settings.tsx
│   │   │   ├── style-settings.tsx      # [FUTURE]
│   │   │   ├── trends-settings.tsx     # [FUTURE]
│   │   │   ├── analytics-settings.tsx  # [FUTURE]
│   │   │   └── feedback-settings.tsx   # [FUTURE]
│   │   │
│   │   ├── landing/
│   │   │   ├── hero.tsx
│   │   │   ├── features.tsx
│   │   │   ├── demo.tsx
│   │   │   └── cta.tsx
│   │   │
│   │   └── common/
│   │       ├── loading-state.tsx
│   │       ├── error-state.tsx
│   │       ├── empty-state.tsx
│   │       └── status-badge.tsx
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts               # Axios with auth interceptor
│   │   │   ├── auth.ts
│   │   │   ├── workspaces.ts
│   │   │   ├── content.ts
│   │   │   ├── newsletters.ts
│   │   │   ├── subscribers.ts
│   │   │   ├── delivery.ts
│   │   │   ├── scheduler.ts
│   │   │   ├── trends.ts               # [FUTURE]
│   │   │   ├── style.ts                # [FUTURE]
│   │   │   ├── feedback.ts             # [FUTURE]
│   │   │   └── analytics.ts            # [FUTURE]
│   │   │
│   │   ├── hooks/
│   │   │   ├── use-auth.ts
│   │   │   ├── use-workspace.ts
│   │   │   ├── use-draft.ts
│   │   │   ├── use-newsletters.ts
│   │   │   ├── use-auto-save.ts
│   │   │   ├── use-keyboard-shortcuts.ts
│   │   │   ├── use-undo-redo.ts
│   │   │   └── use-api.ts
│   │   │
│   │   ├── stores/
│   │   │   ├── auth-store.ts           # Auth state (user, token)
│   │   │   ├── workspace-store.ts      # Current workspace
│   │   │   └── ui-store.ts             # UI state (modals, etc)
│   │   │
│   │   └── utils/
│   │       ├── cn.ts                   # clsx + tailwind-merge
│   │       ├── format.ts               # "1.2K subscribers", "2 hours ago"
│   │       ├── validation.ts           # Zod schemas
│   │       └── constants.ts
│   │
│   ├── types/
│   │   ├── api.ts                      # API response types
│   │   ├── newsletter.ts
│   │   ├── workspace.ts
│   │   ├── user.ts
│   │   └── content.ts
│   │
│   └── middleware.ts                   # Auth middleware
│
├── public/
│   ├── logo.svg
│   ├── demo.gif
│   └── favicon.ico
│
├── .env.example
├── .env.local
├── .eslintrc.json
├── components.json                     # shadcn/ui config
├── next.config.js
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Environment Variables

### `.env.example`
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Info
NEXT_PUBLIC_APP_NAME=CreatorPulse
NEXT_PUBLIC_APP_VERSION=1.0.0

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here-change-in-production

# Optional: OAuth Providers
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### `.env.local` (User creates this)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-secure-key-here
```

---

## Implementation Phases

### Phase 1: Foundation (Days 1-2) - 16 hours

**Tasks:**
1. Initialize Next.js 14 project
   ```bash
   npx create-next-app@latest frontend-nextjs \
     --typescript --tailwind --eslint --app --src-dir
   ```

2. Install dependencies
   ```bash
   npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
     @radix-ui/react-accordion @tanstack/react-query axios zustand \
     next-auth react-hook-form zod use-debounce date-fns
   ```

3. Setup shadcn/ui
   ```bash
   npx shadcn-ui@latest init
   npx shadcn-ui@latest add button input dialog dropdown-menu \
     accordion toast select card badge skeleton
   ```

4. Create API client with auth interceptor
   - `lib/api/client.ts` - Axios instance
   - Add auth token to headers
   - Handle 401 errors (logout)

5. Setup Zustand stores
   - `lib/stores/auth-store.ts` - Auth state
   - `lib/stores/workspace-store.ts` - Current workspace
   - `lib/stores/ui-store.ts` - Modal states

6. Create layouts
   - `app/(marketing)/layout.tsx` - No header
   - `app/(auth)/layout.tsx` - Centered form
   - `app/(product)/layout.tsx` - Header + auth check

**Deliverable:** Project structure ready, auth flow working

---

### Phase 2: Public Pages (Day 2-3) - 12 hours

**Tasks:**
1. Landing page (`app/(marketing)/page.tsx`)
   - Hero section with value prop
   - Features grid (3 benefits)
   - Demo GIF/screenshot
   - CTA button
   - Redirect to `/app` if logged in

2. Login page (`app/(auth)/login/page.tsx`)
   - Email + password form
   - "Continue with Google" (optional)
   - Link to register

3. Register page (`app/(auth)/register/page.tsx`)
   - Name + email + password
   - Link to login

4. NextAuth setup (`app/api/auth/[...nextauth]/route.ts`)
   - JWT strategy
   - Credentials provider
   - Session management

**Deliverable:** Users can land, sign up, log in

---

### Phase 3: Dashboard Core (Days 3-4) - 16 hours

**Tasks:**
1. Dashboard page (`app/(product)/app/page.tsx`)
   - Draft status card
   - Article preview cards (3 visible)
   - Primary action buttons
   - Quick source manager
   - Stats overview

2. Article Card component (`components/dashboard/article-card.tsx`)
   - Read-only view
   - Hover state (pencil icon)
   - Inline editing mode
   - Auto-save with debounce

3. Draft Status Card (`components/dashboard/draft-status-card.tsx`)
   - 4 states: ready/generating/scheduled/empty
   - Progress bar for generating
   - Empty state CTA

4. Quick Source Manager (`components/dashboard/quick-source-manager.tsx`)
   - List sources with counts
   - Pause button per source
   - Add source button

5. Stats Overview (`components/dashboard/stats-overview.tsx`)
   - Subscriber count
   - Last sent date
   - Open rate with trend

**Deliverable:** Dashboard shows draft preview, users can see value immediately

---

### Phase 4: Modals & Editing (Days 4-5) - 16 hours

**Tasks:**
1. Draft Editor Modal (`components/modals/draft-editor-modal.tsx`)
   - Full newsletter preview
   - Subject line editor
   - Mobile/Desktop toggle
   - All article cards (inline editable)
   - Trending section
   - Footer actions

2. Subject Line Editor (`components/draft/subject-line-editor.tsx`)
   - Inline editable
   - Character count
   - Color indicator

3. Send Confirmation Modal (`components/modals/send-confirmation-modal.tsx`)
   - Subscriber count
   - Cancel + Send buttons

4. Add Source Modal (`components/modals/add-source-modal.tsx`)
   - Source type selector
   - Source-specific fields
   - Save + regenerate draft

5. Schedule Send Modal (`components/modals/schedule-send-modal.tsx`)
   - Preset options
   - Custom date/time picker

6. Auto-save hook (`lib/hooks/use-auto-save.ts`)
   - Debounce 1s
   - Visual feedback
   - Error handling

7. Undo/Redo hook (`lib/hooks/use-undo-redo.ts`)
   - Cmd+Z / Cmd+Shift+Z
   - History stack (localStorage)

**Deliverable:** Full editing experience, modal-based, inline editing works

---

### Phase 5: Settings (Day 5) - 8 hours

**Tasks:**
1. Settings page (`app/(product)/app/settings/page.tsx`)
   - Search box (filters accordions)
   - Frequency-ordered accordions

2. Settings sections:
   - Sources (`components/settings/sources-settings.tsx`)
   - Schedule (`components/settings/schedule-settings.tsx`)
   - Subscribers (`components/settings/subscribers-settings.tsx`)
   - Email (`components/settings/email-settings.tsx`)
   - API Keys (`components/settings/api-keys-settings.tsx`)
   - Workspace (`components/settings/workspace-settings.tsx`)

3. Future sections (collapsed, disabled):
   - Style (`components/settings/style-settings.tsx`)
   - Trends (`components/settings/trends-settings.tsx`)
   - Analytics (`components/settings/analytics-settings.tsx`)
   - Feedback (`components/settings/feedback-settings.tsx`)

**Deliverable:** All configuration in one place, future-ready

---

### Phase 6: History & Polish (Days 5-6) - 16 hours

**Tasks:**
1. History page (`app/(product)/app/history/page.tsx`)
   - Date range selector
   - Newsletter cards with stats
   - Trend indicators (↑↓)
   - View/Duplicate/Resend actions

2. Loading states (`components/common/loading-state.tsx`)
   - Skeleton loaders (not spinners)
   - Per component (card, table, page)

3. Empty states (`components/common/empty-state.tsx`)
   - First-time user (no drafts)
   - No sources configured
   - No subscribers
   - No history

4. Error states (`components/common/error-state.tsx`)
   - API errors with retry button
   - Validation errors (inline)

5. Keyboard shortcuts (`lib/hooks/use-keyboard-shortcuts.ts`)
   - Cmd+Enter = Send
   - Cmd+S = Save
   - Escape = Close modal
   - Tab = Navigate

6. Mobile responsive
   - Test at 375px
   - Touch targets ≥44px
   - Mobile menu if needed

**Deliverable:** Polished, production-ready UI

---

### Phase 7: Testing & Documentation (Day 7) - 8 hours

**Tasks:**
1. Integration testing
   - Login → Dashboard → Edit → Send flow
   - Multi-workspace switching
   - Settings save/load
   - Modal open/close

2. Accessibility audit
   - Keyboard navigation
   - Screen reader (ARIA labels)
   - Color contrast (WCAG AA)

3. Performance testing
   - Lighthouse score
   - Bundle size
   - First Contentful Paint

4. Documentation
   - Setup guide (README)
   - Environment variables
   - Development commands
   - Deployment guide

**Deliverable:** Tested, documented, ready to ship

---

## API Integration Checklist

### Backend Endpoints Used (Sprint 0-4B)

✅ **Auth** (`/api/v1/auth`)
- POST `/register` - Create account
- POST `/login` - Get JWT token
- POST `/logout` - Invalidate token
- GET `/me` - Get current user

✅ **Workspaces** (`/api/v1/workspaces`)
- POST `/workspaces` - Create workspace
- GET `/workspaces` - List user's workspaces
- GET `/workspaces/{id}` - Get workspace details
- PUT `/workspaces/{id}` - Update workspace
- DELETE `/workspaces/{id}` - Delete workspace

✅ **Content** (`/api/v1/content`)
- POST `/content/workspaces/{id}/scrape` - Scrape content
- GET `/content/workspaces/{id}` - List content
- GET `/content/workspaces/{id}/stats` - Get stats
- GET `/content/{id}` - Get content item

✅ **Newsletters** (`/api/v1/newsletters`)
- POST `/newsletters` - Generate newsletter
- GET `/newsletters/workspaces/{id}` - List newsletters
- GET `/newsletters/{id}` - Get newsletter
- PUT `/newsletters/{id}` - Update newsletter
- DELETE `/newsletters/{id}` - Delete newsletter

✅ **Subscribers** (`/api/v1/subscribers`)
- POST `/subscribers` - Add subscriber
- POST `/subscribers/bulk` - Bulk import
- GET `/subscribers/workspaces/{id}` - List subscribers
- GET `/subscribers/workspaces/{id}/stats` - Get stats
- PUT `/subscribers/{id}` - Update subscriber
- DELETE `/subscribers/{id}` - Delete subscriber

✅ **Delivery** (`/api/v1/delivery`)
- POST `/delivery/send` - Send newsletter
- POST `/delivery/test` - Send test email
- GET `/delivery/workspaces/{id}` - Delivery history
- GET `/delivery/{id}/status` - Delivery status

✅ **Scheduler** (`/api/v1/scheduler`)
- POST `/scheduler` - Create job
- GET `/scheduler/workspaces/{id}` - List jobs
- GET `/scheduler/{id}` - Get job
- PUT `/scheduler/{id}` - Update job
- DELETE `/scheduler/{id}` - Delete job
- POST `/scheduler/{id}/pause` - Pause job
- POST `/scheduler/{id}/resume` - Resume job
- POST `/scheduler/{id}/run-now` - Trigger now

### Future Endpoints (Sprint 5+)

🔜 **Trends** (`/api/v1/trends`)
- GET `/trends/workspaces/{id}` - Get trending topics
- POST `/trends/detect` - Detect trends from content

🔜 **Style** (`/api/v1/style`)
- POST `/style/train` - Train style model
- GET `/style/workspaces/{id}` - Get style profile
- PUT `/style/workspaces/{id}` - Update style

🔜 **Feedback** (`/api/v1/feedback`)
- POST `/feedback` - Submit feedback
- GET `/feedback/workspaces/{id}` - Get feedback data

🔜 **Analytics** (`/api/v1/analytics`)
- GET `/analytics/workspaces/{id}` - Get analytics
- GET `/analytics/newsletters/{id}` - Newsletter analytics

---

## Success Criteria

### Functional Requirements
- ✅ Visitor sees landing page and understands value in 5 seconds
- ✅ User can sign up and log in
- ✅ Dashboard shows draft preview immediately (not hidden)
- ✅ "Send Now" button is ONE primary action (above fold)
- ✅ Draft editor is modal (not page navigation)
- ✅ Inline editing works (hover → pencil → edit → save)
- ✅ All settings in ONE page (frequency-ordered accordions)
- ✅ Agency can create and switch workspaces
- ✅ Solo user doesn't see workspace switcher (if only 1 workspace)
- ✅ Quick add source from dashboard (1 click)
- ✅ Auto-save works with visual feedback
- ✅ Undo/Redo works (Cmd+Z)
- ✅ Send requires confirmation

### Design Principles (from frontend.txt)
- ✅ Exactly 1 primary button per screen
- ✅ Progressive disclosure (advanced options collapsed)
- ✅ User tasks not features ("Review Draft" not "Newsletter Generator")
- ✅ Action-first design (primary action visible above fold)
- ✅ All 4 states handled (loading/error/empty/success)
- ✅ Mobile works at 375px
- ✅ Keyboard accessible (Tab, Enter, Escape)
- ✅ Using Radix UI components (accessibility built-in)
- ✅ F-pattern layout
- ✅ No confirmations (except destructive actions like Send)
- ✅ Auto-save everything

### UX Improvements (from frontend-review.txt)
- ✅ Dashboard shows draft (not hidden behind "Review & Send")
- ✅ Settings ordered by frequency (Sources first)
- ✅ Quick add source on dashboard
- ✅ Draft editor is modal (not page)
- ✅ Inline editing with hover states
- ✅ Empty state for new users
- ✅ Auto-save status visible
- ✅ Mobile preview toggle
- ✅ Subject line prominent
- ✅ Schedule send dropdown
- ✅ Regenerate clarity
- ✅ Loading states (skeleton loaders)
- ✅ Settings searchable
- ✅ Keyboard shortcuts
- ✅ Undo/Redo
- ✅ Send confirmation

### Extensibility
- ✅ Future backend features = new accordion in Settings
- ✅ No structural changes needed for Sprint 5+
- ✅ API client ready for trends/style/feedback/analytics
- ✅ Settings sections present but collapsed/disabled

---

## Testing Checklist

### Manual Testing

**Authentication Flow:**
- [ ] Landing page loads
- [ ] Sign up creates account
- [ ] Login redirects to dashboard
- [ ] Logout clears session
- [ ] Invalid credentials show error
- [ ] Token refresh works

**Dashboard Flow:**
- [ ] Draft status card shows correct state
- [ ] Article preview cards visible (3)
- [ ] Inline editing works (hover → edit → save)
- [ ] "Preview Full Draft" opens modal
- [ ] "Send Now" opens confirmation
- [ ] Quick source manager shows sources
- [ ] "Add Source" opens modal
- [ ] Stats overview shows data

**Draft Editor Modal:**
- [ ] Modal opens from dashboard
- [ ] Subject line editable
- [ ] Mobile/Desktop toggle works
- [ ] All articles editable inline
- [ ] Trending section editable
- [ ] Auto-save status visible
- [ ] "Send Now" opens confirmation
- [ ] "Send Later" shows options
- [ ] "Send Test" sends test email
- [ ] Escape closes modal
- [ ] Cmd+S manual save works
- [ ] Cmd+Enter sends (with confirmation)

**Settings Page:**
- [ ] Search box filters accordions
- [ ] Sources accordion first
- [ ] All accordions save correctly
- [ ] Future sections collapsed/disabled
- [ ] Workspace switching works (if multiple)

**History Page:**
- [ ] Newsletter list loads
- [ ] Date range filter works
- [ ] Trend indicators show (↑↓)
- [ ] View opens newsletter
- [ ] Duplicate creates copy
- [ ] Resend confirms

**Keyboard Navigation:**
- [ ] Tab moves focus logically
- [ ] Enter activates primary action
- [ ] Escape closes modals
- [ ] Cmd+S saves draft
- [ ] Cmd+Enter sends newsletter
- [ ] Cmd+Z undo works
- [ ] Cmd+Shift+Z redo works

**Mobile Responsive:**
- [ ] Works at 375px width
- [ ] Touch targets ≥44px
- [ ] No horizontal scroll
- [ ] Modals fit screen
- [ ] Forms usable on mobile

**Accessibility:**
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Color contrast WCAG AA
- [ ] Screen reader friendly

---

## Deployment Guide

### Prerequisites
- Node.js 18+ installed
- Backend API running (http://localhost:8000)
- Environment variables configured

### Development

```bash
# Install dependencies
cd frontend-nextjs
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local with your values

# Run dev server
npm run dev

# Open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Test production build locally
npm start

# Deploy to Vercel (recommended)
npx vercel --prod
```

### Environment Variables (Production)
```bash
NEXT_PUBLIC_API_URL=https://api.creatorpulse.com
NEXTAUTH_URL=https://creatorpulse.com
NEXTAUTH_SECRET=<generate-secure-key>
```

---

## Timeline

| Phase | Tasks | Hours | Days |
|-------|-------|-------|------|
| 1. Foundation | Project setup, API client, stores, layouts | 16 | 1-2 |
| 2. Public Pages | Landing, login, register, NextAuth | 12 | 2-3 |
| 3. Dashboard Core | Dashboard page, article cards, stats | 16 | 3-4 |
| 4. Modals & Editing | Draft editor modal, inline editing, auto-save | 16 | 4-5 |
| 5. Settings | Settings page, accordions, all sections | 8 | 5 |
| 6. History & Polish | History page, loading/empty states, keyboard shortcuts | 16 | 5-6 |
| 7. Testing & Docs | Testing, accessibility, documentation | 8 | 7 |
| **Total** | | **92 hours** | **~12 days** |

---

## Next Steps After Sprint 4C

Once frontend is complete with Sprint 0-4B backend integration:

**Sprint 5A: Analytics**
- Backend: Analytics tracking, email events, dashboard
- Frontend: Analytics settings accordion + analytics page

**Sprint 5B: Trends Detection**
- Backend: Topic clustering, velocity detection, trend scoring
- Frontend: Trends settings accordion + trending section UI

**Sprint 5C: Writing Style Trainer**
- Backend: Style analysis, profile generation, style-aware generation
- Frontend: Style settings accordion + training UI

**Sprint 6: Feedback Loop**
- Backend: Feedback tracking, learning algorithm, preference extraction
- Frontend: Feedback settings accordion + rating UI

Each sprint adds:
1. Backend API endpoints
2. Frontend API client in `lib/api/`
3. Settings accordion section in Settings page
4. Optional dashboard widget

**Architecture supports this with zero refactoring.**

---

## Notes

### Why Modal for Draft Editor?
- Maintains context (no navigation loss)
- Faster perceived performance
- Modern pattern (Gmail, Linear, Notion)
- User doesn't lose place
- Easier to implement undo/redo (single state tree)

### Why Settings as ONE Page?
- All configuration in one place (mental model)
- Search works across all settings
- Frequency-based ordering prioritizes power users
- Progressive disclosure (collapse what's rarely used)
- Future sections visible (shows roadmap)

### Why Frequency-Based Ordering?
- 80% of value comes from 20% of features
- Power users (daily users) shouldn't scroll
- Sources modified 2-3x/week → first
- Email setup once → last
- Reduces friction for most common tasks

### Why Quick Actions on Dashboard?
- Most frequent task (add source) should be easiest
- Reduces clicks from 3 → 1
- User stays in flow
- Progressive enhancement (Settings for bulk, Dashboard for quick)

### Why Show Draft on Dashboard?
- Users want to SEE value immediately
- "Review & Send" button hides value behind click
- GitHub shows PR preview without clicking "View PR"
- Less cognitive load (see → decide → act)

### Why Undo/Redo is MVP?
- Users will accidentally delete content
- Cmd+Z is muscle memory
- Easy with React state management
- Builds trust (users feel safe editing)

### Why Send Confirmation?
- Email is destructive (can't undo sending to 1,000 people)
- Exception to "no confirmations" rule
- Prevents costly mistakes
- Industry standard (Mailchimp, Beehiiv all do this)

---

## FAQ

**Q: Why Next.js instead of Streamlit?**
A: Streamlit is for data apps (dashboards, ML demos). Next.js is for production web apps with auth, routing, SEO, performance. We need a polished user experience, not a prototype.

**Q: Why not build separate pages for each feature?**
A: Feature-based navigation is confusing. User-task-based is better. Users think "I need to review my draft" not "I need to go to Newsletter Generator tab".

**Q: Why Radix UI instead of Material UI?**
A: Radix is unstyled (full design control), accessible by default, and used by shadcn/ui (best component library for modern React apps).

**Q: Why TanStack Query instead of SWR?**
A: TanStack Query has better TypeScript support, more features (mutations, optimistic updates), and larger community.

**Q: Why Zustand instead of Redux?**
A: Zustand has zero boilerplate, works with React Server Components, and is perfect for UI state. Use TanStack Query for server state.

**Q: Can we add more pages later?**
A: Yes! Architecture is extensible. Adding a page is just creating `app/(product)/app/newpage/page.tsx`. But question first: Is this a new page or a modal? Most features should be modals.

**Q: How do we handle agency vs individual users?**
A: Same UI. Show/hide workspace switcher based on workspace count. Backend already has multi-tenant RLS. Zero code duplication.

**Q: When do future features (trends, style) get enabled?**
A: When backend is ready (Sprint 5+). Frontend already has:
- API client ready (`lib/api/trends.ts` etc)
- Settings accordion ready (collapsed/disabled)
- Just uncomment + connect to backend

---

## Status

**Current Phase:** Not Started
**Next Task:** Initialize Next.js 14 project
**Blockers:** None
**Dependencies:** Backend API must be running on http://localhost:8000

---

**Created:** 2025-01-16
**Sprint:** 4C
**Status:** 🚧 In Progress
**Target Completion:** 12 days (~92 hours)
**Expected Outcome:** Production-ready Next.js frontend with all Sprint 0-4B features accessible, extensible for Sprint 5+