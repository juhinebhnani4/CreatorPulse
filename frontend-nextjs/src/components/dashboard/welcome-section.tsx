'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface WelcomeSectionProps {
  username: string;
  stepsCompleted: number;
  totalSteps: number;
  showProgress?: boolean;
}

export function WelcomeSection({
  username,
  stepsCompleted,
  totalSteps,
  showProgress = true,
}: WelcomeSectionProps) {
  const progressPercent = (stepsCompleted / totalSteps) * 100;
  const isComplete = stepsCompleted === totalSteps;

  const getMotivationalMessage = () => {
    if (isComplete) {
      return "🎉 You're all set! Ready to create amazing newsletters.";
    }
    const remaining = totalSteps - stepsCompleted;
    if (stepsCompleted === 0) {
      return `You're just ${totalSteps} steps away from your first automated newsletter! Let's get you set up.`;
    }
    if (remaining === 1) {
      return `Almost there! Just ${remaining} step left to complete your setup.`;
    }
    return `You're doing great! ${remaining} steps to go.`;
  };

  return (
    <Card className="border-0 bg-gradient-hero shadow-lg animate-slide-up overflow-hidden">
      <CardContent className="pt-8 pb-8">
        <div className="space-y-4 text-white">
          {/* Greeting */}
          <h1 className="text-3xl font-bold">
            Welcome back, {username}! 👋
          </h1>

          {/* Motivational message */}
          <p className="text-lg opacity-95">
            {getMotivationalMessage()}
          </p>

          {/* Progress bar */}
          {showProgress && !isComplete && (
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Setup Progress</span>
                <span className="font-bold">{stepsCompleted}/{totalSteps}</span>
              </div>
              <div className="relative">
                <div className="h-3 bg-white/20 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white transition-all duration-500 ease-out rounded-full"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Success state */}
          {isComplete && (
            <div className="flex items-center gap-2 pt-2 pb-1">
              <div className="flex items-center gap-2 text-white/90">
                <span className="text-2xl">✓</span>
                <span className="font-medium">Setup complete</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
