import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navbar from '@/components/layout/Navbar';
import AdminPanel from '@/components/admin/AdminPanel';
import AdminLogin from '@/components/admin/AdminLogin';
import api from '@/utils/api';

const AdminPage = () => {
  const { isAuthenticated, isAdmin, login } = useAuth();
  const [adminAuthenticated, setAdminAuthenticated] = useState(false);

  useEffect(() => {
    if (isAdmin) {
      setAdminAuthenticated(true);
    }
  }, [isAdmin]);

  const handleAdminLogin = async (email: string, password: string) => {
    try {
      const response = await api.post('/api/v1/auth/admin/login', { email, password });
      login(response.data.access_token, { type: 'admin', email } as any);
      setAdminAuthenticated(true);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  if (!isAuthenticated || (!isAdmin && !adminAuthenticated)) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <AdminLogin onLogin={handleAdminLogin} />
        </div>
      </div>
    );
  }

  return (
    <AuthGuard requireAdmin>
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <AdminPanel />
        </div>
      </div>
    </AuthGuard>
  );
};

export default AdminPage;

