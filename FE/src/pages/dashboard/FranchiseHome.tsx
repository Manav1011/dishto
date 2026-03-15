import { useState, useEffect } from 'react';
import api from '../../api';
import { 
  Store, 
  TrendingUp, 
  ExternalLink, 
  ShieldCheck, 
  Loader2,
  Building2,
  ChevronRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface Outlet {
  name: string;
  slug: string;
  cover_image: string | null;
  // superadmin_approved: boolean; // Not in API yet, but planned
}

const FranchiseHome = () => {
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOutlets = async () => {
    setLoading(true);
    try {
      const response = await api.get('/protected/restaurant/outlet', {
        params: { slug: '__all__' }
      });
      // Response structure: { status, data: { outlets: [...] } }
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

  return (
    <div className="p-8 max-w-[1600px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Dashboard Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-brand font-bold text-slate-900">Brand Overview</h1>
          <p className="text-slate-500 mt-2 text-lg font-medium">Operational health and location management.</p>
        </div>
        

      </div>

      {/* Stats Pulse */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-orange-500/5 group-hover:bg-orange-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Total Outlets</p>
          <div className="flex items-end gap-2">
            <h2 className="text-4xl font-brand font-black text-slate-900">{outlets.length}</h2>
            <span className="text-emerald-500 text-xs font-bold mb-1.5 flex items-center">
              <TrendingUp className="w-3 h-3 mr-1" />
              Active
            </span>
          </div>
        </div>

        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-blue-500/5 group-hover:bg-blue-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Active Orders</p>
          <h2 className="text-4xl font-brand font-black text-slate-900">--</h2>
        </div>

        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-emerald-500/5 group-hover:bg-emerald-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Total Revenue</p>
          <h2 className="text-4xl font-brand font-black text-slate-900">--</h2>
        </div>

        <div className="p-8 glass rounded-[2.5rem] border border-white/60 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl bg-rose-500/5 group-hover:bg-rose-500/10 transition-colors" />
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Pending Invoices</p>
          <h2 className="text-4xl font-brand font-black text-slate-900">--</h2>
        </div>
      </div>

      {/* Outlet Command Center */}
      <div className="mb-8 flex items-center justify-between">
         <h2 className="text-2xl font-brand font-bold text-slate-800 flex items-center gap-3">
            <Store className="w-6 h-6 text-orange-500" />
            Location Command Center
         </h2>
         <Link to="/admin/outlets" className="text-orange-500 font-bold text-sm hover:underline flex items-center gap-1">
            View All Outlets
            <ChevronRight className="w-4 h-4" />
         </Link>
      </div>

      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center gap-4 bg-white rounded-[3rem] border border-slate-100 shadow-sm">
           <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
           <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px]">Syncing Locations...</p>
        </div>
      ) : outlets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {outlets.slice(0, 6).map((outlet) => (
            <div key={outlet.slug} className="bg-white rounded-[3rem] border border-slate-200 overflow-hidden shadow-xl shadow-slate-200/50 hover:border-orange-500/20 transition-all group p-4">
              <div className="relative aspect-video rounded-[2rem] overflow-hidden mb-6">
                {outlet.cover_image ? (
                  <img 
                    src={outlet.cover_image} 
                    alt={outlet.name}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                ) : (
                  <div className="w-full h-full bg-slate-50 flex items-center justify-center">
                    <Building2 className="w-12 h-12 text-slate-200" />
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-60" />
                <div className="absolute bottom-4 left-6">
                   <h3 className="text-xl font-brand font-black text-white tracking-tight">{outlet.name}</h3>
                </div>
              </div>

              <div className="px-2 space-y-6">
                <div className="flex items-center justify-between">
                   <div className="flex flex-col">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Identifier</span>
                      <code className="text-xs font-bold text-slate-600 mt-0.5">{outlet.slug}</code>
                   </div>
                   <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-black uppercase tracking-widest border border-emerald-100 shadow-sm shadow-emerald-500/5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Active
                   </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                   {['Menu', 'Orders', 'Stock'].map((mod) => (
                     <div key={mod} className="py-3 px-2 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col items-center gap-1">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{mod}</span>
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                     </div>
                   ))}
                </div>

                <button className="w-full py-4 glass text-slate-600 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-900 hover:text-white hover:border-slate-900 transition-all tactile group/btn">
                   Manage Operations
                   <ExternalLink className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-32 text-center bg-white rounded-[4rem] border border-slate-200 shadow-sm">
           <div className="max-w-sm mx-auto flex flex-col items-center gap-6">
              <div className="w-24 h-24 rounded-[2.5rem] bg-slate-50 flex items-center justify-center text-slate-200 shadow-inner">
                 <Store className="w-12 h-12" />
              </div>
              <div>
                 <h3 className="text-2xl font-brand font-bold text-slate-900">No Outlets Deployed</h3>
                 <p className="text-slate-500 mt-2 leading-relaxed font-medium">
                    You haven't added any physical locations to your brand network yet. Start by deploying your first outlet.
                 </p>
                 <Link 
                   to="/admin/outlets"
                   className="inline-flex mt-8 px-10 py-4 bg-orange-500 text-white rounded-2xl font-bold orange-glow tactile shadow-xl shadow-orange-500/20 items-center gap-2"
                 >
                   <Store className="w-5 h-5" />
                   Manage Locations
                 </Link>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};

export default FranchiseHome;
