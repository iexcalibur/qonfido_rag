'use client';

import React from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import CitationChip from './CitationChip';
import FundAnalysisResults from './FundAnalysisResults';
import type { ChatMessage as ChatMessageType } from '@/types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex gap-6 ${isUser ? 'justify-end' : ''}`}>
      
      {!isUser && (
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center flex-shrink-0 mt-1 shadow-lg shadow-indigo-500/20 border border-indigo-400/20">
          <Sparkles size={18} className="text-white" />
        </div>
      )}

      <div className="flex-1 max-w-3xl space-y-4">
        
        <div className={`p-6 rounded-2xl backdrop-blur-md border relative ${
          isUser 
            ? 'bg-slate-800/60 border-white/5 text-white rounded-tr-none' 
            : 'bg-slate-900/50 border-white/10 text-slate-300 rounded-tl-none shadow-[0_0_40px_-10px_rgba(79,70,229,0.1)]'
        }`}>
          
          {message.isLoading ? (
            <div className="flex items-center gap-3">
              <Loader2 size={18} className="animate-spin text-indigo-400" />
              <span className="text-slate-400">Analyzing your query...</span>
            </div>
          ) : message.error ? (
            <div className="text-rose-400">
              <p>{message.content}</p>
              <p className="text-xs mt-2 text-rose-500/70">{message.error}</p>
            </div>
          ) : (
            <>
              <p className="leading-relaxed text-[15px] whitespace-pre-wrap">{message.content}</p>

              {message.data?.funds && message.data.funds.length > 0 && (
                <FundAnalysisResults funds={message.data.funds} />
              )}

              {message.data && (
                <div className="mt-8 space-y-6">
                  {message.data.confidence !== undefined && (
                    <div className="flex items-center gap-3 text-xs text-slate-500 pt-2">
                      <span>Confidence:</span>
                      <div className="flex-1 h-1.5 bg-slate-800 rounded-full max-w-40 overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all ${
                            message.data.confidence > 0.7 ? 'bg-emerald-500' :
                            message.data.confidence > 0.4 ? 'bg-amber-500' : 'bg-rose-500'
                          }`}
                          style={{ width: `${message.data.confidence * 100}%` }}
                        />
                      </div>
                      <span className="font-mono">{(message.data.confidence * 100).toFixed(0)}%</span>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {!isUser && message.data?.citations && message.data.citations.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 pl-1 pt-1">
            <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mr-2">
              Sources
            </span>
            {message.data.citations.map((cite) => (
              <CitationChip 
                key={cite.id} 
                title={cite.title} 
                page={cite.page}
                score={cite.score}
              />
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-xs font-bold text-slate-400">YOU</span>
        </div>
      )}
    </div>
  );
}
