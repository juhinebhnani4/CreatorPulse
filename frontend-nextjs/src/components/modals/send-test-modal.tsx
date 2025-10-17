'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Mail } from 'lucide-react';

interface SendTestModalProps {
  open: boolean;
  onClose: () => void;
  onSend: (email: string) => Promise<void>;
  isLoading?: boolean;
}

export function SendTestModal({
  open,
  onClose,
  onSend,
  isLoading = false,
}: SendTestModalProps) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleSend = async () => {
    setError('');

    if (!email) {
      setError('Email address is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      await onSend(email);
      setEmail(''); // Clear on success
    } catch (err) {
      // Error handled by parent
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Mail className="h-6 w-6 text-primary" />
            </div>
            <div>
              <DialogTitle>Send Test Email</DialogTitle>
              <DialogDescription>Preview your newsletter before sending to subscribers</DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4">
          <div className="space-y-2">
            <label htmlFor="test-email" className="text-sm font-medium">
              Test Email Address
            </label>
            <Input
              id="test-email"
              type="email"
              placeholder="your.email@example.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setError('');
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isLoading) {
                  handleSend();
                }
              }}
              disabled={isLoading}
              className={error ? 'border-red-500' : ''}
            />
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>

          <div className="mt-4 p-3 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              A copy of your newsletter will be sent to this email address for review.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSend} disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send Test Email'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
