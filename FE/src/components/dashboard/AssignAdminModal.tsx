import React, { useState } from 'react';
import { X, Check, Mail, Loader2, ShieldCheck, Store } from 'lucide-react';
import api from '../../api';

interface Outlet {
  name: string;
  slug: string;
}

interface AssignAdminModalProps {
  isOpen: boolean;
  onClose: () => void;
  outlets: Outlet[];
  onSuccess: () => void;
}

const AssignAdminModal = ({ isOpen, onClose, outlets, onSuccess }: AssignAdminModalProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [selectedOutlet, setSelectedOutlet] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.post('/protected/auth/admin/outlet', {
        email,
        slug: selectedOutlet
      });
      onSuccess();
      onClose();
      setEmail('');
      setSelectedOutlet('');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to assign manager. Ensure the email is valid.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-md bg-white rounded-[2.5rem] shadow-2xl border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-300">
        
        {/* Header */}
        <div className="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h2 className="text-2xl font-brand font-bold text-slate-900">Invite Manager</h2>
            <p className="text-slate-500 text-sm mt-1">Assign an administrator to an outlet.</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white hover:shadow-md rounded-xl text-slate-400 transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          {error && (
            <div className="p-4 bg-rose-50 text-rose-600 rounded-2xl text-sm border border-rose-100 flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-rose-500" />
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Target Outlet</label>
            <div className="relative">
              <Store className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300 pointer-events-none" />
              <select
                required
                value={selectedOutlet}
                onChange={(e) => setSelectedOutlet(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 appearance-none font-medium text-slate-700"
              >
                <option value="">Select a location...</option>
                {outlets.map(o => (
                  <option key={o.slug} value={o.slug}>{o.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Admin Email</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
              <input 
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="manager@example.com"
                className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 transition-all font-medium"
              />
            </div>
            <p className="text-[10px] text-slate-400 ml-1">They will receive an invitation to set up their password.</p>
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
              <>
                Send Invitation
                <Check className="w-5 h-5" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AssignAdminModal;
