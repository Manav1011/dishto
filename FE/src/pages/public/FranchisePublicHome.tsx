import { useState, useEffect } from 'react';
import api from '../../api';
import { getSubdomain } from '../../utils/subdomain';
import { 
  Store, 
  MapPin, 
  ArrowRight, 
  Clock, 
  Loader2,
  Building2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Franchise {
  name: string;
  slug: string;
}

interface Outlet {
  name: string;
  slug: string;
  cover_image: string | null;
}

const FranchisePublicHome = () => {
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [franchise, setFranchise] = useState<Franchise | null>(null);
  const [loading, setLoading] = useState(true);
  const subdomain = getSubdomain();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch combined data via modified open endpoint
        const response = await api.get('/open/');
        // Response structure: { status, data: { franchise: {...}, outlets: [...] } }
        const { franchise, outlets } = response.data.data || {};
        
        setFranchise(franchise || null);
        setOutlets(outlets || []);
      } catch (err) {
        console.error('Failed to load public brand data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [subdomain]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
          <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Loading Experience...</p>
        </div>
      </div>
    );
  }

  const brandName = franchise?.name || subdomain || 'Franchise';

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative px-6 py-24 md:py-32 overflow-hidden border-b border-slate-50 text-center">
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-orange-500/5 rounded-full blur-[150px] -z-10 translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[120px] -z-10 -translate-x-1/2 translate-y-1/2" />

        <div className="max-w-7xl mx-auto">
          <div className="mb-6 inline-flex px-4 py-1.5 rounded-full bg-slate-900 text-white text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-slate-900/20 animate-in fade-in slide-in-from-top-4 duration-700">
             Official Digital Storefront
          </div>
          <h1 className="text-6xl md:text-8xl font-brand font-black text-slate-900 tracking-tighter mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
            {brandName}<span className="text-orange-500">.</span>
          </h1>
          <p className="text-slate-500 text-xl md:text-2xl max-w-2xl mx-auto leading-relaxed animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200 font-medium">
            Explore our curated menu and enjoy seamless digital ordering across all locations.
          </p>
        </div>
      </section>

      {/* Outlet Selection */}
      <section className="px-6 py-20 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-12">
           <h2 className="text-3xl font-brand font-bold text-slate-800 flex items-center gap-3">
              <Store className="w-8 h-8 text-orange-500" />
              Our Locations
           </h2>
           <div className="hidden md:flex items-center gap-2 text-slate-400 font-bold text-[10px] uppercase tracking-widest">
              Showing {outlets.length} active outlets
           </div>
        </div>

        {outlets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {outlets.map((outlet, idx) => (
              <div 
                key={outlet.slug} 
                onClick={() => navigate(`/${outlet.slug}`)}
                className="group cursor-pointer animate-in fade-in slide-in-from-bottom-8 duration-700"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="relative aspect-[4/3] rounded-[3rem] overflow-hidden shadow-2xl mb-6 bg-slate-100 border border-slate-100">
                  {outlet.cover_image ? (
                    <img 
                      src={outlet.cover_image} 
                      alt={outlet.name}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                       <Building2 className="w-16 h-16 text-slate-200" />
                    </div>
                  )}
                  
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/0 to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />
                  
                  <div className="absolute top-6 right-6">
                     <div className="glass px-4 py-2 rounded-2xl flex items-center gap-2 text-white text-xs font-bold shadow-xl border-white/20">
                        <Clock className="w-3.5 h-3.5 text-orange-400" />
                        Open Now
                     </div>
                  </div>

                  <div className="absolute bottom-8 left-8 right-8">
                     <h3 className="text-2xl font-brand font-black text-white tracking-tight drop-shadow-lg">
                        {outlet.name}
                     </h3>
                     <div className="flex items-center gap-2 text-white/80 text-sm font-medium mt-1">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>Visit Store</span>
                     </div>
                  </div>
                </div>

                <div className="flex items-center justify-between px-4">
                   <div className="flex flex-col">
                      <span className="text-[10px] font-black text-orange-500 uppercase tracking-widest">Premium Outlet</span>
                      <span className="text-slate-400 text-xs font-medium">Digital Ordering Enabled</span>
                   </div>
                   <div className="w-12 h-12 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-400 group-hover:bg-orange-500 group-hover:text-white transition-all tactile shadow-sm">
                      <ArrowRight className="w-5 h-5" />
                   </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-32 text-center bg-slate-50/50 rounded-[4rem] border border-dashed border-slate-200">
             <div className="max-w-sm mx-auto flex flex-col items-center gap-6">
                <div className="w-24 h-24 rounded-[2.5rem] bg-white shadow-xl flex items-center justify-center text-slate-200">
                   <Building2 className="w-12 h-12" />
                </div>
                <div>
                   <h3 className="text-2xl font-brand font-bold text-slate-900">No Locations Found</h3>
                   <p className="text-slate-500 mt-2 leading-relaxed font-medium">
                      We're currently preparing our digital presence for this brand. Check back soon!
                   </p>
                </div>
             </div>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 border-t border-slate-50 mt-auto">
         <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-2">
               <span className="font-brand font-black text-2xl text-slate-900">{brandName}</span>
               <span className="text-slate-300">×</span>
               <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Powered by Dishto</span>
            </div>
            <div className="flex gap-8 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
               <a href="#" className="hover:text-orange-500 transition-colors">Privacy</a>
               <a href="#" className="hover:text-orange-500 transition-colors">Terms</a>
               <a href="#" className="hover:text-orange-500 transition-colors">Support</a>
            </div>
         </div>
      </footer>
    </div>
  );
};

export default FranchisePublicHome;
