'use client';

import { Badge } from '@/components/ui/badge';
import { Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface SampleDataBadgeProps {
  tooltip?: string;
  variant?: 'default' | 'outline' | 'secondary';
  className?: string;
}

export function SampleDataBadge({
  tooltip = 'This is sample data shown for demonstration purposes. Real data will appear here once you have activity.',
  variant = 'outline',
  className = '',
}: SampleDataBadgeProps) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge
            variant={variant}
            className={`cursor-help border-amber-500/50 bg-amber-50 text-amber-700 hover:bg-amber-100 ${className}`}
          >
            <Info className="h-3 w-3 mr-1" />
            Sample Data
          </Badge>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs">
          <p className="text-sm">{tooltip}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
