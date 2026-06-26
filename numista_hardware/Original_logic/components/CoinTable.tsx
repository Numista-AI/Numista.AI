
import React, { useState, useEffect } from 'react';
import { Coin, SortConfig } from '../types';
import { ChevronUp, ChevronDown, Search, ExternalLink, RefreshCw, Trash2, X, Pencil, Sparkles, BookOpen, Layers, Award, Shield } from 'lucide-react';

interface CoinTableProps {
  coins: Coin[];
  onEstimateValue: (coin: Coin) => void;
  onDeleteCoin: (id: string) => void;
  onEditCoin: (coin: Coin) => void;
  onBulkDelete: (ids: string[]) => void;
  onClearCollection: () => void;
  onEstimateAll: () => void;
  onViewDetails: (coin: Coin) => void;
  onAddToSet: (selectedIds: string[]) => void;
  isEstimating: Record<string, boolean>;
}

export const CoinTable: React.FC<CoinTableProps> = ({ 
    coins, 
    onEstimateValue, 
    onDeleteCoin, 
    onEditCoin, 
    onBulkDelete, 
    onClearCollection, 
    onEstimateAll, 
    onViewDetails, 
    onAddToSet,
    isEstimating 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'dateAdded', direction: 'desc' });
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  
  useEffect(() => {
    const validIds = new Set(coins.map(c => c.id));
    setSelectedIds(prev => {
      const next = new Set<string>();
      prev.forEach(id => {
        if (validIds.has(id)) next.add(id);
      });
      return next.size === prev.size ? prev : next;
    });
  }, [coins]);

  const handleSort = (key: keyof Coin | 'grade') => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const filteredCoins = coins.filter(coin => 
    coin.country.toLowerCase().includes(searchTerm.toLowerCase()) ||
    coin.denomination.toLowerCase().includes(searchTerm.toLowerCase()) ||
    coin.year.includes(searchTerm) ||
    (coin.series && coin.series.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (coin.storageLocation && coin.storageLocation.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const sortedCoins = [...filteredCoins].sort((a, b) => {
    if (sortConfig.key === 'grade') {
        const aVal = a.certification?.grade || a.condition;
        const bVal = b.certification?.grade || b.condition;
        return sortConfig.direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }

    const aVal = a[sortConfig.key as keyof Coin];
    const bVal = b[sortConfig.key as keyof Coin];
    
    if (aVal === bVal) return 0;
    if (aVal === undefined) return 1;
    if (bVal === undefined) return -1;
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
    }
    
    const comparison = String(aVal) < String(bVal) ? -1 : 1;
    return sortConfig.direction === 'asc' ? comparison : -comparison;
  });

  const getSortIcon = (key: keyof Coin | 'grade') => {
    if (sortConfig.key !== key) return <div className="w-4 h-4 opacity-0" />;
    return sortConfig.direction === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />;
  };

  const allSelected = filteredCoins.length > 0 && filteredCoins.every(c => selectedIds.has(c.id));

  const handleSelectAll = () => {
    if (allSelected) {
      setSelectedIds(new Set());
    } else {
      const newSelected = new Set(selectedIds);
      filteredCoins.forEach(c => newSelected.add(c.id));
      setSelectedIds(newSelected);
    }
  };

  const handleSelectRow = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const isActionDisabled = Object.values(isEstimating).some(v => v);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden flex flex-col h-full relative transition-colors duration-300">
      
      <div className={`p-4 border-b border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row gap-4 justify-between items-center transition-colors ${selectedIds.size > 0 ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-slate-50/50 dark:bg-slate-800/50'}`}>
        {selectedIds.size > 0 ? (
          <div className="flex items-center justify-between w-full animate-in fade-in duration-200">
            <div className="flex items-center gap-4">
              <span className="font-semibold text-blue-900 dark:text-blue-300">{selectedIds.size} selected</span>
              <button onClick={() => setSelectedIds(new Set())} className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1">
                <X className="w-4 h-4" /> Clear
              </button>
            </div>
            <div className="flex gap-2">
                <button onClick={() => onAddToSet(Array.from(selectedIds))} disabled={isActionDisabled} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm text-sm font-medium disabled:opacity-50">
                    <Layers className="w-4 h-4" /> Add to Set
                </button>
                <button onClick={() => onBulkDelete(Array.from(selectedIds))} disabled={isActionDisabled} className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors shadow-sm text-sm font-medium disabled:opacity-50">
                    <Trash2 className="w-4 h-4" /> Delete
                </button>
            </div>
          </div>
        ) : (
          <>
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200 whitespace-nowrap hidden sm:block">Collection ({coins.length})</h2>
            <div className="flex items-center gap-2 w-full sm:w-auto">
                <div className="relative flex-1 sm:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search coins, years, or storage..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                    />
                </div>
            </div>
          </>
        )}
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-medium border-b border-slate-200 dark:border-slate-700 sticky top-0 z-10">
            <tr>
              <th className="px-6 py-4 w-12 cursor-pointer select-none" onClick={handleSelectAll}>
                <div className="flex items-center justify-center">
                    <input type="checkbox" checked={allSelected} readOnly className="rounded border-slate-300 text-blue-600 w-4 h-4" />
                </div>
              </th>
              {[
                { label: 'Year/Mint', key: 'year' },
                { label: 'Denomination', key: 'denomination' },
                { label: 'Program/Series', key: 'series' },
                { label: 'Condition', key: 'condition' },
                { label: 'Melt', key: 'meltValue' },
                { label: 'Cost', key: 'purchaseCost' },
                { label: 'Value (USD)', key: 'estimatedValueMax' },
                { label: 'Storage', key: 'storageLocation' },
                { label: 'Actions', key: 'id' },
              ].map((col) => (
                <th key={col.key} onClick={() => col.key !== 'id' && handleSort(col.key as keyof Coin | 'grade')} className={`px-6 py-4 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors whitespace-nowrap`}>
                  <div className="flex items-center gap-2">
                    {col.label}
                    {col.key !== 'id' && getSortIcon(col.key as keyof Coin | 'grade')}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
            {sortedCoins.length === 0 ? (
              <tr><td colSpan={10} className="px-6 py-12 text-center text-slate-400 dark:text-slate-500 font-medium">No coins found in your collection.</td></tr>
            ) : (
              sortedCoins.map((coin) => (
                <tr key={coin.id} className={`transition-colors group ${selectedIds.has(coin.id) ? 'bg-blue-50/50 dark:bg-blue-900/20' : 'hover:bg-blue-50/30 dark:hover:bg-slate-800/60'}`}>
                  <td className="px-6 py-4 cursor-pointer" onClick={() => handleSelectRow(coin.id)}>
                    <div className="flex items-center justify-center">
                        <input type="checkbox" checked={selectedIds.has(coin.id)} readOnly className="rounded border-slate-300 text-blue-600 w-4 h-4" />
                    </div>
                  </td>
                  <td className="px-6 py-4 font-bold text-slate-900 dark:text-slate-100">{coin.year} {coin.mintMark && `(${coin.mintMark})`}</td>
                  <td className="px-6 py-4 text-slate-700 dark:text-slate-300 font-medium">{coin.denomination}</td>
                  <td className="px-6 py-4 text-indigo-700 dark:text-indigo-400 font-bold">{coin.series || '-'}</td>
                  <td className="px-6 py-4">
                    {coin.certification ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-black bg-amber-50 text-amber-800 border border-amber-200">
                            <Award className="w-3 h-3" /> {coin.certification.service} {coin.certification.grade || coin.condition}
                        </span>
                    ) : (
                        <span className="text-slate-500 dark:text-slate-400 font-medium">{coin.condition}</span>
                    )}
                  </td>
                  <td className="px-6 py-4 font-mono text-slate-500 dark:text-slate-400">${coin.meltValue?.toFixed(2) || '0.00'}</td>
                  <td className="px-6 py-4 font-mono text-slate-600 dark:text-slate-300">${coin.purchaseCost?.toFixed(2) || '0.00'}</td>
                  <td className="px-6 py-4">
                    {coin.estimatedValueMax !== undefined ? (
                        <span className="font-black text-emerald-600 dark:text-emerald-400">${coin.estimatedValueMax.toLocaleString()}</span>
                    ) : (
                        <span className="text-slate-300 dark:text-slate-600 italic text-xs">Pending</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {coin.storageLocation ? (
                        <span className="flex items-center gap-1.5 text-xs font-bold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded-lg">
                            <Shield className="w-3 h-3 text-slate-400" /> {coin.storageLocation}
                        </span>
                    ) : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                        <button onClick={() => onViewDetails(coin)} className="p-2 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 rounded-lg transition-colors"><BookOpen className="w-4 h-4" /></button>
                        <button onClick={() => onEstimateValue(coin)} disabled={isActionDisabled} className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"><RefreshCw className={`w-4 h-4 ${isEstimating[coin.id] ? 'animate-spin' : ''}`} /></button>
                        <button onClick={() => onEditCoin(coin)} className="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"><Pencil className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
