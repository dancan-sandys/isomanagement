export interface ContactSurface {
  id: number;
  name: string;
  composition?: string | null;
  description?: string | null;
  source?: string | null;
  provenance?: string | null;
  point_of_contact?: string | null;
  material?: string | null;
  main_processing_steps?: string | null;
  packaging_material?: string | null;
  storage_conditions?: string | null;
  shelf_life?: string | null;
  possible_inherent_hazards?: string | null;
  fs_acceptance_criteria?: string | null;
  created_by?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

