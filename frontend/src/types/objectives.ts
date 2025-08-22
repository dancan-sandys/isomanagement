// Objective Types
export type ObjectiveType = 'corporate' | 'departmental' | 'operational';
export type HierarchyLevel = 'strategic' | 'tactical' | 'operational';
export type MeasurementFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually';
export type TrendDirection = 'improving' | 'declining' | 'stable';
export type PerformanceColor = 'green' | 'yellow' | 'red';
export type DataSource = 'manual' | 'system' | 'integration';

// Main Objective Interface
export interface Objective {
  id: number;
  title: string;
  description: string;
  objective_type: ObjectiveType;
  hierarchy_level: HierarchyLevel;
  parent_objective_id?: number;
  department_id?: number;
  department_name?: string;
  baseline_value?: number;
  target_value: number;
  current_value?: number;
  weight: number;
  measurement_frequency: MeasurementFrequency;
  unit_of_measure: string;
  start_date: string;
  target_date: string;
  trend_direction: TrendDirection;
  performance_color: PerformanceColor;
  automated_calculation: boolean;
  data_source: DataSource;
  last_updated_by?: string;
  last_updated_at?: string;
  created_at: string;
  updated_at: string;
}

// Objective Creation Interface
export interface CreateObjective {
  title: string;
  description: string;
  objective_type: ObjectiveType;
  hierarchy_level: HierarchyLevel;
  parent_objective_id?: number;
  department_id?: number;
  baseline_value?: number;
  target_value: number;
  weight: number;
  measurement_frequency: MeasurementFrequency;
  unit_of_measure: string;
  start_date: string;
  target_date: string;
  automated_calculation?: boolean;
  data_source?: DataSource;
}

// Objective Update Interface
export interface UpdateObjective extends Partial<CreateObjective> {
  id: number;
}

// Progress Entry Interface
export interface ProgressEntry {
  id: number;
  objective_id: number;
  recorded_value: number;
  recorded_date: string;
  notes?: string;
  recorded_by: string;
  created_at: string;
}

// Progress Creation Interface
export interface CreateProgress {
  objective_id: number;
  recorded_value: number;
  recorded_date: string;
  notes?: string;
}

// Department Interface
export interface Department {
  id: number;
  name: string;
  department_code: string;
  description?: string;
  parent_department_id?: number;
  status: 'active' | 'inactive';
  color_code?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

// Dashboard KPI Interface
export interface DashboardKPI {
  total_objectives: number;
  completed_objectives: number;
  on_track_objectives: number;
  behind_schedule_objectives: number;
  overall_progress: number;
  average_completion_rate: number;
}

// Performance Metrics Interface
export interface PerformanceMetrics {
  objective_id: number;
  objective_title: string;
  current_value: number;
  target_value: number;
  progress_percentage: number;
  performance_color: PerformanceColor;
  trend_direction: TrendDirection;
  days_remaining: number;
  is_overdue: boolean;
}

// Trend Analysis Interface
export interface TrendAnalysis {
  objective_id: number;
  objective_title: string;
  trend_data: {
    date: string;
    value: number;
  }[];
  trend_direction: TrendDirection;
  trend_strength: number; // -1 to 1, where 1 is strong positive trend
  predicted_value?: number;
  confidence_level?: number;
}

// Alert Interface
export interface ObjectiveAlert {
  id: number;
  objective_id: number;
  objective_title: string;
  alert_type: 'overdue' | 'behind_schedule' | 'deviation' | 'milestone';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  created_at: string;
  is_read: boolean;
}

// Filter Options Interface
export interface ObjectiveFilters {
  search?: string;
  objective_type?: ObjectiveType | 'all';
  hierarchy_level?: HierarchyLevel | 'all';
  department_id?: number | 'all';
  performance_color?: PerformanceColor | 'all';
  date_range?: {
    start_date: string;
    end_date: string;
  };
}

// Pagination Interface
export interface PaginationParams {
  page: number;
  size: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// API Response Interfaces
export interface ObjectivesResponse {
  data: Objective[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

export interface ObjectiveResponse {
  data: Objective;
}

export interface ProgressResponse {
  data: ProgressEntry[];
  total: number;
}

export interface DashboardResponse {
  data: {
    kpis: DashboardKPI;
    performance_metrics: PerformanceMetrics[];
    trends: TrendAnalysis[];
    alerts: ObjectiveAlert[];
  };
}

// Form Validation Interfaces
export interface ObjectiveFormErrors {
  title?: string;
  description?: string;
  objective_type?: string;
  hierarchy_level?: string;
  target_value?: string;
  weight?: string;
  measurement_frequency?: string;
  unit_of_measure?: string;
  start_date?: string;
  target_date?: string;
}

export interface ProgressFormErrors {
  recorded_value?: string;
  recorded_date?: string;
  notes?: string;
}

// Chart Data Interfaces
export interface ChartDataPoint {
  date: string;
  value: number;
  target: number;
  baseline: number;
}

export interface ChartDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  tension?: number;
  fill?: boolean;
  borderDash?: number[];
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

// Evidence Types
export interface ObjectiveEvidence {
  id: number;
  objective_id: number;
  progress_id?: number | null;
  file_path: string;
  original_filename: string;
  content_type?: string | null;
  file_size?: number | null;
  checksum?: string | null;
  notes?: string | null;
  uploaded_by: number;
  uploaded_at: string;
  is_verified: boolean;
  verified_by?: number | null;
  verified_at?: string | null;
}
export interface ObjectiveEvidenceList {
  data: ObjectiveEvidence[];
}
export interface UploadEvidencePayload {
  file: File;
  notes?: string;
  progress_id?: number;
}

// Export all types - Remove duplicate exports
