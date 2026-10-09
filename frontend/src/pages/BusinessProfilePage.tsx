import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import { businessApi } from '../lib/business';
import type { BusinessProfile } from '../lib/business';

export default function BusinessProfilePage() {
  const { currentWorkspace, loading: workspaceLoading } = useWorkspace();
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    business_name: '',
    description: '',
    address: '',
    phone: '',
    email: '',
    website: '',
    opening_hours: '',
    delivery_info: '',
    policies: '',
    default_language: 'bn',
    supported_languages: 'bn,en',
  });

  useEffect(() => {
    if (!currentWorkspace || currentWorkspace.type !== 'business') return;

    let active = true;

    const load = async () => {
      try {
        const data = await businessApi.getProfile(currentWorkspace.id);
        if (!active) return;
        if (data) {
          setProfile(data);
          setFormData({
            business_name: data.business_name || '',
            description: data.description || '',
            address: data.address || '',
            phone: data.phone || '',
            email: data.email || '',
            website: data.website || '',
            opening_hours: data.opening_hours || '',
            delivery_info: data.delivery_info || '',
            policies: data.policies || '',
            default_language: data.default_language || 'bn',
            supported_languages: data.supported_languages || 'bn,en',
          });
        }
      } catch (error) {
        console.error('Failed to load profile', error);
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace) return;

    setSaving(true);
    setError('');
    setSuccess('');

    try {
      if (profile) {
        const updated = await businessApi.updateProfile(
          currentWorkspace.id,
          formData
        );
        setProfile(updated);
        setSuccess('Profile updated successfully!');
      } else {
        const created = await businessApi.createProfile(
          currentWorkspace.id,
          formData
        );
        setProfile(created);
        setSuccess('Profile created successfully!');
      }
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Failed to save profile', error);
      setError('Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  if (workspaceLoading) {
    return (
      <Layout title="Business Profile">
        <div className="text-center text-gray-500 py-8">Loading...</div>
      </Layout>
    );
  }

  if (!currentWorkspace || currentWorkspace.type !== 'business') {
    return (
      <Layout title="Business Profile">
        <div className="card text-center py-12">
          <p className="text-gray-500">
            Please select a business workspace from the sidebar.
          </p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Business Profile">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-navy">Business Profile</h2>
          <p className="text-sm text-gray-500 bengali">
            আপনার ব্যবসার তথ্য আপডেট করুন
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-navy mb-4">
                Basic Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="label">Business Name *</label>
                  <input
                    type="text"
                    name="business_name"
                    className="input"
                    value={formData.business_name}
                    onChange={handleChange}
                    placeholder="My Business Shop"
                    required
                  />
                </div>
                <div>
                  <label className="label">Description</label>
                  <textarea
                    name="description"
                    className="input"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="What does your business do?"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="label">Address</label>
                  <textarea
                    name="address"
                    className="input"
                    value={formData.address}
                    onChange={handleChange}
                    placeholder="123 Test Street, Dhaka"
                    rows={2}
                  />
                </div>
              </div>
            </div>

            {/* Contact Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-navy mb-4">Contact</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Phone</label>
                  <input
                    type="tel"
                    name="phone"
                    className="input"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="01XXXXXXXXX"
                  />
                </div>
                <div>
                  <label className="label">Email</label>
                  <input
                    type="email"
                    name="email"
                    className="input"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="shop@example.com"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="label">Website</label>
                  <input
                    type="url"
                    name="website"
                    className="input"
                    value={formData.website}
                    onChange={handleChange}
                    placeholder="https://example.com"
                  />
                </div>
              </div>
            </div>

            {/* Business Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-navy mb-4">
                Business Details
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="label">Opening Hours</label>
                  <textarea
                    name="opening_hours"
                    className="input"
                    value={formData.opening_hours}
                    onChange={handleChange}
                    placeholder="Saturday - Thursday: 9 AM - 9 PM&#10;Friday: Closed"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="label">Delivery Information</label>
                  <textarea
                    name="delivery_info"
                    className="input"
                    value={formData.delivery_info}
                    onChange={handleChange}
                    placeholder="Free delivery inside Dhaka"
                    rows={2}
                  />
                </div>
                <div>
                  <label className="label">Policies</label>
                  <textarea
                    name="policies"
                    className="input"
                    value={formData.policies}
                    onChange={handleChange}
                    placeholder="Return within 7 days"
                    rows={3}
                  />
                </div>
              </div>
            </div>

            {/* Language */}
            <div className="card">
              <h3 className="text-lg font-semibold text-navy mb-4">Language</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Default Language</label>
                  <select
                    name="default_language"
                    className="input"
                    value={formData.default_language}
                    onChange={handleChange}
                  >
                    <option value="bn">বাংলা (Bangla)</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div>
                  <label className="label">Supported Languages</label>
                  <input
                    type="text"
                    name="supported_languages"
                    className="input"
                    value={formData.supported_languages}
                    onChange={handleChange}
                    placeholder="bn,en"
                  />
                </div>
              </div>
            </div>

            {/* Submit */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => window.history.back()}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="btn btn-primary"
              >
                {saving ? 'Saving...' : profile ? 'Update Profile' : 'Create Profile'}
              </button>
            </div>
          </form>
        )}
      </div>
    </Layout>
  );
}