import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import api from '@/utils/api';
import { ChatMessage, ChatHistory, Order } from '@/types';

const ChatInterface = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [messageLimit, setMessageLimit] = useState({ remaining: 0, canContinue: true });
  const [orderStatus, setOrderStatus] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }
    checkOrderStatus();
  }, [orderId, isAuthenticated, navigate]);

  useEffect(() => {
    if (orderStatus === 'completed' && !isProcessing) {
      loadChatHistory();
    }
  }, [orderStatus, isProcessing]);

  useEffect(() => {
    if (isProcessing && orderStatus === 'processing') {
      // Poll order status every 5 seconds
      const pollInterval = setInterval(() => {
        checkOrderStatus();
      }, 5000);
      return () => clearInterval(pollInterval);
    }
  }, [isProcessing, orderStatus]);

  const checkOrderStatus = async () => {
    if (!orderId) return;
    try {
      const response = await api.get<Order>(`/api/v1/orders/${orderId}`);
      const status = response.data.status;
      setOrderStatus(status);
      
      if (status === 'completed') {
        setIsProcessing(false);
        setLoading(false);
        loadChatHistory();
      } else if (status === 'processing') {
        setIsProcessing(true);
        setLoading(false);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error checking order status:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    if (!orderId) return;
    try {
      setLoading(true);
      const response = await api.get<ChatHistory>(`/api/v1/orders/${orderId}/chat/history`);
      setMessages(response.data.messages);
      setMessageLimit({
        remaining: response.data.messages_remaining,
        canContinue: response.data.can_continue,
      });
    } catch (error) {
      console.error('Error loading chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (message: string) => {
    if (!orderId || !messageLimit.canContinue || sending) return;

    const tempUserMessage: ChatMessage = {
      id: Date.now(),
      order_id: parseInt(orderId),
      message_number: messages.length + 1,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);
    setSending(true);

    try {
      const response = await api.post(`/api/v1/orders/${orderId}/chat`, { message });
      
      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        order_id: parseInt(orderId),
        message_number: response.data.message_number || messages.length + 2,
        role: 'assistant',
        content: response.data.message, // API returns 'message' field
        created_at: new Date().toISOString(),
      };
      
      // Update message limit from response
      setMessageLimit({
        remaining: response.data.messages_remaining || 0,
        canContinue: response.data.can_continue !== false,
      });

      setMessages((prev) => [...prev, assistantMessage]);
      await loadChatHistory(); // Reload to get updated limits
    } catch (error: any) {
      console.error('Error sending message:', error);
      setMessages((prev) => prev.slice(0, -1)); // Remove temp message
      alert(error.response?.data?.detail || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  if (loading || isProcessing) {
    return (
      <div className="min-h-screen flex flex-col">
        {/* Chat Header */}
        <motion.div
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          className="bg-white/10 backdrop-blur-md border-b border-white/20 p-4"
        >
          <div className="max-w-4xl mx-auto flex justify-between items-center">
            <h2 className="text-2xl font-bold text-white">Chat with AstroGuru AI</h2>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-secondary text-sm"
            >
              Go to Dashboard
            </button>
          </div>
        </motion.div>

        {/* Processing State */}
        <div className="flex-1 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card max-w-md w-full mx-4 text-center"
          >
            <div className="mb-6">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"
              />
              <h3 className="text-2xl font-bold text-text-primary mb-2">
                Processing Your Query
              </h3>
              <p className="text-text-secondary">
                Your astrology query is being analyzed. This will only take a moment...
              </p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
            >
              Go to Dashboard
            </button>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Chat Header */}
      <motion.div
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="bg-white/10 backdrop-blur-md border-b border-white/20 p-4"
      >
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Chat with AstroGuru AI</h2>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-secondary text-sm"
          >
            Back to Dashboard
          </button>
        </div>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <MessageList key={message.id} message={message} />
            ))}
          </AnimatePresence>
          {sending && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-2 text-text-secondary"
            >
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
              <span>AstroGuru AI is thinking...</span>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Message Limit Info */}
      {!messageLimit.canContinue && (
        <div className="bg-warning-light border-2 border-warning p-4 text-center">
          <p className="text-warning font-semibold mb-2">
            Message limit reached (3/3 messages sent)
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary text-sm"
          >
            Create New Query
          </button>
        </div>
      )}

      {/* Input */}
      <MessageInput
        onSend={sendMessage}
        disabled={!messageLimit.canContinue || sending}
        messagesRemaining={messageLimit.remaining}
      />
    </div>
  );
};

export default ChatInterface;

