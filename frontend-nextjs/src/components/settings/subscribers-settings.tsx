'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { subscribersApi, Subscriber } from '@/lib/api/subscribers';
import { Upload, Download, UserPlus, Trash2, Search, Mail } from 'lucide-react';

export function SubscribersSettings() {
  const { toast } = useToast();
  const { currentWorkspace } = useWorkspaceStore();
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [stats, setStats] = useState({ total: 0, active: 0, unsubscribed: 0, bounced: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Add subscriber form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [newName, setNewName] = useState('');

  // Import CSV
  const [showImport, setShowImport] = useState(false);
  const [csvText, setCsvText] = useState('');

  useEffect(() => {
    if (currentWorkspace?.id) {
      loadSubscribers();
      loadStats();
    }
  }, [currentWorkspace?.id]);

  const loadSubscribers = async () => {
    if (!currentWorkspace?.id) return;

    try {
      setIsLoading(true);
      const data = await subscribersApi.list(currentWorkspace.id);
      setSubscribers(data.subscribers);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to load subscribers',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    if (!currentWorkspace?.id) return;

    try {
      const data = await subscribersApi.getStats(currentWorkspace.id);
      setStats(data);
    } catch (error: any) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleAddSubscriber = async () => {
    if (!currentWorkspace?.id || !newEmail) return;

    try {
      await subscribersApi.create({
        workspace_id: currentWorkspace.id,
        email: newEmail,
        name: newName || undefined,
        source: 'manual',
      });

      toast({
        title: 'Subscriber Added',
        description: `${newEmail} has been added to your list`,
      });

      setNewEmail('');
      setNewName('');
      setShowAddForm(false);
      loadSubscribers();
      loadStats();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to add subscriber',
        variant: 'destructive',
      });
    }
  };

  const handleImportCSV = async () => {
    if (!currentWorkspace?.id || !csvText.trim()) return;

    try {
      setIsLoading(true);

      // Parse CSV
      const parsed = subscribersApi.parseCSV(csvText);

      if (parsed.length === 0) {
        toast({
          title: 'No Subscribers Found',
          description: 'Please check your CSV format',
          variant: 'destructive',
        });
        return;
      }

      // Bulk import
      const result = await subscribersApi.bulkCreate({
        workspace_id: currentWorkspace.id,
        subscribers: parsed,
      });

      toast({
        title: 'Import Complete',
        description: `Successfully imported ${result.created_count} subscribers. ${result.failed_count} failed.`,
      });

      if (result.failed_count > 0) {
        console.error('Failed subscribers:', result.failed);
      }

      setCsvText('');
      setShowImport(false);
      loadSubscribers();
      loadStats();
    } catch (error: any) {
      toast({
        title: 'Import Failed',
        description: error.message || 'Failed to import subscribers',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportCSV = () => {
    const csv = ['Email,Name,Status,Subscribed At']
      .concat(
        subscribers.map((sub) =>
          [
            sub.email,
            sub.name || '',
            sub.status,
            new Date(sub.subscribed_at).toLocaleDateString(),
          ].join(',')
        )
      )
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `subscribers-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    toast({
      title: 'Export Complete',
      description: `Exported ${subscribers.length} subscribers`,
    });
  };

  const handleDeleteSubscriber = async (subscriberId: string, email: string) => {
    if (!confirm(`Delete ${email} from your subscriber list?`)) return;

    try {
      await subscribersApi.delete(subscriberId);

      toast({
        title: 'Subscriber Deleted',
        description: `${email} has been removed`,
      });

      loadSubscribers();
      loadStats();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete subscriber',
        variant: 'destructive',
      });
    }
  };

  const filteredSubscribers = subscribers.filter(
    (sub) =>
      sub.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sub.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 border rounded-lg">
          <p className="text-sm text-muted-foreground">Total</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="p-4 border rounded-lg">
          <p className="text-sm text-muted-foreground">Active</p>
          <p className="text-2xl font-bold text-green-600">{stats.active}</p>
        </div>
        <div className="p-4 border rounded-lg">
          <p className="text-sm text-muted-foreground">Unsubscribed</p>
          <p className="text-2xl font-bold text-orange-600">{stats.unsubscribed}</p>
        </div>
        <div className="p-4 border rounded-lg">
          <p className="text-sm text-muted-foreground">Bounced</p>
          <p className="text-2xl font-bold text-red-600">{stats.bounced}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2">
        <Button onClick={() => setShowAddForm(!showAddForm)} variant="default">
          <UserPlus className="h-4 w-4 mr-2" />
          Add Subscriber
        </Button>
        <Button onClick={() => setShowImport(!showImport)} variant="outline">
          <Upload className="h-4 w-4 mr-2" />
          Import CSV
        </Button>
        <Button onClick={handleExportCSV} variant="outline" disabled={subscribers.length === 0}>
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Add Subscriber Form */}
      {showAddForm && (
        <div className="p-4 border rounded-lg space-y-3">
          <h3 className="font-semibold">Add Subscriber</h3>
          <div className="grid md:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Email *</label>
              <Input
                type="email"
                placeholder="subscriber@example.com"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Name (optional)</label>
              <Input
                type="text"
                placeholder="John Doe"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleAddSubscriber} disabled={!newEmail}>
              Add
            </Button>
            <Button onClick={() => setShowAddForm(false)} variant="outline">
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Import CSV Form */}
      {showImport && (
        <div className="p-4 border rounded-lg space-y-3">
          <h3 className="font-semibold">Import from CSV</h3>
          <p className="text-sm text-muted-foreground">
            Format: One subscriber per line. Either "email" or "email,name"
          </p>
          <p className="text-xs text-muted-foreground">
            Example:<br />
            john@example.com,John Doe<br />
            jane@example.com,Jane Smith
          </p>
          <textarea
            className="w-full min-h-[200px] p-3 border rounded-md font-mono text-sm"
            placeholder="email@example.com,Name&#10;another@example.com,Another Name"
            value={csvText}
            onChange={(e) => setCsvText(e.target.value)}
          />
          <div className="flex gap-2">
            <Button onClick={handleImportCSV} disabled={!csvText.trim() || isLoading}>
              {isLoading ? 'Importing...' : 'Import'}
            </Button>
            <Button onClick={() => setShowImport(false)} variant="outline">
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search subscribers..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Subscribers List */}
      <div className="border rounded-lg">
        <div className="max-h-[400px] overflow-y-auto">
          {isLoading && subscribers.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">Loading subscribers...</div>
          ) : filteredSubscribers.length === 0 ? (
            <div className="p-8 text-center">
              <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
              <p className="text-muted-foreground">
                {searchQuery ? 'No subscribers found' : 'No subscribers yet'}
              </p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-muted sticky top-0">
                <tr>
                  <th className="text-left p-3 font-medium text-sm">Email</th>
                  <th className="text-left p-3 font-medium text-sm">Name</th>
                  <th className="text-left p-3 font-medium text-sm">Status</th>
                  <th className="text-left p-3 font-medium text-sm">Subscribed</th>
                  <th className="text-right p-3 font-medium text-sm">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSubscribers.map((subscriber) => (
                  <tr key={subscriber.id} className="border-t hover:bg-muted/50">
                    <td className="p-3 text-sm">{subscriber.email}</td>
                    <td className="p-3 text-sm">{subscriber.name || '-'}</td>
                    <td className="p-3 text-sm">
                      <Badge
                        variant={
                          subscriber.status === 'active'
                            ? 'default'
                            : subscriber.status === 'unsubscribed'
                            ? 'secondary'
                            : 'destructive'
                        }
                      >
                        {subscriber.status}
                      </Badge>
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">
                      {new Date(subscriber.subscribed_at).toLocaleDateString()}
                    </td>
                    <td className="p-3 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteSubscriber(subscriber.id, subscriber.email)}
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {filteredSubscribers.length > 0 && (
        <p className="text-sm text-muted-foreground text-center">
          Showing {filteredSubscribers.length} of {subscribers.length} subscribers
        </p>
      )}
    </div>
  );
}
