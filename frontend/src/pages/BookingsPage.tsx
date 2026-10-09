import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import { bookingsApi } from '../lib/business';
import { parseApiDateTime } from '../lib/datetime';
import type { Service, Booking } from '../lib/business';

const BOOKING_STATUS_COLORS: Record<string, string> = {
  requested: 'bg-blue-100 text-blue-700',
  confirmed: 'bg-green-100 text-green-700',
  completed: 'bg-gray-200 text-gray-700',
  cancelled: 'bg-red-100 text-red-700',
};

export default function BookingsPage() {
  const { currentWorkspace } = useWorkspace();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showServiceForm, setShowServiceForm] = useState(false);

  // Service form
  const [serviceForm, setServiceForm] = useState({
    name: '',
    description: '',
    duration_minutes: '30',
    capacity: '1',
    price: '',
  });

  const loadData = async () => {
    if (!currentWorkspace) return;
    try {
      setLoading(true);
      const [bookingsData, servicesData] = await Promise.all([
        bookingsApi.listBookings(currentWorkspace.id),
        bookingsApi.listServices(currentWorkspace.id),
      ]);
      setBookings(bookingsData);
      setServices(servicesData);
    } catch {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!currentWorkspace) return;

    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        const [bookingsData, servicesData] = await Promise.all([
          bookingsApi.listBookings(currentWorkspace.id),
          bookingsApi.listServices(currentWorkspace.id),
        ]);
        if (!active) return;
        setBookings(bookingsData);
        setServices(servicesData);
      } catch {
        if (!active) return;
        setError('Failed to load data');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  const handleCreateService = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace || !serviceForm.name.trim()) return;

    try {
      await bookingsApi.createService(currentWorkspace.id, {
        name: serviceForm.name,
        description: serviceForm.description,
        duration_minutes: parseInt(serviceForm.duration_minutes),
        capacity: parseInt(serviceForm.capacity),
        price: serviceForm.price ? parseFloat(serviceForm.price) : null,
        currency: 'BDT',
      });
      setServiceForm({
        name: '',
        description: '',
        duration_minutes: '30',
        capacity: '1',
        price: '',
      });
      setShowServiceForm(false);
      loadData();
    } catch {
      setError('Failed to create service');
    }
  };

  const handleCancelBooking = async (booking: Booking) => {
    if (!confirm(`Cancel booking?`)) return;
    try {
      await bookingsApi.cancelBooking(booking.id);
      loadData();
    } catch {
      alert('Failed to cancel');
    }
  };

  const formatDate = (iso: string) => {
    return parseApiDateTime(iso).toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!currentWorkspace || currentWorkspace.type !== 'business') {
    return (
      <Layout title="Bookings">
        <div className="card text-center py-12">
          <p className="text-gray-500">Please select a business workspace.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Bookings">
      <div className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Services Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-navy">Services</h2>
              <p className="text-sm text-gray-500 bengali">সার্ভিসসমূহ</p>
            </div>
            <button
              onClick={() => setShowServiceForm(!showServiceForm)}
              className="btn btn-primary"
            >
              {showServiceForm ? 'Cancel' : '+ New Service'}
            </button>
          </div>

          {showServiceForm && (
            <div className="card mb-4">
              <form onSubmit={handleCreateService} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <label className="label">Service Name *</label>
                    <input
                      type="text"
                      className="input"
                      value={serviceForm.name}
                      onChange={(e) =>
                        setServiceForm({ ...serviceForm, name: e.target.value })
                      }
                      placeholder="Haircut, Consultation, etc."
                      required
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="label">Description</label>
                    <textarea
                      className="input"
                      value={serviceForm.description}
                      onChange={(e) =>
                        setServiceForm({
                          ...serviceForm,
                          description: e.target.value,
                        })
                      }
                      rows={2}
                    />
                  </div>
                  <div>
                    <label className="label">Duration (minutes) *</label>
                    <input
                      type="number"
                      className="input"
                      value={serviceForm.duration_minutes}
                      onChange={(e) =>
                        setServiceForm({
                          ...serviceForm,
                          duration_minutes: e.target.value,
                        })
                      }
                      min="5"
                      required
                    />
                  </div>
                  <div>
                    <label className="label">Capacity *</label>
                    <input
                      type="number"
                      className="input"
                      value={serviceForm.capacity}
                      onChange={(e) =>
                        setServiceForm({
                          ...serviceForm,
                          capacity: e.target.value,
                        })
                      }
                      min="1"
                      required
                    />
                  </div>
                  <div>
                    <label className="label">Price (BDT) - Optional</label>
                    <input
                      type="number"
                      className="input"
                      value={serviceForm.price}
                      onChange={(e) =>
                        setServiceForm({ ...serviceForm, price: e.target.value })
                      }
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary">
                  Create Service
                </button>
              </form>
            </div>
          )}

          {services.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">
                No services yet. Create a service to start accepting bookings.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {services.map((service) => (
                <div key={service.id} className="card">
                  <h3 className="text-lg font-semibold text-navy mb-2">
                    {service.name}
                  </h3>
                  {service.description && (
                    <p className="text-gray-600 text-sm mb-3">
                      {service.description}
                    </p>
                  )}
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Duration:</span>
                      <span className="font-semibold">
                        {service.duration_minutes} min
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Capacity:</span>
                      <span className="font-semibold">{service.capacity}</span>
                    </div>
                    {service.price && (
                      <div className="flex justify-between">
                        <span className="text-gray-500">Price:</span>
                        <span className="font-semibold text-navy">
                          {service.currency} {service.price}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Bookings Section */}
        <div>
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-navy">Bookings</h2>
            <p className="text-sm text-gray-500 bengali">বুকিংসমূহ</p>
          </div>

          {loading ? (
            <div className="text-center text-gray-500 py-8">Loading...</div>
          ) : bookings.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">
                No bookings yet. Customers can book your services here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {bookings.map((booking) => {
                const service = services.find((s) => s.id === booking.service_id);
                return (
                  <div
                    key={booking.id}
                    className={`card ${
                      booking.status === 'cancelled' ? 'opacity-50' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3
                            className={`text-lg font-semibold ${
                              booking.status === 'cancelled'
                                ? 'line-through text-gray-400'
                                : 'text-navy'
                            }`}
                          >
                            {service?.name || `Service #${booking.service_id}`}
                          </h3>
                          <span
                            className={`text-xs px-2 py-1 rounded-full font-semibold ${
                              BOOKING_STATUS_COLORS[booking.status] ||
                              'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {booking.status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>📅 {formatDate(booking.starts_at)}</div>
                          <div>⏰ Until {formatDate(booking.ends_at)}</div>
                        </div>
                        {booking.notes && (
                          <p className="text-sm text-gray-500 mt-2">
                            {booking.notes}
                          </p>
                        )}
                      </div>
                      {(booking.status === 'requested' ||
                        booking.status === 'confirmed') && (
                        <button
                          onClick={() => handleCancelBooking(booking)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}