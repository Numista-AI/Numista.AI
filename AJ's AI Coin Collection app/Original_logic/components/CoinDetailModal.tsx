
import React, { useState } from 'react';
import { Coin } from '../types';
// Fixed: Added Award and ClipboardList to the lucide-react imports
import { X, Sparkles, BookOpen, Calendar, MapPin, RefreshCw, CheckCircle, Copy, Maximize2, Minimize2, Shield, DollarSign, Tag, History, Award, ClipboardList } from 'lucide-react';
import { generateCoinAnalysis } from '../services/geminiService';

interface CoinDetailModalProps {
  coin: Coin;
  onClose: () => void;
  onUpdate: (coin: Coin) => void;
}

export const CoinDetailModal: React.FC<CoinDetailModalProps> = ({ coin, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [isReportExpanded, setIsReportExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'DETAILS' | 'FINANCIALS' | 'LEGACY'>('DETAILS');

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const result = await generateCoinAnalysis(coin);
      onUpdate({ ...coin, analysis: result.text });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      
      {isReportExpanded && (
          <div className="fixed inset-0 z-[60] bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4 md:p-8 animate-in zoom-in-95 duration-200">
              <div className="bg-white rounded-3xl w-full max-w-4xl h-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
                  <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                      <div className="flex items-center gap-3">
                          <div className="p-2 bg-blue-600 rounded-xl text-white shadow-lg">
                              <BookOpen className="w-5 h-5" />
                          </div>
                          <div>
                              <h2 className="text-xl font-black text-slate-900 uppercase italic">Analysis Report</h2>
                              <p className="text-xs text-slate-400 font-black uppercase">{coin.year} {coin.denomination}</p>
                          </div>
                      </div>
                      <button onClick={() => setIsReportExpanded(false)} className="p-2 hover:bg-slate-200 rounded-full text-slate-400"><Minimize2 className="w-6 h-6" /></button>
                  </div>
                  <div className="flex-1 overflow-y-auto p-8 md:p-12 custom-scrollbar">
                      <div className="prose prose-lg prose-slate max-w-none whitespace-pre-wrap font-sans text-slate-600 leading-relaxed">{coin.analysis}</div>
                  </div>
              </div>
          </div>
      )}

      <div className="bg-white rounded-[2.5rem] max-w-5xl w-full max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
        
        <div className="p-8 border-b border-slate-100 flex justify-between items-start bg-white sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-black text-blue-600 bg-blue-50 px-2 py-0.5 rounded uppercase tracking-widest">{coin.country}</span>
                {coin.storageLocation && (
                    <span className="text-[10px] font-black text-slate-500 bg-slate-100 px-2 py-0.5 rounded uppercase tracking-widest flex items-center gap-1">
                        <Shield className="w-3 h-3" /> {coin.storageLocation}
                    </span>
                )}
            </div>
            <h2 className="text-4xl font-black text-slate-900 tracking-tighter italic uppercase">{coin.year} {coin.denomination}</h2>
            <p className="text-slate-400 font-bold text-xs uppercase tracking-[0.3em] mt-1">{coin.series || 'Collector Grade'}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors"><X className="w-6 h-6 text-slate-400" /></button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-100 bg-slate-50/50 px-8">
            {[
                { id: 'DETAILS', label: 'Identity & Info', icon: Tag },
                { id: 'FINANCIALS', label: 'Financials & Market', icon: DollarSign },
                { id: 'LEGACY', label: 'Legacy Records', icon: History },
            ].map(tab => (
                <button 
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-2 px-6 py-4 text-[10px] font-black uppercase tracking-widest transition-all border-b-2 ${
                        activeTab === tab.id ? 'border-blue-600 text-blue-600 bg-white' : 'border-transparent text-slate-400 hover:text-slate-600'
                    }`}
                >
                    <tab.icon className="w-3.5 h-3.5" />
                    {tab.label}
                </button>
            ))}
        </div>

        <div className="flex-1 overflow-y-auto p-10 space-y-12 custom-scrollbar">
          
          {activeTab === 'DETAILS' && (
              <div className="space-y-12 animate-in fade-in duration-300">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200">
                        <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Condition</p>
                        <p className="text-lg font-black text-slate-900 italic">{coin.condition}</p>
                        {coin.surfaceQuality && <p className="text-xs text-slate-500 font-bold mt-1">{coin.surfaceQuality}</p>}
                    </div>
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200">
                        <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Grading</p>
                        {coin.certification ? (
                            <div className="flex items-center gap-2">
                                <Award className="w-5 h-5 text-amber-500" />
                                <span className="text-lg font-black text-slate-900 italic">{coin.certification.service} {coin.certification.serialNumber}</span>
                            </div>
                        ) : <span className="text-slate-400 italic font-bold">Raw / Uncertified</span>}
                    </div>
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200">
                        <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Ref #</p>
                        <p className="text-lg font-black text-slate-900 italic">{coin.personalRefNo || 'N/A'}</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-4">
                        <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2"><MapPin className="w-4 h-4" /> Physical & Storage</h4>
                        <div className="space-y-3">
                            <div className="flex justify-between py-3 border-b border-slate-100"><span className="text-[11px] font-bold text-slate-500 uppercase">Metal</span><span className="font-black text-sm">{coin.metalContent || '-'}</span></div>
                            <div className="flex justify-between py-3 border-b border-slate-100"><span className="text-[11px] font-bold text-slate-500 uppercase">Subject</span><span className="font-black text-sm">{coin.theme || '-'}</span></div>
                            <div className="flex justify-between py-3 border-b border-slate-100"><span className="text-[11px] font-bold text-slate-500 uppercase">Location</span><span className="font-black text-sm text-blue-600">{coin.storageLocation || 'Unknown'}</span></div>
                        </div>
                    </div>
                    <div className="space-y-4">
                        <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2"><ClipboardList className="w-4 h-4" /> Professional Analysis</h4>
                        {coin.analysis ? (
                            <div className="p-5 bg-blue-50/50 rounded-2xl border border-blue-100 text-xs text-slate-600 leading-relaxed max-h-48 overflow-y-auto">
                                {coin.analysis}
                            </div>
                        ) : (
                            <button onClick={handleGenerateReport} disabled={loading} className="w-full p-6 bg-slate-900 text-white rounded-2xl font-black uppercase text-xs tracking-widest flex items-center justify-center gap-3 shadow-xl active:scale-95 transition-all">
                                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                                Generate Report
                            </button>
                        )}
                    </div>
                </div>
              </div>
          )}

          {activeTab === 'FINANCIALS' && (
              <div className="space-y-12 animate-in fade-in duration-300">
                 <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-8 bg-white rounded-3xl border-2 border-slate-100 flex flex-col items-center">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-2">Cost Basis</p>
                        <p className="text-3xl font-black text-slate-900">${coin.purchaseCost?.toFixed(2) || '0.00'}</p>
                        <p className="text-[10px] font-bold text-slate-400 mt-2 uppercase">{coin.datePurchased || 'N/A Date'}</p>
                    </div>
                    <div className="p-8 bg-emerald-50 rounded-3xl border-2 border-emerald-100 flex flex-col items-center">
                        <p className="text-[10px] font-black text-emerald-600 uppercase mb-2">Market Estimate</p>
                        <p className="text-3xl font-black text-emerald-600">${coin.estimatedValueMax?.toLocaleString() || '0.00'}</p>
                        <p className="text-[10px] font-bold text-emerald-400 mt-2 uppercase">Current Value</p>
                    </div>
                    <div className="p-8 bg-blue-50 rounded-3xl border-2 border-blue-100 flex flex-col items-center">
                        <p className="text-[10px] font-black text-blue-600 uppercase mb-2">Melt Value</p>
                        <p className="text-3xl font-black text-blue-600">${coin.meltValue?.toFixed(2) || '0.00'}</p>
                        <p className="text-[10px] font-bold text-blue-400 mt-2 uppercase">Intrinsic Worth</p>
                    </div>
                 </div>

                 <div className="space-y-6">
                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest border-b pb-3">Retailer & Source Tracking</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div>
                            <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Acquired From</p>
                            <p className="font-black text-slate-900">{coin.retailer || 'N/A'}</p>
                        </div>
                        <div>
                            <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Retailer Item #</p>
                            <p className="font-mono font-bold text-slate-900">{coin.retailerItemNo || '-'}</p>
                        </div>
                        <div>
                            <p className="text-[10px] font-black text-slate-400 uppercase mb-1">Invoice #</p>
                            <p className="font-mono font-bold text-slate-900">{coin.retailerInvoiceNo || '-'}</p>
                        </div>
                    </div>
                 </div>
              </div>
          )}

          {activeTab === 'LEGACY' && (
              <div className="space-y-12 animate-in fade-in duration-300">
                  <div className="p-8 bg-slate-50 rounded-[2.5rem] border border-slate-200">
                      <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Imported Migration Notes</h4>
                      <div className="space-y-8">
                          <div>
                              <p className="text-[10px] font-black text-slate-400 uppercase mb-2 italic">Variety (Legacy)</p>
                              <p className="text-sm font-bold text-slate-700">{coin.varietyLegacy || 'No specific variety noted in historical record.'}</p>
                          </div>
                          <div className="border-t border-slate-200 pt-6">
                              <p className="text-[10px] font-black text-slate-400 uppercase mb-2 italic">Notes (Legacy)</p>
                              <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{coin.notesLegacy || 'No legacy notes available.'}</p>
                          </div>
                      </div>
                  </div>
              </div>
          )}

        </div>
      </div>
    </div>
  );
};
