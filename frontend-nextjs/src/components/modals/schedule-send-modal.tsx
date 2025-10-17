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
import { Clock } from 'lucide-react';

interface ScheduleSendModalProps {
  open: boolean;
  onClose: () => void;
  onSchedule: (scheduledAt: Date) => Promise<void>;
  isLoading?: boolean;
}

export function ScheduleSendModal({
  open,
  onClose,
  onSchedule,
  isLoading = false,
}: ScheduleSendModalProps) {
  const [selectedOption, setSelectedOption] = useState<'1hour' | 'tomorrow' | 'custom'>('tomorrow');
  const [customDate, setCustomDate] = useState('');
  const [customTime, setCustomTime] = useState('');

  const now = new Date();
  const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(8, 0, 0, 0);

  const handleSchedule = async () => {
    let scheduledDate: Date;

    switch (selectedOption) {
      case '1hour':
        scheduledDate = oneHourLater;
        break;
      case 'tomorrow':
        scheduledDate = tomorrow;
        break;
      case 'custom':
        if (!customDate || !customTime) {
          return;
        }
        scheduledDate = new Date(`${customDate}T${customTime}`);
        break;
    }

    await onSchedule(scheduledDate);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-950 flex items-center justify-center">
              <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <DialogTitle>Schedule Newsletter</DialogTitle>
              <DialogDescription>Choose when to send your newsletter</DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4 space-y-3">
          {/* 1 Hour Option */}
          <button
            onClick={() => setSelectedOption('1hour')}
            className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${
              selectedOption === '1hour'
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            }`}
          >
            <div className="flex items-center gap-2">
              <div
                className={`w-4 h-4 rounded-full border-2 ${
                  selectedOption === '1hour'
                    ? 'border-primary bg-primary'
                    : 'border-muted-foreground'
                }`}
              >
                {selectedOption === '1hour' && (
                  <div className="w-full h-full rounded-full bg-background scale-50" />
                )}
              </div>
              <div>
                <p className="font-medium">In 1 hour</p>
                <p className="text-sm text-muted-foreground">
                  {oneHourLater.toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true,
                  })}{' '}
                  today
                </p>
              </div>
            </div>
          </button>

          {/* Tomorrow Option */}
          <button
            onClick={() => setSelectedOption('tomorrow')}
            className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${
              selectedOption === 'tomorrow'
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            }`}
          >
            <div className="flex items-center gap-2">
              <div
                className={`w-4 h-4 rounded-full border-2 ${
                  selectedOption === 'tomorrow'
                    ? 'border-primary bg-primary'
                    : 'border-muted-foreground'
                }`}
              >
                {selectedOption === 'tomorrow' && (
                  <div className="w-full h-full rounded-full bg-background scale-50" />
                )}
              </div>
              <div>
                <p className="font-medium">Tomorrow at 8:00 AM</p>
                <p className="text-sm text-muted-foreground">
                  {tomorrow.toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'short',
                    day: 'numeric',
                  })}
                </p>
              </div>
            </div>
          </button>

          {/* Custom Option */}
          <button
            onClick={() => setSelectedOption('custom')}
            className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${
              selectedOption === 'custom'
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            }`}
          >
            <div className="flex items-start gap-2">
              <div
                className={`w-4 h-4 rounded-full border-2 mt-1 ${
                  selectedOption === 'custom'
                    ? 'border-primary bg-primary'
                    : 'border-muted-foreground'
                }`}
              >
                {selectedOption === 'custom' && (
                  <div className="w-full h-full rounded-full bg-background scale-50" />
                )}
              </div>
              <div className="flex-1">
                <p className="font-medium mb-2">Custom date & time</p>
                {selectedOption === 'custom' && (
                  <div className="space-y-2">
                    <Input
                      type="date"
                      value={customDate}
                      onChange={(e) => setCustomDate(e.target.value)}
                      min={now.toISOString().split('T')[0]}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <Input
                      type="time"
                      value={customTime}
                      onChange={(e) => setCustomTime(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                )}
              </div>
            </div>
          </button>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSchedule} disabled={isLoading}>
            {isLoading ? 'Scheduling...' : 'Schedule Send'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
