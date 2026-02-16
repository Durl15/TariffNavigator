/**
 * Admin API Service
 * Handles all admin panel API calls
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with auth interceptor
const adminApi = axios.create({
  baseURL: `${API_BASE_URL}/admin`,
});

// Add auth token to requests
adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'viewer' | 'user' | 'admin' | 'superadmin';
  organization_id: string | null;
  organization_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  is_email_verified: boolean;
  last_login_at: string | null;
  login_count: number;
  created_at: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
  status: string;
  max_users: number;
  max_calculations_per_month: number;
  user_count: number;
  calculation_count_this_month: number;
  created_at: string;
}

export interface SystemStats {
  total_users: number;
  active_users: number;
  total_organizations: number;
  total_calculations: number;
  calculations_this_month: number;
  calculations_today: number;
  total_shared_links: number;
  active_api_keys: number;
  storage_used_mb: number;
  users_last_7_days: number;
  calculations_last_7_days: number;
  avg_calculation_time_ms: number;
  avg_api_response_time_ms: number;
}

export interface AuditLog {
  id: number;
  user_id: string | null;
  user_email: string | null;
  organization_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  changes: Record<string, any> | null;
  ip_address: string | null;
  user_agent: string | null;
  endpoint: string | null;
  method: string | null;
  status_code: number | null;
  duration_ms: number | null;
  created_at: string;
}

export interface AuditLogListResponse {
  logs: AuditLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UserActivityStats {
  date: string;
  new_users: number;
  active_users: number;
  calculations: number;
}

export interface PopularHSCode {
  hs_code: string;
  usage_count: number;
  unique_users: number;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  full_name: string;
  role: 'viewer' | 'user' | 'admin' | 'superadmin';
  organization_id?: string;
}

export interface UpdateUserRequest {
  email?: string;
  full_name?: string;
  role?: 'viewer' | 'user' | 'admin' | 'superadmin';
  is_active?: boolean;
  organization_id?: string;
  password?: string;
}

export interface BulkActionRequest {
  action: 'activate' | 'deactivate' | 'delete' | 'change_role';
  user_ids: string[];
  new_role?: 'viewer' | 'user' | 'admin' | 'superadmin';
}

export interface BulkActionResponse {
  success_count: number;
  failed_count: number;
  errors: string[] | null;
}

// ============================================================================
// User Management API
// ============================================================================

export const getUsers = async (params: {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  is_active?: boolean;
  organization_id?: string;
}): Promise<UserListResponse> => {
  const { data } = await adminApi.get('/users', { params });
  return data;
};

export const getUser = async (userId: string): Promise<User> => {
  const { data } = await adminApi.get(`/users/${userId}`);
  return data;
};

export const createUser = async (userData: CreateUserRequest): Promise<User> => {
  const { data } = await adminApi.post('/users', userData);
  return data;
};

export const updateUser = async (userId: string, userData: UpdateUserRequest): Promise<User> => {
  const { data } = await adminApi.put(`/users/${userId}`, userData);
  return data;
};

export const deleteUser = async (userId: string, hardDelete = false): Promise<void> => {
  await adminApi.delete(`/users/${userId}`, { params: { hard_delete: hardDelete } });
};

export const bulkUserAction = async (request: BulkActionRequest): Promise<BulkActionResponse> => {
  const { data } = await adminApi.post('/users/bulk-action', request);
  return data;
};

// ============================================================================
// Organization Management API
// ============================================================================

export const getOrganizations = async (): Promise<Organization[]> => {
  const { data } = await adminApi.get('/organizations');
  return data;
};

export const createOrganization = async (orgData: {
  name: string;
  slug: string;
  plan?: string;
  max_users?: number;
  max_calculations_per_month?: number;
}): Promise<Organization> => {
  const { data } = await adminApi.post('/organizations', orgData);
  return data;
};

export const updateOrganization = async (
  orgId: string,
  orgData: {
    name?: string;
    slug?: string;
    plan?: string;
    max_users?: number;
    max_calculations_per_month?: number;
    is_active?: boolean;
  }
): Promise<Organization> => {
  const { data } = await adminApi.put(`/organizations/${orgId}`, orgData);
  return data;
};

// ============================================================================
// Statistics & Audit API
// ============================================================================

export const getSystemStats = async (): Promise<SystemStats> => {
  const { data } = await adminApi.get('/stats');
  return data;
};

export const getActivityStats = async (days = 30): Promise<UserActivityStats[]> => {
  const { data } = await adminApi.get('/stats/activity', { params: { days } });
  return data;
};

export const getPopularHSCodes = async (limit = 10, days = 30): Promise<PopularHSCode[]> => {
  const { data } = await adminApi.get('/stats/popular-hs-codes', { params: { limit, days } });
  return data;
};

export const getAuditLogs = async (params: {
  page?: number;
  page_size?: number;
  user_id?: string;
  action?: string;
  resource_type?: string;
  date_from?: string;
  date_to?: string;
}): Promise<AuditLogListResponse> => {
  const { data } = await adminApi.get('/audit-logs', { params });
  return data;
};

export default adminApi;
