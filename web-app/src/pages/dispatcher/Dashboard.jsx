import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';

export default function DispatcherDashboard() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Dispatcher Dashboard</h1>
          <button onClick={() => {logout(); navigate('/login');}} className="text-red-600">Logout</button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold">Welcome, {user?.full_name}!</h2>
          <p className="text-gray-600 mt-2">Manage service requests and technicians</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Pending Requests</h3>
            <p className="text-gray-500">No pending requests</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Available Technicians</h3>
            <p className="text-gray-500">View and assign technicians</p>
          </div>
        </div>
      </div>
    </div>
  );
}
