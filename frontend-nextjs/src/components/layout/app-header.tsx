'use client';

import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { authApi } from '@/lib/api/auth';
import { Home, Settings, History, Users, ChevronDown, FileText, CalendarClock } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function AppHeader() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const { currentWorkspace } = useWorkspaceStore();

  const handleLogout = () => {
    authApi.logout();
    clearAuth();
    router.push('/login');
  };

  const navItems = [
    { href: '/app', label: 'Dashboard', icon: Home },
    { href: '/app/content', label: 'Content', icon: FileText },
    { href: '/app/subscribers', label: 'Subscribers', icon: Users },
    { href: '/app/schedule', label: 'Schedule', icon: CalendarClock },
    { href: '/app/history', label: 'History', icon: History },
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
            {/* Current Workspace (if available) */}
            {currentWorkspace && (
              <div className="hidden sm:block text-sm text-muted-foreground">
                {currentWorkspace.name}
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
