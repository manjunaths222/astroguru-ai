import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';

interface AdminLoginProps {
  onLogin: (email: string, password: string) => Promise<void>;
}

interface LoginFormData {
  email: string;
  password: string;
}

const AdminLogin: React.FC<AdminLoginProps> = ({ onLogin }) => {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>();
  const [error, setError] = useState('');

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError('');
      await onLogin(data.email, data.password);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      onSubmit={handleSubmit(onSubmit)}
      className="card max-w-md w-full"
    >
      <h2 className="text-2xl font-bold text-text-primary mb-6 text-center">Admin Login</h2>
      
      {error && (
        <div className="bg-error-light border-2 border-error text-error p-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Email
          </label>
          <input
            type="email"
            {...register('email', { required: 'Email is required' })}
            className="input-field"
            placeholder="admin@astroguru.ai"
          />
          {errors.email && (
            <p className="text-error text-sm mt-1">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Password
          </label>
          <input
            type="password"
            {...register('password', { required: 'Password is required' })}
            className="input-field"
            placeholder="Enter password"
          />
          {errors.password && (
            <p className="text-error text-sm mt-1">{errors.password.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary w-full"
        >
          {isSubmitting ? 'Logging in...' : 'Login'}
        </button>
      </div>
    </motion.form>
  );
};

export default AdminLogin;

