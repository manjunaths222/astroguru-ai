import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navbar from '@/components/layout/Navbar';
import DashboardTabs from '@/components/dashboard/DashboardTabs';
import BirthDetailsForm from '@/components/forms/BirthDetailsForm';
import api from '@/utils/api';
import { Order } from '@/types';

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const response = await api.get<Order[]>('/api/v1/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrderClick = (order: Order) => {
    if (order.type === 'query' && order.status === 'completed') {
      navigate(`/chat/${order.id}`);
    } else if (order.status === 'completed' && order.analysis_data) {
      // Show full report
      navigate(`/report/${order.id}`);
    }
  };

  const handleRetryPayment = async (orderId: number) => {
    try {
      const response = await api.post(`/api/v1/payments/create?order_id=${orderId}`);
      
      // Load Razorpay script if not already loaded
      if (!(window as any).Razorpay) {
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);
        await new Promise((resolve) => {
          script.onload = resolve;
        });
      }
      
      // Handle Razorpay payment
      const options = {
        key: response.data.key_id,
        amount: response.data.amount * 100,
        currency: 'INR',
        name: 'AstroGuru AI',
        description: 'Astrology Analysis',
        order_id: response.data.razorpay_order_id,
        handler: async (razorpayResponse: any) => {
          await api.post('/api/v1/payments/verify', {
            razorpay_order_id: razorpayResponse.razorpay_order_id,
            razorpay_payment_id: razorpayResponse.razorpay_payment_id,
            razorpay_signature: razorpayResponse.razorpay_signature,
          });
          loadOrders();
        },
        prefill: {
          email: user?.email || '',
        },
        theme: {
          color: '#6366f1',
        },
      };
      const razorpay = new (window as any).Razorpay(options);
      razorpay.open();
    } catch (error) {
      console.error('Error creating payment:', error);
      alert('Failed to initiate payment. Please try again.');
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* User Profile */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-primary to-secondary text-white mb-8"
          >
            <div className="flex items-center gap-4">
              {user?.picture_url && (
                <img
                  src={user.picture_url}
                  alt={user.name}
                  className="w-16 h-16 rounded-full"
                />
              )}
              <div>
                <h3 className="text-xl font-bold">{user?.name || user?.email}</h3>
                <p className="opacity-90">{user?.email}</p>
              </div>
            </div>
          </motion.div>

          {showForm ? (
            <BirthDetailsForm
              onSuccess={async (order) => {
                setShowForm(false);
                // Initiate payment flow immediately after order creation
                try {
                  const paymentResponse = await api.post(`/api/v1/payments/create?order_id=${order.id}`);
                  
                  // Load Razorpay script if not already loaded
                  if (!(window as any).Razorpay) {
                    const script = document.createElement('script');
                    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
                    script.async = true;
                    document.body.appendChild(script);
                    await new Promise((resolve) => {
                      script.onload = resolve;
                    });
                  }
                  
                  // Open Razorpay payment interface
                  const options = {
                    key: paymentResponse.data.key_id,
                    amount: paymentResponse.data.amount * 100, // Convert to paise
                    currency: 'INR',
                    name: 'AstroGuru AI',
                    description: order.type === 'query' ? 'Astrology Query' : 'Astrology Analysis',
                    order_id: paymentResponse.data.razorpay_order_id,
                    handler: async (razorpayResponse: any) => {
                      try {
                        await api.post('/api/v1/payments/verify', {
                          razorpay_order_id: razorpayResponse.razorpay_order_id,
                          razorpay_payment_id: razorpayResponse.razorpay_payment_id,
                          razorpay_signature: razorpayResponse.razorpay_signature,
                        });
                        // Payment successful - navigate based on order type
                        if (order.type === 'query') {
                          navigate(`/chat/${order.id}`);
                        } else {
                          navigate(`/report/generating/${order.id}`);
                        }
                      } catch (error: any) {
                        console.error('Payment verification error:', error);
                        alert(error.response?.data?.detail || 'Payment verification failed');
                        loadOrders();
                      }
                    },
                    prefill: {
                      email: user?.email || '',
                    },
                    theme: {
                      color: '#6366f1',
                    },
                    modal: {
                      ondismiss: () => {
                        // User closed payment modal - navigate based on order type
                        if (order.type === 'query') {
                          navigate(`/chat/${order.id}`);
                        } else {
                          navigate(`/report/generating/${order.id}`);
                        }
                      },
                    },
                  };
                  
                  const razorpay = new (window as any).Razorpay(options);
                  razorpay.open();
                } catch (error: any) {
                  console.error('Error creating payment:', error);
                  alert(error.response?.data?.detail || 'Failed to initiate payment');
                  loadOrders();
                }
              }}
              onCancel={() => setShowForm(false)}
            />
          ) : (
            <>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-text-primary">My Dashboard</h2>
                <button
                  onClick={() => setShowForm(true)}
                  className="btn-primary"
                >
                  New Analysis
                </button>
              </div>

              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                </div>
              ) : (
                <DashboardTabs
                  orders={orders}
                  onOrderClick={handleOrderClick}
                  onRetryPayment={handleRetryPayment}
                />
              )}
            </>
          )}
        </div>
      </div>
    </AuthGuard>
  );
};

export default DashboardPage;

