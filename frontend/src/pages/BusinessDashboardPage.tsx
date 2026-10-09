import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import {
  businessApi,
  productsApi,
  ordersApi,
  bookingsApi,
  type BusinessProfile,
} from '../lib/business';

export default function BusinessDashboardPage() {
  const { currentWorkspace, loading: workspaceLoading } = useWorkspace();
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [stats, setStats] = useState({
    products: 0,
    orders: 0,
    bookings: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentWorkspace || currentWorkspace.type !== 'business') return;

    let active = true;

    const loadData = async () => {
      try {
        setLoading(true);
        const [profileData, products, orders, bookings] = await Promise.all([
          businessApi.getProfile(currentWorkspace.id),
          productsApi.list(currentWorkspace.id),
          ordersApi.list(currentWorkspace.id),
          bookingsApi.listBookings(currentWorkspace.id),
        ]);
        if (!active) return;
        setProfile(profileData);
        setStats({
          products: products.length,
          orders: orders.length,
          bookings: bookings.length,
        });
      } catch (err) {
        console.error('Failed to load business data', err);
      } finally {
        if (active) setLoading(false);
      }
    };

    void loadData();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  if (workspaceLoading) {
    return (
      <Layout title="Business Dashboard">
        <div className="text-center text-gray-500 py-8">Loading...</div>
      </Layout>
    );
  }

  if (!currentWorkspace || currentWorkspace.type !== 'business') {
    return (
      <Layout title="Business Dashboard">
        <div className="card text-center py-12">
          <h2 className="text-xl font-bold text-navy mb-4">
            No Business Workspace Selected
          </h2>
          <p className="text-gray-600">
            Please select a business workspace from the sidebar.
          </p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={`Business: ${currentWorkspace.name}`}>
      <div className="space-y-6">
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : (
          <>
            {/* Business Header */}
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-navy mb-2">
                    {profile?.business_name || currentWorkspace.name}
                  </h1>
                  {profile?.description && (
                    <p className="text-gray-600">{profile.description}</p>
                  )}
                </div>
                {!profile && (
                  <a href="/business/profile" className="btn btn-gold">
                    Setup Business Profile
                  </a>
                )}
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold text-navy mb-2">Products</h3>
                <p className="text-3xl font-bold text-gold">{stats.products}</p>
                <p className="text-sm text-gray-500 mt-1 bengali">পণ্য</p>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold text-navy mb-2">Orders</h3>
                <p className="text-3xl font-bold text-gold">{stats.orders}</p>
                <p className="text-sm text-gray-500 mt-1 bengali">অর্ডার</p>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold text-navy mb-2">Bookings</h3>
                <p className="text-3xl font-bold text-gold">{stats.bookings}</p>
                <p className="text-sm text-gray-500 mt-1 bengali">বুকিং</p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <h2 className="text-xl font-bold text-navy mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <a href="/business/products" className="btn btn-outline">
                  Manage Products
                </a>
                <a href="/business/orders" className="btn btn-outline">
                  View Orders
                </a>
                <a href="/business/bookings" className="btn btn-outline">
                  View Bookings
                </a>
                <a href="/business/faqs" className="btn btn-outline">
                  Manage FAQs
                </a>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}