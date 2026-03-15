import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../api';

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
  login: (credentials: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/protected/auth/user-info');
      const userData = response.data.data || response.data;
      
      // Map backend 'extras.superadmin' and backend roles to frontend 'role' expected values
      if (userData?.extras?.superadmin) {
        userData.role = 'superadmin';
      } else if (userData?.role === 'franchise_owner') {
        userData.role = 'franchise_admin';
      } else if (userData?.role === 'outlet_owner') {
        userData.role = 'outlet_admin';
      }
      
      setUser(userData);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserInfo();
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
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser: fetchUserInfo }}>
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
