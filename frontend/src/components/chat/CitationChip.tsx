'use client';

import React from 'react';
import { FileText } from 'lucide-react';

interface CitationChipProps {
  title: string;
  page?: number;
  score?: number;
}

export default function CitationChip({ title, page, score }: CitationChipProps) {
  return (
    <button className="flex items-center gap-2 bg-slate-800/40 border border-white/5 px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-indigo-400 hover:bg-slate-800/60 transition-all group">
      <FileText size={12} className="text-slate-500 group-hover:text-indigo-400" />
      <span className="truncate max-w-[150px]">{title}</span>
      {page !== undefined && (
        <span className="text-slate-600 group-hover:text-indigo-500/70">p.{page}</span>
      )}
      {score !== undefined && (
        <span className="text-slate-600 group-hover:text-indigo-500/70">{(score * 100).toFixed(0)}%</span>
      )}
    </button>
  );
}
