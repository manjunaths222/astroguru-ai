import ChatInterface from '@/components/chat/ChatInterface';
import AuthGuard from '@/components/auth/AuthGuard';

const ChatPage = () => {
  return (
    <AuthGuard>
      <ChatInterface />
    </AuthGuard>
  );
};

export default ChatPage;

