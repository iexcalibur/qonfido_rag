'use client';

import React from 'react';
import { BarChart2 } from 'lucide-react';
import FundInsightCard from './FundInsightCard';

interface FundAnalysisResultsProps {
  funds: Array<{
    fund_name?: string;
    category?: string;
    cagr_1yr?: number;
    cagr_3yr?: number;
    cagr_5yr?: number;
    volatility?: number;
    sharpe_ratio?: number;
  }>;
}

export default function FundAnalysisResults({ funds }: FundAnalysisResultsProps) {
  if (!funds || funds.length === 0) return null;

  return (
    <div className="mt-6">
      <div className="flex items-center gap-2 mb-3">
        <BarChart2 size={14} className="text-indigo-400" />
        <h4 className="text-xs font-semibold text-indigo-200 uppercase tracking-wider">Analysis Results</h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {funds.slice(0, 4).map((fund, idx) => (
          <FundInsightCard key={idx} fund={fund} />
        ))}
      </div>
    </div>
  );
}

