
import React, { useState, useMemo } from 'react';
import { Coin } from '../types';
import { Filter, Printer, CheckCircle, XCircle, Circle, Save, Calendar, Search, Download } from 'lucide-react';

interface InventoryPageProps {
  coins: Coin[];
  onBatchUpdate: (updatedCoins: Coin[]) => void;
}

export const InventoryPage: React.FC<InventoryPageProps> = ({ coins, onBatchUpdate }) => {
  // --- Filters State ---
  const [filterCountry, setFilterCountry] = useState('');
  const [filterSeries, setFilterSeries] = useState<string[]>([]); // Multi-select
  const [filterDenom, setFilterDenom] = useState('');
  const [filterMinValue, setFilterMinValue] = useState('');
  const [filterMaxValue, setFilterMaxValue] = useState('');
  const [isSeriesDropdownOpen, setIsSeriesDropdownOpen] = useState(false);

  // --- Derived Data ---
  const uniqueCountries = useMemo(() => Array.from(new Set(coins.map(c => c.country))).sort(), [coins]);
  const uniqueSeries = useMemo(() => Array.from(new Set(coins.map(c => c.series).filter(Boolean) as string[])).sort(), [coins]);
  const uniqueDenoms = useMemo(() => Array.from(new Set(coins.map(c => c.denomination))).sort(), [coins]);

  const filteredCoins = useMemo(() => {
    return coins.filter(coin => {
      const matchCountry = !filterCountry || coin.country === filterCountry;
      
      // Multi-select logic for Series
      const matchSeries = filterSeries.length === 0 || (coin.series && filterSeries.includes(coin.series));
      
      const matchDenom = !filterDenom || coin.denomination === filterDenom;
      
      const val = coin.estimatedValueMax || 0;
      const min = filterMinValue ? parseFloat(filterMinValue) : 0;
      const max = filterMaxValue ? parseFloat(filterMaxValue) : Infinity;
      const matchValue = val >= min && val <= max;

      return matchCountry && matchSeries && matchDenom && matchValue;
    }).sort((a, b) => {
        // Sort by year then denomination for inventory sheets
        if (a.year !== b.year) return a.year.localeCompare(b.year);
        return a.denomination.localeCompare(b.denomination);
    });
  }, [coins, filterCountry, filterSeries, filterDenom, filterMinValue, filterMaxValue]);

  const stats = useMemo(() => {
    const total = filteredCoins.length;
    const accounted = filteredCoins.filter(c => c.inventoryStatus === 'ACCOUNTED').length;
    const missing = filteredCoins.filter(c => c.inventoryStatus === 'MISSING').length;
    return { total, accounted, missing };
  }, [filteredCoins]);

  // --- Handlers ---

  const handleStatusChange = (coin: Coin, status: 'ACCOUNTED' | 'MISSING' | 'UNCHECKED') => {
    const updatedCoin = {
      ...coin,
      inventoryStatus: status,
      lastInventoried: new Date().toISOString()
    };
    onBatchUpdate([updatedCoin]);
  };

  const handleNotesChange = (coin: Coin, notes: string) => {
    const updatedCoin = {
      ...coin,
      inventoryNotes: notes
    };
    onBatchUpdate([updatedCoin]);
  };

  const markAllAccounted = () => {
    if (!window.confirm(`Mark all ${filteredCoins.length} listed coins as 'Accounted For'?`)) return;
    
    const updates = filteredCoins.map(c => ({
      ...c,
      inventoryStatus: 'ACCOUNTED' as const,
      lastInventoried: new Date().toISOString()
    }));
    onBatchUpdate(updates);
  };

  const toggleSeriesFilter = (series: string) => {
    setFilterSeries(prev => 
        prev.includes(series) 
            ? prev.filter(s => s !== series)
            : [...prev, series]
    );
  };

  // --- Download Printable HTML Logic ---
  const handleDownloadReport = () => {
    const dateStr = new Date().toLocaleDateString();
    
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Inventory Audit - ${dateStr}</title>
        <style>
          body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #1e293b; }
          h1 { text-transform: uppercase; letter-spacing: 1px; border-bottom: 3px solid #000; padding-bottom: 10px; }
          .meta { display: flex; justify-content: space-between; margin-bottom: 30px; font-size: 14px; }
          table { width: 100%; border-collapse: collapse; font-size: 12px; }
          th { text-align: left; border-bottom: 2px solid #000; padding: 10px; background: #f8fafc; text-transform: uppercase; font-size: 11px; }
          td { border-bottom: 1px solid #e2e8f0; padding: 10px; vertical-align: top; }
          .box { width: 16px; height: 16px; border: 1px solid #94a3b8; display: inline-block; }
          .status-col { text-align: center; width: 50px; }
          .footer { margin-top: 40px; border-top: 1px solid #000; padding-top: 20px; font-size: 12px; display: flex; justify-content: space-between; }
        </style>
      </head>
      <body>
        <h1>Inventory Audit Sheet</h1>
        <div class="meta">
          <div>
            <p><strong>Date:</strong> ${dateStr}</p>
            <p><strong>Total Items:</strong> ${filteredCoins.length}</p>
          </div>
          <div style="text-align: right;">
            <p><strong>Criteria:</strong> ${filterCountry || 'All Countries'}</p>
            <p><strong>Series:</strong> ${filterSeries.length > 0 ? filterSeries.join(', ') : 'All Series'}</p>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th class="status-col">Check</th>
              <th>Year / Mint</th>
              <th>Description</th>
              <th>Condition</th>
              <th>Est. Value</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            ${filteredCoins.map(c => `
              <tr>
                <td class="status-col"><span class="box"></span></td>
                <td><strong>${c.year}</strong> ${c.mintMark ? `(${c.mintMark})` : ''}</td>
                <td>
                  <strong>${c.denomination}</strong><br/>
                  ${c.series || c.design || c.country}
                </td>
                <td>${c.condition}</td>
                <td>${c.estimatedValueMax ? `$${c.estimatedValueMax.toLocaleString()}` : '-'}</td>
                <td>${c.inventoryNotes || ''}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <div class="footer">
          <div>Auditor Signature: _______________________</div>
          <div>Page 1 of 1</div>
        </div>
        
        <script>
           // Automatically trigger print when opened
           window.onload = function() { window.print(); }
        </script>
      </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Numisma_Inventory_${dateStr.replace(/\//g, '-')}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-20">
      
      {/* Controls */}
      <div className="space-y-6">
        <div className="flex justify-between items-start">
            <div>
                <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                    <Filter className="w-6 h-6 text-blue-600" />
                    Inventory Manager
                </h2>
                <p className="text-slate-500 mt-1">Generate lists, track condition, and audit your collection.</p>
            </div>
            <div className="flex gap-3">
                 <button 
                    onClick={handleDownloadReport}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 shadow-sm"
                 >
                    <Download className="w-4 h-4" />
                    Download Printable Report
                 </button>
            </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-500 uppercase">Country</label>
                <select 
                    value={filterCountry} 
                    onChange={e => setFilterCountry(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded-lg text-sm"
                >
                    <option value="">All Countries</option>
                    {uniqueCountries.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
            </div>
            
            {/* Multi-Select for Series */}
            <div className="space-y-1 relative">
                <label className="text-xs font-semibold text-slate-500 uppercase">Series / Type</label>
                <button 
                    onClick={() => setIsSeriesDropdownOpen(!isSeriesDropdownOpen)}
                    className="w-full p-2 border border-slate-300 rounded-lg text-sm text-left bg-white flex justify-between items-center"
                >
                    <span className="truncate">
                        {filterSeries.length === 0 ? 'All Series' : `${filterSeries.length} selected`}
                    </span>
                    <span className="text-xs text-slate-400">▼</span>
                </button>
                {isSeriesDropdownOpen && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-300 rounded-lg shadow-xl z-20 max-h-60 overflow-y-auto p-2">
                        {uniqueSeries.map(s => (
                            <label key={s} className="flex items-center gap-2 p-2 hover:bg-slate-50 cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    checked={filterSeries.includes(s)}
                                    onChange={() => toggleSeriesFilter(s)}
                                    className="rounded text-blue-600"
                                />
                                <span className="text-sm text-slate-700">{s}</span>
                            </label>
                        ))}
                    </div>
                )}
                {isSeriesDropdownOpen && (
                    <div className="fixed inset-0 z-10" onClick={() => setIsSeriesDropdownOpen(false)}></div>
                )}
            </div>

            <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-500 uppercase">Denomination</label>
                <select 
                    value={filterDenom} 
                    onChange={e => setFilterDenom(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded-lg text-sm"
                >
                    <option value="">All Denominations</option>
                    {uniqueDenoms.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
            </div>
            <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-500 uppercase">Min Value ($)</label>
                <input 
                    type="number"
                    value={filterMinValue}
                    onChange={e => setFilterMinValue(e.target.value)}
                    placeholder="0"
                    className="w-full p-2 border border-slate-300 rounded-lg text-sm"
                />
            </div>
             <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-500 uppercase">Max Value ($)</label>
                <input 
                    type="number"
                    value={filterMaxValue}
                    onChange={e => setFilterMaxValue(e.target.value)}
                    placeholder="Any"
                    className="w-full p-2 border border-slate-300 rounded-lg text-sm"
                />
            </div>
        </div>

        {/* Action Bar */}
        <div className="bg-slate-800 text-white p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-6">
                <div className="text-center px-4 border-r border-slate-600">
                    <p className="text-2xl font-bold">{stats.total}</p>
                    <p className="text-xs text-slate-400 uppercase">Items Listed</p>
                </div>
                 <div className="text-center px-4 border-r border-slate-600">
                    <p className="text-2xl font-bold text-emerald-400">{stats.accounted}</p>
                    <p className="text-xs text-slate-400 uppercase">Accounted</p>
                </div>
                 <div className="text-center px-4">
                    <p className="text-2xl font-bold text-red-400">{stats.missing}</p>
                    <p className="text-xs text-slate-400 uppercase">Missing</p>
                </div>
            </div>
            <button 
                onClick={markAllAccounted}
                disabled={filteredCoins.length === 0}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium shadow-lg transition-all flex items-center gap-2 disabled:opacity-50"
            >
                <CheckCircle className="w-5 h-5" />
                All Listed Accounted For
            </button>
        </div>

        {/* Live Inventory Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-medium">
                        <tr>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3">Coin Details</th>
                            <th className="px-4 py-3">Value</th>
                            <th className="px-4 py-3">Last Checked</th>
                            <th className="px-4 py-3 w-1/3">Inventory Notes</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredCoins.map(coin => (
                            <tr key={coin.id} className={coin.inventoryStatus === 'MISSING' ? 'bg-red-50' : coin.inventoryStatus === 'ACCOUNTED' ? 'bg-emerald-50/30' : ''}>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1">
                                        <button 
                                            onClick={() => handleStatusChange(coin, 'ACCOUNTED')}
                                            className={`p-1 rounded hover:bg-emerald-100 ${coin.inventoryStatus === 'ACCOUNTED' ? 'text-emerald-600' : 'text-slate-300'}`}
                                            title="Mark Accounted"
                                        >
                                            <CheckCircle className="w-6 h-6" />
                                        </button>
                                        <button 
                                            onClick={() => handleStatusChange(coin, 'MISSING')}
                                            className={`p-1 rounded hover:bg-red-100 ${coin.inventoryStatus === 'MISSING' ? 'text-red-600' : 'text-slate-300'}`}
                                            title="Mark Missing"
                                        >
                                            <XCircle className="w-6 h-6" />
                                        </button>
                                         <button 
                                            onClick={() => handleStatusChange(coin, 'UNCHECKED')}
                                            className={`p-1 rounded hover:bg-slate-100 ${coin.inventoryStatus === 'UNCHECKED' || !coin.inventoryStatus ? 'text-slate-400' : 'text-slate-200'}`}
                                            title="Reset"
                                        >
                                            <Circle className="w-6 h-6" />
                                        </button>
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <p className="font-bold text-slate-900">{coin.year} {coin.denomination}</p>
                                    <p className="text-slate-500 text-xs">{coin.country} {coin.mintMark ? `(${coin.mintMark})` : ''}</p>
                                    {coin.series && <p className="text-blue-600 text-xs mt-0.5">{coin.series}</p>}
                                    <p className="text-slate-400 text-xs mt-0.5">Grade: {coin.condition}</p>
                                </td>
                                <td className="px-4 py-3 font-mono">
                                    {coin.estimatedValueMax ? `$${coin.estimatedValueMax.toLocaleString()}` : '-'}
                                </td>
                                <td className="px-4 py-3 text-xs text-slate-500">
                                    {coin.lastInventoried ? (
                                        <div className="flex items-center gap-1">
                                            <Calendar className="w-3 h-3" />
                                            {new Date(coin.lastInventoried).toLocaleDateString()}
                                        </div>
                                    ) : (
                                        <span className="italic">Never</span>
                                    )}
                                </td>
                                <td className="px-4 py-3">
                                    <input 
                                        type="text" 
                                        placeholder="Add note..."
                                        className="w-full bg-transparent border-b border-transparent hover:border-slate-300 focus:border-blue-500 outline-none text-sm py-1"
                                        value={coin.inventoryNotes || ''}
                                        onChange={(e) => handleNotesChange(coin, e.target.value)}
                                    />
                                </td>
                            </tr>
                        ))}
                         {filteredCoins.length === 0 && (
                            <tr>
                                <td colSpan={5} className="p-8 text-center text-slate-400">
                                    No coins match your inventory filters.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
      </div>
    </div>
  );
};
