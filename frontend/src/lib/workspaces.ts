import api from './api';
import type { Workspace } from '../types';

export const workspacesApi = {
  list: async (): Promise<Workspace[]> => {
    const response = await api.get<Workspace[]>('/api/v1/workspaces');
    return response.data;
  },

  create: async (data: { name: string; type: 'personal' | 'business' }): Promise<Workspace> => {
    const response = await api.post<Workspace>('/api/v1/workspaces', data);
    return response.data;
  },

  get: async (id: number): Promise<Workspace> => {
    const response = await api.get<Workspace>(`/api/v1/workspaces/${id}`);
    return response.data;
  },
};