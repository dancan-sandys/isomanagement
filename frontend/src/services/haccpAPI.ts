import { AxiosResponse } from 'axios';
import api from './api';

// HACCP API
export const haccpAPI = {
  // Products
  getProducts: async () => {
    const response: AxiosResponse = await api.get('/haccp/products');
    return response.data;
  },

  getProduct: async (productId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/products/${productId}`);
    return response.data;
  },

  createProduct: async (productData: any) => {
    const response: AxiosResponse = await api.post('/haccp/products', productData);
    return response.data;
  },

  updateProduct: async (productId: number, productData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/products/${productId}`, productData);
    return response.data;
  },

  deleteProduct: async (productId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/products/${productId}`);
    return response.data;
  },

  // Process Flows
  createProcessFlow: async (productId: number, flowData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/process-flows`, flowData);
    return response.data;
  },

  updateProcessFlow: async (flowId: number, flowData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/process-flows/${flowId}`, flowData);
    return response.data;
  },

  deleteProcessFlow: async (flowId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/process-flows/${flowId}`);
    return response.data;
  },

  // Hazards
  createHazard: async (productId: number, hazardData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/hazards`, hazardData);
    return response.data;
  },

  updateHazard: async (hazardId: number, hazardData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/hazards/${hazardId}`, hazardData);
    return response.data;
  },

  deleteHazard: async (hazardId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/hazards/${hazardId}`);
    return response.data;
  },

  runDecisionTree: async (hazardId: number) => {
    const response: AxiosResponse = await api.post(`/haccp/hazards/${hazardId}/decision-tree`);
    return response.data;
  },

  // CCPs
  createCCP: async (productId: number, ccpData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/ccps`, ccpData);
    return response.data;
  },

  updateCCP: async (ccpId: number, ccpData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/ccps/${ccpId}`, ccpData);
    return response.data;
  },

  deleteCCP: async (ccpId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/ccps/${ccpId}`);
    return response.data;
  },

  // Monitoring Logs
  createMonitoringLog: async (ccpId: number, logData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/ccps/${ccpId}/monitoring-logs`, logData);
    return response.data;
  },

  getMonitoringLogs: async (ccpId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/ccps/${ccpId}/monitoring-logs`);
    return response.data;
  },

  // Verification Logs
  createVerificationLog: async (ccpId: number, logData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/ccps/${ccpId}/verification-logs`, logData);
    return response.data;
  },

  getVerificationLogs: async (ccpId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/ccps/${ccpId}/verification-logs`);
    return response.data;
  },

  // Dashboard and Reports
  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/haccp/dashboard');
    return response.data;
  },

  getEnhancedDashboard: async () => {
    const response: AxiosResponse = await api.get('/haccp/dashboard/enhanced');
    return response.data;
  },

  getAlertsSummary: async (days: number = 7) => {
    const response: AxiosResponse = await api.get(`/haccp/alerts/summary?days=${days}`);
    return response.data;
  },

  getFlowchartData: async (productId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/products/${productId}/flowchart`);
    return response.data;
  },

  generateReport: async (productId: number, reportRequest: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/reports`, reportRequest);
    return response.data;
  },
};

export default haccpAPI; 