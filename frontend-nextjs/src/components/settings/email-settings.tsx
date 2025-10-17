'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/lib/hooks/use-toast';
import { Mail } from 'lucide-react';

export function EmailSettings() {
  const { toast } = useToast();
  const [provider, setProvider] = useState('smtp');
  const [smtpHost, setSmtpHost] = useState('');
  const [smtpPort, setSmtpPort] = useState('587');
  const [smtpUsername, setSmtpUsername] = useState('');
  const [smtpPassword, setSmtpPassword] = useState('');
  const [fromEmail, setFromEmail] = useState('');
  const [fromName, setFromName] = useState('');

  const handleSave = () => {
    toast({
      title: 'Settings Saved',
      description: 'Your email configuration has been updated',
    });
  };

  const handleTestEmail = () => {
    toast({
      title: 'Test Email Sent',
      description: 'Check your inbox for the test email',
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="text-sm font-medium mb-2 block">Email Provider</label>
        <Select value={provider} onValueChange={setProvider}>
          <SelectTrigger className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="smtp">SMTP</SelectItem>
            <SelectItem value="sendgrid">SendGrid</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {provider === 'smtp' && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">SMTP Host</label>
              <Input
                placeholder="smtp.gmail.com"
                value={smtpHost}
                onChange={(e) => setSmtpHost(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Port</label>
              <Input
                placeholder="587"
                value={smtpPort}
                onChange={(e) => setSmtpPort(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Username</label>
            <Input
              placeholder="your-email@gmail.com"
              value={smtpUsername}
              onChange={(e) => setSmtpUsername(e.target.value)}
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Password</label>
            <Input
              type="password"
              placeholder="••••••••"
              value={smtpPassword}
              onChange={(e) => setSmtpPassword(e.target.value)}
            />
          </div>
        </>
      )}

      {provider === 'sendgrid' && (
        <div>
          <label className="text-sm font-medium mb-2 block">SendGrid API Key</label>
          <Input
            type="password"
            placeholder="SG.••••••••••••••"
            value={smtpPassword}
            onChange={(e) => setSmtpPassword(e.target.value)}
          />
        </div>
      )}

      <div className="pt-4 border-t">
        <h4 className="text-sm font-medium mb-4">Sender Information</h4>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">From Email</label>
            <Input
              type="email"
              placeholder="newsletter@yourdomain.com"
              value={fromEmail}
              onChange={(e) => setFromEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-2 block">From Name</label>
            <Input
              placeholder="Your Newsletter"
              value={fromName}
              onChange={(e) => setFromName(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <Button onClick={handleSave}>Save Configuration</Button>
        <Button variant="outline" onClick={handleTestEmail}>
          <Mail className="h-4 w-4 mr-2" />
          Send Test Email
        </Button>
      </div>
    </div>
  );
}
