import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 shadow-sm sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex justify-between items-center h-14">
          <Link to="/" className="flex items-center space-x-2 group">
            <span className="text-xl font-bold text-indigo-600 dark:text-indigo-400 group-hover:text-indigo-700 transition-colors">AstroGuru</span>
          </Link>
          
          <div className="flex items-center space-x-6 text-sm">
            {user ? (
              <>
                <span className="text-slate-600 dark:text-slate-400 font-medium">
                  {user.name || user.email.split('@')[0]}
                </span>
                {isAdmin && (
                  <Link
                    to="/admin"
                    className="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                  >
                    Admin
                  </Link>
                )}
                <Link
                  to="/dashboard"
                  className="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  Dashboard
                </Link>
                <button
                  onClick={logout}
                  className="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <span className="text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wide">Explore</span>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;

