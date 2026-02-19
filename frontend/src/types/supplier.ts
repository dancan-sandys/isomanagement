// Supplier Management Types

export interface Supplier {
  id: number;
  supplier_code: string;
  name: string;
  status: 'active' | 'inactive' | 'suspended' | 'pending_approval' | 'blacklisted';
  category: string;
  contact_person: string;
  email: string;
  phone: string;
  website?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state?: string;
  postal_code?: string;
  country: string;
  business_registration_number?: string;
  tax_identification_number?: string;
  company_type?: string;
  year_established?: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  overall_score: number;
  last_evaluation_date?: string;
  next_evaluation_date?: string;
  materials_count: number;
  recent_evaluation_score?: number;
  recent_delivery_date?: string;
  notes?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  // Enhanced fields
  certifications?: SupplierCertification[];
  compliance_status?: 'compliant' | 'non_compliant' | 'under_review';
  hygiene_rating?: number;
  last_hygiene_audit?: string;
  next_hygiene_audit?: string;
}

export interface SupplierCertification {
  id: number;
  certification_type: 'iso_22000' | 'iso_9001' | 'haccp' | 'gmp' | 'other';
  certification_number: string;
  issued_date: string;
  expiry_date: string;
  issuing_body: string;
  status: 'valid' | 'expired' | 'pending_renewal';
  document_path?: string;
}

export interface SupplierCreate {
  supplier_code: string;
  name: string;
  category: string;
  contact_person: string;
  email: string;
  phone: string;
  website?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state?: string;
  postal_code?: string;
  country: string;
  business_registration_number?: string;
  tax_identification_number?: string;
  company_type?: string;
  year_established?: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  notes?: string;
  // Enhanced fields
  certifications?: SupplierCertificationCreate[];
  compliance_status?: 'compliant' | 'non_compliant' | 'under_review';
  hygiene_rating?: number;
}

export interface SupplierCertificationCreate {
  certification_type: 'iso_22000' | 'iso_9001' | 'haccp' | 'gmp' | 'other';
  certification_number: string;
  issued_date: string;
  expiry_date: string;
  issuing_body: string;
  document_file?: File;
}

export interface SupplierUpdate {
  name?: string;
  status?: 'active' | 'inactive' | 'suspended' | 'pending_approval' | 'blacklisted';
  category?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  website?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  business_registration_number?: string;
  tax_identification_number?: string;
  company_type?: string;
  year_established?: number;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  notes?: string;
  // Enhanced fields
  compliance_status?: 'compliant' | 'non_compliant' | 'under_review';
  hygiene_rating?: number;
}

// Material Management Types

export interface Material {
  id: number;
  material_code: string;
  name: string;
  category: string;
  description?: string;
  supplier_id: number;
  supplier_name: string;
  supplier_material_code?: string;
  allergens: string[];
  storage_conditions: string;
  shelf_life_days?: number;
  handling_instructions?: string;
  specifications: MaterialSpecification[];
  approval_status: 'pending' | 'approved' | 'rejected' | 'under_review';
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  // Enhanced fields
  hygiene_requirements?: string[];
  microbiological_limits?: MaterialMicrobiologicalLimit[];
  physical_parameters?: MaterialPhysicalParameter[];
  chemical_parameters?: MaterialChemicalParameter[];
  packaging_requirements?: string[];
  transportation_conditions?: string;
  temperature_requirements?: {
    min_temp?: number;
    max_temp?: number;
    unit: 'celsius' | 'fahrenheit';
  };
}

export interface MaterialSpecification {
  id: number;
  parameter_name: string;
  parameter_value: string;
  unit?: string;
  min_value?: number;
  max_value?: number;
  target_value?: number;
  test_method?: string;
  frequency?: string;
}

export interface MaterialMicrobiologicalLimit {
  id: number;
  microorganism: string;
  limit_value: string;
  unit: string;
  test_method: string;
  frequency: string;
}

export interface MaterialPhysicalParameter {
  id: number;
  parameter: string;
  value: string;
  unit?: string;
  acceptable_range?: string;
  test_method: string;
}

export interface MaterialChemicalParameter {
  id: number;
  parameter: string;
  value: string;
  unit?: string;
  acceptable_range?: string;
  test_method: string;
}

export interface MaterialCreate {
  material_code: string;
  name: string;
  category: string;
  description?: string;
  supplier_id: number;
  supplier_material_code?: string;
  allergens: string[];
  storage_conditions: string;
  shelf_life_days?: number;
  handling_instructions?: string;
  specifications: MaterialSpecificationCreate[];
  // Enhanced fields
  hygiene_requirements?: string[];
  microbiological_limits?: MaterialMicrobiologicalLimitCreate[];
  physical_parameters?: MaterialPhysicalParameterCreate[];
  chemical_parameters?: MaterialChemicalParameterCreate[];
  packaging_requirements?: string[];
  transportation_conditions?: string;
  temperature_requirements?: {
    min_temp?: number;
    max_temp?: number;
    unit: 'celsius' | 'fahrenheit';
  };
}

export interface MaterialSpecificationCreate {
  parameter_name: string;
  parameter_value: string;
  unit?: string;
  min_value?: number;
  max_value?: number;
  target_value?: number;
  test_method?: string;
  frequency?: string;
}

export interface MaterialMicrobiologicalLimitCreate {
  microorganism: string;
  limit_value: string;
  unit: string;
  test_method: string;
  frequency: string;
}

export interface MaterialPhysicalParameterCreate {
  parameter: string;
  value: string;
  unit?: string;
  acceptable_range?: string;
  test_method: string;
}

export interface MaterialChemicalParameterCreate {
  parameter: string;
  value: string;
  unit?: string;
  acceptable_range?: string;
  test_method: string;
}

export interface MaterialUpdate {
  name?: string;
  category?: string;
  description?: string;
  supplier_material_code?: string;
  allergens?: string[];
  storage_conditions?: string;
  shelf_life_days?: number;
  handling_instructions?: string;
  approval_status?: 'pending' | 'approved' | 'rejected' | 'under_review';
  rejection_reason?: string;
  // Enhanced fields
  hygiene_requirements?: string[];
  microbiological_limits?: MaterialMicrobiologicalLimitCreate[];
  physical_parameters?: MaterialPhysicalParameterCreate[];
  chemical_parameters?: MaterialChemicalParameterCreate[];
  packaging_requirements?: string[];
  transportation_conditions?: string;
  temperature_requirements?: {
    min_temp?: number;
    max_temp?: number;
    unit: 'celsius' | 'fahrenheit';
  };
}

// Enhanced Evaluation System Types

export interface Evaluation {
  id: number;
  supplier_id: number;
  supplier_name: string;
  evaluation_period: string;
  evaluation_date: string;
  evaluator: string;
  quality_score: number;
  delivery_score: number;
  price_score: number;
  communication_score: number;
  technical_support_score: number;
  hygiene_score: number; // NEW: Hygiene evaluation score
  overall_score: number;
  quality_comments?: string;
  delivery_comments?: string;
  price_comments?: string;
  communication_comments?: string;
  technical_support_comments?: string;
  hygiene_comments?: string; // NEW: Hygiene evaluation comments
  issues_identified?: string;
  improvement_actions?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  status: 'completed' | 'in_progress' | 'scheduled' | 'overdue';
  created_by: string;
  created_at: string;
  updated_at: string;
  // Enhanced fields
  hygiene_audit_details?: HygieneAuditDetail[];
  compliance_score?: number;
  risk_assessment_score?: number;
  corrective_actions?: string[];
  verification_required?: boolean;
  verification_date?: string;
}

export interface HygieneAuditDetail {
  id: number;
  audit_area: string;
  score: number;
  findings: string;
  corrective_actions?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
}

export interface EvaluationCreate {
  supplier_id: number;
  evaluation_period: string;
  evaluation_date: string;
  quality_score: number;
  delivery_score: number;
  price_score: number;
  communication_score: number;
  technical_support_score: number;
  hygiene_score: number; // NEW: Hygiene evaluation score
  quality_comments?: string;
  delivery_comments?: string;
  price_comments?: string;
  communication_comments?: string;
  technical_support_comments?: string;
  hygiene_comments?: string; // NEW: Hygiene evaluation comments
  issues_identified?: string;
  improvement_actions?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  // Enhanced fields
  hygiene_audit_details?: HygieneAuditDetailCreate[];
  compliance_score?: number;
  risk_assessment_score?: number;
  corrective_actions?: string[];
  verification_required?: boolean;
  verification_date?: string;
}

export interface HygieneAuditDetailCreate {
  audit_area: string;
  score: number;
  findings: string;
  corrective_actions?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
}

export interface EvaluationUpdate {
  evaluation_period?: string;
  evaluation_date?: string;
  quality_score?: number;
  delivery_score?: number;
  price_score?: number;
  communication_score?: number;
  technical_support_score?: number;
  hygiene_score?: number; // NEW: Hygiene evaluation score
  quality_comments?: string;
  delivery_comments?: string;
  price_comments?: string;
  communication_comments?: string;
  technical_support_comments?: string;
  hygiene_comments?: string; // NEW: Hygiene evaluation comments
  issues_identified?: string;
  improvement_actions?: string;
  follow_up_required?: boolean;
  follow_up_date?: string;
  status?: 'completed' | 'in_progress' | 'scheduled' | 'overdue';
  // Enhanced fields
  hygiene_audit_details?: HygieneAuditDetailCreate[];
  compliance_score?: number;
  risk_assessment_score?: number;
  corrective_actions?: string[];
  verification_required?: boolean;
  verification_date?: string;
}

// Enhanced Delivery Management Types

export interface Delivery {
  id: number;
  delivery_number: string;
  supplier_id: number;
  supplier_name: string;
  material_id: number;
  material_name: string;
  delivery_date: string;
  expected_delivery_date: string;
  quantity: number;
  unit: string;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  storage_location: string;
  storage_conditions: string;
  inspection_status: 'pending' | 'passed' | 'failed' | 'under_review';
  inspection_date?: string;
  inspector?: string;
  inspection_comments?: string;
  coa_uploaded: boolean;
  coa_file_path?: string;
  quality_alerts: QualityAlert[];
  created_by: string;
  created_at: string;
  updated_at: string;
  // Enhanced fields
  inspection_checklist?: InspectionChecklist;
  compliance_status?: 'compliant' | 'non_compliant' | 'under_review';
  temperature_upon_arrival?: number;
  temperature_unit?: 'celsius' | 'fahrenheit';
  packaging_condition?: 'excellent' | 'good' | 'fair' | 'poor';
  visual_inspection_passed?: boolean;
  microbiological_testing_required?: boolean;
  microbiological_testing_completed?: boolean;
  microbiological_testing_results?: string;
  corrective_actions_required?: boolean;
  corrective_actions_taken?: string[];
  non_compliance_reasons?: string[];
}

export interface QualityAlert {
  id: number;
  delivery_id: number;
  alert_type: 'temperature' | 'damage' | 'expiry' | 'contamination' | 'documentation' | 'hygiene' | 'packaging' | 'microbiological' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  action_taken?: string;
  resolved: boolean;
  resolved_by?: string;
  resolved_at?: string;
  created_at: string;
  // Enhanced fields
  compliance_impact?: 'minor' | 'moderate' | 'major' | 'critical';
  corrective_action_required?: boolean;
  corrective_action_deadline?: string;
  verification_required?: boolean;
  verification_completed?: boolean;
}

export interface DeliveryCreate {
  supplier_id: number;
  material_id: number;
  delivery_date: string;
  expected_delivery_date: string;
  quantity: number;
  unit: string;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  storage_location: string;
  storage_conditions: string;
  // Enhanced fields
  temperature_upon_arrival?: number;
  temperature_unit?: 'celsius' | 'fahrenheit';
  packaging_condition?: 'excellent' | 'good' | 'fair' | 'poor';
  visual_inspection_passed?: boolean;
  microbiological_testing_required?: boolean;
}

export interface DeliveryUpdate {
  delivery_date?: string;
  expected_delivery_date?: string;
  quantity?: number;
  unit?: string;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  storage_location?: string;
  storage_conditions?: string;
  inspection_status?: 'pending' | 'passed' | 'failed' | 'under_review';
  inspection_comments?: string;
  // Enhanced fields
  temperature_upon_arrival?: number;
  temperature_unit?: 'celsius' | 'fahrenheit';
  packaging_condition?: 'excellent' | 'good' | 'fair' | 'poor';
  visual_inspection_passed?: boolean;
  microbiological_testing_required?: boolean;
  microbiological_testing_completed?: boolean;
  microbiological_testing_results?: string;
  compliance_status?: 'compliant' | 'non_compliant' | 'under_review';
}

// NEW: Inspection Checklist Types

export interface InspectionChecklist {
  id: number;
  delivery_id: number;
  checklist_type: 'receiving' | 'storage' | 'processing' | 'packaging' | 'shipping';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  inspector: string;
  inspection_date: string;
  completion_date?: string;
  overall_score?: number;
  items: ChecklistItem[];
  comments?: string;
  created_at: string;
  updated_at: string;
}

export interface ChecklistItem {
  id: number;
  checklist_id: number;
  item_number: number;
  category: string;
  description: string;
  requirement: string;
  acceptable_criteria: string;
  status: 'pending' | 'passed' | 'failed' | 'not_applicable';
  score?: number;
  max_score: number;
  inspector_comments?: string;
  corrective_action_required?: boolean;
  corrective_action?: string;
  follow_up_required?: boolean;
  follow_up_date?: string;
  verification_required?: boolean;
  verification_completed?: boolean;
  verification_date?: string;
  verification_by?: string;
  compliance_impact?: 'minor' | 'moderate' | 'major' | 'critical';
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
}

export interface InspectionChecklistCreate {
  delivery_id: number;
  checklist_type: 'receiving' | 'storage' | 'processing' | 'packaging' | 'shipping';
  inspector: string;
  items: ChecklistItemCreate[];
  comments?: string;
}

export interface ChecklistItemCreate {
  item_number: number;
  category: string;
  description: string;
  requirement: string;
  acceptable_criteria: string;
  max_score: number;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
}

export interface ChecklistItemUpdate {
  status?: 'pending' | 'passed' | 'failed' | 'not_applicable';
  score?: number;
  inspector_comments?: string;
  corrective_action_required?: boolean;
  corrective_action?: string;
  follow_up_required?: boolean;
  follow_up_date?: string;
  verification_required?: boolean;
  verification_completed?: boolean;
  verification_date?: string;
  verification_by?: string;
}

// Enhanced Document Management Types

export interface SupplierDocument {
  id: number;
  supplier_id: number;
  supplier_name: string;
  document_type: 'certificate' | 'license' | 'insurance' | 'contract' | 'specification' | 'iso_certification' | 'haccp_certification' | 'gmp_certification' | 'other';
  document_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  expiry_date?: string;
  verification_status: 'pending' | 'verified' | 'rejected' | 'expired';
  verified_by?: string;
  verified_at?: string;
  verification_comments?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  // Enhanced fields
  compliance_impact?: 'minor' | 'moderate' | 'major' | 'critical';
  renewal_required?: boolean;
  renewal_deadline?: string;
  automatic_renewal?: boolean;
  notification_sent?: boolean;
  notification_date?: string;
}

export interface SupplierDocumentCreate {
  supplier_id: number;
  document_type: 'certificate' | 'license' | 'insurance' | 'contract' | 'specification' | 'iso_certification' | 'haccp_certification' | 'gmp_certification' | 'other';
  document_name: string;
  expiry_date?: string;
  // Enhanced fields
  compliance_impact?: 'minor' | 'moderate' | 'major' | 'critical';
  renewal_required?: boolean;
  renewal_deadline?: string;
  automatic_renewal?: boolean;
}

export interface SupplierDocumentUpdate {
  document_name?: string;
  expiry_date?: string;
  verification_status?: 'pending' | 'verified' | 'rejected' | 'expired';
  verification_comments?: string;
  // Enhanced fields
  compliance_impact?: 'minor' | 'moderate' | 'major' | 'critical';
  renewal_required?: boolean;
  renewal_deadline?: string;
  automatic_renewal?: boolean;
}

// Enhanced Dashboard and Analytics Types

export interface SupplierDashboard {
  total_suppliers: number;
  active_suppliers: number;
  inactive_suppliers: number;
  suspended_suppliers: number;
  pending_approval_suppliers: number;
  blacklisted_suppliers: number;
  overdue_evaluations: number;
  upcoming_evaluations: number;
  suppliers_by_category: CategoryDistribution[];
  suppliers_by_risk: RiskDistribution[];
  recent_evaluations: Evaluation[];
  recent_deliveries: Delivery[];
  performance_trends: PerformanceTrend[];
  alerts: Alert[];
  // Enhanced fields
  non_compliant_suppliers: number;
  hygiene_audits_due: number;
  expired_certificates: number;
  non_compliant_deliveries: number;
  compliance_score: number;
  average_hygiene_score: number;
  suppliers_by_compliance: ComplianceDistribution[];
  hygiene_audit_trends: HygieneAuditTrend[];
  non_compliant_delivery_alerts: NonCompliantDeliveryAlert[];
}

export interface CategoryDistribution {
  category: string;
  count: number;
  percentage: number;
}

export interface RiskDistribution {
  risk_level: string;
  count: number;
  percentage: number;
}

export interface ComplianceDistribution {
  compliance_status: string;
  count: number;
  percentage: number;
}

export interface PerformanceTrend {
  date: string;
  average_score: number;
  evaluation_count: number;
  // Enhanced fields
  hygiene_score?: number;
  compliance_score?: number;
  non_compliant_count?: number;
}

export interface HygieneAuditTrend {
  date: string;
  average_hygiene_score: number;
  audit_count: number;
  non_compliant_count: number;
}

export interface Alert {
  id: number;
  type: 'expired_certificate' | 'overdue_evaluation' | 'quality_alert' | 'expired_material' | 'hygiene_audit_due' | 'non_compliant_delivery' | 'microbiological_alert' | 'temperature_alert' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  supplier_id?: number;
  supplier_name?: string;
  material_id?: number;
  material_name?: string;
  delivery_id?: number;
  created_at: string;
  resolved: boolean;
  resolved_at?: string;
  // Enhanced fields
  compliance_impact?: 'minor' | 'moderate' | 'major' | 'critical';
  corrective_action_required?: boolean;
  corrective_action_deadline?: string;
  verification_required?: boolean;
  verification_completed?: boolean;
  notification_sent?: boolean;
  notification_date?: string;
}

// NEW: Non-Compliant Delivery Alert Types

export interface NonCompliantDeliveryAlert {
  id: number;
  delivery_id: number;
  delivery_number: string;
  supplier_id: number;
  supplier_name: string;
  material_id: number;
  material_name: string;
  alert_type: 'temperature' | 'packaging' | 'microbiological' | 'hygiene' | 'documentation' | 'expiry' | 'contamination' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  compliance_impact: 'minor' | 'moderate' | 'major' | 'critical';
  non_compliance_reasons: string[];
  corrective_actions_required: string[];
  corrective_actions_taken?: string[];
  verification_required: boolean;
  verification_completed: boolean;
  verification_date?: string;
  verification_by?: string;
  created_at: string;
  resolved: boolean;
  resolved_at?: string;
  resolved_by?: string;
  notification_sent: boolean;
  notification_date?: string;
}

// Bulk Operations Types

export interface BulkOperation {
  operation_type: 'status_update' | 'evaluation_schedule' | 'document_reminder' | 'risk_assessment' | 'hygiene_audit_schedule' | 'compliance_check';
  supplier_ids: number[];
  parameters: Record<string, any>;
}

export interface BulkStatusUpdate {
  supplier_ids: number[];
  new_status: 'active' | 'inactive' | 'suspended' | 'pending_approval' | 'blacklisted';
  reason?: string;
}

// Enhanced Filter and Search Types

export interface SupplierFilters {
  search?: string;
  category?: string;
  status?: string;
  risk_level?: string;
  evaluation_status?: string;
  date_from?: string;
  date_to?: string;
  score_min?: number;
  score_max?: number;
  // Enhanced fields
  compliance_status?: string;
  hygiene_score_min?: number;
  hygiene_score_max?: number;
  certification_type?: string;
  certification_status?: string;
  audit_due?: boolean;
}

export interface MaterialFilters {
  search?: string;
  category?: string;
  supplier_id?: number;
  approval_status?: string;
  allergens?: string[];
  // Enhanced fields
  hygiene_requirements?: string[];
  microbiological_testing_required?: boolean;
  temperature_controlled?: boolean;
}

export interface EvaluationFilters {
  supplier_id?: number;
  status?: string;
  date_from?: string;
  date_to?: string;
  score_min?: number;
  score_max?: number;
  follow_up_required?: boolean;
  // Enhanced fields
  hygiene_score_min?: number;
  hygiene_score_max?: number;
  compliance_score_min?: number;
  compliance_score_max?: number;
  verification_required?: boolean;
}

export interface DeliveryFilters {
  supplier_id?: number;
  material_id?: number;
  inspection_status?: string;
  date_from?: string;
  date_to?: string;
  has_alerts?: boolean;
  // Enhanced fields
  compliance_status?: string;
  temperature_controlled?: boolean;
  microbiological_testing_required?: boolean;
  non_compliant?: boolean;
}

// API Response Types

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

// File Upload Types

export interface FileUploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

export interface UploadResponse {
  file_path: string;
  file_size: number;
  mime_type: string;
  original_name: string;
} 