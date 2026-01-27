
import React, { useRef } from 'react';
import { LayoutDashboard, Coins, PlusCircle, PiggyBank, ClipboardList, Download, Gift, FileSpreadsheet, Settings, ShieldCheck, AlertCircle, Save, Check, UploadCloud } from 'lucide-react';
import { AppView, Coin } from '../types';
import { exportCollectionToExcel } from '../utils/excelParser';

interface SidebarProps {
  currentView: AppView;
  onChangeView: (view: AppView) => void;
  coins: Coin[];
  onOpenSettings: () => void;
  hasUnsavedChanges: boolean;
  onSaveToComputer: () => void;
  onRestoreFromJson: (file: File) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  currentView, 
  onChangeView, 
  coins, 
  onOpenSettings, 
  hasUnsavedChanges,
  onSaveToComputer,
  onRestoreFromJson
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navItems = [
    { id: AppView.DASHBOARD, label: 'Home Dashboard', icon: LayoutDashboard },
    { id: AppView.COLLECTION, label: 'My Collection', icon: Coins },
    { id: AppView.ADD_COINS, label: 'Add New Coins', icon: PlusCircle },
    { id: AppView.INVENTORY, label: 'Check Inventory', icon: ClipboardList },
    { id: AppView.WISHLIST, label: 'My Wishlist', icon: Gift },
  ];

  const handleExportExcel = () => {
    if (coins.length === 0) {
        alert("Please add some coins to your collection first.");
        return;
    }
    exportCollectionToExcel(coins);
  };

  const handleRestoreClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onRestoreFromJson(file);
      // Reset input so same file can be picked again if needed
      e.target.value = '';
    }
  };

  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-screen fixed left-0 top-0 border-r border-slate-800 z-50 shadow-2xl">
      <div className="p-8 flex items-center gap-3 border-b border-slate-800">
        <div className="p-2 bg-blue-600 rounded-xl shadow-lg shadow-blue-900/40">
            <PiggyBank className="w-6 h-6 text-white" />
        </div>
        <span className="text-xl font-black tracking-tight text-white italic">NumismaAI</span>
      </div>
      
      <nav className="flex-1 p-4 space-y-2 mt-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChangeView(item.id)}
              className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 ${
                isActive 
                  ? 'bg-blue-600 text-white shadow-xl shadow-blue-900/40 translate-x-1' 
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-500'}`} />
              <span className="font-bold text-sm">{item.label}</span>
            </button>
          );
        })}
      </nav>
      
      <div className="p-6 space-y-4 border-t border-slate-800 bg-slate-900/50">
        <div className="px-1 flex items-center justify-between mb-1">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Safe Storage</p>
            {hasUnsavedChanges && (
                <span className="flex items-center gap-1 text-[9px] text-amber-500 font-black animate-pulse uppercase">
                    <AlertCircle className="w-3 h-3" /> Needs Saving
                </span>
            )}
        </div>

        <button 
          onClick={onSaveToComputer}
          className={`w-full flex items-center justify-center gap-3 px-4 py-4 rounded-2xl transition-all text-xs font-black border uppercase tracking-widest ${
            hasUnsavedChanges 
              ? 'bg-blue-600 text-white border-blue-500 shadow-2xl shadow-blue-900/60 scale-105' 
              : 'bg-slate-800/50 text-slate-500 border-slate-700 pointer-events-none'
          }`}
        >
          {hasUnsavedChanges ? <Save className="w-4 h-4" /> : <Check className="w-4 h-4 text-emerald-500" />}
          {hasUnsavedChanges ? 'Save to Computer' : 'Collection Saved'}
        </button>

        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept=".json" 
          className="hidden" 
        />
        
        <button 
          onClick={handleRestoreClick}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-slate-800/30 hover:bg-slate-800 text-slate-400 rounded-xl transition-colors text-[10px] font-bold border border-slate-800"
        >
          <UploadCloud className="w-3.5 h-3.5 text-blue-500/70" />
          Restore from JSON
        </button>
        
        <button 
          onClick={handleExportExcel}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-slate-800/30 hover:bg-slate-800 text-slate-400 rounded-xl transition-colors text-[10px] font-bold border border-slate-800"
          title="Create an Excel spreadsheet"
        >
          <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500/70" />
          Create Spreadsheet
        </button>

        <button 
          onClick={onOpenSettings}
          className="w-full flex items-center justify-center gap-3 px-4 py-2 hover:bg-slate-800 text-slate-600 hover:text-slate-300 rounded-xl transition-colors text-[10px] font-bold"
        >
          <Settings className="w-3.5 h-3.5" />
          App Settings
        </button>

        <div className="flex items-center justify-center gap-2 pt-2">
            <ShieldCheck className="w-3 h-3 text-emerald-500" />
            <span className="text-[9px] font-bold text-slate-600 uppercase tracking-tighter">Private & Secure</span>
        </div>
      </div>
    </div>
  );
};
