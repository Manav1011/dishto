import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../api';
import { getSubdomain } from '../utils/subdomain';

interface User {
  email: string;
  role: 'superadmin' | 'franchise_admin' | 'outlet_admin';
  name?: string;
  ph_no?: string;
  outlet_slug?: string;
  franchise_slug?: string;
  extras?: any;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  brandNotFound: boolean;
  login: (credentials: any) => Promise<void>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [brandNotFound, setBrandNotFound] = useState(false);

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/protected/auth/user-info');
      const userData = response.data.data || response.data;
      
      if (userData?.extras?.superadmin) {
        userData.role = 'superadmin';
      } else if (userData?.role === 'franchise_owner') {
        userData.role = 'franchise_admin';
      } else if (userData?.role === 'outlet_owner') {
        userData.role = 'outlet_admin';
      }
      
      setUser(userData);
      setBrandNotFound(false);
    } catch (error: any) {
      setUser(null);
      const sub = getSubdomain();
      // Handle Brand Not Found (404)
      if (error.response?.status === 404 && sub && sub !== 'admin') {
        setBrandNotFound(true);
      } else {
        setBrandNotFound(false);
      }
    } finally {
      setLoading(false);
    }
  };

  // Only auto-run on subdomains that are definitely administrative or root
  useEffect(() => {
    const sub = getSubdomain();
    // admin.dishto.in or root dishto.in should check session
    if (sub === 'admin' || !sub) {
      fetchUserInfo();
    } else {
      // For franchise subdomains, we don't block the public page
      // We set loading to false immediately, and /admin routes will trigger checkSession
      setLoading(false);
    }
  }, []);

  const login = async (credentials: any) => {
    await api.post('/protected/auth/login', credentials);
    await fetchUserInfo();
  };

  const logout = async () => {
    await api.post('/protected/auth/logout');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      brandNotFound, 
      login, 
      logout, 
      checkSession: fetchUserInfo 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
