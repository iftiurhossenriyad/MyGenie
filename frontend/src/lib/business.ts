import { isAxiosError } from 'axios';
import api from './api';

export interface BusinessProfile {
  id: number;
  workspace_id: number;
  business_name: string;
  description?: string | null;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  opening_hours?: string | null;
  delivery_info?: string | null;
  policies?: string | null;
  default_language: string;
  supported_languages: string;
  created_at: string;
  updated_at?: string | null;
}

export interface FAQ {
  id: number;
  workspace_id: number;
  question: string;
  answer: string;
  question_bn?: string | null;
  answer_bn?: string | null;
  question_en?: string | null;
  answer_en?: string | null;
  language: string;
  status: string;
  created_at: string;
  updated_at?: string | null;
}

export interface Product {
  id: number;
  workspace_id: number;
  name: string;
  description?: string | null;
  sku?: string | null;
  price: number;
  currency: string;
  stock_quantity: number;
  is_available: boolean;
  status: string;
  created_at: string;
  updated_at?: string | null;
}

export interface Customer {
  id: number;
  workspace_id: number;
  display_name?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  consent_status: string;
  created_at: string;
}

export interface Order {
  id: number;
  workspace_id: number;
  customer_id?: number | null;
  order_number: string;
  status: string;
  subtotal: number;
  delivery_fee: number;
  total: number;
  currency: string;
  delivery_details?: string | null;
  customer_notes?: string | null;
  created_at: string;
  updated_at?: string | null;
  items?: OrderItem[];
}

export interface OrderItem {
  id: number;
  product_id?: number | null;
  product_name_snapshot: string;
  unit_price_snapshot: number;
  quantity: number;
  line_total: number;
}

export interface Service {
  id: number;
  workspace_id: number;
  name: string;
  description?: string | null;
  duration_minutes: number;
  capacity: number;
  price?: number | null;
  currency: string;
  status: string;
}

export interface Booking {
  id: number;
  workspace_id: number;
  customer_id?: number | null;
  service_id: number;
  starts_at: string;
  ends_at: string;
  status: string;
  notes?: string | null;
  created_at: string;
}

// ============ Business Profile API ============
export const businessApi = {
  getProfile: async (workspaceId: number): Promise<BusinessProfile | null> => {
    try {
      const response = await api.get<BusinessProfile>(
        `/api/v1/business/workspaces/${workspaceId}/profile`
      );
      return response.data;
    } catch (error: unknown) {
      if (isAxiosError(error) && error.response?.status === 404) return null;
      throw error;
    }
  },

  createProfile: async (
    workspaceId: number,
    data: Partial<BusinessProfile>
  ): Promise<BusinessProfile> => {
    const response = await api.post<BusinessProfile>(
      `/api/v1/business/workspaces/${workspaceId}/profile`,
      data
    );
    return response.data;
  },

  updateProfile: async (
    workspaceId: number,
    data: Partial<BusinessProfile>
  ): Promise<BusinessProfile> => {
    const response = await api.patch<BusinessProfile>(
      `/api/v1/business/workspaces/${workspaceId}/profile`,
      data
    );
    return response.data;
  },
};

// ============ Products API ============
export const productsApi = {
  list: async (workspaceId: number): Promise<Product[]> => {
    const response = await api.get<Product[]>(
      `/api/v1/products/workspaces/${workspaceId}/products`
    );
    return response.data;
  },

  create: async (workspaceId: number, data: Partial<Product>): Promise<Product> => {
    const response = await api.post<Product>(
      `/api/v1/products/workspaces/${workspaceId}/products`,
      data
    );
    return response.data;
  },

  update: async (productId: number, data: Partial<Product>): Promise<Product> => {
    const response = await api.patch<Product>(`/api/v1/products/${productId}`, data);
    return response.data;
  },

  adjustStock: async (productId: number, quantityChange: number): Promise<Product> => {
    const response = await api.post<Product>(
      `/api/v1/products/${productId}/inventory-adjustments`,
      { quantity_change: quantityChange }
    );
    return response.data;
  },

  delete: async (productId: number): Promise<void> => {
    await api.delete(`/api/v1/products/${productId}`);
  },
};

// ============ Orders API ============
export const ordersApi = {
  list: async (workspaceId: number): Promise<Order[]> => {
    const response = await api.get<Order[]>(
      `/api/v1/orders/workspaces/${workspaceId}/orders`
    );
    return response.data;
  },

  get: async (orderId: number): Promise<Order> => {
    const response = await api.get<Order>(`/api/v1/orders/${orderId}`);
    return response.data;
  },

  updateStatus: async (orderId: number, status: string): Promise<Order> => {
    const response = await api.patch<Order>(`/api/v1/orders/${orderId}/status`, {
      status,
    });
    return response.data;
  },
};

// ============ Services & Bookings API ============
export const bookingsApi = {
  listServices: async (workspaceId: number): Promise<Service[]> => {
    const response = await api.get<Service[]>(
      `/api/v1/bookings/workspaces/${workspaceId}/services`
    );
    return response.data;
  },

  createService: async (
    workspaceId: number,
    data: Partial<Service>
  ): Promise<Service> => {
    const response = await api.post<Service>(
      `/api/v1/bookings/workspaces/${workspaceId}/services`,
      data
    );
    return response.data;
  },

  listBookings: async (workspaceId: number): Promise<Booking[]> => {
    const response = await api.get<Booking[]>(
      `/api/v1/bookings/workspaces/${workspaceId}/bookings`
    );
    return response.data;
  },

  cancelBooking: async (bookingId: number): Promise<Booking> => {
    const response = await api.post<Booking>(
      `/api/v1/bookings/${bookingId}/cancel`
    );
    return response.data;
  },
};