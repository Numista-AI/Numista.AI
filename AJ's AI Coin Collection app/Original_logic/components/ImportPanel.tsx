
import React, { useState } from 'react';
import { Upload, FileSpreadsheet, ArrowLeft, Loader2, Plus, PenTool } from 'lucide-react';
import { parseExcelFile } from '../utils/excelParser';
import { processImportedData } from '../services/geminiService';
import { Coin } from '../types';

interface AddCoinPageProps {
  onImport: (coins: Coin[]) => void;
  onRestore: (coins: Coin[]) => void;
  existingCountries: string[];
  existingCoins: Coin[];
  onGoToDashboard: () => void;
}

type Mode = 'SELECTION' | 'MANUAL' | 'EXCEL' | 'REVIEW';

export const AddCoinPage: React.FC<AddCoinPageProps> = ({ onImport, onRestore, existingCountries, existingCoins, onGoToDashboard }) => {
  const [mode, setMode] = useState<Mode>('SELECTION');
  const [isLoading, setIsLoading] = useState(false);
  const [importProgress, setImportProgress] = useState({ current: 0, total: 0 });
  const [error, setError] = useState<string | null>(null);
  const [importCandidates, setImportCandidates] = useState<Coin[]>([]);
  const [manualForm, setManualForm] = useState<Partial<Coin>>({
    country: 'United States', year: '', denomination: '', condition: 'Circulated', quantity: 1, purchaseCost: 0, datePurchased: new Date().toISOString().split('T')[0]
  });

  const handleExcelUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    setImportProgress({ current: 0, total: 0 });
    try {
      const rawData = await parseExcelFile(file);
      const validRows = rawData.filter(row => row.Year || row.year || row.Denomination || row.denomination);
      if (validRows.length > 0) {
        const processed = await processImportedData(validRows, (current, total) => {
            setImportProgress({ current, total });
        });
        setImportCandidates(processed);
        setMode('REVIEW');
      } else {
        setError("No valid coin data found in the spreadsheet.");
      }
    } catch (err) {
      setError("Failed to parse file. Please ensure it follows the NumismaAI template.");
    } finally {
      setIsLoading(false);
    }
  };

  const finalizeImport = () => {
    onImport(importCandidates);
    setImportCandidates([]);
    setMode('SELECTION');
  };

  if (mode === 'SELECTION') {
    return (
      <div className="max-w-4xl mx-auto mt-12 px-4 space-y-12 pb-20">
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-black text-slate-900 tracking-tight">Expand Collection</h2>
          <p className="text-slate-500 text-lg">Choose a way to catalog your new coins.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <button onClick={() => setMode('MANUAL')} className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm hover:shadow-xl transition-all text-center">
            <PenTool className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold">Manual Entry</h3>
            <p className="text-slate-500 text-sm mt-2">Type in your coin details directly.</p>
          </button>
          <button onClick={() => setMode('EXCEL')} className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm hover:shadow-xl transition-all text-center">
            <FileSpreadsheet className="w-12 h-12 text-emerald-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold">Import Spreadsheet</h3>
            <p className="text-slate-500 text-sm mt-2">Upload multiple coins using Excel.</p>
          </button>
        </div>
        {error && <p className="text-center text-red-500 font-bold">{error}</p>}
      </div>
    );
  }

  if (mode === 'EXCEL') {
    return (
      <div className="max-w-2xl mx-auto mt-12 p-8 bg-white rounded-3xl border border-slate-200 shadow-xl">
        <button onClick={() => setMode('SELECTION')} className="flex items-center gap-2 mb-8 text-slate-500 hover:text-slate-900"><ArrowLeft className="w-4 h-4" /> Back</button>
        <div className="text-center space-y-6">
          <h2 className="text-2xl font-bold">Import from Excel</h2>
          <input type="file" accept=".xlsx" className="hidden" id="excel-input" onChange={(e) => e.target.files?.[0] && handleExcelUpload(e.target.files[0])} />
          <label htmlFor="excel-input" className="cursor-pointer block border-2 border-dashed border-slate-200 rounded-2xl p-12 hover:border-emerald-400 transition-colors">
            <Upload className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="font-bold text-emerald-600">Click to Select Spreadsheet</p>
            <p className="text-slate-400 text-sm mt-2">Supports .xlsx and .xls formats</p>
          </label>
        </div>
        {isLoading && (
          <div className="mt-8 space-y-4 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-emerald-500 mx-auto" />
            <p className="text-sm font-bold text-slate-600">Processing: {importProgress.current} / {importProgress.total}</p>
          </div>
        )}
      </div>
    );
  }

  if (mode === 'REVIEW') {
    return (
      <div className="max-w-4xl mx-auto mt-8 space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Review Imported Items</h2>
          <button onClick={finalizeImport} className="bg-blue-600 text-white px-8 py-2 rounded-xl font-bold shadow-lg hover:bg-blue-700 transition-colors">Finalize ({importCandidates.length})</button>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr><th className="px-6 py-4">Item</th><th className="px-6 py-4">Qty</th><th className="px-6 py-4 text-right">Cost</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {importCandidates.map((c, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="px-6 py-4 font-bold text-slate-800">{c.year} {c.denomination}</td>
                  <td className="px-6 py-4 text-slate-600">{c.quantity}</td>
                  <td className="px-6 py-4 text-right text-slate-600 font-mono">${c.purchaseCost?.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (mode === 'MANUAL') {
      return (
          <div className="max-w-2xl mx-auto mt-12 p-10 bg-white rounded-[2.5rem] border border-slate-200 shadow-xl">
              <button onClick={() => setMode('SELECTION')} className="flex items-center gap-2 mb-8 text-slate-500 hover:text-slate-900 font-bold uppercase text-xs tracking-widest"><ArrowLeft className="w-4 h-4" /> Back to Selection</button>
              <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tight mb-8">Direct Cataloging</h2>
              
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Year</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all font-bold" value={manualForm.year} onChange={e => setManualForm({...manualForm, year: e.target.value})} placeholder="e.g. 1964" />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Country</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all font-bold" value={manualForm.country} onChange={e => setManualForm({...manualForm, country: e.target.value})} />
                    </div>
                </div>
                <div className="space-y-1">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Denomination</label>
                    <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all font-bold text-lg" value={manualForm.denomination} onChange={e => setManualForm({...manualForm, denomination: e.target.value})} placeholder="e.g. Kennedy Half Dollar" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Condition</label>
                        <select className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all font-bold" value={manualForm.condition} onChange={e => setManualForm({...manualForm, condition: e.target.value})}>
                            <option>Uncirculated</option>
                            <option>Circulated</option>
                            <option>Proof</option>
                            <option>About Uncirculated</option>
                        </select>
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Quantity</label>
                        <input type="number" min="1" className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all font-bold" value={manualForm.quantity} onChange={e => setManualForm({...manualForm, quantity: parseInt(e.target.value)})} />
                    </div>
                </div>
                <button 
                    onClick={() => {
                        const newCoin: Coin = {
                            ...manualForm as Coin,
                            id: crypto.randomUUID(),
                            dateAdded: new Date().toISOString(),
                            currency: 'USD'
                        };
                        onImport([newCoin]);
                        onGoToDashboard();
                    }}
                    className="w-full py-5 bg-blue-600 text-white font-black uppercase tracking-widest rounded-2xl shadow-xl hover:bg-blue-700 active:scale-95 transition-all mt-4"
                >
                    Add to Collection
                </button>
              </div>
          </div>
      );
  }

  return null;
};
