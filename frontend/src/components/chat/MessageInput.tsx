import { useState, KeyboardEvent } from 'react';
import { motion } from 'framer-motion';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  messagesRemaining: number;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled, messagesRemaining }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-md border-t border-white/20 p-4">
      <div className="max-w-4xl mx-auto">
        {messagesRemaining > 0 && (
          <p className="text-text-secondary text-sm mb-2 text-center">
            {messagesRemaining} message{messagesRemaining !== 1 ? 's' : ''} remaining
          </p>
        )}
        <div className="flex gap-2">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled}
            placeholder="Type your message..."
            className="flex-1 input-field resize-none min-h-[60px] max-h-[150px]"
            rows={1}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            className="btn-primary px-6"
          >
            Send
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default MessageInput;

