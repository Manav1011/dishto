import React, { useState } from 'react';
import { X, Check, Building2, Mail, ArrowRight, Loader2 } from 'lucide-react';
import api from '../../api';

interface CreateFranchiseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateFranchiseModal = ({ isOpen, onClose, onSuccess }: CreateFranchiseModalProps) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [franchiseName, setFranchiseName] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const [franchiseSlug, setFranchiseSlug] = useState('');

  if (!isOpen) return null;

  const handleCreateFranchise = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Step 1: Create Franchise
      const response = await api.post('/protected/restaurant/franchise/', null, {
        params: { name: franchiseName }
      });
      
      // The backend returns the created franchise object in response.data.data
      const slug = response.data.data?.slug;
      if (slug) {
        setFranchiseSlug(slug);
        setStep(2);
      } else {
        throw new Error('Failed to retrieve franchise identifier.');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create franchise.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Step 2: Create Franchise Admin
      await api.post('/protected/auth/admin/franchise', {
        email: adminEmail,
        slug: franchiseSlug
      });
      
      onSuccess();
      onClose();
      // Reset state for next time
      setStep(1);
      setFranchiseName('');
      setAdminEmail('');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to assign franchise admin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-lg bg-white rounded-[2.5rem] shadow-2xl border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-300">
        
        {/* Header */}
        <div className="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h2 className="text-2xl font-brand font-bold text-slate-900">Register Franchise</h2>
            <p className="text-slate-500 text-sm mt-1">Step {step} of 2: {step === 1 ? 'Core Information' : 'Admin Assignment'}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white hover:shadow-md rounded-xl text-slate-400 transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="h-1.5 w-full bg-slate-100 flex">
          <div className={`h-full bg-orange-500 transition-all duration-500 ${step === 1 ? 'w-1/2' : 'w-full'}`} />
        </div>

        <div className="p-8">
          {error && (
            <div className="mb-6 p-4 bg-rose-50 text-rose-600 rounded-2xl text-sm border border-rose-100 flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-rose-500" />
              {error}
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleCreateFranchise} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Brand Name</label>
                <div className="relative">
                  <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="text"
                    required
                    value={franchiseName}
                    onChange={(e) => setFranchiseName(e.target.value)}
                    placeholder="e.g. Dominos Pizza"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                  />
                </div>
                <p className="text-xs text-slate-400 ml-1">This will be used to generate the system identifiers.</p>
              </div>

              <button 
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  <>
                    Continue to Admin Setup
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleCreateAdmin} className="space-y-6">
              <div className="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 mb-6 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center text-white">
                   <Check className="w-5 h-5" />
                </div>
                <div>
                   <p className="text-xs font-bold text-emerald-700 uppercase tracking-tighter">Franchise Created</p>
                   <p className="text-sm font-medium text-emerald-600">{franchiseName} ({franchiseSlug})</p>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Admin Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="email"
                    required
                    value={adminEmail}
                    onChange={(e) => setAdminEmail(e.target.value)}
                    placeholder="owner@brand.com"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                  />
                </div>
                <p className="text-xs text-slate-400 ml-1">An invitation will be sent to this email to set up their password.</p>
              </div>

              <div className="flex gap-3 pt-2">
                <button 
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-4 glass text-slate-600 rounded-2xl font-bold border border-slate-200 tactile"
                >
                  Back
                </button>
                <button 
                  type="submit"
                  disabled={loading}
                  className="flex-[2] py-4 bg-orange-500 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                    <>
                      Complete Registration
                      <Check className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateFranchiseModal;
