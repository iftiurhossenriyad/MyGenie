import { useState, useEffect, useRef, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import { conversationsApi } from '../lib/conversations';
import { parseApiDateTime } from '../lib/datetime';
import type { Conversation, Message } from '../lib/conversations';

export default function ChatPage() {
  const { currentWorkspace } = useWorkspace();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadMessages = async (conversationId: number) => {
    try {
      const data = await conversationsApi.listMessages(conversationId);
      setMessages(data);
    } catch {
      setError('Failed to load messages');
    }
  };

  useEffect(() => {
    if (!currentWorkspace) return;

    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        const data = await conversationsApi.listByWorkspace(currentWorkspace.id);
        if (!active) return;
        setConversations(data);

        if (data.length > 0) {
          setActiveConversation(data[0]);
          const messagesData = await conversationsApi.listMessages(data[0].id);
          if (!active) return;
          setMessages(messagesData);
        } else {
          setActiveConversation(null);
          setMessages([]);
        }
      } catch {
        if (!active) return;
        setError('Failed to load conversations');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewConversation = async () => {
    if (!currentWorkspace) return;
    try {
      const newConv = await conversationsApi.create({
        workspace_id: currentWorkspace.id,
        channel: 'web',
        language: 'bn',
      });
      setConversations([newConv, ...conversations]);
      setActiveConversation(newConv);
      setMessages([]);
    } catch {
      setError('Failed to create conversation');
    }
  };

  const handleSelectConversation = async (conv: Conversation) => {
    setActiveConversation(conv);
    await loadMessages(conv.id);
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !activeConversation) return;

    const userContent = input.trim();
    setInput('');
    setSending(true);

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: -1,
      conversation_id: activeConversation.id,
      sender_type: 'user',
      sender_id: null,
      content: userContent,
      content_type: 'text',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await conversationsApi.sendMessage(
        activeConversation.id,
        userContent,
        activeConversation.language
      );
      // Replace temp with real messages
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== -1),
        response.user_message,
        response.assistant_message,
      ]);
    } catch (error) {
      console.error('Failed to send message', error);
      setError('Failed to send message');
      setMessages((prev) => prev.filter((m) => m.id !== -1));
    } finally {
      setSending(false);
    }
  };

  const handleHandoff = async () => {
    if (!activeConversation) return;
    if (!confirm('Hand off this conversation to human staff?')) return;

    try {
      const updated = await conversationsApi.handoff(
        activeConversation.id,
        'Customer requested human support'
      );
      setActiveConversation(updated);
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );
      await loadMessages(updated.id);
    } catch {
      setError('Failed to handoff');
    }
  };

  const formatTime = (iso: string) => {
    return parseApiDateTime(iso).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!currentWorkspace) {
    return (
      <Layout title="AI Chat">
        <div className="card text-center py-12">
          <p className="text-gray-500">Please select a workspace.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="AI Chat">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-[calc(100vh-180px)]">
        {/* Conversations List */}
        <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
          <div className="p-4 border-b border-gray-100">
            <button
              onClick={handleNewConversation}
              className="btn btn-primary w-full text-sm"
            >
              + New Chat
            </button>
          </div>

          <div className="flex-1 overflow-auto p-2 space-y-1">
            {loading ? (
              <div className="text-center text-gray-400 text-sm py-4">Loading...</div>
            ) : conversations.length === 0 ? (
              <div className="text-center text-gray-400 text-sm py-8 px-4">
                No conversations yet. Start a new chat!
              </div>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeConversation?.id === conv.id
                      ? 'bg-navy text-white'
                      : 'hover:bg-gray-100 text-navy'
                  }`}
                >
                  <div className="font-medium">Chat #{conv.id}</div>
                  <div
                    className={`text-xs ${
                      activeConversation?.id === conv.id
                        ? 'text-gray-300'
                        : 'text-gray-500'
                    }`}
                  >
                    {conv.status} • {conv.channel}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
          {!activeConversation ? (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <p className="text-lg mb-2">Start a new conversation</p>
                <p className="text-sm">Click "+ New Chat" to begin</p>
              </div>
            </div>
          ) : (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-navy">
                    Chat #{activeConversation.id}
                  </h3>
                  <p className="text-xs text-gray-500">
                    Status: <span className="font-medium">{activeConversation.status}</span>
                    {activeConversation.status === 'handoff' && (
                      <span className="ml-2 text-orange-600">
                        • Waiting for human staff
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex gap-2">
                  {activeConversation.status !== 'handoff' &&
                    activeConversation.status !== 'closed' && (
                      <button
                        onClick={handleHandoff}
                        className="text-xs px-3 py-1 bg-orange-100 text-orange-700 hover:bg-orange-200 rounded"
                      >
                        Handoff to Staff
                      </button>
                    )}
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-auto p-4 space-y-3">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-400 py-8">
                    <p className="mb-2">👋 Hello! I'm MyGenie Assistant.</p>
                    <p className="text-sm">Ask me anything about the business!</p>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${
                        msg.sender_type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                          msg.sender_type === 'user'
                            ? 'bg-navy text-white'
                            : msg.sender_type === 'assistant'
                            ? 'bg-gray-100 text-navy'
                            : msg.sender_type === 'system'
                            ? 'bg-yellow-50 text-yellow-800 text-xs italic'
                            : 'bg-gold text-navy-dark'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <p
                          className={`text-xs mt-1 ${
                            msg.sender_type === 'user'
                              ? 'text-gray-300'
                              : 'text-gray-500'
                          }`}
                        >
                          {formatTime(msg.created_at)}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <form
                onSubmit={handleSend}
                className="p-4 border-t border-gray-100 flex gap-2"
              >
                <input
                  type="text"
                  className="input flex-1"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message... / আপনার বার্তা লিখুন..."
                  disabled={sending}
                />
                <button
                  type="submit"
                  disabled={sending || !input.trim()}
                  className="btn btn-primary"
                >
                  {sending ? '...' : 'Send'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
    </Layout>
  );
}