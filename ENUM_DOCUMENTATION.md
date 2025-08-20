# ISO 22000 FSMS Platform - Enum Documentation

**Date:** August 19, 2025  
**Status:** ✅ COMPLETE ENUM INVENTORY

## 🔧 **FIXED ENUM ISSUES**

### **NonConformanceStatus** ✅ FIXED
- **Issue:** Database had `'CLOSED'` but enum expected `'open'`
- **Fix:** Updated database values to match enum definition
- **Result:** All non-conformance statuses now use lowercase values

### **NonConformanceSource** ✅ FIXED  
- **Issue:** Database had `'OTHER'` but enum expected `'other'`
- **Fix:** Updated database values to match enum definition
- **Result:** All non-conformance sources now use lowercase values

## 📋 **COMPLETE ENUM LIST**

### **User Management**
- **UserRole:** ADMIN, QA_MANAGER, QA_SPECIALIST, PRODUCTION_MANAGER, PRODUCTION_OPERATOR, MAINTENANCE, LAB_TECHNICIAN, SUPPLIER, AUDITOR, VIEWER
- **UserStatus:** ACTIVE, INACTIVE, SUSPENDED, PENDING_APPROVAL

### **HACCP Module**
- **HazardType:** biological, chemical, physical, allergen
- **RiskLevel:** low, medium, high, critical
- **CCPStatus:** active, inactive, suspended, under_review
- **HACCPPlanStatus:** draft, under_review, approved, implemented, under_revision, obsolete

### **Traceability**
- **BatchType:** raw_milk, additive, culture, packaging, final_product, intermediate
- **BatchStatus:** in_production, completed, quarantined, released, recalled, disposed
- **RecallType:** class_i, class_ii, class_iii
- **RecallStatus:** draft, initiated, in_progress, completed, cancelled

### **Audit Management**
- **AuditType:** internal, external, supplier, certification, surveillance, follow_up
- **AuditStatus:** planned, in_progress, completed, cancelled, rescheduled
- **FindingType:** nonconformity, observation, opportunity_for_improvement, compliance
- **FindingSeverity:** minor, major, critical
- **FindingStatus:** open, in_progress, completed, verified, closed

### **Equipment**
- **MaintenanceType:** preventive, corrective, predictive, emergency
- **WorkOrderStatus:** pending, assigned, in_progress, completed, cancelled, on_hold
- **WorkOrderPriority:** low, medium, high, critical

### **Supplier Management**
- **SupplierStatus:** active, inactive, suspended, pending_approval, blacklisted
- **SupplierCategory:** raw_milk, equipment, chemicals, services
- **EvaluationStatus:** pending, in_progress, completed, overdue
- **InspectionStatus:** pending, passed, failed, quarantined

### **Document Management**
- **DocumentType:** policy, procedure, work_instruction, form, record, manual, specification, plan, checklist
- **DocumentStatus:** draft, under_review, approved, obsolete, archived
- **DocumentCategory:** haccp, prp, general, production, hr, finance

### **PRP Module**
- **PRPCategory:** construction_and_layout, layout_of_premises, supplies_of_air_water_energy, supporting_services, suitability_cleaning_maintenance, management_of_purchased_materials, prevention_of_cross_contamination, cleaning_sanitation, pest_control, personnel_hygiene_facilities, product_release, staff_hygiene, waste_management, equipment_calibration, maintenance, personnel_training, supplier_control, water_quality, air_quality
- **PRPFrequency:** daily, weekly, monthly, quarterly, semi_annually, annually, as_needed
- **PRPStatus:** active, inactive, suspended
- **ChecklistStatus:** pending, in_progress, completed, overdue, failed

### **Non-Conformance**
- **NonConformanceSource:** prp, audit, complaint, production_deviation, supplier, haccp, document, inspection, other
- **NonConformanceStatus:** open, under_investigation, root_cause_identified, capa_assigned, in_progress, completed, verified, closed
- **CAPAStatus:** pending, assigned, in_progress, completed, verified, closed, overdue
- **RootCauseMethod:** five_whys, ishikawa, fishbone, fault_tree, other

### **Risk Management**
- **RiskItemType:** process, product, equipment, supplier, personnel, environment, regulatory, other
- **RiskCategory:** food_safety, quality, operational, financial, regulatory, reputational, other
- **RiskStatus:** open, assessed, treated, monitored, closed, escalated
- **RiskSeverity:** very_low, low, medium, high, very_high, critical
- **RiskLikelihood:** very_unlikely, unlikely, possible, likely, very_likely, certain
- **RiskClassification:** food_safety, business, customer
- **RiskDetectability:** very_high, high, medium, low, very_low

### **Management Review**
- **ManagementReviewStatus:** planned, in_progress, completed, cancelled, rescheduled
- **ManagementReviewType:** scheduled, special, emergency, annual
- **ReviewInputType:** audit_results, customer_feedback, process_performance, product_conformity, corrective_actions, preventive_actions, follow_up_actions, changes_external, changes_internal, improvement_suggestions, resource_adequacy, risk_assessment, compliance_status, other
- **ReviewOutputType:** decision, action, resource_allocation, policy_change, objective_change, process_change, training_need, infrastructure_change, other
- **ActionPriority:** low, medium, high, critical
- **ActionStatus:** assigned, in_progress, completed, verified, closed, overdue, cancelled

### **Notifications**
- **NotificationType:** info, success, warning, error, alert
- **NotificationCategory:** system, audit, haccp, prp, supplier, equipment, document, training, compliance, other
- **NotificationPriority:** low, medium, high, critical

### **Permissions**
- **PermissionType:** create, read, update, delete, manage_program, approve, verify, assign, escalate
- **Module:** users, haccp, prp, audit, supplier, equipment, document, training, compliance, dashboard, settings

### **Dashboard**
- **KPICategory:** food_safety, quality, compliance, operational, financial, customer
- **ThresholdType:** minimum, maximum, target, range
- **AlertLevel:** info, warning, error, critical
- **WidgetSize:** small, medium, large, full

### **Settings**
- **SettingCategory:** general, security, notification, integration, backup, compliance
- **SettingType:** string, integer, float, boolean, json, password, email, url

### **Complaints**
- **ComplaintStatus:** open, under_investigation, resolved, closed, escalated
- **ComplaintClassification:** food_safety, quality, packaging, delivery, customer_service, other
- **CommunicationChannel:** email, phone, website, social_media, in_person, letter, other

### **Training**
- **TrainingAction:** assigned, started, completed, failed, cancelled, rescheduled

### **Calibration**
- **CalibrationStatus:** pending, in_progress, completed, failed, overdue

### **HACCP Services**
- **AlertSeverity:** low, medium, high, critical
- **HACCPActionType:** corrective, preventive, verification, validation

## 📊 **STATISTICS**

- **Total Enum Categories:** 50+
- **Total Enum Values:** 300+
- **Modules Covered:** 15+
- **Database Consistency:** ✅ VERIFIED
- **API Compatibility:** ✅ VERIFIED
- **Frontend Integration:** ✅ VERIFIED

## ✅ **VALIDATION STATUS**

All enum values are now consistent across:
- ✅ Database values
- ✅ Backend enum definitions  
- ✅ API responses
- ✅ Frontend components

**Last Updated:** August 19, 2025  
**Status:** ✅ COMPLETE AND VERIFIED


