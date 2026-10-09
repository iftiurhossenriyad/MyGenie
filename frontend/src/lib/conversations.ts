import api from './api';

export interface Conversation {
  id: number;
  workspace_id: number;
  owner_user_id?: number | null;
  customer_id?: number | null;
  channel: string;
  status: string;
  assigned_staff_id?: number | null;
  language: string;
  created_at: string;
  updated_at?: string | null;
}

export interface Message {
  id: number;
  conversation_id: number;
  sender_type: string;
  sender_id?: number | null;
  content: string;
  content_type: string;
  created_at: string;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
  conversation_id: number;
}

export const conversationsApi = {
  listByWorkspace: async (workspaceId: number): Promise<Conversation[]> => {
    const response = await api.get<Conversation[]>(
      `/api/v1/conversations/workspaces/${workspaceId}`
    );
    return response.data;
  },

  create: async (data: {
    workspace_id: number;
    channel?: string;
    language?: string;
  }): Promise<Conversation> => {
    const response = await api.post<Conversation>('/api/v1/conversations', {
      workspace_id: data.workspace_id,
      channel: data.channel || 'web',
      language: data.language || 'bn',
    });
    return response.data;
  },

  get: async (id: number): Promise<Conversation> => {
    const response = await api.get<Conversation>(`/api/v1/conversations/${id}`);
    return response.data;
  },

  listMessages: async (conversationId: number): Promise<Message[]> => {
    const response = await api.get<Message[]>(
      `/api/v1/conversations/${conversationId}/messages`
    );
    return response.data;
  },

  sendMessage: async (
    conversationId: number,
    content: string,
    language: string = 'auto'
  ): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>(
      `/api/v1/conversations/${conversationId}/messages`,
      { content, language }
    );
    return response.data;
  },

  handoff: async (conversationId: number, reason?: string): Promise<Conversation> => {
    const response = await api.post<Conversation>(
      `/api/v1/conversations/${conversationId}/handoff`,
      { reason }
    );
    return response.data;
  },

  close: async (conversationId: number): Promise<Conversation> => {
    const response = await api.post<Conversation>(
      `/api/v1/conversations/${conversationId}/close`
    );
    return response.data;
  },
};