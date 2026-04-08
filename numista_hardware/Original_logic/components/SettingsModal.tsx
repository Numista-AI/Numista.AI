
import React, { useState, useEffect } from 'react';
import { X, Save, Shield, Key, Activity, ShoppingCart, LogIn, Info } from 'lucide-react';
import { loginToPcgs } from '../services/pcgsService';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [pcgsToken, setPcgsToken] = useState('');
  const [numistaToken, setNumistaToken] = useState('');
  const [ebayClientId, setEbayClientId] = useState('');
  const [ebayClientSecret, setEbayClientSecret] = useState('');
  const [pcgsUser, setPcgsUser] = useState('');
  const [pcgsPass, setPcgsPass] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setPcgsToken(localStorage.getItem('pcgs_api_token') || '');
      setNumistaToken(localStorage.getItem('numista_api_key') || '');
      setEbayClientId(localStorage.getItem('ebay_client_id') || '');
      setEbayClientSecret(localStorage.getItem('ebay_client_secret') || '');
      setLoginError(null);
    }
  }, [isOpen]);

  const handlePcgsLogin = async () => {
      if (!pcgsUser || !pcgsPass) {
          setLoginError("Please enter your PCGS Email and Password.");
          return;
      }
      setIsLoggingIn(true);
      setLoginError(null);
      try {
          const token = await loginToPcgs(pcgsUser, pcgsPass);
          setPcgsToken(token);
          setPcgsUser('');
          setPcgsPass('');
          localStorage.setItem('pcgs_api_token', token);
      } catch (err: any) {
          setLoginError(err.message || "Could not connect to PCGS.");
      } finally {
          setIsLoggingIn(false);
      }
  };

  const handleSave = () => {
    localStorage.setItem('pcgs_api_token', pcgsToken.trim());
    localStorage.setItem('numista_api_key', numistaToken.trim());
    localStorage.setItem('ebay_client_id', ebayClientId.trim());
    localStorage.setItem('ebay_client_secret', ebayClientSecret.trim());
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/70 backdrop-blur-md flex items-center justify-center z-[80] p-4 animate-in fade-in duration-300">
      <div className="bg-white rounded-[2.5rem] max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl flex flex-col">
        
        <div className="p-8 border-b border-slate-100 flex justify-between items-center bg-slate-50 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-slate-900 text-white rounded-2xl shadow-xl shadow-slate-200">
                <Shield className="w-6 h-6" />
            </div>
            <div>
                <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight">App Settings</h3>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest opacity-60">Manage your connections</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-10 space-y-12">
            {/* Marketplace Connections */}
            <div className="space-y-6">
                <h4 className="font-black text-slate-800 flex items-center gap-2 text-blue-600 uppercase text-xs tracking-widest">
                    <ShoppingCart className="w-4 h-4" />
                    Market Value Connections
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                     <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">eBay Client ID</label>
                        <input 
                            type="text" 
                            value={ebayClientId}
                            onChange={(e) => setEbayClientId(e.target.value)}
                            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs outline-none focus:ring-2 focus:ring-blue-500 transition-all font-mono"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Numista Key</label>
                        <input 
                            type="text" 
                            value={numistaToken}
                            onChange={(e) => setNumistaToken(e.target.value)}
                            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs outline-none focus:ring-2 focus:ring-blue-500 transition-all font-mono"
                        />
                    </div>
                </div>
            </div>

            <div className="border-t border-slate-100"></div>

            {/* PCGS Section */}
            <div className="space-y-6">
                <h4 className="font-black text-slate-800 flex items-center gap-2 uppercase text-xs tracking-widest">
                    <Key className="w-4 h-4 text-slate-600" />
                    PCGS Grading Account
                </h4>
                <div className="bg-slate-50 p-8 rounded-[2rem] border border-slate-200 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                     <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Email Address</label>
                        <input type="text" value={pcgsUser} onChange={(e) => setPcgsUser(e.target.value)} className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl" />
                     </div>
                     <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Password</label>
                        <input type="password" value={pcgsPass} onChange={(e) => setPcgsPass(e.target.value)} className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl" />
                     </div>
                     <button 
                        onClick={handlePcgsLogin}
                        disabled={isLoggingIn || !pcgsUser || !pcgsPass}
                        className="md:col-span-2 py-5 bg-slate-900 text-white rounded-2xl font-black uppercase text-xs tracking-widest flex items-center justify-center gap-3 disabled:opacity-50 hover:bg-black transition-all shadow-xl active:scale-95"
                     >
                        {isLoggingIn ? <Activity className="w-5 h-5 animate-spin" /> : <LogIn className="w-5 h-5" />}
                        Connect My PCGS Account
                     </button>
                </div>
                {loginError && <p className="text-[10px] text-red-500 font-bold uppercase text-center animate-pulse">{loginError}</p>}
            </div>
        </div>

        <div className="bg-slate-50 p-10 flex justify-end gap-3 border-t border-slate-100">
          <button onClick={handleSave} className="px-16 py-5 bg-blue-600 text-white font-black rounded-2xl hover:bg-blue-700 transition-all shadow-2xl shadow-blue-200 flex items-center gap-3 uppercase text-xs tracking-widest active:scale-95">
            <Save className="w-5 h-5" />
            Apply Changes
          </button>
        </div>
      </div>
    </div>
  );
};
