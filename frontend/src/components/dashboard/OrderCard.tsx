import { motion } from 'framer-motion';
import { Order } from '@/types';

interface OrderCardProps {
  order: Order;
  onClick: () => void;
  onRetryPayment: () => void;
}

const OrderCard: React.FC<OrderCardProps> = ({ order, onClick, onRetryPayment }) => {
  const getStatusClass = (status: string) => {
    const classes: Record<string, string> = {
      payment_pending: 'status-pending',
      processing: 'status-processing',
      completed: 'status-completed',
      failed: 'status-failed',
      refunded: 'status-refunded',
    };
    return classes[status] || 'status-pending';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      payment_pending: 'Payment Pending',
      processing: 'Processing',
      completed: 'Completed',
      failed: 'Failed',
      refunded: 'Refunded',
    };
    return texts[status] || status;
  };

  const getTypeBadge = (type: string) => {
    return type === 'query' ? (
      <span className="status-badge bg-orange-100 text-orange-800 border border-orange-400">
        Query
      </span>
    ) : (
      <span className="status-badge bg-blue-100 text-blue-800 border border-blue-400">
        Full Report
      </span>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="card hover:shadow-2xl transition-all duration-300 relative overflow-hidden"
    >
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary to-secondary transform scale-x-0 hover:scale-x-100 transition-transform duration-300"></div>
      
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-lg font-semibold text-text-primary">
            Order #{order.id} {getTypeBadge(order.type)}
          </h4>
          <p className="text-text-secondary text-sm mt-1">
            {new Date(order.created_at).toLocaleString()}
          </p>
        </div>
        <span className={`status-badge ${getStatusClass(order.status)}`}>
          {getStatusText(order.status)}
        </span>
      </div>

      <div className="mb-4">
        <p className="text-text-primary">
          <strong>Amount:</strong> ₹{order.amount.toFixed(2)}
        </p>
        {order.birth_details?.name && (
          <p className="text-text-primary">
            <strong>Name:</strong> {order.birth_details.name}
          </p>
        )}
      </div>

      <div className="flex gap-2">
        {order.status === 'payment_pending' && (
          <button
            onClick={onRetryPayment}
            className="btn-primary text-sm px-4 py-2"
          >
            Pay Now
          </button>
        )}
        {order.status === 'completed' && (
          <button
            onClick={onClick}
            className="btn-primary text-sm px-4 py-2"
          >
            {order.type === 'query' ? 'View Chat' : 'View Report'}
          </button>
        )}
        {order.status === 'failed' && (
          <span className="text-error text-sm">
            {order.error_reason || 'Failed'}
          </span>
        )}
      </div>
    </motion.div>
  );
};

export default OrderCard;

