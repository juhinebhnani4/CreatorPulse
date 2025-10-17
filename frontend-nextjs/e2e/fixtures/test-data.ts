/**
 * Test Data Fixtures
 *
 * Provides consistent test data across all E2E tests.
 */

export const testUsers = {
  newUser: {
    email: 'e2e-new-user@creatorpulse.test',
    password: 'SecureTestPass123!',
    name: 'E2E Test User',
  },
  existingUser: {
    email: 'e2e-existing-user@creatorpulse.test',
    password: 'SecureTestPass123!',
    name: 'Existing E2E User',
  },
};

export const testWorkspaces = {
  first: {
    name: 'My First Workspace',
    description: 'Testing workspace creation',
  },
  second: {
    name: 'AI News Curator',
    description: 'Curating AI and tech news',
  },
};

export const testContentSources = {
  rss: {
    name: 'TechCrunch AI',
    sourceType: 'rss',
    url: 'https://techcrunch.com/category/artificial-intelligence/feed/',
    config: {
      refreshInterval: 3600,
    },
  },
  reddit: {
    name: 'r/MachineLearning',
    sourceType: 'reddit',
    url: 'https://reddit.com/r/MachineLearning',
    config: {
      subreddit: 'MachineLearning',
      sort: 'hot',
      limit: 10,
    },
  },
  twitter: {
    name: '@OpenAI',
    sourceType: 'twitter',
    url: 'https://twitter.com/OpenAI',
    config: {
      username: 'OpenAI',
      includeReplies: false,
    },
  },
  blog: {
    name: 'Anthropic Blog',
    sourceType: 'blog',
    url: 'https://www.anthropic.com/news',
    config: {
      crawlDepth: 1,
    },
  },
};

export const testNewsletters = {
  weekly: {
    subject: 'Weekly AI News Digest',
    previewText: 'Your curated AI news for this week',
    tone: 'professional',
    frequency: 'weekly',
  },
  daily: {
    subject: 'Daily Tech Updates',
    previewText: "Today's top tech stories",
    tone: 'casual',
    frequency: 'daily',
  },
};

export const testSubscribers = [
  {
    email: 'subscriber1@example.com',
    name: 'Subscriber One',
    status: 'active',
  },
  {
    email: 'subscriber2@example.com',
    name: 'Subscriber Two',
    status: 'active',
  },
  {
    email: 'subscriber3@example.com',
    name: 'Subscriber Three',
    status: 'active',
  },
];

export const testSchedules = {
  daily: {
    frequency: 'daily',
    time: '09:00',
    timezone: 'America/New_York',
    isActive: true,
  },
  weekly: {
    frequency: 'weekly',
    dayOfWeek: 'Monday',
    time: '10:00',
    timezone: 'America/New_York',
    isActive: true,
  },
  monthly: {
    frequency: 'monthly',
    dayOfMonth: 1,
    time: '08:00',
    timezone: 'America/New_York',
    isActive: true,
  },
};

export const testFeedback = {
  positive: {
    rating: 1,
    comment: 'Great content!',
  },
  negative: {
    rating: -1,
    comment: 'Not relevant to my interests',
  },
};

/**
 * Generate unique test email with timestamp
 */
export function generateTestEmail(prefix: string = 'test'): string {
  const timestamp = Date.now();
  return `${prefix}-${timestamp}@creatorpulse.test`;
}

/**
 * Generate unique workspace name
 */
export function generateWorkspaceName(base: string = 'Test Workspace'): string {
  const timestamp = Date.now();
  return `${base} ${timestamp}`;
}

/**
 * Wait for specified milliseconds
 */
export function wait(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry function with exponential backoff
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: Error | undefined;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        await wait(delayMs * Math.pow(2, i)); // Exponential backoff
      }
    }
  }

  throw lastError;
}
