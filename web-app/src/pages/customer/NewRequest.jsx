import { useNavigate } from 'react-router-dom';

export default function NewRequest() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button onClick={() => navigate('/customer')} className="text-blue-600 hover:text-blue-700">
            ← Back to Dashboard
          </button>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold mb-6">New Service Request</h2>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Vehicle Plate</label>
              <input type="text" className="input-field" placeholder="ABC-1234" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Service Type</label>
              <select className="input-field">
                <option>Oil Change</option>
                <option>Brake Repair</option>
                <option>Battery Replacement</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Location</label>
              <textarea className="input-field" rows="3" placeholder="Enter your address"></textarea>
            </div>
            <button type="submit" className="btn-primary">Submit Request</button>
          </form>
        </div>
      </div>
    </div>
  );
}
