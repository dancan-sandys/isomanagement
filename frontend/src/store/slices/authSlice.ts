import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api';

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_id: number;
  role_name?: string;
  status: string;
  department?: string;
  position?: string;
  phone?: string;
  employee_id?: string;
  profile_picture?: string;
  bio?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
};

// Helper function to check if user has specific role
export const hasRole = (user: User | null, roleName: string): boolean => {
  if (!user || !user.role_name) return false;
  return user.role_name.toLowerCase() === roleName.toLowerCase();
};

// Helper function to check if user is system administrator
export const isSystemAdministrator = (user: User | null): boolean => {
  return hasRole(user, 'System Administrator');
};

// Helper function to check if user can manage users
export const canManageUsers = (user: User | null): boolean => {
  if (!user) return false;
  return isSystemAdministrator(user) || hasRole(user, 'QA Manager');
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await authAPI.login({ username, password });
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const signup = createAsyncThunk(
  'auth/signup',
  async (signupData: {
    username: string;
    email: string;
    password: string;
    full_name: string;
    department?: string;
    position?: string;
    phone?: string;
    employee_id?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await authAPI.signup(signupData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Signup failed');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout();
      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Logout failed');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.me();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get user data');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.data.user;
        state.token = action.payload.data.access_token;
        state.refreshToken = action.payload.data.refresh_token;
        state.error = null;
        
        // Store tokens in localStorage
        localStorage.setItem('access_token', action.payload.data.access_token);
        localStorage.setItem('refresh_token', action.payload.data.refresh_token);
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Login failed';
      })
      
      // Signup
      .addCase(signup.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(signup.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false; // Signup doesn't automatically log in
        state.user = action.payload.data;
        state.error = null;
        // Don't set tokens - user needs to login after signup
      })
      .addCase(signup.rejected, (state, action) => {
        state.isLoading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Signup failed';
      })
      
      // Logout
      .addCase(logout.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        
        // Clear tokens from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      })
      .addCase(logout.rejected, (state, action) => {
        state.isLoading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Logout failed';
      })
      
      // Get current user
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data;
        state.isAuthenticated = true;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to get user data';
      });
  },
});

export const { clearError, setLoading } = authSlice.actions;

// Export refreshAuth function for AuthProvider
export const refreshAuth = createAsyncThunk(
  'auth/refreshAuth',
  async (_, { rejectWithValue }) => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await authAPI.refresh(refreshToken);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Token refresh failed');
    }
  }
);

export default authSlice.reducer; 