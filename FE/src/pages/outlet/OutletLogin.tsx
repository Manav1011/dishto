import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

const OutletLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const { outlet_slug } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login({ email, password });
      
      const from = (location.state as any)?.from?.pathname;
      
      if (from) {
        navigate(from, { replace: true });
      } else {
        navigate(`/${outlet_slug}/admin`, { replace: true });
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-10 flex items-center justify-center min-h-screen bg-slate-50 relative overflow-hidden">
      {/* Background orbs */}
      <div className="absolute -top-24 -left-24 w-96 h-96 bg-orange-500/5 rounded-full blur-[100px]" />
      <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-blue-500/5 rounded-full blur-[100px]" />

      <div className="w-full max-w-md glass p-10 rounded-[2.5rem] border border-white shadow-2xl relative z-10">
        <div className="mb-8">
           <h2 className="text-3xl font-brand font-black text-slate-900 tracking-tight capitalize">
             Branch Login
           </h2>
           <p className="text-slate-500 mt-1 font-medium">Access your branch command center.</p>
           {outlet_slug && (
             <code className="text-[10px] font-bold text-orange-500 uppercase tracking-widest mt-2 block bg-orange-50 px-2 py-1 rounded inline-block border border-orange-100 truncate">
               {outlet_slug}
             </code>
           )}
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-rose-50 text-rose-600 rounded-2xl text-sm border border-rose-100 animate-in fade-in zoom-in duration-300 flex items-center gap-3">
            <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-1">Email Address</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@dishto.in" 
              className="w-full px-6 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 transition-all font-medium" 
            />
          </div>
          <div className="space-y-2">
            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-1">Secure Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••" 
              className="w-full px-6 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 transition-all font-medium" 
            />
          </div>
          
          <button 
            disabled={loading}
            className={`w-full py-4 bg-orange-500 text-white rounded-2xl font-bold orange-glow tactile mt-4 flex items-center justify-center gap-2 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : 'Authenticate Access'}
          </button>
        </form>

        <div className="mt-10 text-center border-t border-slate-100 pt-8">
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">
             <a href="/admin/login" className="text-orange-500 hover:underline">Franchise Portal</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default OutletLogin;
