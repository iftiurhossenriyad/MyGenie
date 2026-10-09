import api from './api';
import type { Appointment } from '../types';

export const appointmentsApi = {
  list: async (): Promise<Appointment[]> => {
    const response = await api.get<Appointment[]>('/api/v1/appointments');
    return response.data;
  },

  create: async (data: {
    title: string;
    notes?: string;
    starts_at: string;
    ends_at?: string;
  }): Promise<Appointment> => {
    const response = await api.post<Appointment>('/api/v1/appointments', data);
    return response.data;
  },

  update: async (
    id: number,
    data: { title?: string; notes?: string; status?: string }
  ): Promise<Appointment> => {
    const response = await api.patch<Appointment>(
      `/api/v1/appointments/${id}`,
      data
    );
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/appointments/${id}`);
  },
};