import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Lock, ShieldCheck, CheckCircle2, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import api from '../../api';

const SetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const slug = searchParams.get('slug');
  const code = searchParams.get('code');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!slug || !code) {
      setError('Invalid or expired invitation link. Please contact your administrator.');
    }
  }, [slug, code]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post('/protected/auth/set-password', {
        password,
        code,
        slug
      });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to set password. This link may have already been used.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[120px] -z-10 translate-x-1/3 -translate-y-1/3" />
      
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
           <div className="inline-flex p-4 bg-white rounded-3xl shadow-xl border border-slate-100 mb-6 tactile">
              <ShieldCheck className="w-10 h-10 text-orange-500" />
           </div>
           <h1 className="text-4xl font-brand font-black text-slate-900 tracking-tighter">
              Establish Access<span className="text-orange-500">.</span>
           </h1>
           <p className="text-slate-500 mt-2 font-medium">Configure your secure administrative credentials.</p>
        </div>

        <div className="bg-white rounded-[2.5rem] border border-slate-200 p-10 shadow-2xl shadow-slate-200/50 relative overflow-hidden">
          {success ? (
            <div className="text-center py-4 animate-in zoom-in duration-500">
               <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-500" />
               </div>
               <h2 className="text-2xl font-brand font-bold text-slate-900 mb-2">Password Established</h2>
               <p className="text-slate-500 mb-8 leading-relaxed">Your account is now active. Redirecting you to login...</p>
               <button 
                 onClick={() => navigate('/login')}
                 className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile"
               >
                  Go to Login
                  <ArrowRight className="w-5 h-5" />
               </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-4 bg-rose-50 text-rose-600 rounded-2xl text-sm border border-rose-100 flex items-center gap-3">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="font-medium">{error}</span>
                </div>
              )}

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1 text-left block">New Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="password"
                    required
                    disabled={!slug || !code}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 transition-all font-medium"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1 text-left block">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="password"
                    required
                    disabled={!slug || !code}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 transition-all font-medium"
                  />
                </div>
              </div>

              <button 
                type="submit"
                disabled={loading || !slug || !code}
                className="w-full py-4 bg-orange-500 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  <>
                    Complete Setup
                    <CheckCircle2 className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>
          )}
        </div>
        
        <p className="text-center mt-10 text-slate-400 text-xs font-bold uppercase tracking-widest leading-relaxed">
           Dishto Secure Enrollment System
        </p>
      </div>
    </div>
  );
};

export default SetPassword;
