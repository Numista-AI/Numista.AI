
import React, { useState, useEffect } from 'react';
import { Coin } from '../types';
import { X, Save, PenTool, Award, DollarSign, Tag, ShieldCheck, ClipboardList, MapPin, History, Package } from 'lucide-react';

interface EditCoinModalProps {
  coin: Coin;
  onClose: () => void;
  onSave: (coin: Coin) => void;
}

export const EditCoinModal: React.FC<EditCoinModalProps> = ({ coin, onClose, onSave }) => {
  const [formData, setFormData] = useState<Coin>(coin);

  useEffect(() => {
    setFormData(coin);
  }, [coin]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleChange = (field: keyof Coin, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCertChange = (field: string, value: string) => {
    setFormData(prev => ({
        ...prev,
        certification: {
            service: field === 'service' ? value : (prev.certification?.service || ''),
            serialNumber: field === 'serialNumber' ? value : (prev.certification?.serialNumber || ''),
            grade: field === 'grade' ? value : (prev.certification?.grade || prev.condition)
        }
    }));
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-hidden animate-in fade-in duration-200">
      <div className="bg-white rounded-[2.5rem] max-w-5xl w-full max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
        <div className="p-8 border-b border-slate-100 flex justify-between items-center bg-slate-50/50 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-600 text-white rounded-2xl shadow-xl shadow-blue-200">
                <PenTool className="w-6 h-6" />
            </div>
            <div>
                <h2 className="text-2xl font-black text-slate-900 tracking-tight italic uppercase">Edit Coin Entry</h2>
                <p className="text-xs text-slate-400 font-black uppercase tracking-widest">{coin.year} {coin.denomination} ({coin.id.slice(0,8)})</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full text-slate-400 transition-colors"><X className="w-6 h-6" /></button>
        </div>

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-8 md:p-12 space-y-16 custom-scrollbar">
            {/* Identity & Physicals */}
            <div className="space-y-8">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest border-b pb-3 flex items-center gap-2">
                    <Tag className="w-4 h-4" /> Identity & Classification
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Country</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.country} onChange={e => handleChange('country', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Year</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.year} onChange={e => handleChange('year', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Mint Mark</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.mintMark || ''} onChange={e => handleChange('mintMark', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Qty</label>
                        <input type="number" className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.quantity} onChange={e => handleChange('quantity', parseInt(e.target.value))} />
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Denomination</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold text-lg" value={formData.denomination} onChange={e => handleChange('denomination', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Program / Series</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.series || ''} onChange={e => handleChange('series', e.target.value)} />
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Theme / Subject</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.theme || ''} onChange={e => handleChange('theme', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Metal Content</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.metalContent || ''} onChange={e => handleChange('metalContent', e.target.value)} />
                    </div>
                </div>
            </div>

            {/* Quality & Certification */}
            <div className="space-y-8">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest border-b pb-3 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4" /> Condition & Certification
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Condition (Grade)</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.condition} onChange={e => handleChange('condition', e.target.value)} />
                    </div>
                    <div className="md:col-span-2 space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Surface & Strike Quality</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.surfaceQuality || ''} onChange={e => handleChange('surfaceQuality', e.target.value)} />
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-slate-50 rounded-[2rem] border border-slate-200">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Grading Service</label>
                        <input className="w-full p-4 bg-white border border-slate-200 rounded-2xl font-bold" value={formData.certification?.service || ''} onChange={e => handleCertChange('service', e.target.value)} placeholder="PCGS, NGC, etc." />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Certification #</label>
                        <input className="w-full p-4 bg-white border border-slate-200 rounded-2xl font-mono font-bold" value={formData.certification?.serialNumber || ''} onChange={e => handleCertChange('serialNumber', e.target.value)} />
                    </div>
                </div>
            </div>

            {/* Financials & Acquisition */}
            <div className="space-y-8">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest border-b pb-3 flex items-center gap-2">
                    <DollarSign className="w-4 h-4" /> Financials & Retailer
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Cost ($)</label>
                        <input type="number" step="0.01" className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-mono font-bold" value={formData.purchaseCost || 0} onChange={e => handleChange('purchaseCost', parseFloat(e.target.value))} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Purchase Date</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.datePurchased || ''} onChange={e => handleChange('datePurchased', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Melt Value ($)</label>
                        <input type="number" step="0.01" className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-mono font-bold" value={formData.meltValue || 0} onChange={e => handleChange('meltValue', parseFloat(e.target.value))} />
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Retailer / Website</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.retailer || ''} onChange={e => handleChange('retailer', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Retailer Item #</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.retailerItemNo || ''} onChange={e => handleChange('retailerItemNo', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Invoice #</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.retailerInvoiceNo || ''} onChange={e => handleChange('retailerInvoiceNo', e.target.value)} />
                    </div>
                </div>
            </div>

            {/* Logistics & Legacy */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div className="space-y-8">
                    <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest border-b pb-3 flex items-center gap-2">
                        <MapPin className="w-4 h-4" /> Logistics
                    </h3>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Storage Location</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.storageLocation || ''} onChange={e => handleChange('storageLocation', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Personal Ref #</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.personalRefNo || ''} onChange={e => handleChange('personalRefNo', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Personal Notes</label>
                        <textarea rows={3} className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold resize-none" value={formData.personalNotes || ''} onChange={e => handleChange('personalNotes', e.target.value)} />
                    </div>
                </div>

                <div className="space-y-8">
                    <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest border-b pb-3 flex items-center gap-2">
                        <History className="w-4 h-4" /> Legacy Migration Data
                    </h3>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Variety (Legacy)</label>
                        <input className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold" value={formData.varietyLegacy || ''} onChange={e => handleChange('varietyLegacy', e.target.value)} />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Notes (Legacy)</label>
                        <textarea rows={6} className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold resize-none" value={formData.notesLegacy || ''} onChange={e => handleChange('notesLegacy', e.target.value)} />
                    </div>
                </div>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t border-slate-100">
                <button type="button" onClick={onClose} className="px-8 py-4 text-slate-500 font-black uppercase tracking-widest hover:bg-slate-50 rounded-2xl transition-all">Cancel</button>
                <button type="submit" className="px-12 py-4 bg-blue-600 text-white font-black uppercase tracking-widest rounded-2xl shadow-xl shadow-blue-100 hover:bg-blue-700 active:scale-95 transition-all flex items-center gap-3">
                    <Save className="w-5 h-5" /> Update Record
                </button>
            </div>
        </form>
      </div>
    </div>
  );
};
