import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import notificationReducer from './slices/notificationSlice';
import rbacReducer from './slices/rbacSlice';
import documentReducer from './slices/documentSlice';
import haccpReducer from './slices/haccpSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    notifications: notificationReducer,
    rbac: rbacReducer,
    documents: documentReducer,
    haccp: haccpReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 