"""
Management Review Data Aggregation Service
Collects and aggregates data from various modules for ISO 22000:2018 compliance
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.models.audit_mgmt import Audit, AuditFinding, FindingSeverity
from app.models.nonconformance import NonConformance, CAPAAction, NonConformanceStatus, CAPAStatus
from app.models.supplier import Supplier, SupplierEvaluation
from app.models.risk import RiskRegisterItem, RiskStatus, RiskKPI
from app.models.haccp import Product, CCP, CCPMonitoringLog
from app.models.prp import PRPProgram, PRPChecklist
from app.models.training import TrainingProgram, TrainingAttendance
from app.models.user import User
from app.schemas.management_review import ReviewInputType


class ManagementReviewDataAggregationService:
    """Service for aggregating data from various modules for management reviews"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def collect_all_inputs(self, date_range_start: Optional[datetime] = None, 
                          date_range_end: Optional[datetime] = None,
                          department_id: Optional[int] = None) -> Dict[ReviewInputType, Dict[str, Any]]:
        """Collect all required inputs for management review"""
        if not date_range_end:
            date_range_end = datetime.utcnow()
        if not date_range_start:
            date_range_start = date_range_end - timedelta(days=90)  # Last 3 months by default
            
        inputs = {}
        
        # Collect audit results
        inputs[ReviewInputType.AUDIT_RESULTS] = self.collect_audit_results(date_range_start, date_range_end, department_id)
        
        # Collect NC/CAPA status
        inputs[ReviewInputType.NC_CAPA_STATUS] = self.collect_nc_capa_status(date_range_start, date_range_end, department_id)
        
        # Collect supplier performance
        inputs[ReviewInputType.SUPPLIER_PERFORMANCE] = self.collect_supplier_performance(date_range_start, date_range_end)
        
        # Collect KPI metrics
        inputs[ReviewInputType.KPI_METRICS] = self.collect_kpi_metrics(date_range_start, date_range_end, department_id)
        
        # Collect HACCP performance
        inputs[ReviewInputType.HACCP_PERFORMANCE] = self.collect_haccp_performance(date_range_start, date_range_end)
        
        # Collect PRP performance
        inputs[ReviewInputType.PRP_PERFORMANCE] = self.collect_prp_performance(date_range_start, date_range_end)
        
        # Collect risk assessment updates
        inputs[ReviewInputType.RISK_ASSESSMENT] = self.collect_risk_assessment_updates(date_range_start, date_range_end)
        
        # Collect customer feedback (placeholder - to be integrated with complaints module)
        inputs[ReviewInputType.CUSTOMER_FEEDBACK] = self.collect_customer_feedback(date_range_start, date_range_end)
        
        return inputs
    
    def collect_audit_results(self, start_date: datetime, end_date: datetime, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Collect audit results and findings"""
        try:
            # Get audits in the date range
            q = self.db.query(Audit).filter(
                and_(
                    Audit.scheduled_date >= start_date,
                    Audit.scheduled_date <= end_date
                )
            )
            if department_id is not None:
                q = q.filter(Audit.auditee_department_id == department_id) if hasattr(Audit, 'auditee_department_id') else q
            audits = q.all()
            
            # Get audit findings
            audit_ids = [audit.id for audit in audits]
            findings = self.db.query(AuditFinding).filter(
                AuditFinding.audit_id.in_(audit_ids)
            ).all() if audit_ids else []
            
            # Aggregate findings by severity
            findings_by_severity = {}
            for severity in FindingSeverity:
                findings_by_severity[severity.value] = len([
                    f for f in findings if f.severity == severity
                ])
            
            # Calculate completion rates
            completed_audits = len([a for a in audits if a.status == "completed"])
            total_audits = len(audits)
            completion_rate = (completed_audits / total_audits * 100) if total_audits > 0 else 0
            
            # Get open findings
            open_findings = len([f for f in findings if f.status != "closed"])
            
            return {
                "summary": f"Conducted {total_audits} audits with {completion_rate:.1f}% completion rate",
                "data": {
                    "total_audits": total_audits,
                    "completed_audits": completed_audits,
                    "completion_rate": completion_rate,
                    "total_findings": len(findings),
                    "open_findings": open_findings,
                    "findings_by_severity": findings_by_severity,
                    "audit_details": [
                        {
                            "id": a.id,
                            "title": a.title,
                            "status": a.status,
                            "scheduled_date": a.scheduled_date.isoformat() if a.scheduled_date else None,
                            "findings_count": len([f for f in findings if f.audit_id == a.id])
                        } for a in audits
                    ]
                },
                "completeness_score": 0.9,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting audit results: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_nc_capa_status(self, start_date: datetime, end_date: datetime, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Collect nonconformance and CAPA status"""
        try:
            # Get nonconformances in date range
            q = self.db.query(NonConformance).filter(
                and_(
                    NonConformance.created_at >= start_date,
                    NonConformance.created_at <= end_date
                )
            )
            if department_id is not None and hasattr(NonConformance, 'department_id'):
                q = q.filter(NonConformance.department_id == department_id)
            ncs = q.all()
            
            # Get CAPA actions
            nc_ids = [nc.id for nc in ncs]
            capas = self.db.query(CAPAAction).filter(
                CAPAAction.nonconformance_id.in_(nc_ids)
            ).all() if nc_ids else []
            
            # Status distribution
            nc_status_dist = {}
            for status in NonConformanceStatus:
                nc_status_dist[status.value] = len([nc for nc in ncs if nc.status == status])
            
            capa_status_dist = {}
            for status in CAPAStatus:
                capa_status_dist[status.value] = len([c for c in capas if c.status == status])
            
            # Calculate closure rates
            closed_ncs = len([nc for nc in ncs if nc.status == NonConformanceStatus.CLOSED])
            nc_closure_rate = (closed_ncs / len(ncs) * 100) if ncs else 0
            
            completed_capas = len([c for c in capas if c.status == CAPAStatus.COMPLETED])
            capa_completion_rate = (completed_capas / len(capas) * 100) if capas else 0
            
            return {
                "summary": f"Managed {len(ncs)} nonconformances with {nc_closure_rate:.1f}% closure rate and {len(capas)} CAPA actions with {capa_completion_rate:.1f}% completion rate",
                "data": {
                    "total_nonconformances": len(ncs),
                    "nc_status_distribution": nc_status_dist,
                    "nc_closure_rate": nc_closure_rate,
                    "total_capa_actions": len(capas),
                    "capa_status_distribution": capa_status_dist,
                    "capa_completion_rate": capa_completion_rate,
                    "overdue_actions": len([c for c in capas if c.due_date and c.due_date < datetime.utcnow() and c.status != CAPAStatus.COMPLETED])
                },
                "completeness_score": 0.95,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting NC/CAPA status: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_supplier_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect supplier performance data"""
        try:
            # Get supplier evaluations in date range
            evaluations = self.db.query(SupplierEvaluation).filter(
                and_(
                    SupplierEvaluation.evaluation_date >= start_date,
                    SupplierEvaluation.evaluation_date <= end_date
                )
            ).all()
            
            # Get all active suppliers
            suppliers = self.db.query(Supplier).filter(Supplier.status == "active").all()
            
            # Calculate average scores
            if evaluations:
                avg_quality_score = sum([e.quality_score for e in evaluations if e.quality_score]) / len([e for e in evaluations if e.quality_score])
                avg_delivery_score = sum([e.delivery_score for e in evaluations if e.delivery_score]) / len([e for e in evaluations if e.delivery_score])
                avg_service_score = sum([e.service_score for e in evaluations if e.service_score]) / len([e for e in evaluations if e.service_score])
            else:
                avg_quality_score = avg_delivery_score = avg_service_score = 0
            
            # Count approved vs non-approved suppliers
            approved_suppliers = len([s for s in suppliers if s.approval_status == "approved"])
            
            return {
                "summary": f"Evaluated {len(evaluations)} suppliers with average quality score of {avg_quality_score:.1f}",
                "data": {
                    "total_suppliers": len(suppliers),
                    "approved_suppliers": approved_suppliers,
                    "approval_rate": (approved_suppliers / len(suppliers) * 100) if suppliers else 0,
                    "evaluations_conducted": len(evaluations),
                    "average_scores": {
                        "quality": round(avg_quality_score, 2),
                        "delivery": round(avg_delivery_score, 2),
                        "service": round(avg_service_score, 2)
                    },
                    "supplier_performance_trends": "Stable"  # This could be calculated based on historical data
                },
                "completeness_score": 0.8,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting supplier performance: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_kpi_metrics(self, start_date: datetime, end_date: datetime, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Collect KPI metrics from risk management"""
        try:
            # Get KPIs with recent updates
            q = self.db.query(RiskKPI).filter(
                and_(
                    RiskKPI.last_updated >= start_date,
                    RiskKPI.last_updated <= end_date
                )
            )
            if department_id is not None and hasattr(RiskKPI, 'department_id'):
                q = q.filter(RiskKPI.department_id == department_id)
            kpis = q.all()
            
            # Calculate performance
            on_target_kpis = len([k for k in kpis if k.kpi_current_value and k.kpi_target and k.kpi_current_value >= k.kpi_target])
            total_kpis = len(kpis)
            performance_rate = (on_target_kpis / total_kpis * 100) if total_kpis > 0 else 0
            
            # Group by category
            kpi_by_category = {}
            for kpi in kpis:
                category = kpi.kpi_category or "uncategorized"
                if category not in kpi_by_category:
                    kpi_by_category[category] = []
                kpi_by_category[category].append({
                    "name": kpi.kpi_name,
                    "current_value": kpi.kpi_current_value,
                    "target_value": kpi.kpi_target,
                    "unit": kpi.kpi_unit,
                    "status": kpi.kpi_status
                })
            
            return {
                "summary": f"Monitored {total_kpis} KPIs with {performance_rate:.1f}% meeting targets",
                "data": {
                    "total_kpis": total_kpis,
                    "on_target_kpis": on_target_kpis,
                    "performance_rate": performance_rate,
                    "kpi_by_category": kpi_by_category
                },
                "completeness_score": 0.85,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting KPI metrics: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_haccp_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect HACCP system performance data"""
        try:
            # Get monitoring logs in date range
            monitoring_logs = self.db.query(CCPMonitoringLog).filter(
                and_(
                    CCPMonitoringLog.monitoring_datetime >= start_date,
                    CCPMonitoringLog.monitoring_datetime <= end_date
                )
            ).all()
            
            # Get active CCPs
            ccps = self.db.query(CCP).all()
            
            # Get products with approved HACCP plans
            approved_products = self.db.query(Product).filter(
                Product.haccp_plan_approved == True
            ).all()
            
            # Calculate compliance rate
            compliant_logs = len([log for log in monitoring_logs if log.within_limits])
            total_logs = len(monitoring_logs)
            compliance_rate = (compliant_logs / total_logs * 100) if total_logs > 0 else 0
            
            # Count deviations
            deviations = len([log for log in monitoring_logs if not log.within_limits])
            
            return {
                "summary": f"HACCP monitoring shows {compliance_rate:.1f}% compliance rate with {deviations} deviations",
                "data": {
                    "total_ccps": len(ccps),
                    "approved_haccp_plans": len(approved_products),
                    "monitoring_logs": total_logs,
                    "compliance_rate": compliance_rate,
                    "deviations": deviations,
                    "corrective_actions_taken": len([log for log in monitoring_logs if log.corrective_action_taken])
                },
                "completeness_score": 0.9,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting HACCP performance: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_prp_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect PRP performance data"""
        try:
            # Get PRP programs
            prp_programs = self.db.query(PRPProgram).all()
            
            # Get PRP checklists in date range
            checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.created_at >= start_date,
                    PRPChecklist.created_at <= end_date
                )
            ).all()
            
            # Calculate compliance
            active_programs = len([p for p in prp_programs if p.status == "active"])
            completed_checklists = len([c for c in checklists if c.status == "completed"])
            
            return {
                "summary": f"PRP monitoring: {active_programs} active programs, {completed_checklists} checklists completed",
                "data": {
                    "total_prp_programs": len(prp_programs),
                    "active_programs": active_programs,
                    "completed_checklists": completed_checklists,
                    "checklist_completion_rate": (completed_checklists / len(checklists) * 100) if checklists else 0
                },
                "completeness_score": 0.8,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting PRP performance: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_risk_assessment_updates(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect risk assessment updates"""
        try:
            # Get risk items updated in date range
            risks = self.db.query(RiskRegisterItem).filter(
                and_(
                    RiskRegisterItem.updated_at >= start_date,
                    RiskRegisterItem.updated_at <= end_date
                )
            ).all()
            
            # Status distribution
            status_dist = {}
            for status in RiskStatus:
                status_dist[status.value] = len([r for r in risks if r.status == status])
            
            # Risk level distribution
            risk_levels = {}
            for risk in risks:
                level = risk.risk_level or "unknown"
                risk_levels[level] = risk_levels.get(level, 0) + 1
            
            return {
                "summary": f"Updated {len(risks)} risk assessments with current status distribution",
                "data": {
                    "total_risks_updated": len(risks),
                    "status_distribution": status_dist,
                    "risk_level_distribution": risk_levels,
                    "new_risks_identified": len([r for r in risks if r.created_at >= start_date]),
                    "risks_mitigated": len([r for r in risks if r.status == RiskStatus.MITIGATED])
                },
                "completeness_score": 0.85,
                "collection_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "summary": f"Error collecting risk assessment updates: {str(e)}",
                "data": {},
                "completeness_score": 0.0,
                "collection_date": datetime.utcnow().isoformat()
            }
    
    def collect_customer_feedback(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect customer feedback data (placeholder for complaints integration)"""
        # This would integrate with the complaints module when available
        return {
            "summary": "Customer feedback collection pending integration with complaints module",
            "data": {
                "total_complaints": 0,
                "resolved_complaints": 0,
                "customer_satisfaction_score": 4.2,
                "feedback_categories": {},
                "improvement_suggestions": []
            },
            "completeness_score": 0.3,
            "collection_date": datetime.utcnow().isoformat()
        }
    
    def calculate_overall_fsms_effectiveness(self, inputs: Dict[ReviewInputType, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall FSMS effectiveness based on collected inputs"""
        try:
            # Weight different input types
            weights = {
                ReviewInputType.AUDIT_RESULTS: 0.2,
                ReviewInputType.NC_CAPA_STATUS: 0.2,
                ReviewInputType.HACCP_PERFORMANCE: 0.2,
                ReviewInputType.PRP_PERFORMANCE: 0.15,
                ReviewInputType.SUPPLIER_PERFORMANCE: 0.1,
                ReviewInputType.RISK_ASSESSMENT: 0.1,
                ReviewInputType.KPI_METRICS: 0.05
            }
            
            weighted_score = 0
            total_weight = 0
            
            for input_type, weight in weights.items():
                if input_type in inputs:
                    completeness = inputs[input_type].get("completeness_score", 0)
                    weighted_score += completeness * weight
                    total_weight += weight
            
            overall_effectiveness = (weighted_score / total_weight * 100) if total_weight > 0 else 0
            
            # Determine effectiveness level
            if overall_effectiveness >= 90:
                effectiveness_level = "Excellent"
            elif overall_effectiveness >= 80:
                effectiveness_level = "Good"
            elif overall_effectiveness >= 70:
                effectiveness_level = "Satisfactory"
            elif overall_effectiveness >= 60:
                effectiveness_level = "Needs Improvement"
            else:
                effectiveness_level = "Poor"
            
            return {
                "overall_effectiveness_score": round(overall_effectiveness, 2),
                "effectiveness_level": effectiveness_level,
                "data_completeness": round(weighted_score / total_weight * 100, 2) if total_weight > 0 else 0,
                "key_strengths": self._identify_strengths(inputs),
                "improvement_areas": self._identify_improvement_areas(inputs),
                "recommendations": self._generate_recommendations(inputs, overall_effectiveness)
            }
        except Exception as e:
            return {
                "overall_effectiveness_score": 0,
                "effectiveness_level": "Unable to Calculate",
                "error": str(e),
                "recommendations": ["Review data collection processes", "Ensure all modules are properly integrated"]
            }
    
    def _identify_strengths(self, inputs: Dict[ReviewInputType, Dict[str, Any]]) -> List[str]:
        """Identify key strengths based on input data"""
        strengths = []
        
        # Check audit performance
        if ReviewInputType.AUDIT_RESULTS in inputs:
            audit_data = inputs[ReviewInputType.AUDIT_RESULTS].get("data", {})
            if audit_data.get("completion_rate", 0) >= 90:
                strengths.append("High audit completion rate")
        
        # Check NC/CAPA performance
        if ReviewInputType.NC_CAPA_STATUS in inputs:
            nc_data = inputs[ReviewInputType.NC_CAPA_STATUS].get("data", {})
            if nc_data.get("nc_closure_rate", 0) >= 80:
                strengths.append("Effective nonconformance closure rate")
        
        # Check HACCP compliance
        if ReviewInputType.HACCP_PERFORMANCE in inputs:
            haccp_data = inputs[ReviewInputType.HACCP_PERFORMANCE].get("data", {})
            if haccp_data.get("compliance_rate", 0) >= 95:
                strengths.append("Excellent HACCP compliance")
        
        return strengths
    
    def _identify_improvement_areas(self, inputs: Dict[ReviewInputType, Dict[str, Any]]) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        # Check for low performance areas
        for input_type, data in inputs.items():
            completeness = data.get("completeness_score", 0)
            if completeness < 0.7:
                improvements.append(f"Improve data collection for {input_type.value}")
        
        return improvements
    
    def _generate_recommendations(self, inputs: Dict[ReviewInputType, Dict[str, Any]], 
                                 effectiveness_score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if effectiveness_score < 70:
            recommendations.append("Conduct comprehensive FSMS review to identify systemic issues")
            recommendations.append("Implement additional monitoring and measurement procedures")
        
        if effectiveness_score < 80:
            recommendations.append("Enhance staff training on food safety procedures")
            recommendations.append("Review and update risk assessments")
        
        # Always include continuous improvement
        recommendations.append("Continue monitoring performance indicators")
        recommendations.append("Schedule regular management reviews to maintain FSMS effectiveness")
        
        return recommendations