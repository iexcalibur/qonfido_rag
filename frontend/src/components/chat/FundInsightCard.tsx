'use client';

import React from 'react';
import { TrendingUp, ShieldAlert, Activity } from 'lucide-react';
import { getSharpeContext, getVolatilityContext, getReturnColor } from './FundMetricsUtils';

interface FundInsightCardProps {
  fund: {
    fund_name?: string;
    category?: string;
    cagr_1yr?: number;
    cagr_3yr?: number;
    cagr_5yr?: number;
    volatility?: number;
    sharpe_ratio?: number;
  };
}

export default function FundInsightCard({ fund }: FundInsightCardProps) {
  const fundName = fund.fund_name || 'Unknown Fund';
  const cagr = fund.cagr_5yr ?? fund.cagr_3yr ?? fund.cagr_1yr;
  const volatility = fund.volatility;
  const sharpe = fund.sharpe_ratio;

  const sharpeCtx = getSharpeContext(sharpe);
  const volCtx = getVolatilityContext(volatility);
  const returnColor = getReturnColor(cagr);

  return (
    <div className="bg-slate-900/60 backdrop-blur-md border border-white/5 rounded-xl p-4 hover:border-indigo-500/30 transition-all group">
      
      <div className="flex justify-between items-start mb-4">
        <h5 className="text-sm font-semibold text-white leading-tight max-w-[80%] group-hover:text-indigo-300 transition-colors">
          {fundName}
        </h5>
        {fund.category && (
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 border border-white/5 text-slate-400">
            {fund.category}
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2">

        <div className="bg-slate-800/30 rounded-lg p-2 flex flex-col justify-between border border-white/5">
          <div className="flex items-center gap-1 mb-1">
            <TrendingUp size={12} className="text-slate-500" />
            <span className="text-[10px] text-slate-500 uppercase tracking-wider">Returns</span>
          </div>
          <div>
            <div className={`text-sm font-bold ${returnColor}`}>
              {cagr ? `${cagr.toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-[10px] text-slate-600">
              {fund.cagr_5yr ? '5Y CAGR' : fund.cagr_3yr ? '3Y CAGR' : '1Y CAGR'}
            </div>
          </div>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-2 flex flex-col justify-between border border-white/5">
          <div className="flex items-center gap-1 mb-1">
            <Activity size={12} className="text-slate-500" />
            <span className="text-[10px] text-slate-500 uppercase tracking-wider">Sharpe</span>
          </div>
          <div>
            <div className={`text-sm font-bold ${sharpeCtx.color}`}>
              {sharpe ? sharpe.toFixed(2) : '-'}
            </div>

            <div className="h-1 w-full bg-slate-700 rounded-full mt-1.5 overflow-hidden">
              <div 
                className={`h-full ${sharpeCtx.bg}`} 
                style={{ width: `${Math.min(((sharpe || 0) / 3) * 100, 100)}%` }} 
              />
            </div>
            <div className="text-[10px] text-slate-500 mt-1">{sharpeCtx.label}</div>
          </div>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-2 flex flex-col justify-between border border-white/5">
          <div className="flex items-center gap-1 mb-1">
            <ShieldAlert size={12} className="text-slate-500" />
            <span className="text-[10px] text-slate-500 uppercase tracking-wider">Risk</span>
          </div>
          <div>
            <div className={`text-sm font-bold ${volCtx.color}`}>
              {volatility ? `${volatility.toFixed(1)}%` : '-'}
            </div>
            <div className="text-[10px] text-slate-600 truncate">
              {volCtx.label}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

