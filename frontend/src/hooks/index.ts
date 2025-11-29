// =============================================================================
// Qonfido RAG - Custom Hooks
// =============================================================================

import { useState, useCallback } from 'react';
import { sendQuery, getFunds, getFundById, checkHealth } from '@/lib/api';
import type { 
  QueryRequest, 
  QueryResponse, 
  FundListResponse, 
  FundDetail,
  ChatMessage,
  SearchMode,
  MessageMetric,
  MessageCitation,
} from '@/types';
import { generateId } from '@/lib/utils';

// =============================================================================
// useChat Hook - Connected to Backend API
// =============================================================================

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string, searchMode?: SearchMode) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string, searchMode: SearchMode = 'hybrid') => {
    if (!content.trim()) return;

    // Create user message
    const userMessage: ChatMessage = {
      id: generateId(),
      sender: 'user',
      content: content.trim(),
    };

    // Create placeholder AI message with loading state
    const aiMessageId = generateId();
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      sender: 'ai',
      content: '',
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, aiMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Call the backend API
      const request: QueryRequest = {
        query: content.trim(),
        search_mode: searchMode,
        top_k: 5,
        rerank: true,
      };

      const response: QueryResponse = await sendQuery(request);

      // Transform funds to metrics for display
      const metrics: MessageMetric[] = response.funds.slice(0, 3).map((fund) => ({
        label: fund.fund_name.length > 18 
          ? fund.fund_name.slice(0, 18) + '...' 
          : fund.fund_name,
        value: fund.sharpe_ratio 
          ? fund.sharpe_ratio.toFixed(2) 
          : fund.cagr_3yr 
            ? `${fund.cagr_3yr.toFixed(1)}%` 
            : 'N/A',
        status: (fund.sharpe_ratio && fund.sharpe_ratio > 1) || (fund.cagr_3yr && fund.cagr_3yr > 10)
          ? 'good' as const 
          : 'neutral' as const,
      }));

      // Transform sources to citations
      const citations: MessageCitation[] = response.sources.slice(0, 4).map((src, idx) => ({
        id: idx,
        title: src.source === 'fund' ? `Fund: ${src.id}` : `FAQ: ${src.id.slice(0, 20)}...`,
        score: src.score,
      }));

      // Update AI message with response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId
            ? {
                ...msg,
                content: response.answer,
                isLoading: false,
                data: {
                  metrics: metrics.length > 0 ? metrics : undefined,
                  chartPlaceholder: response.funds.length > 0 
                    ? `${response.query_type.charAt(0).toUpperCase() + response.query_type.slice(1)} Analysis` 
                    : undefined,
                  citations: citations.length > 0 ? citations : undefined,
                  // Keep raw data too
                  funds: response.funds,
                  sources: response.sources,
                  confidence: response.confidence,
                  query_type: response.query_type,
                },
              }
            : msg
        )
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId
            ? {
                ...msg,
                content: 'Sorry, I encountered an error processing your request. Please make sure the backend server is running on http://localhost:8000',
                isLoading: false,
                error: errorMessage,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}

// =============================================================================
// useFunds Hook
// =============================================================================

interface UseFundsReturn {
  funds: FundListResponse | null;
  isLoading: boolean;
  error: string | null;
  fetchFunds: (params?: { category?: string; risk_level?: string; limit?: number }) => Promise<void>;
}

export function useFunds(): UseFundsReturn {
  const [funds, setFunds] = useState<FundListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFunds = useCallback(async (params?: { category?: string; risk_level?: string; limit?: number }) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getFunds(params);
      setFunds(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch funds');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { funds, isLoading, error, fetchFunds };
}

// =============================================================================
// useFundDetail Hook
// =============================================================================

interface UseFundDetailReturn {
  fund: FundDetail | null;
  isLoading: boolean;
  error: string | null;
  fetchFund: (fundId: string) => Promise<void>;
}

export function useFundDetail(): UseFundDetailReturn {
  const [fund, setFund] = useState<FundDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFund = useCallback(async (fundId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getFundById(fundId);
      setFund(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch fund');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { fund, isLoading, error, fetchFund };
}

// =============================================================================
// useHealth Hook
// =============================================================================

interface UseHealthReturn {
  isHealthy: boolean | null;
  isChecking: boolean;
  checkAPI: () => Promise<void>;
}

export function useHealth(): UseHealthReturn {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkAPI = useCallback(async () => {
    setIsChecking(true);
    try {
      const response = await checkHealth();
      setIsHealthy(response.status === 'healthy');
    } catch {
      setIsHealthy(false);
    } finally {
      setIsChecking(false);
    }
  }, []);

  return { isHealthy, isChecking, checkAPI };
}
