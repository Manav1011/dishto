import { Routes, Route, Navigate } from 'react-router-dom';
import { useHealthCheck } from './hooks/useHealthCheck';
import { getSubdomain, isSuperAdmin, isFranchise } from './utils/subdomain';
import LoginPage from './pages/auth/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import FranchiseDirectory from './pages/superadmin/FranchiseDirectory';
import FeatureRequests from './pages/superadmin/FeatureRequests';
import ProfileSettings from './pages/auth/ProfileSettings';
import SuperAdminLayout from './layouts/SuperAdminLayout';

function App() {
  const status = useHealthCheck();
  const subdomain = getSubdomain();
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-orange-500/20 border-t-orange-500 rounded-full animate-spin" />
          <p className="text-slate-400 font-medium animate-pulse">Initializing Dishto...</p>
        </div>
      </div>
    );
  }

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

      <Routes>
        {/* --- Public / Auth --- */}
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />

        {/* --- SuperAdmin Scope --- */}
        <Route path="/" element={
          isSuperAdmin() ? (
            <ProtectedRoute allowedRoles={['superadmin']}>
              <SuperAdminLayout><FranchiseDirectory /></SuperAdminLayout>
            </ProtectedRoute>
          ) : isFranchise() ? (
            <div className="p-10">
              <h1 className="text-4xl font-brand font-bold capitalize text-slate-900">{subdomain}</h1>
              <p className="text-slate-500 mt-1">Select an outlet to view the digital menu.</p>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center min-h-screen bg-white">
               <h1 className="text-7xl font-brand font-black text-slate-900">Dishto<span className="text-orange-500">.</span></h1>
               <p className="text-slate-500 mt-4 text-xl">The Future of Food Logistics.</p>
            </div>
          )
        } />

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

        {/* --- Franchise Admin Scope --- */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['franchise_admin']}>
            <div className="p-10">
              <h1 className="text-4xl font-brand font-bold text-slate-900">Franchise Dashboard</h1>
            </div>
          </ProtectedRoute>
        } />

        {/* --- Outlet Admin Scope --- */}
        <Route path="/:outlet_slug/manage" element={
          <ProtectedRoute allowedRoles={['outlet_admin']}>
            <div className="p-10">
              <h1 className="text-4xl font-brand font-bold text-slate-900">Outlet Operations</h1>
            </div>
          </ProtectedRoute>
        } />

        {/* --- Public Outlet View --- */}
        <Route path="/:outlet_slug" element={
          <div className="p-10">
            <h1 className="text-4xl font-brand font-bold text-slate-900">Digital Menu</h1>
          </div>
        } />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
