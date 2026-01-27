import React, { useState, useMemo } from 'react';
import { Coin, WishlistItem } from '../types';
import { Gift, Plus, Trash2, Printer, Download, CheckCircle, Search, DollarSign, Filter, X } from 'lucide-react';
import * as XLSX from 'xlsx';

interface WishlistPageProps {
  coins: Coin[];
  wishlist: WishlistItem[];
  onUpdateWishlist: (items: WishlistItem[]) => void;
}

export const WishlistPage: React.FC<WishlistPageProps> = ({ coins, wishlist, onUpdateWishlist }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newItem, setNewItem] = useState<Partial<WishlistItem>>({
    country: 'United States',
    denomination: '',
    priority: 'Medium'
  });

  // Filters
  const [filterMinPrice, setFilterMinPrice] = useState('');
  const [filterMaxPrice, setFilterMaxPrice] = useState('');
  const [hideOwned, setHideOwned] = useState(false);

  // Helper to check if item exists in collection
  const checkOwnership = (item: WishlistItem) => {
    return coins.find(c => {
        // Match logic: If series is defined, match series. Else match Year + Denom
        if (item.series && c.series && c.series.toLowerCase().includes(item.series.toLowerCase())) return true;
        if (item.design && c.design && c.design.toLowerCase().includes(item.design.toLowerCase())) return true;
        if (item.year && c.year === item.year && c.denomination.toLowerCase().includes(item.denomination.toLowerCase())) return true;
        return false;
    });
  };

  const filteredWishlist = useMemo(() => {
    return wishlist.filter(item => {
        const matchesPriceMin = !filterMinPrice || (item.maxPrice || 0) >= parseFloat(filterMinPrice);
        const matchesPriceMax = !filterMaxPrice || (item.maxPrice || 0) <= parseFloat(filterMaxPrice);
        
        const ownedCoin = checkOwnership(item);
        const matchesOwnership = hideOwned ? !ownedCoin : true;

        return matchesPriceMin && matchesPriceMax && matchesOwnership;
    });
  }, [wishlist, coins, filterMinPrice, filterMaxPrice, hideOwned]);

  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItem.denomination) return;

    const item: WishlistItem = {
        id: crypto.randomUUID(),
        country: newItem.country || 'United States',
        year: newItem.year,
        denomination: newItem.denomination || '',
        series: newItem.series,
        design: newItem.design,
        targetCondition: newItem.targetCondition,
        maxPrice: newItem.maxPrice ? Number(newItem.maxPrice) : undefined,
        notes: newItem.notes,
        priority: newItem.priority as 'High' | 'Medium' | 'Low' || 'Medium'
    };

    onUpdateWishlist([...wishlist, item]);
    setNewItem({ country: 'United States', denomination: '', priority: 'Medium' });
    setShowAddForm(false);
  };

  const handleDelete = (id: string) => {
    onUpdateWishlist(wishlist.filter(item => item.id !== id));
  };

  const handleExportExcel = () => {
    const data = filteredWishlist.map(item => {
        const owned = checkOwnership(item);
        return {
            "Priority": item.priority,
            "Denomination": item.denomination,
            "Year": item.year || "Any",
            "Series / Program": item.series || '-',
            "Design": item.design || '-',
            "Target Condition": item.targetCondition || '-',
            "Budget ($)": item.maxPrice || '-',
            "Status": owned ? "IN COLLECTION" : "Wanted",
            "Notes": item.notes || '-'
        };
    });

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Coin Wishlist");
    XLSX.writeFile(wb, "My_Coin_Wishlist.xlsx");
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-20">
      
      {/* Screen Controls */}
      <div className="print:hidden space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start gap-4">
            <div>
                <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                    <Gift className="w-6 h-6 text-pink-500" />
                    My Wishlist
                </h2>
                <p className="text-slate-500 mt-1">Track coins you want to acquire. Items in green are already in your collection.</p>
            </div>
            <div className="flex gap-2 w-full md:w-auto">
                 <button 
                    onClick={() => setShowAddForm(true)}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 shadow-sm"
                 >
                    <Plus className="w-4 h-4" />
                    Add Item
                 </button>
                 <button 
                    onClick={handleExportExcel}
                    className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-slate-50 shadow-sm"
                 >
                    <Download className="w-4 h-4" />
                    Export
                 </button>
                 <button 
                    onClick={() => window.print()}
                    className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-slate-50 shadow-sm"
                 >
                    <Printer className="w-4 h-4" />
                    Print
                 </button>
            </div>
        </div>

        {/* Filters Panel */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-6 items-end">
            <div className="w-full md:flex-1 grid grid-cols-2 gap-4">
                <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-500 uppercase">Min Price ($)</label>
                    <input 
                        type="number" 
                        value={filterMinPrice}
                        onChange={(e) => setFilterMinPrice(e.target.value)}
                        placeholder="0"
                        className="w-full p-2 border border-slate-300 rounded-lg text-sm"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-500 uppercase">Max Price ($)</label>
                    <input 
                        type="number" 
                        value={filterMaxPrice}
                        onChange={(e) => setFilterMaxPrice(e.target.value)}
                        placeholder="Any"
                        className="w-full p-2 border border-slate-300 rounded-lg text-sm"
                    />
                </div>
            </div>
            <div className="w-full md:w-auto">
                <label className="flex items-center gap-2 cursor-pointer p-2.5 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
                    <input 
                        type="checkbox"
                        checked={hideOwned}
                        onChange={(e) => setHideOwned(e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-slate-700">Hide items I already own</span>
                </label>
            </div>
        </div>

        {/* Add Item Modal/Form */}
        {showAddForm && (
            <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-white rounded-xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                    <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                        <h3 className="font-bold text-slate-800">Add to Wishlist</h3>
                        <button onClick={() => setShowAddForm(false)} className="p-1 hover:bg-slate-200 rounded-full">
                            <X className="w-5 h-5 text-slate-500" />
                        </button>
                    </div>
                    <form onSubmit={handleAddItem} className="p-6 space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500">Denomination *</label>
                                <input 
                                    className="w-full p-2 border border-slate-300 rounded-lg"
                                    placeholder="e.g. Quarter"
                                    value={newItem.denomination}
                                    onChange={e => setNewItem({...newItem, denomination: e.target.value})}
                                    required
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500">Year</label>
                                <input 
                                    className="w-full p-2 border border-slate-300 rounded-lg"
                                    placeholder="e.g. 1932"
                                    value={newItem.year || ''}
                                    onChange={e => setNewItem({...newItem, year: e.target.value})}
                                />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500">Series / Program</label>
                            <input 
                                className="w-full p-2 border border-slate-300 rounded-lg"
                                placeholder="e.g. American Women Quarters"
                                value={newItem.series || ''}
                                onChange={e => setNewItem({...newItem, series: e.target.value})}
                            />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500">Specific Design</label>
                            <input 
                                className="w-full p-2 border border-slate-300 rounded-lg"
                                placeholder="e.g. Maya Angelou"
                                value={newItem.design || ''}
                                onChange={e => setNewItem({...newItem, design: e.target.value})}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                             <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500">Max Budget ($)</label>
                                <input 
                                    type="number"
                                    className="w-full p-2 border border-slate-300 rounded-lg"
                                    placeholder="50.00"
                                    value={newItem.maxPrice || ''}
                                    onChange={e => setNewItem({...newItem, maxPrice: parseFloat(e.target.value)})}
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500">Priority</label>
                                <select 
                                    className="w-full p-2 border border-slate-300 rounded-lg"
                                    value={newItem.priority}
                                    onChange={e => setNewItem({...newItem, priority: e.target.value as any})}
                                >
                                    <option>High</option>
                                    <option>Medium</option>
                                    <option>Low</option>
                                </select>
                            </div>
                        </div>
                         <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500">Notes</label>
                            <textarea 
                                className="w-full p-2 border border-slate-300 rounded-lg resize-none"
                                rows={2}
                                value={newItem.notes || ''}
                                onChange={e => setNewItem({...newItem, notes: e.target.value})}
                            />
                        </div>
                        <div className="pt-2 flex justify-end gap-2">
                             <button type="button" onClick={() => setShowAddForm(false)} className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
                             <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Add to List</button>
                        </div>
                    </form>
                </div>
            </div>
        )}

        {/* Wishlist Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredWishlist.map(item => {
                const owned = checkOwnership(item);
                return (
                    <div key={item.id} className={`bg-white p-5 rounded-xl border shadow-sm transition-all hover:shadow-md relative group ${owned ? 'border-emerald-200 bg-emerald-50/30' : 'border-slate-200'}`}>
                        <div className="absolute top-4 right-4 flex gap-2">
                            {owned && (
                                <span className="bg-emerald-100 text-emerald-700 text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1">
                                    <CheckCircle className="w-3 h-3" /> In Collection
                                </span>
                            )}
                            <button 
                                onClick={() => handleDelete(item.id)}
                                className="text-slate-300 hover:text-red-500 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="mb-1">
                            <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                                item.priority === 'High' ? 'bg-red-100 text-red-700' :
                                item.priority === 'Medium' ? 'bg-amber-100 text-amber-700' :
                                'bg-slate-100 text-slate-600'
                            }`}>
                                {item.priority} Priority
                            </span>
                        </div>

                        <h3 className="font-bold text-lg text-slate-900 mt-2">{item.year || 'Any'} {item.denomination}</h3>
                        <p className="text-sm text-slate-600 font-medium">{item.series || item.design || item.country}</p>
                        
                        <div className="mt-4 flex flex-wrap gap-2 text-xs">
                             {item.maxPrice && (
                                <span className="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded text-slate-600">
                                    <DollarSign className="w-3 h-3" /> Max: ${item.maxPrice}
                                </span>
                             )}
                             {item.targetCondition && (
                                <span className="bg-slate-100 px-2 py-1 rounded text-slate-600">
                                    Grade: {item.targetCondition}
                                </span>
                             )}
                        </div>
                        {item.notes && (
                            <p className="mt-3 text-xs text-slate-500 italic border-t border-slate-100 pt-2">
                                "{item.notes}"
                            </p>
                        )}
                    </div>
                );
            })}
        </div>

        {filteredWishlist.length === 0 && (
            <div className="text-center py-12 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                <Gift className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Your wishlist is empty (or matches no filters).</p>
                <button onClick={() => setShowAddForm(true)} className="text-blue-600 hover:underline mt-2">Add your first item</button>
            </div>
        )}
      </div>

      {/* Print View (Hidden on Screen) */}
      <div className="hidden print:block fixed inset-0 bg-white z-[100] p-8 overflow-y-auto">
        <div className="mb-8 border-b-2 border-black pb-4">
            <h1 className="text-3xl font-bold uppercase tracking-wider mb-2">My Coin Wishlist</h1>
            <p className="text-sm">Generated on {new Date().toLocaleDateString()}</p>
        </div>

        <table className="w-full text-sm border-collapse">
            <thead>
                <tr className="border-b-2 border-black text-left">
                    <th className="py-2 w-16 text-center border-r border-slate-300">Priority</th>
                    <th className="py-2 pl-4 border-r border-slate-300">Item Details</th>
                    <th className="py-2 pl-4 border-r border-slate-300">Max Budget</th>
                    <th className="py-2 pl-4 border-r border-slate-300">Status</th>
                    <th className="py-2 pl-4">Notes</th>
                </tr>
            </thead>
            <tbody>
                {filteredWishlist.map((item) => {
                    const owned = checkOwnership(item);
                    return (
                        <tr key={item.id} className="border-b border-slate-200 break-inside-avoid">
                            <td className="py-3 text-center border-r border-slate-300 font-bold text-xs uppercase">
                                {item.priority}
                            </td>
                            <td className="py-3 pl-4 border-r border-slate-300">
                                <div className="font-bold">{item.year || 'Any Year'} {item.denomination}</div>
                                <div className="text-xs">{item.series || item.design}</div>
                                {item.targetCondition && <div className="text-xs italic">Pref: {item.targetCondition}</div>}
                            </td>
                            <td className="py-3 pl-4 border-r border-slate-300">
                                {item.maxPrice ? `$${item.maxPrice}` : '-'}
                            </td>
                            <td className="py-3 pl-4 border-r border-slate-300 text-xs">
                                {owned ? (
                                    <span className="font-bold text-emerald-700">[X] In Collection</span>
                                ) : (
                                    <span className="text-slate-400">[ ] Need</span>
                                )}
                            </td>
                            <td className="py-3 pl-4 text-xs italic">
                                {item.notes}
                            </td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
      </div>
    </div>
  );
};