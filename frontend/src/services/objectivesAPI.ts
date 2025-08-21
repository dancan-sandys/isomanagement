import { api } from './api';

export interface Objective {
  id: number;
  objective_code: string;
  title: string;
  description?: string;
  category?: string;
  measurement_unit?: string;
  frequency?: string;
  status?: 'active' | 'inactive' | 'archived';
}

export interface ObjectiveTargetPayload {
  objective_id: number;
  department_id?: number | null;
  period_start: string; // ISO
  period_end: string;   // ISO
  target_value: number;
  lower_threshold?: number | null;
  upper_threshold?: number | null;
  weight?: number;
  is_lower_better?: boolean;
  created_by: number;
}

export interface ObjectiveProgressPayload {
  objective_id: number;
  department_id?: number | null;
  period_start: string; // ISO
  period_end: string;   // ISO
  actual_value: number;
  evidence?: string;
  created_by: number;
}

const objectivesAPI = {
  listObjectives: async () => {
    const res = await api.get('/objectives');
    return res.data as Objective[];
  },

  upsertTarget: async (objectiveId: number, payload: ObjectiveTargetPayload) => {
    const res = await api.post(`/objectives/${objectiveId}/targets`, payload);
    return res.data;
  },

  upsertProgress: async (objectiveId: number, payload: ObjectiveProgressPayload) => {
    const res = await api.post(`/objectives/${objectiveId}/progress`, payload);
    return res.data;
  },

  getKPIs: async (params?: { objective_id?: number; department_id?: number; period_start?: string; period_end?: string }) => {
    const res = await api.get('/objectives/kpis', { params });
    return res.data;
  },
};

export default objectivesAPI;

