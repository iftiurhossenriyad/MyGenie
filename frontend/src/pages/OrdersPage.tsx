import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import { ordersApi } from '../lib/business';
import { parseApiDateTime } from '../lib/datetime';
import type { Order } from '../lib/business';

const STATUS_FLOW: Record<string, string[]> = {
  requested: ['validated', 'cancelled'],
  validated: ['confirmed', 'cancelled'],
  confirmed: ['preparing', 'cancelled'],
  preparing: ['dispatched', 'cancelled'],
  dispatched: ['completed', 'cancelled'],
  completed: [],
  cancelled: [],
};

const STATUS_COLORS: Record<string, string> = {
  requested: 'bg-blue-100 text-blue-700',
  validated: 'bg-indigo-100 text-indigo-700',
  confirmed: 'bg-green-100 text-green-700',
  preparing: 'bg-yellow-100 text-yellow-700',
  dispatched: 'bg-orange-100 text-orange-700',
  completed: 'bg-gray-200 text-gray-700',
  cancelled: 'bg-red-100 text-red-700',
};

export default function OrdersPage() {
  const { currentWorkspace, loading: workspaceLoading } = useWorkspace();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadOrders = async () => {
    if (!currentWorkspace) return;
    try {
      setLoading(true);
      const data = await ordersApi.list(currentWorkspace.id);
      setOrders(data);
    } catch {
      setError('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!currentWorkspace) return;

    let active = true;

    const load = async () => {
      try {
        const data = await ordersApi.list(currentWorkspace.id);
        if (active) setOrders(data);
      } catch {
        if (active) setError('Failed to load orders');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  const handleUpdateStatus = async (order: Order, newStatus: string) => {
    if (!confirm(`Change order status to "${newStatus}"?`)) return;

    try {
      await ordersApi.updateStatus(order.id, newStatus);
      loadOrders();
    } catch {
      alert('Failed to update status');
    }
  };

  const formatDate = (iso: string) => {
    return parseApiDateTime(iso).toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (workspaceLoading) {
    return (
      <Layout title="Orders">
        <div className="text-center text-gray-500 py-8">Loading...</div>
      </Layout>
    );
  }

  if (!currentWorkspace || currentWorkspace.type !== 'business') {
    return (
      <Layout title="Orders">
        <div className="card text-center py-12">
          <p className="text-gray-500">Please select a business workspace.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Orders">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-navy">Orders</h2>
            <p className="text-sm text-gray-500 bengali">আপনার অর্ডারসমূহ</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Orders List */}
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : orders.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-2">No orders yet</p>
            <p className="text-sm text-gray-400">
              Orders will appear here once customers place them
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="card">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-navy">
                      {order.order_number}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      Created: {formatDate(order.created_at)}
                    </p>
                  </div>
                  <span
                    className={`text-xs px-3 py-1 rounded-full font-semibold ${
                      STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {order.status.toUpperCase()}
                  </span>
                </div>

                {/* Order Items */}
                {order.items && order.items.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-3">
                    <p className="text-xs font-semibold text-gray-500 mb-2">
                      ITEMS
                    </p>
                    {order.items.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex justify-between text-sm py-1"
                      >
                        <span>
                          {item.product_name_snapshot} × {item.quantity}
                        </span>
                        <span className="font-semibold">
                          {order.currency} {item.line_total}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Totals */}
                <div className="space-y-1 text-sm mb-3">
                  <div className="flex justify-between text-gray-500">
                    <span>Subtotal:</span>
                    <span>
                      {order.currency} {order.subtotal}
                    </span>
                  </div>
                  <div className="flex justify-between text-gray-500">
                    <span>Delivery:</span>
                    <span>
                      {order.currency} {order.delivery_fee}
                    </span>
                  </div>
                  <div className="flex justify-between font-semibold text-navy pt-1 border-t border-gray-100">
                    <span>Total:</span>
                    <span>
                      {order.currency} {order.total}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                {STATUS_FLOW[order.status] && STATUS_FLOW[order.status].length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-100">
                    {STATUS_FLOW[order.status].map((nextStatus) => (
                      <button
                        key={nextStatus}
                        onClick={() => handleUpdateStatus(order, nextStatus)}
                        className={`text-xs px-3 py-1 rounded ${
                          nextStatus === 'cancelled'
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-navy text-white hover:bg-navy-dark'
                        }`}
                      >
                        → {nextStatus}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}