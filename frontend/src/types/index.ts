// =============================================================================
// Qonfido RAG - TypeScript Types
// =============================================================================

// Search modes
export type SearchMode = 'lexical' | 'semantic' | 'hybrid';

// Source document from RAG
export interface SourceDocument {
  id: string;
  text: string;
  source: 'faq' | 'fund';
  score: number;
  metadata: Record<string, unknown>;
}

// Fund info in response
export interface FundInfo {
  fund_name: string;
  fund_house?: string;
  category?: string;
  cagr_1yr?: number;
  cagr_3yr?: number;
  cagr_5yr?: number;
  sharpe_ratio?: number;
  volatility?: number;
  risk_level?: string;
}

// Query request
export interface QueryRequest {
  query: string;
  search_mode?: SearchMode;
  top_k?: number;
  rerank?: boolean;
  source_filter?: 'faq' | 'fund' | null;
}

// Query response
export interface QueryResponse {
  answer: string;
  query_type: 'faq' | 'numerical' | 'hybrid';
  funds: FundInfo[];
  sources: SourceDocument[];
  confidence: number;
  search_mode: SearchMode;
}

// Fund summary for list (includes metrics for display)
export interface FundSummary {
  id: string;
  fund_name: string;
  fund_house?: string;
  category?: string;
  risk_level?: string;
  // Performance metrics (optional, may be included in list)
  cagr_1yr?: number;
  cagr_3yr?: number;
  cagr_5yr?: number;
  sharpe_ratio?: number;
  volatility?: number;
}

// Detailed fund (all fields)
export interface FundDetail extends FundSummary {
  sub_category?: string;
  sortino_ratio?: number;
  max_drawdown?: number;
  beta?: number;
  alpha?: number;
  aum?: number;
  expense_ratio?: number;
  nav?: number;
}

// Fund list response
export interface FundListResponse {
  funds: FundSummary[];
  total: number;
}

// Health response
export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  services: Record<string, boolean>;
}

// =============================================================================
// Chat Message Types (matching ChatMessage component)
// =============================================================================

export interface MessageMetric {
  label: string;
  value: string;
  status: 'good' | 'neutral' | 'bad';
}

export interface MessageCitation {
  id: number | string;
  title: string;
  page?: number;
  score?: number;
}

export interface ChartDataPoint {
  fund_name: string;
  cagr: number;
  volatility: number;
  sharpe: number;
  cagr_raw?: number | null;
  volatility_raw?: number | null;
  sharpe_raw?: number | null;
}

export interface MessageData {
  metrics?: MessageMetric[];
  chartPlaceholder?: string;
  chartData?: number[]; // Legacy single-series data
  chartDataMulti?: ChartDataPoint[]; // Multi-series chart data (CAGR, Volatility, Sharpe)
  citations?: MessageCitation[];
  // Also keep raw data for flexibility
  funds?: FundInfo[];
  sources?: SourceDocument[];
  confidence?: number;
  query_type?: string;
}

// Chat message type matching the component
export interface ChatMessage {
  id: string | number;
  sender: 'user' | 'ai';
  content: string;
  data?: MessageData;
  isLoading?: boolean;
  error?: string;
}
