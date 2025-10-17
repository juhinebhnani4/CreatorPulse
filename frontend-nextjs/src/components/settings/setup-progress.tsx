'use client';

import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle2, Circle } from 'lucide-react';

interface SetupStep {
  id: string;
  label: string;
  completed: boolean;
}

interface SetupProgressProps {
  steps: SetupStep[];
}

export function SetupProgress({ steps }: SetupProgressProps) {
  const completedCount = steps.filter(s => s.completed).length;
  const totalCount = steps.length;
  const progressPercent = (completedCount / totalCount) * 100;

  return (
    <Card className="border-0 shadow-lg bg-gradient-hero animate-slide-up">
      <CardContent className="pt-6 pb-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between text-white">
            <h3 className="text-lg font-bold">Setup Progress</h3>
            <span className="text-sm font-semibold bg-white/20 px-3 py-1 rounded-full">
              {completedCount}/{totalCount} Complete
            </span>
          </div>

          {/* Progress Bar */}
          <div className="relative">
            <div className="h-2 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-white transition-all duration-500 ease-out"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* Steps Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 pt-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className="flex items-center gap-2 text-white animate-slide-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {step.completed ? (
                  <CheckCircle2 className="h-5 w-5 flex-shrink-0" />
                ) : (
                  <Circle className="h-5 w-5 flex-shrink-0 opacity-60" />
                )}
                <span className={`text-sm font-medium ${step.completed ? '' : 'opacity-70'}`}>
                  {step.label}
                </span>
              </div>
            ))}
          </div>

          {/* Encouragement Message */}
          {completedCount < totalCount && (
            <div className="pt-2 border-t border-white/20">
              <p className="text-sm text-white/90">
                {completedCount === 0
                  ? '🚀 Get started by configuring your content sources!'
                  : completedCount < totalCount / 2
                  ? '💪 Great start! Keep going to unlock full features.'
                  : '🎉 Almost there! Just a few more steps to complete setup.'}
              </p>
            </div>
          )}

          {completedCount === totalCount && (
            <div className="pt-2 border-t border-white/20">
              <p className="text-sm text-white/90 font-medium">
                ✅ All set! You're ready to create amazing newsletters.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
