import React, { useState } from 'react';
import { Database, Search, Brain, Server, Layout, BarChart3, MessageSquare, Zap, Shield, Eye, Layers, GitBranch, Box, Cloud, Terminal } from 'lucide-react';

const ArchitectureDiagram = () => {
  const [activeLayer, setActiveLayer] = useState(null);

  const layers = [
    {
      id: 'frontend',
      title: 'Frontend Layer',
      subtitle: 'Next.js 14 Dashboard',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-300',
      icon: Layout,
      technologies: [
        { name: 'Next.js 14', purpose: 'App Router, SSR, API Routes' },
        { name: 'TypeScript', purpose: 'Type safety, better DX' },
        { name: 'Tailwind CSS', purpose: 'Utility-first styling' },
        { name: 'shadcn/ui', purpose: 'Beautiful, accessible components' },
        { name: 'TanStack Query', purpose: 'Server state management' },
        { name: 'Tremor / Recharts', purpose: 'Fund performance charts' },
      ]
    },
    {
      id: 'api',
      title: 'API Gateway',
      subtitle: 'FastAPI Backend',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-300',
      icon: Server,
      technologies: [
        { name: 'FastAPI', purpose: 'Async REST API, auto docs' },
        { name: 'Pydantic v2', purpose: 'Request/Response validation' },
        { name: 'SQLModel', purpose: 'Database ORM' },
        { name: 'Redis', purpose: 'Caching & rate limiting' },
      ]
    },
    {
      id: 'orchestration',
      title: 'Orchestration Layer',
      subtitle: 'Query Intelligence',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-300',
      icon: GitBranch,
      technologies: [
        { name: 'LangGraph', purpose: 'Agentic query routing & workflows' },
        { name: 'Query Classifier', purpose: 'FAQ vs Numerical vs Hybrid' },
        { name: 'Intent Detection', purpose: 'Understand user needs' },
      ]
    },
    {
      id: 'retrieval',
      title: 'Retrieval Layer',
      subtitle: 'Hybrid Search Engine',
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-300',
      icon: Search,
      technologies: [
        { name: 'BGE-M3', purpose: 'Dense + Sparse embeddings' },
        { name: 'Qdrant', purpose: 'Vector store with hybrid search' },
        { name: 'BM25', purpose: 'Lexical search baseline' },
        { name: 'Cohere Rerank v3', purpose: 'Result reranking for accuracy' },
        { name: 'RRF (Reciprocal Rank Fusion)', purpose: 'Combine search results' },
      ]
    },
    {
      id: 'generation',
      title: 'Generation Layer',
      subtitle: 'LLM Response',
      color: 'from-pink-500 to-pink-600',
      bgColor: 'bg-pink-50',
      borderColor: 'border-pink-300',
      icon: Brain,
      technologies: [
        { name: 'Claude API', purpose: 'claude-sonnet-4-5-20250514 for generation' },
        { name: 'Instructor', purpose: 'Structured JSON outputs' },
        { name: 'Prompt Templates', purpose: 'Financial domain prompts' },
      ]
    },
    {
      id: 'data',
      title: 'Data Layer',
      subtitle: 'Storage & Persistence',
      color: 'from-cyan-500 to-cyan-600',
      bgColor: 'bg-cyan-50',
      borderColor: 'border-cyan-300',
      icon: Database,
      technologies: [
        { name: 'PostgreSQL', purpose: 'Fund metadata, query logs' },
        { name: 'Qdrant', purpose: 'Vector embeddings storage' },
        { name: 'Redis', purpose: 'Embedding cache, query cache' },
      ]
    },
    {
      id: 'observability',
      title: 'Observability Layer',
      subtitle: 'Monitoring & Evaluation',
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-300',
      icon: Eye,
      technologies: [
        { name: 'LangFuse', purpose: 'LLM tracing & monitoring' },
        { name: 'Ragas', purpose: 'RAG evaluation metrics' },
        { name: 'Pytest', purpose: 'Backend test coverage' },
      ]
    },
    {
      id: 'infrastructure',
      title: 'Infrastructure',
      subtitle: 'Deployment & DevOps',
      color: 'from-gray-600 to-gray-700',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-300',
      icon: Box,
      technologies: [
        { name: 'Docker Compose', purpose: 'One-command local setup' },
        { name: 'Pre-commit hooks', purpose: 'Ruff, Black for code quality' },
        { name: 'GitHub Actions', purpose: 'CI/CD pipeline (optional)' },
      ]
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            🚀 Qonfido RAG System Architecture
          </h1>
          <p className="text-slate-300 text-lg">
            Financial Intelligence Platform - Full Stack Architecture
          </p>
          <p className="text-slate-400 text-sm mt-2">
            Click on any layer to see detailed technology breakdown
          </p>
        </div>

        {/* Main Flow Diagram */}
        <div className="bg-slate-800/50 rounded-2xl p-8 mb-8 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-6 text-center">Request Flow</h2>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            {['User Query', 'Next.js', 'FastAPI', 'LangGraph', 'Retrieval', 'Claude LLM', 'Response'].map((step, i) => (
              <React.Fragment key={step}>
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-2 rounded-lg text-white font-medium text-sm">
                  {step}
                </div>
                {i < 6 && <Zap className="text-yellow-400 w-5 h-5" />}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Architecture Layers */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {layers.map((layer) => {
            const IconComponent = layer.icon;
            return (
              <div
                key={layer.id}
                className={`rounded-xl border-2 ${layer.borderColor} ${layer.bgColor} p-5 cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl ${activeLayer === layer.id ? 'ring-4 ring-offset-2 ring-blue-500' : ''}`}
                onClick={() => setActiveLayer(activeLayer === layer.id ? null : layer.id)}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${layer.color} flex items-center justify-center mb-4`}>
                  <IconComponent className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-slate-800 text-lg">{layer.title}</h3>
                <p className="text-slate-600 text-sm">{layer.subtitle}</p>
                <div className="mt-3 flex flex-wrap gap-1">
                  {layer.technologies.slice(0, 3).map((tech) => (
                    <span key={tech.name} className="text-xs bg-white/60 px-2 py-1 rounded-full text-slate-700">
                      {tech.name}
                    </span>
                  ))}
                  {layer.technologies.length > 3 && (
                    <span className="text-xs bg-slate-200 px-2 py-1 rounded-full text-slate-600">
                      +{layer.technologies.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Detailed View */}
        {activeLayer && (
          <div className="bg-slate-800 rounded-2xl p-8 border border-slate-600 mb-8 animate-in fade-in duration-300">
            <h2 className="text-2xl font-bold text-white mb-6">
              {layers.find(l => l.id === activeLayer)?.title} - Detailed Breakdown
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {layers.find(l => l.id === activeLayer)?.technologies.map((tech) => (
                <div key={tech.name} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                  <h4 className="font-semibold text-white text-lg">{tech.name}</h4>
                  <p className="text-slate-300 text-sm mt-1">{tech.purpose}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Data Flow Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Ingestion Pipeline */}
          <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Layers className="w-5 h-5 text-green-400" />
              Data Ingestion Pipeline
            </h3>
            <div className="space-y-3">
              {[
                { step: '1', title: 'Load CSVs', desc: 'FAQs + Fund Performance Data' },
                { step: '2', title: 'Transform', desc: 'Convert numerical data to rich text descriptions' },
                { step: '3', title: 'Chunk', desc: 'Semantic chunking for FAQs' },
                { step: '4', title: 'Embed', desc: 'BGE-M3 → Dense + Sparse vectors' },
                { step: '5', title: 'Index', desc: 'Store in Qdrant with metadata filters' },
              ].map((item) => (
                <div key={item.step} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white font-bold text-sm">
                    {item.step}
                  </div>
                  <div>
                    <span className="text-white font-medium">{item.title}</span>
                    <span className="text-slate-400 text-sm ml-2">{item.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Query Pipeline */}
          <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-purple-400" />
              Query Processing Pipeline
            </h3>
            <div className="space-y-3">
              {[
                { step: '1', title: 'Classify Query', desc: 'FAQ / Numerical / Hybrid intent' },
                { step: '2', title: 'Route', desc: 'LangGraph decides retrieval strategy' },
                { step: '3', title: 'Retrieve', desc: 'Hybrid search (Dense + BM25)' },
                { step: '4', title: 'Rerank', desc: 'Cohere Rerank for precision' },
                { step: '5', title: 'Generate', desc: 'Claude + Instructor → Structured JSON' },
              ].map((item) => (
                <div key={item.step} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white font-bold text-sm">
                    {item.step}
                  </div>
                  <div>
                    <span className="text-white font-medium">{item.title}</span>
                    <span className="text-slate-400 text-sm ml-2">{item.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Dashboard Features */}
        <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-2xl p-8 border border-blue-700/50 mb-8">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            Next.js Dashboard Features
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: 'AI Chat Interface', icon: '💬' },
              { name: 'Fund Comparison', icon: '📊' },
              { name: 'Performance Charts', icon: '📈' },
              { name: 'Search Mode Toggle', icon: '🔍' },
              { name: 'Source Citations', icon: '📑' },
              { name: 'Query Traces', icon: '🔬' },
            ].map((feature) => (
              <div key={feature.name} className="bg-white/10 rounded-lg p-4 text-center">
                <div className="text-3xl mb-2">{feature.icon}</div>
                <p className="text-white text-sm font-medium">{feature.name}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Summary */}
        <div className="bg-slate-800/50 rounded-2xl p-8 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6 text-center">Complete Tech Stack Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {[
              'Next.js 14', 'TypeScript', 'Tailwind', 'shadcn/ui', 'TanStack Query', 'Tremor',
              'FastAPI', 'Pydantic v2', 'SQLModel', 'LangGraph', 'BGE-M3', 'Qdrant',
              'Cohere Rerank', 'Claude API', 'Instructor', 'PostgreSQL', 'Redis', 'LangFuse',
              'Ragas', 'Docker', 'Pytest', 'Ruff/Black', 'GitHub Actions', 'Pre-commit'
            ].map((tech) => (
              <div key={tech} className="bg-gradient-to-r from-slate-700 to-slate-600 px-3 py-2 rounded-lg text-center">
                <span className="text-white text-sm font-medium">{tech}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-slate-400">
          <p>Built for Qonfido Founding ML/AI Engineer Role</p>
          <p className="text-sm mt-1">By Shubham - 11/10 Submission 🔥</p>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureDiagram;
