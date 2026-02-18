import { motion } from 'framer-motion';

const Header = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="text-center mb-10 py-8"
    >
      <motion.h1
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-5xl md:text-6xl font-bold mb-4 text-white drop-shadow-2xl"
        style={{ textShadow: '3px 3px 10px rgba(0,0,0,0.6), 0 0 30px rgba(0,0,0,0.4)' }}
      >
        ✨ AstroGuru AI
      </motion.h1>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="relative inline-block px-6 py-2 mb-2"
      >
        {/* Background glow effect */}
        <motion.div
          className="absolute inset-0 bg-white/20 backdrop-blur-sm rounded-full"
          animate={{
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <p
          className="text-xl md:text-2xl font-semibold relative z-10 text-white px-4"
          style={{ 
            textShadow: '2px 2px 8px rgba(0,0,0,0.9), 0 0 15px rgba(0,0,0,0.7), 0 0 25px rgba(0,0,0,0.5), 0 0 40px rgba(255,255,255,0.3)',
          }}
        >
          Discover Your Cosmic Path with AI-Powered Vedic Astrology
        </p>
      </motion.div>
    </motion.header>
  );
};

export default Header;

