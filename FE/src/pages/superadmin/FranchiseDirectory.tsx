import { useState, useEffect } from 'react';
import api from '../../api';
import { Plus, Building2, Search, ExternalLink, ShieldCheck, Loader2 } from 'lucide-react';
import CreateFranchiseModal from '../../components/superadmin/CreateFranchiseModal';

interface Franchise {
  id: number;
  name: string;
  slug: string;
}

const FranchiseDirectory = () => {
  const [franchises, setFranchises] = useState<Franchise[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchFranchises = async () => {
    setLoading(true);
    try {
      const response = await api.get('/protected/restaurant/franchise', {
        params: { slug: '__all__' }
      });
      setFranchises(response.data.data?.franchises || []);
    } catch (err) {
      console.error('Failed to fetch franchises', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFranchises();
  }, []);

  const filtered = franchises.filter(f => 
    f.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    f.slug.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8 max-w-[1600px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-brand font-bold text-slate-900 flex items-center gap-3">
            <Building2 className="w-10 h-10 text-orange-500" />
            Franchise Network
          </h1>
          <p className="text-slate-500 mt-2 text-lg font-medium">Centralized orchestration of all registered brand partners.</p>
        </div>
        
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-8 py-4 bg-slate-900 text-white rounded-[1.25rem] font-bold orange-glow tactile shadow-2xl shadow-slate-900/20"
        >
          <Plus className="w-5 h-5" />
          Register New Franchise
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-orange-500/5 group-hover:bg-orange-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Total Franchises</p>
          <h2 className="text-4xl font-brand font-black text-slate-900">{franchises.length}</h2>
        </div>
        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-emerald-500/5 group-hover:bg-emerald-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Active Outlets</p>
          <h2 className="text-4xl font-brand font-black text-slate-900">--</h2>
        </div>
        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-blue-500/5 group-hover:bg-blue-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Pending Requests</p>
          <h2 className="text-4xl font-brand font-black text-slate-900">--</h2>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-white rounded-[2.5rem] border border-slate-200 overflow-hidden shadow-2xl shadow-slate-200/50">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
           <div className="relative w-full max-w-xl">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
              <input 
                type="text" 
                placeholder="Search by name or slug..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-white focus:outline-none focus:ring-4 focus:ring-orange-500/5 focus:border-orange-500/20 transition-all font-medium"
              />
           </div>
           
           <button 
             onClick={fetchFranchises}
             className="p-3 text-slate-400 hover:text-orange-500 hover:bg-white hover:shadow-md rounded-xl transition-all tactile"
           >
             {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
               <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M3 21v-5h5"/></svg>
             )}
           </button>
        </div>

        <div className="overflow-x-auto min-h-[400px] flex flex-col">
          <table className="w-full min-w-[800px] text-left">
            <thead>
              <tr className="bg-slate-50/50 border-b border-slate-100">
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Franchise Name</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Identifier (Slug)</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Status</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {loading && franchises.length === 0 ? (
                [1, 2, 3, 4].map(i => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={4} className="px-8 py-8 h-24 bg-slate-50/20" />
                  </tr>
                ))
              ) : filtered.length > 0 ? (
                filtered.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-8 py-7">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-orange-50 border border-orange-100 flex items-center justify-center text-orange-600 font-bold shadow-sm group-hover:scale-110 transition-transform">
                          {f.name[0]}
                        </div>
                        <div>
                          <p className="font-bold text-slate-900 group-hover:text-orange-600 transition-colors">{f.name}</p>
                          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Franchise Partner</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-7">
                      <code className="px-3 py-1.5 bg-slate-100 rounded-lg text-slate-600 text-xs font-bold border border-slate-200">
                        {f.slug}
                      </code>
                    </td>
                    <td className="px-8 py-7">
                      <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-black uppercase tracking-widest border border-emerald-100 shadow-sm shadow-emerald-500/5">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Verified
                      </span>
                    </td>
                    <td className="px-8 py-7 text-right">
                      <button className="p-3 hover:bg-white hover:text-orange-500 hover:shadow-xl rounded-[1.25rem] text-slate-400 transition-all tactile border border-transparent hover:border-slate-100">
                        <ExternalLink className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : null}
            </tbody>
          </table>
          
          {(!loading || franchises.length > 0) && filtered.length === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center py-24 text-center">
              <div className="w-20 h-20 rounded-[2.5rem] bg-slate-50 flex items-center justify-center text-slate-200 mb-6 shadow-inner">
                 <Building2 className="w-10 h-10" />
              </div>
              <h3 className="text-2xl font-brand font-bold text-slate-900">
                {franchises.length === 0 ? 'No franchises registered' : 'No results found'}
              </h3>
              <p className="text-slate-500 text-base leading-relaxed max-w-xs mt-2 font-medium">
                {franchises.length === 0 
                  ? 'Your network is currently empty. Start by registering your first brand partner.' 
                  : `We couldn't find any franchise matching "${searchTerm}".`}
              </p>
              {franchises.length === 0 && (
                <button 
                  onClick={() => setIsModalOpen(true)}
                  className="mt-8 px-10 py-4 bg-orange-500 text-white rounded-2xl font-bold orange-glow tactile shadow-xl shadow-orange-500/20"
                >
                  Add First Franchise
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      <CreateFranchiseModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchFranchises}
      />
    </div>
  );
};

export default FranchiseDirectory;
