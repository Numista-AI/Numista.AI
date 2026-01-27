import React, { useState } from 'react';
import { AlertTriangle, ArrowRight, Check, X, Save } from 'lucide-react';
import { Coin } from '../types';

interface ImportFixWizardProps {
  brokenRows: any[];
  onComplete: (fixedRows: any[]) => void;
  onCancel: () => void;
}

export const ImportFixWizard: React.FC<ImportFixWizardProps> = ({ brokenRows, onComplete, onCancel }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fixedRows, setFixedRows] = useState<any[]>([]);
  const [currentRow, setCurrentRow] = useState<any>(brokenRows[0]);

  const total = brokenRows.length;
  const progress = ((currentIndex) / total) * 100;

  const handleSkip = () => {
    if (currentIndex < total - 1) {
      setCurrentIndex(prev => prev + 1);
      setCurrentRow(brokenRows[currentIndex + 1]);
    } else {
      finish();
    }
  };

  const handleSave = () => {
    if (!currentRow.year && !currentRow.Year && !currentRow.Date) return; 
    if (!currentRow.denomination && !currentRow.Denomination && !currentRow['Coin Type'] && !currentRow.Description) return;

    setFixedRows(prev => [...prev, currentRow]);
    handleSkip();
  };

  const finish = () => {
    onComplete(fixedRows);
  };

  const handleChange = (field: string, value: string) => {
    setCurrentRow((prev: any) => ({ ...prev, [field]: value }));
  };

  // Helper to safely get value from various potential Excel headers
  const getValue = (keys: string[]) => {
    for (const key of keys) {
      if (currentRow[key]) return currentRow[key];
    }
    return '';
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[80] p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="bg-slate-50 p-6 border-b border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">Import Fix Wizard</h3>
                <p className="text-slate-500 text-sm">
                  We found {total} coins missing required info (Year or Denomination).
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-slate-700">{currentIndex + 1} <span className="text-slate-400 text-lg">/ {total}</span></p>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-amber-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-8 flex-1 overflow-y-auto">
          <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 mb-8">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Original Data Found</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
               {Object.entries(brokenRows[currentIndex]).map(([key, val]) => (
                 <div key={key}>
                   <span className="font-semibold text-slate-700">{key}:</span> <span className="text-slate-600">{String(val)}</span>
                 </div>
               ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Year <span className="text-red-500">*</span></label>
              <input 
                type="text" 
                className="w-full p-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g. 1964"
                value={getValue(['year', 'Year', 'Date'])}
                onChange={(e) => handleChange('year', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Denomination <span className="text-red-500">*</span></label>
              <input 
                type="text" 
                className="w-full p-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g. Quarter"
                value={getValue(['denomination', 'Denomination', 'Coin Type', 'Description'])}
                onChange={(e) => handleChange('denomination', e.target.value)}
              />
            </div>
             <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Country</label>
              <input 
                type="text" 
                className="w-full p-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="United States"
                value={getValue(['country', 'Country']) || 'United States'}
                onChange={(e) => handleChange('country', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 p-6 border-t border-slate-200 flex justify-between items-center">
          <button 
            onClick={onCancel}
            className="text-slate-500 hover:text-slate-800 font-medium px-4 py-2"
          >
            Cancel All
          </button>
          <div className="flex gap-3">
            <button 
              onClick={handleSkip}
              className="px-6 py-2 bg-white border border-slate-300 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors"
            >
              Skip / Discard
            </button>
            <button 
              onClick={handleSave}
              className="px-6 py-2 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/30 flex items-center gap-2"
            >
              <Check className="w-5 h-5" />
              Save & Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};