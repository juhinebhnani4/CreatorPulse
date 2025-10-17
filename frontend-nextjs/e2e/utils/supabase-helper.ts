/**
 * Supabase Helper for E2E Testing
 *
 * Provides utilities to verify database state during E2E tests.
 * Each test action on the frontend is verified against the database.
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from .env.test.local
dotenv.config({ path: path.resolve(__dirname, '../../.env.test.local') });

export class SupabaseTestHelper {
  private client: SupabaseClient;
  private serviceClient: SupabaseClient;

  constructor() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseAnonKey = process.env.SUPABASE_ANON_KEY;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseAnonKey || !supabaseServiceKey) {
      throw new Error('Missing Supabase environment variables for testing');
    }

    // Regular client (respects RLS)
    this.client = createClient(supabaseUrl, supabaseAnonKey);

    // Service client (bypasses RLS for test verification)
    this.serviceClient = createClient(supabaseUrl, supabaseServiceKey);
  }

  /**
   * Set authentication token for RLS-aware queries
   */
  setAuthToken(token: string) {
    this.client = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_ANON_KEY!,
      {
        global: {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      }
    );
  }

  // ==================== USER VERIFICATION ====================

  /**
   * Verify user exists in database
   */
  async verifyUserExists(email: string): Promise<{ id: string; email: string } | null> {
    // Try public.users table first
    const { data, error } = await this.serviceClient
      .from('users')
      .select('id, email')
      .eq('email', email)
      .maybeSingle(); // Use maybeSingle() instead of single() to avoid error when no rows

    if (data) {
      return data;
    }

    if (error && error.code !== 'PGRST116') {
      console.error('Error verifying user in users table:', error);
    }

    // Fallback: Try to get user from Supabase Auth
    try {
      const { data: authData, error: authError } = await this.serviceClient.auth.admin.listUsers();

      if (authError) {
        console.error('Error listing auth users:', authError);
        return null;
      }

      const user = authData.users.find(u => u.email === email);
      if (user) {
        return {
          id: user.id,
          email: user.email!
        };
      }
    } catch (authErr) {
      console.error('Error checking auth users:', authErr);
    }

    return null;
  }

  /**
   * Verify user session exists
   */
  async verifyUserSession(userId: string): Promise<boolean> {
    const { data, error } = await this.serviceClient.auth.admin.listUserSessions(userId);

    if (error) {
      console.error('Error checking session:', error);
      return false;
    }

    return data && data.length > 0;
  }

  /**
   * Get user by email
   */
  async getUserByEmail(email: string) {
    const { data, error } = await this.serviceClient
      .from('users')
      .select('*')
      .eq('email', email)
      .maybeSingle(); // Use maybeSingle() to avoid error when no rows

    return { data, error };
  }

  // ==================== WORKSPACE VERIFICATION ====================

  /**
   * Verify workspace exists and belongs to user
   */
  async verifyWorkspace(workspaceId: string, userId: string) {
    const { data, error } = await this.serviceClient
      .from('workspaces')
      .select('*')
      .eq('id', workspaceId)
      .eq('user_id', userId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Get all workspaces for a user
   */
  async getUserWorkspaces(userId: string) {
    const { data, error } = await this.serviceClient
      .from('workspaces')
      .select('*')
      .eq('user_id', userId);

    return { data, error };
  }

  /**
   * List workspaces for a user (returns array)
   */
  async listWorkspaces(userId: string): Promise<any[]> {
    const { data, error } = await this.serviceClient
      .from('workspaces')
      .select('*')
      .eq('user_id', userId);

    if (error) {
      console.error('Error listing workspaces:', error);
      return [];
    }

    return data || [];
  }

  /**
   * Verify workspace was created recently (within last minute)
   */
  async verifyRecentWorkspaceCreation(workspaceId: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('workspaces')
      .select('created_at')
      .eq('id', workspaceId)
      .single();

    if (!data) return false;

    const createdAt = new Date(data.created_at);
    const now = new Date();
    const diffMs = now.getTime() - createdAt.getTime();
    const diffMinutes = diffMs / (1000 * 60);

    return diffMinutes < 1; // Created within last minute
  }

  // ==================== CONTENT SOURCE VERIFICATION ====================

  /**
   * Verify content source exists
   */
  async verifyContentSource(sourceId: string, workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('content_sources')
      .select('*')
      .eq('id', sourceId)
      .eq('workspace_id', workspaceId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Get all sources for a workspace
   */
  async getWorkspaceSources(workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('content_sources')
      .select('*')
      .eq('workspace_id', workspaceId);

    return { data, error };
  }

  /**
   * Verify source type
   */
  async verifySourceType(sourceId: string, expectedType: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('content_sources')
      .select('source_type')
      .eq('id', sourceId)
      .single();

    return data?.source_type === expectedType;
  }

  // ==================== CONTENT ITEMS VERIFICATION ====================

  /**
   * Verify content item exists
   */
  async verifyContentItem(contentId: string) {
    const { data, error } = await this.serviceClient
      .from('content_items')
      .select('*')
      .eq('id', contentId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Get all content items for a workspace
   */
  async getWorkspaceContent(workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('content_items')
      .select('*')
      .eq('workspace_id', workspaceId);

    return { data, error };
  }

  /**
   * Get content items by source
   */
  async getContentBySource(sourceId: string) {
    const { data, error } = await this.serviceClient
      .from('content_items')
      .select('*')
      .eq('source_id', sourceId);

    return { data, error };
  }

  /**
   * Verify content item has required fields
   */
  async verifyContentItemFields(contentId: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('content_items')
      .select('title, url, source_id, workspace_id')
      .eq('id', contentId)
      .single();

    return !!(data?.title && data?.url && data?.source_id && data?.workspace_id);
  }

  // ==================== SCRAPE JOB VERIFICATION ====================

  /**
   * Verify scrape job status
   */
  async verifyScrapeJobStatus(jobId: string, expectedStatus: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('scrape_jobs')
      .select('status')
      .eq('id', jobId)
      .single();

    return data?.status === expectedStatus;
  }

  /**
   * Wait for scrape job to complete
   */
  async waitForScrapeJobCompletion(jobId: string, timeoutMs: number = 30000): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      const { data } = await this.serviceClient
        .from('scrape_jobs')
        .select('status')
        .eq('id', jobId)
        .single();

      if (data?.status === 'completed') return true;
      if (data?.status === 'failed') return false;

      // Wait 1 second before checking again
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    return false; // Timeout
  }

  // ==================== NEWSLETTER VERIFICATION ====================

  /**
   * Verify newsletter exists
   */
  async verifyNewsletter(newsletterId: string, workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('newsletters')
      .select('*')
      .eq('id', newsletterId)
      .eq('workspace_id', workspaceId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Verify newsletter status
   */
  async verifyNewsletterStatus(newsletterId: string, expectedStatus: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('newsletters')
      .select('status')
      .eq('id', newsletterId)
      .single();

    return data?.status === expectedStatus;
  }

  /**
   * Verify newsletter has content
   */
  async verifyNewsletterContent(newsletterId: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('newsletters')
      .select('content_html')
      .eq('id', newsletterId)
      .single();

    return !!data?.content_html && data.content_html.length > 0;
  }

  /**
   * Wait for newsletter generation
   */
  async waitForNewsletterGeneration(newsletterId: string, timeoutMs: number = 60000): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      const { data } = await this.serviceClient
        .from('newsletters')
        .select('status')
        .eq('id', newsletterId)
        .single();

      if (data?.status === 'completed') return true;
      if (data?.status === 'failed') return false;

      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    return false;
  }

  /**
   * Create a test newsletter
   */
  async createNewsletter(workspaceId: string, data: any): Promise<any> {
    const newsletterData = {
      workspace_id: workspaceId,
      title: data.title || 'Test Newsletter',
      subject_line: data.subject_line || 'Test Subject',
      status: data.status || 'draft',
      content_html: data.content_html || '<p>Test content</p>',
      content_json: data.content_json || {},
      sent_at: data.sent_at || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const { data: newsletter, error } = await this.serviceClient
      .from('newsletters')
      .insert(newsletterData)
      .select()
      .single();

    if (error) {
      console.error('Error creating newsletter:', error);
      throw error;
    }

    return newsletter;
  }

  // ==================== SUBSCRIBER VERIFICATION ====================

  /**
   * Verify subscriber exists
   */
  async verifySubscriber(email: string, workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('subscribers')
      .select('*')
      .eq('email', email)
      .eq('workspace_id', workspaceId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Get all subscribers for workspace
   */
  async getWorkspaceSubscribers(workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('subscribers')
      .select('*')
      .eq('workspace_id', workspaceId);

    return { data, error };
  }

  /**
   * Create a test subscriber
   */
  async createSubscriber(workspaceId: string, data: any): Promise<any> {
    const subscriberData = {
      workspace_id: workspaceId,
      email: data.email,
      name: data.name || null,
      status: data.status || 'active',
      source: data.source || 'manual',
      metadata: data.metadata || {},
      subscribed_at: data.subscribed_at || new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const { data: subscriber, error } = await this.serviceClient
      .from('subscribers')
      .insert(subscriberData)
      .select()
      .single();

    if (error) {
      console.error('Error creating subscriber:', error);
      throw error;
    }

    return subscriber;
  }

  // ==================== SCHEDULE VERIFICATION ====================

  /**
   * Verify schedule exists and is active
   */
  async verifySchedule(scheduleId: string, workspaceId: string) {
    const { data, error } = await this.serviceClient
      .from('schedules')
      .select('*')
      .eq('id', scheduleId)
      .eq('workspace_id', workspaceId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Verify schedule is active
   */
  async verifyScheduleActive(scheduleId: string): Promise<boolean> {
    const { data } = await this.serviceClient
      .from('schedules')
      .select('is_active')
      .eq('id', scheduleId)
      .single();

    return data?.is_active === true;
  }

  // ==================== ANALYTICS VERIFICATION ====================

  /**
   * Get analytics events for newsletter
   */
  async getNewsletterAnalytics(newsletterId: string) {
    const { data, error } = await this.serviceClient
      .from('analytics_events')
      .select('*')
      .eq('newsletter_id', newsletterId);

    return { data, error };
  }

  /**
   * Count events by type
   */
  async countEventsByType(newsletterId: string, eventType: string): Promise<number> {
    const { data } = await this.serviceClient
      .from('analytics_events')
      .select('id')
      .eq('newsletter_id', newsletterId)
      .eq('event_type', eventType);

    return data?.length || 0;
  }

  /**
   * Verify analytics event exists
   */
  async verifyAnalyticsEvent(eventType: string, metadata: any) {
    const { data, error } = await this.serviceClient
      .from('analytics_events')
      .select('*')
      .eq('event_type', eventType)
      .contains('metadata', metadata);

    return { data, error, exists: data && data.length > 0 };
  }

  // ==================== FEEDBACK VERIFICATION ====================

  /**
   * Verify user feedback exists
   */
  async verifyFeedback(userId: string, contentId: string) {
    const { data, error } = await this.serviceClient
      .from('user_feedback')
      .select('*')
      .eq('user_id', userId)
      .eq('content_id', contentId)
      .single();

    return { data, error, exists: !!data };
  }

  /**
   * Get user's style profile
   */
  async getUserStyleProfile(userId: string) {
    const { data, error } = await this.serviceClient
      .from('style_profiles')
      .select('*')
      .eq('user_id', userId)
      .single();

    return { data, error };
  }

  // ==================== CLEANUP UTILITIES ====================

  /**
   * Delete test user and all related data
   */
  async cleanupTestUser(userId: string) {
    // Delete user (cascade should handle related records)
    await this.serviceClient.auth.admin.deleteUser(userId);

    // Manually clean up any orphaned records
    await this.serviceClient.from('workspaces').delete().eq('user_id', userId);
    await this.serviceClient.from('style_profiles').delete().eq('user_id', userId);
  }

  /**
   * Delete test user by email
   */
  async cleanupUser(email: string) {
    try {
      // Find user
      const user = await this.verifyUserExists(email);
      if (!user) {
        console.log(`[Cleanup] User ${email} not found`);
        return;
      }

      console.log(`[Cleanup] Deleting user: ${email} (${user.id})`);

      // Delete from auth
      await this.serviceClient.auth.admin.deleteUser(user.id);

      // Delete from users table
      await this.serviceClient.from('users').delete().eq('id', user.id);

      // Clean up workspaces (should cascade)
      await this.serviceClient.from('workspaces').delete().eq('user_id', user.id);

      console.log(`[Cleanup] User ${email} deleted successfully`);
    } catch (error) {
      console.error(`[Cleanup] Error deleting user ${email}:`, error);
    }
  }

  /**
   * Delete test workspace and all related data
   */
  async cleanupTestWorkspace(workspaceId: string) {
    // Delete workspace (cascade should handle related records)
    await this.serviceClient.from('workspaces').delete().eq('id', workspaceId);

    // Manually clean up any orphaned records
    await this.serviceClient.from('content_sources').delete().eq('workspace_id', workspaceId);
    await this.serviceClient.from('content_items').delete().eq('workspace_id', workspaceId);
    await this.serviceClient.from('newsletters').delete().eq('workspace_id', workspaceId);
    await this.serviceClient.from('subscribers').delete().eq('workspace_id', workspaceId);
    await this.serviceClient.from('schedules').delete().eq('workspace_id', workspaceId);
  }

  /**
   * Clean up all test data created after a specific timestamp
   */
  async cleanupTestDataAfter(timestamp: Date) {
    const isoTimestamp = timestamp.toISOString();

    // Clean up in reverse dependency order
    await this.serviceClient.from('analytics_events').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('user_feedback').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('newsletters').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('content_items').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('content_sources').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('subscribers').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('schedules').delete().gte('created_at', isoTimestamp);
    await this.serviceClient.from('workspaces').delete().gte('created_at', isoTimestamp);
  }
}

// Export singleton instance
export const supabaseHelper = new SupabaseTestHelper();
