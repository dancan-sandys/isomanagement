export enum ActionStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  ON_HOLD = "on_hold",
  OVERDUE = "overdue"
}

export enum ActionPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
  URGENT = "urgent"
}

export enum ActionSource {
  INTERESTED_PARTY = "interested_party",
  SWOT_ANALYSIS = "swot_analysis",
  PESTEL_ANALYSIS = "pestel_analysis",
  RISK_ASSESSMENT = "risk_assessment",
  AUDIT_FINDING = "audit_finding",
  NON_CONFORMANCE = "non_conformance",
  MANAGEMENT_REVIEW = "management_review",
  COMPLAINT = "complaint",
  REGULATORY = "regulatory",
  STRATEGIC_PLANNING = "strategic_planning",
  CONTINUOUS_IMPROVEMENT = "continuous_improvement"
}

export interface ActionLogBase {
  title: string;
  description: string;
  action_source: ActionSource;
  source_id?: number;
  risk_id?: number;
  priority: ActionPriority;
  assigned_to?: number;
  department_id?: number;
  due_date?: string;
  estimated_hours?: number;
  tags?: Record<string, any>;
  notes?: string;
}

export interface ActionLogCreate extends ActionLogBase {
  assigned_by: number;
}

export interface ActionLogUpdate {
  title?: string;
  description?: string;
  status?: ActionStatus;
  priority?: ActionPriority;
  assigned_to?: number;
  department_id?: number;
  due_date?: string;
  estimated_hours?: number;
  progress_percent?: number;
  actual_hours?: number;
  tags?: Record<string, any>;
  notes?: string;
}

export interface ActionLog extends ActionLogBase {
  id: number;
  status: ActionStatus;
  assigned_by: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress_percent: number;
  actual_hours?: number;
  attachments?: Record<string, any>;
  assigned_user_name?: string;
  created_by_name?: string;
  department_name?: string;
}

export interface ActionsAnalytics {
  total_actions: number;
  pending_actions: number;
  in_progress_actions: number;
  completed_actions: number;
  overdue_actions: number;
  critical_actions: number;
  high_priority_actions: number;
  average_completion_time?: number;
  completion_rate: number;
  source_breakdown: Record<string, number>;
  priority_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
  department_breakdown: Record<string, number>;
}

export interface ActionsDashboard {
  recent_actions: ActionLog[];
  critical_actions: ActionLog[];
  analytics: ActionsAnalytics;
}

export interface ActionLogFilters {
  status?: ActionStatus;
  priority?: ActionPriority;
  source?: ActionSource;
  assigned_to?: number;
  department_id?: number;
  risk_id?: number;
  page?: number;
  size?: number;
  limit?: number;
  offset?: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}