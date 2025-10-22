# Settings Components Reference

**Purpose**: Detailed reference for all 10 Settings page sections and their components.

**Last Updated**: 2025-01-20

**Related Docs**:
- [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) - Overall frontend architecture
- [CLAUDE.md](../../CLAUDE.md) - Quick reference

---

## Overview

The Settings page (`/app/settings`) contains **10 configurable sections**, each implemented as a React component. This document provides detailed information about each section: its purpose, props, API endpoints, and related backend services.

### Settings Section List

**Essential** (User-facing, critical for functionality):
1. [Content Sources](#1-content-sources) - `sources-settings.tsx`
2. [Schedule Settings](#2-schedule-settings) - `schedule-settings.tsx`
3. [Subscribers](#3-subscribers) - `subscribers-settings.tsx`
4. [Email Configuration](#4-email-configuration) - `email-settings.tsx`
5. [Workspace](#5-workspace) - `workspace-settings.tsx`

**Advanced** (Power users, optional enhancements):
6. [API Keys](#6-api-keys) - `api-keys-settings.tsx`
7. [Writing Style](#7-writing-style) - `style-settings.tsx`
8. [Trends Detection](#8-trends-detection) - `trends-settings.tsx`
9. [Analytics](#9-analytics) - `analytics-settings.tsx`
10. [Feedback Loop](#10-feedback-loop) - `feedback-settings.tsx`

---

## 1. Content Sources

**File**: `frontend-nextjs/src/components/settings/sources-settings.tsx`

**Icon**: 📱

**Description**: Configure content aggregation sources (Reddit, RSS, YouTube, Twitter/X, Blogs).

### Purpose

Allow users to:
- Add new content sources
- Configure source-specific settings (subreddits, RSS URLs, Twitter handles, etc.)
- Enable/disable sources
- Test source connections
- View items scraped per source

### Component Structure

**Renders**:
- List of configured sources (source cards)
- "Add Source" button
- Test scraping button per source
- Enable/disable toggles

### API Endpoints Used

- `GET /api/v1/workspaces/{id}/config` - Fetch current source configuration
- `POST /api/v1/workspaces/{id}/config` - Update source configuration
- `POST /api/v1/content/scrape` - Test scrape from specific source
- `GET /api/v1/content/workspaces/{id}/stats` - View items per source

### Related Backend Services

- `WorkspaceService.get_config()` - Retrieve workspace configuration
- `WorkspaceService.update_config()` - Save updated configuration
- `ContentService.scrape_content()` - Scrape from sources

### Configuration Structure

```typescript
interface SourceConfig {
  type: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog';
  enabled: boolean;
  config: {
    // Reddit
    subreddits?: string[];  // e.g., ["MachineLearning", "artificial"]
    sort?: 'hot' | 'new' | 'top';
    limit?: number;

    // RSS
    feeds?: Array<{ url: string; name: string }>;

    // YouTube
    channels?: string[];  // Channel IDs
    query?: string;  // Search query

    // Twitter/X
    usernames?: string[];  // Without @ prefix

    // Blog
    urls?: string[];
    selectors?: {
      article: string;
      title: string;
      content: string;
    };
  };
}
```

### User Actions

1. **Add Source**: Opens `AddSourceModal` or inline form
2. **Edit Source**: Modify source-specific config (subreddits, feeds, etc.)
3. **Delete Source**: Remove source from configuration
4. **Test Scrape**: Trigger manual scrape to verify source works
5. **Toggle Enable**: Enable/disable source without deleting

### Status Indicators

- **Configured**: Shows count of active sources (e.g., "2 sources active")
- **Badge Colors**: Green (enabled), Gray (disabled), Red (error)

---

## 2. Schedule Settings

**File**: `frontend-nextjs/src/components/settings/schedule-settings.tsx`

**Icon**: ⏰

**Description**: Configure automated newsletter generation and delivery schedule.

### Purpose

Allow users to:
- Set daily/weekly schedule for newsletter generation
- Configure send time (timezone-aware)
- Enable/disable automation
- View execution history
- Pause/resume scheduled jobs

### Component Structure

**Renders**:
- Current schedule display (e.g., "Daily at 8:00 AM EST")
- Schedule picker (day selector + time picker)
- Enable/disable toggle
- Execution history table (last 10 runs)
- "Run Now" button for manual trigger

### API Endpoints Used

- `GET /api/v1/scheduler/workspaces/{id}/jobs` - Fetch workspace jobs
- `POST /api/v1/scheduler/jobs` - Create new scheduled job
- `PUT /api/v1/scheduler/jobs/{id}` - Update existing job
- `POST /api/v1/scheduler/jobs/{id}/pause` - Pause job
- `POST /api/v1/scheduler/jobs/{id}/resume` - Resume job
- `GET /api/v1/scheduler/jobs/{id}/history` - View execution logs

### Related Backend Services

- `SchedulerService.create_job()` - Create scheduled job
- `SchedulerService.update_job()` - Modify schedule
- `SchedulerService.pause_job()` / `resume_job()` - Control execution
- `SchedulerService.get_execution_history()` - View past runs

### Schedule Format

**Cron Expression Examples**:
- `0 9 * * *` - Every day at 9:00 AM
- `0 9 * * 1` - Every Monday at 9:00 AM
- `0 9 * * 1-5` - Every weekday at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 1 * *` - First day of month at midnight

### User Actions

1. **Set Schedule**: Choose days and time
2. **Enable/Disable**: Toggle automation without deleting schedule
3. **Pause**: Temporarily pause without changing schedule
4. **Run Now**: Manually trigger generation/send
5. **View History**: See past execution results

### Status Indicators

- **Configured**: Shows schedule (e.g., "Daily at 8:00 AM")
- **Badge**: Green (active), Yellow (paused), Gray (disabled)

---

## 3. Subscribers

**File**: `frontend-nextjs/src/components/settings/subscribers-settings.tsx`

**Icon**: 👥

**Description**: Manage email subscriber list.

### Purpose

Allow users to:
- View all subscribers with status
- Add single subscriber
- Import bulk subscribers from CSV
- Remove subscribers
- Export subscriber list
- View subscription/unsubscription dates

### Component Structure

**Renders**:
- Subscriber table (email, status, subscribed date)
- Search/filter input
- "Add Subscriber" button
- "Import CSV" button
- "Export" button
- Pagination controls

### API Endpoints Used

- `GET /api/v1/delivery/workspaces/{id}/subscribers` - List all subscribers
- `POST /api/v1/delivery/workspaces/{id}/subscribers` - Add single subscriber
- `DELETE /api/v1/delivery/workspaces/{id}/subscribers/{email}` - Remove subscriber
- (Future) `POST /api/v1/delivery/workspaces/{id}/subscribers/import` - Bulk import

### Related Backend Services

- `DeliveryService.list_subscribers()` - Retrieve subscriber list
- `DeliveryService.add_subscriber()` - Add new subscriber
- `DeliveryService.remove_subscriber()` - Remove subscriber

### Subscriber Model

```typescript
interface Subscriber {
  id: string;
  workspace_id: string;
  email: string;
  status: 'subscribed' | 'unsubscribed' | 'bounced';
  subscribed_at: string;  // ISO 8601
  unsubscribed_at: string | null;
}
```

### User Actions

1. **Add Subscriber**: Opens `AddSubscriberModal`, enter email
2. **Import CSV**: Opens `ImportCSVModal`, upload file with email column
3. **Remove Subscriber**: Click delete icon, confirm removal
4. **Export**: Download CSV of all subscribers
5. **Search**: Filter subscribers by email

### CSV Import Format

```csv
email,name
john@example.com,John Doe
jane@example.com,Jane Smith
```

**Requirements**:
- Must have `email` column
- Optional: `name` column
- Ignores duplicates (checks existing subscribers)

### Status Indicators

- **Configured**: Shows subscriber count (e.g., "1,234 subscribers")
- **Status Badges**: Green (subscribed), Red (unsubscribed), Yellow (bounced)

---

## 4. Email Configuration

**File**: `frontend-nextjs/src/components/settings/email-settings.tsx`

**Icon**: 📧

**Description**: Configure email delivery provider (SMTP or SendGrid).

### Purpose

Allow users to:
- Choose email provider: SMTP or SendGrid
- Configure SMTP settings (server, port, credentials)
- Configure SendGrid API key
- Set "From" name and reply-to email
- Test email delivery

### Component Structure

**Renders**:
- Provider selector (radio: SMTP | SendGrid)
- **SMTP Form** (if selected):
  - Server input
  - Port input (default: 587)
  - Username input
  - Password input (hidden)
  - Use TLS toggle
- **SendGrid Form** (if selected):
  - API Key input (hidden)
- From Name input
- Reply-To email input (optional)
- "Send Test Email" button

### API Endpoints Used

- `GET /api/v1/workspaces/{id}/config` - Fetch delivery config
- `POST /api/v1/workspaces/{id}/config` - Update delivery config
- `POST /api/v1/delivery/send-test` - Send test email

### Related Backend Services

- `WorkspaceService.get_config()` / `update_config()` - Manage config
- `DeliveryService.send_test_email()` - Send test

### Configuration Structure

```typescript
interface DeliveryConfig {
  method: 'smtp' | 'sendgrid';
  from_name: string;  // Display name in "From" field
  reply_to?: string;  // Optional reply-to address

  // SMTP-specific (stored in backend .env, NOT in config)
  smtp_server?: string;
  smtp_port?: number;
  smtp_username?: string;
  smtp_password?: string;  // Never returned to frontend

  // SendGrid-specific (stored in backend .env)
  sendgrid_api_key?: string;  // Never returned to frontend
}
```

**Security Note**: API keys and passwords are stored in backend `.env`, NOT in workspace config. Frontend only updates method selection and from_name.

### User Actions

1. **Select Provider**: Choose SMTP or SendGrid
2. **Configure SMTP**: Enter server details (requires backend .env update)
3. **Configure SendGrid**: Enter API key (requires backend .env update)
4. **Set From Name**: Display name for outgoing emails
5. **Test Email**: Send test to verify configuration

### Status Indicators

- **Configured**: Shows "SMTP Configured" or "SendGrid Configured"
- **Not Set Up**: Shows "Email provider not configured"

---

## 5. Workspace

**File**: `frontend-nextjs/src/components/settings/workspace-settings.tsx`

**Icon**: 🏢

**Description**: Manage workspace settings and team members.

### Purpose

Allow users to:
- Edit workspace name and description
- View workspace owner
- Manage team members (add/remove)
- Set member roles (owner, editor, viewer)
- Delete workspace (with confirmation)

### Component Structure

**Renders**:
- Workspace name input
- Description textarea
- Owner display (read-only)
- Team members table (email, role, actions)
- "Invite Member" button
- "Delete Workspace" button (danger zone)

### API Endpoints Used

- `GET /api/v1/workspaces/{id}` - Fetch workspace details
- `PUT /api/v1/workspaces/{id}` - Update workspace
- `GET /api/v1/workspaces/{id}/members` - List team members
- `POST /api/v1/workspaces/{id}/members` - Invite member
- `DELETE /api/v1/workspaces/{id}/members/{user_id}` - Remove member
- `DELETE /api/v1/workspaces/{id}` - Delete workspace

### Related Backend Services

- `WorkspaceService.update_workspace()` - Modify name/description
- `WorkspaceService.add_user_to_workspace()` - Add team member
- `WorkspaceService.remove_user_from_workspace()` - Remove member
- `WorkspaceService.delete_workspace()` - Delete workspace

### Workspace Model

```typescript
interface Workspace {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;  // User who created workspace
  created_at: string;
  updated_at: string;
}

interface WorkspaceMember {
  id: string;
  user_id: string;
  email: string;
  role: 'owner' | 'editor' | 'viewer';
  joined_at: string;
}
```

### Role Permissions

- **Owner**: Full access (edit workspace, manage team, delete workspace)
- **Editor**: Read and write (create/edit content and newsletters)
- **Viewer**: Read-only access

### User Actions

1. **Edit Name/Description**: Update workspace metadata
2. **Invite Member**: Enter email, select role, send invitation
3. **Change Role**: Update member's role (owner only)
4. **Remove Member**: Delete member from workspace (owner only)
5. **Delete Workspace**: Permanent deletion (owner only, with confirmation)

### Status Indicators

- **Configured**: Shows workspace name (e.g., "My Workspace")
- **Member Count**: Shows team size (e.g., "3 members")

---

## 6. API Keys

**File**: `frontend-nextjs/src/components/settings/api-keys-settings.tsx`

**Icon**: 🔑

**Description**: Configure API keys for external integrations.

### Purpose

Allow users to:
- Set OpenAI API key (for GPT-4 newsletter generation)
- Set OpenRouter API key (for Claude and alternatives)
- Set YouTube API key (for YouTube scraping)
- Set Twitter/X API credentials (for Twitter scraping)
- Test API key validity

### Component Structure

**Renders**:
- **OpenAI API Key**:
  - Input (password field)
  - "Test Connection" button
  - Status indicator
- **OpenRouter API Key**:
  - Input (password field)
  - "Test Connection" button
  - Status indicator
- **YouTube API Key**:
  - Input (password field)
  - Status indicator
- **Twitter/X Credentials**:
  - API Key input
  - API Secret input
  - Bearer Token input
  - Status indicator

### API Endpoints Used

- `GET /api/v1/workspaces/{id}/config` - Fetch API key status (NOT keys themselves)
- `POST /api/v1/workspaces/{id}/config` - Update API keys
- (Future) `POST /api/v1/integrations/test` - Test API key validity

### Related Backend Services

**Security Note**: API keys are stored in backend `.env` file, NOT in database. Frontend only indicates whether keys are set or not.

- Backend checks for environment variables:
  - `OPENAI_API_KEY`
  - `OPENROUTER_API_KEY`
  - `YOUTUBE_API_KEY`
  - `X_API_KEY`, `X_API_SECRET`, `X_BEARER_TOKEN`

### Configuration (Frontend Only Shows Status)

```typescript
interface APIKeysStatus {
  openai_configured: boolean;
  openrouter_configured: boolean;
  youtube_configured: boolean;
  twitter_configured: boolean;
}
```

**Important**: Frontend never receives actual API keys. Backend only returns whether keys are present.

### User Actions

1. **Set OpenAI Key**: Enter key, backend stores in `.env`
2. **Set OpenRouter Key**: Enter key, backend stores in `.env`
3. **Set YouTube Key**: Enter key, backend stores in `.env`
4. **Set Twitter Credentials**: Enter credentials, backend stores in `.env`
5. **Test Connection**: Verify key works by making test API call

### Status Indicators

- **Incomplete**: "API keys not configured"
- **Configured**: "OpenAI: ✓, OpenRouter: ✓, YouTube: ✗, Twitter: ✗"

---

## 7. Writing Style

**File**: `frontend-nextjs/src/components/settings/style-settings.tsx`

**Icon**: ✍️

**Description**: Train AI on writing style and customize newsletter tone.

### Purpose

Allow users to:
- Upload sample newsletters to train AI on style
- Set default tone (professional, casual, technical, friendly)
- View learned style characteristics
- Reset to defaults

### Component Structure

**Renders**:
- Tone selector (radio: Professional | Casual | Technical | Friendly)
- "Upload Sample Newsletter" button
- Learned characteristics display:
  - Average sentence length
  - Readability score (Flesch-Kincaid)
  - Vocabulary complexity
  - Common phrases
- "Reset to Defaults" button

### API Endpoints Used

- `POST /api/v1/style/train` - Train on newsletter sample
- `GET /api/v1/style/workspaces/{id}` - Get style profile
- `PUT /api/v1/style/workspaces/{id}` - Update style preferences

### Related Backend Services

- `StyleService.analyze_style()` - Extract style from sample
- `StyleService.train_on_newsletters()` - Build style profile
- `StyleService.get_style_profile()` - Retrieve learned style

### Style Profile Model

```typescript
interface StyleProfile {
  id: string;
  workspace_id: string;
  tone: 'professional' | 'casual' | 'technical' | 'friendly';
  sentence_length_avg: number;  // Words per sentence
  readability_score: number;  // Flesch-Kincaid grade level
  vocabulary_complexity: number;  // 0.0-1.0
  metadata: {
    common_phrases: string[];
    vocabulary_preferences: Record<string, number>;
  };
  trained_at: string;
}
```

### User Actions

1. **Select Tone**: Choose default tone for newsletters
2. **Upload Sample**: Provide example newsletter for AI to learn from
3. **View Characteristics**: See what AI learned about writing style
4. **Reset Defaults**: Clear learned style, use default tone only

### Status Indicators

- **Pending**: "Using defaults (not trained)"
- **Configured**: "Trained on 3 newsletters"

---

## 8. Trends Detection

**File**: `frontend-nextjs/src/components/settings/trends-settings.tsx`

**Icon**: 🔥

**Description**: Configure trend detection algorithm.

### Purpose

Allow users to:
- Enable/disable trend detection
- Set detection sensitivity (how easily topics are identified as trending)
- Configure trend scoring weights (mention frequency, velocity, source diversity)
- View detected trends

### Component Structure

**Renders**:
- Enable/disable toggle
- Sensitivity slider (Low | Medium | High)
- Scoring weights sliders:
  - Mention frequency weight (0-100%)
  - Velocity weight (0-100%)
  - Source diversity weight (0-100%)
- Recent trends list (preview)

### API Endpoints Used

- `GET /api/v1/trends/workspaces/{id}` - List detected trends
- `POST /api/v1/trends/detect` - Manually trigger detection
- `GET /api/v1/workspaces/{id}/config` - Fetch trend config
- `POST /api/v1/workspaces/{id}/config` - Update trend config

### Related Backend Services

- `TrendService.detect_trends()` - Run trend detection algorithm
- `TrendService.get_trending_topics()` - Retrieve trends

### Trend Detection Algorithm

**Scoring Formula**:
```
Trend Score = (Mention Frequency × 0.3) + (Velocity × 0.4) + (Source Diversity × 0.3)
```

**Configurable Weights**: Users can adjust the 30/40/30 split

**Sensitivity Levels**:
- Low: Threshold 0.8 (only very clear trends)
- Medium: Threshold 0.6 (default)
- High: Threshold 0.4 (detect more trends)

### User Actions

1. **Enable/Disable**: Turn trend detection on/off
2. **Adjust Sensitivity**: Set how easily trends are detected
3. **Adjust Weights**: Prioritize mention frequency vs velocity vs diversity
4. **View Trends**: See currently detected trends

### Status Indicators

- **Active**: "Trend detection enabled"
- **Inactive**: "Trend detection disabled"

---

## 9. Analytics

**File**: `frontend-nextjs/src/components/settings/analytics-settings.tsx`

**Icon**: 📊

**Description**: Configure email analytics and tracking.

### Purpose

Allow users to:
- Enable/disable tracking pixels
- Enable/disable click tracking
- Set analytics data retention period
- Configure tracking domains (for click redirect)
- Export analytics data

### Component Structure

**Renders**:
- "Enable Tracking" toggle
- "Track Opens" checkbox (tracking pixel)
- "Track Clicks" checkbox (link redirects)
- Retention period dropdown (30, 60, 90 days, Forever)
- Tracking domain input (optional custom domain)
- "Export Analytics Data" button

### API Endpoints Used

- `GET /api/v1/workspaces/{id}/config` - Fetch analytics config
- `POST /api/v1/workspaces/{id}/config` - Update analytics config
- `GET /api/v1/analytics/workspaces/{id}/export` - Export data

### Related Backend Services

- `AnalyticsService.record_event()` - Log tracking events
- `AnalyticsService.calculate_metrics()` - Compute open/click rates

### Analytics Configuration

```typescript
interface AnalyticsConfig {
  tracking_enabled: boolean;
  track_opens: boolean;  // Tracking pixel
  track_clicks: boolean;  // Link redirects
  retention_days: number;  // 30, 60, 90, or 0 (forever)
  tracking_domain?: string;  // Custom domain for click tracking
}
```

### User Actions

1. **Enable/Disable Tracking**: Turn all tracking on/off
2. **Configure Opens**: Include tracking pixel in emails
3. **Configure Clicks**: Wrap links with tracking redirects
4. **Set Retention**: How long to keep analytics data
5. **Export Data**: Download CSV of all analytics events

### Status Indicators

- **Tracking Enabled**: "Analytics active"
- **Tracking Disabled**: "Analytics disabled"

---

## 10. Feedback Loop

**File**: `frontend-nextjs/src/components/settings/feedback-settings.tsx`

**Icon**: 💬

**Description**: Configure feedback collection and impact on curation.

### Purpose

Allow users to:
- Enable/disable feedback collection
- Configure feedback prompts (ask subscribers to rate)
- Set feedback impact on content curation (boost/penalty percentages)
- View feedback summary

### Component Structure

**Renders**:
- Enable/disable toggle
- Feedback prompt settings:
  - Include rating prompt in emails (checkbox)
  - Prompt text input
- Impact settings:
  - "Liked" content boost (slider, 0-50%)
  - "Disliked" content penalty (slider, 0-50%)
- Feedback summary:
  - Positive count
  - Negative count
  - Top preferred sources

### API Endpoints Used

- `GET /api/v1/feedback/workspaces/{id}` - Fetch feedback summary
- `GET /api/v1/workspaces/{id}/config` - Fetch feedback config
- `POST /api/v1/workspaces/{id}/config` - Update feedback config

### Related Backend Services

- `FeedbackService.record_feedback()` - Store user feedback
- `FeedbackService.apply_feedback_to_ranking()` - Adjust content scores
- `NewsletterService.generate_newsletter()` - Uses feedback-adjusted scores

### Feedback Impact

**Default Settings**:
- Liked content: +20% score boost
- Disliked content: -30% score penalty

**How It Works**:
1. User rates content item (thumbs up/down)
2. Feedback stored in `feedback` table
3. Next newsletter generation:
   - Fetch feedback for workspace
   - Adjust content scores based on feedback
   - Preferred sources get boosted
   - Disliked sources get penalized

### User Actions

1. **Enable/Disable**: Turn feedback collection on/off
2. **Configure Prompts**: Customize feedback request text
3. **Adjust Impact**: Set boost/penalty percentages
4. **View Summary**: See aggregated feedback stats

### Status Indicators

- **Active**: "Feedback collection enabled"
- **Inactive**: "Feedback collection disabled"

---

## Supporting Components

### Settings Sidebar

**File**: `frontend-nextjs/src/components/settings/settings-sidebar.tsx`

**Purpose**: Navigation sidebar for Settings page

**Props**:
```typescript
interface SettingsSidebarProps {
  sections: Section[];
  activeSection: string;
  onSectionChange: (sectionId: string) => void;
}
```

**Renders**:
- List of sections with icons and titles
- Status badges per section
- Active state highlighting
- Grouped by Essential/Advanced

### Setup Progress

**File**: `frontend-nextjs/src/components/settings/setup-progress.tsx`

**Purpose**: Progress bar showing setup completion

**Props**:
```typescript
interface SetupProgressProps {
  steps: Array<{
    id: string;
    label: string;
    completed: boolean;
  }>;
}
```

**Renders**:
- Progress bar (filled based on completed steps)
- Step labels with checkmarks
- Percentage complete

---

## Common Patterns Across All Sections

### Loading State
```typescript
if (isLoading) {
  return <Skeleton />;
}
```

### Error Handling
```typescript
try {
  await api.updateConfig(data);
  toast({ title: 'Success', description: 'Settings saved' });
} catch (error: any) {
  toast({
    title: 'Error',
    description: error.message || 'Failed to save settings',
    variant: 'destructive',
  });
}
```

### Save Button Pattern
```typescript
<Button onClick={handleSave} disabled={isSaving}>
  {isSaving ? <Loader2 className="animate-spin" /> : 'Save Changes'}
</Button>
```

---

## Summary

The 10 Settings sections provide comprehensive configuration for all aspects of CreatorPulse:

**Essential** (Must configure for basic functionality):
1. ✅ Content Sources - Where content comes from
2. ✅ Schedule - When newsletters are generated
3. ✅ Subscribers - Who receives newsletters
4. ✅ Email Config - How newsletters are sent
5. ✅ Workspace - Team collaboration

**Advanced** (Enhance functionality):
6. 🔑 API Keys - External integrations
7. ✍️ Writing Style - AI tone customization
8. 🔥 Trends - Topic detection
9. 📊 Analytics - Engagement tracking
10. 💬 Feedback - Curation improvement

**Key Takeaway**: Each section is self-contained, uses consistent patterns, and integrates with backend APIs for persistence.

---

**For overall frontend architecture, see**: [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)

**END OF SETTINGS_COMPONENTS.md**