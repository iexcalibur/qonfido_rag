'use client';

import React, { useRef, useEffect, useMemo, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useChat } from '@/hooks';
import { ChatMessage as ChatMessageComponent, ChatInput, WelcomeMessage } from '@/components/chat';

function ChatContent() {
  // Replace local state with hook
  const { messages, isLoading, sendMessage } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const hasProcessedQuery = useRef(false);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle URL query parameter (e.g., /chat?q=show%20me%20funds)
  const urlQuery = useMemo(() => searchParams.get('q'), [searchParams]);
  useEffect(() => {
    if (hasProcessedQuery.current || !urlQuery || isLoading) return;
    const trimmedQuery = urlQuery.trim();
    if (trimmedQuery && messages.length === 0) {
      hasProcessedQuery.current = true;
      sendMessage(trimmedQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlQuery]);

  return (
    <div className="relative h-screen w-full bg-slate-950 text-slate-200 font-sans selection:bg-indigo-500/30 overflow-hidden">
      
      {/* --- Ambient Background Glows --- */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-violet-900/10 blur-[120px] pointer-events-none z-0"></div>
      <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-indigo-900/10 blur-[120px] pointer-events-none z-0"></div>

      {/* --- SCROLL CONTAINER --- */}
      <div 
        ref={scrollRef}
        className="absolute top-16 bottom-0 left-0 right-0 overflow-y-auto px-4 md:px-8 pt-6 pb-40 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent z-10"
      >
        <div className="max-w-4xl mx-auto space-y-10">
          
          {/* Welcome Message (Hidden if messages exist) */}
          {messages.length === 0 && (
            <WelcomeMessage onQuickAction={sendMessage} />
          )}

          {/* Chat Messages */}
          {messages.map((msg) => (
            <ChatMessageComponent key={msg.id} message={msg} />
          ))}
        </div>
      </div>

      {/* --- Fixed Input Area --- */}
      <ChatInput 
        onSubmit={sendMessage} 
        isLoading={isLoading}
        placeholder="Ask about funds..."
      />
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center bg-slate-950"><Loader2 size={32} className="animate-spin text-indigo-500" /></div>}>
      <ChatContent />
    </Suspense>
  );
}