// ============ User ============
export interface User {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  status: string;
  is_verified: boolean;
  created_at: string;
}

export interface UserCreate {
  name: string;
  email: string;
  phone?: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// ============ Workspace ============
export interface Workspace {
  id: number;
  name: string;
  type: 'personal' | 'business';
  owner_user_id: number;
  status: string;
  created_at: string;
  updated_at?: string | null;
}

// ============ Task ============
export interface Task {
  id: number;
  user_id: number;
  title: string;
  description?: string | null;
  due_at?: string | null;
  status: string;
  priority: string;
  workspace_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

// ============ Note ============
export interface Note {
  id: number;
  user_id: number;
  title: string;
  body?: string | null;
  workspace_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

// ============ Appointment ============
export interface Appointment {
  id: number;
  user_id: number;
  title: string;
  notes?: string | null;
  starts_at: string;
  ends_at?: string | null;
  status: string;
  workspace_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

// ============ Conversation ============
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

// ============ Generic API Error ============
export interface ApiValidationIssue {
  loc?: Array<string | number>;
  msg?: string;
}

export interface ApiError {
  detail: string | ApiValidationIssue[];
}