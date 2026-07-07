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
  const [knowledge, setKnowledge] = useState<KnowledgeDoc[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [kRes, sRes] = await Promise.all([
        fetch('http://localhost:8080/api/admin/brain/knowledge'),
        fetch('http://localhost:8080/api/admin/brain/suggestions')
      ]);
      setKnowledge(await kRes.json());
      setSuggestions(await sRes.json());
    } catch (err) {
      console.error("Failed to fetch admin data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string, approved: boolean) => {
    await fetch('http://localhost:8080/api/admin/brain/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_id: id, approved })
    });
    fetchData();
  };

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto">
      <header className="mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold accent-text mb-2 tracking-tight">Numista.AI Brain Control</h1>
          <p className="text-slate-400">Monitoring autonomous knowledge absorption and self-healing suggestions.</p>
        </div>
        <div className="flex gap-4">
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
                <div key={doc.id} className="glass p-6 rounded-2xl hover:border-slate-500 transition-colors group">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-slate-100">{doc.filename}</h3>
                      <span className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded uppercase tracking-widest">{doc.type}</span>
                    </div>
                    <button className="text-slate-500 hover:text-white text-xs underline">Reprocess</button>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed mb-4">{doc.summary}</p>
                  {doc.intent && (
                    <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Director's Notes</span>
                        <p className="text-xs italic text-slate-400">"{doc.intent}"</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Healing Suggestions */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <span className="opacity-70">✨</span> Healing Suggestions
          </h2>
          {suggestions.length === 0 ? (
             <div className="glass p-8 rounded-2xl text-center opacity-50 text-sm">
                No pending suggestions.
             </div>
          ) : (
            <div className="space-y-4">
              {suggestions.map((sug) => (
                <div key={sug.id} className="glass p-5 rounded-2xl border-l-4 border-l-blue-500">
                  <p className="text-xs text-slate-500 mb-2">From: {sug.source_filename}</p>
                  <p className="text-sm font-medium mb-4">{sug.suggestion}</p>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => handleApprove(sug.id, true)}
                      className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-2 rounded-lg transition-colors"
                    >
                      Approve & Apply
                    </button>
                    <button 
                      onClick={() => handleApprove(sug.id, false)}
                      className="px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold py-2 rounded-lg transition-colors"
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
