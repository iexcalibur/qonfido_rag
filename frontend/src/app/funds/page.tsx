'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Search, TrendingUp, ShieldAlert, ArrowRight, Loader2, RefreshCw, MessageSquare } from 'lucide-react';
import { getFunds } from '@/lib/api';
import type { FundSummary, FundListResponse } from '@/types';

const formatPercent = (value?: number): string => {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toFixed(1)}%`;
};

const formatNumber = (value?: number): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toFixed(2);
};

const getRiskBadgeStyles = (risk?: string): string => {
  if (!risk) return 'text-slate-400 border-slate-500/20 bg-slate-500/5';
  const level = risk.toLowerCase();
  if (level.includes('very high') || level.includes('high')) {
    return 'text-rose-400 border-rose-500/20 bg-rose-500/5';
  }
  if (level.includes('moderate')) {
    return 'text-amber-400 border-amber-500/20 bg-amber-500/5';
  }
  return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';
};

export default function FundsPage() {
  const router = useRouter();
  const [funds, setFunds] = useState<FundListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null);

  const fetchFunds = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getFunds({ limit: 100 });
      setFunds(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch funds');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFunds();
  }, [fetchFunds]);

  const filteredFunds = funds?.funds.filter((fund) => {
    let matches = true;
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      matches = (
        fund.fund_name.toLowerCase().includes(query) ||
        (fund.category?.toLowerCase().includes(query) ?? false) ||
        (fund.fund_house?.toLowerCase().includes(query) ?? false)
      );
    }
    
    if (selectedFilter && matches) {
      const filter = selectedFilter.toLowerCase();
      matches = (fund.category?.toLowerCase().includes(filter) ?? false);
    }
    
    return matches;
  });

  const handleAskAI = (fundName: string) => {
    router.push(`/chat?q=Tell me about ${encodeURIComponent(fundName)}`);
  };

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-200 pt-24 pb-10 relative overflow-hidden">
      
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-violet-900/10 blur-[120px] pointer-events-none"></div>
      <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-indigo-900/10 blur-[120px] pointer-events-none"></div>

      <main className="max-w-7xl mx-auto px-6 relative z-10">

        <div className="mb-10">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-3 tracking-tight">Fund Explorer</h1>
              <p className="text-slate-400 text-lg max-w-2xl">
                Analyze mutual funds with AI-powered insights.
                {funds && <span className="text-indigo-400 ml-2">{funds.total} funds available</span>}
              </p>
            </div>
            <button
              onClick={fetchFunds}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:border-indigo-500/50 transition-all disabled:opacity-50"
            >
              <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </div>

        <div className="mb-8 flex flex-col md:flex-row gap-4">
          <div className="relative flex-1 group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-xl opacity-20 blur group-hover:opacity-40 transition duration-500"></div>
            <div className="relative bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-xl shadow-lg flex items-center">
              <Search className="absolute left-4 text-slate-400 group-hover:text-indigo-400 transition-colors" size={20} />
              <input
                type="text"
                placeholder="Search funds by name, category, or AMC..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-transparent border-none text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-0 transition-all"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="absolute right-4 text-slate-500 hover:text-white text-xl">×</button>
              )}
            </div>
          </div>
          
          <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0 no-scrollbar">
            {['Large Cap', 'Small Cap','Hybrid', 'Flexi', 'Debt', 'Index', 'ELSS'].map((filter) => (
              <button 
                key={filter} 
                onClick={() => setSelectedFilter(selectedFilter === filter ? null : filter)}
                className={`px-4 py-3 backdrop-blur-md border rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                  selectedFilter === filter
                    ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-400'
                    : 'bg-slate-900/50 border-white/10 text-slate-400 hover:text-white hover:border-indigo-500/50 hover:bg-slate-800/60'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 size={32} className="animate-spin text-indigo-500 mb-4" />
            <p className="text-slate-400">Loading funds...</p>
          </div>
        )}

        {error && !isLoading && (
          <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-8 text-center">
            <p className="text-rose-400 mb-2 font-medium">Failed to load funds</p>
            <p className="text-rose-400/70 text-sm mb-4">{error}</p>
            <p className="text-slate-500 text-sm mb-4">Make sure the backend is running on localhost:8000</p>
            <button onClick={fetchFunds} className="px-4 py-2 bg-rose-500/20 rounded-lg text-rose-300 hover:bg-rose-500/30 transition-colors">
              Try Again
            </button>
          </div>
        )}

        {!isLoading && !error && filteredFunds && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredFunds.map((fund) => (
              <div key={fund.id} className="group relative block">
                <div className="absolute -inset-0.5 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl opacity-0 group-hover:opacity-30 blur-lg transition duration-500"></div>

                <div className="relative bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:bg-slate-800/40 transition-all duration-300 overflow-hidden shadow-xl h-full">
                  
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-white group-hover:text-indigo-300 transition-colors truncate">
                        {fund.fund_name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        {fund.category && (
                          <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-800/50 text-slate-400 border border-white/5">
                            {fund.category}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 ml-2">
                      <button
                        onClick={() => handleAskAI(fund.fund_name)}
                        className="p-2 bg-slate-800/50 rounded-lg text-slate-500 hover:text-indigo-400 hover:bg-indigo-500/10 transition-all"
                        title="Ask AI"
                      >
                        <MessageSquare size={16} />
                      </button>
                      <Link href={`/funds/${fund.id}`} className="p-2 bg-slate-800/50 rounded-lg text-slate-500 group-hover:text-white group-hover:bg-indigo-600 transition-all">
                        <ArrowRight size={16} />
                      </Link>
                    </div>
                  </div>
                  
                  <div className="space-y-3 pt-4 border-t border-white/5">
                    {fund.fund_house && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500">AMC</span>
                        <span className="text-sm text-slate-300 truncate max-w-[150px]">{fund.fund_house}</span>
                      </div>
                    )}
                    {fund.cagr_3yr !== undefined && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500 flex items-center gap-1.5"><TrendingUp size={14}/> 3Y Returns</span>
                        <span className={`font-mono font-bold px-2 py-0.5 rounded ${fund.cagr_3yr > 0 ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'}`}>
                          {formatPercent(fund.cagr_3yr)}
                        </span>
                      </div>
                    )}
                    {fund.sharpe_ratio !== undefined && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500">Sharpe Ratio</span>
                        <span className={`font-mono font-medium ${fund.sharpe_ratio > 1 ? 'text-emerald-400' : 'text-slate-200'}`}>
                          {formatNumber(fund.sharpe_ratio)}
                        </span>
                      </div>
                    )}
                    {fund.risk_level && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500 flex items-center gap-1.5"><ShieldAlert size={14}/> Risk</span>
                        <span className={`text-sm font-medium px-2 py-0.5 rounded border ${getRiskBadgeStyles(fund.risk_level)}`}>
                          {fund.risk_level}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!isLoading && !error && filteredFunds?.length === 0 && (
          <div className="text-center py-20">
            <p className="text-slate-400 mb-4">No funds found matching your criteria.</p>
            <button onClick={() => { setSearchQuery(''); setSelectedFilter(null); }} className="px-4 py-2 bg-slate-800/50 rounded-lg text-slate-300 hover:text-white transition-colors">
              Clear Filters
            </button>
          </div>
        )}

        {!isLoading && !error && filteredFunds && filteredFunds.length > 0 && (
          <div className="mt-8 text-center text-sm text-slate-500">
            Showing {filteredFunds.length} of {funds?.total || 0} funds
          </div>
        )}
      </main>
    </div>
  );
}
