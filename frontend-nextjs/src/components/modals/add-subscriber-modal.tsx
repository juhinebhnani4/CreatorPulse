'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { UserPlus, Loader2 } from 'lucide-react';
import { Subscriber } from '@/types/subscriber';

interface AddSubscriberModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (email: string, name?: string) => Promise<Subscriber>;
}

export function AddSubscriberModal({ open, onClose, onAdd }: AddSubscriberModalProps) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      setIsAdding(true);
      await onAdd(email.trim(), name.trim() || undefined);

      // Reset form
      setEmail('');
      setName('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to add subscriber');
    } finally {
      setIsAdding(false);
    }
  };

  const handleClose = () => {
    if (!isAdding) {
      setEmail('');
      setName('');
      setError('');
      onClose();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <UserPlus className="h-6 w-6 text-primary" />
            Add Subscriber
          </DialogTitle>
          <DialogDescription>
            Add a new subscriber to your mailing list manually
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 py-4">
          {/* Email Field */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-semibold">
              Email Address <span className="text-destructive">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="subscriber@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isAdding}
              className="rounded-xl"
              autoFocus
            />
          </div>

          {/* Name Field */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-semibold">
              Name <span className="text-muted-foreground text-xs">(Optional)</span>
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isAdding}
              className="rounded-xl"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-xl bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isAdding}
              className="rounded-xl"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isAdding || !email.trim()}
              className="rounded-xl bg-gradient-hero hover:opacity-90"
            >
              {isAdding ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Subscriber
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
