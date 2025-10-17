'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Upload, Loader2, CheckCircle2, XCircle, Download } from 'lucide-react';
import { BulkCreateResponse } from '@/types/subscriber';

interface ImportCSVModalProps {
  open: boolean;
  onClose: () => void;
  onImport: (subscribers: Array<{ email: string; name?: string }>) => Promise<BulkCreateResponse>;
}

export function ImportCSVModal({ open, onClose, onImport }: ImportCSVModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [result, setResult] = useState<BulkCreateResponse | null>(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      setFile(selectedFile);
      setError('');
      setResult(null);
    }
  };

  const parseCSV = (text: string): Array<{ email: string; name?: string }> => {
    const lines = text.split('\n').filter(line => line.trim());
    const subscribers: Array<{ email: string; name?: string }> = [];

    // Detect header row
    const hasHeader = lines[0].toLowerCase().includes('email');
    const startIndex = hasHeader ? 1 : 0;

    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      const columns = line.split(',').map(col => col.trim().replace(/^["']|["']$/g, ''));

      if (columns.length > 0) {
        const email = columns[0];
        const name = columns.length > 1 ? columns[1] : undefined;

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailRegex.test(email)) {
          subscribers.push({ email, name });
        }
      }
    }

    return subscribers;
  };

  const handleImport = async () => {
    if (!file) return;

    try {
      setIsImporting(true);
      setError('');

      const text = await file.text();
      const subscribers = parseCSV(text);

      if (subscribers.length === 0) {
        setError('No valid subscribers found in CSV file');
        setIsImporting(false);
        return;
      }

      const importResult = await onImport(subscribers);
      setResult(importResult);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.message || 'Failed to import subscribers');
    } finally {
      setIsImporting(false);
    }
  };

  const handleClose = () => {
    if (!isImporting) {
      setFile(null);
      setError('');
      setResult(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onClose();
    }
  };

  const downloadTemplate = () => {
    const csvContent = 'email,name\nsubscriber@example.com,John Doe\nuser@example.com,Jane Smith';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'subscriber-import-template.csv';
    a.click();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Upload className="h-6 w-6 text-primary" />
            Import Subscribers from CSV
          </DialogTitle>
          <DialogDescription>
            Upload a CSV file with subscriber emails and names
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Template Download */}
          <div className="p-4 rounded-xl bg-muted/50 border border-border">
            <p className="text-sm mb-3">
              <strong>CSV Format:</strong> First column should be email, second column (optional) should be name
            </p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={downloadTemplate}
              className="rounded-xl"
            >
              <Download className="h-4 w-4 mr-2" />
              Download Template
            </Button>
          </div>

          {/* File Upload */}
          <div className="space-y-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-upload"
            />
            <label
              htmlFor="csv-upload"
              className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-border rounded-xl cursor-pointer hover:bg-muted/30 transition-colors"
            >
              <Upload className="h-8 w-8 text-muted-foreground mb-2" />
              <span className="text-sm text-muted-foreground">
                {file ? file.name : 'Click to upload CSV file'}
              </span>
              <span className="text-xs text-muted-foreground mt-1">
                or drag and drop
              </span>
            </label>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-xl bg-destructive/10 text-destructive text-sm flex items-center gap-2">
              <XCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          {/* Import Result */}
          {result && (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-success/10 border border-success/20">
                <div className="flex items-center gap-2 text-success mb-2">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="font-semibold">Import Complete!</span>
                </div>
                <div className="space-y-1 text-sm">
                  <p><strong>Successfully added:</strong> {result.created_count} subscriber{result.created_count !== 1 ? 's' : ''}</p>
                  {result.failed_count > 0 && (
                    <p className="text-destructive"><strong>Failed:</strong> {result.failed_count} subscriber{result.failed_count !== 1 ? 's' : ''}</p>
                  )}
                </div>
              </div>

              {result.failed && result.failed.length > 0 && (
                <div className="p-3 rounded-xl bg-muted/50 max-h-32 overflow-y-auto">
                  <p className="text-sm font-semibold mb-2">Failed Imports:</p>
                  <ul className="text-xs space-y-1 text-muted-foreground">
                    {result.failed.map((fail, idx) => (
                      <li key={idx}>
                        {fail.email}: {fail.error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isImporting}
              className="rounded-xl"
            >
              {result ? 'Done' : 'Cancel'}
            </Button>
            {!result && (
              <Button
                onClick={handleImport}
                disabled={!file || isImporting}
                className="rounded-xl bg-gradient-hero hover:opacity-90"
              >
                {isImporting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Import Subscribers
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
