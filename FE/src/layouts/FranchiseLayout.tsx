import { ReactNode, useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getSubdomain } from '../utils/subdomain';
import { 
  LayoutDashboard, 
  Store, 
  Users, 
  Settings, 
  LogOut, 
  ChevronRight
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

interface FranchiseLayoutProps {
  children: ReactNode;
}

const FranchiseLayout = ({ children }: FranchiseLayoutProps) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const subdomain = getSubdomain();
  const [franchiseName, setFranchiseName] = useState<string>('Franchise');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.extras?.franchise?.name) {
      setFranchiseName(user.extras.franchise.name);
    } else if (subdomain) {
      setFranchiseName(subdomain);
    }
    setLoading(false);
  }, [user, subdomain]);

  const navItems = [
    { name: 'Overview', icon: LayoutDashboard, path: '/admin' },
    { name: 'Outlets', icon: Store, path: '/admin/outlets' },
    { name: 'Team', icon: Users, path: '/admin/team' },
    { name: 'Settings', icon: Settings, path: '/admin/settings' },
  ];

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-72 bg-white/80 backdrop-blur-xl border-r border-slate-200/60 flex flex-col p-6 h-full z-20 shrink-0">
        <div className="mb-10 px-2">
          <Link to="/admin" className="flex items-center gap-3 group">
            <div className="w-12 h-12 rounded-[18px] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center text-white font-brand font-black shadow-xl shadow-slate-900/10 group-hover:scale-105 transition-all duration-300 border border-white/10 relative overflow-hidden">
              {/* Added a dynamic subtle glow in background of the avatar */}
              <div className="absolute inset-0 bg-gradient-to-br from-orange-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <span className="text-lg tracking-tight">
                {franchiseName?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'F'}
              </span>
            </div>
            
            <div className="flex flex-col min-w-0 flex-1">
              <span className="text-[9px] font-black text-orange-500 uppercase tracking-[0.15em] leading-none mb-1.5 flex items-center gap-1">
                 <div className="w-1 h-1 rounded-full bg-orange-500" />
                 Control Center
              </span>
              <h1 className="text-base font-brand font-extrabold text-slate-800 tracking-tight group-hover:text-orange-500 transition-colors truncate">
                {loading ? (
                  <div className="h-4 w-24 bg-slate-100 animate-pulse rounded-md" />
                ) : (
                  franchiseName
                )}
              </h1>
            </div>
          </Link>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center justify-between px-4 py-3.5 rounded-2xl font-bold transition-all tactile ${
                  isActive 
                    ? 'bg-slate-900 text-white shadow-xl shadow-slate-900/20' 
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-5 h-5 ${isActive ? 'text-orange-500' : ''}`} />
                  {item.name}
                </div>
                {isActive && <ChevronRight className="w-4 h-4 text-orange-500/50" />}
              </Link>
            );
          })}
        </nav>

        {/* User Summary */}
        <div className="mt-auto pt-6 border-t border-slate-100">
           <div className="flex items-center gap-3 px-2 mb-6 group cursor-pointer">
              <div className="w-10 h-10 rounded-xl bg-orange-500 flex items-center justify-center text-white font-bold shadow-lg shadow-orange-500/20 group-hover:scale-110 transition-transform text-xs">
                 {user?.email?.[0].toUpperCase()}
              </div>
              <div className="flex flex-col truncate">
                 <span className="text-sm font-bold text-slate-800 truncate">{user?.name || user?.email.split('@')[0]}</span>
                 <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Franchise Owner</span>
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
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[120px] -z-10 pointer-events-none translate-x-1/2 -translate-y-1/2" />
        
        {children}
      </main>
    </div>
  );
};

export default FranchiseLayout;
