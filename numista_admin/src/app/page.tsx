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
  confidence?: number | null;
  status: string;
}

interface TierConfig {
  label: string;
  emoji: string;
  color: string;
  borderColor: string;
  badgeBg: string;
  badgeText: string;
  approveBtn: string;
  description: string;
  filter: (s: Suggestion) => boolean;
}

const TIERS: TierConfig[] = [
  {
    label: 'High Confidence',
    emoji: '🟢',
    color: 'text-green-400',
    borderColor: 'border-l-green-500',
    badgeBg: 'bg-green-500/20',
    badgeText: 'text-green-400',
    approveBtn: 'bg-green-600 hover:bg-green-500 text-white',
    description: '93%+ · Directly stated in source — safe to approve all',
    filter: (s) => s.confidence != null && s.confidence >= 0.93,
  },
  {
    label: 'Review Recommended',
    emoji: '🟡',
    color: 'text-yellow-400',
    borderColor: 'border-l-yellow-500',
    badgeBg: 'bg-yellow-500/20',
    badgeText: 'text-yellow-400',
    approveBtn: 'bg-yellow-600 hover:bg-yellow-500 text-white',
    description: '85–92% · Strongly implied — quick review advised',
    filter: (s) => s.confidence != null && s.confidence >= 0.85 && s.confidence < 0.93,
  },
  {
    label: 'Needs Research',
    emoji: '🔴',
    color: 'text-red-400',
    borderColor: 'border-l-red-500',
    badgeBg: 'bg-red-500/20',
    badgeText: 'text-red-400',
    approveBtn: 'bg-red-600 hover:bg-red-500 text-white',
    description: '≤84% · Inferred or ambiguous — verify before approving',
    filter: (s) => s.confidence != null && s.confidence < 0.85,
  },
];

function ConfidenceBadge({ confidence }: { confidence?: number | null }) {
  if (confidence == null) return null;
  const pct = Math.round(confidence * 100);
  const color =
    confidence >= 0.93
      ? 'bg-green-500/20 text-green-400'
      : confidence >= 0.85
      ? 'bg-yellow-500/20 text-yellow-400'
      : 'bg-red-500/20 text-red-400';
  return (
    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${color}`}>
      {pct}%
    </span>
  );
}

function SuggestionCard({
  sug,
  selected,
  onToggle,
  onApprove,
  onIgnore,
  tierBorder,
}: {
  sug: Suggestion;
  selected: boolean;
  onToggle: () => void;
  onApprove: () => void;
  onIgnore: () => void;
  tierBorder: string;
}) {
  return (
    <div
      onClick={onToggle}
      className={`glass p-5 rounded-2xl border-l-4 transition-all cursor-pointer ${
        selected ? `${tierBorder} ring-2 ring-white/10` : `${tierBorder} opacity-80`
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <p className="text-[10px] uppercase font-bold opacity-40">
          From:{' '}
          {sug.source_filename.length > 22
            ? sug.source_filename.substring(0, 22) + '...'
            : sug.source_filename}
        </p>
        <div className="flex items-center gap-2">
          <ConfidenceBadge confidence={sug.confidence} />
          <div
            className={`w-4 h-4 rounded border flex items-center justify-center ${
              selected ? 'bg-green-500 border-green-500' : 'border-slate-500'
            }`}
          >
            {selected && <span className="text-white text-[10px]">✓</span>}
          </div>
        </div>
      </div>
      <p className="text-sm font-medium mb-4 leading-tight">{sug.suggestion}</p>
      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={onApprove}
          className="flex-1 bg-blue-600/10 hover:bg-blue-600/20 text-blue-600 text-[10px] font-bold py-1.5 rounded-lg border border-blue-600/20"
        >
          Approve
        </button>
        <button
          onClick={onIgnore}
          className="px-3 bg-slate-500/5 hover:bg-slate-500/10 text-[10px] font-bold py-1.5 rounded-lg"
        >
          Ignore
        </button>
      </div>
    </div>
  );
}

function TierSection({
  tier,
  suggestions,
  selectedIds,
  onToggle,
  onApprove,
  onIgnore,
  onApproveAll,
}: {
  tier: TierConfig;
  suggestions: Suggestion[];
  selectedIds: string[];
  onToggle: (id: string) => void;
  onApprove: (id: string) => void;
  onIgnore: (id: string) => void;
  onApproveAll: (ids: string[]) => void;
}) {
  const [collapsed, setCollapsed] = useState(false);
  if (suggestions.length === 0) return null;
  const ids = suggestions.map((s) => s.id);

  return (
    <div className="space-y-3">
      {/* Tier header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="flex items-center gap-2 group"
        >
          <span className="text-base">{tier.emoji}</span>
          <span className={`text-sm font-bold ${tier.color}`}>{tier.label}</span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${tier.badgeBg} ${tier.badgeText}`}>
            {suggestions.length}
          </span>
          <span className="text-[10px] opacity-40 group-hover:opacity-70 transition-opacity">
            {collapsed ? '▸' : '▾'}
          </span>
        </button>
        <button
          onClick={() => onApproveAll(ids)}
          className={`text-[10px] uppercase font-bold px-3 py-1.5 rounded-lg transition-colors ${tier.approveBtn}`}
          title={`Approve all ${suggestions.length} suggestions in this tier`}
        >
          ✓ Approve All
        </button>
      </div>
      <p className="text-[10px] opacity-40 -mt-1">{tier.description}</p>

      {!collapsed && (
        <div className="space-y-3 pl-1 border-l border-white/5">
          {suggestions.map((sug) => (
            <SuggestionCard
              key={sug.id}
              sug={sug}
              selected={selectedIds.includes(sug.id)}
              onToggle={() => onToggle(sug.id)}
              onApprove={() => onApprove(sug.id)}
              onIgnore={() => onIgnore(sug.id)}
              tierBorder={tier.borderColor}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';
  const [knowledge, setKnowledge] = useState<KnowledgeDoc[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [rescoring, setRescoring] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [kRes, sRes] = await Promise.all([
        fetch(`${API_BASE}/api/admin/brain/knowledge`),
        fetch(`${API_BASE}/api/admin/brain/suggestions`),
      ]);
      setKnowledge(await kRes.json());
      setSuggestions(await sRes.json());
      setSelectedIds([]);
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const bulkAction = async (ids: string[], action: 'approved' | 'ignored') => {
    if (ids.length === 0) return;
    await fetch(`${API_BASE}/api/admin/brain/suggestions/bulk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_ids: ids, action }),
    });
    fetchData();
  };

  const handleApprove = (id: string) => bulkAction([id], 'approved');
  const handleIgnore = (id: string) => bulkAction([id], 'ignored');
  const handleBulkSelected = (action: 'approved' | 'ignored') => bulkAction(selectedIds, action);
  const handleApproveAll = () => bulkAction(suggestions.map((s) => s.id), 'approved');
  const handleApproveAllInTier = (ids: string[]) => bulkAction(ids, 'approved');

  const handleRescore = async () => {
    setRescoring(true);
    try {
      await fetch(`${API_BASE}/api/admin/brain/suggestions/rescore`, { method: 'POST' });
      await fetchData();
    } catch (err) {
      console.error('Rescore failed', err);
    } finally {
      setRescoring(false);
    }
  };

  const toggleSelect = (id: string) =>
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );

  // Split into tiers + legacy (no confidence score)
  const tiered = TIERS.map((tier) => ({
    tier,
    items: suggestions.filter(tier.filter),
  }));
  const legacy = suggestions.filter((s) => s.confidence == null);

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto">
      <header className="mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold accent-text mb-2 tracking-tight">Numista.AI Brain Control</h1>
          <p className="opacity-60 text-sm">Monitoring autonomous knowledge absorption and self-healing suggestions.</p>
        </div>
        <div className="flex gap-4 items-center">
          <a href="/deals" className="px-4 py-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-lg text-sm font-semibold hover:bg-emerald-500/20 transition-all flex items-center gap-2">
            <span>💰</span> Deals &amp; Arbitrage
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

        {/* Right Column: Tiered Suggestions */}
        <div className="space-y-6">
          {/* Panel header */}
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <span className="opacity-70">✨</span> Suggestions
              {suggestions.length > 0 && (
                <span className="text-xs font-bold bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">
                  {suggestions.length}
                </span>
              )}
            </h2>
            {suggestions.length > 0 && (
              <button
                onClick={handleApproveAll}
                className="text-[10px] uppercase font-bold bg-green-600 hover:bg-green-500 text-white px-3 py-1.5 rounded-lg transition-colors"
                title={`Approve all ${suggestions.length} pending suggestions`}
              >
                ✓ Approve All
              </button>
            )}
          </div>

          {/* Selection action bar */}
          {selectedIds.length > 0 && (
            <div className="glass p-4 rounded-xl flex gap-2">
              <button
                onClick={() => handleBulkSelected('approved')}
                className="flex-1 bg-green-600 hover:bg-green-500 text-white text-[10px] font-bold py-2 rounded-lg uppercase tracking-tighter"
              >
                Approve ({selectedIds.length})
              </button>
              <button
                onClick={() => handleBulkSelected('ignored')}
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
            <div className="space-y-8">
              {/* Confidence tiers */}
              {tiered.map(({ tier, items }) => (
                <TierSection
                  key={tier.label}
                  tier={tier}
                  suggestions={items}
                  selectedIds={selectedIds}
                  onToggle={toggleSelect}
                  onApprove={handleApprove}
                  onIgnore={handleIgnore}
                  onApproveAll={handleApproveAllInTier}
                />
              ))}

              {/* Legacy: no confidence score */}
              {legacy.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-base">⚪</span>
                      <span className="text-sm font-bold text-slate-400">Unscored</span>
                      <span className="text-[10px] font-bold bg-slate-500/20 text-slate-400 px-2 py-0.5 rounded-full">
                        {legacy.length}
                      </span>
                    </div>
                    <button
                      onClick={handleRescore}
                      disabled={rescoring}
                      className="text-[10px] uppercase font-bold bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
                      title="Ask Gemini to score all unscored suggestions — no approvals made"
                    >
                      {rescoring ? (
                        <>
                          <span className="inline-block w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                          Scoring...
                        </>
                      ) : (
                        '🤖 Re-evaluate with AI'
                      )}
                    </button>
                  </div>
                  <p className="text-[10px] opacity-40 -mt-1">Generated before confidence scoring — click Re-evaluate to score without approving</p>
                  <div className="space-y-3 pl-1 border-l border-white/5">
                    {legacy.map((sug) => (
                      <SuggestionCard
                        key={sug.id}
                        sug={sug}
                        selected={selectedIds.includes(sug.id)}
                        onToggle={() => toggleSelect(sug.id)}
                        onApprove={() => handleApprove(sug.id)}
                        onIgnore={() => handleIgnore(sug.id)}
                        tierBorder="border-l-slate-500"
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
