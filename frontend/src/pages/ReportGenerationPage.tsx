import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navbar from '@/components/layout/Navbar';
import api from '@/utils/api';
import { Order } from '@/types';

const ReportGenerationPage = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }
    if (orderId) {
      checkOrderStatus();
      // Poll order status every 10 seconds
      const pollInterval = setInterval(() => {
        checkOrderStatus();
      }, 10000);
      return () => clearInterval(pollInterval);
    }
  }, [orderId, isAuthenticated, navigate]);

  const checkOrderStatus = async () => {
    if (!orderId) return;
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<Order>(`/api/v1/orders/${orderId}`);
      setOrder(response.data);
      
      // If order is completed, redirect to report page
      if (response.data.status === 'completed') {
        navigate(`/report/${orderId}`);
        return;
      }
      
      // If order failed, show error
      if (response.data.status === 'failed') {
        setError(response.data.error_reason || 'Report generation failed');
      }
    } catch (err: any) {
      console.error('Error checking order status:', err);
      setError(err.response?.data?.detail || 'Failed to check order status');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <AuthGuard>
        <div className="min-h-screen">
          <Navbar />
          <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
            <div className="card max-w-md w-full mx-4 text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-text-primary mb-4">Error</h2>
              <p className="text-text-secondary mb-6">{error}</p>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-primary"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="min-h-screen relative overflow-hidden">
        <Navbar />
        
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute top-20 left-10 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"
            animate={{
              scale: [1, 1.2, 1],
              x: [0, 100, 0],
              y: [0, 50, 0],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute top-40 right-10 w-96 h-96 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"
            animate={{
              scale: [1.2, 1, 1.2],
              x: [0, -100, 0],
              y: [0, -50, 0],
            }}
            transition={{
              duration: 25,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </div>

        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="card max-w-2xl w-full mx-4 text-center"
          >
            {/* Large animated icon */}
            <div className="mb-8">
              <motion.div
                animate={{ 
                  rotate: [0, 360],
                  scale: [1, 1.1, 1]
                }}
                transition={{ 
                  rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                  scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                }}
                className="w-32 h-32 mx-auto mb-6 relative"
              >
                <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full" />
                <div className="absolute inset-4 border-4 border-secondary border-r-transparent rounded-full" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-6xl">🔮</span>
                </div>
              </motion.div>
            </div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-3xl md:text-4xl font-bold text-text-primary mb-4"
            >
              Generating Your Comprehensive Astrology Report
            </motion.h1>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-4 mb-8"
            >
              <p className="text-xl text-text-secondary">
                This usually takes <strong className="text-primary">3-5 minutes</strong>
              </p>
              
              <div className="bg-primary/10 border-2 border-primary/30 rounded-lg p-4">
                <p className="text-text-primary">
                  <span className="text-2xl mr-2">📧</span>
                  <strong>We'll email the report to you</strong> once it's ready
                </p>
                {order && (
                  <p className="text-text-secondary text-sm mt-2">
                    Your report will be sent to your registered email address
                  </p>
                )}
              </div>

              <div className="flex items-center justify-center gap-2 text-text-secondary mt-6">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="ml-2">Analyzing your birth chart and planetary positions...</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-secondary"
              >
                Go to Dashboard
              </button>
            </motion.div>

            {order && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="text-text-secondary text-sm mt-6"
              >
                Order #{order.id} • Status: <span className="capitalize">{order.status}</span>
              </motion.p>
            )}
          </motion.div>
        </div>
      </div>
    </AuthGuard>
  );
};

export default ReportGenerationPage;

