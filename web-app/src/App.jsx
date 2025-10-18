import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Auth pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// Customer pages
import CustomerDashboard from './pages/customer/Dashboard';
import NewRequest from './pages/customer/NewRequest';
import CustomerProfile from './pages/customer/Profile';

// Dispatcher pages
import DispatcherDashboard from './pages/dispatcher/Dashboard';

// Technician pages
import TechnicianDashboard from './pages/technician/Dashboard';

// Admin pages
import AdminDashboard from './pages/admin/Dashboard';

function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, user, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  const { loadToken, user } = useAuthStore();

  useEffect(() => {
    loadToken();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Customer routes */}
        <Route
          path="/customer"
          element={
            <ProtectedRoute allowedRoles={['customer']}>
              <CustomerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/customer/new-request"
          element={
            <ProtectedRoute allowedRoles={['customer']}>
              <NewRequest />
            </ProtectedRoute>
          }
        />
        <Route
          path="/customer/profile"
          element={
            <ProtectedRoute allowedRoles={['customer']}>
              <CustomerProfile />
            </ProtectedRoute>
          }
        />

        {/* Dispatcher routes */}
        <Route
          path="/dispatcher"
          element={
            <ProtectedRoute allowedRoles={['dispatcher']}>
              <DispatcherDashboard />
            </ProtectedRoute>
          }
        />

        {/* Technician routes */}
        <Route
          path="/technician"
          element={
            <ProtectedRoute allowedRoles={['technician']}>
              <TechnicianDashboard />
            </ProtectedRoute>
          }
        />

        {/* Admin routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* Default redirect based on role */}
        <Route
          path="/"
          element={
            user ? (
              <Navigate
                to={
                  {
                    customer: '/customer',
                    dispatcher: '/dispatcher',
                    technician: '/technician',
                    admin: '/admin',
                  }[user.role] || '/login'
                }
                replace
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
