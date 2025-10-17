'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { workspacesApi } from '@/lib/api/workspaces';
import { Workspace } from '@/types/workspace';
import { Plus, Trash2, Edit2, Check, X, Building2 } from 'lucide-react';

export function WorkspaceSettings() {
  const { toast } = useToast();
  const { currentWorkspace, setCurrentWorkspace } = useWorkspaceStore();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Edit workspace state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');

  // Create workspace state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      setIsLoading(true);
      const data = await workspacesApi.list();
      setWorkspaces(data);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to load workspaces',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!newName.trim()) {
      toast({
        title: 'Error',
        description: 'Workspace name is required',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsLoading(true);
      const workspace = await workspacesApi.create({
        name: newName.trim(),
        description: newDescription.trim() || undefined,
      });

      toast({
        title: 'Workspace Created',
        description: `${workspace.name} has been created`,
      });

      setNewName('');
      setNewDescription('');
      setShowCreateForm(false);
      loadWorkspaces();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to create workspace',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartEdit = (workspace: Workspace) => {
    setEditingId(workspace.id);
    setEditName(workspace.name);
    setEditDescription(workspace.description || '');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditName('');
    setEditDescription('');
  };

  const handleSaveEdit = async (workspaceId: string) => {
    if (!editName.trim()) {
      toast({
        title: 'Error',
        description: 'Workspace name is required',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsLoading(true);
      await workspacesApi.update(workspaceId, {
        name: editName.trim(),
        description: editDescription.trim() || undefined,
      });

      toast({
        title: 'Workspace Updated',
        description: 'Your changes have been saved',
      });

      // Update current workspace if it was edited
      if (currentWorkspace?.id === workspaceId) {
        setCurrentWorkspace({
          ...currentWorkspace,
          name: editName.trim(),
          description: editDescription.trim() || undefined,
        });
      }

      setEditingId(null);
      loadWorkspaces();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update workspace',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteWorkspace = async (workspace: Workspace) => {
    if (workspaces.length === 1) {
      toast({
        title: 'Cannot Delete',
        description: 'You must have at least one workspace',
        variant: 'destructive',
      });
      return;
    }

    if (!confirm(`Delete workspace "${workspace.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setIsLoading(true);
      await workspacesApi.delete(workspace.id);

      toast({
        title: 'Workspace Deleted',
        description: `${workspace.name} has been deleted`,
      });

      // Switch to another workspace if current was deleted
      if (currentWorkspace?.id === workspace.id) {
        const remaining = workspaces.filter((w) => w.id !== workspace.id);
        if (remaining.length > 0) {
          setCurrentWorkspace(remaining[0]);
        }
      }

      loadWorkspaces();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete workspace',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwitchWorkspace = (workspace: Workspace) => {
    setCurrentWorkspace(workspace);
    toast({
      title: 'Workspace Switched',
      description: `Now using ${workspace.name}`,
    });
  };

  return (
    <div className="space-y-6">
      {/* Info */}
      <div className="p-4 bg-muted/50 rounded-lg">
        <p className="text-sm text-muted-foreground">
          Workspaces help you organize newsletters for different brands, clients, or topics.
          Each workspace has its own sources, subscribers, and settings.
        </p>
      </div>

      {/* Current Workspace */}
      {currentWorkspace && (
        <div>
          <h3 className="text-sm font-medium mb-2">Current Workspace</h3>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Building2 className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold">{currentWorkspace.name}</h4>
                      <Badge>Active</Badge>
                    </div>
                    {currentWorkspace.description && (
                      <p className="text-sm text-muted-foreground mt-1">
                        {currentWorkspace.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Create New Workspace */}
      <div>
        <Button onClick={() => setShowCreateForm(!showCreateForm)} variant="default">
          <Plus className="h-4 w-4 mr-2" />
          Create New Workspace
        </Button>

        {showCreateForm && (
          <Card className="mt-4">
            <CardContent className="pt-6 space-y-3">
              <div>
                <label className="text-sm font-medium mb-1 block">Workspace Name *</label>
                <Input
                  placeholder="My Newsletter"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Description (optional)</label>
                <Input
                  placeholder="A brief description of this workspace"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleCreateWorkspace} disabled={!newName.trim() || isLoading}>
                  Create
                </Button>
                <Button onClick={() => setShowCreateForm(false)} variant="outline">
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* All Workspaces */}
      <div>
        <h3 className="text-sm font-medium mb-2">All Workspaces ({workspaces.length})</h3>
        <div className="space-y-2">
          {isLoading && workspaces.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Loading workspaces...
              </CardContent>
            </Card>
          ) : workspaces.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center">
                <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No workspaces found</p>
              </CardContent>
            </Card>
          ) : (
            workspaces.map((workspace) => (
              <Card key={workspace.id}>
                <CardContent className="pt-6">
                  {editingId === workspace.id ? (
                    // Edit Mode
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium mb-1 block">Name</label>
                        <Input
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-1 block">Description</label>
                        <Input
                          value={editDescription}
                          onChange={(e) => setEditDescription(e.target.value)}
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleSaveEdit(workspace.id)}
                          disabled={isLoading}
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Save
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleCancelEdit}
                          disabled={isLoading}
                        >
                          <X className="h-4 w-4 mr-1" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    // View Mode
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="p-2 bg-muted rounded-lg">
                          <Building2 className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold">{workspace.name}</h4>
                            {currentWorkspace?.id === workspace.id && (
                              <Badge>Current</Badge>
                            )}
                          </div>
                          {workspace.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {workspace.description}
                            </p>
                          )}
                          <p className="text-xs text-muted-foreground mt-2">
                            Created {new Date(workspace.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {currentWorkspace?.id !== workspace.id && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSwitchWorkspace(workspace)}
                          >
                            Switch
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleStartEdit(workspace)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        {workspaces.length > 1 && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteWorkspace(workspace)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
