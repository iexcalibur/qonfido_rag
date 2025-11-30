"use client";

import React, { useState, useEffect } from "react";

import { useRouter } from "next/navigation";

import {
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Activity,
  Wifi,
  WifiOff,
  Loader2,
} from "lucide-react";

import { useHealth } from "@/hooks";

export default function HomePage() {
  const [query, setQuery] = useState("");

  const router = useRouter();

  const { isHealthy, isChecking, checkAPI } = useHealth();

  // Check backend health on mount and periodically

  useEffect(() => {
    checkAPI();

    // Check health every 30 seconds

    const interval = setInterval(checkAPI, 30000);

    return () => clearInterval(interval);
  }, [checkAPI]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (query.trim()) {
      router.push(`/chat?q=${encodeURIComponent(query)}`);
    } else {
      router.push("/chat");
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  return (
    <div className="h-screen w-full relative overflow-hidden flex flex-col font-sans text-white selection:bg-indigo-500/30 bg-slate-950">
      {/* --- BACKGROUND EFFECTS --- */}

      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

      {/* Top Right Blob */}

      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-violet-900/10 blur-[120px] pointer-events-none"></div>

      {/* The Horizon Glow */}

      <div className="absolute bottom-[-20%] left-[-20%] right-[-20%] h-[500px] bg-indigo-600/20 blur-[120px] rounded-[100%] pointer-events-none"></div>

      <main className="relative z-10 h-full w-full flex flex-col items-center justify-center px-4 text-center">
        {/* Backend Status Indicator */}

        <div
          className="absolute bottom-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all bg-slate-900/60 backdrop-blur-md border border-white/10 select-none"
          style={{ pointerEvents: "auto" }}
        >
          {isChecking ? (
            <>
              <Loader2 size={14} className="animate-spin text-slate-400" />

              <span className="text-slate-400">Checking...</span>
            </>
          ) : isHealthy ? (
            <>
              <div className="relative">
                <Wifi size={14} className="text-emerald-400" />

                <div className="absolute inset-0 w-3 h-3 bg-emerald-400/20 rounded-full animate-ping"></div>
              </div>

              <span className="text-emerald-400">Backend Connected</span>
            </>
          ) : (
            <>
              <WifiOff size={14} className="text-rose-400" />

              <span className="text-rose-400">Backend Offline</span>
            </>
          )}
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-400">
          Superhuman <br className="hidden md:block" /> Financial Intelligence
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-12 leading-relaxed">
          Ask any question. Get RAG-powered answers, real-time charts, and risk
          analysis in seconds.{" "}
          <span className="text-indigo-400">
            Stop searching, start knowing.
          </span>
        </p>

        {/* --- GLASS INPUT BOX --- */}

        <form
          onSubmit={handleSubmit}
          className="w-full max-w-3xl relative group"
        >
          {/* Glow Behind - CHANGED: Removed 'group-hover:opacity-40' so it doesn't brighten on hover */}

          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 rounded-3xl opacity-20 blur-xl transition duration-1000"></div>

          {/* Main Glass Container */}

          <div className="relative bg-slate-900/60 backdrop-blur-md rounded-3xl p-2 flex flex-col md:flex-row items-center shadow-2xl">
            <div className="flex-1 w-full">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask Qonfido to analyze a fund, compare returns..."
                className="w-full bg-transparent border-none text-white placeholder-slate-500 text-lg px-6 py-4 focus:ring-0 resize-none h-24 md:h-auto outline-none scrollbar-hide"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();

                    handleSubmit(e);
                  }
                }}
              />
            </div>

            <div className="p-2 w-full md:w-auto flex justify-end">
              <button
                type="submit"
                className="bg-white text-slate-950 hover:bg-indigo-50 px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all group-focus-within:shadow-[0_0_20px_rgba(255,255,255,0.3)]"
              >
                Get Started <ArrowRight size={18} />
              </button>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-3 mt-6">
            {[
              { label: "Analyze Axis Bluechip", icon: TrendingUp },

              { label: "Compare HDFC vs SBI", icon: Activity },

              { label: "Explain Sharpe Ratio", icon: ShieldCheck },
            ].map((item, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSuggestionClick(item.label)}
                className="flex items-center gap-2 px-4 py-2 bg-slate-900/40 backdrop-blur-md border border-white/5 hover:border-indigo-500/50 rounded-full text-sm text-slate-400 hover:text-white transition-all shadow-sm"
              >
                <item.icon size={14} className="text-indigo-400" />

                {item.label}
              </button>
            ))}
          </div>
        </form>
      </main>
    </div>
  );
}
