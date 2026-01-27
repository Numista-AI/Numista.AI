import React from 'react';
import { Sparkles, Play, X } from 'lucide-react';

interface EstimateConfirmationModalProps {
  isOpen: boolean;
  count: number;
  onClose: () => void;
  onConfirm: () => void;
}

export const EstimateConfirmationModal: React.FC<EstimateConfirmationModalProps> = ({ isOpen, count, onClose, onConfirm }) => {
  if (!isOpen) return null;

  // Approximate time calculation (2.5s per coin + overhead)
  const estTimeSeconds = count * 2.5;
  const estTimeDisplay = estTimeSeconds > 60 
    ? `${Math.ceil(estTimeSeconds / 60)} minutes` 
    : `${Math.ceil(estTimeSeconds)} seconds`;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-xl max-w-md w-full shadow-2xl overflow-hidden transform transition-all scale-100">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-emerald-100 rounded-full flex-shrink-0">
              <Sparkles className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Start Bulk Valuation?</h3>
              <p className="text-slate-500 mt-2 text-sm leading-relaxed">
                You are about to estimate the value of <strong>{count} coins</strong>.
              </p>
              <div className="mt-4 bg-slate-50 p-3 rounded-lg border border-slate-100 text-sm text-slate-600">
                <p className="font-medium mb-1">Estimated Time: ~{estTimeDisplay}</p>
                <p className="text-xs text-slate-500">
                  To ensure accuracy and prevent errors, we process one coin every few seconds. Please keep this tab open.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-slate-50 p-4 flex justify-end gap-3 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 font-medium rounded-lg transition-colors shadow-sm text-sm"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors shadow-sm flex items-center gap-2 text-sm"
          >
            <Play className="w-4 h-4" />
            Start Valuation
          </button>
        </div>
      </div>
    </div>
  );
};