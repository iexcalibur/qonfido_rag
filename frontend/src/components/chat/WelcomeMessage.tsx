'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

interface WelcomeMessageProps {
  onQuickAction: (query: string) => void;
}

export default function WelcomeMessage({ onQuickAction }: WelcomeMessageProps) {
  const quickActions = ["Analyze Axis Bluechip", "High Sharpe Funds", "Safe Debt Funds"];

  return (
    <div className="flex gap-6 animate-in fade-in duration-700">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center flex-shrink-0 mt-1">
        <Sparkles size={18} className="text-white" />
      </div>
      <div className="flex-1 max-w-3xl space-y-4">
        <div className="p-6 rounded-2xl backdrop-blur-md border bg-slate-900/50 border-white/5 text-slate-300 rounded-tl-none">
          <p className="leading-relaxed text-[15px]">
            👋 Welcome! Ask me to analyze funds, compare risks, or explain metrics like Sharpe Ratio.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 pl-1">
          {quickActions.map((action, i) => (
            <button
              key={i}
              onClick={() => onQuickAction(action)}
              className="px-3 py-1.5 bg-slate-800/40 border border-white/5 rounded-lg text-xs text-slate-400 hover:text-white hover:border-indigo-500/50 transition-all"
            >
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

