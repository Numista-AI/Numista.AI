
import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { CoinTable } from './components/CoinTable';
import { AddCoinPage } from './components/ImportPanel';
import { StatsCard } from './components/StatsCard';
import { AiAssistant } from './components/AiAssistant';
import { EditCoinModal } from './components/EditCoinModal';
import { CoinDetailModal } from './components/CoinDetailModal';
import { DeleteConfirmationModal } from './components/DeleteConfirmationModal';
import { EstimateConfirmationModal } from './components/EstimateConfirmationModal';
import { InventoryPage } from './components/InventoryPage';
import { SetAssignmentModal } from './components/SetAssignmentModal';
import { WishlistPage } from './components/WishlistPage';
import { SettingsModal } from './components/SettingsModal';
import { AppView, Coin, WishlistItem } from './types';
import { Coins, TrendingUp, DollarSign, Wallet, Sparkles, Loader2, CheckCircle, AlertTriangle, Activity } from 'lucide-react';
import { estimateCoinValue } from './services/geminiService';
import { db } from './utils/db';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.DASHBOARD);
  const [coins, setCoins] = useState<Coin[]>([]);
  const [wishlist, setWishlist] = useState<WishlistItem[]>([]);
  const [isDbLoading, setIsDbLoading] = useState(true);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isEstimating, setIsEstimating] = useState<Record<string, boolean>>({});
  const [isBulkProcessing, setIsBulkProcessing] = useState(false);
  const [bulkProgress, setBulkProgress] = useState({ current: 0, total: 0 });
  const [editingCoin, setEditingCoin] = useState<Coin | null>(null);
  const [viewingCoin, setViewingCoin] = useState<Coin | null>(null);
  const [itemsToDelete, setItemsToDelete] = useState<string[]>([]);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isEstimateModalOpen, setIsEstimateModalOpen] = useState(false);
  const [isSetModalOpen, setIsSetModalOpen] = useState(false);
  const [selectedForSetIds, setSelectedForSetIds] = useState<string[]>([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const coinsRef = useRef(coins);
  const wishlistRef = useRef(wishlist);
  useEffect(() => { coinsRef.current = coins; }, [coins]);
  useEffect(() => { wishlistRef.current = wishlist; }, [wishlist]);

  // Persistent storage and recovery
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsDbLoading(true);
        const [loadedCoins, loadedWishlist] = await Promise.all([
          db.getAllCoins(),
          db.getAllWishlist()
        ]);
        setCoins(loadedCoins);
        setWishlist(loadedWishlist);
      } catch (error) {
        console.error("Database load error:", error);
      } finally {
        setIsDbLoading(false);
      }
    };
    loadData();
  }, []);

  const handleSaveToComputer = useCallback(() => {
    const backupData = {
      version: '2.0',
      timestamp: new Date().toISOString(),
      coins: coinsRef.current,
      wishlist: wishlistRef.current
    };
    
    const dataStr = JSON.stringify(backupData, null, 2);
    const now = new Date();
    const filename = `Numisma_Full_Backup_${now.toISOString().split('T')[0]}.json`;
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setHasUnsavedChanges(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 4000);
  }, []);

  const handleRestoreFromJson = useCallback(async (file: File) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const content = e.target?.result as string;
        const data = JSON.parse(content);
        
        let coinsToRestore: Coin[] = [];
        let wishlistToRestore: WishlistItem[] = [];

        // Support for Full Backup (v2.0)
        if (data.coins && Array.isArray(data.coins)) {
          coinsToRestore = data.coins;
          wishlistToRestore = Array.isArray(data.wishlist) ? data.wishlist : [];
        } 
        // Support for Legacy Backup (Array of coins only)
        else if (Array.isArray(data)) {
          coinsToRestore = data;
        } 
        else {
          alert("Invalid backup file. JSON format not recognized.");
          return;
        }

        const confirmMsg = `Restore collection from file? 
- Coins found: ${coinsToRestore.length}
- Wishlist items found: ${wishlistToRestore.length}

Warning: This will completely replace your current local database.`;

        if (confirm(confirmMsg)) {
          setIsDbLoading(true);
          
          try {
            await db.clearCoins();
            await db.clearWishlist();
            
            if (coinsToRestore.length > 0) await db.bulkPutCoins(coinsToRestore);
            if (wishlistToRestore.length > 0) await db.bulkPutWishlist(wishlistToRestore);
            
            setCoins(coinsToRestore);
            setWishlist(wishlistToRestore);
            setHasUnsavedChanges(false);
            
            alert("Workspace restored successfully.");
            setCurrentView(AppView.COLLECTION);
          } catch (dbErr) {
            console.error("DB Restore Failure:", dbErr);
            alert("Database error during restoration. Some data might be incomplete.");
          } finally {
            setIsDbLoading(false);
          }
        }
      } catch (err) {
        console.error("JSON Parse Error:", err);
        alert("Failed to parse the backup file. Please ensure it is a valid JSON file exported from NumismaAI.");
      }
    };
    reader.readAsText(file);
  }, []);

  const totalValueMax = useMemo(() => 
    coins.reduce((acc, coin) => acc + (coin.estimatedValueMax || 0), 0), 
    [coins]
  );

  const pendingValuations = useMemo(() => 
    coins.filter(c => c.estimatedValueMax === undefined).length,
    [coins]
  );

  const handleImport = async (newCoins: Coin[]) => {
    try {
        await db.bulkPutCoins(newCoins);
        const updatedCoins = [...coins, ...newCoins];
        setCoins(updatedCoins);
        setHasUnsavedChanges(true);
    } catch (err) {
        console.error("Import failed:", err);
    }
  };

  const handleEstimateValue = async (coin: Coin) => {
    setIsEstimating(prev => ({ ...prev, [coin.id]: true }));
    try {
      const result = await estimateCoinValue(coin);
      const updatedCoin: Coin = {
        ...coin,
        estimatedValueMin: result.min,
        estimatedValueMax: result.max,
        faceValueUSD: result.faceValue,
        valuationNotes: result.notes,
        valuationDate: new Date().toISOString(),
        sources: result.sources
      };
      await db.putCoin(updatedCoin);
      setCoins(prev => prev.map(c => c.id === coin.id ? updatedCoin : c));
      setHasUnsavedChanges(true);
    } catch (error) {
      console.error("Valuation failed:", error);
    } finally {
      setIsEstimating(prev => ({ ...prev, [coin.id]: false }));
    }
  };

  const handleBulkEstimate = async () => {
    setIsEstimateModalOpen(false);
    const targetCoins = coinsRef.current.filter(c => c.estimatedValueMax === undefined);
    if (targetCoins.length === 0) return;
    setIsBulkProcessing(true);
    setBulkProgress({ current: 0, total: targetCoins.length });
    try {
        for (let i = 0; i < targetCoins.length; i++) {
            const coin = targetCoins[i];
            setBulkProgress(prev => ({ ...prev, current: i + 1 }));
            await handleEstimateValue(coin);
            if (i < targetCoins.length - 1) await new Promise(resolve => setTimeout(resolve, 2000));
        }
    } catch (err) {
        console.error("Bulk process error:", err);
    } finally {
        setIsBulkProcessing(false);
        setBulkProgress({ current: 0, total: 0 });
    }
  };

  if (isDbLoading) return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center text-slate-500">
      <Loader2 className="w-10 h-10 animate-spin text-blue-600 mb-4" />
      <p className="font-bold tracking-tight italic">Processing Workspace Data...</p>
    </div>
  );

  return (
    <div className="flex bg-slate-50 min-h-screen font-sans text-slate-900">
      <Sidebar 
        currentView={currentView} 
        onChangeView={setCurrentView} 
        coins={coins} 
        onOpenSettings={() => setIsSettingsOpen(true)} 
        hasUnsavedChanges={hasUnsavedChanges} 
        onSaveToComputer={handleSaveToComputer}
        onRestoreFromJson={handleRestoreFromJson}
      />
      <main className="flex-1 ml-64 p-10 overflow-y-auto h-screen">
        <div className="max-w-6xl mx-auto space-y-10">
          
          {isBulkProcessing && (
              <div className="bg-indigo-600 p-5 rounded-3xl flex items-center justify-between text-white animate-in slide-in-from-top-4 shadow-2xl">
                  <div className="flex items-center gap-4">
                      <Activity className="w-6 h-6 animate-pulse" />
                      <p className="text-xs opacity-90 font-medium">Bulk Valuing {bulkProgress.current} / {bulkProgress.total}...</p>
                  </div>
                  <div className="w-48 h-2 bg-white/20 rounded-full overflow-hidden mr-4">
                      <div className="h-full bg-white transition-all duration-500" style={{ width: `${(bulkProgress.current / bulkProgress.total) * 100}%` }} />
                  </div>
              </div>
          )}

          <div className="flex justify-between items-end">
             <div>
                <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">
                    {currentView === AppView.DASHBOARD && 'Dashboard'}
                    {currentView === AppView.COLLECTION && 'My Coins'}
                    {currentView === AppView.ADD_COINS && 'Add Items'}
                    {currentView === AppView.INVENTORY && 'Inventory'}
                    {currentView === AppView.WISHLIST && 'Wishlist'}
                </h1>
                <p className="text-slate-400 font-bold uppercase text-[10px] tracking-[0.3em] mt-1 ml-1">Coin Collection AI Manager</p>
             </div>
             <div className="text-right pb-1">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Portfolio Value</p>
                <p className="text-4xl font-black text-emerald-600 tracking-tighter">${totalValueMax.toLocaleString()}</p>
             </div>
          </div>

          {currentView === AppView.DASHBOARD && (
            <div className="space-y-8 animate-in fade-in">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatsCard title="Total Coins" value={coins.length} icon={Coins} />
                <StatsCard title="Market Value" value={`$${totalValueMax.toLocaleString()}`} icon={DollarSign} />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                 <div className="lg:col-span-2 bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-sm flex items-center justify-center text-slate-400 italic">
                    Analytics Dashboard
                 </div>
                 <AiAssistant coins={coins} />
              </div>
            </div>
          )}

          {currentView === AppView.COLLECTION && (
            <div className="animate-in fade-in h-[calc(100vh-16rem)]">
              <CoinTable coins={coins} onEstimateValue={handleEstimateValue} onDeleteCoin={(id) => { setItemsToDelete([id]); setIsDeleteModalOpen(true); }} onEditCoin={setEditingCoin} onBulkDelete={(ids) => { setItemsToDelete(ids); setIsDeleteModalOpen(true); }} onClearCollection={() => { setItemsToDelete(coins.map(c => c.id)); setIsDeleteModalOpen(true); }} onEstimateAll={() => setIsEstimateModalOpen(true)} onViewDetails={setViewingCoin} onAddToSet={(ids) => { setSelectedForSetIds(ids); setIsSetModalOpen(true); }} isEstimating={isEstimating} />
            </div>
          )}

          {currentView === AppView.ADD_COINS && (
            <AddCoinPage onImport={handleImport} onRestore={async (c) => { await db.clearCoins(); await db.bulkPutCoins(c); setCoins(c); }} existingCountries={[]} existingCoins={coins} onGoToDashboard={() => setCurrentView(AppView.DASHBOARD)} />
          )}

          {currentView === AppView.INVENTORY && <InventoryPage coins={coins} onBatchUpdate={async (updates) => { await db.bulkPutCoins(updates); }} />}
          {currentView === AppView.WISHLIST && <WishlistPage coins={coins} wishlist={wishlist} onUpdateWishlist={async (items) => { await db.bulkPutWishlist(items); setWishlist(items); }} />}
        </div>
      </main>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <DeleteConfirmationModal isOpen={isDeleteModalOpen} count={itemsToDelete.length} onClose={() => setIsDeleteModalOpen(false)} onConfirm={async () => { await Promise.all(itemsToDelete.map(id => db.deleteCoin(id))); setCoins(coins.filter(c => !itemsToDelete.includes(c.id))); setIsDeleteModalOpen(false); }} />
      {editingCoin && <EditCoinModal coin={editingCoin} onClose={() => setEditingCoin(null)} onSave={async (u) => { await db.putCoin(u); setCoins(coins.map(c => c.id === u.id ? u : c)); setEditingCoin(null); }} />}
      {viewingCoin && <CoinDetailModal coin={viewingCoin} onClose={() => setViewingCoin(null)} onUpdate={async (u) => { await db.putCoin(u); setCoins(coins.map(c => c.id === u.id ? u : c)); setViewingCoin(u); }} />}
      <EstimateConfirmationModal isOpen={isEstimateModalOpen} count={pendingValuations} onClose={() => setIsEstimateModalOpen(false)} onConfirm={handleBulkEstimate} />
    </div>
  );
};

export default App;
