import { useState, useEffect } from 'react';
import api from '../../api';
import { 
  Users, 
  Store, 
  Mail, 
  ShieldCheck, 
  Loader2,
  Building2,
  ChevronRight,
  UserPlus
} from 'lucide-react';
import AssignAdminModal from '../../components/dashboard/AssignAdminModal';

interface Outlet {
  name: string;
  slug: string;
  admin?: {
    email: string;
    first_name?: string | null;
    last_name?: string | null;
  } | null;
}

const TeamManagement = () => {
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [loading, setLoading] = useState(true);
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

  return (
    <div className="p-8 max-w-[1600px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-brand font-bold text-slate-900 flex items-center gap-3">
            <Users className="w-10 h-10 text-orange-500" />
            Operational Team
          </h1>
          <p className="text-slate-500 mt-2 text-lg font-medium">Manage and assign administrators for your restaurant locations.</p>
        </div>
        
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-8 py-4 bg-slate-900 text-white rounded-[1.25rem] font-bold orange-glow tactile shadow-2xl shadow-slate-900/20"
        >
          <UserPlus className="w-5 h-5" />
          Invite New Manager
        </button>
      </div>

      {loading ? (
        <div className="py-32 flex flex-col items-center justify-center gap-4">
           <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
           <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Loading Team Data...</p>
        </div>
      ) : outlets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {outlets.map((o) => (
            <div key={o.slug} className="bg-white rounded-[2.5rem] border border-slate-200 p-8 shadow-xl shadow-slate-200/50 group hover:border-orange-500/20 transition-all">
               <div className="flex items-start justify-between mb-8">
                  <div className="flex items-center gap-4">
                     <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-400 group-hover:text-orange-500 transition-colors">
                        <Store className="w-7 h-7" />
                     </div>
                     <div>
                        <h3 className="text-xl font-brand font-bold text-slate-900">{o.name}</h3>
                        <code className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{o.slug}</code>
                     </div>
                  </div>
                  <div className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-black uppercase tracking-widest border border-emerald-100">
                     Operational
                  </div>
               </div>

               <div className="p-6 bg-slate-50 rounded-[2rem] border border-slate-100 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-5">
                     <ShieldCheck className="w-16 h-16" />
                  </div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Assigned Administrator</h4>
                  
                  <div className="flex items-center gap-3">
                     <div className={`w-10 h-10 rounded-xl shadow-sm flex items-center justify-center ${o.admin ? 'bg-orange-500 text-white font-black text-sm' : 'bg-white text-slate-300'}`}>
                        {o.admin ? o.admin.email[0].toUpperCase() : <Mail className="w-5 h-5" />}
                     </div>
                     <div>
                        {o.admin ? (
                          <>
                             <p className="text-sm font-bold text-slate-800 tracking-tight">{o.admin.email}</p>
                             <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5 block flex items-center gap-1">
                                <ShieldCheck className="w-3 h-3 text-emerald-500" />
                                Branch Manager
                             </span>
                          </>
                        ) : (
                          <>
                             <p className="text-sm font-bold text-slate-400 italic">No manager assigned yet</p>
                             <button 
                               onClick={() => setIsModalOpen(true)}
                               className="text-orange-500 text-xs font-bold hover:underline mt-0.5 flex items-center gap-1"
                             >
                                Assign Manager <ChevronRight className="w-3 h-3" />
                             </button>
                          </>
                        )}
                     </div>
                  </div>
               </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-32 text-center bg-white rounded-[4rem] border border-slate-200 shadow-sm">
           <div className="max-w-sm mx-auto flex flex-col items-center gap-6">
              <div className="w-24 h-24 rounded-[2.5rem] bg-slate-50 flex items-center justify-center text-slate-200 shadow-inner">
                 <Building2 className="w-12 h-12" />
              </div>
              <div>
                 <h3 className="text-2xl font-brand font-bold text-slate-900">No Outlets to Manage</h3>
                 <p className="text-slate-500 mt-2 leading-relaxed font-medium">
                    You need to deploy at least one outlet before you can assign managers to your team.
                 </p>
              </div>
           </div>
        </div>
      )}

      <AssignAdminModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        outlets={outlets}
        onSuccess={fetchOutlets}
      />
    </div>
  );
};

export default TeamManagement;
