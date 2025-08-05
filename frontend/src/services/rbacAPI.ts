import api from './api';

// Types
export interface Permission {
  id: number;
  module: string;
  action: string;
  description?: string;
  created_at: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
  is_default: boolean;
  is_editable: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  permissions: Permission[];
  user_count?: number;
}

export interface RoleCreate {
  name: string;
  description?: string;
  is_default?: boolean;
  is_editable?: boolean;
  is_active?: boolean;
  permissions: number[];
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
  permissions?: number[];
}

export interface RoleClone {
  name: string;
  description?: string;
  permissions: number[];
}

export interface UserPermission {
  id: number;
  user_id: number;
  permission_id: number;
  granted: boolean;
  granted_by?: number;
  granted_at: string;
  permission: Permission;
}

export interface UserPermissionCreate {
  permission_id: number;
  granted: boolean;
}

export interface RoleSummary {
  role_id: number;
  role_name: string;
  user_count: number;
  permissions: Permission[];
}

export interface PermissionMatrix {
  modules: string[];
  permissions: string[];
  role_permissions: Record<string, Record<string, string[]>>;
}

// API functions
export const rbacAPI = {
  // Permission endpoints
  getPermissions: async (params?: { module?: string; action?: string }) => {
    const response = await api.get('/rbac/permissions', { params });
    return response.data;
  },

  createPermission: async (permissionData: { module: string; action: string; description?: string }) => {
    const response = await api.post('/rbac/permissions', permissionData);
    return response.data;
  },

  // Role endpoints
  getRoles: async (params?: { page?: number; size?: number; search?: string; is_active?: boolean }) => {
    const response = await api.get('/rbac/roles', { params });
    return response.data;
  },

  getRole: async (roleId: number) => {
    const response = await api.get(`/rbac/roles/${roleId}`);
    return response.data;
  },

  createRole: async (roleData: RoleCreate) => {
    const response = await api.post('/rbac/roles', roleData);
    return response.data;
  },

  updateRole: async (roleId: number, roleData: RoleUpdate) => {
    const response = await api.put(`/rbac/roles/${roleId}`, roleData);
    return response.data;
  },

  cloneRole: async (roleId: number, cloneData: RoleClone) => {
    const response = await api.post(`/rbac/roles/${roleId}/clone`, cloneData);
    return response.data;
  },

  deleteRole: async (roleId: number) => {
    const response = await api.delete(`/rbac/roles/${roleId}`);
    return response.data;
  },

  getRoleSummary: async () => {
    const response = await api.get('/rbac/roles/summary');
    return response.data;
  },

  getPermissionMatrix: async () => {
    const response = await api.get('/rbac/permissions/matrix');
    return response.data;
  },

  // User permission endpoints
  getUserPermissions: async (userId: number) => {
    const response = await api.get(`/rbac/users/${userId}/permissions`);
    return response.data;
  },

  assignUserPermission: async (userId: number, permissionData: UserPermissionCreate) => {
    const response = await api.post(`/rbac/users/${userId}/permissions`, permissionData);
    return response.data;
  },

  removeUserPermission: async (userId: number, permissionId: number) => {
    const response = await api.delete(`/rbac/users/${userId}/permissions/${permissionId}`);
    return response.data;
  },

  // Permission check endpoint
  checkPermission: async (module: string, action: string) => {
    const response = await api.post('/rbac/check-permission', { module, action });
    return response.data;
  },
}; 