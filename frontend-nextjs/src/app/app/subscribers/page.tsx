'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Users,
  UserPlus,
  Upload,
  Download,
  Trash2,
  Loader2,
  Search,
  Mail,
  Calendar,
  UserCheck,
  UserX,
  UserMinus
} from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';
import { AppHeader } from '@/components/layout/app-header';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { subscribersApi } from '@/lib/api/subscribers';
import { Subscriber, SubscriberStats } from '@/types/subscriber';
import { AddSubscriberModal } from '@/components/modals/add-subscriber-modal';
import { ImportCSVModal } from '@/components/modals/import-csv-modal';

export default function SubscribersPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const { currentWorkspace } = useWorkspaceStore();
  const [isMounted, setIsMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [stats, setStats] = useState<SubscriberStats | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted || !_hasHydrated) return;

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (!currentWorkspace) {
      return;
    }

    fetchData();
  }, [isAuthenticated, isMounted, _hasHydrated, currentWorkspace, statusFilter, router]);

  const fetchData = async () => {
    if (!currentWorkspace) return;

    try {
      setIsLoading(true);

      const [subscriberData, statsData] = await Promise.all([
        subscribersApi.list(
          currentWorkspace.id,
          statusFilter === 'all' ? undefined : statusFilter
        ),
        subscribersApi.getStats(currentWorkspace.id)
      ]);

      setSubscribers(subscriberData.subscribers || []);
      setStats(statsData);
    } catch (error: any) {
      console.error('Failed to fetch subscribers:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to load subscribers',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSelection = (id: string) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === filteredSubscribers.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredSubscribers.map(s => s.id));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    if (!confirm(`Are you sure you want to delete ${selectedIds.length} subscriber${selectedIds.length > 1 ? 's' : ''}? This action cannot be undone.`)) {
      return;
    }

    try {
      setIsDeleting(true);

      await Promise.all(selectedIds.map(id => subscribersApi.delete(id)));

      toast({
        title: '✓ Subscribers Deleted',
        description: `${selectedIds.length} subscriber${selectedIds.length > 1 ? 's' : ''} removed successfully`,
      });

      setSubscribers(subscribers.filter(s => !selectedIds.includes(s.id)));
      setSelectedIds([]);

      // Refresh stats
      if (currentWorkspace) {
        const statsData = await subscribersApi.getStats(currentWorkspace.id);
        setStats(statsData);
      }
    } catch (error: any) {
      toast({
        title: 'Bulk Delete Failed',
        description: error.message || 'Could not delete all subscribers',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this subscriber? This action cannot be undone.')) {
      return;
    }

    try {
      await subscribersApi.delete(id);

      toast({
        title: '✓ Subscriber Deleted',
        description: 'The subscriber has been removed',
      });

      setSubscribers(subscribers.filter(s => s.id !== id));

      // Refresh stats
      if (currentWorkspace) {
        const statsData = await subscribersApi.getStats(currentWorkspace.id);
        setStats(statsData);
      }
    } catch (error: any) {
      toast({
        title: 'Failed to Delete',
        description: error.message || 'Could not delete subscriber',
        variant: 'destructive',
      });
    }
  };

  const handleAddSubscriber = async (email: string, name?: string): Promise<Subscriber> => {
    if (!currentWorkspace) throw new Error('No workspace selected');

    const subscriber = await subscribersApi.create({
      workspace_id: currentWorkspace.id,
      email,
      name,
      source: 'manual',
    });

    toast({
      title: '✓ Subscriber Added',
      description: `${email} has been added to your list`,
    });

    // Add to local state
    setSubscribers([subscriber, ...subscribers]);

    // Refresh stats
    const statsData = await subscribersApi.getStats(currentWorkspace.id);
    setStats(statsData);

    return subscriber;
  };

  const handleImportSubscribers = async (
    importedSubs: Array<{ email: string; name?: string }>
  ) => {
    if (!currentWorkspace) throw new Error('No workspace selected');

    const result = await subscribersApi.bulkCreate({
      workspace_id: currentWorkspace.id,
      subscribers: importedSubs,
    });

    // Refresh the list
    await fetchData();

    return result;
  };

  const handleExportCSV = () => {
    const csvData = filteredSubscribers.map(s => ({
      email: s.email,
      name: s.name || '',
      status: s.status,
      subscribed_at: new Date(s.subscribed_at).toLocaleDateString(),
      source: s.source || '',
    }));

    const headers = Object.keys(csvData[0] || {}).join(',');
    const rows = csvData.map(row => Object.values(row).join(','));
    const csv = [headers, ...rows].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `subscribers-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();

    toast({
      title: '✓ Export Complete',
      description: `${filteredSubscribers.length} subscribers exported to CSV`,
    });
  };

  if (!isMounted || !_hasHydrated || !isAuthenticated) {
    return null;
  }

  // Filter subscribers by search query
  const filteredSubscribers = subscribers.filter(sub => {
    const matchesSearch = searchQuery === '' ||
      sub.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sub.name?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-10 animate-slide-up">
          <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Subscribers
          </h1>
          <p className="text-lg text-muted-foreground">Manage your newsletter subscribers and mailing lists</p>
        </div>

        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-slide-up" style={{ animationDelay: '50ms' }}>
            <Card className="p-4 bg-gradient-warm/10 border-none shadow-md hover:-translate-y-1 transition-transform">
              <div className="flex items-center gap-3 mb-2">
                <Users className="h-5 w-5 text-primary" />
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Total</p>
              </div>
              <p className="text-3xl font-bold">{stats.total_subscribers}</p>
            </Card>

            <Card className="p-4 bg-green-500/10 border-none shadow-md hover:-translate-y-1 transition-transform">
              <div className="flex items-center gap-3 mb-2">
                <UserCheck className="h-5 w-5 text-green-600" />
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Active</p>
              </div>
              <p className="text-3xl font-bold text-green-600">{stats.active_subscribers}</p>
            </Card>

            <Card className="p-4 bg-yellow-500/10 border-none shadow-md hover:-translate-y-1 transition-transform">
              <div className="flex items-center gap-3 mb-2">
                <UserMinus className="h-5 w-5 text-yellow-600" />
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Unsubscribed</p>
              </div>
              <p className="text-3xl font-bold text-yellow-600">{stats.unsubscribed}</p>
            </Card>

            <Card className="p-4 bg-red-500/10 border-none shadow-md hover:-translate-y-1 transition-transform">
              <div className="flex items-center gap-3 mb-2">
                <UserX className="h-5 w-5 text-red-600" />
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Bounced</p>
              </div>
              <p className="text-3xl font-bold text-red-600">{stats.bounced}</p>
            </Card>
          </div>
        )}

        {/* Actions Bar */}
        <div className="mb-6 flex flex-wrap gap-3 items-center animate-slide-up" style={{ animationDelay: '100ms' }}>
          {/* Bulk Actions */}
          {filteredSubscribers.length > 0 && (
            <div className="flex items-center gap-3">
              <Checkbox
                checked={selectedIds.length === filteredSubscribers.length && filteredSubscribers.length > 0}
                onCheckedChange={toggleSelectAll}
                aria-label="Select all subscribers"
              />
              <span className="text-sm text-muted-foreground">
                {selectedIds.length > 0 ? `${selectedIds.length} selected` : 'Select all'}
              </span>
              {selectedIds.length > 0 && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleBulkDelete}
                  disabled={isDeleting}
                  className="rounded-xl"
                >
                  {isDeleting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Selected
                    </>
                  )}
                </Button>
              )}
            </div>
          )}

          <div className="flex-1" />

          {/* Action Buttons */}
          <Button
            onClick={handleExportCSV}
            variant="outline"
            className="rounded-xl"
            disabled={filteredSubscribers.length === 0}
          >
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>

          <Button
            onClick={() => setShowImportModal(true)}
            variant="outline"
            className="rounded-xl"
          >
            <Upload className="h-4 w-4 mr-2" />
            Import CSV
          </Button>

          <Button
            onClick={() => setShowAddModal(true)}
            className="rounded-xl bg-gradient-hero hover:opacity-90"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            Add Subscriber
          </Button>
        </div>

        {/* Filters Bar */}
        <div className="mb-6 flex flex-wrap gap-3 items-center animate-slide-up" style={{ animationDelay: '150ms' }}>
          <div className="relative flex-1 min-w-[200px] max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by email or name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 rounded-xl"
            />
          </div>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px] rounded-xl border-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Subscribers</SelectItem>
              <SelectItem value="active">Active Only</SelectItem>
              <SelectItem value="unsubscribed">Unsubscribed</SelectItem>
              <SelectItem value="bounced">Bounced</SelectItem>
            </SelectContent>
          </Select>

          <div className="text-sm text-muted-foreground">
            {filteredSubscribers.length} {filteredSubscribers.length === 1 ? 'subscriber' : 'subscribers'}
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Subscribers Table */}
        {!isLoading && filteredSubscribers.length > 0 && (
          <Card className="border-0 shadow-lg overflow-hidden animate-slide-up" style={{ animationDelay: '200ms' }}>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 text-left w-10"></th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Name</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Source</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Subscribed</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Last Sent</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold w-32">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredSubscribers.map((subscriber, index) => {
                    const subscribedDate = new Date(subscriber.subscribed_at);
                    const lastSentDate = subscriber.last_sent_at ? new Date(subscriber.last_sent_at) : null;

                    return (
                      <tr key={subscriber.id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3">
                          <Checkbox
                            checked={selectedIds.includes(subscriber.id)}
                            onCheckedChange={() => toggleSelection(subscriber.id)}
                            aria-label={`Select ${subscriber.email}`}
                          />
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">{subscriber.email}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-muted-foreground">{subscriber.name || '-'}</span>
                        </td>
                        <td className="px-4 py-3">
                          <Badge
                            className={`border-0 ${
                              subscriber.status === 'active'
                                ? 'bg-green-500/10 text-green-600'
                                : subscriber.status === 'unsubscribed'
                                ? 'bg-yellow-500/10 text-yellow-600'
                                : 'bg-red-500/10 text-red-600'
                            }`}
                          >
                            {subscriber.status === 'active' ? '✓ Active' : subscriber.status === 'unsubscribed' ? 'Unsubscribed' : 'Bounced'}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-muted-foreground capitalize">{subscriber.source || 'manual'}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            {subscribedDate.toLocaleDateString()}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-muted-foreground">
                            {lastSentDate ? lastSentDate.toLocaleDateString() : 'Never'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(subscriber.id)}
                            className="hover:bg-destructive hover:text-destructive-foreground"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && filteredSubscribers.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                <Users className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                {searchQuery || statusFilter !== 'all' ? 'No subscribers found' : 'No subscribers yet'}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {searchQuery || statusFilter !== 'all'
                  ? 'Try adjusting your filters or search query'
                  : 'Start building your audience by adding subscribers'}
              </p>
              {!searchQuery && statusFilter === 'all' && (
                <Button onClick={() => setShowAddModal(true)}>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Your First Subscriber
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </main>

      {/* Modals */}
      <AddSubscriberModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddSubscriber}
      />
      <ImportCSVModal
        open={showImportModal}
        onClose={() => setShowImportModal(false)}
        onImport={handleImportSubscribers}
      />
    </div>
  );
}
