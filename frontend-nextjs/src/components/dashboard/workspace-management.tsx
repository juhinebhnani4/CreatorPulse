'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Building2, Plus, Loader2 } from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';
import { workspacesApi } from '@/lib/api/workspaces';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';

interface WorkspaceManagementProps {
  onWorkspaceCreated?: () => void;
}

export function WorkspaceManagement({ onWorkspaceCreated }: WorkspaceManagementProps) {
  const { toast } = useToast();
  const { setCurrentWorkspace } = useWorkspaceStore();

  const [isCreating, setIsCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [workspaceName, setWorkspaceName] = useState('');
  const [workspaceDescription, setWorkspaceDescription] = useState('');

  const handleCreateWorkspace = async () => {
    if (!workspaceName.trim()) {
      toast({
        title: 'Name Required',
        description: 'Please enter a workspace name',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsCreating(true);

      const newWorkspace = await workspacesApi.create({
        name: workspaceName.trim(),
        description: workspaceDescription.trim() || undefined,
      });

      // Set as current workspace
      setCurrentWorkspace(newWorkspace);

      toast({
        title: '✓ Workspace Created',
        description: `Successfully created "${newWorkspace.name}"`,
      });

      // Reset form
      setWorkspaceName('');
      setWorkspaceDescription('');
      setShowCreateForm(false);

      // Notify parent
      onWorkspaceCreated?.();
    } catch (error: any) {
      console.error('Failed to create workspace:', error);

      // Show detailed error to help debugging
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create workspace';

      toast({
        title: 'Creation Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Card className="border-2 border-primary/20 shadow-lg">
      <CardHeader className="bg-gradient-to-r from-primary/10 to-primary/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-hero flex items-center justify-center">
              <Building2 className="h-5 w-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl">Workspace Management</CardTitle>
              <CardDescription>
                {showCreateForm ? 'Create a new workspace' : 'Manage your workspaces'}
              </CardDescription>
            </div>
          </div>
          {!showCreateForm && (
            <Button
              onClick={() => setShowCreateForm(true)}
              size="sm"
              className="bg-gradient-warm hover:opacity-90"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Workspace
            </Button>
          )}
        </div>
      </CardHeader>

      {showCreateForm && (
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Workspace Name */}
            <div className="space-y-2">
              <Label htmlFor="workspace-name">
                Workspace Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="workspace-name"
                placeholder="e.g., My Workspace, Client A, Tech Newsletter"
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                disabled={isCreating}
                className="border-primary/20 focus:border-primary"
              />
              <p className="text-xs text-muted-foreground">
                Choose a descriptive name for your workspace
              </p>
            </div>

            {/* Workspace Description */}
            <div className="space-y-2">
              <Label htmlFor="workspace-description">Description (Optional)</Label>
              <Textarea
                id="workspace-description"
                placeholder="Describe what this workspace is for..."
                value={workspaceDescription}
                onChange={(e) => setWorkspaceDescription(e.target.value)}
                disabled={isCreating}
                rows={3}
                className="border-primary/20 focus:border-primary resize-none"
              />
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-blue-600 dark:text-blue-400 mt-0.5">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Workspace Benefits:
                  </p>
                  <ul className="mt-2 text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li>• Independent content sources</li>
                    <li>• Separate newsletter drafts</li>
                    <li>• Isolated subscriber lists</li>
                    <li>• Perfect for agencies managing multiple clients</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-2">
              <Button
                onClick={handleCreateWorkspace}
                disabled={isCreating || !workspaceName.trim()}
                className="flex-1 bg-gradient-warm hover:opacity-90"
              >
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Workspace
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false);
                  setWorkspaceName('');
                  setWorkspaceDescription('');
                }}
                disabled={isCreating}
              >
                Cancel
              </Button>
            </div>
          </div>
        </CardContent>
      )}

      {!showCreateForm && (
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
              <Building2 className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground mb-4">
              Create additional workspaces to manage multiple newsletters or clients
            </p>
            <Button
              onClick={() => setShowCreateForm(true)}
              variant="outline"
              className="border-primary/40 hover:bg-primary/5"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create New Workspace
            </Button>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
