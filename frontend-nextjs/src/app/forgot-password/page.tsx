'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card';
import { ArrowLeft, Mail } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('[ForgotPasswordPage] Requesting password reset for:', email);

    try {
      // TODO: Implement password reset API call
      // const response = await authApi.requestPasswordReset({ email });

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      console.log('[ForgotPasswordPage] Password reset email sent');
      setSuccess(true);
    } catch (err: any) {
      console.error('[ForgotPasswordPage] Error:', err);
      setError(err.message || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/20 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold">
              CP
            </div>
            <span className="text-2xl font-bold">CreatorPulse</span>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="gap-1">
                  <ArrowLeft className="h-4 w-4" />
                  Back to login
                </Button>
              </Link>
            </div>
            <h2 className="text-2xl font-semibold leading-none tracking-tight">
              Reset your password
            </h2>
            <CardDescription data-testid="forgot-password-description">
              Enter your email address and we'll send you a link to reset your password
            </CardDescription>
          </CardHeader>
          <CardContent>
            {success ? (
              <div className="space-y-4">
                <div className="p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-md" data-testid="reset-email-sent-message">
                  <div className="flex items-start gap-3">
                    <Mail className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-green-900 dark:text-green-100">
                        Check your email
                      </p>
                      <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                        We've sent a password reset link to <strong>{email}</strong>
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400 mt-2">
                        If you don't see it, check your spam folder.
                      </p>
                    </div>
                  </div>
                </div>

                <Link href="/login" className="block" data-testid="back-to-login-link">
                  <Button className="w-full">
                    Back to Login
                  </Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    Email address
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={loading}
                    data-testid="forgot-password-email"
                  />
                </div>

                <Button type="submit" className="w-full" disabled={loading} data-testid="forgot-password-submit">
                  {loading ? 'Sending reset link...' : 'Send reset link'}
                </Button>

                <div className="text-center text-sm text-muted-foreground">
                  Remember your password?{' '}
                  <Link href="/login" className="text-primary hover:underline">
                    Sign in
                  </Link>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
