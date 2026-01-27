import React from 'react';
import { AlertTriangle, Trash2, X } from 'lucide-react';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  count: number;
  onClose: () => void;
  onConfirm: () => void;
}

export const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({ isOpen, count, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-xl max-w-md w-full shadow-2xl overflow-hidden transform transition-all scale-100">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-red-100 rounded-full flex-shrink-0">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Delete {count > 1 ? `${count} Coins` : 'Coin'}?</h3>
              <p className="text-slate-500 mt-2 text-sm leading-relaxed">
                Are you sure you want to remove {count > 1 ? 'these items' : 'this item'} from your collection? This action cannot be undone.
              </p>
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
            className="px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors shadow-sm flex items-center gap-2 text-sm"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};