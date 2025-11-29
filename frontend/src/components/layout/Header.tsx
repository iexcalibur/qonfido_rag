'use client';

import React, { useEffect } from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';
import { useHealth } from '@/hooks';
import { cn } from '@/lib/utils';

export default function Header() {
  const { isHealthy, isChecking, checkAPI } = useHealth();

  useEffect(() => {
    checkAPI();
    // Check health every 30 seconds
    const interval = setInterval(checkAPI, 30000);
    return () => clearInterval(interval);
  }, [checkAPI]);

  return (
    <header className="fixed top-0 left-16 md:left-64 right-0 h-16 bg-slate-950/80 backdrop-blur-xl border-b border-white/5 z-40 flex items-center justify-between px-6">
      
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-white hidden sm:block">Financial Intelligence</h2>
      </div>

      <div className="flex items-center gap-4">
        {/* API Status */}
        <div className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
          isChecking ? 'text-slate-400 bg-slate-800/50' :
          isHealthy ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
        )}>
          {isChecking ? (
            <Activity size={14} className="animate-pulse" />
          ) : isHealthy ? (
            <Wifi size={14} />
          ) : (
            <WifiOff size={14} />
          )}
          <span className="hidden sm:inline">
            {isChecking ? 'Checking...' : isHealthy ? 'API Connected' : 'API Offline'}
          </span>
        </div>
      </div>
    </header>
  );
}
