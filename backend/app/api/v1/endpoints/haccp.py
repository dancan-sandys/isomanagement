from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus
)
from app.schemas.common import ResponseModel
from app.schemas.haccp import (
    ProductCreate, ProductUpdate, ProcessFlowCreate, HazardCreate, CCPCreate,
    MonitoringLogCreate, VerificationLogCreate, DecisionTreeResult, HACCPReportRequest,
    HACCPPlanCreate, HACCPPlanUpdate, HACCPPlanVersionCreate
)
from app.services.haccp_service import HACCPService
from app.utils.audit import audit_event

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
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    try:
        # Check if product code already exists
        existing_product = db.query(Product).filter(
            Product.product_code == product_data.product_code
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists"
            )
        
        product = Product(
            product_code=product_data.product_code,
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            formulation=product_data.formulation,
            allergens=product_data.allergens,
            shelf_life_days=product_data.shelf_life_days,
            storage_conditions=product_data.storage_conditions,
            packaging_type=product_data.packaging_type,
            created_by=current_user.id
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Get creator name
        creator = db.query(User).filter(User.id == product.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        resp = ResponseModel(
            success=True,
            message="Product created successfully",
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
            }
        )
        try:
            audit_event(db, current_user.id, "haccp_product_created", "haccp", str(product.id))
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing product"""
    try:
        # Check if product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update fields
        if product_data.name is not None:
            product.name = product_data.name
        if product_data.description is not None:
            product.description = product_data.description
        if product_data.category is not None:
            product.category = product_data.category
        if product_data.formulation is not None:
            product.formulation = product_data.formulation
        if product_data.allergens is not None:
            product.allergens = product_data.allergens
        if product_data.shelf_life_days is not None:
            product.shelf_life_days = product_data.shelf_life_days
        if product_data.storage_conditions is not None:
            product.storage_conditions = product_data.storage_conditions
        if product_data.packaging_type is not None:
            product.packaging_type = product_data.packaging_type
        if product_data.haccp_plan_approved is not None:
            product.haccp_plan_approved = product_data.haccp_plan_approved
        if product_data.haccp_plan_version is not None:
            product.haccp_plan_version = product_data.haccp_plan_version
        
        db.commit()
        db.refresh(product)
        
        # Get creator name
        creator = db.query(User).filter(User.id == product.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        resp = ResponseModel(
            success=True,
            message="Product updated successfully",
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
            }
        )
        try:
            audit_event(db, current_user.id, "haccp_product_updated", "haccp", str(product.id))
        except Exception:
            pass
        return resp
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update product: {str(e)}")


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product"""
    try:
        # Check if product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check permissions (only QA Manager or System Administrator can delete)
        if current_user.role and current_user.role.name not in ["QA Manager", "System Administrator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete products"
            )
        
        db.delete(product)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_product_deleted", "haccp", str(product_id))
        except Exception:
            pass
        return ResponseModel(
            success=True,
            message="Product deleted successfully",
            data={"id": product_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete product: {str(e)}")


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
        
        resp = ResponseModel(
            success=True,
            message="Process flow created successfully",
            data={"id": process_flow.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_flow_created", "haccp", str(process_flow.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create process flow: {str(e)}"
        )


@router.put("/process-flows/{flow_id}")
async def update_process_flow(
    flow_id: int,
    flow_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a process flow step"""
    try:
        flow = db.query(ProcessFlow).filter(ProcessFlow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process flow not found")

        for field in [
            "step_number",
            "step_name",
            "description",
            "equipment",
            "temperature",
            "time_minutes",
            "ph",
            "aw",
            "parameters",
        ]:
            if field in flow_data:
                setattr(flow, field, flow_data[field])

        db.commit()
        db.refresh(flow)

        try:
            audit_event(db, current_user.id, "haccp_flow_updated", "haccp", str(flow.id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Process flow updated successfully", data={"id": flow.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update process flow: {str(e)}")


@router.delete("/process-flows/{flow_id}")
async def delete_process_flow(
    flow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a process flow step"""
    try:
        flow = db.query(ProcessFlow).filter(ProcessFlow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process flow not found")
        db.delete(flow)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_flow_deleted", "haccp", str(flow_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Process flow deleted successfully", data={"id": flow_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete process flow: {str(e)}")


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
        
        # Validate required fields
        required_fields = ["process_step_id", "hazard_type", "hazard_name"]
        missing = [f for f in required_fields if hazard_data.get(f) in (None, "")]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing)}"
            )

        # Ensure process step exists and belongs to product
        step_id = int(hazard_data.get("process_step_id"))
        step = db.query(ProcessFlow).filter(ProcessFlow.id == step_id, ProcessFlow.product_id == product_id).first()
        if not step:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid process_step_id for this product")

        # Parse hazard type
        try:
            hz_type = HazardType(hazard_data.get("hazard_type"))
        except Exception:
            allowed = ", ".join([t.value for t in HazardType])
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid hazard_type. Allowed: {allowed}")

        # Calculate risk score (coerce to int)
        try:
            likelihood = int(hazard_data.get("likelihood", 1) or 1)
        except Exception:
            likelihood = 1
        try:
            severity = int(hazard_data.get("severity", 1) or 1)
        except Exception:
            severity = 1
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
            process_step_id=step_id,
            hazard_type=hz_type,
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
        
        resp = ResponseModel(
            success=True,
            message="Hazard created successfully",
            data={"id": hazard.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_hazard_created", "haccp", str(hazard.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hazard: {str(e)}"
        )


@router.put("/hazards/{hazard_id}")
async def update_hazard(
    hazard_id: int,
    hazard_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a hazard"""
    try:
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hazard not found")

        # Recalculate risk if likelihood or severity provided
        if "likelihood" in hazard_data or "severity" in hazard_data:
            likelihood = hazard_data.get("likelihood", hazard.likelihood)
            severity = hazard_data.get("severity", hazard.severity)
            risk_score = likelihood * severity
            if risk_score <= 4:
                risk_level = RiskLevel.LOW
            elif risk_score <= 8:
                risk_level = RiskLevel.MEDIUM
            elif risk_score <= 15:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
            hazard.likelihood = likelihood
            hazard.severity = severity
            hazard.risk_score = risk_score
            hazard.risk_level = risk_level

        for field in [
            "process_step_id",
            "hazard_type",
            "hazard_name",
            "description",
            "control_measures",
            "is_controlled",
            "control_effectiveness",
            "is_ccp",
            "ccp_justification",
        ]:
            if field in hazard_data:
                # cast enums where needed
                if field == "hazard_type":
                    setattr(hazard, field, HazardType(hazard_data[field]))
                else:
                    setattr(hazard, field, hazard_data[field])

        db.commit()
        db.refresh(hazard)
        try:
            audit_event(db, current_user.id, "haccp_hazard_updated", "haccp", str(hazard.id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Hazard updated successfully", data={"id": hazard.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update hazard: {str(e)}")


@router.delete("/hazards/{hazard_id}")
async def delete_hazard(
    hazard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a hazard"""
    try:
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hazard not found")
        db.delete(hazard)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_hazard_deleted", "haccp", str(hazard_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Hazard deleted successfully", data={"id": hazard_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete hazard: {str(e)}")


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
        
        resp = ResponseModel(
            success=True,
            message="CCP created successfully",
            data={"id": ccp.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_ccp_created", "haccp", str(ccp.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create CCP: {str(e)}"
        )


@router.put("/ccps/{ccp_id}")
async def update_ccp(
    ccp_id: int,
    ccp_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a CCP"""
    try:
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CCP not found")

        for field in [
            "hazard_id",
            "ccp_number",
            "ccp_name",
            "description",
            "status",
            "critical_limit_min",
            "critical_limit_max",
            "critical_limit_unit",
            "critical_limit_description",
            "monitoring_frequency",
            "monitoring_method",
            "monitoring_responsible",
            "monitoring_equipment",
            "corrective_actions",
            "verification_frequency",
            "verification_method",
            "verification_responsible",
            "monitoring_records",
            "verification_records",
        ]:
            if field in ccp_data:
                if field == "status":
                    setattr(ccp, field, CCPStatus(ccp_data[field]))
                else:
                    setattr(ccp, field, ccp_data[field])

        db.commit()
        db.refresh(ccp)
        try:
            audit_event(db, current_user.id, "haccp_ccp_updated", "haccp", str(ccp.id))
        except Exception:
            pass
        return ResponseModel(success=True, message="CCP updated successfully", data={"id": ccp.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update CCP: {str(e)}")


@router.delete("/ccps/{ccp_id}")
async def delete_ccp(
    ccp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a CCP"""
    try:
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CCP not found")
        db.delete(ccp)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_ccp_deleted", "haccp", str(ccp_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="CCP deleted successfully", data={"id": ccp_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete CCP: {str(e)}")
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
        
        resp = ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data={"id": monitoring_log.id, "is_within_limits": is_within_limits}
        )
        try:
            audit_event(db, current_user.id, "haccp_monitoring_log_created", "haccp", str(monitoring_log.id), {
                "ccp_id": ccp_id,
                "is_within_limits": is_within_limits
            })
        except Exception:
            pass
        return resp
        
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
        
        resp = ResponseModel(
            success=True,
            message="Verification log created successfully",
            data={"id": verification_log.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_verification_log_created", "haccp", str(verification_log.id), {
                "ccp_id": ccp_id
            })
        except Exception:
            pass
        return resp
        
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


# Decision Tree Endpoint
@router.post("/hazards/{hazard_id}/decision-tree")
async def run_decision_tree(
    hazard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run CCP decision tree for a hazard"""
    try:
        haccp_service = HACCPService(db)
        result = haccp_service.run_decision_tree(hazard_id, run_by_user_id=current_user.id)
        
        return ResponseModel(
            success=True,
            message="Decision tree completed successfully",
            data={
                "is_ccp": result.is_ccp,
                "justification": result.justification,
                "steps": [
                    {
                        "question": step.question.value,
                        "answer": step.answer,
                        "explanation": step.explanation
                    } for step in result.steps
                ]
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run decision tree: {str(e)}"
        )


# Flowchart Endpoint
@router.get("/products/{product_id}/flowchart")
async def get_flowchart_data(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flowchart data for a product"""
    try:
        haccp_service = HACCPService(db)
        flowchart_data = haccp_service.get_flowchart_data(product_id)
        
        return ResponseModel(
            success=True,
            message="Flowchart data retrieved successfully",
            data={
                "nodes": [
                    {
                        "id": node.id,
                        "type": node.type,
                        "label": node.label,
                        "x": node.x,
                        "y": node.y,
                        "data": node.data
                    } for node in flowchart_data.nodes
                ],
                "edges": [
                    {
                        "id": edge.id,
                        "source": edge.source,
                        "target": edge.target,
                        "label": edge.label
                    } for edge in flowchart_data.edges
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve flowchart data: {str(e)}"
        )


# --- HACCP Plan endpoints ---

@router.post("/products/{product_id}/plan")
async def create_haccp_plan(
    product_id: int,
    payload: HACCPPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = HACCPService(db)
        plan = service.create_haccp_plan(
            product_id=product_id,
            title=payload.title,
            description=payload.description,
            content=payload.content,
            created_by=current_user.id,
            effective_date=payload.effective_date,
            review_date=payload.review_date,
        )
        return ResponseModel(success=True, message="HACCP plan created", data={"id": plan.id, "version": plan.version, "status": plan.status.value})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")


@router.post("/plans/{plan_id}/versions")
async def create_haccp_plan_version(
    plan_id: int,
    payload: HACCPPlanVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = HACCPService(db)
        version = service.create_haccp_plan_version(
            plan_id=plan_id,
            content=payload.content,
            change_description=payload.change_description,
            change_reason=payload.change_reason,
            created_by=current_user.id,
        )
        return ResponseModel(success=True, message="HACCP plan version created", data={"id": version.id, "version": version.version_number})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plan version: {str(e)}")


@router.post("/plans/{plan_id}/approvals")
async def submit_haccp_plan_for_approval(
    plan_id: int,
    approvals: List[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = HACCPService(db)
        created = service.submit_haccp_plan_for_approval(plan_id, approvals, submitted_by=current_user.id)
        return ResponseModel(success=True, message="Plan submitted for approval", data={"approvals": created})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit plan for approval: {str(e)}")


@router.post("/plans/{plan_id}/approvals/{approval_id}/approve")
async def approve_haccp_plan_step(
    plan_id: int,
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = HACCPService(db)
        remaining = service.approve_haccp_plan_step(plan_id, approval_id, approver_id=current_user.id)
        return ResponseModel(success=True, message="Approval recorded", data={"remaining": remaining})
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve plan: {str(e)}")


@router.post("/plans/{plan_id}/approvals/{approval_id}/reject")
async def reject_haccp_plan_step(
    plan_id: int,
    approval_id: int,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = HACCPService(db)
        service.reject_haccp_plan_step(plan_id, approval_id, approver_id=current_user.id, comments=comments)
        return ResponseModel(success=True, message="Rejection recorded")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject plan: {str(e)}")


# Enhanced Monitoring Log with Alerts
@router.post("/ccps/{ccp_id}/monitoring-logs/enhanced")
async def create_enhanced_monitoring_log(
    ccp_id: int,
    log_data: MonitoringLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a monitoring log with automatic alert generation"""
    try:
        haccp_service = HACCPService(db)
        monitoring_log, alert_created = haccp_service.create_monitoring_log(ccp_id, log_data, current_user.id)
        
        response_data = {
            "id": monitoring_log.id,
            "is_within_limits": monitoring_log.is_within_limits,
            "alert_created": alert_created
        }
        
        if alert_created:
            response_data["alert_message"] = "Out-of-spec alert has been generated and sent to responsible personnel"
        
        return ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data=response_data
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create monitoring log: {str(e)}"
        )


# HACCP Report Generation
@router.post("/products/{product_id}/reports")
async def generate_haccp_report(
    product_id: int,
    report_request: HACCPReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate HACCP report"""
    try:
        haccp_service = HACCPService(db)
        report_data = haccp_service.generate_haccp_report(
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# Enhanced Dashboard with Alerts
@router.get("/dashboard/enhanced")
async def get_enhanced_haccp_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced HACCP dashboard with alerts"""
    try:
        haccp_service = HACCPService(db)
        stats = haccp_service.get_haccp_dashboard_stats()
        
        return ResponseModel(
            success=True,
            message="Enhanced HACCP dashboard data retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve enhanced dashboard data: {str(e)}"
        )


# CCP Alerts Summary
@router.get("/alerts/summary")
async def get_ccp_alerts_summary(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary of CCP alerts"""
    try:
        # Get recent out-of-spec incidents
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_alerts = db.query(CCPMonitoringLog).filter(
            and_(
                CCPMonitoringLog.is_within_limits == False,
                CCPMonitoringLog.created_at >= cutoff_date
            )
        ).order_by(desc(CCPMonitoringLog.created_at)).all()
        
        alerts_summary = []
        for alert in recent_alerts:
            # Get CCP details
            ccp = db.query(CCP).filter(CCP.id == alert.ccp_id).first()
            if ccp:
                alerts_summary.append({
                    "id": alert.id,
                    "ccp_number": ccp.ccp_number,
                    "ccp_name": ccp.ccp_name,
                    "batch_number": alert.batch_number,
                    "measured_value": alert.measured_value,
                    "unit": alert.unit,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                    "corrective_action_taken": alert.corrective_action_taken,
                    "corrective_action_description": alert.corrective_action_description
                })
        
        return ResponseModel(
            success=True,
            message="CCP alerts summary retrieved successfully",
            data={
                "total_alerts": len(alerts_summary),
                "period_days": days,
                "alerts": alerts_summary
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts summary: {str(e)}"


@router.put("/process-flows/{flow_id}")
async def update_process_flow(
    flow_id: int,
    flow_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a process flow step"""
    try:
        flow = db.query(ProcessFlow).filter(ProcessFlow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process flow not found")

        for field in [
            "step_number",
            "step_name",
            "description",
            "equipment",
            "temperature",
            "time_minutes",
            "ph",
            "aw",
            "parameters",
        ]:
            if field in flow_data:
                setattr(flow, field, flow_data[field])

        db.commit()
        db.refresh(flow)

        try:
            audit_event(db, current_user.id, "haccp_flow_updated", "haccp", str(flow.id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Process flow updated successfully", data={"id": flow.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update process flow: {str(e)}")


@router.delete("/process-flows/{flow_id}")
async def delete_process_flow(
    flow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a process flow step"""
    try:
        flow = db.query(ProcessFlow).filter(ProcessFlow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process flow not found")
        db.delete(flow)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_flow_deleted", "haccp", str(flow_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Process flow deleted successfully", data={"id": flow_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete process flow: {str(e)}")


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
        
        # Validate required fields
        required_fields = ["process_step_id", "hazard_type", "hazard_name"]
        missing = [f for f in required_fields if hazard_data.get(f) in (None, "")]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing)}"
            )

        # Ensure process step exists and belongs to product
        step_id = int(hazard_data.get("process_step_id"))
        step = db.query(ProcessFlow).filter(ProcessFlow.id == step_id, ProcessFlow.product_id == product_id).first()
        if not step:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid process_step_id for this product")

        # Parse hazard type
        try:
            hz_type = HazardType(hazard_data.get("hazard_type"))
        except Exception:
            allowed = ", ".join([t.value for t in HazardType])
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid hazard_type. Allowed: {allowed}")

        # Calculate risk score (coerce to int)
        try:
            likelihood = int(hazard_data.get("likelihood", 1) or 1)
        except Exception:
            likelihood = 1
        try:
            severity = int(hazard_data.get("severity", 1) or 1)
        except Exception:
            severity = 1
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
            process_step_id=step_id,
            hazard_type=hz_type,
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
        
        resp = ResponseModel(
            success=True,
            message="Hazard created successfully",
            data={"id": hazard.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_hazard_created", "haccp", str(hazard.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hazard: {str(e)}"
        )


@router.put("/hazards/{hazard_id}")
async def update_hazard(
    hazard_id: int,
    hazard_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a hazard"""
    try:
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hazard not found")

        # Recalculate risk if likelihood or severity provided
        if "likelihood" in hazard_data or "severity" in hazard_data:
            likelihood = hazard_data.get("likelihood", hazard.likelihood)
            severity = hazard_data.get("severity", hazard.severity)
            risk_score = likelihood * severity
            if risk_score <= 4:
                risk_level = RiskLevel.LOW
            elif risk_score <= 8:
                risk_level = RiskLevel.MEDIUM
            elif risk_score <= 15:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
            hazard.likelihood = likelihood
            hazard.severity = severity
            hazard.risk_score = risk_score
            hazard.risk_level = risk_level

        for field in [
            "process_step_id",
            "hazard_type",
            "hazard_name",
            "description",
            "control_measures",
            "is_controlled",
            "control_effectiveness",
            "is_ccp",
            "ccp_justification",
        ]:
            if field in hazard_data:
                # cast enums where needed
                if field == "hazard_type":
                    setattr(hazard, field, HazardType(hazard_data[field]))
                else:
                    setattr(hazard, field, hazard_data[field])

        db.commit()
        db.refresh(hazard)
        try:
            audit_event(db, current_user.id, "haccp_hazard_updated", "haccp", str(hazard.id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Hazard updated successfully", data={"id": hazard.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update hazard: {str(e)}")


@router.delete("/hazards/{hazard_id}")
async def delete_hazard(
    hazard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a hazard"""
    try:
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hazard not found")
        db.delete(hazard)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_hazard_deleted", "haccp", str(hazard_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Hazard deleted successfully", data={"id": hazard_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete hazard: {str(e)}")


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
        
        resp = ResponseModel(
            success=True,
            message="CCP created successfully",
            data={"id": ccp.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_ccp_created", "haccp", str(ccp.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create CCP: {str(e)}"
        )


@router.put("/ccps/{ccp_id}")
async def update_ccp(
    ccp_id: int,
    ccp_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a CCP"""
    try:
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CCP not found")

        for field in [
            "hazard_id",
            "ccp_number",
            "ccp_name",
            "description",
            "status",
            "critical_limit_min",
            "critical_limit_max",
            "critical_limit_unit",
            "critical_limit_description",
            "monitoring_frequency",
            "monitoring_method",
            "monitoring_responsible",
            "monitoring_equipment",
            "corrective_actions",
            "verification_frequency",
            "verification_method",
            "verification_responsible",
            "monitoring_records",
            "verification_records",
        ]:
            if field in ccp_data:
                if field == "status":
                    setattr(ccp, field, CCPStatus(ccp_data[field]))
                else:
                    setattr(ccp, field, ccp_data[field])

        db.commit()
        db.refresh(ccp)
        try:
            audit_event(db, current_user.id, "haccp_ccp_updated", "haccp", str(ccp.id))
        except Exception:
            pass
        return ResponseModel(success=True, message="CCP updated successfully", data={"id": ccp.id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update CCP: {str(e)}")


@router.delete("/ccps/{ccp_id}")
async def delete_ccp(
    ccp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a CCP"""
    try:
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CCP not found")
        db.delete(ccp)
        db.commit()
        try:
            audit_event(db, current_user.id, "haccp_ccp_deleted", "haccp", str(ccp_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="CCP deleted successfully", data={"id": ccp_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete CCP: {str(e)}")
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
        
        resp = ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data={"id": monitoring_log.id, "is_within_limits": is_within_limits}
        )
        try:
            audit_event(db, current_user.id, "haccp_monitoring_log_created", "haccp", str(monitoring_log.id), {
                "ccp_id": ccp_id,
                "is_within_limits": is_within_limits
            })
        except Exception:
            pass
        return resp
        
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
        
        resp = ResponseModel(
            success=True,
            message="Verification log created successfully",
            data={"id": verification_log.id}
        )
        try:
            audit_event(db, current_user.id, "haccp_verification_log_created", "haccp", str(verification_log.id), {
                "ccp_id": ccp_id
            })
        except Exception:
            pass
        return resp
        
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


# Decision Tree Endpoint
@router.post("/hazards/{hazard_id}/decision-tree")
async def run_decision_tree(
    hazard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run CCP decision tree for a hazard"""
    try:
        haccp_service = HACCPService(db)
        result = haccp_service.run_decision_tree(hazard_id)
        
        return ResponseModel(
            success=True,
            message="Decision tree completed successfully",
            data={
                "is_ccp": result.is_ccp,
                "justification": result.justification,
                "steps": [
                    {
                        "question": step.question.value,
                        "answer": step.answer,
                        "explanation": step.explanation
                    } for step in result.steps
                ]
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run decision tree: {str(e)}"
        )


# Flowchart Endpoint
@router.get("/products/{product_id}/flowchart")
async def get_flowchart_data(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flowchart data for a product"""
    try:
        haccp_service = HACCPService(db)
        flowchart_data = haccp_service.get_flowchart_data(product_id)
        
        return ResponseModel(
            success=True,
            message="Flowchart data retrieved successfully",
            data={
                "nodes": [
                    {
                        "id": node.id,
                        "type": node.type,
                        "label": node.label,
                        "x": node.x,
                        "y": node.y,
                        "data": node.data
                    } for node in flowchart_data.nodes
                ],
                "edges": [
                    {
                        "id": edge.id,
                        "source": edge.source,
                        "target": edge.target,
                        "label": edge.label
                    } for edge in flowchart_data.edges
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve flowchart data: {str(e)}"
        )


# Enhanced Monitoring Log with Alerts
@router.post("/ccps/{ccp_id}/monitoring-logs/enhanced")
async def create_enhanced_monitoring_log(
    ccp_id: int,
    log_data: MonitoringLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a monitoring log with automatic alert generation"""
    try:
        haccp_service = HACCPService(db)
        monitoring_log, alert_created = haccp_service.create_monitoring_log(ccp_id, log_data, current_user.id)
        
        response_data = {
            "id": monitoring_log.id,
            "is_within_limits": monitoring_log.is_within_limits,
            "alert_created": alert_created
        }
        
        if alert_created:
            response_data["alert_message"] = "Out-of-spec alert has been generated and sent to responsible personnel"
        
        return ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data=response_data
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create monitoring log: {str(e)}"
        )


# HACCP Report Generation
@router.post("/products/{product_id}/reports")
async def generate_haccp_report(
    product_id: int,
    report_request: HACCPReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate HACCP report"""
    try:
        haccp_service = HACCPService(db)
        report_data = haccp_service.generate_haccp_report(
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# Enhanced Dashboard with Alerts
@router.get("/dashboard/enhanced")
async def get_enhanced_haccp_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced HACCP dashboard with alerts"""
    try:
        haccp_service = HACCPService(db)
        stats = haccp_service.get_haccp_dashboard_stats()
        
        return ResponseModel(
            success=True,
            message="Enhanced HACCP dashboard data retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve enhanced dashboard data: {str(e)}"
        )


# CCP Alerts Summary
@router.get("/alerts/summary")
async def get_ccp_alerts_summary(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary of CCP alerts"""
    try:
        # Get recent out-of-spec incidents
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_alerts = db.query(CCPMonitoringLog).filter(
            and_(
                CCPMonitoringLog.is_within_limits == False,
                CCPMonitoringLog.created_at >= cutoff_date
            )
        ).order_by(desc(CCPMonitoringLog.created_at)).all()
        
        alerts_summary = []
        for alert in recent_alerts:
            # Get CCP details
            ccp = db.query(CCP).filter(CCP.id == alert.ccp_id).first()
            if ccp:
                alerts_summary.append({
                    "id": alert.id,
                    "ccp_number": ccp.ccp_number,
                    "ccp_name": ccp.ccp_name,
                    "batch_number": alert.batch_number,
                    "measured_value": alert.measured_value,
                    "unit": alert.unit,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                    "corrective_action_taken": alert.corrective_action_taken,
                    "corrective_action_description": alert.corrective_action_description
                })
        
        return ResponseModel(
            success=True,
            message="CCP alerts summary retrieved successfully",
            data={
                "total_alerts": len(alerts_summary),
                "period_days": days,
                "alerts": alerts_summary
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts summary: {str(e)}"
        ) 