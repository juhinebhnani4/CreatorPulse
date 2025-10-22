# Frontend Architecture - CreatorPulse

**Purpose**: Comprehensive guide to the frontend architecture, page structure, and design system.

**Last Updated**: 2025-01-20

**Related Docs**:
- [CLAUDE.md](../../CLAUDE.md) - Quick reference
- [SETTINGS_COMPONENTS.md](./SETTINGS_COMPONENTS.md) - Settings sections detail
- [TYPE_DEFINITIONS.md](../_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md) - TypeScript types

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Page Structure & Routing](#page-structure--routing)
4. [Settings Page Architecture](#settings-page-architecture)
5. [Component Architecture](#component-architecture)
6. [State Management](#state-management)
7. [Visual Design System](#visual-design-system)
8. [Key User Flows](#key-user-flows)
9. [API Integration Patterns](#api-integration-patterns)
10. [File Organization](#file-organization)

---

## Overview

CreatorPulse's frontend is a **modern, production-ready Next.js 14 application** using the App Router, TypeScript, and a component-based architecture. The design emphasizes:

- **User-friendly onboarding** - Guided setup with progress tracking
- **Unified settings hub** - Single page with sidebar navigation for all configurations
- **Flexible architecture** - Dual approach: Settings sections + dedicated pages for future growth
- **Modern UX** - Gradient-heavy design, smooth animations, responsive layouts

### Key Architectural Decisions

**Why Settings as Unified Hub?**
- **Problem**: 10+ configuration areas scattered across app made navigation complex
- **Solution**: Single Settings page with sidebar containing all 10 sections
- **Benefit**: Users can quickly access any config without leaving the page

**Why Duplicate Pages Exist?**
- **Strategy**: Some features appear in BOTH Settings (sidebar section) AND dedicated pages
- **Reason**: Future-proofing for power-user full-screen interfaces
- **Examples**: Subscribers, Schedule, Style, Trends, Analytics, Feedback
- **Current State**: Settings sections are fully functional; dedicated pages are placeholders

---

## Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.2.33 | React framework with App Router |
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 3.4.1 | Utility-first CSS |
| **Radix UI** | Latest | Accessible component primitives |
| **Zustand** | 5.0.8 | State management |
| **React Query** | 5.90.x | Server state & caching |
| **Axios** | 1.12.2 | HTTP client |
| **Lucide React** | 0.545 | Icon library |

### Key Libraries

**UI Components**: shadcn/ui pattern (Radix UI + Tailwind)
**Forms**: React Hook Form + Zod validation
**Dates**: date-fns for formatting
**Notifications**: react-hot-toast
**Utilities**: clsx for class merging

---

## Page Structure & Routing

### Route Hierarchy

```
/                          Landing page (public)
/login                     Login page (public)
/register                  Registration page (public)
/forgot-password           Password recovery (public)

/app                       Dashboard (protected) ⭐
/app/content               Content Library (protected)
/app/history               Newsletter History (protected)
/app/settings              Unified Settings Hub (protected) ⭐⭐⭐

/app/subscribers           Subscribers (protected, also in Settings)
/app/schedule              Scheduler (protected, also in Settings)
/app/style                 Style Training (protected, also in Settings)
/app/trends                Trends (protected, also in Settings)
/app/feedback              Feedback (protected, also in Settings)
/app/analytics             Analytics (protected, also in Settings)
```

### Route Protection

**Public Routes**: Landing, Login, Register
**Protected Routes**: All `/app/*` routes

**Auth Guard Implementation**:
```typescript
// In every protected page
const { isAuthenticated, _hasHydrated } = useAuthStore();

useEffect(() => {
  if (!isMounted || !_hasHydrated) return;

  if (!isAuthenticated) {
    router.push('/login');
    return;
  }

  // Load page data
}, [isAuthenticated, _hasHydrated]);
```

---

## Settings Page Architecture

### Overview

The Settings page (`/app/settings/page.tsx`) is a **unified configuration hub** with:
- **Left Sidebar**: Navigation with 10 sections
- **Main Content Area**: Dynamic component based on selected section
- **Setup Progress**: Top banner showing completion status
- **Mobile Dropdown**: Replaces sidebar on small screens

### Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│                      App Header                              │
│  Logo | Dashboard | Content | Settings | User Menu          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                Setup Progress Bar                            │
│  [✓] Sources  [✓] Schedule  [✓] Email  [ ] API Keys [  ] Style │
└─────────────────────────────────────────────────────────────┘
┌───────────────┬─────────────────────────────────────────────┐
│   Sidebar     │         Main Content Area                    │
│  (Desktop)    │                                              │
│               │  ┌────────────────────────────────────────┐ │
│ Essential     │  │  Section Header                        │ │
│ 📱 Sources    │  │  Icon + Title + Description            │ │
│ ⏰ Schedule   │  └────────────────────────────────────────┘ │
│ 👥 Subscribers│                                             │
│ 📧 Email      │  ┌────────────────────────────────────────┐ │
│ 🏢 Workspace  │  │                                         │ │
│               │  │                                         │ │
│ Advanced      │  │    <ActiveSectionComponent />          │ │
│ 🔑 API Keys   │  │                                         │ │
│ ✍️ Style      │  │    (e.g., SourcesSettings)             │ │
│ 🔥 Trends     │  │                                         │ │
│ 📊 Analytics  │  │                                         │ │
│ 💬 Feedback   │  │                                         │ │
│               │  └────────────────────────────────────────┘ │
└───────────────┴─────────────────────────────────────────────┘
```

### The 10 Settings Sections

#### Essential Settings (Top Group)

1. **📱 Content Sources** (`sources-settings.tsx`)
   - Configure Reddit, RSS, YouTube, Twitter/X, Blogs
   - Add/remove sources
   - Enable/disable individual sources
   - Test source connections
   - **Status**: Configured (shows active source count)

2. **⏰ Schedule Settings** (`schedule-settings.tsx`)
   - Set daily/weekly generation schedule (cron)
   - Configure send time
   - Enable/disable automation
   - View execution history
   - **Status**: Configured (shows schedule time)

3. **👥 Subscribers** (`subscribers-settings.tsx`)
   - View subscriber list
   - Add single subscriber
   - Import CSV bulk subscribers
   - Manage subscription status
   - Export subscriber list
   - **Status**: Configured (shows subscriber count)

4. **📧 Email Configuration** (`email-settings.tsx`)
   - Choose provider: SMTP or SendGrid
   - Configure SMTP settings (server, port, credentials)
   - Configure SendGrid API key
   - Set from name and reply-to
   - Test email delivery
   - **Status**: Configured/Not Set Up

5. **🏢 Workspace** (`workspace-settings.tsx`)
   - Edit workspace name and description
   - Manage team members (add/remove)
   - Set member roles (owner, editor, viewer)
   - Delete workspace
   - **Status**: Configured (shows workspace name)

#### Advanced Settings (Bottom Group)

6. **🔑 API Keys** (`api-keys-settings.tsx`)
   - OpenAI API key (for GPT-4)
   - OpenRouter API key (for Claude)
   - YouTube API key
   - Twitter/X API credentials
   - **Status**: Incomplete/Configured

7. **✍️ Writing Style** (`style-settings.tsx`)
   - Train AI on sample newsletters
   - Set default tone (professional, casual, technical, friendly)
   - Configure readability level
   - View learned style characteristics
   - **Status**: Pending/Using Defaults

8. **🔥 Trends Detection** (`trends-settings.tsx`)
   - Enable/disable trend detection
   - Set detection sensitivity
   - Configure trend scoring weights
   - View detected trends
   - **Status**: Active/Inactive

9. **📊 Analytics** (`analytics-settings.tsx`)
   - Enable/disable tracking
   - Configure tracking pixels
   - Set analytics retention period
   - Export settings
   - **Status**: Tracking Enabled/Disabled

10. **💬 Feedback Loop** (`feedback-settings.tsx`)
    - Enable/disable feedback collection
    - Configure feedback prompts
    - Set feedback impact on curation
    - View feedback summary
    - **Status**: Active/Inactive

### Implementation Details

**File**: `frontend-nextjs/src/app/app/settings/page.tsx`

**State Management**:
```typescript
const [activeSection, setActiveSection] = useState('sources');

const sections = [
  {
    id: 'sources',
    title: '📱 Content Sources',
    component: <SourcesSettings />,
    status: 'configured',
    statusText: '2 sources active',
    description: 'Configure Reddit, RSS feeds, Twitter, and more',
  },
  // ... 9 more sections
];
```

**Sidebar Navigation**:
- Component: `SettingsSidebar`
- Props: `sections`, `activeSection`, `onSectionChange`
- Mobile: Replaced with dropdown selector

**Dynamic Content**:
```typescript
const activeContent = sections.find(s => s.id === activeSection);

<div className="content-area">
  {activeContent?.component}
</div>
```

---

## Component Architecture

### Component Categories

#### 1. Page Components
- **Location**: `src/app/**/page.tsx`
- **Purpose**: Top-level route components
- **Pattern**: Client component with data fetching

#### 2. Dashboard Components
- **Location**: `src/components/dashboard/`
- **Examples**: `enhanced-draft-card.tsx`, `article-card.tsx`, `stats-overview.tsx`
- **Purpose**: Dashboard-specific UI elements

#### 3. Settings Components
- **Location**: `src/components/settings/`
- **Examples**: All 10 section components + `settings-sidebar.tsx`, `setup-progress.tsx`
- **Purpose**: Settings page sections

#### 4. Modal Components
- **Location**: `src/components/modals/`
- **Examples**: `draft-editor-modal.tsx`, `send-confirmation-modal.tsx`, `add-source-modal.tsx`
- **Purpose**: Overlay dialogs for actions

#### 5. Layout Components
- **Location**: `src/components/layout/`
- **Examples**: `app-header.tsx`
- **Purpose**: Shared layout elements

#### 6. UI Primitives
- **Location**: `src/components/ui/`
- **Examples**: `button.tsx`, `input.tsx`, `card.tsx`, `dialog.tsx`
- **Purpose**: Reusable Radix UI-based components

### Component Patterns

**Data Fetching Pattern**:
```typescript
'use client';

export default function Page() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      const result = await api.getData();
      setData(result);
      setIsLoading(false);
    }
    fetchData();
  }, []);

  if (isLoading) return <Skeleton />;
  return <Content data={data} />;
}
```

**Modal Pattern**:
```typescript
const [showModal, setShowModal] = useState(false);

<Modal open={showModal} onClose={() => setShowModal(false)}>
  <ModalContent />
</Modal>
```

---

## State Management

### Zustand Stores

#### 1. Auth Store
**File**: `src/lib/store/auth-store.ts`

**State**:
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  _hasHydrated: boolean;  // SSR hydration flag

  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
}
```

**Persistence**: Synced to `localStorage` (key: `auth-storage`)

**Usage**:
```typescript
const { user, isAuthenticated, setAuth, clearAuth } = useAuthStore();
```

#### 2. Workspace Store
**File**: `src/lib/store/workspace-store.ts`

**State**:
```typescript
interface WorkspaceState {
  currentWorkspace: Workspace | null;
  setCurrentWorkspace: (workspace: Workspace) => void;
  clearWorkspace: () => void;
}
```

**Persistence**: Synced to `localStorage` (key: `workspace-storage`)

### React Query (TanStack Query)

**Configuration**: Axios + React Query for server state

**Pattern**:
```typescript
// API client wraps axios calls
export const contentApi = {
  list: (workspaceId: string) =>
    apiClient.get(`/content/workspaces/${workspaceId}`),
};

// In component
const { data, isLoading } = useQuery({
  queryKey: ['content', workspaceId],
  queryFn: () => contentApi.list(workspaceId),
});
```

---

## Visual Design System

### Color Palette

**Primary Colors**:
- `primary`: Blue (used for main CTAs, links)
- `primary-foreground`: White text on primary

**Gradients**:
- `gradient-hero`: Blue gradient (used for primary buttons, cards)
- `gradient-warm`: Orange/pink gradient (used for highlights)

**Status Colors**:
- `success`: Green (completed states, positive actions)
- `destructive`: Red (errors, delete actions)
- `secondary`: Purple/gray (secondary actions)
- `muted`: Gray (backgrounds, disabled states)

**Source-Specific Colors** (badges):
- Reddit: Red (`destructive`)
- RSS: Orange (`secondary`)
- Twitter/X: Blue (`default`)
- YouTube: Green (`outline`)
- Blog: Purple (`secondary`)

### Typography

**Headings**:
- `text-5xl font-bold` - Page titles (Dashboard welcome)
- `text-4xl font-bold` - Section titles (Content Library)
- `text-3xl font-bold` - Card titles
- `text-2xl font-bold` - Subsection titles
- `text-xl font-semibold` - Card subtitles

**Body**:
- `text-base` - Default body text
- `text-sm` - Secondary text, descriptions
- `text-xs` - Labels, metadata

**Colors**:
- `text-foreground` - Primary text
- `text-muted-foreground` - Secondary text
- `bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent` - Gradient text

### Spacing & Layout

**Container**: `container mx-auto px-4` (max-width responsive)
**Padding**: `p-4`, `p-6`, `p-8` for cards
**Gaps**: `gap-4`, `gap-6`, `gap-8` for flex/grid
**Margins**: `mb-4`, `mb-6`, `mb-8` between sections

### Animations

**Built-in Classes**:
- `animate-slide-up` - Cards slide in from bottom
- `animate-pulse-soft` - Gentle pulse for loading states
- `animate-celebration` - Toast celebrations
- `animate-bounce` - Pointing arrows

**Staggered Delays**:
```typescript
<Card
  className="animate-slide-up"
  style={{ animationDelay: `${index * 50}ms` }}
/>
```

**Transitions**:
- `transition-all` - Smooth transitions
- `hover:shadow-lg` - Elevation on hover
- `hover:-translate-y-1` - Lift effect

### Responsive Breakpoints

**Tailwind Defaults**:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

**Common Patterns**:
- Mobile: Single column, stacked
- Tablet (`md:`): 2-column grids
- Desktop (`lg:`): 3-column grids, sidebar layouts

---

## Key User Flows

### 1. First-Time User Onboarding

**Path**: Register → Dashboard → Settings → Generate

**Steps**:
1. User registers at `/register`
2. Redirected to `/app` (Dashboard)
3. Sees empty state with trending article preview
4. **Welcome Section** shows progress: "0/3 steps completed"
5. **Motivational Tip** encourages adding sources
6. Scrolls to **Unified Source Setup** card
7. Adds sources (Reddit, Twitter, RSS) in multi-input
8. Clicks "Add Sources & Generate"
9. System auto-triggers scrape → generate → shows draft
10. Draft card changes to "Ready" state
11. User clicks "Preview Draft" → sees full newsletter

**Key Components**:
- `WelcomeSection` - Greeting + progress
- `MotivationalTip` - Encouragement
- `UnifiedSourceSetup` - Quick source input
- `EnhancedDraftCard` - Status display

### 2. Returning User - Quick Send

**Path**: Login → Dashboard → Preview → Send

**Steps**:
1. User logs in at `/login`
2. Redirected to `/app` (Dashboard)
3. Sees "Ready" draft card (green badge)
4. Clicks "Preview Draft"
5. **DraftEditorModal** opens with subject + articles
6. Reviews content, clicks "Send Now"
7. **SendConfirmationModal** opens with subscriber count
8. Confirms send
9. Toast: "Newsletter Sent to 1,234 subscribers"
10. Draft card changes to "Scheduled" state

### 3. Settings Configuration

**Path**: Dashboard → Settings → Configure Sources → Test

**Steps**:
1. User clicks Settings in header
2. Lands on `/app/settings` (default section: Sources)
3. Sidebar shows 10 sections with status badges
4. Clicks "📱 Content Sources"
5. Sees list of configured sources
6. Clicks "Add Source" button
7. **AddSourceModal** opens
8. Selects "Reddit", enters subreddit name
9. Saves, sees new source card appear
10. Clicks "Scrape Now" to test
11. Toast: "Successfully scraped 25 items"

---

## API Integration Patterns

### Axios Instance

**File**: `src/lib/utils/axios-instance.ts`

**Setup**:
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add auth token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### API Client Modules

**Location**: `src/lib/api/`

**Pattern**:
```typescript
// src/lib/api/content.ts
import apiClient from '@/lib/utils/axios-instance';

export const contentApi = {
  list: async (workspaceId: string, params?: any) => {
    const response = await apiClient.get(
      `/api/v1/content/workspaces/${workspaceId}`,
      { params }
    );
    return response.data.data; // Unwrap APIResponse<T>
  },

  scrape: async (data: { workspace_id: string }) => {
    const response = await apiClient.post('/api/v1/content/scrape', data);
    return response.data.data;
  },
};
```

**Usage**:
```typescript
import { contentApi } from '@/lib/api/content';

const items = await contentApi.list(workspaceId);
```

### Error Handling

**Pattern**:
```typescript
try {
  const result = await api.someAction();
  toast({ title: 'Success', description: 'Action completed' });
} catch (error: any) {
  toast({
    title: 'Error',
    description: error.message || 'Action failed',
    variant: 'destructive',
  });
}
```

### Loading States

**Pattern**:
```typescript
const [isLoading, setIsLoading] = useState(false);

const handleAction = async () => {
  setIsLoading(true);
  try {
    await api.action();
  } finally {
    setIsLoading(false);
  }
};

<Button disabled={isLoading}>
  {isLoading ? <Loader2 className="animate-spin" /> : 'Action'}
</Button>
```

---

## File Organization

### Adding New Pages

**Location**: `src/app/app/[page-name]/page.tsx`

**Template**:
```typescript
'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/stores/auth-store';
import { AppHeader } from '@/components/layout/app-header';

export default function NewPage() {
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Auth guard
  useEffect(() => {
    if (!isMounted || !_hasHydrated) return;
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isMounted, _hasHydrated]);

  if (!isMounted || !_hasHydrated) return null;

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Content */}
      </main>
    </div>
  );
}
```

### Adding New Components

**Dashboard Component**: `src/components/dashboard/[name].tsx`
**Settings Component**: `src/components/settings/[name]-settings.tsx`
**Modal**: `src/components/modals/[name]-modal.tsx`
**UI Primitive**: `src/components/ui/[name].tsx`

### Naming Conventions

**Files**: kebab-case (e.g., `enhanced-draft-card.tsx`)
**Components**: PascalCase (e.g., `EnhancedDraftCard`)
**Functions**: camelCase (e.g., `handleSendNow`)
**Constants**: SCREAMING_SNAKE_CASE (e.g., `MAX_ITEMS`)

### Import Order

```typescript
// 1. External libraries
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// 2. Internal libraries/stores
import { useAuthStore } from '@/lib/stores/auth-store';
import { contentApi } from '@/lib/api/content';

// 3. Components
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// 4. Types
import { ContentItem } from '@/types/content';

// 5. Utilities
import { cn } from '@/lib/utils';
```

---

## Best Practices

### Performance

1. ✅ Use `'use client'` only when needed (state, effects, browser APIs)
2. ✅ Lazy load modals and heavy components
3. ✅ Use React Query for caching and deduplication
4. ✅ Implement skeleton loading states
5. ✅ Optimize images with Next.js `<Image>` component

### Accessibility

1. ✅ Use Radix UI primitives (keyboard navigation, ARIA labels)
2. ✅ Provide `aria-label` for icon-only buttons
3. ✅ Use semantic HTML (`<main>`, `<nav>`, `<article>`)
4. ✅ Ensure sufficient color contrast
5. ✅ Test with keyboard-only navigation

### TypeScript

1. ✅ Define interfaces for all props
2. ✅ Use strict mode
3. ✅ Avoid `any` type (use `unknown` or generics)
4. ✅ Import types from `@/types/`
5. ✅ Use discriminated unions for state

### State Management

1. ✅ Use Zustand for global state (auth, workspace)
2. ✅ Use React Query for server state (API data)
3. ✅ Use `useState` for local component state
4. ✅ Persist critical state to localStorage
5. ✅ Handle SSR hydration with `_hasHydrated` flag

---

## Summary

The CreatorPulse frontend is a **well-architected, modern Next.js application** that balances:
- ✅ **User experience** - Intuitive navigation, guided onboarding
- ✅ **Developer experience** - Clear structure, reusable components
- ✅ **Flexibility** - Settings hub + dedicated pages for future growth
- ✅ **Performance** - React Query caching, optimized images
- ✅ **Maintainability** - TypeScript, consistent patterns, documented

**Key Takeaway**: The Settings page architecture (unified hub with sidebar) is the centerpiece of the configuration experience, providing quick access to all 10 configuration areas while maintaining future flexibility with dedicated pages.

---

**For detailed Settings component reference, see**: [SETTINGS_COMPONENTS.md](./SETTINGS_COMPONENTS.md)

**END OF FRONTEND_ARCHITECTURE.md**