import { Routes, Route, Navigate } from 'react-router-dom';
import { Building2 } from 'lucide-react';
import { useHealthCheck } from './hooks/useHealthCheck';
import { getSubdomain, isSuperAdmin, isFranchise } from './utils/subdomain';
import LoginPage from './pages/auth/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import FranchiseDirectory from './pages/superadmin/FranchiseDirectory';
import FeatureRequests from './pages/superadmin/FeatureRequests';
import ProfileSettings from './pages/auth/ProfileSettings';
import SuperAdminLayout from './layouts/SuperAdminLayout';
import FranchiseLayout from './layouts/FranchiseLayout';
import BrandNotFound from './pages/public/BrandNotFound';
import FranchisePublicHome from './pages/public/FranchisePublicHome';
import FranchiseHome from './pages/dashboard/FranchiseHome';
import ManageOutlets from './pages/dashboard/ManageOutlets';
import TeamManagement from './pages/dashboard/TeamManagement';
import SetPassword from './pages/auth/SetPassword';
import OutletLogin from './pages/outlet/OutletLogin';

function App() {
  const status = useHealthCheck();
  const subdomain = getSubdomain();
  const { user, logout, brandNotFound } = useAuth();

  if (brandNotFound) {
    return <BrandNotFound />;
  }

  const FranchiseHomeWrapper = () => {
    if (user?.role === 'franchise_admin') {
      return <Navigate to="/admin" replace />;
    }
    return <FranchisePublicHome />;
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* API Health Indicator */}
      <div className="fixed bottom-4 right-4 z-50">
        <div className={`px-3 py-1.5 rounded-full text-[10px] uppercase tracking-widest font-bold glass flex items-center gap-2 shadow-xl border border-white/50`}>
          <span className={`w-2 h-2 rounded-full ${
            status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 
            status === 'offline' ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]' : 'bg-slate-300 animate-pulse'
          }`} />
          API: {status}
        </div>
      </div>
      
      {/* Removed: Global User Info / Logout - now handled by specific layouts */}

      <Routes>
        {/* --- Shared Routes --- */}
        <Route path="/admin/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
        <Route path="/:outlet_slug/admin/login" element={user ? <Navigate to="/" replace /> : <OutletLogin />} />
        <Route path="/set-password" element={<SetPassword />} />

        {/* --- Root Route Logic --- */}
        <Route path="/" element={
          isSuperAdmin() ? (
            <ProtectedRoute allowedRoles={['superadmin']}>
              <SuperAdminLayout><FranchiseDirectory /></SuperAdminLayout>
            </ProtectedRoute>
          ) : isFranchise() ? (
            <FranchiseHomeWrapper />
          ) : (
            <div className="flex flex-col items-center justify-center min-h-screen bg-white relative overflow-hidden text-center p-6">
              <div className="absolute -top-24 -left-24 w-96 h-96 bg-orange-500/10 rounded-full blur-[100px]" />
              <div className="mb-6 inline-flex px-4 py-1.5 rounded-full bg-orange-50 border border-orange-100 text-orange-600 text-xs font-bold uppercase tracking-widest">
                 The Future of Food Logistics
              </div>
              <h1 className="text-7xl md:text-8xl font-brand font-black text-slate-900 tracking-tighter mb-4">
                Dishto<span className="text-orange-500">.</span>
              </h1>
              <p className="text-slate-500 max-w-2xl text-xl md:text-2xl leading-relaxed mb-12">
                Unified multi-tenant orchestration for franchises, smart inventory mapping, and photorealistic AI menus.
              </p>
              <div className="flex gap-4">
                <button className="px-10 py-5 bg-orange-500 text-white rounded-[1.25rem] font-bold text-lg orange-glow tactile shadow-2xl shadow-orange-500/20">
                  Register Brand
                </button>
                <button className="px-10 py-5 glass rounded-[1.25rem] font-bold text-lg border border-slate-200 tactile">
                  View Demo
                </button>
              </div>
            </div>
          )
        } />

        {/* --- SuperAdmin Scope --- */}
        <Route path="/features" element={
          <ProtectedRoute allowedRoles={['superadmin']}>
            <SuperAdminLayout><FeatureRequests /></SuperAdminLayout>
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute allowedRoles={['superadmin']}>
            <SuperAdminLayout><ProfileSettings /></SuperAdminLayout>
          </ProtectedRoute>
        } />

        {/* --- Franchise Management Scope --- */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['franchise_admin']}>
            <FranchiseLayout>
               <FranchiseHome />
            </FranchiseLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/admin/outlets" element={
          <ProtectedRoute allowedRoles={['franchise_admin']}>
            <FranchiseLayout>
               <ManageOutlets />
            </FranchiseLayout>
          </ProtectedRoute>
        } />

        <Route path="/admin/team" element={
          <ProtectedRoute allowedRoles={['franchise_admin']}>
            <FranchiseLayout>
               <TeamManagement />
            </FranchiseLayout>
          </ProtectedRoute>
        } />

        <Route path="/admin/settings" element={
          <ProtectedRoute allowedRoles={['franchise_admin']}>
            <FranchiseLayout>
               <ProfileSettings />
            </FranchiseLayout>
          </ProtectedRoute>
        } />

        {/* --- Outlet Management Scope --- */}
        <Route path="/:outlet_slug/admin" element={
          <ProtectedRoute allowedRoles={['outlet_admin', 'franchise_admin']}>
             <div className="flex items-center justify-center min-h-screen text-4xl text-emerald-500 font-bold">Outlet Dashboard (Under Construction)</div>
          </ProtectedRoute>
        } />

        {/* --- Public Outlet Menus --- */}
        <Route path="/:outlet_slug" element={
          <div className="p-10 flex flex-col items-center justify-center min-h-screen text-center">
            <h1 className="text-5xl font-brand font-black text-slate-900 mb-4 tracking-tight">Digital Menu</h1>
            <p className="text-slate-500 text-xl font-medium max-w-lg leading-relaxed">
               We are currently preparing our digital catalog. Check back soon to explore our dishes.
            </p>
            <button 
              onClick={() => window.history.back()}
              className="mt-12 px-8 py-4 glass text-slate-600 rounded-2xl font-bold border border-slate-200 tactile flex items-center gap-3"
            >
               <Building2 className="w-5 h-5" />
               Return to Brand Home
            </button>
          </div>
        } />

        {/* --- Catch-all --- */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
