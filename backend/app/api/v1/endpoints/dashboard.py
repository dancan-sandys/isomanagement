from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

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
    Get dashboard statistics
    """
    try:
        # Get counts for different entities
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        total_haccp_plans = db.query(func.count(Product.id)).scalar() or 0
        total_prp_programs = db.query(func.count(PRPProgram.id)).scalar() or 0
        total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0
        
        # For now, we'll set pending approvals to 0 since we don't have approval system yet
        pending_approvals = 0
        
        stats = {
            "totalDocuments": total_documents,
            "totalHaccpPlans": total_haccp_plans,
            "totalPrpPrograms": total_prp_programs,
            "totalSuppliers": total_suppliers,
            "pendingApprovals": pending_approvals
        }
        
        return ResponseModel(
            success=True,
            message="Dashboard stats retrieved successfully",
            data=stats
        )
        
    except Exception as e:
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
    Get recent activities
    """
    try:
        # For now, we'll return mock data since we don't have an audit log system yet
        # In a real implementation, this would query an audit_log table
        
        recent_activities = [
            {
                "id": 1,
                "action": "created",
                "resource_type": "document",
                "resource_id": 123,
                "user": "John Doe",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "action": "updated",
                "resource_type": "haccp_plan",
                "resource_id": 45,
                "user": "Jane Smith",
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat()
            },
            {
                "id": 3,
                "action": "approved",
                "resource_type": "document",
                "resource_id": 67,
                "user": "Mike Johnson",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            }
        ]
        
        return ResponseModel(
            success=True,
            message="Recent activity retrieved successfully",
            data=recent_activities
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activity: {str(e)}"
        ) 