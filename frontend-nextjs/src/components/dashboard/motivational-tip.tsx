'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Lightbulb, Target, Clock, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

interface MotivationalTipProps {
  stepsCompleted?: number;
  totalSteps?: number;
}

export function MotivationalTip({ stepsCompleted = 0, totalSteps = 3 }: MotivationalTipProps) {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);

  const tips = [
    {
      icon: Lightbulb,
      title: 'Did you know?',
      message: 'Newsletters with 3-5 sources get 23% higher engagement!',
      color: 'text-warning',
      bgColor: 'bg-warning/10',
    },
    {
      icon: Target,
      title: 'Goal',
      message: 'Send your first newsletter by tomorrow!',
      color: 'text-success',
      bgColor: 'bg-success/10',
    },
    {
      icon: Clock,
      title: 'Quick Setup',
      message: 'Setup takes most users just 8 minutes',
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      icon: Sparkles,
      title: 'Join the community',
      message: 'Join 10,000+ creators using CreatorPulse',
      color: 'text-secondary',
      bgColor: 'bg-secondary/10',
    },
  ];

  // Rotate tips every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % tips.length);
    }, 10000);

    return () => clearInterval(interval);
  }, [tips.length]);

  const currentTip = tips[currentTipIndex];
  const Icon = currentTip.icon;

  // Show different tips based on progress
  const getContextualTip = () => {
    if (stepsCompleted === 0) {
      return {
        icon: Target,
        title: '🚀 Let\'s get started',
        message: 'Configure your first source to begin your newsletter journey!',
        color: 'text-primary',
        bgColor: 'bg-primary/10',
      };
    }
    if (stepsCompleted < totalSteps) {
      return {
        icon: Clock,
        title: '💪 Keep going',
        message: `You're ${Math.round((stepsCompleted / totalSteps) * 100)}% of the way there!`,
        color: 'text-warning',
        bgColor: 'bg-warning/10',
      };
    }
    return currentTip;
  };

  const tip = getContextualTip();
  const TipIcon = tip.icon;

  return (
    <Card className={`border-0 ${tip.bgColor} animate-slide-up`} style={{ animationDelay: '300ms' }}>
      <CardContent className="pt-4 pb-4">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${tip.bgColor} ${tip.color}`}>
            <TipIcon className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-sm mb-1">{tip.title}</h4>
            <p className="text-sm text-muted-foreground">{tip.message}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
