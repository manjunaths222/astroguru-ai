import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '@/utils/api';
import { User } from '@/types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  fetchUserInfo: () => Promise<void>;
  initiateGoogleLogin: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load from localStorage
    const storedToken = localStorage.getItem('astroguru_token');
    const storedUser = localStorage.getItem('astroguru_user');
    
    if (storedToken) {
      setToken(storedToken);
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (e) {
          console.error('Error parsing stored user:', e);
        }
      }
      // Verify token and fetch fresh user info
      fetchUserInfo().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/api/v1/auth/me');
      const userData = response.data;
      setUser(userData);
      localStorage.setItem('astroguru_user', JSON.stringify(userData));
      return userData;
    } catch (error) {
      console.error('Error fetching user info:', error);
      logout();
      throw error;
    }
  };

  const login = (newToken: string, userData: User) => {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem('astroguru_token', newToken);
    localStorage.setItem('astroguru_user', JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('astroguru_token');
    localStorage.removeItem('astroguru_user');
  };

  const initiateGoogleLogin = async () => {
    try {
      const response = await api.get('/api/v1/auth/google');
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url;
      }
    } catch (error) {
      console.error('Error initiating Google login:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isAdmin: user?.type === 'admin',
    login,
    logout,
    fetchUserInfo,
    initiateGoogleLogin,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

