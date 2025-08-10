// Enhanced Traceability Types and Interfaces

// Batch Management
export interface Batch {
  id: number;
  batch_number: string;
  batch_type: 'raw_milk' | 'additive' | 'culture' | 'packaging' | 'final_product' | 'intermediate';
  status: 'in_production' | 'completed' | 'quarantined' | 'released' | 'recalled' | 'disposed';
  product_name: string;
  quantity: number;
  unit: string;
  production_date: string;
  expiry_date?: string;
  lot_number?: string;
  quality_status: 'pending' | 'passed' | 'failed';
  storage_location?: string;
  storage_conditions?: string;
  barcode?: string;
  qr_code?: string;
  supplier_id?: number;
  supplier_name?: string;
  created_at: string;
  updated_at: string;
}

export interface BatchFormData {
  batch_type: string;
  product_name: string;
  quantity: string;
  unit: string;
  production_date: string;
  expiry_date: string;
  lot_number: string;
  storage_location: string;
  storage_conditions: string;
  supplier_id?: number;
}

// Barcode and QR Code System
export interface BarcodeData {
  batch_id: number;
  barcode: string;
  barcode_type: string;
  barcode_image?: string;
  generated_at: string;
}

export interface QRCodeData {
  batch_id: number;
  qr_code: string;
  qr_code_image?: string;
  data_payload: string;
  generated_at: string;
}

export interface PrintLabelData {
  batch_id: number;
  label_format: 'pdf' | 'png' | 'svg';
  label_template: string;
  label_data: Record<string, any>;
  print_url?: string;
}

// Traceability Chain
export interface TraceabilityLink {
  id: number;
  source_batch_id: number;
  target_batch_id: number;
  link_type: 'ingredient' | 'product' | 'process';
  quantity_used: number;
  process_step: string;
  process_date: string;
  created_at: string;
}

export interface TraceabilityChain {
  batch_id: number;
  incoming_links: TraceabilityLink[];
  outgoing_links: TraceabilityLink[];
  process_steps: ProcessStep[];
}

export interface ProcessStep {
  id: number;
  step_name: string;
  step_type: string;
  batch_id: number;
  quantity_used: number;
  step_date: string;
  operator_id?: number;
  operator_name?: string;
}

// Enhanced Trace Analysis
export interface TraceAnalysis {
  batch_id: number;
  trace_type: 'backward' | 'forward' | 'full';
  trace_depth: number;
  trace_date: string;
  trace_path: TraceNode[];
  summary: TraceSummary;
}

export interface TraceNode {
  batch_id: number;
  batch_number: string;
  batch_type: string;
  product_name: string;
  level: number;
  direction: 'incoming' | 'outgoing';
  quantity: number;
  process_step?: string;
  link_type?: string;
}

export interface TraceSummary {
  total_batches: number;
  total_quantity: number;
  trace_depth_reached: number;
  risk_level: 'low' | 'medium' | 'high';
  affected_suppliers: number;
  affected_customers: number;
}

// Recall Management
export interface Recall {
  id: number;
  recall_number: string;
  recall_type: 'class_i' | 'class_ii' | 'class_iii';
  status: 'draft' | 'initiated' | 'in_progress' | 'completed' | 'cancelled';
  title: string;
  description: string;
  reason: string;
  hazard_description: string;
  affected_products: string;
  affected_batches: string;
  total_quantity_affected: number;
  quantity_in_distribution: number;
  quantity_recalled: number;
  issue_discovered_date: string;
  recall_initiated_date?: string;
  regulatory_notification_required: boolean;
  regulatory_notification_sent?: boolean;
  assigned_to: number;
  assigned_to_name?: string;
  created_at: string;
  updated_at: string;
}

export interface RecallFormData {
  recall_type: string;
  title: string;
  description: string;
  reason: string;
  hazard_description: string;
  affected_products: string;
  affected_batches: string;
  total_quantity_affected: string;
  quantity_in_distribution: string;
  issue_discovered_date: string;
  regulatory_notification_required: boolean;
  assigned_to?: number;
}

// Recall Simulation
export interface RecallSimulation {
  id: number;
  simulation_number: string;
  batch_id: number;
  batch_number: string;
  recall_type: string;
  reason: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  affected_batches: number;
  affected_quantity: number;
  estimated_cost: number;
  simulation_date: string;
  results: SimulationResults;
}

export interface SimulationResults {
  affected_batches: Batch[];
  trace_analysis: TraceAnalysis;
  risk_assessment: RiskAssessment;
  recommendations: Recommendation[];
  estimated_timeline: string;
}

export interface RiskAssessment {
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  risk_factors: string[];
  mitigation_measures: string[];
}

export interface Recommendation {
  id: number;
  type: 'immediate' | 'short_term' | 'long_term';
  priority: 'high' | 'medium' | 'low';
  description: string;
  action_required: string;
  estimated_cost?: number;
  timeline?: string;
}

// Enhanced Search
export interface SearchFilters {
  query: string;
  batch_type?: string;
  status?: string;
  quality_status?: string;
  date_from?: string;
  date_to?: string;
  product_name?: string;
  supplier_id?: number;
  page?: number;
  size?: number;
}

export interface SearchResult<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
  search_time: number;
}

export interface SearchHistory {
  id: number;
  query: string;
  filters: SearchFilters;
  result_count: number;
  search_date: string;
}

// Traceability Reports
export interface TraceabilityReport {
  id: number;
  report_number: string;
  report_type: 'full_trace' | 'forward_trace' | 'backward_trace' | 'recall_analysis';
  starting_batch_id: number;
  starting_batch_number?: string;
  trace_date: string;
  trace_depth: number;
  trace_summary: string;
  report_data: any;
  created_by: number;
  created_by_name?: string;
  created_at: string;
}

export interface ReportFormData {
  starting_batch_id: string;
  report_type: string;
  trace_depth: number;
  description?: string;
}

// Corrective Actions
export interface CorrectiveAction {
  id: number;
  recall_id: number;
  action_type: string;
  description: string;
  responsible_person: string;
  target_date: string;
  completion_date?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  effectiveness_score?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CorrectiveActionFormData {
  action_type: string;
  description: string;
  responsible_person: string;
  target_date: string;
  notes: string;
}

// Root Cause Analysis
export interface RootCauseAnalysis {
  id: number;
  recall_id: number;
  analysis_date: string;
  root_causes: RootCause[];
  contributing_factors: ContributingFactor[];
  analysis_method: string;
  analyst: string;
  conclusions: string;
  recommendations: string;
  created_at: string;
}

export interface RootCause {
  id: number;
  cause_type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  evidence: string;
  corrective_action?: string;
}

export interface ContributingFactor {
  id: number;
  factor_type: string;
  description: string;
  impact_level: 'low' | 'medium' | 'high';
  mitigation_required: boolean;
}

// Preventive Measures
export interface PreventiveMeasure {
  id: number;
  recall_id: number;
  measure_type: string;
  description: string;
  implementation_date: string;
  responsible_person: string;
  status: 'planned' | 'implemented' | 'monitoring' | 'completed';
  effectiveness_score?: number;
  review_date?: string;
  notes?: string;
  created_at: string;
}

// Verification Plans
export interface VerificationPlan {
  id: number;
  recall_id: number;
  plan_name: string;
  description: string;
  verification_type: string;
  frequency: string;
  responsible_person: string;
  start_date: string;
  end_date?: string;
  status: 'draft' | 'active' | 'completed' | 'cancelled';
  verification_results: VerificationResult[];
  created_at: string;
}

export interface VerificationResult {
  id: number;
  verification_date: string;
  result: 'pass' | 'fail' | 'partial';
  findings: string;
  corrective_actions?: string;
  verified_by: string;
}

// Effectiveness Reviews
export interface EffectivenessReview {
  id: number;
  recall_id: number;
  review_date: string;
  reviewer: string;
  review_period: string;
  effectiveness_score: number;
  criteria_evaluated: EffectivenessCriteria[];
  overall_assessment: string;
  recommendations: string;
  next_review_date: string;
  created_at: string;
}

export interface EffectivenessCriteria {
  id: number;
  criteria_name: string;
  weight: number;
  score: number;
  comments: string;
}

// Dashboard Data
export interface TraceabilityDashboard {
  batch_counts: Record<string, number>;
  status_counts: Record<string, number>;
  quality_breakdown: Record<string, number>;
  recent_batches: number;
  active_recalls: number;
  recent_reports: number;
  risk_alerts: RiskAlert[];
  recent_activities: Activity[];
}

export interface RiskAlert {
  id: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affected_batches: number;
  created_at: string;
}

export interface Activity {
  id: number;
  activity_type: string;
  description: string;
  user_id: number;
  user_name: string;
  timestamp: string;
  related_id?: number;
  related_type?: string;
}

// Export and Print
export interface ExportOptions {
  format: 'csv' | 'pdf' | 'excel';
  filters?: SearchFilters;
  include_headers?: boolean;
  date_range?: {
    from: string;
    to: string;
  };
}

export interface PrintOptions {
  template: string;
  orientation: 'portrait' | 'landscape';
  paper_size: 'a4' | 'letter' | 'label';
  copies: number;
  include_barcode?: boolean;
  include_qr_code?: boolean;
}

// Bulk Operations
export interface BulkOperation {
  operation_type: 'update' | 'delete' | 'export';
  batch_ids: number[];
  operation_data?: any;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress?: number;
  results?: any;
  created_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

// Form Validation
export interface ValidationError {
  field: string;
  message: string;
}

export interface FormValidation {
  isValid: boolean;
  errors: ValidationError[];
}

// UI State
export interface LoadingState {
  isLoading: boolean;
  loadingMessage?: string;
}

export interface ErrorState {
  hasError: boolean;
  errorMessage?: string;
  errorDetails?: any;
}

// Filter and Sort
export interface SortOption {
  field: string;
  direction: 'asc' | 'desc';
}

export interface FilterOption {
  field: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
}

export interface TableState {
  page: number;
  size: number;
  sort: SortOption[];
  filters: FilterOption[];
  selectedRows: number[];
} 