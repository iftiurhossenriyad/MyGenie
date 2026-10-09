import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { notesApi } from '../lib/notes';
import { parseApiDateTime } from '../lib/datetime';
import type { Note } from '../types';

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');

  const loadNotes = async (search?: string) => {
    try {
      setLoading(true);
      const data = await notesApi.list(search);
      setNotes(data);
    } catch {
      setError('Failed to load notes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const data = await notesApi.list();
        if (active) setNotes(data);
      } catch {
        if (active) setError('Failed to load notes');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    loadNotes(searchQuery || undefined);
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      await notesApi.create({ title, body });
      setTitle('');
      setBody('');
      setShowForm(false);
      loadNotes();
    } catch {
      setError('Failed to create note');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this note?')) return;
    try {
      await notesApi.delete(id);
      loadNotes();
    } catch {
      setError('Failed to delete note');
    }
  };

  return (
    <Layout title="Notes">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-navy">Your Notes</h2>
            <p className="text-sm text-gray-500 bengali">আপনার নোটসমূহ</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary"
          >
            {showForm ? 'Cancel' : '+ New Note'}
          </button>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            className="input flex-1"
            placeholder="Search notes by title or content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="btn btn-gold">
            Search
          </button>
          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                loadNotes();
              }}
              className="btn btn-outline"
            >
              Clear
            </button>
          )}
        </form>

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
                  placeholder="Note title"
                  required
                />
              </div>

              <div>
                <label className="label">Content</label>
                <textarea
                  className="input"
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Write your note here..."
                  rows={6}
                />
              </div>

              <button type="submit" className="btn btn-primary">
                Create Note
              </button>
            </form>
          </div>
        )}

        {/* Notes Grid */}
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading notes...</div>
        ) : notes.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-4">
              {searchQuery ? 'No notes match your search' : 'No notes yet'}
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowForm(true)}
                className="btn btn-gold"
              >
                Create your first note
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {notes.map((note) => (
              <div key={note.id} className="card flex flex-col">
                <h3 className="text-lg font-semibold text-navy mb-2">
                  {note.title}
                </h3>
                {note.body && (
                  <p className="text-gray-600 text-sm flex-1 whitespace-pre-wrap">
                    {note.body}
                  </p>
                )}
                <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
                  <span className="text-xs text-gray-400">
                    {parseApiDateTime(note.created_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}