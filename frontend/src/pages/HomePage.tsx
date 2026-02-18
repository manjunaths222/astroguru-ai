import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Header from '@/components/layout/Header';
import LoginButton from '@/components/auth/LoginButton';
import BirthDetailsForm from '@/components/forms/BirthDetailsForm';
import api from '@/utils/api';
import { Order } from '@/types';

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <Navbar />
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"
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
            className="absolute top-40 right-10 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"
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
          <motion.div
            className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"
            animate={{
              scale: [1, 1.3, 1],
              x: [0, 50, 0],
              y: [0, -100, 0],
            }}
            transition={{
              duration: 30,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </div>
        
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="card max-w-md w-full mx-4 text-center"
          >
            <Header />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mb-6"
            >
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="text-text-secondary mb-6 text-lg"
              >
                Please login to get your astrology analysis
              </motion.p>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 1 }}
              >
                <LoginButton />
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
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
        <motion.div
          className="absolute bottom-20 left-1/2 w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"
          animate={{
            scale: [1, 1.3, 1],
            x: [0, 50, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>
      
      <div className="max-w-4xl mx-auto px-4 py-8 relative z-10">
        {!showForm ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="card text-center"
          >
            <Header />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="mb-8"
            >
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="text-text-secondary text-lg md:text-xl mb-8 leading-relaxed"
              >
                Welcome to AstroGuru AI! Get personalized Vedic astrology insights powered by AI.
              </motion.p>
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.7 }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 10px 30px rgba(99, 102, 241, 0.4)",
                }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowForm(true)}
                className="btn-primary text-lg px-8 py-4 relative overflow-hidden group"
              >
                <span className="relative z-10">Get Started</span>
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-primary to-secondary opacity-0 group-hover:opacity-100"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: "100%" }}
                  transition={{ duration: 0.5 }}
                />
              </motion.button>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
          >
            <BirthDetailsForm
              onSuccess={async (order: Order) => {
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
                        navigate(`/dashboard?order=${order.id}&payment=failed`);
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
                  navigate(`/dashboard?order=${order.id}`);
                }
              }}
              onCancel={() => setShowForm(false)}
            />
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default HomePage;

