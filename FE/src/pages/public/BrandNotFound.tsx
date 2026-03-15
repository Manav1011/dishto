import { Building2, Home, ArrowLeft } from 'lucide-react';
import { getSubdomain } from '../../utils/subdomain';

const BrandNotFound = () => {
  const subdomain = getSubdomain();

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[120px] -z-10 translate-x-1/3 -translate-y-1/3" />
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-slate-200/50 rounded-full blur-[120px] -z-10 -translate-x-1/3 translate-y-1/3" />

      <div className="max-w-xl w-full text-center">
        <div className="mb-10 inline-flex items-center justify-center w-24 h-24 rounded-[2.5rem] bg-white shadow-2xl border border-slate-100 relative group tactile">
          <div className="absolute inset-0 bg-orange-500/5 rounded-[2.5rem] blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
          <Building2 className="w-10 h-10 text-slate-300 group-hover:text-orange-500 transition-colors" />
          <div className="absolute -top-1 -right-1 w-6 h-6 bg-rose-500 rounded-full border-4 border-white flex items-center justify-center">
            <span className="text-white text-[10px] font-black">!</span>
          </div>
        </div>

        <h1 className="text-5xl font-brand font-black text-slate-900 tracking-tighter mb-4">
          Brand Not Found<span className="text-orange-500">.</span>
        </h1>
        
        <p className="text-slate-500 text-lg md:text-xl leading-relaxed mb-12 font-medium">
          The brand <span className="text-slate-900 font-bold px-2 py-1 bg-slate-100 rounded-lg">"{subdomain}"</span> is not currently registered on the Dishto network. Please check the URL or contact the administrator.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a 
            href="https://dishto.in"
            className="w-full sm:w-auto px-8 py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-3 orange-glow tactile shadow-2xl shadow-slate-900/20"
          >
            <Home className="w-5 h-5" />
            Return to Portal
          </a>
          
          <button 
            onClick={() => window.history.back()}
            className="w-full sm:w-auto px-8 py-4 glass text-slate-600 rounded-2xl font-bold flex items-center justify-center gap-3 border border-slate-200 tactile shadow-sm"
          >
            <ArrowLeft className="w-5 h-5" />
            Go Back
          </button>
        </div>

        <div className="mt-20 pt-8 border-t border-slate-100">
          <p className="text-slate-400 text-sm font-medium">
            Want to register your brand? <a href="https://dishto.in/contact" className="text-orange-500 hover:underline">Contact Sales</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default BrandNotFound;
