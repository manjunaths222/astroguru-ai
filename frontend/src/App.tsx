import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import ReportPage from './pages/ReportPage';
import ReportGenerationPage from './pages/ReportGenerationPage';
import AdminPage from './pages/AdminPage';
import AuthCallbackPage from './pages/AuthCallbackPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/chat/:orderId" element={<ChatPage />} />
          <Route path="/report/generating/:orderId" element={<ReportGenerationPage />} />
          <Route path="/report/:orderId" element={<ReportPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

