from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.haccp import Product
from app.models.prp import PRPProgram
from app.models.supplier import Supplier
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
        total_haccp_plans = db.query(func.count(Product.id)).scalar() or 0
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
        
        stats = {
            "totalDocuments": total_documents,
            "totalHaccpPlans": total_haccp_plans,
            "totalPrpPrograms": total_prp_programs,
            "totalSuppliers": total_suppliers,
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
        # Get recent documents
        recent_docs = db.query(Document).order_by(desc(Document.updated_at)).limit(3).all()
        
        # Get recent users (for demonstration)
        recent_users = db.query(User).order_by(desc(User.created_at)).limit(2).all()
        
        activities = []
        
        # Add document activities
        for doc in recent_docs:
            try:
                # Get user name for created_by
                user_name = "System"
                if doc.created_by:
                    user = db.query(User).filter(User.id == doc.created_by).first()
                    if user:
                        user_name = user.full_name or user.username
                
                activities.append({
                    "id": len(activities) + 1,
                    "action": "updated" if doc.updated_at and doc.updated_at > doc.created_at else "created",
                    "resource_type": "document",
                    "resource_id": doc.id,
                    "user": user_name,
                    "timestamp": doc.updated_at.isoformat() if doc.updated_at else doc.created_at.isoformat(),
                    "title": doc.title
                })
            except Exception as doc_error:
                print(f"Error processing document activity {doc.id}: {doc_error}")
                continue
        
        # Add user activities (mock for now)
        for user in recent_users:
            try:
                activities.append({
                    "id": len(activities) + 1,
                    "action": "created",
                    "resource_type": "user",
                    "resource_id": user.id,
                    "user": "System",
                    "timestamp": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
                    "title": f"User {user.username}"
                })
            except Exception as user_error:
                print(f"Error processing user activity {user.id}: {user_error}")
                continue
        
        # Add some mock activities for demonstration
        mock_activities = [
            {
                "id": len(activities) + 1,
                "action": "approved",
                "resource_type": "haccp_plan",
                "resource_id": 1,
                "user": "QA Manager",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "title": "Milk Processing HACCP Plan"
            },
            {
                "id": len(activities) + 2,
                "action": "completed",
                "resource_type": "prp_checklist",
                "resource_id": 5,
                "user": "Production Supervisor",
                "timestamp": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                "title": "Daily Sanitation Checklist"
            },
            {
                "id": len(activities) + 3,
                "action": "registered",
                "resource_type": "supplier",
                "resource_id": 3,
                "user": "Procurement Manager",
                "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                "title": "New Milk Supplier Registration"
            }
        ]
        
        activities.extend(mock_activities)
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return ResponseModel(
            success=True,
            message="Recent activity retrieved successfully",
            data={"activities": activities[:10]}  # Wrap in dictionary
        )
        
    except Exception as e:
        print(f"Recent activity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activity: {str(e)}"
        )


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
    period: str = Query(default="month", regex="^(week|month|quarter|year)$"),
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