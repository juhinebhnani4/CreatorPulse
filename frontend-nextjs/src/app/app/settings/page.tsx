'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { ChevronDown } from 'lucide-react';
import { SourcesSettings } from '@/components/settings/sources-settings';
import { ScheduleSettings } from '@/components/settings/schedule-settings';
import { SubscribersSettings } from '@/components/settings/subscribers-settings';
import { WorkspaceSettings } from '@/components/settings/workspace-settings';
import { StyleSettings } from '@/components/settings/style-settings';
import { TrendsSettings } from '@/components/settings/trends-settings';
import { AnalyticsSettings } from '@/components/settings/analytics-settings';
import { FeedbackSettings } from '@/components/settings/feedback-settings';
import { SetupProgress } from '@/components/settings/setup-progress';
import { SettingsSidebar } from '@/components/settings/settings-sidebar';
import { AppHeader } from '@/components/layout/app-header';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function SettingsPage() {
  const searchParams = useSearchParams();
  const [activeSection, setActiveSection] = useState('sources');
  const [highlightAction, setHighlightAction] = useState<string | null>(null);

  // Check URL parameters for navigation from dropdown
  useEffect(() => {
    const section = searchParams.get('section');
    const action = searchParams.get('action');

    if (section) {
      setActiveSection(section);
    }

    if (action === 'create') {
      setHighlightAction('create');
      // Remove highlight after animation
      setTimeout(() => setHighlightAction(null), 3000);
    }
  }, [searchParams]);

  // Setup progress tracking
  const setupSteps = [
    { id: 'sources', label: 'Content Sources', completed: true },
    { id: 'schedule', label: 'Schedule', completed: true },
    { id: 'style', label: 'Writing Style', completed: false },
  ];

  const sections = [
    {
      id: 'sources',
      title: '📱 Content Sources',
      icon: '📱',
      component: <SourcesSettings />,
      status: 'configured' as const,
      statusText: '2 sources active',
      description: 'Configure Reddit, RSS feeds, Twitter, and more',
    },
    {
      id: 'schedule',
      title: '⏰ Schedule Settings',
      icon: '⏰',
      component: <ScheduleSettings />,
      status: 'configured' as const,
      statusText: 'Daily at 8:00 AM',
      description: 'Set when your newsletters are generated and sent',
    },
    {
      id: 'subscribers',
      title: '👥 Subscribers',
      icon: '👥',
      component: <SubscribersSettings />,
      status: 'configured' as const,
      statusText: '1,234 subscribers',
      description: 'Manage your subscriber list and import contacts',
    },
    {
      id: 'workspace',
      title: '🏢 Workspace',
      icon: '🏢',
      component: <WorkspaceSettings highlightCreate={highlightAction === 'create'} />,
      status: 'configured' as const,
      statusText: 'My Workspace',
      description: 'Manage workspace settings and team members',
    },
    {
      id: 'style',
      title: '✍️ Writing Style',
      icon: '✍️',
      component: <StyleSettings />,
      status: 'pending' as const,
      statusText: 'Using defaults',
      description: 'Customize your newsletter tone and style',
      isAdvanced: true,
    },
    {
      id: 'trends',
      title: '🔥 Trends Detection',
      icon: '🔥',
      component: <TrendsSettings />,
      status: 'configured' as const,
      statusText: 'Active',
      description: 'Identify trending topics in your content',
      isAdvanced: true,
    },
    {
      id: 'analytics',
      title: '📊 Analytics',
      icon: '📊',
      component: <AnalyticsSettings />,
      status: 'configured' as const,
      statusText: 'Tracking enabled',
      description: 'Track engagement and performance metrics',
      isAdvanced: true,
    },
    {
      id: 'feedback',
      title: '💬 Feedback Loop',
      icon: '💬',
      component: <FeedbackSettings />,
      status: 'configured' as const,
      statusText: 'Active',
      description: 'Learn from subscriber interactions',
      isAdvanced: true,
    },
  ];

  const activeContent = sections.find(s => s.id === activeSection);

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />

      {/* Main Container with Sidebar */}
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Setup Progress - Full Width */}
        <div className="mb-6 animate-slide-up">
          <SetupProgress steps={setupSteps} />
        </div>

        {/* Sidebar Layout */}
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <SettingsSidebar
            sections={sections}
            activeSection={activeSection}
            onSectionChange={setActiveSection}
          />

          {/* Main Content Area */}
          <main className="flex-1 min-w-0">
            {/* Mobile Section Selector */}
            <div className="lg:hidden mb-6">
              <Select value={activeSection} onValueChange={setActiveSection}>
                <SelectTrigger className="w-full h-12 text-base">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {sections.map((section) => (
                    <SelectItem key={section.id} value={section.id}>
                      <div className="flex items-center gap-2">
                        <span>{section.icon}</span>
                        <span>{section.title.replace(/^[^\s]+\s/, '')}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Section Header */}
            <div className="mb-6 animate-slide-up">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-3xl">{activeContent?.icon}</span>
                <h1 className="text-3xl font-bold">
                  {activeContent?.title.replace(/^[^\s]+\s/, '')}
                </h1>
              </div>
              <p className="text-muted-foreground">
                {activeContent?.description}
              </p>
            </div>

            {/* Section Content Card */}
            <div className="bg-card rounded-2xl shadow-lg p-8 animate-slide-up" style={{ animationDelay: '100ms' }}>
              {activeContent?.component}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
