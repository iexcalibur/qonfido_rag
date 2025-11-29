'use client';

import React, { useState, useRef, useEffect, useMemo, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { sendQuery } from '@/lib/api';
import type { SearchMode, QueryResponse, ChatMessage } from '@/types';
import { ChatMessage as ChatMessageComponent, ChatInput, WelcomeMessage } from '@/components/chat';

function ChatContent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const hasProcessedQuery = useRef(false);

  const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (content: string, searchMode: SearchMode = 'hybrid') => {
    if (!content.trim() || isLoading) return;

    const userMessage: ChatMessage = { id: generateId(), sender: 'user', content: content.trim() };
    const aiMessageId = generateId();
    const aiMessage: ChatMessage = { id: aiMessageId, sender: 'ai', content: '', isLoading: true };

    setMessages((prev) => [...prev, userMessage, aiMessage]);
    setIsLoading(true);

    try {
      const response: QueryResponse = await sendQuery({
        query: content.trim(),
        search_mode: searchMode,
        top_k: 5,
        rerank: true,
      });

      const citations = response.sources.slice(0, 4).map((src, idx) => ({
        id: idx,
        title: src.source === 'fund' ? `Fund: ${src.id.slice(0, 20)}` : `FAQ: ${src.id.slice(0, 20)}`,
        score: src.score,
      }));

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId
            ? {
                ...msg,
                content: response.answer,
                isLoading: false,
                data: {
                  funds: response.funds.length > 0 ? response.funds : undefined,
                  citations: citations.length > 0 ? citations : undefined,
                  confidence: response.confidence,
                },
              }
            : msg
        )
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId
            ? { ...msg, content: 'Sorry, I encountered an error.', isLoading: false, error: errorMessage }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const urlQuery = useMemo(() => searchParams.get('q'), [searchParams]);
  useEffect(() => {
    if (hasProcessedQuery.current || !urlQuery || isLoading) return;
    const trimmedQuery = urlQuery.trim();
    if (trimmedQuery && messages.length === 0) {
      hasProcessedQuery.current = true;
      handleSendMessage(trimmedQuery);
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
            <WelcomeMessage onQuickAction={handleSendMessage} />
          )}

          {/* Chat Messages */}
          {messages.map((msg) => (
            <ChatMessageComponent key={msg.id} message={msg} />
          ))}
        </div>
      </div>

      {/* --- Fixed Input Area --- */}
      <ChatInput 
        onSubmit={handleSendMessage} 
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