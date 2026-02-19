import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import notificationReducer from './slices/notificationSlice';
import rbacReducer from './slices/rbacSlice';
import documentReducer from './slices/documentSlice';
import haccpReducer from './slices/haccpSlice';
import traceabilityReducer from './slices/traceabilitySlice';
import supplierReducer from './slices/supplierSlice';
import ncReducer from './slices/ncSlice';
import trainingReducer from './slices/trainingSlice';
import riskReducer from './slices/riskSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    notifications: notificationReducer,
    rbac: rbacReducer,
    documents: documentReducer,
    haccp: haccpReducer,
    traceability: traceabilityReducer,
    supplier: supplierReducer,
    nc: ncReducer,
  training: trainingReducer,
  risk: riskReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 