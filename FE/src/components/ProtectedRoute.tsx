import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ReactNode, useEffect, useState } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: ('superadmin' | 'franchise_admin' | 'outlet_admin')[];
}

const ProtectedRoute = ({ children, allowedRoles }: ProtectedRouteProps) => {
  const { user, loading, checkSession } = useAuth();
  const location = useLocation();
  const [checking, setChecking] = useState(false);
  const [hasStartedCheck, setHasStartedCheck] = useState(false);

  // If AuthContext is done loading, we don't have a user, and haven't tried checking yet
  const needsCheck = !loading && !user && !hasStartedCheck;

  useEffect(() => {
    if (needsCheck) {
      setChecking(true);
      setHasStartedCheck(true);
      checkSession().finally(() => setChecking(false));
    }
  }, [needsCheck, checkSession]);

  // Block ANY redirect until either context loading finishes OR our explicit check resolves
  if (loading || checking || needsCheck) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 flex-col gap-4">
        <div className="w-12 h-12 border-4 border-orange-500/20 border-t-orange-500 rounded-full animate-spin" />
        <span className="text-slate-400 font-bold uppercase tracking-widest text-[10px]">Validating Access...</span>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // If wrong role, kick to root
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
