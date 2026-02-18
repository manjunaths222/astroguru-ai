import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import LoginButton from './LoginButton';
import Header from '../layout/Header';

interface AuthGuardProps {
  children: ReactNode;
  requireAdmin?: boolean;
}

const AuthGuard = ({ children, requireAdmin = false }: AuthGuardProps) => {
  const { isAuthenticated, isAdmin, user } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card max-w-md w-full mx-4 text-center">
          <Header />
          <div className="mb-6">
            <p className="text-text-secondary mb-6">
              Please login to continue
            </p>
            <LoginButton />
          </div>
        </div>
      </div>
    );
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export default AuthGuard;

