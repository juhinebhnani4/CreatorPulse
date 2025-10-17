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
import { Textarea } from '@/components/ui/textarea';
import { Upload, FileText, CheckCircle2, XCircle } from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';
import { subscribersApi } from '@/lib/api/subscribers';

interface ImportSubscribersModalProps {
  open: boolean;
  onClose: () => void;
  workspaceId: string;
  onSuccess: () => void;
}

export function ImportSubscribersModal({
  open,
  onClose,
  workspaceId,
  onSuccess,
}: ImportSubscribersModalProps) {
  const { toast } = useToast();
  const [csvText, setCsvText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{
    created_count: number;
    failed_count: number;
    failed: Array<{ email: string; error: string }>;
  } | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setCsvText(text);
    };
    reader.readAsText(file);
  };

  const handleImport = async () => {
    if (!csvText.trim()) {
      toast({
        title: 'No Data',
        description: 'Please paste CSV data or upload a file',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      // Parse CSV
      const parsedSubscribers = subscribersApi.parseCSV(csvText);

      if (parsedSubscribers.length === 0) {
        toast({
          title: 'No Valid Data',
          description: 'Could not find any valid email addresses in the CSV',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      // Bulk import
      const importResult = await subscribersApi.bulkCreate({
        workspace_id: workspaceId,
        subscribers: parsedSubscribers,
      });

      setResult(importResult);

      toast({
        title: 'Import Complete',
        description: `Successfully imported ${importResult.created_count} subscribers`,
      });

      if (importResult.failed_count === 0) {
        // Auto-close if all successful
        setTimeout(() => {
          handleClose();
          onSuccess();
        }, 2000);
      }
    } catch (error: any) {
      toast({
        title: 'Import Failed',
        description: error.message || 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setCsvText('');
    setResult(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="h-6 w-6 text-primary" />
            </div>
            <div>
              <DialogTitle>Import Subscribers</DialogTitle>
              <DialogDescription>Upload a CSV file or paste CSV data</DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* File Upload */}
          <div>
            <label
              htmlFor="csv-file"
              className="flex items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
            >
              <div className="flex flex-col items-center gap-2">
                <FileText className="h-8 w-8 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Click to upload CSV file
                </span>
              </div>
              <input
                id="csv-file"
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleFileUpload}
                disabled={isLoading}
              />
            </label>
          </div>

          {/* CSV Format Info */}
          <div className="bg-muted p-3 rounded-lg text-sm">
            <p className="font-medium mb-1">CSV Format:</p>
            <code className="block text-xs">
              email,name
              <br />
              user@example.com,John Doe
              <br />
              another@example.com,Jane Smith
            </code>
            <p className="mt-2 text-muted-foreground text-xs">
              The name column is optional. Email-only lists are also supported.
            </p>
          </div>

          {/* Or Divider */}
          <div className="flex items-center gap-4">
            <div className="flex-1 border-t"></div>
            <span className="text-sm text-muted-foreground">OR</span>
            <div className="flex-1 border-t"></div>
          </div>

          {/* Text Area */}
          <div>
            <Textarea
              placeholder="Paste CSV data here..."
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              className="min-h-[150px] font-mono text-sm"
              disabled={isLoading}
            />
          </div>

          {/* Import Results */}
          {result && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>
                  Successfully imported: <strong>{result.created_count}</strong>
                </span>
              </div>

              {result.failed_count > 0 && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <XCircle className="h-4 w-4 text-red-600" />
                    <span>
                      Failed: <strong>{result.failed_count}</strong>
                    </span>
                  </div>
                  <div className="bg-red-50 dark:bg-red-950/30 p-3 rounded-lg max-h-32 overflow-y-auto">
                    {result.failed.map((fail, idx) => (
                      <div key={idx} className="text-xs text-red-800 dark:text-red-200">
                        {fail.email}: {fail.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={handleClose} disabled={isLoading}>
            {result && result.failed_count === 0 ? 'Done' : 'Cancel'}
          </Button>
          {(!result || result.failed_count > 0) && (
            <Button onClick={handleImport} disabled={isLoading}>
              {isLoading ? 'Importing...' : 'Import Subscribers'}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
