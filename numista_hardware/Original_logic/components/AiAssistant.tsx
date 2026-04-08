import React, { useState } from 'react';
import { Send, Sparkles, Bot } from 'lucide-react';
import { Coin } from '../types';
import { getCollectionInsights } from '../services/geminiService';

interface AiAssistantProps {
  coins: Coin[];
}

export const AiAssistant: React.FC<AiAssistantProps> = ({ coins }) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setResponse(null);

    try {
      const answer = await getCollectionInsights(coins, query);
      setResponse(answer);
    } catch (error) {
      setResponse("I'm having trouble connecting to the valuation service right now.");
    } finally {
      setIsLoading(false);
    }
  };

  const suggestions = [
    "What is my most valuable coin?",
    "How much are my US coins worth?",
    "Show me coins purchased in 2023",
    "What is my total profit?"
  ];

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-6 text-white shadow-xl border border-slate-700">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-600 rounded-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold">Collection Intelligence</h3>
          <p className="text-slate-400 text-xs">Ask specific questions about your inventory</p>
        </div>
      </div>

      <div className="space-y-4">
        {response && (
          <div className="bg-slate-700/50 p-4 rounded-lg border border-slate-600 animate-in fade-in slide-in-from-bottom-2">
            <div className="flex gap-3">
              <Bot className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
              <p className="text-slate-200 text-sm leading-relaxed">{response}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleAsk} className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ex: How much are my American Eagle silver dollars worth?"
            className="w-full bg-slate-950/50 border border-slate-700 rounded-lg pl-4 pr-12 py-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-white placeholder-slate-500"
            aria-label="Ask a question about your collection"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-500 disabled:opacity-50 transition-colors"
            aria-label="Send question"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>

        {!response && (
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => setQuery(s)}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-full border border-slate-700 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};