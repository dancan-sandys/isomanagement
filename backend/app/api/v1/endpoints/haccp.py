from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus
)
from app.schemas.common import ResponseModel

router = APIRouter()


# Product Management Endpoints
@router.get("/products")
async def get_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products with HACCP plans"""
    try:
        products = db.query(Product).order_by(desc(Product.updated_at)).all()
        
        items = []
        for product in products:
            # Get creator name
            creator = db.query(User).filter(User.id == product.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            # Get CCP count
            ccp_count = db.query(CCP).filter(CCP.product_id == product.id).count()
            
            items.append({
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "haccp_plan_approved": product.haccp_plan_approved,
                "haccp_plan_version": product.haccp_plan_version,
                "ccp_count": ccp_count,
                "created_by": creator_name,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            })
        
        return ResponseModel(
            success=True,
            message="Products retrieved successfully",
            data={"items": items}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific product with its HACCP details"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get creator name
        creator = db.query(User).filter(User.id == product.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        # Get process flows
        process_flows = db.query(ProcessFlow).filter(
            ProcessFlow.product_id == product_id
        ).order_by(ProcessFlow.step_number).all()
        
        # Get hazards
        hazards = db.query(Hazard).filter(
            Hazard.product_id == product_id
        ).all()
        
        # Get CCPs
        ccps = db.query(CCP).filter(
            CCP.product_id == product_id
        ).all()
        
        return ResponseModel(
            success=True,
            message="Product retrieved successfully",
            data={
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "formulation": product.formulation,
                "allergens": product.allergens,
                "shelf_life_days": product.shelf_life_days,
                "storage_conditions": product.storage_conditions,
                "packaging_type": product.packaging_type,
                "haccp_plan_approved": product.haccp_plan_approved,
                "haccp_plan_version": product.haccp_plan_version,
                "created_by": creator_name,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
                "process_flows": [
                    {
                        "id": flow.id,
                        "step_number": flow.step_number,
                        "step_name": flow.step_name,
                        "description": flow.description,
                        "equipment": flow.equipment,
                        "temperature": flow.temperature,
                        "time_minutes": flow.time_minutes,
                        "ph": flow.ph,
                        "aw": flow.aw,
                        "parameters": flow.parameters,
                    } for flow in process_flows
                ],
                "hazards": [
                    {
                        "id": hazard.id,
                        "process_step_id": hazard.process_step_id,
                        "hazard_type": hazard.hazard_type.value if hazard.hazard_type else None,
                        "hazard_name": hazard.hazard_name,
                        "description": hazard.description,
                        "likelihood": hazard.likelihood,
                        "severity": hazard.severity,
                        "risk_score": hazard.risk_score,
                        "risk_level": hazard.risk_level.value if hazard.risk_level else None,
                        "control_measures": hazard.control_measures,
                        "is_controlled": hazard.is_controlled,
                        "control_effectiveness": hazard.control_effectiveness,
                        "is_ccp": hazard.is_ccp,
                        "ccp_justification": hazard.ccp_justification,
                    } for hazard in hazards
                ],
                "ccps": [
                    {
                        "id": ccp.id,
                        "ccp_number": ccp.ccp_number,
                        "ccp_name": ccp.ccp_name,
                        "description": ccp.description,
                        "status": ccp.status.value if ccp.status else None,
                        "critical_limit_min": ccp.critical_limit_min,
                        "critical_limit_max": ccp.critical_limit_max,
                        "critical_limit_unit": ccp.critical_limit_unit,
                        "critical_limit_description": ccp.critical_limit_description,
                        "monitoring_frequency": ccp.monitoring_frequency,
                        "monitoring_method": ccp.monitoring_method,
                        "corrective_actions": ccp.corrective_actions,
                        "verification_frequency": ccp.verification_frequency,
                        "verification_method": ccp.verification_method,
                    } for ccp in ccps
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product: {str(e)}"
        )


@router.post("/products")
async def create_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    try:
        # Check if product code already exists
        existing_product = db.query(Product).filter(
            Product.product_code == product_data["product_code"]
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists"
            )
        
        product = Product(
            product_code=product_data["product_code"],
            name=product_data["name"],
            description=product_data.get("description"),
            category=product_data.get("category"),
            formulation=product_data.get("formulation"),
            allergens=product_data.get("allergens"),
            shelf_life_days=product_data.get("shelf_life_days"),
            storage_conditions=product_data.get("storage_conditions"),
            packaging_type=product_data.get("packaging_type"),
            created_by=current_user.id
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return ResponseModel(
            success=True,
            message="Product created successfully",
            data={"id": product.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


# Process Flow Management
@router.post("/products/{product_id}/process-flows")
async def create_process_flow(
    product_id: int,
    flow_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a process flow step for a product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        process_flow = ProcessFlow(
            product_id=product_id,
            step_number=flow_data["step_number"],
            step_name=flow_data["step_name"],
            description=flow_data.get("description"),
            equipment=flow_data.get("equipment"),
            temperature=flow_data.get("temperature"),
            time_minutes=flow_data.get("time_minutes"),
            ph=flow_data.get("ph"),
            aw=flow_data.get("aw"),
            parameters=flow_data.get("parameters"),
            created_by=current_user.id
        )
        
        db.add(process_flow)
        db.commit()
        db.refresh(process_flow)
        
        return ResponseModel(
            success=True,
            message="Process flow created successfully",
            data={"id": process_flow.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create process flow: {str(e)}"
        )


# Hazard Management
@router.post("/products/{product_id}/hazards")
async def create_hazard(
    product_id: int,
    hazard_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a hazard for a product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Calculate risk score
        likelihood = hazard_data.get("likelihood", 1)
        severity = hazard_data.get("severity", 1)
        risk_score = likelihood * severity
        
        # Determine risk level
        if risk_score <= 4:
            risk_level = RiskLevel.LOW
        elif risk_score <= 8:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 15:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        hazard = Hazard(
            product_id=product_id,
            process_step_id=hazard_data["process_step_id"],
            hazard_type=HazardType(hazard_data["hazard_type"]),
            hazard_name=hazard_data["hazard_name"],
            description=hazard_data.get("description"),
            likelihood=likelihood,
            severity=severity,
            risk_score=risk_score,
            risk_level=risk_level,
            control_measures=hazard_data.get("control_measures"),
            is_controlled=hazard_data.get("is_controlled", False),
            control_effectiveness=hazard_data.get("control_effectiveness"),
            is_ccp=hazard_data.get("is_ccp", False),
            ccp_justification=hazard_data.get("ccp_justification"),
            created_by=current_user.id
        )
        
        db.add(hazard)
        db.commit()
        db.refresh(hazard)
        
        return ResponseModel(
            success=True,
            message="Hazard created successfully",
            data={"id": hazard.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hazard: {str(e)}"
        )


# CCP Management
@router.post("/products/{product_id}/ccps")
async def create_ccp(
    product_id: int,
    ccp_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a CCP for a product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        ccp = CCP(
            product_id=product_id,
            hazard_id=ccp_data["hazard_id"],
            ccp_number=ccp_data["ccp_number"],
            ccp_name=ccp_data["ccp_name"],
            description=ccp_data.get("description"),
            status=CCPStatus.ACTIVE,
            critical_limit_min=ccp_data.get("critical_limit_min"),
            critical_limit_max=ccp_data.get("critical_limit_max"),
            critical_limit_unit=ccp_data.get("critical_limit_unit"),
            critical_limit_description=ccp_data.get("critical_limit_description"),
            monitoring_frequency=ccp_data.get("monitoring_frequency"),
            monitoring_method=ccp_data.get("monitoring_method"),
            monitoring_responsible=ccp_data.get("monitoring_responsible"),
            monitoring_equipment=ccp_data.get("monitoring_equipment"),
            corrective_actions=ccp_data.get("corrective_actions"),
            verification_frequency=ccp_data.get("verification_frequency"),
            verification_method=ccp_data.get("verification_method"),
            verification_responsible=ccp_data.get("verification_responsible"),
            monitoring_records=ccp_data.get("monitoring_records"),
            verification_records=ccp_data.get("verification_records"),
            created_by=current_user.id
        )
        
        db.add(ccp)
        db.commit()
        db.refresh(ccp)
        
        return ResponseModel(
            success=True,
            message="CCP created successfully",
            data={"id": ccp.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create CCP: {str(e)}"
        )


# CCP Monitoring Logs
@router.post("/ccps/{ccp_id}/monitoring-logs")
async def create_monitoring_log(
    ccp_id: int,
    log_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a monitoring log for a CCP"""
    try:
        # Verify CCP exists
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CCP not found"
            )
        
        # Check if within limits
        measured_value = log_data["measured_value"]
        is_within_limits = True
        
        if ccp.critical_limit_min is not None and measured_value < ccp.critical_limit_min:
            is_within_limits = False
        if ccp.critical_limit_max is not None and measured_value > ccp.critical_limit_max:
            is_within_limits = False
        
        monitoring_log = CCPMonitoringLog(
            ccp_id=ccp_id,
            batch_number=log_data["batch_number"],
            monitoring_time=datetime.utcnow(),
            measured_value=measured_value,
            unit=log_data.get("unit"),
            is_within_limits=is_within_limits,
            additional_parameters=log_data.get("additional_parameters"),
            observations=log_data.get("observations"),
            evidence_files=log_data.get("evidence_files"),
            corrective_action_taken=log_data.get("corrective_action_taken", False),
            corrective_action_description=log_data.get("corrective_action_description"),
            corrective_action_by=log_data.get("corrective_action_by"),
            created_by=current_user.id
        )
        
        db.add(monitoring_log)
        db.commit()
        db.refresh(monitoring_log)
        
        return ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data={"id": monitoring_log.id, "is_within_limits": is_within_limits}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create monitoring log: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/monitoring-logs")
async def get_monitoring_logs(
    ccp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monitoring logs for a CCP"""
    try:
        # Verify CCP exists
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CCP not found"
            )
        
        logs = db.query(CCPMonitoringLog).filter(
            CCPMonitoringLog.ccp_id == ccp_id
        ).order_by(desc(CCPMonitoringLog.monitoring_time)).all()
        
        items = []
        for log in logs:
            # Get creator name
            creator = db.query(User).filter(User.id == log.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            items.append({
                "id": log.id,
                "batch_number": log.batch_number,
                "monitoring_time": log.monitoring_time.isoformat() if log.monitoring_time else None,
                "measured_value": log.measured_value,
                "unit": log.unit,
                "is_within_limits": log.is_within_limits,
                "additional_parameters": log.additional_parameters,
                "observations": log.observations,
                "evidence_files": log.evidence_files,
                "corrective_action_taken": log.corrective_action_taken,
                "corrective_action_description": log.corrective_action_description,
                "created_by": creator_name,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            })
        
        return ResponseModel(
            success=True,
            message="Monitoring logs retrieved successfully",
            data={"items": items}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve monitoring logs: {str(e)}"
        )


# CCP Verification Logs
@router.post("/ccps/{ccp_id}/verification-logs")
async def create_verification_log(
    ccp_id: int,
    log_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a verification log for a CCP"""
    try:
        # Verify CCP exists
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CCP not found"
            )
        
        verification_log = CCPVerificationLog(
            ccp_id=ccp_id,
            verification_date=datetime.utcnow(),
            verification_method=log_data.get("verification_method"),
            verification_result=log_data.get("verification_result"),
            is_compliant=log_data.get("is_compliant", True),
            samples_tested=log_data.get("samples_tested"),
            test_results=log_data.get("test_results"),
            equipment_calibration=log_data.get("equipment_calibration"),
            calibration_date=log_data.get("calibration_date"),
            evidence_files=log_data.get("evidence_files"),
            created_by=current_user.id
        )
        
        db.add(verification_log)
        db.commit()
        db.refresh(verification_log)
        
        return ResponseModel(
            success=True,
            message="Verification log created successfully",
            data={"id": verification_log.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create verification log: {str(e)}"
        )


# HACCP Dashboard Statistics
@router.get("/dashboard")
async def get_haccp_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get HACCP dashboard statistics"""
    try:
        # Get total products
        total_products = db.query(Product).count()
        
        # Get approved HACCP plans
        approved_plans = db.query(Product).filter(Product.haccp_plan_approved == True).count()
        
        # Get total CCPs
        total_ccps = db.query(CCP).count()
        
        # Get active CCPs
        active_ccps = db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).count()
        
        # Get recent monitoring logs
        recent_logs = db.query(CCPMonitoringLog).order_by(
            desc(CCPMonitoringLog.monitoring_time)
        ).limit(5).all()
        
        # Get out-of-spec incidents
        out_of_spec_count = db.query(CCPMonitoringLog).filter(
            CCPMonitoringLog.is_within_limits == False
        ).count()
        
        return ResponseModel(
            success=True,
            message="HACCP dashboard data retrieved successfully",
            data={
                "total_products": total_products,
                "approved_plans": approved_plans,
                "total_ccps": total_ccps,
                "active_ccps": active_ccps,
                "out_of_spec_count": out_of_spec_count,
                "recent_logs": [
                    {
                        "id": log.id,
                        "ccp_name": log.ccp.ccp_name,
                        "batch_number": log.batch_number,
                        "measured_value": log.measured_value,
                        "unit": log.unit,
                        "is_within_limits": log.is_within_limits,
                        "monitoring_time": log.monitoring_time.isoformat() if log.monitoring_time else None,
                    } for log in recent_logs
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        ) 