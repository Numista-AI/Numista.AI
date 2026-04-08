
import React from 'react';
import { Coin } from '../types';
import { AlertTriangle, CheckCircle, X, Search } from 'lucide-react';

interface VarietyDiscoveryModalProps {
  coin: Coin;
  onClose: () => void;
  onConfirmVariety: (coin: Coin) => void;
  onDismissVariety: (coin: Coin) => void;
}

export const VarietyDiscoveryModal: React.FC<VarietyDiscoveryModalProps> = ({ 
    coin, 
    onClose, 
    onConfirmVariety, 
    onDismissVariety 
}) => {
  const variety = coin.potentialVariety;

  if (!variety) return null;

  const handleConfirm = () => {
    // Logic: Append the variety name to the description or series, then call parent
    const updatedCoin = {
        ...coin,
        description: `${coin.description ? coin.description + '\n' : ''}**Identified as: ${variety.name}**`,
        potentialVariety: undefined // Clear the flag
    };
    onConfirmVariety(updatedCoin);
  };

  const handleDismiss = () => {
    // Logic: Just clear the flag
    const updatedCoin = {
        ...coin,
        potentialVariety: undefined
    };
    onDismissVariety(updatedCoin);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[90] p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl overflow-hidden">
        <div className="bg-amber-50 p-6 border-b border-amber-100 flex items-start gap-4">
          <div className="p-3 bg-amber-100 rounded-full flex-shrink-0">
            <AlertTriangle className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-amber-900">Potential Rare Variety Detected</h3>
            <p className="text-amber-700 mt-1 text-sm">
              We noticed this coin type has a version with significantly higher value.
            </p>
          </div>
          <button onClick={onClose} className="ml-auto text-amber-400 hover:text-amber-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex justify-between items-center p-4 bg-slate-50 rounded-lg border border-slate-200">
             <div>
                <p className="text-xs font-bold text-slate-400 uppercase">Current Estimate</p>
                <p className="text-lg font-bold text-slate-700">${coin.estimatedValueMin} - ${coin.estimatedValueMax}</p>
             </div>
             <div className="text-right">
                <p className="text-xs font-bold text-amber-600 uppercase">Potential Value</p>
                <p className="text-lg font-bold text-amber-600">{variety.estimatedValue}</p>
             </div>
          </div>

          <div>
             <h4 className="font-bold text-slate-900 mb-2">{variety.name}</h4>
             <p className="text-slate-600 text-sm leading-relaxed">{variety.description}</p>
          </div>
          
          <div className="p-4 bg-blue-50 text-blue-800 rounded-lg text-sm flex items-start gap-2">
             <Search className="w-4 h-4 mt-0.5 flex-shrink-0" />
             <p>
                Since we don't have a purchase record to verify, please inspect your coin. 
                Does it match the description of the <strong>{variety.name}</strong>?
             </p>
          </div>
        </div>

        <div className="bg-slate-50 p-4 flex justify-end gap-3 border-t border-slate-100">
          <button
            onClick={handleDismiss}
            className="px-4 py-2 text-slate-600 hover:bg-slate-100 font-medium rounded-lg transition-colors text-sm"
          >
            No, it's the common version
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 transition-colors shadow-sm flex items-center gap-2 text-sm"
          >
            <CheckCircle className="w-4 h-4" />
            Yes, it matches!
          </button>
        </div>
      </div>
    </div>
  );
};
