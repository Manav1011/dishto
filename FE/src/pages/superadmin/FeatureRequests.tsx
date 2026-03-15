import { useState, useEffect } from 'react';
import api from '../../api';
import { 
  ShieldCheck, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  ChevronRight, 
  Building2, 
  Tag, 
  MessageSquare,
  Loader2,
  AlertCircle
} from 'lucide-react';

interface Feature {
  id: number;
  name: string;
  slug: string;
}

interface FeatureRequest {
  id: number;
  outlet_name: string;
  outlet_slug: string;
  features: Feature[];
  status: 'pending' | 'approved' | 'rejected';
  request_type: 'add' | 'remove';
  requested_by_email: string;
  created_at: string;
  note?: string;
}

const FeatureRequests = () => {
  const [requests, setRequests] = useState<FeatureRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'pending' | 'approved' | 'rejected'>('pending');
  
  // Action State
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [actionNote, setActionNote] = useState('');
  const [prices, setPrices] = useState<Record<string, string>>({}); // feature_id -> price

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const response = await api.get('/protected/feature/admin/requests/', {
        params: { status_filter: filter }
      });
      setRequests(response.data.data || []);
    } catch (err) {
      console.error('Failed to fetch requests', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const handleAction = async (requestId: number, status: 'approved' | 'rejected') => {
    setProcessingId(requestId);
    try {
      // The backend expects OutletFeatureRequestUpdateRequest
      // status: str, note: str, prices: Optional[Dict[str, float]]
      await api.patch(`/protected/feature/admin/requests/${requestId}/`, {
        status,
        note: actionNote,
        prices: status === 'approved' ? prices : undefined
      });
      
      // Refresh list
      fetchRequests();
      // Reset action state
      setActionNote('');
      setPrices({});
      setProcessingId(null);
    } catch (err) {
      console.error('Action failed', err);
      setProcessingId(null);
    }
  };

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-emerald-50 text-emerald-600 border-emerald-100';
      case 'rejected': return 'bg-rose-50 text-rose-600 border-rose-100';
      default: return 'bg-amber-50 text-amber-600 border-amber-100';
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-brand font-bold text-slate-900 flex items-center gap-3">
            <ShieldCheck className="w-10 h-10 text-orange-500" />
            Feature Subscriptions
          </h1>
          <p className="text-slate-500 mt-2 text-lg font-medium">Evaluate and activate high-performance modules for outlets.</p>
        </div>

        <div className="flex glass p-1 rounded-2xl border border-slate-200 shadow-sm">
          {(['pending', 'approved', 'rejected'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-6 py-2.5 rounded-xl text-sm font-bold capitalize transition-all ${
                filter === s 
                  ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/10' 
                  : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-32 gap-4">
          <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
          <p className="text-slate-400 font-bold uppercase tracking-widest text-xs animate-pulse">Scanning Requests...</p>
        </div>
      ) : requests.length > 0 ? (
        <div className="grid grid-cols-1 gap-6">
          {requests.map((req) => (
            <div key={req.id} className="bg-white rounded-[2.5rem] border border-slate-200 overflow-hidden shadow-xl shadow-slate-200/50 hover:border-orange-500/20 transition-all group">
              <div className="flex flex-col lg:flex-row">
                
                {/* Request Header Info */}
                <div className="p-8 lg:w-1/3 bg-slate-50/50 border-b lg:border-b-0 lg:border-r border-slate-100">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-12 h-12 rounded-[1.25rem] bg-white shadow-sm border border-slate-100 flex items-center justify-center text-slate-400 group-hover:text-orange-500 transition-colors">
                      <Building2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900 text-lg">{req.outlet_name}</h3>
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{req.outlet_slug}</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center gap-3 text-sm">
                      <Clock className="w-4 h-4 text-slate-300" />
                      <span className="text-slate-500 font-medium">Requested {new Date(req.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm">
                      <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${getStatusStyle(req.status)}`}>
                        {req.status}
                      </div>
                      <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${req.request_type === 'add' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-slate-50 text-slate-600 border-slate-100'}`}>
                        {req.request_type} Feature
                      </div>
                    </div>
                  </div>
                </div>

                {/* Features & Action Area */}
                <div className="p-8 flex-1">
                  <div className="mb-8">
                    <h4 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Requested Modules</h4>
                    <div className="flex flex-wrap gap-3">
                      {req.features.map(f => (
                        <div key={f.id} className="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-xl border border-slate-200 shadow-sm group/feature">
                          <Tag className="w-3.5 h-3.5 text-slate-400 group-hover/feature:text-orange-500" />
                          <span className="text-sm font-bold text-slate-700 capitalize">{f.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {filter === 'pending' ? (
                    <div className="space-y-6 animate-in slide-in-from-right-4 duration-500">
                       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Pricing Inputs */}
                          <div className="space-y-3">
                             <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Set Subscription Price (Optional)</h4>
                             {req.features.map(f => (
                               <div key={f.id} className="flex items-center gap-3 bg-slate-50 p-2 rounded-xl border border-slate-100">
                                  <span className="text-xs font-bold text-slate-500 min-w-[80px] capitalize">{f.name}</span>
                                  <div className="relative flex-1">
                                     <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-300 font-bold">$</span>
                                     <input 
                                       type="number" 
                                       placeholder="0.00"
                                       value={prices[f.id] || ''}
                                       onChange={(e) => setPrices({...prices, [f.id]: e.target.value})}
                                       className="w-full pl-7 pr-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/10 transition-all"
                                     />
                                  </div>
                               </div>
                             ))}
                          </div>
                          
                          {/* Note Input */}
                          <div className="space-y-3">
                             <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Internal Notes</h4>
                             <textarea 
                               placeholder="Add a reason for approval/rejection..."
                               value={actionNote}
                               onChange={(e) => setActionNote(e.target.value)}
                               className="w-full h-[calc(100%-24px)] p-4 bg-slate-50 border border-slate-200 rounded-2xl text-sm focus:outline-none focus:ring-4 focus:ring-orange-500/5 transition-all resize-none"
                             />
                          </div>
                       </div>

                       <div className="flex gap-4">
                          <button 
                            onClick={() => handleAction(req.id, 'approved')}
                            disabled={!!processingId}
                            className="flex-1 py-4 bg-orange-500 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
                          >
                            {processingId === req.id ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                              <>
                                <CheckCircle2 className="w-5 h-5" />
                                Approve Subscription
                              </>
                            )}
                          </button>
                          <button 
                            onClick={() => handleAction(req.id, 'rejected')}
                            disabled={!!processingId}
                            className="px-8 py-4 bg-white text-rose-500 border border-rose-100 rounded-2xl font-bold hover:bg-rose-50 transition-all tactile disabled:opacity-50 flex items-center gap-2"
                          >
                            <XCircle className="w-5 h-5" />
                            Reject
                          </button>
                       </div>
                    </div>
                  ) : (
                    <div className="p-6 bg-slate-50 rounded-[2rem] border border-slate-100 flex items-start gap-4">
                       <MessageSquare className="w-5 h-5 text-slate-300 mt-1" />
                       <div>
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Decision Note</p>
                          <p className="text-sm text-slate-600 leading-relaxed italic">
                            {req.note || "No notes provided for this decision."}
                          </p>
                       </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-[3rem] border border-slate-200 py-32 text-center shadow-sm">
           <div className="max-w-xs mx-auto flex flex-col items-center gap-6">
              <div className="w-24 h-24 rounded-[2.5rem] bg-slate-50 flex items-center justify-center text-slate-200">
                 {filter === 'pending' ? <Clock className="w-12 h-12" /> : <AlertCircle className="w-12 h-12" />}
              </div>
              <div>
                <h3 className="text-2xl font-brand font-bold text-slate-900 capitalize">No {filter} Requests</h3>
                <p className="text-slate-400 mt-2 leading-relaxed font-medium">
                  {filter === 'pending' 
                    ? "Your queue is clear. All current requests have been processed." 
                    : `No ${filter} subscription requests were found in history.`}
                </p>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};

export default FeatureRequests;
