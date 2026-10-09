import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Welcome Card */}
        <div className="card">
          <h1 className="text-3xl font-bold text-navy mb-2">
            Welcome, {user?.name}!
          </h1>
          <p className="text-gray-600 bengali">
            আপনার MyGenie ড্যাশবোর্ডে স্বাগতম
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-navy mb-2">Tasks</h3>
            <p className="text-3xl font-bold text-gold">0</p>
            <p className="text-sm text-gray-500 mt-1">Active tasks</p>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-navy mb-2">Notes</h3>
            <p className="text-3xl font-bold text-gold">0</p>
            <p className="text-sm text-gray-500 mt-1">Saved notes</p>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-navy mb-2">Appointments</h3>
            <p className="text-3xl font-bold text-gold">0</p>
            <p className="text-sm text-gray-500 mt-1">Upcoming</p>
          </div>
        </div>

        {/* Coming Soon */}
        <div className="card">
          <h2 className="text-xl font-bold text-navy mb-4">
            Coming Soon 🚀
          </h2>
          <ul className="space-y-2 text-gray-600">
            <li>✅ Tasks Management</li>
            <li>✅ Notes with Search</li>
            <li>✅ Appointments</li>
            <li>✅ AI Chat Assistant</li>
            <li>✅ Business Mode (Products, Orders, Bookings)</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}