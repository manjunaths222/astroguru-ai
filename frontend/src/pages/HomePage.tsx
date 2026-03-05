import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Header from '@/components/layout/Header';
import LoginButton from '@/components/auth/LoginButton';
import BirthDetailsForm from '@/components/forms/BirthDetailsForm';
import AboutSection from '@/components/sections/AboutSection';
import ArticlesSection from '@/components/articles/ArticlesSection';
import api from '@/utils/api';
import { Order } from '@/types';

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white dark:bg-slate-950">
        <Navbar />
        
        {/* Hero Section */}
        <div className="relative pt-20 pb-32 md:pt-32 md:pb-48">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="max-w-3xl mx-auto text-center"
            >
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-slate-900 dark:text-white mb-6 leading-tight">
                Unlock Your Cosmic Destiny
              </h1>
              <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
                Experience personalized Vedic astrology insights powered by advanced AI. Discover your life path, career direction, and relationships through ancient wisdom meets modern technology.
              </p>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="flex flex-col sm:flex-row gap-4 justify-center"
              >
                <LoginButton />
                <button className="btn-secondary">Learn More</button>
              </motion.div>
            </motion.div>
          </div>

          {/* Subtle gradient accent */}
          <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-200 dark:bg-indigo-900/20 rounded-full blur-3xl opacity-20 dark:opacity-10" />
          </div>
        </div>

        {/* About Section */}
        <AboutSection />

        {/* Articles Section */}
        <ArticlesSection limit={6} showCategories={true} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12 relative">
        {!showForm ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="max-w-3xl mx-auto text-center"
          >
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-900 dark:text-white mb-6">
              Welcome to AstroGuru AI
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              Discover personalized Vedic astrology insights powered by cutting-edge AI technology.
            </p>
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowForm(true)}
              className="btn-primary text-base px-8 py-3"
            >
              Start Your Reading
            </motion.button>
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

      {/* About Section */}
      <AboutSection />

      {/* Articles Section */}
      <ArticlesSection limit={6} showCategories={true} />
    </div>
  );
};

export default HomePage;

