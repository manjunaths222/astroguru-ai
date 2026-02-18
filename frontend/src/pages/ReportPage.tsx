import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navbar from '@/components/layout/Navbar';
import api from '@/utils/api';
import { Order } from '@/types';
import { formatMarkdown } from '@/utils/formatMarkdown';

const ReportPage = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }
    if (orderId) {
      loadOrder();
    }
  }, [orderId, isAuthenticated, navigate]);

  const loadOrder = async () => {
    if (!orderId) return;
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<Order>(`/api/v1/orders/${orderId}`);
      setOrder(response.data);
      
      if (response.data.type !== 'full_report') {
        setError('This is not a full report order');
      } else if (response.data.status !== 'completed') {
        setError('This report is not yet completed');
      } else if (!response.data.analysis_data) {
        setError('Analysis data not available for this order');
      }
    } catch (err: any) {
      console.error('Error loading order:', err);
      setError(err.response?.data?.detail || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AuthGuard>
        <div className="min-h-screen">
          <Navbar />
          <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-text-secondary">Loading report...</p>
            </div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  if (error || !order) {
    return (
      <AuthGuard>
        <div className="min-h-screen">
          <Navbar />
          <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
            <div className="card max-w-md w-full mx-4 text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-text-primary mb-4">Error Loading Report</h2>
              <p className="text-text-secondary mb-6">{error || 'Order not found'}</p>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-primary"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  const analysisData = order.analysis_data || {};
  const birthDetails = order.birth_details || {};

  return (
    <AuthGuard>
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-3xl font-bold text-text-primary">Astrology Report</h1>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-secondary"
              >
                ← Back to Dashboard
              </button>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 space-y-2">
              <p className="text-base text-white"><strong className="font-semibold text-white">Order ID:</strong> <span className="text-white font-medium">#{order.id}</span></p>
              <p className="text-base text-white"><strong className="font-semibold text-white">Date:</strong> <span className="text-white font-medium">{new Date(order.created_at).toLocaleString()}</span></p>
              {birthDetails.name && <p className="text-base text-white"><strong className="font-semibold text-white">Name:</strong> <span className="text-white font-medium">{birthDetails.name}</span></p>}
            </div>
          </motion.div>

          {/* Summary Section */}
          {analysisData.summary && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card mb-6"
            >
              <div className="flex justify-between items-center mb-4 border-b-2 border-primary pb-2">
                <h2 className="text-2xl font-bold text-text-primary">
                  📋 Analysis Summary
                </h2>
                <button
                  onClick={() => setShowDetailedAnalysis(!showDetailedAnalysis)}
                  className="btn-secondary text-sm"
                >
                  {showDetailedAnalysis ? 'Hide' : 'Show'} Detailed Analysis
                </button>
              </div>
              <div
                className="prose prose-lg max-w-none markdown-content"
                dangerouslySetInnerHTML={{ __html: formatMarkdown(analysisData.summary) }}
              />
            </motion.section>
          )}

          {/* Detailed Analysis Sections - Collapsible */}
          {showDetailedAnalysis && (
            <>
              {/* Chart Analysis Section */}
              {analysisData.chart_data_analysis && (
                <motion.section
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="card mb-6"
                >
                  <h2 className="text-2xl font-bold text-text-primary mb-4 border-b-2 border-primary pb-2">
                    🔮 Birth Chart Analysis
                  </h2>
                  <div
                    className="prose prose-lg max-w-none markdown-content"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(analysisData.chart_data_analysis) }}
                  />
                </motion.section>
              )}

              {/* Dasha Analysis Section */}
              {analysisData.dasha_analysis && (
                <motion.section
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="card mb-6"
                >
                  <h2 className="text-2xl font-bold text-text-primary mb-4 border-b-2 border-primary pb-2">
                    ⏰ Dasha Analysis
                  </h2>
                  <div
                    className="prose prose-lg max-w-none markdown-content"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(analysisData.dasha_analysis) }}
                  />
                </motion.section>
              )}

              {/* Goal Analysis Section */}
              {analysisData.goal_analysis && (
                <motion.section
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="card mb-6"
                >
                  <h2 className="text-2xl font-bold text-text-primary mb-4 border-b-2 border-primary pb-2">
                    🎯 Goal Analysis
                  </h2>
                  <div
                    className="prose prose-lg max-w-none markdown-content"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(analysisData.goal_analysis) }}
                  />
                </motion.section>
              )}

              {/* Recommendations Section */}
              {analysisData.recommendations && (
                <motion.section
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="card mb-6"
                >
                  <h2 className="text-2xl font-bold text-text-primary mb-4 border-b-2 border-primary pb-2">
                    💡 Recommendations
                  </h2>
                  <div
                    className="prose prose-lg max-w-none markdown-content"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(analysisData.recommendations) }}
                  />
                </motion.section>
              )}
            </>
          )}

          {/* Birth Details Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="card mb-6"
          >
            <h2 className="text-2xl font-bold text-text-primary mb-4 border-b-2 border-primary pb-2">
              📅 Birth Details
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {birthDetails.name && (
                <div>
                  <strong className="text-text-primary">Name:</strong>
                  <p className="text-text-secondary">{birthDetails.name}</p>
                </div>
              )}
              {(birthDetails.dateOfBirth || birthDetails.date_of_birth) && (
                <div>
                  <strong className="text-text-primary">Date of Birth:</strong>
                  <p className="text-text-secondary">{birthDetails.dateOfBirth || birthDetails.date_of_birth}</p>
                </div>
              )}
              {(birthDetails.timeOfBirth || birthDetails.time_of_birth) && (
                <div>
                  <strong className="text-text-primary">Time of Birth:</strong>
                  <p className="text-text-secondary">{birthDetails.timeOfBirth || birthDetails.time_of_birth}</p>
                </div>
              )}
              {(birthDetails.placeOfBirth || birthDetails.place_of_birth) && (
                <div>
                  <strong className="text-text-primary">Place of Birth:</strong>
                  <p className="text-text-secondary">{birthDetails.placeOfBirth || birthDetails.place_of_birth}</p>
                </div>
              )}
            </div>
          </motion.section>

          {/* Back Button */}
          <div className="text-center mt-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-primary"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
};

export default ReportPage;

