import { useState } from 'react';
import { motion } from 'framer-motion';
import OrderList from './OrderList';
import { Order } from '@/types';

interface DashboardTabsProps {
  orders: Order[];
  onOrderClick: (order: Order) => void;
  onRetryPayment: (orderId: number) => void;
}

const DashboardTabs: React.FC<DashboardTabsProps> = ({ orders, onOrderClick, onRetryPayment }) => {
  const [activeTab, setActiveTab] = useState<'chatQueries' | 'fullReports'>('chatQueries');

  const chatQueries = orders.filter(order => order.type === 'query');
  const fullReports = orders.filter(order => order.type === 'full_report');

  return (
    <div className="mt-8">
      {/* Tab Buttons */}
      <div className="flex gap-2 border-b-2 border-border mb-6 bg-surface rounded-t-lg p-1">
        <button
          onClick={() => setActiveTab('chatQueries')}
          className={`px-6 py-3 font-semibold transition-all duration-300 relative rounded-lg ${
            activeTab === 'chatQueries'
              ? 'text-white bg-primary shadow-md border-b-2 border-primary-dark'
              : 'text-text-primary hover:text-primary hover:bg-background'
          }`}
        >
          💬 Chat Queries
        </button>
        <button
          onClick={() => setActiveTab('fullReports')}
          className={`px-6 py-3 font-semibold transition-all duration-300 relative rounded-lg ${
            activeTab === 'fullReports'
              ? 'text-white bg-primary shadow-md border-b-2 border-primary-dark'
              : 'text-text-primary hover:text-primary hover:bg-background'
          }`}
        >
          📊 Full Reports
        </button>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'chatQueries' ? (
          <OrderList
            orders={chatQueries}
            onOrderClick={onOrderClick}
            onRetryPayment={onRetryPayment}
          />
        ) : (
          <OrderList
            orders={fullReports}
            onOrderClick={onOrderClick}
            onRetryPayment={onRetryPayment}
          />
        )}
      </motion.div>
    </div>
  );
};

export default DashboardTabs;

