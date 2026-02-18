import { motion } from 'framer-motion';
import { Order } from '@/types';

interface OrderTableProps {
  orders: Order[];
  onOrderSelect: (order: Order) => void;
  onRetryAnalysis: (orderId: number) => void;
  onRefund: (orderId: number) => void;
}

const OrderTable: React.FC<OrderTableProps> = ({ orders, onOrderSelect, onRetryAnalysis, onRefund }) => {
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
    return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
  };

  return (
    <div className="card overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="text-left p-4 text-text-primary font-semibold">Order</th>
            <th className="text-left p-4 text-text-primary font-semibold">User</th>
            <th className="text-left p-4 text-text-primary font-semibold">Amount</th>
            <th className="text-left p-4 text-text-primary font-semibold">Status</th>
            <th className="text-left p-4 text-text-primary font-semibold">Date</th>
            <th className="text-left p-4 text-text-primary font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <motion.tr
              key={order.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="border-b border-border hover:bg-background transition-colors"
            >
              <td className="p-4">
                <div className="flex items-center gap-2">
                  <span className="font-semibold">#{order.id}</span>
                  <span className={`status-badge ${
                    order.type === 'query' 
                      ? 'bg-orange-100 text-orange-800 border border-orange-400'
                      : 'bg-blue-100 text-blue-800 border border-blue-400'
                  }`}>
                    {order.type === 'query' ? 'Query' : 'Full Report'}
                  </span>
                </div>
              </td>
              <td className="p-4 text-text-secondary">User {order.user_id}</td>
              <td className="p-4 font-semibold">₹{order.amount.toFixed(2)}</td>
              <td className="p-4">
                <span className={`status-badge ${getStatusClass(order.status)}`}>
                  {getStatusText(order.status)}
                </span>
              </td>
              <td className="p-4 text-text-secondary text-sm">
                {new Date(order.created_at).toLocaleString()}
              </td>
              <td className="p-4">
                <div className="flex gap-2">
                  <button
                    onClick={() => onOrderSelect(order)}
                    className="btn-action btn-view text-sm"
                  >
                    View
                  </button>
                  {order.type === 'full_report' && (order.status === 'failed' || order.status === 'completed') && (
                    <button
                      onClick={() => onRetryAnalysis(order.id)}
                      className="btn-action btn-retry text-sm"
                    >
                      Re-trigger
                    </button>
                  )}
                  {order.status === 'completed' && (
                    <button
                      onClick={() => onRefund(order.id)}
                      className="btn-action btn-refund text-sm"
                    >
                      Refund
                    </button>
                  )}
                </div>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OrderTable;

