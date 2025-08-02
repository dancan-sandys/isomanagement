import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api';
import { getToken, getRefreshToken, isTokenValid, setToken as setTokenStorage, setRefreshToken as setRefreshTokenStorage, removeTokens } from '../../utils/auth';

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  department?: string;
  position?: string;
  phone?: string;
  employee_id?: string;
  profile_picture?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Check if we have valid tokens on app startup
const storedToken = getToken();
const storedRefreshToken = getRefreshToken();
const hasValidToken = storedToken ? isTokenValid(storedToken) : false;

// Initial state
const initialState: AuthState = {
  user: null,
  token: storedToken,
  refreshToken: storedRefreshToken,
  isAuthenticated: hasValidToken,
  isLoading: false, // Always start with loading false
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(username, password);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout();
      return;
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
      return rejectWithValue(error.response?.data?.detail || 'Failed to get user info');
    }
  }
);

export const refreshAuth = createAsyncThunk(
  'auth/refresh',
  async (_, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: AuthState };
      const refreshToken = state.auth.refreshToken;
      
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

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.isAuthenticated = true;
      setTokenStorage(action.payload);
    },
    setRefreshToken: (state, action: PayloadAction<string>) => {
      state.refreshToken = action.payload;
      setRefreshTokenStorage(action.payload);
    },
    clearAuth: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      removeTokens();
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        console.log('Auth slice - login.pending - setting isLoading to true');
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        console.log('Auth slice - login.fulfilled - setting isLoading to false');
        state.isLoading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.user = action.payload.user;
        state.error = null;
        setTokenStorage(action.payload.access_token);
        setRefreshTokenStorage(action.payload.refresh_token);
      })
      .addCase(login.rejected, (state, action) => {
        console.log('Auth slice - login.rejected - setting isLoading to false');
        state.isLoading = false;
        state.error = action.payload as string;
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
        removeTokens();
      })
      .addCase(logout.rejected, (state) => {
        state.isLoading = false;
        // Still clear auth state even if logout API fails
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        removeTokens();
      })
      // Get current user
      .addCase(getCurrentUser.pending, (state) => {
        console.log('Auth slice - getCurrentUser.pending - setting isLoading to true');
        state.isLoading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        console.log('Auth slice - getCurrentUser.fulfilled - setting isLoading to false');
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        console.log('Auth slice - getCurrentUser.rejected - setting isLoading to false');
        state.isLoading = false;
        state.error = action.payload as string;
        // If we can't get user info, they might not be authenticated
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        removeTokens();
      })
      // Refresh auth
      .addCase(refreshAuth.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(refreshAuth.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
        setTokenStorage(action.payload.access_token);
        setRefreshTokenStorage(action.payload.refresh_token);
      })
      .addCase(refreshAuth.rejected, (state) => {
        state.isLoading = false;
        // If refresh fails, clear auth state
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        removeTokens();
      });
  },
});

export const { clearError, setToken, setRefreshToken, clearAuth } = authSlice.actions;
export default authSlice.reducer; 