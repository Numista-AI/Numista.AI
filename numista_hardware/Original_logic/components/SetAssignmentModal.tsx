import React, { useState } from 'react';
import { Coin } from '../types';
import { Layers, Sparkles, CheckCircle, Plus, Search } from 'lucide-react';
import { findMissingCoinsForSet } from '../services/geminiService';

interface SetAssignmentModalProps {
  isOpen: boolean;
  selectedIds: string[];
  allCoins: Coin[];
  onClose: () => void;
  onConfirm: (setIds: string[], setName: string) => void;
  existingSets: string[];
}

export const SetAssignmentModal: React.FC<SetAssignmentModalProps> = ({ 
  isOpen, 
  selectedIds, 
  allCoins, 
  onClose, 
  onConfirm, 
  existingSets 
}) => {
  const [setName, setSetName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [suggestedIds, setSuggestedIds] = useState<string[]>([]);
  const [confirmedSuggestions, setConfirmedSuggestions] = useState<Set<string>>(new Set());

  if (!isOpen) return null;

  const handleScanForMissing = async () => {
    setIsAnalyzing(true);
    const selectedCoins = allCoins.filter(c => selectedIds.includes(c.id));
    const availableCoins = allCoins.filter(c => !selectedIds.includes(c.id)); // Coins not in current selection

    try {
      // Ask AI to look at available coins and find matches for the new set
      const foundIds = await findMissingCoinsForSet(setName, selectedCoins, availableCoins);
      setSuggestedIds(foundIds);
      
      // Auto-select all suggestions by default
      setConfirmedSuggestions(new Set(foundIds));
    } catch (error) {
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const toggleSuggestion = (id: string) => {
    const next = new Set(confirmedSuggestions);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setConfirmedSuggestions(next);
  };

  const handleConfirm = () => {
    // Combine original selection + accepted AI suggestions
    const finalIds = [...selectedIds, ...Array.from(confirmedSuggestions)];
    onConfirm(finalIds, setName);
    // Reset state
    setSetName('');
    setSuggestedIds([]);
    setConfirmedSuggestions(new Set());
  };

  const getCoinLabel = (id: string) => {
    const c = allCoins.find(coin => coin.id === id);
    if (!c) return 'Unknown Coin';
    return `${c.year} ${c.denomination} (${c.series || c.country})`;
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[70] p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl overflow-hidden">
        <div className="bg-slate-50 p-6 border-b border-slate-100 flex items-start gap-4">
          <div className="p-3 bg-indigo-100 rounded-full flex-shrink-0">
            <Layers className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Add to Set</h3>
            <p className="text-slate-500 mt-1 text-sm">
              Group {selectedIds.length} selected coins into a named collection (Set).
            </p>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-2">Set / Program Name</label>
            <div className="relative">
                <input 
                    type="text" 
                    list="existing-sets"
                    value={setName}
                    onChange={(e) => setSetName(e.target.value)}
                    placeholder="e.g. Barber Silver Half Dollars"
                    className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    autoFocus
                />
                <datalist id="existing-sets">
                    {existingSets.map(s => <option key={s} value={s} />)}
                </datalist>
            </div>
          </div>

          {/* AI Suggestion Section */}
          {setName.length > 3 && (
            <div className="bg-indigo-50 rounded-xl p-4 border border-indigo-100">
                <div className="flex justify-between items-center mb-3">
                    <h4 className="font-semibold text-indigo-900 flex items-center gap-2 text-sm">
                        <Sparkles className="w-4 h-4" />
                        AI Set Completion
                    </h4>
                </div>
                
                {suggestedIds.length === 0 ? (
                    <div className="text-center">
                        <p className="text-xs text-indigo-700 mb-3">
                            Want to see if other coins in your collection belong to this set?
                        </p>
                        <button 
                            onClick={handleScanForMissing}
                            disabled={isAnalyzing}
                            className="text-xs bg-indigo-600 text-white px-3 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 mx-auto disabled:opacity-50"
                        >
                            {isAnalyzing ? (
                                <>Scanning Collection...</>
                            ) : (
                                <><Search className="w-3 h-3" /> Find Missing Set Items</>
                            )}
                        </button>
                    </div>
                ) : (
                    <div className="animate-in slide-in-from-top-2">
                         <p className="text-xs font-bold text-indigo-800 mb-2">Found {suggestedIds.length} potential matches:</p>
                         <div className="max-h-32 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
                            {suggestedIds.map(id => (
                                <label key={id} className="flex items-center gap-2 p-2 bg-white rounded border border-indigo-100 cursor-pointer hover:bg-indigo-50">
                                    <input 
                                        type="checkbox"
                                        checked={confirmedSuggestions.has(id)}
                                        onChange={() => toggleSuggestion(id)}
                                        className="rounded text-indigo-600 focus:ring-indigo-500"
                                    />
                                    <span className="text-xs text-slate-700 truncate">{getCoinLabel(id)}</span>
                                </label>
                            ))}
                         </div>
                    </div>
                )}
            </div>
          )}
        </div>

        <div className="bg-slate-50 p-4 flex justify-end gap-3 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 font-medium rounded-lg transition-colors shadow-sm text-sm"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!setName}
            className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm flex items-center gap-2 text-sm disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            Add {selectedIds.length + confirmedSuggestions.size} Coins to Set
          </button>
        </div>
      </div>
    </div>
  );
};