// Global Type Definitions for ISO 22000 FSMS Frontend

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  errors?: string[];
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Error Types
export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
  errors?: Record<string, string[]>;
}

// User Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_name: string;
  department?: string;
  position?: string;
  phone?: string;
  employee_id?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

// Dashboard Types
export interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  pendingApprovals: number;
  systemAlerts: number;
  systemHealth: {
    database: 'healthy' | 'warning' | 'error';
    storage: string;
    performance: 'ok' | 'slow' | 'error';
    security: 'ok' | 'warning' | 'error';
  };
}

export interface DashboardActivity {
  id: number;
  action: string;
  time: string;
  type: 'info' | 'warning' | 'error' | 'success';
  user?: string;
  details?: string;
}

export interface DashboardMetrics {
  id: string;
  title: string;
  value: number | string;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
  unit?: string;
  color?: string;
}

export interface DashboardTask {
  id: number;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  due_date: string;
  assigned_to?: string;
  category: string;
}

export interface DashboardInsight {
  id: number;
  title: string;
  description: string;
  type: 'info' | 'warning' | 'error' | 'success';
  action_required?: boolean;
  link?: string;
}

// Document Types
export interface Document {
  id: number;
  title: string;
  document_number: string;
  version: string;
  category: string;
  status: 'draft' | 'under_review' | 'approved' | 'obsolete' | 'archived';
  file_path?: string;
  file_size?: number;
  mime_type?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  approved_by?: number;
  approved_at?: string;
  expiry_date?: string;
  tags?: string[];
  description?: string;
}

// HACCP Types
export interface HACCPProduct {
  id: number;
  name: string;
  code: string;
  category: string;
  description?: string;
  process_steps: HACCPProcessStep[];
  created_at: string;
  updated_at: string;
}

export interface HACCPProcessStep {
  id: number;
  step_number: number;
  name: string;
  description?: string;
  hazards: HACCPHazard[];
  ccp_points: CCPPoint[];
}

export interface HACCPHazard {
  id: number;
  name: string;
  type: 'biological' | 'chemical' | 'physical';
  severity: 'low' | 'medium' | 'high' | 'critical';
  likelihood: 'low' | 'medium' | 'high';
  control_measures: string[];
}

export interface CCPPoint {
  id: number;
  name: string;
  critical_limits: string;
  monitoring_frequency: string;
  corrective_actions: string[];
  responsible_person: string;
}

// Supplier Types (extending existing types)
export interface SupplierEvaluation {
  id: number;
  supplier_id: number;
  evaluation_date: string;
  evaluator_id: number;
  overall_score: number;
  criteria_scores: SupplierCriteriaScore[];
  recommendations: string[];
  next_evaluation_date: string;
  status: 'pending' | 'completed' | 'overdue';
}

export interface SupplierCriteriaScore {
  criteria: string;
  score: number;
  weight: number;
  comments?: string;
}

// Non-Conformance & CAPA Types
export interface NonConformance {
  id: number;
  nc_number: string;
  title: string;
  description: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'under_investigation' | 'root_cause_identified' | 'capa_assigned' | 'in_progress' | 'completed' | 'verified' | 'closed';
  reported_by: number;
  reported_at: string;
  assigned_to?: number;
  due_date?: string;
  root_cause?: string;
  corrective_actions?: string[];
  preventive_actions?: string[];
  verification_date?: string;
  closed_by?: number;
  closed_at?: string;
}

export interface CAPA {
  id: number;
  capa_number: string;
  nc_id?: number;
  title: string;
  description: string;
  type: 'corrective' | 'preventive';
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'verified' | 'closed' | 'overdue';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assigned_to?: number;
  due_date?: string;
  completed_date?: string;
  effectiveness_review_date?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

// Training Types
export interface TrainingProgram {
  id: number;
  title: string;
  description?: string;
  category: string;
  duration_hours: number;
  target_roles: string[];
  prerequisites?: string[];
  materials?: string[];
  status: 'active' | 'inactive' | 'draft';
  created_at: string;
  updated_at: string;
}

export interface TrainingRecord {
  id: number;
  user_id: number;
  program_id: number;
  completion_date: string;
  score?: number;
  status: 'enrolled' | 'in_progress' | 'completed' | 'failed';
  certificate_path?: string;
  expiry_date?: string;
  trainer?: string;
  notes?: string;
}

// Audit Types
export interface Audit {
  id: number;
  audit_number: string;
  title: string;
  type: 'internal' | 'external' | 'supplier' | 'certification';
  scope: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  scheduled_date: string;
  actual_date?: string;
  auditor_id: number;
  auditee_id?: number;
  findings: AuditFinding[];
  conclusion?: string;
  recommendations?: string[];
  created_at: string;
  updated_at: string;
}

export interface AuditFinding {
  id: number;
  description: string;
  severity: 'minor' | 'major' | 'critical';
  category: string;
  requirement?: string;
  corrective_action?: string;
  due_date?: string;
  status: 'open' | 'in_progress' | 'closed' | 'verified';
}

// Equipment Types
export interface Equipment {
  id: number;
  name: string;
  code: string;
  category: string;
  location: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  installation_date?: string;
  status: 'operational' | 'maintenance' | 'out_of_service' | 'retired';
  last_maintenance?: string;
  next_maintenance?: string;
  calibration_due?: string;
  responsible_person?: string;
  notes?: string;
}

// Complaint Types
export interface Complaint {
  id: number;
  complaint_number: string;
  title: string;
  description: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'under_investigation' | 'resolved' | 'closed';
  reported_by: number;
  reported_at: string;
  assigned_to?: number;
  resolution?: string;
  resolution_date?: string;
  customer_satisfaction?: number;
  follow_up_required?: boolean;
  follow_up_date?: string;
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'multiselect' | 'textarea' | 'date' | 'datetime' | 'checkbox' | 'radio' | 'file';
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    custom?: (value: any) => string | undefined;
  };
  placeholder?: string;
  help_text?: string;
}

// Table Types
export interface TableColumn<T = any> {
  field: keyof T;
  headerName: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  renderCell?: (value: any, row: T) => React.ReactNode;
  valueGetter?: (row: T) => any;
}

export interface TableFilters {
  search?: string;
  status?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
  assigned_to?: number;
  [key: string]: any;
}

// Notification Types
export interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  created_at: string;
  action_url?: string;
  user_id: number;
}

// File Upload Types
export interface FileUpload {
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
  url?: string;
}

// Chart Types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
}

// Utility Types
export type LoadingState = 'idle' | 'loading' | 'succeeded' | 'failed';

export interface AsyncState<T = any> {
  data: T | null;
  loading: LoadingState;
  error: string | null;
}

// API Error Handler
export const isApiError = (error: any): error is ApiError => {
  return error && typeof error === 'object' && 'message' in error;
};

// Safe API Response Handler
export const safeApiResponse = <T>(response: any): T => {
  if (response?.data) {
    return response.data;
  }
  return response;
};

// Type Guards
export const isUser = (obj: any): obj is User => {
  return obj && typeof obj === 'object' && 'id' in obj && 'username' in obj;
};

export const isDocument = (obj: any): obj is Document => {
  return obj && typeof obj === 'object' && 'id' in obj && 'title' in obj;
};

// Narrow check to basic supplier shape without needing a full type here
export const isSupplier = (obj: any): boolean => {
  return obj && typeof obj === 'object' && 'id' in obj && ('name' in obj || 'supplier_name' in obj);
};

