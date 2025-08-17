from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, text
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_permission_dependency
from app.models.user import User
from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus, RiskThreshold
)
from app.schemas.common import ResponseModel
from app.schemas.haccp import (
    ProductCreate, ProductUpdate, ProductResponse, ProcessFlowCreate, ProcessFlowUpdate, ProcessFlowResponse,
    HazardCreate, HazardUpdate, HazardResponse, CCPCreate, CCPUpdate, CCPResponse,
    MonitoringLogCreate, MonitoringLogResponse, VerificationLogCreate, VerificationLogResponse,
    HACCPPlanCreate, HACCPPlanUpdate, HACCPPlanResponse, HACCPPlanVersionCreate, HACCPPlanVersionResponse,
    HACCPPlanApprovalCreate, HACCPPlanApprovalResponse, ProductRiskConfigCreate, ProductRiskConfigUpdate, ProductRiskConfigResponse,
    DecisionTreeCreate, DecisionTreeUpdate, DecisionTreeResponse, DecisionTreeQuestionResponse,
    RiskThresholdCreate, RiskThresholdUpdate, RiskThresholdResponse,
    HazardReviewCreate, HazardReviewUpdate, HazardReviewResponse,
    HACCPReportRequest, ValidationEvidence
)
from app.services.haccp_service import HACCPService, HACCPValidationError, HACCPBusinessError
from app.utils.audit import audit_event

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# PRODUCT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/products", response_model=ResponseModel)
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all products with pagination and filtering"""
    try:
        service = HACCPService(db)
        products = service.get_products(
            skip=skip, 
            limit=limit, 
            search=search, 
            category=category
        )
        
        return ResponseModel(
            success=True,
            message="Products retrieved successfully",
            data=products
        )
        
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )


@router.get("/products/{product_id}", response_model=ResponseModel)
async def get_product(
    product_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID"""
    try:
        service = HACCPService(db)
        product = service.get_product(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ResponseModel(
            success=True,
            message="Product retrieved successfully",
            data=product
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )


@router.post("/products", response_model=ResponseModel)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    try:
        service = HACCPService(db)
        product = service.create_product(
            product_data=product_data,
            created_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Product created successfully",
            data={"id": product.id, "name": product.name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/products/{product_id}", response_model=ResponseModel)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update an existing product"""
    try:
        service = HACCPService(db)
        product = service.update_product(
            product_id=product_id,
            product_data=product_data,
            updated_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Product updated successfully",
            data={"id": product.id, "name": product.name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@router.delete("/products/{product_id}", response_model=ResponseModel)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a product"""
    try:
        service = HACCPService(db)
        service.delete_product(product_id, deleted_by=current_user.id)
        
        return ResponseModel(
            success=True,
            message="Product deleted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HACCPBusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )


# ============================================================================
# PROCESS FLOW ENDPOINTS
# ============================================================================

@router.post("/products/{product_id}/process-flows", response_model=ResponseModel)
async def create_process_flow(
    product_id: int,
    flow_data: ProcessFlowCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a process flow for a product"""
    try:
        service = HACCPService(db)
        flow = service.create_process_flow(
            product_id=product_id,
            flow_data=flow_data,
            created_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Process flow created successfully",
            data={"id": flow.id, "name": flow.name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating process flow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create process flow"
        )


@router.put("/process-flows/{flow_id}", response_model=ResponseModel)
async def update_process_flow(
    flow_id: int,
    flow_data: ProcessFlowUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a process flow"""
    try:
        service = HACCPService(db)
        flow = service.update_process_flow(
            flow_id=flow_id,
            flow_data=flow_data,
            updated_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Process flow updated successfully",
            data={"id": flow.id, "name": flow.name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating process flow {flow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update process flow"
        )


@router.delete("/process-flows/{flow_id}", response_model=ResponseModel)
async def delete_process_flow(
    flow_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a process flow"""
    try:
        service = HACCPService(db)
        service.delete_process_flow(flow_id, deleted_by=current_user.id)
        
        return ResponseModel(
            success=True,
            message="Process flow deleted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HACCPBusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting process flow {flow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete process flow"
        )


# ============================================================================
# HAZARD MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/products/{product_id}/hazards", response_model=ResponseModel)
async def create_hazard(
    product_id: int,
    hazard_data: HazardCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a hazard for a product"""
    try:
        service = HACCPService(db)
        hazard = service.create_hazard(
            product_id=product_id,
            hazard_data=hazard_data,
            created_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Hazard created successfully",
            data={"id": hazard.id, "name": hazard.name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating hazard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create hazard"
        )


@router.put("/hazards/{hazard_id}", response_model=ResponseModel)
async def update_hazard(
    hazard_id: int,
    hazard_data: HazardUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a hazard"""
    try:
        service = HACCPService(db)
        hazard = service.update_hazard(
            hazard_id=hazard_id,
            hazard_data=hazard_data,
            updated_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Hazard updated successfully",
            data={"id": hazard.id, "name": hazard.name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating hazard {hazard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update hazard"
        )


@router.delete("/hazards/{hazard_id}", response_model=ResponseModel)
async def delete_hazard(
    hazard_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a hazard"""
    try:
        service = HACCPService(db)
        service.delete_hazard(hazard_id, deleted_by=current_user.id)
        
        return ResponseModel(
            success=True,
            message="Hazard deleted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HACCPBusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting hazard {hazard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete hazard"
        )


@router.post("/hazards/{hazard_id}/decision-tree", response_model=ResponseModel)
async def run_decision_tree(
    hazard_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Run the CCP decision tree for a hazard"""
    try:
        service = HACCPService(db)
        result = service.run_decision_tree(hazard_id, run_by_user_id=current_user.id)
        
        return ResponseModel(
            success=True,
            message="Decision tree executed successfully",
            data=result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error running decision tree for hazard {hazard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run decision tree"
        )


# ============================================================================
# CCP MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/products/{product_id}/ccps", response_model=ResponseModel)
async def create_ccp(
    product_id: int,
    ccp_data: CCPCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a CCP for a product"""
    try:
        service = HACCPService(db)
        ccp = service.create_ccp(
            product_id=product_id,
            ccp_data=ccp_data,
            created_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="CCP created successfully",
            data={"id": ccp.id, "name": ccp.ccp_name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating CCP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create CCP"
        )


@router.put("/ccps/{ccp_id}", response_model=ResponseModel)
async def update_ccp(
    ccp_id: int,
    ccp_data: CCPUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a CCP"""
    try:
        service = HACCPService(db)
        ccp = service.update_ccp(
            ccp_id=ccp_id,
            ccp_data=ccp_data,
            updated_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="CCP updated successfully",
            data={"id": ccp.id, "name": ccp.ccp_name}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating CCP {ccp_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update CCP"
        )


@router.delete("/ccps/{ccp_id}", response_model=ResponseModel)
async def delete_ccp(
    ccp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a CCP"""
    try:
        service = HACCPService(db)
        service.delete_ccp(ccp_id, deleted_by=current_user.id)
        
        return ResponseModel(
            success=True,
            message="CCP deleted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HACCPBusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting CCP {ccp_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete CCP"
        )


# ============================================================================
# MONITORING ENDPOINTS
# ============================================================================

@router.post("/ccps/{ccp_id}/monitoring-logs", response_model=ResponseModel)
async def create_monitoring_log(
    ccp_id: int,
    log_data: MonitoringLogCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a monitoring log for a CCP"""
    try:
        service = HACCPService(db)
        log = service.create_monitoring_log(
            ccp_id=ccp_id,
            log_data=log_data,
            created_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data={"id": log.id, "timestamp": log.monitoring_timestamp.isoformat()}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HACCPBusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating monitoring log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monitoring log"
        )


@router.get("/ccps/{ccp_id}/monitoring-logs", response_model=ResponseModel)
async def get_monitoring_logs(
    ccp_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get monitoring logs for a CCP"""
    try:
        service = HACCPService(db)
        logs = service.get_monitoring_logs(
            ccp_id=ccp_id,
            skip=skip,
            limit=limit
        )
        
        return ResponseModel(
            success=True,
            message="Monitoring logs retrieved successfully",
            data=logs
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving monitoring logs for CCP {ccp_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monitoring logs"
        )


# ============================================================================
# VERIFICATION ENDPOINTS
# ============================================================================

@router.post("/ccps/{ccp_id}/verification-logs", response_model=ResponseModel)
async def create_verification_log(
    ccp_id: int,
    log_data: VerificationLogCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a verification log for a CCP"""
    try:
        service = HACCPService(db)
        log = service.create_verification_log(
            ccp_id=ccp_id,
            log_data=log_data,
            created_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Verification log created successfully",
            data={"id": log.id, "timestamp": log.verification_timestamp.isoformat()}
        )
        
    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HACCPBusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating verification log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create verification log"
        )


@router.get("/ccps/{ccp_id}/verification-logs", response_model=ResponseModel)
async def get_verification_logs(
    ccp_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get verification logs for a CCP"""
    try:
        service = HACCPService(db)
        logs = service.get_verification_logs(
            ccp_id=ccp_id,
            skip=skip,
            limit=limit
        )
        
        return ResponseModel(
            success=True,
            message="Verification logs retrieved successfully",
            data=logs
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving verification logs for CCP {ccp_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve verification logs"
        )


# ============================================================================
# DASHBOARD AND ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=ResponseModel)
async def get_haccp_dashboard(
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get HACCP dashboard data"""
    try:
        service = HACCPService(db)
        dashboard_data = service.get_dashboard_data()
        
        return ResponseModel(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )


@router.get("/dashboard/enhanced", response_model=ResponseModel)
async def get_enhanced_haccp_dashboard(
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get enhanced HACCP dashboard with alerts"""
    try:
        service = HACCPService(db)
        dashboard_data = service.get_enhanced_dashboard_data()
        
        return ResponseModel(
            success=True,
            message="Enhanced dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving enhanced dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enhanced dashboard data"
        )


@router.get("/alerts/summary", response_model=ResponseModel)
async def get_alerts_summary(
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get HACCP alerts summary"""
    try:
        service = HACCPService(db)
        alerts = service.get_alerts_summary(days=days)
        
        return ResponseModel(
            success=True,
            message="Alerts summary retrieved successfully",
            data=alerts
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alerts summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts summary"
        )


# ============================================================================
# REPORTING ENDPOINTS
# ============================================================================

@router.post("/products/{product_id}/reports", response_model=ResponseModel)
async def generate_haccp_report(
    product_id: int,
    report_request: HACCPReportRequest,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Generate HACCP report"""
    try:
        service = HACCPService(db)
        report_data = service.generate_haccp_report(
            product_id=product_id,
            report_type=report_request.report_type,
            date_from=report_request.date_from,
            date_to=report_request.date_to
        )
        
        # Generate unique report ID
        report_id = f"haccp_report_{product_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return ResponseModel(
            success=True,
            message="HACCP report generated successfully",
            data={
                "report_id": report_id,
                "report_data": report_data,
                "report_type": report_request.report_type,
                "format": report_request.format,
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating HACCP report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate HACCP report"
        )


# ============================================================================
# FLOWCHART ENDPOINTS
# ============================================================================

@router.get("/products/{product_id}/flowchart", response_model=ResponseModel)
async def get_flowchart_data(
    product_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get flowchart data for a product"""
    try:
        service = HACCPService(db)
        flowchart_data = service.get_flowchart_data(product_id)
        
        return ResponseModel(
            success=True,
            message="Flowchart data retrieved successfully",
            data=flowchart_data
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving flowchart data for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve flowchart data"
        )
