export type SearchMode = 'lexical' | 'semantic' | 'hybrid';

export interface SourceDocument {
  id: string;
  text: string;
  source: 'faq' | 'fund';
  score: number;
  metadata: Record<string, unknown>;
}

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

export interface QueryRequest {
  query: string;
  search_mode?: SearchMode;
  top_k?: number;
  rerank?: boolean;
  source_filter?: 'faq' | 'fund' | null;
}

export interface QueryResponse {
  answer: string;
  query_type: 'faq' | 'numerical' | 'hybrid';
  funds: FundInfo[];
  sources: SourceDocument[];
  confidence: number;
  search_mode: SearchMode;
}

export interface FundSummary {
  id: string;
  fund_name: string;
  fund_house?: string;
  category?: string;
  risk_level?: string;
  cagr_1yr?: number;
  cagr_3yr?: number;
  cagr_5yr?: number;
  sharpe_ratio?: number;
  volatility?: number;
}

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

export interface FundListResponse {
  funds: FundSummary[];
  total: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  services: Record<string, boolean>;
}

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
  chartData?: number[];
  chartDataMulti?: ChartDataPoint[];
  citations?: MessageCitation[];
  funds?: FundInfo[];
  sources?: SourceDocument[];
  confidence?: number;
  query_type?: string;
}

export interface ChatMessage {
  id: string | number;
  sender: 'user' | 'ai';
  content: string;
  data?: MessageData;
  isLoading?: boolean;
  error?: string;
}
