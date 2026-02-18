import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import api from '@/utils/api';
import { Order } from '@/types';
import OrderTable from './OrderTable';

const AdminPanel = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const response = await api.get<{ orders: Order[] }>('/api/v1/admin/orders');
      setOrders(response.data.orders);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetryAnalysis = async (orderId: number) => {
    try {
      await api.post(`/api/v1/admin/orders/${orderId}/retry-analysis`);
      alert('Analysis re-triggered successfully');
      loadOrders();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to re-trigger analysis');
    }
  };

  const handleRefund = async (orderId: number) => {
    if (!confirm('Are you sure you want to process a full refund for this order?')) {
      return;
    }
    try {
      await api.post(`/api/v1/admin/orders/${orderId}/refund`);
      alert('Refund processed successfully');
      loadOrders();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to process refund');
    }
  };

  return (
    <div>
      <h2 className="text-3xl font-bold text-text-primary mb-6">Admin Panel</h2>
      
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        </div>
      ) : (
        <OrderTable
          orders={orders}
          onOrderSelect={setSelectedOrder}
          onRetryAnalysis={handleRetryAnalysis}
          onRefund={handleRefund}
        />
      )}

      {selectedOrder && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Order Details</h3>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-text-secondary hover:text-text-primary"
              >
                ✕
              </button>
            </div>
            {/* Order details content */}
            <pre className="text-sm overflow-auto">
              {JSON.stringify(selectedOrder, null, 2)}
            </pre>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;

