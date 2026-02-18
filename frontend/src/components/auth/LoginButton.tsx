import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';

const LoginButton = () => {
  const { initiateGoogleLogin } = useAuth();

  const handleLogin = async () => {
    try {
      await initiateGoogleLogin();
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ 
        scale: 1.05,
        boxShadow: "0 10px 30px rgba(99, 102, 241, 0.4)",
      }}
      whileTap={{ scale: 0.95 }}
      onClick={handleLogin}
      className="btn-primary text-lg px-8 py-4 relative overflow-hidden group"
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        <motion.span
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          🔐
        </motion.span>
        Login with Google
      </span>
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-primary to-secondary opacity-0 group-hover:opacity-100"
        initial={{ x: "-100%" }}
        whileHover={{ x: "100%" }}
        transition={{ duration: 0.5 }}
      />
    </motion.button>
  );
};

export default LoginButton;

