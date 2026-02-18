import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

const AuthCallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login, fetchUserInfo } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      login(token, null as any); // Will be updated by fetchUserInfo
      fetchUserInfo()
        .then(() => {
          navigate('/dashboard');
        })
        .catch(() => {
          navigate('/');
        });
    } else {
      navigate('/');
    }
  }, [searchParams, login, fetchUserInfo, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-white text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>Completing login...</p>
      </div>
    </div>
  );
};

export default AuthCallbackPage;

