import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import { getApiErrorMessage } from '../lib/apiErrors';
import { workspacesApi } from '../lib/workspaces';

export default function CreateWorkspacePage() {
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const { setCurrentWorkspace } = useWorkspace();
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setSaving(true);

    try {
      const workspace = await workspacesApi.create({
        name: name.trim(),
        type: 'business',
      });
      setCurrentWorkspace(workspace);
      navigate('/business');
    } catch (createError: unknown) {
      setError(
        getApiErrorMessage(
          createError,
          'Failed to create business workspace. Please try again.'
        )
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout title="Create Business Workspace">
      <div className="mx-auto max-w-xl">
        <div className="card">
          <h2 className="mb-2 text-2xl font-bold text-navy">
            Create Business Workspace
          </h2>
          <p className="mb-6 text-gray-600">
            Set up a workspace for your business products, orders, bookings, and
            customer conversations.
          </p>

          {error && (
            <div
              role="alert"
              className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="workspace-name" className="label">
                Business name
              </label>
              <input
                id="workspace-name"
                type="text"
                className="input"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="My business"
                minLength={2}
                maxLength={150}
                required
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={saving || name.trim().length < 2}
              >
                {saving ? 'Creating...' : 'Create Workspace'}
              </button>
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => navigate(-1)}
                disabled={saving}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}
