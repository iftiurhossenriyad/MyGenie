import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import TasksPage from './pages/TasksPage';
import NotesPage from './pages/NotesPage';
import AppointmentsPage from './pages/AppointmentsPage';
import BusinessDashboardPage from './pages/BusinessDashboardPage';
import BusinessProfilePage from './pages/BusinessProfilePage';
import ProductsPage from './pages/ProductsPage';
import OrdersPage from './pages/OrdersPage';
import BookingsPage from './pages/BookingsPage';
import FAQsPage from './pages/FAQsPage';
import ChatPage from './pages/ChatPage';
import CreateWorkspacePage from './pages/CreateWorkspacePage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-navy text-lg">Loading...</div></div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-navy text-lg">Loading...</div></div>;
  if (user) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/tasks" element={<ProtectedRoute><TasksPage /></ProtectedRoute>} />
        <Route path="/notes" element={<ProtectedRoute><NotesPage /></ProtectedRoute>} />
        <Route path="/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
        <Route path="/workspaces/new" element={<ProtectedRoute><CreateWorkspacePage /></ProtectedRoute>} />
        <Route path="/business" element={<ProtectedRoute><BusinessDashboardPage /></ProtectedRoute>} />
        <Route path="/business/profile" element={<ProtectedRoute><BusinessProfilePage /></ProtectedRoute>} />
        <Route path="/business/products" element={<ProtectedRoute><ProductsPage /></ProtectedRoute>} />
        <Route path="/business/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
        <Route path="/business/bookings" element={<ProtectedRoute><BookingsPage /></ProtectedRoute>} />
        <Route path="/business/faqs" element={<ProtectedRoute><FAQsPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}