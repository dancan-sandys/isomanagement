import api from './api';
import { AxiosResponse } from 'axios';

export interface InterestedParty {
  id: number;
  name: string;
  category: 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor';
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  website?: string;
  description?: string;
  satisfaction_level?: number; // 1-10 rating
  last_assessment_date?: string;
  next_assessment_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  expectations_count?: number;
  actions_count?: number;
  completed_actions_count?: number;
}

export interface InterestedPartyCreate {
  name: string;
  category: 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor';
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  description?: string;
  satisfaction_level?: number;
  is_active?: boolean;
}

export interface InterestedPartyUpdate {
  name?: string;
  category?: 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor';
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  description?: string;
  satisfaction_level?: number;
  is_active?: boolean;
}

export const interestedPartiesAPI = {
  // Get all interested parties
  getInterestedParties: async () => {
    const response: AxiosResponse = await api.get('/actions-log/interested-parties');
    return response.data as InterestedParty[];
  },

  // Get interested party by ID
  getInterestedParty: async (partyId: number) => {
    const response: AxiosResponse = await api.get(`/actions-log/interested-parties/${partyId}`);
    return response.data as InterestedParty;
  },

  // Get actions for a specific interested party
  getPartyActions: async (partyId: number) => {
    const response: AxiosResponse = await api.get(`/actions-log/interested-parties/${partyId}/actions`);
    return response.data;
  },

  // Create new interested party
  createInterestedParty: async (partyData: InterestedPartyCreate) => {
    const response: AxiosResponse = await api.post('/actions-log/interested-parties', partyData);
    return response.data as InterestedParty;
  },

  // Update interested party
  updateInterestedParty: async (partyId: number, partyData: InterestedPartyUpdate) => {
    const response: AxiosResponse = await api.put(`/actions-log/interested-parties/${partyId}`, partyData);
    return response.data as InterestedParty;
  }
};

export default interestedPartiesAPI;