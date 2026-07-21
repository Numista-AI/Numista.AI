"use client";

import { useState, useEffect } from 'react';

interface KnowledgeDoc {
  id: string;
  filename: string;
  type: string;
  summary: string;
  intent?: string;
  absorbed_at: any;
  status: string;
}

interface Suggestion {
  id: string;
  source_filename: string;
  suggestion: string;
  target_collection: string;
  proposed_data: any;
  status: string;
}

export default function AdminDashboard() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';
  const [knowledge, setKnowledge] = useState<KnowledgeDoc[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [kRes, sRes] = await Promise.all([
        fetch(`${API_BASE}/api/admin/brain/knowledge`),
        fetch(`${API_BASE}/api/admin/brain/suggestions`)
      ]);
      setKnowledge(await kRes.json());
      setSuggestions(await sRes.json());
      setSelectedIds([]); // Reset selection on refresh
    } catch (err) {
      console.error("Failed to fetch admin data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string, approved: boolean) => {
    const action = approved ? 'approved' : 'ignored';
    await fetch(`${API_BASE}/api/admin/brain/suggestions/bulk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_ids: [id], action })
    });
    fetchData();
  };

  const handleBulkAction = async (action: 'approved' | 'ignored') => {
    if (selectedIds.length === 0) return;
    await fetch(`${API_BASE}/api/admin/brain/suggestions/bulk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_ids: selectedIds, action })
    });
    fetchData();
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === suggestions.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(suggestions.map(s => s.id));
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto">
      <header className="mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold accent-text mb-2 tracking-tight">Numista.AI Brain Control</h1>
          <p className="opacity-60 text-sm">Monitoring autonomous knowledge absorption and self-healing suggestions.</p>
        </div>
        <div className="flex gap-4 items-center">
            <a href="/deals" className="px-4 py-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-lg text-sm font-semibold hover:bg-emerald-500/20 transition-all flex items-center gap-2">
                <span>💰</span> Deals & Arbitrage
            </a>
            <a href="/ingestion" className="px-4 py-2 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-lg text-sm font-semibold hover:bg-amber-500/20 transition-all flex items-center gap-2">
                <span>⚡</span> Ingestion Ops
            </a>
            <div className="glass px-4 py-2 rounded-lg flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-sm font-medium">Watcher Active</span>
            </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Knowledge Library */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <span className="opacity-70">📚</span> Knowledge Library
          </h2>
          {loading ? (
             <div className="glass p-12 rounded-2xl text-center opacity-50">Loading brain matrix...</div>
          ) : knowledge.length === 0 ? (
            <div className="glass p-12 rounded-2xl text-center opacity-50">
                <p>The library is empty.</p>
                <p className="text-xs mt-2">Drop a PDF into the Brain Inbox to begin.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {knowledge.map((doc) => (
                <div key={doc.id} className="glass p-6 rounded-2xl transition-colors group">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-lg">{doc.filename}</h3>
                      <span className="text-[10px] font-bold bg-slate-500/10 text-slate-500 px-2 py-1 rounded uppercase tracking-widest">{doc.type}</span>
                    </div>
                    <button className="text-slate-500 hover:text-blue-500 text-xs underline decoration-dotted">Reprocess</button>
                  </div>
                  <p className="text-sm opacity-80 leading-relaxed mb-4">{doc.summary}</p>
                  {doc.intent && (
                    <div className="bg-slate-500/5 p-3 rounded-lg border border-slate-500/10">
                        <span className="text-[10px] uppercase font-bold opacity-40 block mb-1">Director's Notes</span>
                        <p className="text-xs italic opacity-70">"{doc.intent}"</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Healing Suggestions */}
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="opacity-70">✨</span> Suggestions
            </h2>
            {suggestions.length > 0 && (
                <button 
                    onClick={toggleSelectAll}
                    className="text-[10px] uppercase font-bold opacity-50 hover:opacity-100"
                >
                    {selectedIds.length === suggestions.length ? 'Deselect All' : 'Select All'}
                </button>
            )}
          </div>

          {selectedIds.length > 0 && (
              <div className="glass p-4 rounded-xl flex gap-2 animate-in fade-in slide-in-from-top-2">
                  <button 
                    onClick={() => handleBulkAction('approved')}
                    className="flex-1 bg-green-600 hover:bg-green-500 text-white text-[10px] font-bold py-2 rounded-lg uppercase tracking-tighter"
                  >
                    Approve ({selectedIds.length})
                  </button>
                  <button 
                    onClick={() => handleBulkAction('ignored')}
                    className="flex-1 bg-red-600/10 hover:bg-red-600/20 text-red-600 text-[10px] font-bold py-2 rounded-lg uppercase tracking-tighter border border-red-600/20"
                  >
                    Ignore Selected
                  </button>
              </div>
          )}

          {suggestions.length === 0 ? (
             <div className="glass p-8 rounded-2xl text-center opacity-50 text-sm">
                No pending suggestions.
             </div>
          ) : (
            <div className="space-y-4">
              {suggestions.map((sug) => (
                <div 
                    key={sug.id} 
                    onClick={() => toggleSelect(sug.id)}
                    className={`glass p-5 rounded-2xl border-l-4 transition-all cursor-pointer ${selectedIds.includes(sug.id) ? 'border-l-green-500 ring-2 ring-green-500/20' : 'border-l-blue-500 opacity-80'}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <p className="text-[10px] uppercase font-bold opacity-40">From: {sug.source_filename.length > 25 ? sug.source_filename.substring(0, 25) + '...' : sug.source_filename}</p>
                    <div className={`w-4 h-4 rounded border flex items-center justify-center ${selectedIds.includes(sug.id) ? 'bg-green-500 border-green-500' : 'border-slate-500'}`}>
                        {selectedIds.includes(sug.id) && <span className="text-white text-[10px]">✓</span>}
                    </div>
                  </div>
                  <p className="text-sm font-medium mb-4 leading-tight">{sug.suggestion}</p>
                  <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                    <button 
                      onClick={() => handleApprove(sug.id, true)}
                      className="flex-1 bg-blue-600/10 hover:bg-blue-600/20 text-blue-600 text-[10px] font-bold py-1.5 rounded-lg border border-blue-600/20"
                    >
                      Approve
                    </button>
                    <button 
                      onClick={() => handleApprove(sug.id, false)}
                      className="px-3 bg-slate-500/5 hover:bg-slate-500/10 text-[10px] font-bold py-1.5 rounded-lg"
                    >
                      Ignore
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
