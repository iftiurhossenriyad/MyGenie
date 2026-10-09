import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import api from '../lib/api';
import type { FAQ } from '../lib/business';

export default function FAQsPage() {
  const { currentWorkspace, loading: workspaceLoading } = useWorkspace();
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    question_bn: '',
    answer_bn: '',
    question_en: '',
    answer_en: '',
    language: 'bn',
  });

  const loadFaqs = async () => {
    if (!currentWorkspace) return;
    try {
      setLoading(true);
      const response = await api.get<FAQ[]>(
        `/api/v1/business/workspaces/${currentWorkspace.id}/faqs`
      );
      setFaqs(response.data);
    } catch {
      setError('Failed to load FAQs');
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
        const response = await api.get<FAQ[]>(
          `/api/v1/business/workspaces/${currentWorkspace.id}/faqs`
        );
        if (!active) return;
        setFaqs(response.data);
      } catch {
        if (!active) return;
        setError('Failed to load FAQs');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace || !formData.question.trim()) return;

    try {
      await api.post(
        `/api/v1/business/workspaces/${currentWorkspace.id}/faqs`,
        formData
      );
      setFormData({
        question: '',
        answer: '',
        question_bn: '',
        answer_bn: '',
        question_en: '',
        answer_en: '',
        language: 'bn',
      });
      setShowForm(false);
      loadFaqs();
    } catch {
      setError('Failed to create FAQ');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this FAQ?')) return;
    try {
      await api.delete(`/api/v1/business/faqs/${id}`);
      loadFaqs();
    } catch {
      setError('Failed to delete FAQ');
    }
  };

  if (workspaceLoading) {
    return (
      <Layout title="FAQs">
        <div className="text-center text-gray-500 py-8">Loading...</div>
      </Layout>
    );
  }

  if (!currentWorkspace || currentWorkspace.type !== 'business') {
    return (
      <Layout title="FAQs">
        <div className="card text-center py-12">
          <p className="text-gray-500">Please select a business workspace.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="FAQs">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-navy">
              Frequently Asked Questions
            </h2>
            <p className="text-sm text-gray-500 bengali">সাধারণ প্রশ্নোত্তর</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary"
          >
            {showForm ? 'Cancel' : '+ New FAQ'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {showForm && (
          <div className="card">
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="label">Question (Bangla) *</label>
                <input
                  type="text"
                  className="input bengali"
                  value={formData.question}
                  onChange={(e) =>
                    setFormData({ ...formData, question: e.target.value })
                  }
                  placeholder="আপনাদের দোকান কখন খোলা থাকে?"
                  required
                />
              </div>

              <div>
                <label className="label">Answer (Bangla) *</label>
                <textarea
                  className="input bengali"
                  value={formData.answer}
                  onChange={(e) =>
                    setFormData({ ...formData, answer: e.target.value })
                  }
                  rows={3}
                  placeholder="আমরা সকাল ৯টা থেকে রাত ৯টা পর্যন্ত খোলা।"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Question (English)</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.question_en}
                    onChange={(e) =>
                      setFormData({ ...formData, question_en: e.target.value })
                    }
                    placeholder="What are your opening hours?"
                  />
                </div>
                <div>
                  <label className="label">Answer (English)</label>
                  <textarea
                    className="input"
                    value={formData.answer_en}
                    onChange={(e) =>
                      setFormData({ ...formData, answer_en: e.target.value })
                    }
                    rows={2}
                    placeholder="We are open from 9 AM to 9 PM."
                  />
                </div>
              </div>

              <div>
                <label className="label">Default Language</label>
                <select
                  className="input"
                  value={formData.language}
                  onChange={(e) =>
                    setFormData({ ...formData, language: e.target.value })
                  }
                >
                  <option value="bn">বাংলা (Bangla)</option>
                  <option value="en">English</option>
                </select>
              </div>

              <button type="submit" className="btn btn-primary">
                Create FAQ
              </button>
            </form>
          </div>
        )}

        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : faqs.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-4">No FAQs yet</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn btn-gold"
            >
              Add your first FAQ
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {faqs.map((faq) => (
              <div key={faq.id} className="card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-navy bengali mb-2">
                      Q: {faq.question}
                    </h3>
                    <p className="text-gray-600 bengali mb-3">A: {faq.answer}</p>
                    {faq.question_en && (
                      <>
                        <p className="text-sm text-gray-500 italic">
                          Q (EN): {faq.question_en}
                        </p>
                        <p className="text-sm text-gray-500 italic">
                          A (EN): {faq.answer_en}
                        </p>
                      </>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(faq.id)}
                    className="text-red-500 hover:text-red-700 text-sm ml-4"
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