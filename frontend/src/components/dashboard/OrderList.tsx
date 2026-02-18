import { Order } from '@/types';
import OrderCard from './OrderCard';

interface OrderListProps {
  orders: Order[];
  onOrderClick: (order: Order) => void;
  onRetryPayment: (orderId: number) => void;
}

const OrderList: React.FC<OrderListProps> = ({ orders, onOrderClick, onRetryPayment }) => {
  if (orders.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📭</div>
        <p className="text-text-secondary text-lg">
          No orders yet. Start your first analysis!
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {orders.map((order) => (
        <OrderCard
          key={order.id}
          order={order}
          onClick={() => onOrderClick(order)}
          onRetryPayment={() => onRetryPayment(order.id)}
        />
      ))}
    </div>
  );
};

export default OrderList;

