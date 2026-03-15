import { useState, useEffect } from 'react';
import api from '../../api';
import { 
  Store, 
  Plus, 
  Search, 
  ExternalLink, 
  ShieldCheck, 
  Loader2,
  Building2,
  Filter,
  MoreVertical
} from 'lucide-react';
import CreateOutletModal from '../../components/dashboard/CreateOutletModal';

interface Outlet {
  name: string;
  slug: string;
  cover_image: string | null;
}

const ManageOutlets = () => {
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchOutlets = async () => {
    setLoading(true);
    try {
      const response = await api.get('/protected/restaurant/outlet', {
        params: { slug: '__all__' }
      });
      setOutlets(response.data.data?.outlets || []);
    } catch (err) {
      console.error('Failed to fetch outlets', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOutlets();
  }, []);

  const filtered = outlets.filter(o => 
    o.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    o.slug.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8 max-w-[1600px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-brand font-bold text-slate-900 flex items-center gap-3">
            <Store className="w-10 h-10 text-orange-500" />
            Brand Locations
          </h1>
          <p className="text-slate-500 mt-2 text-lg font-medium">Detailed management of your physical outlet network.</p>
        </div>
        
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-8 py-4 bg-slate-900 text-white rounded-[1.25rem] font-bold orange-glow tactile shadow-2xl shadow-slate-900/20"
        >
          <Plus className="w-5 h-5" />
          Deploy New Outlet
        </button>
      </div>

      <div className="bg-white rounded-[2.5rem] border border-slate-200 overflow-hidden shadow-2xl shadow-slate-200/50">
        <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row items-center justify-between bg-slate-50/50 gap-4">
           <div className="relative w-full max-w-xl">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
              <input 
                type="text" 
                placeholder="Search by outlet name or identifier..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-white focus:outline-none focus:ring-4 focus:ring-orange-500/5 focus:border-orange-500/20 transition-all font-medium"
              />
           </div>
           
           <div className="flex items-center gap-2 w-full md:w-auto">
              <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-4 glass rounded-2xl text-slate-600 font-bold border border-slate-200 tactile">
                 <Filter className="w-4 h-4" />
                 Filter
              </button>
              <button 
                onClick={fetchOutlets}
                className="p-4 text-slate-400 hover:text-orange-500 hover:bg-white hover:shadow-md rounded-2xl transition-all tactile border border-transparent"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M3 21v-5h5"/></svg>
                )}
              </button>
           </div>
        </div>

        <div className="overflow-x-auto min-h-[400px] flex flex-col">
          <table className="w-full min-w-[1000px] text-left">
            <thead>
              <tr className="bg-slate-50/50 border-b border-slate-100">
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Outlet Identity</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Identifier</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Active Modules</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Status</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {loading && outlets.length === 0 ? (
                [1, 2, 3, 4].map(i => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={5} className="px-8 py-10 h-28 bg-slate-50/20" />
                  </tr>
                ))
              ) : filtered.length > 0 ? (
                filtered.map((o) => (
                  <tr key={o.slug} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-8 py-8">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-[1.5rem] bg-slate-100 overflow-hidden border border-slate-200 shadow-sm group-hover:scale-105 transition-transform">
                          {o.cover_image ? (
                            <img src={o.cover_image} alt={o.name} className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-slate-300">
                               <Building2 className="w-6 h-6" />
                            </div>
                          )}
                        </div>
                        <div>
                          <p className="font-bold text-slate-900 group-hover:text-orange-600 transition-colors text-lg">{o.name}</p>
                          <div className="flex items-center gap-2 mt-1">
                             <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                             <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Operational</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-8">
                      <code className="px-3 py-1.5 bg-slate-100 rounded-lg text-slate-600 text-xs font-bold border border-slate-200">
                        {o.slug}
                      </code>
                    </td>
                    <td className="px-8 py-8">
                       <div className="flex gap-1.5">
                          {['Menu', 'Orders', 'Inventory'].map(m => (
                            <div key={m} className="px-2.5 py-1 bg-slate-50 rounded-md border border-slate-100 text-[9px] font-black text-slate-400 uppercase tracking-tighter">
                               {m}
                            </div>
                          ))}
                       </div>
                    </td>
                    <td className="px-8 py-8">
                      <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-black uppercase tracking-widest border border-emerald-100 shadow-sm shadow-emerald-500/5">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Verified
                      </span>
                    </td>
                    <td className="px-8 py-8 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button className="p-3 hover:bg-white hover:text-orange-500 hover:shadow-xl rounded-[1.25rem] text-slate-400 transition-all tactile border border-transparent hover:border-slate-100">
                          <ExternalLink className="w-5 h-5" />
                        </button>
                        <button className="p-3 hover:bg-white hover:text-slate-900 hover:shadow-xl rounded-[1.25rem] text-slate-400 transition-all tactile border border-transparent hover:border-slate-100">
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : null}
            </tbody>
          </table>
          
          {(!loading || outlets.length > 0) && filtered.length === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center py-32 text-center">
              <div className="w-24 h-24 rounded-[3rem] bg-slate-50 flex items-center justify-center text-slate-200 mb-8 shadow-inner relative">
                 <Store className="w-12 h-12" />
                 <div className="absolute -top-1 -right-1 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-sm border border-slate-100">
                    <Search className="w-4 h-4 text-slate-300" />
                 </div>
              </div>
              <h3 className="text-2xl font-brand font-bold text-slate-900">
                {outlets.length === 0 ? 'No outlets deployed' : 'No results found'}
              </h3>
              <p className="text-slate-500 text-base leading-relaxed max-w-xs mt-3 font-medium">
                {outlets.length === 0 
                  ? 'Your brand currently has no physical locations registered. Start by deploying your first outlet.' 
                  : `We couldn't find any location matching "${searchTerm}".`}
              </p>
              {outlets.length === 0 && (
                <button 
                  onClick={() => setIsModalOpen(true)}
                  className="mt-10 px-10 py-4 bg-orange-500 text-white rounded-2xl font-bold orange-glow tactile shadow-xl shadow-orange-500/20 flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Add First Outlet
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      <CreateOutletModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchOutlets}
      />
    </div>
  );
};

export default ManageOutlets;
