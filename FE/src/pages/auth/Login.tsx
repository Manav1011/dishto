import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { getSubdomain } from '../../utils/subdomain';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const subdomain = getSubdomain();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login({ email, password });
      // Redirect handled by user's role in App.tsx or here
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-10 flex items-center justify-center min-h-screen">
      <div className="w-full max-w-md glass p-10 rounded-[2.5rem] border border-slate-200 shadow-2xl">
        <h2 className="text-3xl font-brand mb-2 capitalize">
          {subdomain === 'admin' ? 'Superadmin' : subdomain || 'Partner'} Login
        </h2>
        <p className="text-slate-500 mb-8">Enter your credentials to manage your dashboard.</p>
        
        {error && (
          <div className="mb-6 p-4 bg-rose-50 text-rose-600 rounded-xl text-sm border border-rose-100 animate-in fade-in zoom-in duration-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-2 ml-1 uppercase tracking-wider">Email Address</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@dishto.in" 
              className="w-full px-5 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all" 
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-2 ml-1 uppercase tracking-wider">Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••" 
              className="w-full px-5 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all" 
            />
          </div>
          
          <button 
            disabled={loading}
            className={`w-full py-4 bg-orange-500 text-white rounded-xl font-medium orange-glow tactile mt-4 flex items-center justify-center gap-2 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-slate-400 text-sm">
            Lost your credentials? <a href="#" className="text-orange-500 font-medium hover:underline">Request Reset</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
