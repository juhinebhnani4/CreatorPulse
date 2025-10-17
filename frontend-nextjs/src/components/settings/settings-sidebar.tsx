'use client';

import { cn } from '@/lib/utils';
import { CheckCircle2, AlertCircle, Clock, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface SettingsSection {
  id: string;
  title: string;
  icon: string;
  status?: 'configured' | 'incomplete' | 'pending';
  statusText?: string;
  isAdvanced?: boolean;
}

interface SettingsSidebarProps {
  sections: SettingsSection[];
  activeSection: string;
  onSectionChange: (sectionId: string) => void;
}

export function SettingsSidebar({
  sections,
  activeSection,
  onSectionChange,
}: SettingsSidebarProps) {
  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'configured':
        return <CheckCircle2 className="h-4 w-4 text-success" />;
      case 'incomplete':
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-warning" />;
      default:
        return null;
    }
  };

  const basicSections = sections.filter(s => !s.isAdvanced);
  const advancedSections = sections.filter(s => s.isAdvanced);

  return (
    <aside className="w-72 flex-shrink-0 border-r bg-card/50 p-6 sticky top-20 h-[calc(100vh-5rem)] overflow-y-auto hidden lg:block">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gradient mb-1">Settings</h2>
        <p className="text-sm text-muted-foreground">Configure your workspace</p>
      </div>

      {/* Navigation */}
      <nav className="space-y-2">
        {/* Basic sections */}
        {basicSections.map((section, index) => {
          const isActive = activeSection === section.id;

          return (
            <button
              key={section.id}
              onClick={() => onSectionChange(section.id)}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 group animate-slide-up',
                isActive
                  ? 'bg-gradient-hero text-white shadow-lg'
                  : 'hover:bg-muted/50'
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Icon and Title */}
              <div className="flex-1 flex items-center gap-3 min-w-0">
                <span className="text-xl flex-shrink-0">{section.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">
                    {section.title.replace(/^[^\s]+\s/, '')} {/* Remove emoji from title */}
                  </div>
                  {section.statusText && !isActive && (
                    <div className="text-xs text-muted-foreground truncate">
                      {section.statusText}
                    </div>
                  )}
                </div>
              </div>

              {/* Status indicator */}
              <div className="flex-shrink-0 flex items-center gap-1">
                {!isActive && getStatusIcon(section.status)}
                {isActive && (
                  <ChevronRight className={cn(
                    'h-4 w-4 transition-transform',
                    isActive ? 'text-white' : 'text-muted-foreground'
                  )} />
                )}
              </div>
            </button>
          );
        })}

        {/* Advanced section divider */}
        {advancedSections.length > 0 && (
          <>
            <div className="pt-4 pb-2">
              <div className="flex items-center gap-2 px-4">
                <div className="flex-1 h-px bg-border" />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Advanced
                </span>
                <div className="flex-1 h-px bg-border" />
              </div>
            </div>

            {/* Advanced sections */}
            {advancedSections.map((section, index) => {
              const isActive = activeSection === section.id;

              return (
                <button
                  key={section.id}
                  onClick={() => onSectionChange(section.id)}
                  className={cn(
                    'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 group animate-slide-up',
                    isActive
                      ? 'bg-gradient-hero text-white shadow-lg'
                      : 'hover:bg-muted/50'
                  )}
                  style={{ animationDelay: `${(basicSections.length + index) * 50}ms` }}
                >
                  {/* Icon and Title */}
                  <div className="flex-1 flex items-center gap-3 min-w-0">
                    <span className="text-xl flex-shrink-0">{section.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">
                        {section.title.replace(/^[^\s]+\s/, '')}
                      </div>
                      {section.statusText && !isActive && (
                        <div className="text-xs text-muted-foreground truncate">
                          {section.statusText}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Status indicator */}
                  <div className="flex-shrink-0 flex items-center gap-1">
                    {!isActive && getStatusIcon(section.status)}
                    {isActive && (
                      <ChevronRight className={cn(
                        'h-4 w-4 transition-transform',
                        isActive ? 'text-white' : 'text-muted-foreground'
                      )} />
                    )}
                  </div>
                </button>
              );
            })}
          </>
        )}
      </nav>

      {/* Help section */}
      <div className="mt-8 p-4 bg-primary/5 border border-primary/20 rounded-xl">
        <div className="flex items-start gap-2">
          <span className="text-lg">💡</span>
          <div className="text-xs">
            <p className="font-medium text-foreground mb-1">Need help?</p>
            <p className="text-muted-foreground">
              Check out our <span className="text-primary font-medium cursor-pointer">documentation</span>
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
