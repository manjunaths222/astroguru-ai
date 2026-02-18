import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="bg-white/10 backdrop-blur-md border-b border-white/20 shadow-lg"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-white">✨ AstroGuru AI</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-white font-medium">
                  {user.name || user.email.split('@')[0]}
                </span>
                {isAdmin && (
                  <Link
                    to="/admin"
                    className="text-white hover:text-primary-light transition-colors"
                  >
                    Admin
                  </Link>
                )}
                <Link
                  to="/dashboard"
                  className="text-white hover:text-primary-light transition-colors"
                >
                  Dashboard
                </Link>
                <button
                  onClick={logout}
                  className="text-white hover:text-primary-light transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <span className="text-white">Please login</span>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;

