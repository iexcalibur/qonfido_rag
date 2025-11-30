'use client';

import React, { useState } from 'react';
import { ArrowRight, Settings2 } from 'lucide-react';
import type { SearchMode } from '@/types';

interface ChatInputProps {
  onSubmit: (message: string, searchMode?: SearchMode) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export default function ChatInput({ onSubmit, isLoading, placeholder }: ChatInputProps) {
  const [input, setInput] = useState('');
  const [searchMode, setSearchMode] = useState<SearchMode>('hybrid');
  const [showSettings, setShowSettings] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input.trim(), searchMode);
      setInput('');
    }
  };

  return (
    <div className="absolute bottom-0 left-0 w-full z-20">
      <div className="bg-slate-950/0 px-4 pb-6 pt-2">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative group">
          
          <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 rounded-2xl opacity-10 blur-xl group-hover:opacity-30 transition duration-500" />
          
          {showSettings && (
            <div className="absolute bottom-full mb-2 left-0 right-0 bg-slate-900/90 backdrop-blur-md border border-white/10 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-300">Search Mode</span>
                <button
                  type="button"
                  onClick={() => setShowSettings(false)}
                  className="text-slate-500 hover:text-white"
                >
                  ×
                </button>
              </div>
              <div className="flex gap-2">
                {(['hybrid', 'semantic', 'lexical'] as SearchMode[]).map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => {
                      setSearchMode(mode);
                    }}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      searchMode === mode
                        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                        : 'bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-700/50'
                    }`}
                  >
                    {mode.charAt(0).toUpperCase() + mode.slice(1)}
                    {searchMode === mode && (
                      <span className="ml-2 text-xs">✓</span>
                    )}
                  </button>
                ))}
              </div>
              <p className="mt-3 text-xs text-slate-500">
                {searchMode === 'hybrid' && 'Best of both: combines keyword matching with semantic understanding'}
                {searchMode === 'semantic' && 'Understands meaning and context, good for conceptual questions'}
                {searchMode === 'lexical' && 'Exact keyword matching, good for specific terms'}
              </p>
            </div>
          )}

          {/* Glass Input Container */}
          <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-2xl p-2 flex flex-col relative">
            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder || "Ask about funds, portfolio risks, or market trends..."} 
              className="w-full resize-none border-none focus:ring-0 outline-none text-slate-200 placeholder-slate-600 p-4 min-h-[60px] max-h-[200px] bg-transparent text-base scrollbar-thin scrollbar-thumb-slate-700"
              rows={1}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            
            <div className="flex justify-between items-center px-2 pb-1">
              <div className="flex gap-1 items-center">
                <button 
                  type="button" 
                  onClick={() => setShowSettings(!showSettings)}
                  className={`p-2 rounded-lg transition-colors ${
                    showSettings 
                      ? 'text-indigo-400 bg-indigo-500/10' 
                      : 'text-slate-500 hover:text-indigo-400 hover:bg-indigo-500/10'
                  }`}
                >
                  <Settings2 size={18} />
                </button>
                <div className="px-3 py-1 text-xs text-slate-400 flex items-center gap-1.5 ml-2 bg-slate-800/50 border border-indigo-500/20 rounded-lg">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
                  <span className="font-medium">{searchMode.charAt(0).toUpperCase() + searchMode.slice(1)}</span>
                </div>
              </div>
              <button 
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl px-5 py-2 font-medium flex items-center gap-2 text-sm transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!input.trim() || isLoading}
              >
                <span>{isLoading ? 'Analyzing...' : 'Analyze'}</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
