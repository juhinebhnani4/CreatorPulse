'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, ArrowRight, Zap, Target, Mail } from 'lucide-react';

interface EmptyStateProps {
  onAddSource: () => void;
}

export function EmptyState({ onAddSource }: EmptyStateProps) {
  return (
    <Card className="border-2 border-dashed animate-slide-up">
      <CardContent className="pt-8 pb-10">
        <div className="text-center">
          {/* Hero Icon with Gradient */}
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-hero mb-6 shadow-lg animate-pulse-soft">
            <Sparkles className="w-12 h-12 text-white" />
          </div>

          {/* Main Heading */}
          <h2 className="text-3xl font-bold mb-3 text-gradient">
            Let's Create Your First Newsletter!
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto leading-relaxed">
            Connect your favorite content sources and we'll craft a beautiful, personalized newsletter for you automatically.
          </p>

          {/* Steps Visual */}
          <div className="grid md:grid-cols-3 gap-6 mb-10 max-w-3xl mx-auto">
            {/* Step 1 */}
            <div className="bg-muted/50 rounded-2xl p-6 text-left hover:bg-muted transition-colors">
              <div className="w-12 h-12 bg-gradient-warm rounded-xl flex items-center justify-center mb-4">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold text-primary text-xl">1</span>
                <h3 className="font-semibold text-base">Add Sources</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Connect Reddit, RSS feeds, Twitter, and more
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-muted/50 rounded-2xl p-6 text-left hover:bg-muted transition-colors">
              <div className="w-12 h-12 bg-gradient-hero rounded-xl flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold text-primary text-xl">2</span>
                <h3 className="font-semibold text-base">AI Curates</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                We find the best content and craft summaries
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-muted/50 rounded-2xl p-6 text-left hover:bg-muted transition-colors">
              <div className="w-12 h-12 bg-gradient-cool rounded-xl flex items-center justify-center mb-4">
                <Mail className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold text-primary text-xl">3</span>
                <h3 className="font-semibold text-base">Send & Shine</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Review, personalize, and send to subscribers
              </p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex gap-4 justify-center items-center">
            <Button
              size="lg"
              onClick={onAddSource}
              className="bg-gradient-hero hover:opacity-90 transition-opacity shadow-lg text-lg px-8 h-12"
            >
              <Sparkles className="h-5 w-5 mr-2" />
              Create My First Newsletter
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </div>

          {/* Helper Text */}
          <p className="text-xs text-muted-foreground mt-6">
            Takes less than 2 minutes • No credit card required • Free forever
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
