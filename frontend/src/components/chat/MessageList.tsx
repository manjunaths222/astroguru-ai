import { motion } from 'framer-motion';
import { ChatMessage } from '@/types';
import { formatMarkdown } from '@/utils/formatMarkdown';

interface MessageListProps {
  message: ChatMessage;
}

const MessageList: React.FC<MessageListProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-2xl p-4 ${
            isUser
              ? 'bg-primary text-white rounded-br-sm'
              : 'bg-surface border-2 border-border rounded-bl-sm'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div
              className="prose prose-sm max-w-none markdown-content"
              dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
            />
          )}
        </div>
        <div className={`flex gap-2 mt-1 text-xs text-text-secondary ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span>{isUser ? 'You' : 'AstroGuru AI'}</span>
          <span>•</span>
          <span>{new Date(message.created_at).toLocaleTimeString()}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageList;

