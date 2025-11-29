'use client';

import React from 'react';

interface MetricCardProps {
  label: string;
  value: string;
  status: 'good' | 'neutral' | 'bad';
}

export default function MetricCard({ label, value, status }: MetricCardProps) {
  return (
    <div className="bg-slate-900/40 backdrop-blur-md border border-white/5 rounded-xl p-4 flex-1 min-w-[140px]">
      <div className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">
        {label}
      </div>
      <div className={`text-xl font-bold ${status === 'good' ? 'text-emerald-400' : 'text-white'}`}>
        {value}
      </div>
      <div className="h-1 w-full bg-slate-800/50 mt-3 rounded-full overflow-hidden">
        <div className={`h-full w-2/3 ${status === 'good' ? 'bg-emerald-500/50' : 'bg-indigo-500/50'}`} />
      </div>
    </div>
  );
}
