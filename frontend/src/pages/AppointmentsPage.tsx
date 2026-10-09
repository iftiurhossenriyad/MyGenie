import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { appointmentsApi } from '../lib/appointments';
import { parseApiDateTime } from '../lib/datetime';
import type { Appointment } from '../types';

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);

  // Form
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [date, setDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const data = await appointmentsApi.list();
      setAppointments(data);
    } catch {
      setError('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        const data = await appointmentsApi.list();
        if (!active) return;
        setAppointments(data);
      } catch {
        if (!active) return;
        setError('Failed to load appointments');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !date || !startTime) return;

    try {
      // Build ISO datetime from date + time
      const startsAt = new Date(`${date}T${startTime}:00`).toISOString();
      const endsAt = endTime
        ? new Date(`${date}T${endTime}:00`).toISOString()
        : undefined;

      await appointmentsApi.create({
        title,
        notes,
        starts_at: startsAt,
        ends_at: endsAt,
      });

      setTitle('');
      setNotes('');
      setDate('');
      setStartTime('');
      setEndTime('');
      setShowForm(false);
      loadAppointments();
    } catch {
      setError('Failed to create appointment');
    }
  };

  const handleCancel = async (id: number) => {
    if (!confirm('Cancel this appointment?')) return;
    try {
      await appointmentsApi.update(id, { status: 'cancelled' });
      loadAppointments();
    } catch {
      setError('Failed to cancel appointment');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this appointment?')) return;
    try {
      await appointmentsApi.delete(id);
      loadAppointments();
    } catch {
      setError('Failed to delete appointment');
    }
  };

  const formatDateTime = (isoString: string) => {
    const d = parseApiDateTime(isoString);
    return d.toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Layout title="Appointments">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-navy">Your Appointments</h2>
            <p className="text-sm text-gray-500 bengali">আপনার অ্যাপয়েন্টমেন্ট</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary"
          >
            {showForm ? 'Cancel' : '+ New Appointment'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Create Form */}
        {showForm && (
          <div className="card">
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="label">Title</label>
                <input
                  type="text"
                  className="input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Team meeting"
                  required
                />
              </div>

              <div>
                <label className="label">Notes (Optional)</label>
                <textarea
                  className="input"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label">Date</label>
                  <input
                    type="date"
                    className="input"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="label">Start Time</label>
                  <input
                    type="time"
                    className="input"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="label">End Time (Optional)</label>
                  <input
                    type="time"
                    className="input"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                  />
                </div>
              </div>

              <button type="submit" className="btn btn-primary">
                Create Appointment
              </button>
            </form>
          </div>
        )}

        {/* Appointments List */}
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : appointments.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-4">No appointments yet</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn btn-gold"
            >
              Create your first appointment
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {appointments.map((apt) => (
              <div
                key={apt.id}
                className={`card ${apt.status === 'cancelled' ? 'opacity-50' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3
                        className={`text-lg font-semibold ${
                          apt.status === 'cancelled'
                            ? 'line-through text-gray-400'
                            : 'text-navy'
                        }`}
                      >
                        {apt.title}
                      </h3>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          apt.status === 'cancelled'
                            ? 'bg-red-100 text-red-700'
                            : apt.status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}
                      >
                        {apt.status}
                      </span>
                    </div>
                    <div className="text-gray-600 text-sm space-y-1">
                      <div>📅 {formatDateTime(apt.starts_at)}</div>
                      {apt.ends_at && <div>⏰ Until {formatDateTime(apt.ends_at)}</div>}
                    </div>
                    {apt.notes && (
                      <p className="text-gray-500 text-sm mt-2">{apt.notes}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {apt.status === 'scheduled' && (
                      <button
                        onClick={() => handleCancel(apt.id)}
                        className="text-orange-500 hover:text-orange-700 text-sm"
                      >
                        Cancel
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(apt.id)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}