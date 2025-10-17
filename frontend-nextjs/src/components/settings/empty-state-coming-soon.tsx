'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LucideIcon } from 'lucide-react';

interface EmptyStateComingSoonProps {
  icon: LucideIcon;
  title: string;
  description: string;
  helpText?: string;
  helpLink?: string;
}

export function EmptyStateComingSoon({
  icon: Icon,
  title,
  description,
  helpText,
  helpLink,
}: EmptyStateComingSoonProps) {
  return (
    <div className="py-12">
      <div className="text-center">
        {/* Icon */}
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-hero mb-6 animate-pulse-soft">
          <Icon className="w-8 h-8 text-white" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold mb-3">{title}</h3>

        {/* Description */}
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          {description}
        </p>

        {/* Help link */}
        {helpText && helpLink && (
          <div className="flex items-center justify-center gap-2">
            <span className="text-sm text-muted-foreground">{helpText}</span>
            <Button variant="link" className="text-sm p-0 h-auto">
              {helpLink}
            </Button>
          </div>
        )}

        {/* Coming soon badge */}
        <div className="mt-6">
          <span className="inline-block px-4 py-2 bg-warning/10 text-warning rounded-full text-sm font-medium">
            🚀 Coming Soon
          </span>
        </div>
      </div>
    </div>
  );
}
