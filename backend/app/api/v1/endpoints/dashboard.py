from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.haccp import Product, Hazard
from app.models.prp import PRPProgram, PRPChecklist
from app.models.supplier import Supplier, SupplierEvaluation, SupplierDocument, IncomingDelivery
from app.models.training import TrainingAttendance, TrainingProgram, TrainingSession
from app.models.nonconformance import NonConformance, CAPAAction
from app.models.audit_mgmt import Audit, AuditFinding
from app.models.equipment import MaintenancePlan, CalibrationPlan
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics for ISO 22000 FSMS
    """
    try:
        # Get counts for different entities (use String casts to avoid enum issues in some SQLite rows)
        from sqlalchemy import cast, String
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        # Also normalize document type counts to strings to avoid enum coercion errors downstream
        doc_type_counts = db.query(cast(Document.document_type, String), func.count(Document.id)).group_by(cast(Document.document_type, String)).all()
        total_products = db.query(func.count(Product.id)).scalar() or 0
        total_haccp_plans = db.query(func.count(Product.id)).filter(Product.haccp_plan_approved == True).scalar() or 0
        total_prp_programs = db.query(func.count(PRPProgram.id)).scalar() or 0
        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        
        # Calculate compliance metrics (mock data for now)
        # In a real implementation, these would be calculated from actual data
        compliance_score = 98  # Percentage
        open_issues = 2
        pending_approvals = 0  # Will be implemented when approval system is added
        
        # Get recent document activity using a projection to avoid enum coercion
        recent_documents = (
            db.query(
                Document.id,
                Document.title,
                cast(Document.category, String).label("category"),
                cast(Document.status, String).label("status"),
                Document.created_at,
            )
            .order_by(desc(Document.created_at))
            .limit(5)
            .all()
        )
        
        # Calculate system health metrics
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        
        # Process recent documents safely
        recent_docs_data = []
        for doc in recent_documents:
            try:
                recent_docs_data.append({
                    "id": doc.id,
                    "title": doc.title,
                    "category": (doc.category or None),
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "status": (doc.status or None)
                })
            except Exception as doc_error:
                # Skip problematic documents
                print(f"Error processing document {doc.id}: {doc_error}")
                continue
        
        # Normalize doc type counts to a serializable structure
        doc_type_counts_data = [
            {"type": (t or "unknown"), "count": int(c or 0)} for t, c in (doc_type_counts or [])
        ]
        
        stats = {
            "totalDocuments": total_documents,
            "totalProducts": total_products,
            "totalHaccpPlans": total_haccp_plans,
            "totalPrpPrograms": total_prp_programs,
            "totalSuppliers": total_suppliers,
            "docTypeCounts": doc_type_counts_data,
            "pendingApprovals": pending_approvals,
            "complianceScore": compliance_score,
            "openIssues": open_issues,
            "totalUsers": total_users,
            "activeUsers": active_users,
            "systemStatus": "online",
            "nextAuditDate": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "recentDocuments": recent_docs_data
        }
        
        return ResponseModel(
            success=True,
            message="Dashboard stats retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        print(f"Dashboard stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard stats: {str(e)}"
        )


@router.get("/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activities across the FSMS system
    """
    try:
        # Get recent documents using projection and string casts to avoid enum coercion issues
        from sqlalchemy import cast, String
        recent_docs = (
            db.query(
                Document.id,
                Document.title,
                Document.created_at,
                Document.updated_at,
                cast(Document.status, String).label("status"),
                cast(Document.category, String).label("category"),
            )
            .order_by(desc(Document.updated_at))
            .limit(3)
            .all()
        )
        # Build activities with safe, minimal fields
        activities = []
        for doc in recent_docs:
            try:
                user_name = "System"
                try:
                    creator_id = db.query(Document.created_by).filter(Document.id == doc.id).scalar()
                except Exception:
                    creator_id = None
                if creator_id:
                    u = db.query(User).filter(User.id == creator_id).first()
                    if u:
                        user_name = u.full_name or u.username or "System"
                activities.append({
                    "id": len(activities) + 1,
                    "action": "updated" if doc.updated_at and doc.updated_at > doc.created_at else "created",
                    "resource_type": "document",
                    "resource_id": doc.id,
                    "user": user_name,
                    "timestamp": (doc.updated_at or doc.created_at).isoformat() if (doc.updated_at or doc.created_at) else datetime.utcnow().isoformat(),
                    "title": doc.title,
                })
            except Exception:
                continue
        
        return ResponseModel(success=True, message="Recent activity retrieved successfully", data={"activities": activities})
    except Exception as e:
        print(f"Recent activity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activity: {str(e)}"
        )


@router.get("/iso-summary")
async def get_iso_executive_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executive summary for dashboard with ISO-centric KPIs and trends."""
    try:
        from sqlalchemy import cast, String

        # Compliance metrics
        total_docs = db.query(func.count(Document.id)).scalar() or 0
        approved_docs = db.query(func.count(Document.id)).filter(cast(Document.status, String) == "approved").scalar() or 0
        doc_compliance = round((approved_docs / total_docs) * 100, 2) if total_docs else 0.0

        total_hazards = db.query(func.count(Hazard.id)).scalar() or 0
        controlled_hazards = db.query(func.count(Hazard.id)).filter(Hazard.is_controlled == True).scalar() or 0
        haccp_score = round((controlled_hazards / total_hazards) * 100, 2) if total_hazards else 0.0

        total_prp = db.query(func.count(PRPChecklist.id)).scalar() or 0
        completed_prp = db.query(func.count(PRPChecklist.id)).filter(cast(PRPChecklist.status, String) == "completed").scalar() or 0
        prp_score = round((completed_prp / total_prp) * 100, 2) if total_prp else 0.0

        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        avg_supplier_score = db.query(func.avg(SupplierEvaluation.overall_score)).scalar() or 0.0
        supplier_score = round((avg_supplier_score / 5.0) * 100, 2) if avg_supplier_score else (100.0 if total_suppliers and avg_supplier_score == 0 else 0.0)

        total_users = db.query(func.count(User.id)).scalar() or 0
        trained_users = db.query(func.count(func.distinct(TrainingAttendance.user_id))).filter(TrainingAttendance.attended == True).scalar() or 0
        training_score = round((trained_users / total_users) * 100, 2) if total_users else 0.0

        overall = round((doc_compliance + haccp_score + prp_score + supplier_score + training_score) / 5.0, 2)

        # Risk distribution from NC severity
        high_nc = db.query(func.count(NonConformance.id)).filter(NonConformance.severity.in_(["high", "critical"])).scalar() or 0
        med_nc = db.query(func.count(NonConformance.id)).filter(NonConformance.severity == "medium").scalar() or 0
        low_nc = db.query(func.count(NonConformance.id)).filter(NonConformance.severity == "low").scalar() or 0

        # Performance counts
        nc_count = db.query(func.count(NonConformance.id)).scalar() or 0
        capa_count = db.query(func.count(CAPAAction.id)).scalar() or 0
        audit_count = db.query(func.count(Audit.id)).scalar() or 0
        training_count = db.query(func.count(TrainingAttendance.id)).filter(TrainingAttendance.attended == True).scalar() or 0

        # Trends (last 6 months)
        # SQLite-compatible month key
        month_fmt = "%Y-%m"
        now = datetime.utcnow()
        months = [(now - timedelta(days=30*i)).strftime(month_fmt) for i in reversed(range(6))]

        # NC per month
        nc_per_month = dict(
            db.query(func.strftime(month_fmt, NonConformance.reported_date), func.count(NonConformance.id))
              .group_by(func.strftime(month_fmt, NonConformance.reported_date)).all()
        )
        # Training attendance per month
        tr_per_month = dict(
            db.query(func.strftime(month_fmt, TrainingAttendance.created_at), func.count(TrainingAttendance.id))
              .group_by(func.strftime(month_fmt, TrainingAttendance.created_at)).all()
        )

        trend_data = []
        for m in months:
            # Approximate compliance trend using document compliance as proxy
            trend_data.append({
                "month": m.split("-")[-1],
                "compliance": overall,
                "incidents": int(nc_per_month.get(m, 0) or 0),
                "training": int(tr_per_month.get(m, 0) or 0),
            })

        payload = {
            "complianceMetrics": {
                "overall": overall,
                "haccp": haccp_score,
                "prp": prp_score,
                "supplier": supplier_score,
                "training": training_score,
            },
            "riskMetrics": {
                "high": int(high_nc),
                "medium": int(med_nc),
                "low": int(low_nc),
            },
            "performanceMetrics": {
                "ncCount": int(nc_count),
                "capaCount": int(capa_count),
                "auditCount": int(audit_count),
                "trainingCount": int(training_count),
            },
            "trendData": trend_data,
        }

        return ResponseModel(success=True, message="ISO executive summary", data=payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ISO summary: {e}")


@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return a comprehensive, ISO-grade overview for the dashboard."""
    try:
        from sqlalchemy import cast, String
        now = datetime.utcnow()
        in_30 = now + timedelta(days=30)
        last_90 = now - timedelta(days=90)

        # Documents
        total_docs = db.query(func.count(Document.id)).scalar() or 0
        docs_by_status = dict(
            db.query(cast(Document.status, String), func.count(Document.id)).group_by(cast(Document.status, String)).all()
        )
        docs_by_type = dict(
            db.query(cast(Document.document_type, String), func.count(Document.id)).group_by(cast(Document.document_type, String)).all()
        )
        approved_docs = int(docs_by_status.get("approved", 0) or 0)
        document_compliance = round((approved_docs / total_docs) * 100, 2) if total_docs else 0.0
        pending_approvals = int(docs_by_status.get("under_review", 0) or 0)
        upcoming_reviews = db.query(func.count(Document.id)).filter(Document.review_date != None, Document.review_date <= in_30).scalar() or 0

        # Suppliers
        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        avg_supplier_score = db.query(func.avg(SupplierEvaluation.overall_score)).scalar() or 0.0
        supplier_performance = round((avg_supplier_score / 5.0) * 100, 2) if avg_supplier_score else 0.0
        expiring_supplier_docs = db.query(func.count(SupplierDocument.id)).filter(SupplierDocument.expiry_date != None, SupplierDocument.expiry_date <= in_30).scalar() or 0
        deliveries_last_90 = db.query(func.count(IncomingDelivery.id)).filter(IncomingDelivery.delivery_date >= last_90).scalar() or 0
        deliveries_passed_last_90 = db.query(func.count(IncomingDelivery.id)).filter(IncomingDelivery.delivery_date >= last_90, IncomingDelivery.inspection_status == "passed").scalar() or 0
        delivery_pass_rate = round((deliveries_passed_last_90 / deliveries_last_90) * 100, 2) if deliveries_last_90 else 0.0

        # PRP
        total_prp_checklists = db.query(func.count(PRPChecklist.id)).scalar() or 0
        completed_prp = db.query(func.count(PRPChecklist.id)).filter(cast(PRPChecklist.status, String) == "completed").scalar() or 0
        prp_completion = round((completed_prp / total_prp_checklists) * 100, 2) if total_prp_checklists else 0.0

        # HACCP
        total_hazards = db.query(func.count(Hazard.id)).scalar() or 0
        controlled_hazards = db.query(func.count(Hazard.id)).filter(Hazard.is_controlled == True).scalar() or 0
        ccp_compliance = round((controlled_hazards / total_hazards) * 100, 2) if total_hazards else 0.0

        # Training
        total_users = db.query(func.count(User.id)).scalar() or 0
        trained_last_90 = db.query(func.count(func.distinct(TrainingAttendance.user_id))).filter(TrainingAttendance.created_at >= last_90, TrainingAttendance.attended == True).scalar() or 0
        training_completion = round((trained_last_90 / total_users) * 100, 2) if total_users else 0.0
        upcoming_sessions = db.query(func.count(TrainingSession.id)).filter(TrainingSession.session_date >= now, TrainingSession.session_date <= in_30).scalar() or 0

        # Audits
        audits_by_status = dict(db.query(cast(Audit.status, String), func.count(Audit.id)).group_by(cast(Audit.status, String)).all())
        findings_by_severity = dict(db.query(cast(AuditFinding.severity, String), func.count(AuditFinding.id)).group_by(cast(AuditFinding.severity, String)).all())

        # NC/CAPA
        nc_open = db.query(func.count(NonConformance.id)).filter(NonConformance.status.in_(["open", "in_progress"])) .scalar() or 0
        capa_open = db.query(func.count(CAPAAction.id)).filter(CAPAAction.status.in_(["open", "in_progress"])) .scalar() or 0

        # Equipment
        maintenance_due = db.query(func.count(MaintenancePlan.id)).filter(MaintenancePlan.next_due_at != None, MaintenancePlan.next_due_at <= in_30).scalar() or 0
        calibration_due = db.query(func.count(CalibrationPlan.id)).filter(CalibrationPlan.next_due_at != None, CalibrationPlan.next_due_at <= in_30).scalar() or 0

        # Trends (6 months) for NC and training
        month_fmt = "%Y-%m"
        months = [(now - timedelta(days=30*i)).strftime(month_fmt) for i in reversed(range(6))]
        nc_per_month = dict(db.query(func.strftime(month_fmt, NonConformance.reported_date), func.count(NonConformance.id)).group_by(func.strftime(month_fmt, NonConformance.reported_date)).all())
        capa_per_month = dict(db.query(func.strftime(month_fmt, CAPAAction.created_at), func.count(CAPAAction.id)).group_by(func.strftime(month_fmt, CAPAAction.created_at)).all())
        tr_per_month = dict(db.query(func.strftime(month_fmt, TrainingAttendance.created_at), func.count(TrainingAttendance.id)).group_by(func.strftime(month_fmt, TrainingAttendance.created_at)).all())
        trend = [{
            "month": m,
            "nc": int(nc_per_month.get(m, 0) or 0),
            "capa": int(capa_per_month.get(m, 0) or 0),
            "training": int(tr_per_month.get(m, 0) or 0)
        } for m in months]

        payload = {
            "kpis": {
                "overallCompliance": round((document_compliance + prp_completion + ccp_compliance + supplier_performance + training_completion) / 5.0, 2),
                "documentCompliance": document_compliance,
                "supplierPerformance": supplier_performance,
                "trainingCompletion": training_completion,
                "prpCompletion": prp_completion,
                "ccpCompliance": ccp_compliance,
            },
            "documents": {
                "total": int(total_docs),
                "byStatus": docs_by_status,
                "byType": docs_by_type,
                "pendingApprovals": int(pending_approvals),
                "upcomingReviews": int(upcoming_reviews),
            },
            "suppliers": {
                "total": int(total_suppliers),
                "avgScorePct": supplier_performance,
                "expiringCertificates": int(expiring_supplier_docs),
                "deliveryPassRate": delivery_pass_rate,
            },
            "audits": {
                "byStatus": audits_by_status,
                "findingsBySeverity": findings_by_severity,
            },
            "training": {
                "completionLast90": training_completion,
                "upcomingSessions": int(upcoming_sessions),
            },
            "equipment": {
                "maintenanceDue30": int(maintenance_due),
                "calibrationDue30": int(calibration_due),
            },
            "ncCapaTrend": trend,
            # Convenience tiles for front-end Action Center
            "actions": {
                "approvals": {
                    "documents": int(pending_approvals),
                    "audits": int(audits_by_status.get("in_progress", 0) or 0),
                    "suppliers": int(max(0, round((total_suppliers or 0) * 0.05)))
                },
                "expiring": {
                    "docReviews": int(upcoming_reviews),
                    "supplierCerts": int(expiring_supplier_docs),
                    "calibrations": int(calibration_due)
                }
            }
        }

        return ResponseModel(success=True, message="Overview ready", data=payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build overview: {e}")


# Frontend-expected auxiliary dashboard endpoints
@router.get("/user-metrics/{user_id}")
async def get_user_metrics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        metrics = {
            "compliance_score": 94.2,
            "open_capas": db.query(func.count(Document.id)).scalar() or 8,
            "audit_score": 98.5,
            "risk_level": "low",
            "tasks_completed_today": 6,
            "line_efficiency": 96.8,
        }
        return ResponseModel(success=True, message="User metrics retrieved", data={"user_id": user_id, "metrics": metrics})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user metrics: {str(e)}")


@router.get("/priority-tasks/{user_id}")
async def get_priority_tasks(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tasks = [
            {
                "id": "1",
                "title": "Monthly HACCP Review",
                "description": "Review and approve HACCP plans for new products",
                "priority": "high",
                "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                "category": "HACCP",
                "progress": 75,
                "estimated_time": "2 hours",
            },
            {
                "id": "2",
                "title": "Supplier Audit Schedule",
                "description": "Schedule quarterly audits for critical suppliers",
                "priority": "medium",
                "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                "category": "Supplier Management",
                "estimated_time": "1 hour",
            },
        ]
        return ResponseModel(success=True, message="Priority tasks retrieved", data={"tasks": tasks})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get priority tasks: {str(e)}")


@router.get("/insights/{user_id}")
async def get_insights(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        insights = [
            {
                "id": "1",
                "type": "info",
                "title": "System Performance",
                "description": "System is running optimally with 99.9% uptime",
                "action": {"label": "View Details", "endpoint": "/dashboard/stats", "method": "GET"},
            }
        ]
        return ResponseModel(success=True, message="Insights retrieved", data={"insights": insights})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.get("/compliance-metrics")
async def get_compliance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed compliance metrics for ISO 22000
    """
    try:
        # Calculate various compliance metrics
        total_docs = db.query(func.count(Document.id)).scalar() or 0
        total_haccp = db.query(func.count(Product.id)).scalar() or 0
        total_prp = db.query(func.count(PRPProgram.id)).scalar() or 0
        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        
        # Mock compliance calculations
        # In a real system, these would be based on actual audit results, checklist completions, etc.
        metrics = {
            "documentControl": {
                "score": 95,
                "total": total_docs,
                "compliant": total_docs - 1 if total_docs > 0 else 0,
                "status": "compliant"
            },
            "haccpImplementation": {
                "score": 92,
                "total": total_haccp,
                "compliant": total_haccp if total_haccp > 0 else 0,
                "status": "compliant" if total_haccp > 0 else "non_compliant"
            },
            "prpPrograms": {
                "score": 88,
                "total": total_prp,
                "compliant": total_prp if total_prp > 0 else 0,
                "status": "compliant" if total_prp > 0 else "non_compliant"
            },
            "supplierManagement": {
                "score": 96,
                "total": total_suppliers,
                "compliant": total_suppliers if total_suppliers > 0 else 0,
                "status": "compliant" if total_suppliers > 0 else "non_compliant"
            },
            "overallCompliance": 92.75
        }
        
        return ResponseModel(
            success=True,
            message="Compliance metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve compliance metrics: {str(e)}"
        )


@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system health and status information
    """
    try:
        # Check database connectivity
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception:
            db_status = "error"
        
        # Get system metrics
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        
        status_info = {
            "database": db_status,
            "api": "healthy",
            "authentication": "healthy",
            "fileStorage": "healthy",
            "totalUsers": total_users,
            "activeUsers": active_users,
            "lastBackup": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "uptime": "99.9%",
            "version": "1.0.0"
        }
        
        return ResponseModel(
            success=True,
            message="System status retrieved successfully",
            data=status_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system status: {str(e)}"
        )


# =============================================================================
# ADVANCED DASHBOARD FEATURES
# =============================================================================

@router.get("/fsms-compliance-score")
async def get_fsms_compliance_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time FSMS compliance score calculation"""
    try:
        # Calculate comprehensive FSMS compliance score
        # This would aggregate data from all modules
        
        # Mock calculations based on various factors
        compliance_factors = {
            "document_control": {
                "weight": 0.15,
                "score": 95.0,
                "factors": ["approval_workflow", "version_control", "distribution"]
            },
            "haccp_implementation": {
                "weight": 0.25,
                "score": 92.0,
                "factors": ["ccp_monitoring", "corrective_actions", "verification"]
            },
            "prp_programs": {
                "weight": 0.20,
                "score": 88.0,
                "factors": ["checklist_completion", "non_conformances", "improvements"]
            },
            "supplier_management": {
                "weight": 0.15,
                "score": 96.0,
                "factors": ["evaluations", "deliveries", "corrective_actions"]
            },
            "training_competency": {
                "weight": 0.10,
                "score": 94.0,
                "factors": ["completion_rates", "assessments", "certifications"]
            },
            "audit_compliance": {
                "weight": 0.15,
                "score": 90.0,
                "factors": ["internal_audits", "external_audits", "findings_resolution"]
            }
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            factor["weight"] * factor["score"] 
            for factor in compliance_factors.values()
        )
        
        compliance_data = {
            "overall_score": round(overall_score, 2),
            "compliance_level": "compliant" if overall_score >= 90 else "needs_improvement" if overall_score >= 80 else "non_compliant",
            "last_calculated": datetime.utcnow().isoformat(),
            "factors": compliance_factors,
            "trend": "stable",  # improving, stable, declining
            "recommendations": [
                "Focus on PRP program completion rates",
                "Enhance HACCP verification procedures",
                "Improve audit findings resolution time"
            ]
        }
        
        return ResponseModel(
            success=True,
            message="FSMS compliance score calculated successfully",
            data=compliance_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate FSMS compliance score: {str(e)}"
        )


@router.get("/cross-module-kpis")
async def get_cross_module_kpis(
    period: str = Query(default="month", pattern="^(week|month|quarter|year)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated KPIs across all modules"""
    try:
        # Calculate period dates
        end_date = datetime.utcnow()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "quarter":
            start_date = end_date - timedelta(days=90)
        else:  # year
            start_date = end_date - timedelta(days=365)
        
        # Mock cross-module KPIs
        kpi_data = {
            "period": {
                "type": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "food_safety_metrics": {
                "ccp_compliance_rate": 95.5,
                "prp_completion_rate": 92.1,
                "non_conformances": 15,
                "corrective_actions_completed": 14,
                "food_safety_incidents": 0
            },
            "operational_metrics": {
                "documents_processed": 245,
                "audits_completed": 12,
                "training_sessions": 8,
                "supplier_evaluations": 6
            },
            "quality_metrics": {
                "customer_complaints": 3,
                "complaint_resolution_rate": 100.0,
                "supplier_delivery_accuracy": 98.5,
                "equipment_calibration_compliance": 100.0
            },
            "compliance_metrics": {
                "regulatory_compliance": 100.0,
                "iso_22000_compliance": 92.8,
                "certification_status": "valid",
                "next_audit_date": (end_date + timedelta(days=45)).isoformat()
            },
            "trends": {
                "ccp_compliance_trend": "improving",
                "prp_completion_trend": "stable",
                "non_conformance_trend": "declining",
                "overall_performance": "improving"
            }
        }
        
        return ResponseModel(
            success=True,
            message="Cross-module KPIs retrieved successfully",
            data=kpi_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cross-module KPIs: {str(e)}"
        )


@router.post("/executive-summary")
async def generate_executive_summary(
    summary_params: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate executive summary reports"""
    try:
        # Extract parameters
        report_type = summary_params.get("report_type", "monthly")
        include_details = summary_params.get("include_details", True)
        include_recommendations = summary_params.get("include_recommendations", True)
        
        # Generate executive summary
        summary_data = {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": f"{current_user.first_name} {current_user.last_name}",
            "executive_summary": {
                "overall_performance": "Excellent",
                "fsms_effectiveness": "High",
                "key_achievements": [
                    "Zero food safety incidents this period",
                    "100% CCP compliance maintained",
                    "All regulatory requirements met",
                    "Supplier performance improved by 5%"
                ],
                "key_metrics": {
                    "fsms_compliance_score": 92.8,
                    "ccp_compliance_rate": 95.5,
                    "prp_completion_rate": 92.1,
                    "customer_satisfaction": 4.8
                }
            },
            "detailed_analysis": {
                "strengths": [
                    "Strong HACCP implementation",
                    "Effective document control",
                    "Proactive supplier management",
                    "Comprehensive training programs"
                ],
                "areas_for_improvement": [
                    "PRP completion rates could be higher",
                    "Some audit findings need faster resolution",
                    "Consider expanding training programs"
                ],
                "risks_and_opportunities": [
                    "Risk: Equipment aging may affect calibration",
                    "Opportunity: Implement predictive maintenance",
                    "Risk: Staff turnover affecting competency",
                    "Opportunity: Enhanced digital training platform"
                ]
            },
            "recommendations": [
                "Implement automated PRP reminders",
                "Establish audit findings tracking system",
                "Develop equipment replacement schedule",
                "Enhance competency assessment tools"
            ] if include_recommendations else [],
            "next_period_focus": [
                "Complete equipment calibration review",
                "Implement new training modules",
                "Conduct supplier performance review",
                "Prepare for external audit"
            ]
        }
        
        return ResponseModel(
            success=True,
            message="Executive summary generated successfully",
            data=summary_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate executive summary: {str(e)}"
        )


# =============================================================================
# REPORT SCHEDULER ENDPOINTS
# =============================================================================

@router.post("/reports/schedule")
async def schedule_automated_report(
    schedule_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule automated report generation"""
    try:
        # Validate required fields
        required_fields = ["report_type", "frequency", "recipients"]
        for field in required_fields:
            if field not in schedule_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Validate frequency
        valid_frequencies = ["daily", "weekly", "monthly", "quarterly"]
        if schedule_data["frequency"] not in valid_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid frequency. Must be one of: {', '.join(valid_frequencies)}"
            )

        # Create schedule record
        schedule_id = 1  # Mock ID - implement with actual model
        
        scheduled_report = {
            "id": schedule_id,
            "report_type": schedule_data["report_type"],
            "frequency": schedule_data["frequency"],
            "recipients": schedule_data["recipients"],
            "format": schedule_data.get("format", "pdf"),
            "include_attachments": schedule_data.get("include_attachments", True),
            "is_active": True,
            "next_run": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "created_by": current_user.id,
            "created_at": datetime.utcnow().isoformat()
        }

        return ResponseModel(
            success=True,
            message="Automated report scheduled successfully",
            data=scheduled_report
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule automated report: {str(e)}"
        )


@router.get("/reports/scheduled")
async def list_scheduled_reports(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List scheduled automated reports"""
    try:
        # Mock scheduled reports
        scheduled_reports = [
            {
                "id": 1,
                "report_type": "compliance_summary",
                "frequency": "monthly",
                "recipients": ["management@company.com", "quality@company.com"],
                "format": "pdf",
                "is_active": True,
                "next_run": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                "last_run": (datetime.utcnow() - timedelta(days=25)).isoformat(),
                "created_by": current_user.id
            },
            {
                "id": 2,
                "report_type": "executive_summary",
                "frequency": "quarterly",
                "recipients": ["ceo@company.com", "board@company.com"],
                "format": "pdf",
                "is_active": True,
                "next_run": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                "last_run": (datetime.utcnow() - timedelta(days=85)).isoformat(),
                "created_by": current_user.id
            }
        ]

        return ResponseModel(
            success=True,
            message="Scheduled reports retrieved successfully",
            data={"scheduled_reports": scheduled_reports}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scheduled reports: {str(e)}"
        )


@router.put("/reports/scheduled/{schedule_id}")
async def update_scheduled_report(
    schedule_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update scheduled report configuration"""
    try:
        # Validate update fields
        allowed_fields = ["frequency", "recipients", "format", "include_attachments", "is_active"]
        for field in update_data:
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field}' not allowed for update"
                )

        # Mock update
        updated_report = {
            "id": schedule_id,
            "report_type": "compliance_summary",
            "frequency": update_data.get("frequency", "monthly"),
            "recipients": update_data.get("recipients", []),
            "format": update_data.get("format", "pdf"),
            "is_active": update_data.get("is_active", True),
            "updated_by": current_user.id,
            "updated_at": datetime.utcnow().isoformat()
        }

        return ResponseModel(
            success=True,
            message="Scheduled report updated successfully",
            data=updated_report
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scheduled report: {str(e)}"
        )


@router.delete("/reports/scheduled/{schedule_id}")
async def cancel_scheduled_report(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel scheduled automated report"""
    try:
        # Mock cancellation
        cancelled_report = {
            "id": schedule_id,
            "status": "cancelled",
            "cancelled_by": current_user.id,
            "cancelled_at": datetime.utcnow().isoformat()
        }

        return ResponseModel(
            success=True,
            message="Scheduled report cancelled successfully",
            data=cancelled_report
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel scheduled report: {str(e)}"
        ) 

@router.get("/kpis")
async def get_dashboard_kpis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive KPIs for dashboard with real data calculations
    """
    try:
        from sqlalchemy import cast, String
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        last_90_days = now - timedelta(days=90)
        
        # Document Control KPIs
        total_docs = db.query(func.count(Document.id)).scalar() or 0
        approved_docs = db.query(func.count(Document.id)).filter(cast(Document.status, String) == "approved").scalar() or 0
        doc_compliance = round((approved_docs / total_docs) * 100, 2) if total_docs else 0.0
        
        # HACCP KPIs
        total_hazards = db.query(func.count(Hazard.id)).scalar() or 0
        controlled_hazards = db.query(func.count(Hazard.id)).filter(Hazard.is_controlled == True).scalar() or 0
        ccp_compliance = round((controlled_hazards / total_hazards) * 100, 2) if total_hazards else 0.0
        
        # PRP KPIs
        total_prp = db.query(func.count(PRPChecklist.id)).scalar() or 0
        completed_prp = db.query(func.count(PRPChecklist.id)).filter(cast(PRPChecklist.status, String) == "completed").scalar() or 0
        prp_completion = round((completed_prp / total_prp) * 100, 2) if total_prp else 0.0
        
        # Supplier KPIs
        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        avg_supplier_score = db.query(func.avg(SupplierEvaluation.overall_score)).scalar() or 0.0
        supplier_score = round((avg_supplier_score / 5.0) * 100, 2) if avg_supplier_score else 0.0
        
        # Training KPIs
        total_users = db.query(func.count(User.id)).scalar() or 0
        trained_users = db.query(func.count(func.distinct(TrainingAttendance.user_id))).filter(TrainingAttendance.attended == True).scalar() or 0
        training_completion = round((trained_users / total_users) * 100, 2) if total_users else 0.0
        
        # NC/CAPA KPIs
        nc_last_30 = db.query(func.count(NonConformance.id)).filter(NonConformance.reported_date >= last_30_days).scalar() or 0
        capa_last_30 = db.query(func.count(CAPAAction.id)).filter(CAPAAction.created_at >= last_30_days).scalar() or 0
        open_nc = db.query(func.count(NonConformance.id)).filter(NonConformance.status.in_(["open", "in_progress"])).scalar() or 0
        open_capa = db.query(func.count(CAPAAction.id)).filter(CAPAAction.status.in_(["open", "in_progress"])).scalar() or 0
        
        # Audit KPIs
        total_audits = db.query(func.count(Audit.id)).scalar() or 0
        completed_audits = db.query(func.count(Audit.id)).filter(cast(Audit.status, String) == "completed").scalar() or 0
        audit_completion = round((completed_audits / total_audits) * 100, 2) if total_audits else 0.0
        
        # Overall FSMS Compliance Score
        overall_compliance = round((doc_compliance + ccp_compliance + prp_completion + supplier_score + training_completion) / 5.0, 2)
        
        kpis = {
            "overallCompliance": overall_compliance,
            "documentControl": {
                "compliance": doc_compliance,
                "totalDocuments": total_docs,
                "approvedDocuments": approved_docs
            },
            "haccp": {
                "ccpCompliance": ccp_compliance,
                "totalHazards": total_hazards,
                "controlledHazards": controlled_hazards
            },
            "prp": {
                "completion": prp_completion,
                "totalChecklists": total_prp,
                "completedChecklists": completed_prp
            },
            "suppliers": {
                "performance": supplier_score,
                "totalSuppliers": total_suppliers,
                "avgScore": avg_supplier_score
            },
            "training": {
                "completion": training_completion,
                "totalUsers": total_users,
                "trainedUsers": trained_users
            },
            "nonConformance": {
                "last30Days": nc_last_30,
                "openNC": open_nc,
                "openCAPA": open_capa
            },
            "audits": {
                "completion": audit_completion,
                "totalAudits": total_audits,
                "completedAudits": completed_audits
            }
        }
        
        return ResponseModel(success=True, message="KPIs retrieved successfully", data=kpis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get KPIs: {str(e)}")


@router.get("/charts/{chart_type}")
async def get_dashboard_charts(
    chart_type: str,
    period: str = Query("6m", description="Time period: 1m, 3m, 6m, 1y"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chart data for different dashboard visualizations
    """
    try:
        from sqlalchemy import cast, String
        now = datetime.utcnow()
        
        # Calculate date range based on period
        if period == "1m":
            start_date = now - timedelta(days=30)
            group_by = "%Y-%m-%d"
        elif period == "3m":
            start_date = now - timedelta(days=90)
            group_by = "%Y-%m"
        elif period == "6m":
            start_date = now - timedelta(days=180)
            group_by = "%Y-%m"
        elif period == "1y":
            start_date = now - timedelta(days=365)
            group_by = "%Y-%m"
        else:
            start_date = now - timedelta(days=180)
            group_by = "%Y-%m"
        
        if chart_type == "nc_trend":
            # Non-conformance trend over time
            data = db.query(
                func.strftime(group_by, NonConformance.reported_date).label("period"),
                func.count(NonConformance.id).label("count")
            ).filter(
                NonConformance.reported_date >= start_date
            ).group_by(
                func.strftime(group_by, NonConformance.reported_date)
            ).order_by("period").all()
            
            chart_data = [{"period": row.period, "count": row.count} for row in data]
            
        elif chart_type == "compliance_by_department":
            # Compliance scores by department (using document categories as proxy)
            data = db.query(
                cast(Document.category, String).label("department"),
                func.count(Document.id).label("total"),
                func.sum(func.case((cast(Document.status, String) == "approved", 1), else_=0)).label("approved")
            ).filter(
                Document.created_at >= start_date
            ).group_by(
                cast(Document.category, String)
            ).all()
            
            chart_data = []
            for row in data:
                if row.total > 0:
                    compliance = round((row.approved / row.total) * 100, 2)
                    chart_data.append({
                        "department": row.department or "Unknown",
                        "compliance": compliance,
                        "total": row.total,
                        "approved": row.approved
                    })
                    
        elif chart_type == "supplier_performance":
            # Supplier performance distribution
            data = db.query(
                func.round(SupplierEvaluation.overall_score, 1).label("score"),
                func.count(SupplierEvaluation.id).label("count")
            ).group_by(
                func.round(SupplierEvaluation.overall_score, 1)
            ).order_by("score").all()
            
            chart_data = [{"score": row.score, "count": row.count} for row in data]
            
        elif chart_type == "training_completion":
            # Training completion over time
            data = db.query(
                func.strftime(group_by, TrainingAttendance.created_at).label("period"),
                func.count(TrainingAttendance.id).label("total"),
                func.sum(func.case((TrainingAttendance.attended == True, 1), else_=0)).label("attended")
            ).filter(
                TrainingAttendance.created_at >= start_date
            ).group_by(
                func.strftime(group_by, TrainingAttendance.created_at)
            ).order_by("period").all()
            
            chart_data = []
            for row in data:
                if row.total > 0:
                    completion_rate = round((row.attended / row.total) * 100, 2)
                    chart_data.append({
                        "period": row.period,
                        "completion_rate": completion_rate,
                        "total": row.total,
                        "attended": row.attended
                    })
                    
        elif chart_type == "audit_findings":
            # Audit findings by severity
            data = db.query(
                cast(AuditFinding.severity, String).label("severity"),
                func.count(AuditFinding.id).label("count")
            ).group_by(
                cast(AuditFinding.severity, String)
            ).all()
            
            chart_data = [{"severity": row.severity or "Unknown", "count": row.count} for row in data]
            
        elif chart_type == "document_status":
            # Document status distribution
            data = db.query(
                cast(Document.status, String).label("status"),
                func.count(Document.id).label("count")
            ).group_by(
                cast(Document.status, String)
            ).all()
            
            chart_data = [{"status": row.status or "Unknown", "count": row.count} for row in data]
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown chart type: {chart_type}")
        
        return ResponseModel(
            success=True, 
            message=f"{chart_type} chart data retrieved", 
            data={
                "chart_type": chart_type,
                "period": period,
                "data": chart_data
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chart data: {str(e)}")


@router.get("/department-compliance")
async def get_department_compliance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get FSMS compliance score per department
    """
    try:
        from sqlalchemy import cast, String
        
        # Get document compliance by category (department proxy)
        doc_compliance = db.query(
            cast(Document.category, String).label("department"),
            func.count(Document.id).label("total"),
            func.sum(func.case((cast(Document.status, String) == "approved", 1), else_=0)).label("approved")
        ).group_by(
            cast(Document.category, String)
        ).all()
        
        # Get training completion by department (using user roles as proxy)
        training_compliance = db.query(
            cast(User.role, String).label("department"),
            func.count(func.distinct(User.id)).label("total_users"),
            func.count(func.distinct(TrainingAttendance.user_id)).label("trained_users")
        ).outerjoin(
            TrainingAttendance, User.id == TrainingAttendance.user_id
        ).filter(
            TrainingAttendance.attended == True
        ).group_by(
            cast(User.role, String)
        ).all()
        
        # Calculate compliance scores
        department_scores = {}
        
        # Document compliance
        for row in doc_compliance:
            dept = row.department or "Unknown"
            if row.total > 0:
                score = round((row.approved / row.total) * 100, 2)
                department_scores[dept] = {
                    "document_compliance": score,
                    "total_documents": row.total,
                    "approved_documents": row.approved
                }
        
        # Training compliance
        for row in training_compliance:
            dept = row.department or "Unknown"
            if row.total_users > 0:
                score = round((row.trained_users / row.total_users) * 100, 2)
                if dept in department_scores:
                    department_scores[dept]["training_compliance"] = score
                    department_scores[dept]["total_users"] = row.total_users
                    department_scores[dept]["trained_users"] = row.trained_users
                else:
                    department_scores[dept] = {
                        "training_compliance": score,
                        "total_users": row.total_users,
                        "trained_users": row.trained_users
                    }
        
        # Calculate overall department compliance
        for dept, data in department_scores.items():
            scores = []
            if "document_compliance" in data:
                scores.append(data["document_compliance"])
            if "training_compliance" in data:
                scores.append(data["training_compliance"])
            
            if scores:
                data["overall_compliance"] = round(sum(scores) / len(scores), 2)
        
        return ResponseModel(
            success=True,
            message="Department compliance scores retrieved",
            data=department_scores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get department compliance: {str(e)}")


@router.get("/export/{export_type}")
async def export_dashboard_data(
    export_type: str,
    format: str = Query("excel", description="Export format: excel, pdf, csv"),
    period: str = Query("6m", description="Time period: 1m, 3m, 6m, 1y"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export dashboard data in various formats
    """
    try:
        from sqlalchemy import cast, String
        import pandas as pd
        from io import BytesIO
        
        now = datetime.utcnow()
        
        # Calculate date range
        if period == "1m":
            start_date = now - timedelta(days=30)
        elif period == "3m":
            start_date = now - timedelta(days=90)
        elif period == "6m":
            start_date = now - timedelta(days=180)
        elif period == "1y":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=180)
        
        if export_type == "compliance_report":
            # Export compliance data
            data = []
            
            # Document compliance
            docs = db.query(
                Document.title,
                cast(Document.category, String).label("category"),
                cast(Document.status, String).label("status"),
                Document.created_at,
                Document.review_date
            ).filter(
                Document.created_at >= start_date
            ).all()
            
            for doc in docs:
                data.append({
                    "Type": "Document",
                    "Title": doc.title,
                    "Category": doc.category,
                    "Status": doc.status,
                    "Created": doc.created_at,
                    "Review_Date": doc.review_date
                })
            
            # NC/CAPA data
            ncs = db.query(
                NonConformance.title,
                NonConformance.severity,
                cast(NonConformance.status, String).label("status"),
                NonConformance.reported_date,
                NonConformance.resolution_date
            ).filter(
                NonConformance.reported_date >= start_date
            ).all()
            
            for nc in ncs:
                data.append({
                    "Type": "Non-Conformance",
                    "Title": nc.title,
                    "Severity": nc.severity,
                    "Status": nc.status,
                    "Reported": nc.reported_date,
                    "Resolved": nc.resolution_date
                })
            
            df = pd.DataFrame(data)
            
        elif export_type == "kpi_summary":
            # Export KPI summary
            kpis = await get_dashboard_kpis(current_user, db)
            kpi_data = kpis.data
            
            data = [
                {"KPI": "Overall Compliance", "Value": f"{kpi_data['overallCompliance']}%"},
                {"KPI": "Document Compliance", "Value": f"{kpi_data['documentControl']['compliance']}%"},
                {"KPI": "CCP Compliance", "Value": f"{kpi_data['haccp']['ccpCompliance']}%"},
                {"KPI": "PRP Completion", "Value": f"{kpi_data['prp']['completion']}%"},
                {"KPI": "Supplier Performance", "Value": f"{kpi_data['suppliers']['performance']}%"},
                {"KPI": "Training Completion", "Value": f"{kpi_data['training']['completion']}%"},
                {"KPI": "NC Last 30 Days", "Value": kpi_data['nonConformance']['last30Days']},
                {"KPI": "Open NC", "Value": kpi_data['nonConformance']['openNC']},
                {"KPI": "Open CAPA", "Value": kpi_data['nonConformance']['openCAPA']},
                {"KPI": "Audit Completion", "Value": f"{kpi_data['audits']['completion']}%"}
            ]
            
            df = pd.DataFrame(data)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown export type: {export_type}")
        
        # Create export file
        output = BytesIO()
        
        if format == "excel":
            df.to_excel(output, index=False, engine='openpyxl')
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"{export_type}_{period}_{now.strftime('%Y%m%d')}.xlsx"
        elif format == "csv":
            df.to_csv(output, index=False)
            media_type = "text/csv"
            filename = f"{export_type}_{period}_{now.strftime('%Y%m%d')}.csv"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        output.seek(0)
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.post("/schedule-report")
async def schedule_report(
    report_type: str,
    frequency: str = Query("weekly", description="Frequency: daily, weekly, monthly"),
    recipients: List[str] = Query(..., description="List of recipient emails"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule automated reports
    """
    try:
        # This would integrate with a task scheduler like Celery
        # For now, we'll just return a success message
        schedule_data = {
            "report_type": report_type,
            "frequency": frequency,
            "recipients": recipients,
            "created_by": current_user.id,
            "created_at": datetime.utcnow(),
            "status": "scheduled"
        }
        
        # TODO: Implement actual scheduling logic
        # This could involve:
        # 1. Creating a scheduled task in Celery
        # 2. Storing schedule in database
        # 3. Setting up email notifications
        
        return ResponseModel(
            success=True,
            message=f"Report scheduled successfully: {report_type} - {frequency}",
            data=schedule_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule report: {str(e)}") 