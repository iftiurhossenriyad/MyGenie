import api from './api';
import type { Note } from '../types';

export const notesApi = {
  list: async (search?: string): Promise<Note[]> => {
    const params = search ? { search } : {};
    const response = await api.get<Note[]>('/api/v1/notes', { params });
    return response.data;
  },

  create: async (data: { title: string; body?: string }): Promise<Note> => {
    const response = await api.post<Note>('/api/v1/notes', data);
    return response.data;
  },

  update: async (
    id: number,
    data: { title?: string; body?: string }
  ): Promise<Note> => {
    const response = await api.patch<Note>(`/api/v1/notes/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/notes/${id}`);
  },
};