import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { tasksApi } from '../lib/tasks';
import type { Task } from '../types';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('normal');

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await tasksApi.list();
      setTasks(data);
    } catch {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const data = await tasksApi.list();
        if (active) setTasks(data);
      } catch {
        if (active) setError('Failed to load tasks');
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
    if (!title.trim()) return;

    try {
      await tasksApi.create({ title, description, priority });
      setTitle('');
      setDescription('');
      setPriority('normal');
      setShowForm(false);
      loadTasks();
    } catch {
      setError('Failed to create task');
    }
  };

  const handleComplete = async (task: Task) => {
    try {
      const newStatus = task.status === 'completed' ? 'pending' : 'completed';
      await tasksApi.update(task.id, { status: newStatus });
      loadTasks();
    } catch {
      setError('Failed to update task');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await tasksApi.delete(id);
      loadTasks();
    } catch {
      setError('Failed to delete task');
    }
  };

  return (
    <Layout title="Tasks">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-navy">Your Tasks</h2>
            <p className="text-sm text-gray-500 bengali">আপনার টাস্কসমূহ</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary"
          >
            {showForm ? 'Cancel' : '+ New Task'}
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
                  placeholder="What needs to be done?"
                  required
                />
              </div>

              <div>
                <label className="label">Description (Optional)</label>
                <textarea
                  className="input"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add details..."
                  rows={3}
                />
              </div>

              <div>
                <label className="label">Priority</label>
                <select
                  className="input"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                </select>
              </div>

              <button type="submit" className="btn btn-primary">
                Create Task
              </button>
            </form>
          </div>
        )}

        {/* Tasks List */}
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading tasks...</div>
        ) : tasks.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-4">No tasks yet</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn btn-gold"
            >
              Create your first task
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="card flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={task.status === 'completed'}
                      onChange={() => handleComplete(task)}
                      className="w-5 h-5 cursor-pointer"
                    />
                    <h3
                      className={`text-lg font-semibold ${
                        task.status === 'completed'
                          ? 'line-through text-gray-400'
                          : 'text-navy'
                      }`}
                    >
                      {task.title}
                    </h3>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        task.priority === 'high'
                          ? 'bg-red-100 text-red-700'
                          : task.priority === 'low'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                  {task.description && (
                    <p className="text-gray-600 mt-2 ml-8">{task.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(task.id)}
                  className="text-red-500 hover:text-red-700 px-3 py-1"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}