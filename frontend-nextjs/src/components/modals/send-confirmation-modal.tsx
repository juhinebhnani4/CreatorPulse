'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

interface SendConfirmationModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  newsletterId?: string;
  subscriberCount: number;
  subject?: string;
  isLoading?: boolean;
}

export function SendConfirmationModal({
  open,
  onClose,
  onConfirm,
  newsletterId,
  subscriberCount,
  subject = 'Your newsletter',
  isLoading = false,
}: SendConfirmationModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-950 flex items-center justify-center">
              <AlertTriangle className="h-6 w-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <DialogTitle>Send Newsletter?</DialogTitle>
              <DialogDescription>This action cannot be undone</DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4">
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Subject</p>
              <p className="text-sm">{subject}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Recipients</p>
              <p className="text-sm">
                {subscriberCount.toLocaleString()} {subscriberCount === 1 ? 'subscriber' : 'subscribers'}
              </p>
            </div>
          </div>

          <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-950/50 border border-orange-200 dark:border-orange-800 rounded-lg">
            <p className="text-sm text-orange-900 dark:text-orange-100">
              <strong>Warning:</strong> Once sent, you cannot recall this newsletter. Make sure you've reviewed
              all content carefully.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={onConfirm} disabled={isLoading}>
            {isLoading ? 'Sending...' : `Send to ${subscriberCount.toLocaleString()} Subscribers`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
