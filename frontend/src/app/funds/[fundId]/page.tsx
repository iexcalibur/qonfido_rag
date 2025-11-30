'use client';

import React, { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2, MessageSquare } from 'lucide-react';
import { useFundDetail } from '@/hooks';
import { formatPercent, formatNumber, getRiskBadgeStyles } from '@/lib/utils';

export default function FundDetailPage() {
  const params = useParams();
  const router = useRouter();
  const fundId = params.fundId as string;
  
  const { fund, isLoading, error, fetchFund } = useFundDetail();

  useEffect(() => {
    if (fundId) {
      fetchFund(fundId);
    }
  }, [fundId, fetchFund]);

  const handleAskAboutFund = () => {
    if (fund) {
      router.push(`/chat?q=Tell me about ${fund.fund_name}`);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-950">
        <Loader2 size={32} className="animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error || !fund) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-950">
        <div className="text-center">
          <p className="text-rose-400 mb-4">{error || 'Fund not found'}</p>
          <Link
            href="/funds"
            className="px-4 py-2 bg-slate-800 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors"
          >
            Back to Funds
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] w-full bg-slate-950 text-slate-200 py-8 relative overflow-hidden">
      
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-violet-900/10 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-indigo-900/10 blur-[120px] pointer-events-none" />

      <main className="max-w-5xl mx-auto px-6 relative z-10">
        
        <div className="bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8 mt-10">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{fund.fund_name}</h1>
              <div className="flex flex-wrap items-center gap-3">
                {fund.fund_house && (
                  <span className="text-slate-400">{fund.fund_house}</span>
                )}
                {fund.category && (
                  <span className="px-3 py-1 bg-slate-800/50 rounded-lg text-sm text-slate-300 border border-white/5">
                    {fund.category}
                  </span>
                )}
                {fund.risk_level && (
                  <span className={`px-3 py-1 rounded-lg text-sm font-medium border ${getRiskBadgeStyles(fund.risk_level)}`}>
                    {fund.risk_level} Risk
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={handleAskAboutFund}
              className="flex items-center gap-2 px-5 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-white font-medium transition-colors shadow-lg shadow-indigo-500/20"
            >
              <MessageSquare size={18} />
              Ask AI about this fund
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {fund.cagr_1yr !== undefined && fund.cagr_1yr !== null && (
            <MetricBox 
              label="1Y Returns" 
              value={formatPercent(fund.cagr_1yr)} 
              positive={fund.cagr_1yr > 0}
            />
          )}
          {fund.cagr_3yr !== undefined && fund.cagr_3yr !== null && (
            <MetricBox 
              label="3Y CAGR" 
              value={formatPercent(fund.cagr_3yr)} 
              positive={fund.cagr_3yr > 0}
            />
          )}
          {fund.cagr_5yr !== undefined && fund.cagr_5yr !== null && (
            <MetricBox 
              label="5Y CAGR" 
              value={formatPercent(fund.cagr_5yr)} 
              positive={fund.cagr_5yr > 0}
            />
          )}
          
          {fund.sharpe_ratio !== undefined && fund.sharpe_ratio !== null && (
            <MetricBox 
              label="Sharpe Ratio" 
              value={formatNumber(fund.sharpe_ratio)} 
              positive={fund.sharpe_ratio > 1}
            />
          )}
          {fund.volatility !== undefined && fund.volatility !== null && (
            <MetricBox 
              label="Volatility" 
              value={formatPercent(fund.volatility)} 
            />
          )}
          {fund.sortino_ratio !== undefined && fund.sortino_ratio !== null && (
            <MetricBox 
              label="Sortino Ratio" 
              value={formatNumber(fund.sortino_ratio)} 
              positive={fund.sortino_ratio > 1}
            />
          )}
          {fund.max_drawdown !== undefined && fund.max_drawdown !== null && (
            <MetricBox 
              label="Max Drawdown" 
              value={formatPercent(fund.max_drawdown)} 
              positive={false}
            />
          )}
          {fund.beta !== undefined && fund.beta !== null && (
            <MetricBox 
              label="Beta" 
              value={formatNumber(fund.beta)} 
            />
          )}
          
          {fund.aum !== undefined && fund.aum !== null && (
            <MetricBox 
              label="AUM" 
              value={`₹${fund.aum.toFixed(0)} Cr`} 
            />
          )}
          {fund.expense_ratio !== undefined && fund.expense_ratio !== null && (
            <MetricBox 
              label="Expense Ratio" 
              value={formatPercent(fund.expense_ratio)} 
            />
          )}
          {fund.nav !== undefined && fund.nav !== null && (
            <MetricBox 
              label="NAV" 
              value={`₹${fund.nav.toFixed(2)}`} 
            />
          )}
        </div>

        {fund.sub_category && (
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Fund Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-slate-500 block mb-1">Sub-Category</span>
                <p className="text-slate-200 font-medium">{fund.sub_category}</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function MetricBox({ 
  label, 
  value, 
  positive 
}: { 
  label: string; 
  value: string; 
  positive?: boolean;
}) {
  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-xl p-4 hover:bg-slate-800/50 transition-colors">
      <div className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">
        {label}
      </div>
      <div className={`text-xl font-bold font-mono ${
        positive === true ? 'text-emerald-400' :
        positive === false ? 'text-rose-400' : 'text-white'
      }`}>
        {value}
      </div>
    </div>
  );
}