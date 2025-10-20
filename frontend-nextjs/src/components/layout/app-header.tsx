'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { authApi } from '@/lib/api/auth';
import { workspacesApi } from '@/lib/api/workspaces';
import { Home, Settings, ChevronDown, FileText, Building2, Check } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { Workspace } from '@/types/workspace';

export function AppHeader() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const { currentWorkspace, setCurrentWorkspace } = useWorkspaceStore();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);

  // Fetch user's workspaces
  useEffect(() => {
    if (user) {
      workspacesApi.list().then(setWorkspaces).catch(console.error);
    }
  }, [user]);

  const handleLogout = () => {
    authApi.logout();
    clearAuth();
    router.push('/login');
  };

  const handleWorkspaceSwitch = (workspace: Workspace) => {
    setCurrentWorkspace(workspace);
    // Reload current page to refresh data with new workspace
    router.refresh();
  };

  const navItems = [
    { href: '/app', label: 'Dashboard', icon: Home },
    { href: '/app/content', label: 'Content', icon: FileText },
    { href: '/app/settings', label: 'Settings', icon: Settings },
  ];

  const isActive = (href: string) => {
    if (href === '/app') {
      return pathname === '/app';
    }
    return pathname.startsWith(href);
  };

  return (
    <header className="border-b bg-background/80 backdrop-blur-lg sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo with gradient */}
          <div className="flex items-center gap-8">
            <button
              onClick={() => router.push('/app')}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity group"
            >
              <div className="h-10 w-10 rounded-xl bg-gradient-hero flex items-center justify-center text-white font-bold text-lg shadow-md group-hover:shadow-lg transition-shadow">
                CP
              </div>
              <span className="text-2xl font-bold text-gradient">CreatorPulse</span>
            </button>

            {/* Navigation with improved styling */}
            <nav className="hidden md:flex items-center gap-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);

                return (
                  <Button
                    key={item.href}
                    variant={active ? 'secondary' : 'ghost'}
                    size="default"
                    onClick={() => router.push(item.href)}
                    className={`gap-2 rounded-xl ${
                      active ? 'bg-gradient-hero text-white hover:opacity-90' : ''
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Button>
                );
              })}
            </nav>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* Workspace Switcher (for agency users with multiple workspaces) */}
            {workspaces.length > 1 && currentWorkspace && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    size="default"
                    className="gap-2 rounded-xl border-primary/20 hover:border-primary/40 transition-colors"
                    data-testid="workspace-switcher"
                  >
                    <Building2 className="h-4 w-4 text-primary" />
                    <span className="hidden sm:inline font-medium max-w-[120px] truncate">
                      {currentWorkspace.name}
                    </span>
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel className="text-xs uppercase text-muted-foreground">
                    Switch Workspace
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {workspaces.map((workspace) => (
                    <DropdownMenuItem
                      key={workspace.id}
                      onClick={() => handleWorkspaceSwitch(workspace)}
                      className="flex items-center justify-between cursor-pointer"
                      data-testid={`workspace-option-${workspace.id}`}
                    >
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        <div>
                          <p className="font-medium">{workspace.name}</p>
                          {workspace.description && (
                            <p className="text-xs text-muted-foreground truncate max-w-[180px]">
                              {workspace.description}
                            </p>
                          )}
                        </div>
                      </div>
                      {currentWorkspace.id === workspace.id && (
                        <Check className="h-4 w-4 text-primary" />
                      )}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            )}

            {/* Current Workspace Label (for single workspace users) */}
            {workspaces.length === 1 && currentWorkspace && (
              <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground px-3 py-2 rounded-xl bg-muted/50">
                <Building2 className="h-4 w-4" />
                <span className="font-medium">{currentWorkspace.name}</span>
              </div>
            )}

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="default" className="gap-2 rounded-xl hover:bg-muted">
                  <div className="w-8 h-8 rounded-full bg-gradient-hero flex items-center justify-center text-sm font-bold text-white shadow-md">
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="hidden sm:inline font-medium">{user?.username || user?.email}</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <div className="px-2 py-1.5">
                  <p className="text-sm font-medium">{user?.username || 'User'}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => router.push('/app/settings')}>
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Mobile Navigation */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    Menu
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <DropdownMenuItem key={item.href} onClick={() => router.push(item.href)}>
                        <Icon className="h-4 w-4 mr-2" />
                        {item.label}
                      </DropdownMenuItem>
                    );
                  })}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
