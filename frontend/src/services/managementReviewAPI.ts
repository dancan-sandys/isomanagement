import api from './api';
import { AxiosResponse } from 'axios';

// Enhanced interfaces for ISO compliance
export interface ReviewParticipant {
  user_id?: number;
  name: string;
  role: string;
  department?: string;
  email?: string;
  attendance_status?: 'present' | 'absent' | 'partial';
}

export interface MRPayload {
  title: string;
  review_date?: string;
  review_type?: 'scheduled' | 'ad_hoc' | 'emergency';
  review_scope?: string;
  attendees?: ReviewParticipant[];
  chairperson_id?: number;
  review_frequency?: string;
  
  // ISO compliance fields
  food_safety_policy_reviewed?: boolean;
  food_safety_objectives_reviewed?: boolean;
  fsms_changes_required?: boolean;
  resource_adequacy_assessment?: string;
  improvement_opportunities?: any[];
  external_issues?: string;
  internal_issues?: string;
  
  status?: 'planned' | 'in_progress' | 'completed';
  next_review_date?: string;
  agenda?: Array<{ topic: string; discussion?: string; decision?: string; order_index?: number }>;
}

export interface ReviewActionPayload {
  title: string;
  description?: string;
  assigned_to?: number;
  due_date?: string;
  action_type?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  verification_required?: boolean;
  estimated_effort_hours?: number;
  resource_requirements?: string;
}

export interface ReviewInputPayload {
  input_type: string;
  input_source?: string;
  input_data?: any;
  input_summary?: string;
  collection_date?: string;
  responsible_person_id?: number;
}

export interface ReviewOutputPayload {
  output_type: string;
  title: string;
  description?: string;
  assigned_to?: number;
  target_completion_date?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  implementation_plan?: string;
  resource_requirements?: string;
  success_criteria?: string;
  verification_required?: boolean;
}

export interface DataCollectionRequest {
  input_types: string[];
  date_range_start?: string;
  date_range_end?: string;
  include_summaries?: boolean;
}

export interface TemplatePayload {
  name: string;
  description?: string;
  agenda_template?: any[];
  input_checklist?: any[];
  output_categories?: any[];
  is_default?: boolean;
  review_frequency?: string;
  applicable_departments?: string[];
  compliance_standards?: string[];
}

const managementReviewAPI = {
  // Core review management
  list: async (params?: { page?: number; size?: number; status?: string; review_type?: string }) => {
    const resp: AxiosResponse = await api.get('/management-reviews', { params });
    return resp.data;
  },
  get: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}`);
    return resp.data;
  },
  create: async (payload: MRPayload) => {
    const resp: AxiosResponse = await api.post('/management-reviews', payload);
    return resp.data;
  },
  createFromTemplate: async (templateId: number, payload: MRPayload) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/from-template/${templateId}`, payload);
    return resp.data;
  },
  update: async (id: number, payload: Partial<MRPayload>) => {
    const resp: AxiosResponse = await api.put(`/management-reviews/${id}`, payload);
    return resp.data;
  },
  complete: async (id: number) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/${id}/complete`);
    return resp.data;
  },
  delete: async (id: number) => {
    const resp: AxiosResponse = await api.delete(`/management-reviews/${id}`);
    return resp.data;
  },

  // Data collection and inputs
  collectInputs: async (id: number, request: DataCollectionRequest) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/${id}/collect-inputs`, request);
    return resp.data;
  },
  addManualInput: async (id: number, payload: ReviewInputPayload) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/${id}/inputs`, payload);
    return resp.data;
  },
  getInputs: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}/inputs`);
    return resp.data;
  },

  // Outputs and decisions
  addOutput: async (id: number, payload: ReviewOutputPayload) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/${id}/outputs`, payload);
    return resp.data;
  },
  getOutputs: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}/outputs`);
    return resp.data;
  },
  updateOutputProgress: async (outputId: number, progress: number, notes?: string) => {
    const params = { progress_percentage: progress };
    if (notes) params.progress_notes = notes;
    const resp: AxiosResponse = await api.put(`/management-reviews/outputs/${outputId}/progress`, null, { params });
    return resp.data;
  },

  // Enhanced action management
  addAction: async (id: number, payload: ReviewActionPayload) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/${id}/actions`, payload);
    return resp.data;
  },
  listActions: async (id: number, status?: string) => {
    const params = status ? { status } : undefined;
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}/actions`, { params });
    return resp.data;
  },
  updateAction: async (actionId: number, payload: Partial<ReviewActionPayload>) => {
    const resp: AxiosResponse = await api.put(`/management-reviews/actions/${actionId}`, payload);
    return resp.data;
  },
  completeAction: async (actionId: number) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/actions/${actionId}/complete`);
    return resp.data;
  },
  getOverdueActions: async (reviewId?: number) => {
    const params = reviewId ? { review_id: reviewId } : undefined;
    const resp: AxiosResponse = await api.get('/management-reviews/actions/overdue', { params });
    return resp.data;
  },

  // Analytics and reporting
  getAnalytics: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}/analytics`);
    return resp.data;
  },
  checkCompliance: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}/compliance-check`);
    return resp.data;
  },

  // Template management
  listTemplates: async (activeOnly: boolean = true) => {
    const params = { active_only: activeOnly };
    const resp: AxiosResponse = await api.get('/management-reviews/templates', { params });
    return resp.data;
  },
  getTemplate: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/templates/${id}`);
    return resp.data;
  },
  getDefaultTemplate: async () => {
    const resp: AxiosResponse = await api.get('/management-reviews/templates/default');
    return resp.data;
  },
  createTemplate: async (payload: TemplatePayload) => {
    const resp: AxiosResponse = await api.post('/management-reviews/templates', payload);
    return resp.data;
  },
};

export default managementReviewAPI;


