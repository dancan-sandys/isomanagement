// Dashboard Types for ISO 22000 FSMS Master Dashboard

export interface Department {
  id: number;
  name: string;
  code?: string;
  description?: string;
  parent_id?: number;
  manager_id?: number;
  location?: string;
  is_active: boolean;
  level: number;
  created_at: string;
  updated_at?: string;
}

export interface DepartmentCreate {
  name: string;
  code?: string;
  description?: string;
  parent_id?: number;
  manager_id?: number;
  location?: string;
  is_active?: boolean;
}

// KPI Types
export type KPICategory = 
  | 'haccp_compliance'
  | 'prp_performance'
  | 'nc_capa'
  | 'supplier_performance'
  | 'training_competency'
  | 'document_control'
  | 'audit_management'
  | 'risk_management'
  | 'operational_metrics'
  | 'compliance_score';

export interface KPIDefinition {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  category: KPICategory;
  module: string;
  calculation_formula?: string;
  data_sources?: Record<string, any>;
  calculation_method: string;
  unit?: string;
  decimal_places: number;
  target_value?: number;
  target_operator: string;
  is_active: boolean;
  requires_department_filter: boolean;
  update_frequency: number;
  created_at: string;
  updated_at?: string;
}

export interface KPIDefinitionCreate {
  name: string;
  display_name: string;
  description?: string;
  category: KPICategory;
  module: string;
  calculation_formula?: string;
  data_sources?: Record<string, any>;
  calculation_method?: string;
  unit?: string;
  decimal_places?: number;
  target_value?: number;
  target_operator?: string;
  is_active?: boolean;
  requires_department_filter?: boolean;
  update_frequency?: number;
}

export interface KPIValue {
  id: number;
  kpi_definition_id: number;
  value: number;
  period_start: string;
  period_end: string;
  department_id?: number;
  location_id?: number;
  product_category_id?: number;
  calculated_at: string;
  calculation_duration?: number;
  metadata?: Record<string, any>;
  confidence_score: number;
  data_completeness: number;
}

export interface KPIValueCreate {
  kpi_definition_id: number;
  value: number;
  period_start: string;
  period_end: string;
  department_id?: number;
  location_id?: number;
  product_category_id?: number;
  metadata?: Record<string, any>;
  confidence_score?: number;
  data_completeness?: number;
}

// Dashboard Configuration Types
export type WidgetSize = 'small' | 'medium' | 'large' | 'xlarge' | 'full';

export interface DashboardConfiguration {
  id: number;
  user_id?: number;
  role_id?: number;
  name: string;
  description?: string;
  layout_config?: Record<string, any>;
  widget_preferences?: Record<string, any>;
  refresh_interval: number;
  theme: string;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface DashboardConfigurationCreate {
  user_id?: number;
  role_id?: number;
  name?: string;
  description?: string;
  layout_config?: Record<string, any>;
  widget_preferences?: Record<string, any>;
  refresh_interval?: number;
  theme?: string;
  is_default?: boolean;
  is_active?: boolean;
}

export interface DashboardConfigurationUpdate {
  name?: string;
  description?: string;
  layout_config?: Record<string, any>;
  widget_preferences?: Record<string, any>;
  refresh_interval?: number;
  theme?: string;
  is_default?: boolean;
  is_active?: boolean;
}

// Widget Types
export interface DashboardWidget {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  component_name: string;
  category: string;
  widget_type: string;
  required_permissions?: string[];
  required_modules?: string[];
  default_size: WidgetSize;
  min_size?: { w: number; h: number };
  max_size?: { w: number; h: number };
  config_schema?: Record<string, any>;
  default_config?: Record<string, any>;
  is_active: boolean;
  version: string;
  created_at: string;
  updated_at?: string;
}

// Alert Types
export type ThresholdType = 'above' | 'below' | 'equals' | 'between';
export type AlertLevel = 'info' | 'warning' | 'critical';

export interface DashboardAlert {
  id: number;
  kpi_definition_id: number;
  name: string;
  description?: string;
  threshold_type: ThresholdType;
  threshold_value: number;
  threshold_value_max?: number;
  alert_level: AlertLevel;
  consecutive_periods: number;
  notification_config?: Record<string, any>;
  notification_recipients?: string[];
  cooldown_minutes: number;
  max_alerts_per_day: number;
  department_id?: number;
  is_active: boolean;
  last_triggered_at?: string;
  trigger_count: number;
  created_at: string;
  updated_at?: string;
}

export interface DashboardAlertCreate {
  kpi_definition_id: number;
  name: string;
  description?: string;
  threshold_type: ThresholdType;
  threshold_value: number;
  threshold_value_max?: number;
  alert_level: AlertLevel;
  consecutive_periods?: number;
  notification_config?: Record<string, any>;
  notification_recipients?: string[];
  cooldown_minutes?: number;
  max_alerts_per_day?: number;
  department_id?: number;
  is_active?: boolean;
}

// Dashboard Stats and Responses
export interface DashboardStats {
  total_kpis: number;
  active_alerts: number;
  compliance_score: number;
  last_updated: string;
  kpi_summaries: Record<string, any>;
  recent_alerts: Array<{
    id: number;
    name: string;
    level: string;
    message: string;
    created_at: string;
  }>;
  system_status: string;
  data_freshness: Record<string, string>;
}

export interface ComplianceScoreBreakdown {
  overall_score: number;
  component_scores: Record<string, number>;
  weights: Record<string, number>;
  compliance_level: string;
  last_calculated: string;
  department_scores?: Record<string, number>;
}

export interface KPITrendPoint {
  date: string;
  value: number;
  target?: number;
}

export interface KPICardData {
  kpi_id: number;
  name: string;
  display_name: string;
  current_value: number;
  target_value?: number;
  unit: string;
  trend_direction?: 'up' | 'down' | 'stable';
  trend_percentage?: number;
  status: 'good' | 'warning' | 'critical';
  last_updated: string;
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    [key: string]: any;
  }>;
  options?: Record<string, any>;
}

// Export Types
export interface ExportRequest {
  format: 'excel' | 'pdf' | 'csv';
  data_type: 'dashboard' | 'kpis' | 'alerts' | 'reports';
  filters?: Record<string, any>;
  date_range?: {
    start: string;
    end: string;
  };
  include_charts?: boolean;
}

export interface ExportResponse {
  file_url: string;
  file_name: string;
  file_size: number;
  expires_at: string;
  download_count: number;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string;
  data: Record<string, any>;
  timestamp: string;
}

export interface KPIUpdateMessage extends WebSocketMessage {
  type: 'kpi_update';
  data: {
    kpi_id: number;
    new_value: number;
    department_id?: number;
  };
}

export interface AlertMessage extends WebSocketMessage {
  type: 'alert';
  data: {
    alert_id: number;
    kpi_id: number;
    level: AlertLevel;
    message: string;
  };
}

export interface SystemStatusMessage extends WebSocketMessage {
  type: 'system_status';
  data: {
    status: 'online' | 'maintenance' | 'error';
    message?: string;
  };
}

// Layout Types for react-grid-layout
export interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  maxW?: number;
  minH?: number;
  maxH?: number;
  static?: boolean;
  isDraggable?: boolean;
  isResizable?: boolean;
}

export interface Layouts {
  lg: LayoutItem[];
  md: LayoutItem[];
  sm: LayoutItem[];
  xs: LayoutItem[];
  xxs: LayoutItem[];
}

// Widget Configuration Types
export interface WidgetConfig {
  id: string;
  type: string;
  component: string;
  title?: string;
  config: Record<string, any>;
  layout: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

export interface KPICardConfig {
  kpi_id: number;
  show_trend?: boolean;
  show_target?: boolean;
  show_details?: boolean;
  title?: string;
  refresh_interval?: number;
}

export interface LineChartConfig {
  kpi_ids: number[];
  period_days?: number;
  show_target_line?: boolean;
  title?: string;
  chart_type?: 'line' | 'area';
}

export interface ComplianceGaugeConfig {
  compliance_type: 'overall' | 'haccp' | 'prp';
  department_filter?: boolean;
  title?: string;
  show_breakdown?: boolean;
}

export interface AlertFeedConfig {
  max_items?: number;
  alert_levels?: AlertLevel[];
  auto_refresh?: boolean;
  title?: string;
  show_timestamps?: boolean;
}

// Dashboard View Types
export type DashboardViewType = 'executive' | 'management' | 'operational' | 'specialist';

export interface DashboardViewConfig {
  view_type: DashboardViewType;
  columns: number;
  widgets: WidgetConfig[];
  layout: LayoutItem[];
}

// User Permission Types
export interface DashboardPermissions {
  can_view: boolean;
  can_edit: boolean;
  can_create: boolean;
  can_delete: boolean;
  can_export: boolean;
  accessible_modules: string[];
  accessible_kpis: number[];
  accessible_departments: number[];
}

// Error Types
export interface DashboardError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// Audit Log Types
export interface DashboardAuditLog {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id?: number;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  details?: Record<string, any>;
  duration_ms?: number;
  success: boolean;
  error_message?: string;
  created_at: string;
}

// Scheduled Report Types
export interface ScheduledReport {
  id: number;
  name: string;
  description?: string;
  report_type: string;
  report_config: Record<string, any>;
  schedule_expression: string;
  timezone: string;
  output_format: string;
  recipients: string[];
  is_active: boolean;
  last_run_at?: string;
  next_run_at?: string;
  last_run_status?: string;
  last_run_error?: string;
  execution_count: number;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface ScheduledReportCreate {
  name: string;
  description?: string;
  report_type: string;
  report_config: Record<string, any>;
  schedule_expression: string;
  timezone?: string;
  output_format?: string;
  recipients: string[];
  is_active?: boolean;
  created_by: number;
}

// Theme Types
export interface DashboardTheme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
    };
  };
  typography: {
    fontFamily: string;
    fontSize: {
      small: string;
      medium: string;
      large: string;
    };
  };
  spacing: {
    small: number;
    medium: number;
    large: number;
  };
}