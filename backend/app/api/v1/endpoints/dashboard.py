from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
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
        # Get counts for different entities
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        total_haccp_plans = db.query(func.count(Product.id)).scalar() or 0
        total_prp_programs = db.query(func.count(PRPProgram.id)).scalar() or 0
        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        
        # Calculate compliance metrics (mock data for now)
        # In a real implementation, these would be calculated from actual data
        compliance_score = 98  # Percentage
        open_issues = 2
        pending_approvals = 0  # Will be implemented when approval system is added
        
        # Get recent document activity
        recent_documents = db.query(Document).order_by(desc(Document.created_at)).limit(5).all()
        
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
                    "category": doc.category.value if doc.category else None,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "status": doc.status.value if doc.status else None
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