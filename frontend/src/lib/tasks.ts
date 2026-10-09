import api from './api';
import type { Task } from '../types';

export const tasksApi = {
  list: async (): Promise<Task[]> => {
    const response = await api.get<Task[]>('/api/v1/tasks');
    return response.data;
  },

  create: async (data: {
    title: string;
    description?: string;
    due_at?: string;
    priority?: string;
  }): Promise<Task> => {
    const response = await api.post<Task>('/api/v1/tasks', data);
    return response.data;
  },

  update: async (
    id: number,
    data: { title?: string; description?: string; status?: string; priority?: string }
  ): Promise<Task> => {
    const response = await api.patch<Task>(`/api/v1/tasks/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/tasks/${id}`);
  },
};