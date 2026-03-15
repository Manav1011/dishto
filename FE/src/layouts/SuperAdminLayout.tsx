import { ReactNode } from 'react';
import { useAuth } from '../context/AuthContext';
import { Building2, ShieldCheck, LogOut, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

interface SuperAdminLayoutProps {
  children: ReactNode;
}

const SuperAdminLayout = ({ children }: SuperAdminLayoutProps) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { name: 'Franchise Network', icon: Building2, path: '/' },
    { name: 'Feature Requests', icon: ShieldCheck, path: '/features' },
    { name: 'Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans overflow-x-hidden">
      {/* Sidebar */}
      <aside className="w-72 glass border-r border-slate-200/50 flex flex-col p-6 sticky top-0 h-screen z-20 shrink-0">
        <div className="mb-10 px-4">
          <Link to="/" className="inline-block group">
            <h1 className="text-3xl font-brand font-black text-slate-900 tracking-tighter group-hover:scale-105 transition-transform">
              Dishto<span className="text-orange-500">.</span>
            </h1>
          </Link>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mt-2 ml-1">Administration</p>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3.5 rounded-2xl font-bold transition-all tactile ${
                  isActive 
                    ? 'bg-slate-900 text-white shadow-xl shadow-slate-900/20' 
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-orange-500' : ''}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User Profile Summary */}
        <div className="mt-auto pt-6 border-t border-slate-100">
           <div className="flex items-center gap-3 px-2 mb-6 group cursor-pointer">
              <div className="w-10 h-10 rounded-xl bg-orange-500 flex items-center justify-center text-white font-bold shadow-lg shadow-orange-500/20 group-hover:scale-110 transition-transform text-xs">
                 {user?.email?.[0].toUpperCase()}
              </div>
              <div className="flex flex-col truncate">
                 <span className="text-sm font-bold text-slate-800 truncate">{user?.name || user?.email.split('@')[0]}</span>
                 <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">System Control</span>
              </div>
           </div>
           
           <button 
             onClick={logout}
             className="w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl font-bold text-rose-500 hover:bg-rose-50 transition-all tactile"
           >
             <LogOut className="w-5 h-5" />
             Sign Out
           </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 min-w-0 overflow-y-auto overflow-x-hidden relative">
        {/* Subtle background decorative element */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-orange-500/5 rounded-full blur-[120px] -z-10 pointer-events-none translate-x-1/2 -translate-y-1/2" />
        
        {children}
      </main>
    </div>
  );
};

export default SuperAdminLayout;
