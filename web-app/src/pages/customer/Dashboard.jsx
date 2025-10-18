import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';

export default function CustomerDashboard() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Customer Dashboard</h1>
          <button onClick={handleLogout} className="text-red-600 hover:text-red-700">
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Welcome, {user?.full_name}!</h2>
          <p className="text-gray-600">Email: {user?.email}</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <button
            onClick={() => navigate('/customer/new-request')}
            className="bg-blue-600 text-white p-6 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <div className="text-xl font-semibold">New Service Request</div>
            <div className="text-sm mt-2">Request maintenance service</div>
          </button>

          <button
            onClick={() => navigate('/customer/profile')}
            className="bg-gray-100 text-gray-800 p-6 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <div className="text-xl font-semibold">My Profile</div>
            <div className="text-sm mt-2">View and edit profile</div>
          </button>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Requests</h3>
          <p className="text-gray-500">No requests yet. Create your first request!</p>
        </div>
      </div>
    </div>
  );
}
