import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { rbacAPI, Role, Permission, RoleSummary, PermissionMatrix } from '../../services/rbacAPI';

// Types
export interface RBACState {
  roles: Role[];
  permissions: Permission[];
  roleSummary: RoleSummary[];
  permissionMatrix: PermissionMatrix | null;
  loading: boolean;
  error: string | null;
  selectedRole: Role | null;
}

// Initial state
const initialState: RBACState = {
  roles: [],
  permissions: [],
  roleSummary: [],
  permissionMatrix: null,
  loading: false,
  error: null,
  selectedRole: null,
};

// Async thunks
export const fetchRoles = createAsyncThunk(
  'rbac/fetchRoles',
  async (params?: { page?: number; size?: number; search?: string; is_active?: boolean }) => {
    const response = await rbacAPI.getRoles(params);
    return response; // Backend returns roles directly, not wrapped in data
  }
);

export const fetchPermissions = createAsyncThunk(
  'rbac/fetchPermissions',
  async (params?: { module?: string; action?: string }) => {
    const response = await rbacAPI.getPermissions(params);
    return response.data;
  }
);

export const createRole = createAsyncThunk(
  'rbac/createRole',
  async (roleData: any) => {
    const response = await rbacAPI.createRole(roleData);
    return response.data;
  }
);

export const updateRole = createAsyncThunk(
  'rbac/updateRole',
  async ({ roleId, roleData }: { roleId: number; roleData: any }) => {
    const response = await rbacAPI.updateRole(roleId, roleData);
    return response.data;
  }
);

export const cloneRole = createAsyncThunk(
  'rbac/cloneRole',
  async ({ roleId, cloneData }: { roleId: number; cloneData: any }) => {
    const response = await rbacAPI.cloneRole(roleId, cloneData);
    return response.data;
  }
);

export const deleteRole = createAsyncThunk(
  'rbac/deleteRole',
  async (roleId: number) => {
    await rbacAPI.deleteRole(roleId);
    return roleId;
  }
);

export const fetchRoleSummary = createAsyncThunk(
  'rbac/fetchRoleSummary',
  async () => {
    const response = await rbacAPI.getRoleSummary();
    return response.data;
  }
);

export const fetchPermissionMatrix = createAsyncThunk(
  'rbac/fetchPermissionMatrix',
  async () => {
    const response = await rbacAPI.getPermissionMatrix();
    return response.data;
  }
);

// Slice
const rbacSlice = createSlice({
  name: 'rbac',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedRole: (state, action: PayloadAction<Role | null>) => {
      state.selectedRole = action.payload;
    },
    clearSelectedRole: (state) => {
      state.selectedRole = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch roles
    builder
      .addCase(fetchRoles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoles.fulfilled, (state, action) => {
        state.loading = false;
        state.roles = action.payload;
      })
      .addCase(fetchRoles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch roles';
      });

    // Fetch permissions
    builder
      .addCase(fetchPermissions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPermissions.fulfilled, (state, action) => {
        state.loading = false;
        state.permissions = action.payload.data || action.payload;
      })
      .addCase(fetchPermissions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch permissions';
      });

    // Create role
    builder
      .addCase(createRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createRole.fulfilled, (state, action) => {
        state.loading = false;
        state.roles.push(action.payload);
      })
      .addCase(createRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create role';
      });

    // Update role
    builder
      .addCase(updateRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateRole.fulfilled, (state, action) => {
        state.loading = false;
        const updatedRole = action.payload.data;
        const index = state.roles.findIndex(role => role.id === updatedRole.id);
        if (index !== -1) {
          state.roles[index] = updatedRole;
        }
        if (state.selectedRole?.id === updatedRole.id) {
          state.selectedRole = updatedRole;
        }
      })
      .addCase(updateRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update role';
      });

    // Clone role
    builder
      .addCase(cloneRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(cloneRole.fulfilled, (state, action) => {
        state.loading = false;
        state.roles.push(action.payload.data);
      })
      .addCase(cloneRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to clone role';
      });

    // Delete role
    builder
      .addCase(deleteRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteRole.fulfilled, (state, action) => {
        state.loading = false;
        state.roles = state.roles.filter(role => role.id !== action.payload);
        if (state.selectedRole?.id === action.payload) {
          state.selectedRole = null;
        }
      })
      .addCase(deleteRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete role';
      });

    // Fetch role summary
    builder
      .addCase(fetchRoleSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoleSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.roleSummary = action.payload.data || action.payload;
      })
      .addCase(fetchRoleSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch role summary';
      });

    // Fetch permission matrix
    builder
      .addCase(fetchPermissionMatrix.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPermissionMatrix.fulfilled, (state, action) => {
        state.loading = false;
        state.permissionMatrix = action.payload.data || action.payload;
      })
      .addCase(fetchPermissionMatrix.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch permission matrix';
      });
  },
});

export const { clearError, setSelectedRole, clearSelectedRole } = rbacSlice.actions;
export default rbacSlice.reducer; 