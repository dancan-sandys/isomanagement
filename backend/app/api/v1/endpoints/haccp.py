import json
from json import JSONDecodeError
from typing import List, Optional, Set
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, text
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_permission_dependency
from app.models.user import User
from app.models.haccp import (
    Product, ProcessFlow, Hazard, HazardReview, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus, RiskThreshold, ProductRiskConfig, DecisionTree,
    ContactSurface, product_contact_surface_association
)
from app.models.oprp import OPRP, OPRPMonitoringLog, OPRPVerificationLog
from app.models.rbac import Module, PermissionType
from app.services.rbac_service import RBACService
from app.services.haccp_access import (
    get_user_haccp_assignments,
    is_ccp_monitoring_responsible,
    is_ccp_verification_responsible,
)
from app.schemas.common import ResponseModel
from app.schemas.haccp import (
    ProductCreate, ProductUpdate, ProductResponse, ProcessFlowCreate, ProcessFlowUpdate, ProcessFlowResponse,
    HazardCreate, HazardUpdate, HazardResponse, CCPCreate, CCPUpdate, CCPResponse,
    MonitoringLogCreate, MonitoringLogVerificationUpdate, MonitoringLogResponse,
    VerificationLogCreate, VerificationLogResponse,
    HACCPPlanCreate, HACCPPlanUpdate, HACCPPlanResponse, HACCPPlanVersionCreate, HACCPPlanVersionResponse,
    HACCPPlanApprovalCreate, HACCPPlanApprovalResponse, ProductRiskConfigCreate, ProductRiskConfigUpdate, ProductRiskConfigResponse,
    DecisionTreeCreate, DecisionTreeUpdate, DecisionTreeResponse, DecisionTreeQuestionResponse,
    RiskThresholdCreate, RiskThresholdUpdate, RiskThresholdResponse,
    HazardReviewCreate, HazardReviewUpdate, HazardReviewResponse,
    HACCPReportRequest, ValidationEvidence,
    ContactSurfaceCreate, ContactSurfaceResponse
)
from app.services.haccp_service import HACCPService, HACCPValidationError
from sqlalchemy.exc import StatementError
from app.services.storage_service import StorageService
from app.utils.audit import audit_event

router = APIRouter()

PRIVILEGED_HACCP_ROLES = {
    "System Administrator",
    "QA Manager",
    "QA Specialist",
    "Production Manager",
    "Compliance Officer",
}


def get_user_role_name(user: Optional[User]) -> Optional[str]:
    if not user:
        return None
    try:
        if getattr(user, "role", None):
            if getattr(user.role, "display_name", None):
                return user.role.display_name
            if getattr(user.role, "name", None):
                return user.role.name
    except Exception:
        pass
    return None


def is_privileged_haccp_user(user: Optional[User]) -> bool:
    role_name = get_user_role_name(user)
    if not role_name:
        return False
    return role_name in PRIVILEGED_HACCP_ROLES


def serialize_contact_surface(surface: ContactSurface) -> dict:
    if not surface:
        return {}
    return {
        "id": surface.id,
        "name": surface.name,
        "composition": surface.composition,
        "description": surface.description,
        "source": surface.source,
        "provenance": surface.provenance,
        "point_of_contact": surface.point_of_contact,
        "material": surface.material,
        "main_processing_steps": surface.main_processing_steps,
        "packaging_material": surface.packaging_material,
        "storage_conditions": surface.storage_conditions,
        "shelf_life": surface.shelf_life,
        "possible_inherent_hazards": surface.possible_inherent_hazards,
        "fs_acceptance_criteria": surface.fs_acceptance_criteria,
        "created_by": surface.created_by,
        "created_at": surface.created_at.isoformat() if surface.created_at else None,
        "updated_at": surface.updated_at.isoformat() if surface.updated_at else None,
    }


def get_assigned_product_ids(db: Session, user_id: int) -> Set[int]:
    if not user_id:
        return set()
    try:
        results = (
            db.query(CCP.product_id)
            .filter(
                or_(
                    CCP.monitoring_responsible == user_id,
                    CCP.verification_responsible == user_id,
                )
            )
            .distinct()
            .all()
        )
        return {row[0] for row in results if row[0] is not None}
    except Exception:
        return set()


def require_haccp_view_dependency(allow_assignment: bool = False):
    """
    FastAPI dependency that allows users with HACCP view permission or
    (optionally) users who are assigned to CCPs to access product-level data.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        rbac_service = RBACService(db)
        if rbac_service.has_permission(current_user.id, Module.HACCP, PermissionType.VIEW):
            return current_user

        if allow_assignment:
            assignments = get_user_haccp_assignments(db, current_user.id)
            if assignments["product_ids"]:
                return current_user

        error_detail = {
            "error": "Insufficient permissions",
            "required_permission": "haccp:view",
            "user_id": current_user.id,
            "user_username": current_user.username,
            "allow_assignment": allow_assignment,
        }
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail,
        )

    return dependency


def require_haccp_monitoring_dependency(
    ccp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Dependency that allows HACCP create/update permissions or the assigned
    monitoring responsible user to record monitoring logs.
    """
    rbac_service = RBACService(db)
    if any(
        rbac_service.has_permission(current_user.id, Module.HACCP, action)
        for action in (PermissionType.CREATE, PermissionType.UPDATE)
    ):
        return current_user

    if is_ccp_monitoring_responsible(db, current_user.id, ccp_id):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "Insufficient permissions",
            "required": "haccp:create or haccp:update or CCP monitoring assignment",
            "ccp_id": ccp_id,
            "user_id": current_user.id,
        },
    )


def require_haccp_verification_dependency(
    ccp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Dependency that allows HACCP update permission or the assigned
    verification responsible user to verify monitoring logs.
    """
    rbac_service = RBACService(db)
    if rbac_service.has_permission(current_user.id, Module.HACCP, PermissionType.UPDATE):
        return current_user

    if is_ccp_verification_responsible(db, current_user.id, ccp_id):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "Insufficient permissions",
            "required": "haccp:update or CCP verification assignment",
            "ccp_id": ccp_id,
            "user_id": current_user.id,
        },
    )


def require_haccp_view_or_assignment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    module = Module.HACCP
    action = PermissionType.VIEW
    rbac_service = RBACService(db)

    if rbac_service.has_permission(current_user.id, module, action):
        return current_user

    assigned_product_ids = get_assigned_product_ids(db, current_user.id)
    if assigned_product_ids:
        return current_user

    user_permissions = rbac_service.get_user_permissions(current_user.id)
    user_modules = rbac_service.get_user_modules(current_user.id)

    error_detail = {
        "error": "Insufficient permissions",
        "required_permission": f"{module.value}:{action.value}",
        "required_module": module.value,
        "required_action": action.value,
        "user_id": current_user.id,
        "user_username": current_user.username,
        "user_has_module_access": module in user_modules,
        "user_permissions_count": len(user_permissions),
        "available_modules": [m.value for m in user_modules],
        "available_permissions": [f"{p.module}:{p.action}" for p in user_permissions[:10]],
    }

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=error_detail
    )


# Contact Surface Endpoints
@router.get("/contact-surfaces")
async def list_contact_surfaces(
    q: Optional[str] = Query(None, description="Search term for contact surface name or material"),
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
    db: Session = Depends(get_db)
):
    """List stored contact surfaces for reuse in product records."""
    query = db.query(ContactSurface)
    if q:
        like_query = f"%{q.strip()}%"
        query = query.filter(
            or_(
                ContactSurface.name.ilike(like_query),
                ContactSurface.material.ilike(like_query),
                ContactSurface.point_of_contact.ilike(like_query),
            )
        )
    surfaces = query.order_by(ContactSurface.name.asc()).all()

    return ResponseModel(
        success=True,
        message="Contact surfaces retrieved successfully",
        data={
            "items": [serialize_contact_surface(surface) for surface in surfaces],
            "count": len(surfaces),
        },
    )


@router.post("/contact-surfaces")
async def create_contact_surface(
    surface_data: ContactSurfaceCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a new reusable contact surface definition."""
    try:
        surface = ContactSurface(
            name=surface_data.name,
            composition=surface_data.composition,
            description=surface_data.description,
            source=surface_data.source,
            provenance=surface_data.provenance,
            point_of_contact=surface_data.point_of_contact,
            material=surface_data.material,
            main_processing_steps=surface_data.main_processing_steps,
            packaging_material=surface_data.packaging_material,
            storage_conditions=surface_data.storage_conditions,
            shelf_life=surface_data.shelf_life,
            possible_inherent_hazards=surface_data.possible_inherent_hazards,
            fs_acceptance_criteria=surface_data.fs_acceptance_criteria,
            created_by=current_user.id,
        )
        db.add(surface)
        db.commit()
        db.refresh(surface)

        return ResponseModel(
            success=True,
            message="Contact surface created successfully",
            data=serialize_contact_surface(surface),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contact surface: {str(e)}",
        )


# Product Management Endpoints
@router.get("/products")
async def get_products(
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
    db: Session = Depends(get_db)
):
    """Get all products with HACCP plans"""
    try:
        is_privileged_user = is_privileged_haccp_user(current_user)
        assigned_product_ids = get_assigned_product_ids(db, current_user.id) if current_user else set()

        product_rows = db.execute(
            text(
                """
                SELECT
                    id,
                    product_code,
                    name,
                    description,
                    composition,
                    high_risk_ingredients,
                    physical_chemical_biological_description,
                    main_processing_steps,
                    distribution_serving_methods,
                    consumer_groups,
                    storage_conditions,
                    shelf_life_days,
                    packaging_type,
                    inherent_hazards,
                    fs_acceptance_criteria,
                    law_regulation_requirement,
                    haccp_plan_approved,
                    haccp_plan_version,
                    created_by,
                    created_at,
                    updated_at
                FROM products
                ORDER BY COALESCE(updated_at, created_at) DESC, id DESC
                """
            )
        ).mappings().all()

        assigned_only = False
        if not is_privileged_user:
            if assigned_product_ids:
                product_rows = [row for row in product_rows if row["id"] in assigned_product_ids]
                assigned_only = True
            else:
                product_rows = []
                assigned_only = True

        contact_surface_map = defaultdict(list)
        product_ids = [row["id"] for row in product_rows]
        if product_ids:
            surface_rows = (
                db.query(
                    product_contact_surface_association.c.product_id,
                    ContactSurface
                )
                .join(
                    ContactSurface,
                    ContactSurface.id == product_contact_surface_association.c.contact_surface_id,
                )
                .filter(product_contact_surface_association.c.product_id.in_(product_ids))
                .order_by(product_contact_surface_association.c.product_id, ContactSurface.name)
                .all()
            )
            for product_id, surface in surface_rows:
                contact_surface_map[product_id].append(serialize_contact_surface(surface))

        items = []
        for product in product_rows:
            product_id = product["id"]
            try:
                composition_data = product["composition"]
            except (StatementError, JSONDecodeError, ValueError, TypeError) as exc:
                print(f"DEBUG: Failed to decode product composition for product_id={product_id}: {exc}")
                composition_data = None
            if isinstance(composition_data, (bytes, bytearray)):
                composition_data = composition_data.decode("utf-8", errors="ignore").strip()
            if isinstance(composition_data, str):
                composition_data = composition_data.strip()
                if composition_data:
                    try:
                        composition_data = json.loads(composition_data)
                    except (JSONDecodeError, ValueError) as exc:
                        print(f"DEBUG: Invalid JSON string in product composition for product_id={product_id}: {exc}")
                        composition_data = None
            composition = composition_data or []

            try:
                high_risk_data = product["high_risk_ingredients"]
            except (StatementError, JSONDecodeError, ValueError, TypeError) as exc:
                print(f"DEBUG: Failed to decode high-risk ingredient for product_id={product_id}: {exc}")
                high_risk_data = None
            if isinstance(high_risk_data, (bytes, bytearray)):
                high_risk_data = high_risk_data.decode("utf-8", errors="ignore").strip()
            if isinstance(high_risk_data, str):
                high_risk_str = high_risk_data.strip()
                if high_risk_str:
                    try:
                        high_risk_data = json.loads(high_risk_str)
                    except (JSONDecodeError, ValueError) as exc:
                        print(f"DEBUG: Invalid JSON string in high-risk ingredient for product_id={product_id}: {exc}")
                        high_risk_data = None

            # Get creator name
            created_by = product["created_by"]
            if isinstance(created_by, str) and created_by.isdigit():
                created_by_lookup = int(created_by)
            else:
                created_by_lookup = created_by

            creator = db.query(User).filter(User.id == created_by_lookup).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            # Get CCP count
            ccp_count = db.query(CCP).filter(CCP.product_id == product_id).count()

            created_at_value = product["created_at"]
            if isinstance(created_at_value, datetime):
                created_at_str = created_at_value.isoformat()
            elif created_at_value:
                created_at_str = str(created_at_value)
            else:
                created_at_str = None

            updated_at_value = product["updated_at"]
            if isinstance(updated_at_value, datetime):
                updated_at_str = updated_at_value.isoformat()
            elif updated_at_value:
                updated_at_str = str(updated_at_value)
            else:
                updated_at_str = None
            
            items.append({
                "id": product_id,
                "product_code": product["product_code"],
                "name": product["name"],
                "description": product["description"],
                "composition": composition,
                "high_risk_ingredients": high_risk_data,
                "physical_chemical_biological_description": product["physical_chemical_biological_description"],
                "main_processing_steps": product["main_processing_steps"],
                "distribution_serving_methods": product["distribution_serving_methods"],
                "contact_surfaces": contact_surface_map.get(product_id, []),
                "consumer_groups": product["consumer_groups"],
                "storage_conditions": product["storage_conditions"],
                "shelf_life_days": product["shelf_life_days"],
                "packaging_type": product["packaging_type"],
                "inherent_hazards": product["inherent_hazards"],
                "fs_acceptance_criteria": product["fs_acceptance_criteria"],
                "law_regulation_requirement": product["law_regulation_requirement"],
                "haccp_plan_approved": product["haccp_plan_approved"],
                "haccp_plan_version": product["haccp_plan_version"],
                "ccp_count": ccp_count,
                "created_by": creator_name,
                "created_at": created_at_str,
                "updated_at": updated_at_str,
            })
        
        return ResponseModel(
            success=True,
            message="Products retrieved successfully",
            data={
                "items": items,
                "assigned_only": assigned_only
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
    db: Session = Depends(get_db)
):
    """Get a product with its process flows, hazards, and CCPs"""
    try:
        is_privileged_user = is_privileged_haccp_user(current_user)
        if not is_privileged_user:
            assigned_product_ids = get_assigned_product_ids(db, current_user.id)
            if product_id not in assigned_product_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to access this product."
                )

        def safe_json_load(value):
            if value is None:
                return None
            if isinstance(value, (bytes, bytearray)):
                value = value.decode("utf-8", errors="ignore")
            if isinstance(value, str):
                stripped = value.strip()
                if not stripped:
                    return None
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    print(f"DEBUG: Malformed JSON encountered: {stripped}")
                    return None
            return value

        # Fetch product using raw SQL to avoid json deserializer being strict
        product_row = db.execute(
            text(
                """
                SELECT *
                FROM products
                WHERE id = :pid
                """
            ),
            {"pid": product_id}
        ).mappings().first()

        if not product_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        composition_data = safe_json_load(product_row.get("composition")) or []
        if not isinstance(composition_data, list):
            composition_data = []
        high_risk_data = safe_json_load(product_row.get("high_risk_ingredients"))
        if high_risk_data is not None and not isinstance(high_risk_data, dict):
            high_risk_data = None

        created_at_value = product_row.get("created_at")
        updated_at_value = product_row.get("updated_at")
        product_code = product_row.get("product_code")
        product_name = product_row.get("name")
        product_description = product_row.get("description")
        physical_chemical_bio = product_row.get("physical_chemical_biological_description")
        main_processing_steps = product_row.get("main_processing_steps")
        distribution_serving_methods = product_row.get("distribution_serving_methods")
        consumer_groups = product_row.get("consumer_groups")
        storage_conditions = product_row.get("storage_conditions")
        shelf_life_days = product_row.get("shelf_life_days")
        packaging_type = product_row.get("packaging_type")
        inherent_hazards = product_row.get("inherent_hazards")
        fs_acceptance_criteria = product_row.get("fs_acceptance_criteria")
        law_regulation_requirement = product_row.get("law_regulation_requirement")
        haccp_plan_approved = product_row.get("haccp_plan_approved")
        haccp_plan_version = product_row.get("haccp_plan_version")

        contact_surfaces = (
            db.query(ContactSurface)
            .join(
                product_contact_surface_association,
                ContactSurface.id == product_contact_surface_association.c.contact_surface_id,
            )
            .filter(product_contact_surface_association.c.product_id == product_id)
            .order_by(ContactSurface.name)
            .all()
        )
        contact_surfaces_data = [serialize_contact_surface(surface) for surface in contact_surfaces]
        
        created_by_value = product_row.get("created_by")
        if isinstance(created_by_value, str) and created_by_value.isdigit():
            created_by_lookup = int(created_by_value)
        else:
            created_by_lookup = created_by_value
        creator = db.query(User).filter(User.id == created_by_lookup).first()
        creator_name = creator.full_name if creator else "Unknown"
        
        # Get risk configuration
        risk_config = db.query(ProductRiskConfig).filter(ProductRiskConfig.product_id == product_id).first()
        risk_config_data = None
        if risk_config:
            risk_config_data = {
                "calculation_method": risk_config.calculation_method,
                "likelihood_scale": risk_config.likelihood_scale,
                "severity_scale": risk_config.severity_scale,
                "risk_thresholds": {
                    "low_threshold": risk_config.low_threshold,
                    "medium_threshold": risk_config.medium_threshold,
                    "high_threshold": risk_config.high_threshold,
                }
            }
        
        # Get process flows
        process_flows = db.query(ProcessFlow).filter(
            ProcessFlow.product_id == product_id
        ).order_by(ProcessFlow.step_number).all()
        
        # Get hazards (raw SQL to tolerate legacy enum/string values)
        try:
            hazard_rows = db.execute(
                text(
                    """
                    SELECT id, process_step_id, hazard_type, hazard_name, description,
                           consequences,
                           prp_reference_ids, reference_documents,
                           likelihood, severity, risk_score, risk_level, control_measures,
                           is_controlled, control_effectiveness, is_ccp, ccp_justification,
                           risk_strategy, risk_strategy_justification, subsequent_step,
                           created_at, updated_at
                    FROM hazards
                    WHERE product_id = :pid
                    """
                ),
                {"pid": product_id}
            ).fetchall()
        except Exception as e:
            print(f"DEBUG: Error in hazards query: {e}")
            hazard_rows = []
        
        # Get CCPs (raw SQL to avoid enum coercion issues)
        try:
            ccp_rows = db.execute(
                text(
                    """
                    SELECT id, hazard_id, ccp_number, ccp_name, description, status,
                           critical_limit_min, critical_limit_max, critical_limit_unit,
                           critical_limit_description, monitoring_frequency, monitoring_method,
                           monitoring_responsible, monitoring_equipment, corrective_actions,
                           verification_frequency, verification_method, verification_responsible
                    FROM ccps
                    WHERE product_id = :pid
                    """
                ),
                {"pid": product_id}
            ).fetchall()
        except Exception as e:
            print(f"DEBUG: Error in CCPs query: {e}")
            ccp_rows = []
        
        # Get OPRPs (raw SQL to avoid enum coercion issues)
        try:
            oprp_rows = db.execute(
                text(
                    """
                    SELECT id, product_id, hazard_id, oprp_number, oprp_name, description, status,
                           operational_limits, operational_limit_min, operational_limit_max,
                           operational_limit_unit, operational_limit_description,
                           monitoring_frequency, monitoring_method, monitoring_responsible,
                           monitoring_equipment, corrective_actions,
                           verification_frequency, verification_method, verification_responsible,
                           justification
                    FROM oprps
                    WHERE product_id = :pid
                    """
                ),
                {"pid": product_id}
            ).fetchall()
        except Exception as e:
            print(f"DEBUG: Error in OPRPs query: {e}")
            oprp_rows = []
        
        # Process hazards with safe mapping
        try:
            hazards_data = []
            for row in hazard_rows:
                mapping = getattr(row, "_mapping", {})
                
                # Handle datetime serialization safely
                created_at = mapping.get("created_at")
                if created_at and hasattr(created_at, 'isoformat'):
                    created_at = created_at.isoformat()
                
                updated_at = mapping.get("updated_at")
                if updated_at and hasattr(updated_at, 'isoformat'):
                    updated_at = updated_at.isoformat()
                
                hazard_data = {
                    "id": mapping.get("id"),
                    "process_step_id": mapping.get("process_step_id"),
                    "hazard_type": mapping.get("hazard_type"),
                    "hazard_name": mapping.get("hazard_name"),
                    "description": mapping.get("description"),
                    "consequences": mapping.get("consequences"),  # Already uses COALESCE in SQL
                    "prp_reference_ids": mapping.get("prp_reference_ids") if mapping.get("prp_reference_ids") is not None else [],
                    "reference_documents": mapping.get("reference_documents") if mapping.get("reference_documents") is not None else [],
                    "likelihood": mapping.get("likelihood"),
                    "severity": mapping.get("severity"),
                    "risk_score": mapping.get("risk_score"),
                    "risk_level": mapping.get("risk_level"),
                    "control_measures": mapping.get("control_measures"),
                    "is_controlled": mapping.get("is_controlled"),
                    "control_effectiveness": mapping.get("control_effectiveness"),
                    "is_ccp": mapping.get("is_ccp"),
                    "ccp_justification": mapping.get("ccp_justification"),
                    "opprp_justification": None,  # Column doesn't exist yet in database
                    "risk_strategy": mapping.get("risk_strategy"),
                    "risk_strategy_justification": mapping.get("risk_strategy_justification"),
                    "subsequent_step": mapping.get("subsequent_step"),
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
                hazards_data.append(hazard_data)
        except Exception as e:
            print(f"DEBUG: Error processing hazards data: {e}")
            hazards_data = []
        
        # Process CCPs with safe mapping
        try:
            ccps_data = []
            for row in ccp_rows:
                mapping = getattr(row, "_mapping", {})
                ccp_data = {
                    "id": mapping.get("id"),
                    "hazard_id": mapping.get("hazard_id"),
                    "ccp_number": mapping.get("ccp_number"),
                    "ccp_name": mapping.get("ccp_name"),
                    "description": mapping.get("description"),
                    "status": mapping.get("status"),
                    "critical_limit_min": mapping.get("critical_limit_min"),
                    "critical_limit_max": mapping.get("critical_limit_max"),
                    "critical_limit_unit": mapping.get("critical_limit_unit"),
                    "critical_limit_description": mapping.get("critical_limit_description"),
                    "monitoring_frequency": mapping.get("monitoring_frequency"),
                    "monitoring_method": mapping.get("monitoring_method"),
                    "monitoring_responsible": mapping.get("monitoring_responsible"),
                    "monitoring_equipment": mapping.get("monitoring_equipment"),
                    "corrective_actions": mapping.get("corrective_actions"),
                    "verification_frequency": mapping.get("verification_frequency"),
                    "verification_method": mapping.get("verification_method"),
                    "verification_responsible": mapping.get("verification_responsible"),
                }
                ccps_data.append(ccp_data)
        except Exception as e:
            print(f"DEBUG: Error processing CCPs data: {e}")
            ccps_data = []
        
        # Process OPRPs with safe mapping
        try:
            oprps_data = []
            for row in oprp_rows:
                mapping = getattr(row, "_mapping", {})
                oprp_data = {
                    "id": mapping.get("id"),
                    "product_id": mapping.get("product_id"),
                    "hazard_id": mapping.get("hazard_id"),
                    "oprp_number": mapping.get("oprp_number"),
                    "oprp_name": mapping.get("oprp_name"),
                    "description": mapping.get("description"),
                    "status": mapping.get("status"),
                    "operational_limits": mapping.get("operational_limits"),
                    "operational_limit_min": mapping.get("operational_limit_min"),
                    "operational_limit_max": mapping.get("operational_limit_max"),
                    "operational_limit_unit": mapping.get("operational_limit_unit"),
                    "operational_limit_description": mapping.get("operational_limit_description"),
                    "monitoring_frequency": mapping.get("monitoring_frequency"),
                    "monitoring_method": mapping.get("monitoring_method"),
                    "monitoring_responsible": mapping.get("monitoring_responsible"),
                    "monitoring_equipment": mapping.get("monitoring_equipment"),
                    "corrective_actions": mapping.get("corrective_actions"),
                    "verification_frequency": mapping.get("verification_frequency"),
                    "verification_method": mapping.get("verification_method"),
                    "verification_responsible": mapping.get("verification_responsible"),
                    "justification": mapping.get("justification"),
                }
                oprps_data.append(oprp_data)
        except Exception as e:
            print(f"DEBUG: Error processing OPRPs data: {e}")
            oprps_data = []
        
        def serialize_dt(value):
            if value is None:
                return None
            if hasattr(value, "isoformat"):
                return value.isoformat()
            return str(value)

        def to_bool(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return value != 0
            if isinstance(value, str):
                return value.strip().lower() in {"true", "1", "yes", "y"}
            return bool(value)

        return ResponseModel(
            success=True,
            message="Product retrieved successfully",
            data={
                "id": product_row.get("id"),
                "product_code": product_code,
                "name": product_name,
                "description": product_description,
                "composition": composition_data,
                "high_risk_ingredients": high_risk_data,
                "physical_chemical_biological_description": physical_chemical_bio,
                "main_processing_steps": main_processing_steps,
                "distribution_serving_methods": distribution_serving_methods,
                "contact_surfaces": contact_surfaces_data,
                "consumer_groups": consumer_groups,
                "storage_conditions": storage_conditions,
                "shelf_life_days": shelf_life_days,
                "packaging_type": packaging_type,
                "inherent_hazards": inherent_hazards,
                "fs_acceptance_criteria": fs_acceptance_criteria,
                "law_regulation_requirement": law_regulation_requirement,
                "haccp_plan_approved": to_bool(haccp_plan_approved),
                "haccp_plan_version": haccp_plan_version,
                "risk_config": risk_config_data,
                "created_by": creator_name,
                "created_at": serialize_dt(created_at_value),
                "updated_at": serialize_dt(updated_at_value),
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
                "hazards": hazards_data,
                "ccps": ccps_data,
                "oprps": oprps_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in get_product: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product: {str(e)}"
        )


@router.post("/products")
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

        creator = db.query(User).filter(User.id == product.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        contact_surfaces_data = [serialize_contact_surface(surface) for surface in product.contact_surfaces]

        resp = ResponseModel(
            success=True,
            message="Product created successfully",
            data={
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "description": product.description,
                "composition": product.composition or [],
                "high_risk_ingredients": product.high_risk_ingredients,
                "physical_chemical_biological_description": product.physical_chemical_biological_description,
                "main_processing_steps": product.main_processing_steps,
                "distribution_serving_methods": product.distribution_serving_methods,
                "contact_surfaces": contact_surfaces_data,
                "consumer_groups": product.consumer_groups,
                "storage_conditions": product.storage_conditions,
                "shelf_life_days": product.shelf_life_days,
                "packaging_type": product.packaging_type,
                "inherent_hazards": product.inherent_hazards,
                "fs_acceptance_criteria": product.fs_acceptance_criteria,
                "law_regulation_requirement": product.law_regulation_requirement,
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

    except HACCPValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a product"""
    try:
        service = HACCPService(db)
        product = service.update_product(
            product_id=product_id,
            product_data=product_data,
            updated_by=current_user.id
        )

        creator = db.query(User).filter(User.id == product.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        contact_surfaces_data = [serialize_contact_surface(surface) for surface in product.contact_surfaces]

        resp = ResponseModel(
            success=True,
            message="Product updated successfully",
            data={
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "description": product.description,
                "composition": product.composition or [],
                "high_risk_ingredients": product.high_risk_ingredients,
                "physical_chemical_biological_description": product.physical_chemical_biological_description,
                "main_processing_steps": product.main_processing_steps,
                "distribution_serving_methods": product.distribution_serving_methods,
                "contact_surfaces": contact_surfaces_data,
                "consumer_groups": product.consumer_groups,
                "storage_conditions": product.storage_conditions,
                "shelf_life_days": product.shelf_life_days,
                "packaging_type": product.packaging_type,
                "inherent_hazards": product.inherent_hazards,
                "fs_acceptance_criteria": product.fs_acceptance_criteria,
                "law_regulation_requirement": product.law_regulation_requirement,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a product and its dependent HACCP records safely."""
    try:
        # Ensure product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Permission check
        if current_user.role and current_user.role.name not in ["QA Manager", "System Administrator"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to delete products")

        service = HACCPService(db)
        service.delete_product(product_id, deleted_by=current_user.id)

        try:
            audit_event(db, current_user.id, "haccp_product_deleted", "haccp", str(product_id))
        except Exception:
            pass

        return ResponseModel(success=True, message="Product deleted successfully", data={"id": product_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete product: {str(e)}")


# Process Flow Management
@router.post("/products/{product_id}/process-flows")
async def create_process_flow(
    product_id: int,
    flow_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
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
        
        # Validate required fields
        if not flow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body cannot be empty. Required fields: step_number, step_name"
            )
        
        if "step_number" not in flow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: step_number"
            )
        
        if "step_name" not in flow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: step_name"
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
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
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
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
    hazard_data: HazardCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
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
        
        # Ensure process step exists and belongs to product
        step = db.query(ProcessFlow).filter(
            ProcessFlow.id == hazard_data.process_step_id, 
            ProcessFlow.product_id == product_id
        ).first()
        if not step:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid process_step_id for this product"
            )

        # Use the service layer for business logic (now handles CCP/OPRP creation)
        haccp_service = HACCPService(db)
        hazard = haccp_service.create_hazard(product_id, hazard_data, current_user.id)
        
        # Check if CCP or OPRP was created
        message = "Hazard created successfully"
        if hazard.risk_strategy == "ccp":
            ccp = db.query(CCP).filter(CCP.hazard_id == hazard.id).first()
            if ccp:
                message += f" and CCP ({ccp.ccp_number}) created"
        elif hazard.risk_strategy == "opprp":
            oprp = db.query(OPRP).filter(OPRP.hazard_id == hazard.id).first()
            if oprp:
                message += f" and OPRP ({oprp.oprp_number}) created"
        
        resp = ResponseModel(
            success=True,
            message=message,
            data={"id": hazard.id, "risk_strategy": hazard.risk_strategy}
        )
        try:
            audit_event(db, current_user.id, "haccp_hazard_created", "haccp", str(hazard.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a hazard"""
    try:
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hazard not found")

        # Recalculate risk if likelihood or severity provided (coerce to int safely)
        if "likelihood" in hazard_data or "severity" in hazard_data:
            try:
                likelihood = int(hazard_data.get("likelihood", hazard.likelihood))
            except Exception:
                likelihood = int(hazard.likelihood or 1)
            try:
                severity = int(hazard_data.get("severity", hazard.severity))
            except Exception:
                severity = int(hazard.severity or 1)
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
                    val = hazard_data[field]
                    if field in ("control_effectiveness", "process_step_id") and val is not None:
                        try:
                            val = int(val)
                        except Exception:
                            pass
                    setattr(hazard, field, val)

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
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a hazard and all related records"""
    try:
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hazard not found")
        
        # Delete related OPRPs first (to avoid foreign key constraint violation)
        oprps = db.query(OPRP).filter(OPRP.hazard_id == hazard_id).all()
        for oprp in oprps:
            # Delete OPRP monitoring and verification logs
            db.query(OPRPMonitoringLog).filter(OPRPMonitoringLog.oprp_id == oprp.id).delete(synchronize_session=False)
            db.query(OPRPVerificationLog).filter(OPRPVerificationLog.oprp_id == oprp.id).delete(synchronize_session=False)
            db.delete(oprp)
        
        # Delete decision tree records
        db.query(DecisionTree).filter(DecisionTree.hazard_id == hazard_id).delete(synchronize_session=False)
        
        # Delete hazard reviews if they exist
        try:
            db.query(HazardReview).filter(HazardReview.hazard_id == hazard_id).delete(synchronize_session=False)
        except Exception:
            pass
        
        # Finally delete the hazard
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
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete hazard: {str(e)}")


# CCP Management
@router.post("/products/{product_id}/ccps")
async def create_ccp(
    product_id: int,
    ccp_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
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
        
        # Ensure hazard_id is provided or find a default hazard for this product
        hazard_id = ccp_data.get("hazard_id")
        if not hazard_id:
            # Find the first hazard for this product as a default
            hazard = db.query(Hazard).filter(Hazard.product_id == product_id).first()
            if hazard:
                hazard_id = hazard.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hazards found for this product. Please create a hazard first or specify hazard_id."
                )
        
        # Validate role segregation: monitoring_responsible and verification_responsible must be different
        monitoring_responsible = ccp_data.get("monitoring_responsible")
        verification_responsible = ccp_data.get("verification_responsible")
        if (monitoring_responsible and verification_responsible and 
            monitoring_responsible == verification_responsible):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role segregation violation: The monitoring_responsible and verification_responsible "
                       "must be different users. This is required for proper HACCP compliance."
            )
        
        ccp = CCP(
            product_id=product_id,
            hazard_id=hazard_id,
            ccp_number=ccp_data["ccp_number"],
            ccp_name=ccp_data.get("step_name", ccp_data.get("ccp_name", "Unnamed CCP")),  # Handle different field names
            description=ccp_data.get("description"),
            status=CCPStatus.ACTIVE,
            critical_limit_min=ccp_data.get("critical_limit_min"),
            critical_limit_max=ccp_data.get("critical_limit_max"),
            critical_limit_unit=ccp_data.get("critical_limit_unit"),
            critical_limit_description=ccp_data.get("critical_limit_description"),
            monitoring_frequency=ccp_data.get("monitoring_frequency"),
            monitoring_method=ccp_data.get("monitoring_method"),
            monitoring_responsible=monitoring_responsible,
            monitoring_equipment=ccp_data.get("monitoring_equipment"),
            corrective_actions=ccp_data.get("corrective_actions"),
            verification_frequency=ccp_data.get("verification_frequency"),
            verification_method=ccp_data.get("verification_method"),
            verification_responsible=verification_responsible,
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a CCP"""
    try:
        ccp = db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CCP not found")

        # Validate role segregation before updating
        monitoring_responsible = ccp_data.get("monitoring_responsible", ccp.monitoring_responsible)
        verification_responsible = ccp_data.get("verification_responsible", ccp.verification_responsible)
        
        if monitoring_responsible and verification_responsible and monitoring_responsible == verification_responsible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role segregation violation: The monitoring_responsible and verification_responsible "
                       "must be different users. This is required for proper HACCP compliance."
            )
        
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
                value = ccp_data[field]
                # Never null out non-nullable FK
                if field == "hazard_id" and value is None:
                    continue
                if field == "status" and value is not None:
                    setattr(ccp, field, CCPStatus(value))
                else:
                    setattr(ccp, field, value)

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
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
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
    log_data: MonitoringLogCreate,
    current_user: User = Depends(require_haccp_monitoring_dependency),
    db: Session = Depends(get_db),
    allow_override: bool = Query(False, description="Allow supervisor override of monitoring_responsible requirement")
):
    """Create a monitoring log for a CCP
    
    Only the designated monitoring_responsible person can create logs unless allow_override=true
    and the user has supervisor permissions (haccp:update or haccp:admin).
    """
    try:
        from app.services.haccp_service import HACCPService
        service = HACCPService(db)
        monitoring_log, alert_created, nc_created = service.create_monitoring_log(
            ccp_id=ccp_id,
            log_data=log_data,
            created_by=current_user.id,
            allow_override=allow_override
        )
        
        response_data = {
            "id": monitoring_log.id,
            "timestamp": monitoring_log.monitoring_time.isoformat() if monitoring_log.monitoring_time else None,
            "is_within_limits": monitoring_log.is_within_limits,
            "alert_created": alert_created,
            "nc_created": nc_created
        }
        
        if alert_created:
            response_data["alert_message"] = "Out-of-spec alert has been generated"
        if nc_created:
            response_data["nc_message"] = "Non-Conformance has been automatically created"
        
        resp = ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data=response_data
        )
        try:
            audit_event(db, current_user.id, "haccp_monitoring_log_created", "haccp", str(monitoring_log.id), {
                "ccp_id": ccp_id,
                "is_within_limits": monitoring_log.is_within_limits
            })
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle validation errors (e.g., unauthorized user, missing responsible person)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create monitoring log: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/monitoring-logs")
async def get_monitoring_logs(
    ccp_id: int,
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
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
            verifier = log.verifier if hasattr(log, "verifier") else None
            if verifier is None and log.verified_by:
                verifier = db.query(User).filter(User.id == log.verified_by).first()
            verifier_name = verifier.full_name if verifier else None
            
            items.append({
                "id": log.id,
                "batch_number": log.batch_number,
                "batch_id": log.batch_id,
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
                "is_verified": bool(log.is_verified),
                "verified_by": verifier_name,
                "verified_at": log.verified_at.isoformat() if log.verified_at else None,
                "verification_method": log.verification_method,
                "verification_result": log.verification_result,
                "verification_is_compliant": log.verification_is_compliant,
                "verification_notes": log.verification_notes,
                "verification_evidence_files": log.verification_evidence_files,
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


@router.post("/ccps/{ccp_id}/monitoring-logs/{log_id}/verify")
async def verify_monitoring_log(
    ccp_id: int,
    log_id: int,
    verification_data: MonitoringLogVerificationUpdate,
    allow_override: bool = Query(False, description="Allow supervisor override of verification_responsible requirement"),
    current_user: User = Depends(require_haccp_verification_dependency),
    db: Session = Depends(get_db)
):
    """Verify an existing monitoring log and capture verification details"""
    try:
        service = HACCPService(db)
        verified_log = service.verify_monitoring_log(
            ccp_id=ccp_id,
            monitoring_log_id=log_id,
            verification_data=verification_data,
            verified_by=current_user.id,
            allow_override=allow_override
        )
        
        creator = db.query(User).filter(User.id == verified_log.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        verifier = db.query(User).filter(User.id == verified_log.verified_by).first() if verified_log.verified_by else None
        verifier_name = verifier.full_name if verifier else None
        
        response_payload = {
            "id": verified_log.id,
            "batch_number": verified_log.batch_number,
            "batch_id": verified_log.batch_id,
            "monitoring_time": verified_log.monitoring_time.isoformat() if verified_log.monitoring_time else None,
            "measured_value": verified_log.measured_value,
            "unit": verified_log.unit,
            "is_within_limits": verified_log.is_within_limits,
            "additional_parameters": verified_log.additional_parameters,
            "observations": verified_log.observations,
            "evidence_files": verified_log.evidence_files,
            "corrective_action_taken": verified_log.corrective_action_taken,
            "corrective_action_description": verified_log.corrective_action_description,
            "created_by": creator_name,
            "created_at": verified_log.created_at.isoformat() if verified_log.created_at else None,
            "is_verified": bool(verified_log.is_verified),
            "verified_by": verifier_name,
            "verified_at": verified_log.verified_at.isoformat() if verified_log.verified_at else None,
            "verification_method": verified_log.verification_method,
            "verification_result": verified_log.verification_result,
            "verification_is_compliant": verified_log.verification_is_compliant,
            "verification_notes": verified_log.verification_notes,
            "verification_evidence_files": verified_log.verification_evidence_files,
        }
        
        return ResponseModel(
            success=True,
            message="Monitoring log verified successfully",
            data=response_payload
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify monitoring log: {str(e)}"
        )


# CCP Verification Logs
@router.post("/ccps/{ccp_id}/verification-logs")
async def create_verification_log(
    ccp_id: int,
    log_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
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
        
        # Competency check removed - any user with HACCP access can create verification logs
        
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
    current_user: User = Depends(require_permission_dependency("haccp:view")),
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
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
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
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
    current_user: User = Depends(require_permission_dependency("haccp:create")),
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
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
    current_user: User = Depends(require_permission_dependency("haccp:approve")),
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
    current_user: User = Depends(require_permission_dependency("haccp:update")),
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
    log_data: dict,  # Change to dict to handle raw data first
    current_user: User = Depends(require_haccp_monitoring_dependency),
    db: Session = Depends(get_db)
):
    """Create a monitoring log with automatic alert generation"""
    try:
        print(f"DEBUG: Starting create_enhanced_monitoring_log")
        print(f"DEBUG: ccp_id: {ccp_id}")
        print(f"DEBUG: current_user.id: {current_user.id}")
        print(f"DEBUG: log_data type: {type(log_data)}")
        print(f"DEBUG: log_data: {log_data}")
        
        # Validate and clean the incoming data
        if not isinstance(log_data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request body: expected JSON object"
            )
        
        # Extract and validate measured_value
        measured_value_raw = log_data.get("measured_value")
        if measured_value_raw is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="measured_value is required"
            )
        
        try:
            measured_value = float(measured_value_raw)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid measured_value: {measured_value_raw}. Must be a valid number."
            )
        
        # Create a clean MonitoringLogCreate object
        clean_log_data = MonitoringLogCreate(
            batch_number=log_data.get("batch_number"),
            batch_id=log_data.get("batch_id"),
            measured_value=measured_value,
            unit=log_data.get("unit"),
            additional_parameters=log_data.get("additional_parameters"),
            observations=log_data.get("observations"),
            evidence_files=log_data.get("evidence_files"),
            corrective_action_taken=log_data.get("corrective_action_taken", False),
            corrective_action_description=log_data.get("corrective_action_description"),
            corrective_action_by=log_data.get("corrective_action_by"),
            equipment_id=log_data.get("equipment_id")
        )
        
        print(f"DEBUG: Clean log_data created: {clean_log_data}")
        
        # Competency/permissions are checked in the service callers above; here we just persist safely
        haccp_service = HACCPService(db)
        print(f"DEBUG: HACCPService created")
        
        print(f"DEBUG: About to call haccp_service.create_monitoring_log")
        # Allow override for enhanced endpoint (can be made configurable via query param if needed)
        allow_override = log_data.get("allow_override", False)
        monitoring_log, alert_created, nc_created = haccp_service.create_monitoring_log(
            ccp_id, clean_log_data, current_user.id, allow_override=allow_override
        )
        print(f"DEBUG: haccp_service.create_monitoring_log completed successfully")
        
        response_data = {
            "id": monitoring_log.id,
            "is_within_limits": monitoring_log.is_within_limits,
            "alert_created": alert_created,
            "nc_created": nc_created
        }
        
        if alert_created:
            response_data["alert_message"] = "Out-of-spec alert has been generated and sent to responsible personnel"
        
        if nc_created:
            response_data["nc_message"] = "Non-Conformance has been automatically created and batch quarantined"
        
        print(f"DEBUG: Returning successful response")
        return ResponseModel(
            success=True,
            message="Monitoring log created successfully",
            data=response_data
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        print(f"DEBUG: ValueError caught: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create monitoring log: {str(e)}"
        )


# Evidence Upload for Monitoring Logs
@router.post("/ccps/{ccp_id}/monitoring-logs/upload-evidence")
async def upload_monitoring_evidence(
    ccp_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_haccp_monitoring_dependency),
    db: Session = Depends(get_db)
):
    """Upload evidence file (photo, document, CSV) for HACCP monitoring logs.

    Returns stored file metadata and path for later association to a monitoring log.
    """
    try:
        storage = StorageService(base_upload_dir="uploads/haccp")
        file_path, file_size, content_type, original_filename, checksum = storage.save_upload(
            file, subdir=f"ccps/{ccp_id}"
        )

        return ResponseModel(
            success=True,
            message="Evidence uploaded successfully",
            data={
                "file_path": file_path,
                "file_size": file_size,
                "content_type": content_type,
                "filename": original_filename,
                "checksum": checksum,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload evidence: {str(e)}"
        )


# HACCP Report Generation
@router.post("/products/{product_id}/reports")
async def generate_haccp_report(
    product_id: int,
    report_request: HACCPReportRequest,
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
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
    current_user: User = Depends(require_permission_dependency("haccp:view")),
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
    current_user: User = Depends(require_permission_dependency("haccp:view")),
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


# Hazard Management (Duplicate route - using service layer with CCP/OPRP creation)
@router.post("/products/{product_id}/hazards")
async def create_hazard_alt(
    product_id: int,
    hazard_data: HazardCreate,
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
        
        # Ensure process step exists and belongs to product
        step = db.query(ProcessFlow).filter(
            ProcessFlow.id == hazard_data.process_step_id, 
            ProcessFlow.product_id == product_id
        ).first()
        if not step:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid process_step_id for this product"
            )

        # Use the service layer for business logic (now handles CCP/OPRP creation)
        haccp_service = HACCPService(db)
        hazard = haccp_service.create_hazard(product_id, hazard_data, current_user.id)
        
        # Check if CCP or OPRP was created
        message = "Hazard created successfully"
        if hazard.risk_strategy == "ccp":
            ccp = db.query(CCP).filter(CCP.hazard_id == hazard.id).first()
            if ccp:
                message += f" and CCP ({ccp.ccp_number}) created"
        elif hazard.risk_strategy == "opprp":
            oprp = db.query(OPRP).filter(OPRP.hazard_id == hazard.id).first()
            if oprp:
                message += f" and OPRP ({oprp.oprp_number}) created"
        
        resp = ResponseModel(
            success=True,
            message=message,
            data={"id": hazard.id, "risk_strategy": hazard.risk_strategy}
        )
        try:
            audit_event(db, current_user.id, "haccp_hazard_created", "haccp", str(hazard.id), {"product_id": product_id})
        except Exception:
            pass
        return resp
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
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


# CCP Management (duplicate delete_hazard endpoint removed)
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
        
        # Ensure hazard_id is provided or find a default hazard for this product
        hazard_id = ccp_data.get("hazard_id")
        if not hazard_id:
            # Find the first hazard for this product as a default
            hazard = db.query(Hazard).filter(Hazard.product_id == product_id).first()
            if hazard:
                hazard_id = hazard.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hazards found for this product. Please create a hazard first or specify hazard_id."
                )
        
        ccp = CCP(
            product_id=product_id,
            hazard_id=hazard_id,
            ccp_number=ccp_data["ccp_number"],
            ccp_name=ccp_data.get("step_name", ccp_data.get("ccp_name", "Unnamed CCP")),  # Handle different field names
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
                value = ccp_data[field]
                if field == "hazard_id" and value is None:
                    continue
                if field == "status" and value is not None:
                    setattr(ccp, field, CCPStatus(value))
                else:
                    setattr(ccp, field, value)

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


# Risk Threshold Management
@router.post("/risk-thresholds")
async def create_risk_threshold(
    threshold_data: RiskThresholdCreate,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a new risk threshold configuration"""
    try:
        # Validate scope_id if provided
        if threshold_data.scope_id is not None:
            if threshold_data.scope_type == "product":
                product = db.query(Product).filter(Product.id == threshold_data.scope_id).first()
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found"
                    )
            # Add other scope validations as needed
        
        threshold = RiskThreshold(
            name=threshold_data.name,
            description=threshold_data.description,
            scope_type=threshold_data.scope_type,
            scope_id=threshold_data.scope_id,
            low_threshold=threshold_data.low_threshold,
            medium_threshold=threshold_data.medium_threshold,
            high_threshold=threshold_data.high_threshold,
            likelihood_scale=threshold_data.likelihood_scale,
            severity_scale=threshold_data.severity_scale,
            calculation_method=threshold_data.calculation_method,
            created_by=current_user.id
        )
        
        db.add(threshold)
        db.commit()
        db.refresh(threshold)
        
        return ResponseModel(
            success=True,
            message="Risk threshold created successfully",
            data={"id": threshold.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create risk threshold: {str(e)}"
        )


@router.get("/risk-thresholds")
async def get_risk_thresholds(
    scope_type: Optional[str] = None,
    scope_id: Optional[int] = None,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get risk threshold configurations"""
    try:
        query = db.query(RiskThreshold)
        
        if scope_type:
            query = query.filter(RiskThreshold.scope_type == scope_type)
        if scope_id:
            query = query.filter(RiskThreshold.scope_id == scope_id)
        
        thresholds = query.order_by(RiskThreshold.created_at.desc()).all()
        
        items = []
        for threshold in thresholds:
            items.append(RiskThresholdResponse.from_orm(threshold))
        
        return ResponseModel(
            success=True,
            message="Risk thresholds retrieved successfully",
            data={"items": items}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk thresholds: {str(e)}"
        )


@router.get("/risk-thresholds/{threshold_id}")
async def get_risk_threshold(
    threshold_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get a specific risk threshold configuration"""
    try:
        threshold = db.query(RiskThreshold).filter(RiskThreshold.id == threshold_id).first()
        if not threshold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk threshold not found"
            )
        
        return ResponseModel(
            success=True,
            message="Risk threshold retrieved successfully",
            data=RiskThresholdResponse.from_orm(threshold)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk threshold: {str(e)}"
        )


@router.put("/risk-thresholds/{threshold_id}")
async def update_risk_threshold(
    threshold_id: int,
    threshold_data: RiskThresholdUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a risk threshold configuration"""
    try:
        threshold = db.query(RiskThreshold).filter(RiskThreshold.id == threshold_id).first()
        if not threshold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk threshold not found"
            )
        
        # Update fields
        update_data = threshold_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(threshold, field, value)
        
        threshold.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(threshold)
        
        return ResponseModel(
            success=True,
            message="Risk threshold updated successfully",
            data={"id": threshold.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update risk threshold: {str(e)}"
        )


@router.delete("/risk-thresholds/{threshold_id}")
async def delete_risk_threshold(
    threshold_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete a risk threshold configuration"""
    try:
        threshold = db.query(RiskThreshold).filter(RiskThreshold.id == threshold_id).first()
        if not threshold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk threshold not found"
            )
        
        db.delete(threshold)
        db.commit()
        
        return ResponseModel(
            success=True,
            message="Risk threshold deleted successfully",
            data={"id": threshold_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete risk threshold: {str(e)}"
        )


@router.post("/risk-thresholds/calculate")
async def calculate_risk_level(
    likelihood: int,
    severity: int,
    scope_type: str = "site",
    scope_id: Optional[int] = None,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Calculate risk level using configured thresholds"""
    try:
        # Find the appropriate threshold configuration
        query = db.query(RiskThreshold).filter(RiskThreshold.scope_type == scope_type)
        if scope_id:
            query = query.filter(RiskThreshold.scope_id == scope_id)
        else:
            query = query.filter(RiskThreshold.scope_id.is_(None))
        
        threshold = query.first()
        
        if not threshold:
            # Use default thresholds if none configured
            threshold = RiskThreshold(
                low_threshold=4,
                medium_threshold=8,
                high_threshold=15,
                calculation_method="multiplication"
            )
        
        risk_level = threshold.calculate_risk_level(likelihood, severity)
        risk_score = likelihood * severity  # Default calculation
        
        return ResponseModel(
            success=True,
            message="Risk level calculated successfully",
            data={
                "likelihood": likelihood,
                "severity": severity,
                "risk_score": risk_score,
                "risk_level": risk_level.value,
                "threshold_config": {
                    "low_threshold": threshold.low_threshold,
                    "medium_threshold": threshold.medium_threshold,
                    "high_threshold": threshold.high_threshold,
                    "calculation_method": threshold.calculation_method
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate risk level: {str(e)}"
        )


# Hazard Review Management
@router.post("/hazards/{hazard_id}/reviews", response_model=HazardReviewResponse)
async def create_hazard_review(
    hazard_id: int,
    review_data: HazardReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a hazard review"""
    haccp_service = HACCPService(db)
    return haccp_service.create_hazard_review(hazard_id, review_data, current_user.id)


@router.get("/hazards/{hazard_id}/reviews")
async def get_hazard_reviews(
    hazard_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all reviews for a hazard"""
    try:
        # Verify hazard exists
        hazard = db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hazard not found"
            )
        
        reviews = db.query(HazardReview).filter(HazardReview.hazard_id == hazard_id).all()
        
        items = []
        for review in reviews:
            reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
            review_data = HazardReviewResponse.from_orm(review)
            review_data.reviewer_name = reviewer.full_name if reviewer else "Unknown"
            items.append(review_data)
        
        return ResponseModel(
            success=True,
            message="Hazard reviews retrieved successfully",
            data={"items": items}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve hazard reviews: {str(e)}"
        )


@router.put("/hazards/{hazard_id}/reviews/{review_id}")
async def update_hazard_review(
    hazard_id: int,
    review_id: int,
    review_data: HazardReviewUpdate,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update a hazard review"""
    try:
        review = db.query(HazardReview).filter(
            and_(HazardReview.id == review_id, HazardReview.hazard_id == hazard_id)
        ).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hazard review not found"
            )
        
        # Update fields
        update_data = review_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)
        
        if review_data.review_status in ["approved", "rejected"]:
            review.review_date = datetime.utcnow()
        
        review.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(review)
        
        return ResponseModel(
            success=True,
            message="Hazard review updated successfully",
            data={"id": review.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update hazard review: {str(e)}"
        )


@router.get("/products/{product_id}/hazard-review-status")
async def get_hazard_review_status(
    product_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get hazard review status for a product"""
    try:
        # Get all hazards for the product
        hazards = db.query(Hazard).filter(Hazard.product_id == product_id).all()
        
        review_status = {
            "total_hazards": len(hazards),
            "reviewed_hazards": 0,
            "approved_hazards": 0,
            "rejected_hazards": 0,
            "pending_reviews": 0,
            "hazards": []
        }
        
        for hazard in hazards:
            # Get the latest review for each hazard
            latest_review = db.query(HazardReview).filter(
                HazardReview.hazard_id == hazard.id
            ).order_by(HazardReview.created_at.desc()).first()
            
            hazard_status = {
                "hazard_id": hazard.id,
                "hazard_name": hazard.hazard_name,
                "has_review": latest_review is not None,
                "review_status": latest_review.review_status if latest_review else "pending",
                "reviewer_name": None,
                "review_date": latest_review.review_date if latest_review else None
            }
            
            if latest_review:
                reviewer = db.query(User).filter(User.id == latest_review.reviewer_id).first()
                hazard_status["reviewer_name"] = reviewer.full_name if reviewer else "Unknown"
                
                if latest_review.review_status == "approved":
                    review_status["approved_hazards"] += 1
                    review_status["reviewed_hazards"] += 1
                elif latest_review.review_status == "rejected":
                    review_status["rejected_hazards"] += 1
                    review_status["reviewed_hazards"] += 1
            else:
                review_status["pending_reviews"] += 1
            
            review_status["hazards"].append(hazard_status)
        
        return ResponseModel(
            success=True,
            message="Hazard review status retrieved successfully",
            data=review_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve hazard review status: {str(e)}"
        )


# Decision Tree Endpoints (Codex Alimentarius)
@router.post("/hazards/{hazard_id}/decision-tree", response_model=DecisionTreeResponse)
async def create_decision_tree(
    hazard_id: int,
    decision_data: DecisionTreeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start the Codex Alimentarius decision tree for a hazard"""
    haccp_service = HACCPService(db)
    decision_tree = haccp_service.create_decision_tree(
        hazard_id, 
        decision_data.q1_answer, 
        decision_data.q1_justification, 
        current_user.id
    )
    
    # Convert to response format
    return DecisionTreeResponse(
        id=decision_tree.id,
        hazard_id=decision_tree.hazard_id,
        q1_answer=decision_tree.q1_answer,
        q1_justification=decision_tree.q1_justification,
        q1_answered_by=decision_tree.q1_answered_by,
        q1_answered_at=decision_tree.q1_answered_at,
        q2_answer=decision_tree.q2_answer,
        q2_justification=decision_tree.q2_justification,
        q2_answered_by=decision_tree.q2_answered_by,
        q2_answered_at=decision_tree.q2_answered_at,
        q3_answer=decision_tree.q3_answer,
        q3_justification=decision_tree.q3_justification,
        q3_answered_by=decision_tree.q3_answered_by,
        q3_answered_at=decision_tree.q3_answered_at,
        q4_answer=decision_tree.q4_answer,
        q4_justification=decision_tree.q4_justification,
        q4_answered_by=decision_tree.q4_answered_by,
        q4_answered_at=decision_tree.q4_answered_at,
        is_ccp=decision_tree.is_ccp,
        decision_reasoning=decision_tree.decision_reasoning,
        decision_date=decision_tree.decision_date,
        decision_by=decision_tree.decision_by,
        status=decision_tree.status,
        current_question=decision_tree.get_current_question(),
        can_proceed=decision_tree.can_proceed_to_next_question(),
        created_at=decision_tree.created_at,
        updated_at=decision_tree.updated_at
    )

@router.post("/hazards/{hazard_id}/decision-tree/answer", response_model=DecisionTreeResponse)
async def answer_decision_tree_question(
    hazard_id: int,
    question_response: DecisionTreeQuestionResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Answer a specific question in the decision tree"""
    haccp_service = HACCPService(db)
    decision_tree = haccp_service.answer_decision_tree_question(
        hazard_id,
        question_response.question_number,
        question_response.answer,
        question_response.justification or "",
        current_user.id
    )
    
    # Convert to response format
    return DecisionTreeResponse(
        id=decision_tree.id,
        hazard_id=decision_tree.hazard_id,
        q1_answer=decision_tree.q1_answer,
        q1_justification=decision_tree.q1_justification,
        q1_answered_by=decision_tree.q1_answered_by,
        q1_answered_at=decision_tree.q1_answered_at,
        q2_answer=decision_tree.q2_answer,
        q2_justification=decision_tree.q2_justification,
        q2_answered_by=decision_tree.q2_answered_by,
        q2_answered_at=decision_tree.q2_answered_at,
        q3_answer=decision_tree.q3_answer,
        q3_justification=decision_tree.q3_justification,
        q3_answered_by=decision_tree.q3_answered_by,
        q3_answered_at=decision_tree.q3_answered_at,
        q4_answer=decision_tree.q4_answer,
        q4_justification=decision_tree.q4_justification,
        q4_answered_by=decision_tree.q4_answered_by,
        q4_answered_at=decision_tree.q4_answered_at,
        is_ccp=decision_tree.is_ccp,
        decision_reasoning=decision_tree.decision_reasoning,
        decision_date=decision_tree.decision_date,
        decision_by=decision_tree.decision_by,
        status=decision_tree.status,
        current_question=decision_tree.get_current_question(),
        can_proceed=decision_tree.can_proceed_to_next_question(),
        created_at=decision_tree.created_at,
        updated_at=decision_tree.updated_at
    )

@router.get("/hazards/{hazard_id}/decision-tree", response_model=DecisionTreeResponse)
async def get_decision_tree(
    hazard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the decision tree for a hazard"""
    haccp_service = HACCPService(db)
    decision_tree = haccp_service.get_decision_tree(hazard_id)
    
    if not decision_tree:
        raise HTTPException(status_code=404, detail="Decision tree not found")
    
    return DecisionTreeResponse(
        id=decision_tree.id,
        hazard_id=decision_tree.hazard_id,
        q1_answer=decision_tree.q1_answer,
        q1_justification=decision_tree.q1_justification,
        q1_answered_by=decision_tree.q1_answered_by,
        q1_answered_at=decision_tree.q1_answered_at,
        q2_answer=decision_tree.q2_answer,
        q2_justification=decision_tree.q2_justification,
        q2_answered_by=decision_tree.q2_answered_by,
        q2_answered_at=decision_tree.q2_answered_at,
        q3_answer=decision_tree.q3_answer,
        q3_justification=decision_tree.q3_justification,
        q3_answered_by=decision_tree.q3_answered_by,
        q3_answered_at=decision_tree.q3_answered_at,
        q4_answer=decision_tree.q4_answer,
        q4_justification=decision_tree.q4_justification,
        q4_answered_by=decision_tree.q4_answered_by,
        q4_answered_at=decision_tree.q4_answered_at,
        is_ccp=decision_tree.is_ccp,
        decision_reasoning=decision_tree.decision_reasoning,
        decision_date=decision_tree.decision_date,
        decision_by=decision_tree.decision_by,
        status=decision_tree.status,
        current_question=decision_tree.get_current_question(),
        can_proceed=decision_tree.can_proceed_to_next_question(),
        created_at=decision_tree.created_at,
        updated_at=decision_tree.updated_at
    )

@router.get("/hazards/{hazard_id}/decision-tree/status")
async def get_decision_tree_status(
    hazard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current status of a decision tree"""
    haccp_service = HACCPService(db)
    return haccp_service.get_decision_tree_status(hazard_id)
# Validation Evidence Endpoints
@router.post("/ccps/{ccp_id}/validation-evidence")
async def add_validation_evidence(
    ccp_id: int,
    evidence_data: ValidationEvidence,
    current_user: User = Depends(require_permission_dependency("haccp:edit")),
    db: Session = Depends(get_db)
):
    """Add validation evidence to a CCP"""
    try:
        haccp_service = HACCPService(db)
        ccp = haccp_service.add_validation_evidence(ccp_id, evidence_data.dict(), current_user.id)
        
        return ResponseModel(
            success=True,
            message="Validation evidence added successfully",
            data={"ccp_id": ccp.id, "evidence_count": len(ccp.validation_evidence or [])}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add validation evidence: {str(e)}"
        )


@router.delete("/ccps/{ccp_id}/validation-evidence/{evidence_id}")
async def remove_validation_evidence(
    ccp_id: int,
    evidence_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:edit")),
    db: Session = Depends(get_db)
):
    """Remove validation evidence from a CCP"""
    try:
        haccp_service = HACCPService(db)
        ccp = haccp_service.remove_validation_evidence(ccp_id, evidence_id, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Validation evidence removed successfully",
            data={"ccp_id": ccp.id, "evidence_count": len(ccp.validation_evidence or [])}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove validation evidence: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/validation-evidence/summary")
async def get_validation_evidence_summary(
    ccp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get validation evidence summary for a CCP"""
    try:
        haccp_service = HACCPService(db)
        summary = haccp_service.get_validation_evidence_summary(ccp_id)
        
        return ResponseModel(
            success=True,
            message="Validation evidence summary retrieved successfully",
            data=summary
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validation evidence summary: {str(e)}"
        )

# Monitoring Schedule Endpoints
@router.post("/ccps/{ccp_id}/monitoring-schedule")
async def create_monitoring_schedule(
    ccp_id: int,
    schedule_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a monitoring schedule for a CCP"""
    try:
        schedule_data["ccp_id"] = ccp_id
        haccp_service = HACCPService(db)
        schedule = haccp_service.create_monitoring_schedule(schedule_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Monitoring schedule created successfully",
            data={
                "id": schedule.id,
                "ccp_id": schedule.ccp_id,
                "schedule_type": schedule.schedule_type,
                "next_due_time": schedule.next_due_time.isoformat() if schedule.next_due_time else None
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create monitoring schedule: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/monitoring-schedule/status")
async def get_monitoring_schedule_status(
    ccp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get monitoring schedule status for a CCP"""
    try:
        haccp_service = HACCPService(db)
        status = haccp_service.get_monitoring_schedule_status(ccp_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No monitoring schedule found for this CCP"
            )
        
        return ResponseModel(
            success=True,
            message="Monitoring schedule status retrieved successfully",
            data={
                "schedule_id": status.schedule_id,
                "ccp_id": status.ccp_id,
                "ccp_name": status.ccp_name,
                "is_due": status.is_due,
                "is_overdue": status.is_overdue,
                "next_due_time": status.next_due_time.isoformat() if status.next_due_time else None,
                "last_monitoring_time": status.last_monitoring_time.isoformat() if status.last_monitoring_time else None,
                "tolerance_window_minutes": status.tolerance_window_minutes,
                "schedule_type": status.schedule_type,
                "is_active": status.is_active
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring schedule status: {str(e)}"
        )


@router.get("/monitoring/due")
async def get_due_monitoring(
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all CCPs that are due for monitoring"""
    try:
        haccp_service = HACCPService(db)
        due_schedules = haccp_service.get_all_due_monitoring()
        
        items = []
        for status in due_schedules:
            items.append({
                "schedule_id": status.schedule_id,
                "ccp_id": status.ccp_id,
                "ccp_name": status.ccp_name,
                "is_due": status.is_due,
                "is_overdue": status.is_overdue,
                "next_due_time": status.next_due_time.isoformat() if status.next_due_time else None,
                "last_monitoring_time": status.last_monitoring_time.isoformat() if status.last_monitoring_time else None,
                "tolerance_window_minutes": status.tolerance_window_minutes,
                "schedule_type": status.schedule_type,
                "is_active": status.is_active
            })
        
        return ResponseModel(
            success=True,
            message="Due monitoring schedules retrieved successfully",
            data={"items": items, "total": len(items)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get due monitoring schedules: {str(e)}"
        )

# Batch Disposition Endpoints
@router.get("/batches/quarantined")
async def get_quarantined_batches(
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all quarantined batches"""
    try:
        haccp_service = HACCPService(db)
        quarantined_batches = haccp_service.get_quarantined_batches()
        
        return ResponseModel(
            success=True,
            message="Quarantined batches retrieved successfully",
            data={"items": quarantined_batches, "total": len(quarantined_batches)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quarantined batches: {str(e)}"
        )


@router.post("/batches/{batch_id}/disposition")
async def dispose_batch(
    batch_id: int,
    disposition_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:approve")),
    db: Session = Depends(get_db)
):
    """Dispose of a quarantined batch (release, dispose, or rework)"""
    try:
        haccp_service = HACCPService(db)
        success = haccp_service.release_batch_from_quarantine(batch_id, disposition_data, current_user.id)
        
        if success:
            disposition_type = disposition_data.get("disposition_type", "unknown")
            return ResponseModel(
                success=True,
                message=f"Batch {disposition_type}d successfully",
                data={
                    "batch_id": batch_id,
                    "disposition_type": disposition_type,
                    "approved_by": current_user.id,
                    "approved_at": datetime.utcnow().isoformat()
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to dispose batch"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispose batch: {str(e)}"
        )

# Verification Program Endpoints
@router.post("/ccps/{ccp_id}/verification-programs")
async def create_verification_program(
    ccp_id: int,
    program_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a verification program for a CCP"""
    try:
        program_data["ccp_id"] = ccp_id
        haccp_service = HACCPService(db)
        program = haccp_service.create_verification_program(program_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Verification program created successfully",
            data={
                "id": program.id,
                "ccp_id": program.ccp_id,
                "verification_type": program.verification_type,
                "frequency": program.frequency,
                "next_verification_date": program.next_verification_date
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create verification program: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/verification-programs")
async def get_verification_programs(
    ccp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all verification programs for a CCP"""
    try:
        haccp_service = HACCPService(db)
        programs = haccp_service.get_verification_programs_for_ccp(ccp_id)
        
        return ResponseModel(
            success=True,
            message="Verification programs retrieved successfully",
            data={"items": programs, "total": len(programs)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get verification programs: {str(e)}"
        )


@router.get("/verification/due")
async def get_due_verifications(
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all verification programs that are due"""
    try:
        haccp_service = HACCPService(db)
        due_verifications = haccp_service.get_due_verifications()
        
        return ResponseModel(
            success=True,
            message="Due verifications retrieved successfully",
            data={"items": due_verifications, "total": len(due_verifications)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get due verifications: {str(e)}"
        )


# Enhanced Verification Log Endpoints with Role Segregation
@router.post("/ccps/{ccp_id}/verification-logs")
async def create_verification_log(
    ccp_id: int,
    log_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:verify")),
    db: Session = Depends(get_db)
):
    """Create a verification log with role segregation enforcement"""
    try:
        haccp_service = HACCPService(db)
        verification_log = haccp_service.create_verification_log_with_role_check(ccp_id, log_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Verification log created successfully",
            data={
                "id": verification_log.id,
                "ccp_id": verification_log.ccp_id,
                "verification_date": verification_log.verification_date,
                "is_compliant": verification_log.is_compliant
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create verification log: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/verification-logs")
async def get_verification_logs(
    ccp_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_haccp_view_dependency(allow_assignment=True)),
    db: Session = Depends(get_db)
):
    """Get verification logs for a CCP with pagination"""
    try:
        base_query = db.query(CCPMonitoringLog).filter(
            CCPMonitoringLog.ccp_id == ccp_id,
            CCPMonitoringLog.is_verified == True
        )
        
        total = base_query.count()
        logs = base_query.order_by(
            desc(CCPMonitoringLog.verified_at),
            desc(CCPMonitoringLog.monitoring_time)
        ).offset(skip).limit(limit).all()
        
        items = []
        for log in logs:
            creator = db.query(User).filter(User.id == log.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            verifier = db.query(User).filter(User.id == log.verified_by).first() if log.verified_by else None
            verifier_name = verifier.full_name if verifier else None
            
            items.append({
                "id": log.id,
                "batch_number": log.batch_number,
                "batch_id": log.batch_id,
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
                "is_verified": bool(log.is_verified),
                "verified_by": verifier_name,
                "verified_at": log.verified_at.isoformat() if log.verified_at else None,
                "verification_method": log.verification_method,
                "verification_result": log.verification_result,
                "verification_is_compliant": log.verification_is_compliant,
                "verification_notes": log.verification_notes,
                "verification_evidence_files": log.verification_evidence_files,
            })
        
        return ResponseModel(
            success=True,
            message="Verification logs retrieved successfully",
            data={
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get verification logs: {str(e)}"
        )


# Validation Endpoints
@router.post("/ccps/{ccp_id}/validations")
async def create_validation(
    ccp_id: int,
    validation_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a validation for a CCP"""
    try:
        validation_data["ccp_id"] = ccp_id
        haccp_service = HACCPService(db)
        validation = haccp_service.create_validation(validation_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Validation created successfully",
            data={
                "id": validation.id,
                "ccp_id": validation.ccp_id,
                "validation_type": validation.validation_type,
                "validation_title": validation.validation_title,
                "review_status": validation.review_status
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create validation: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/validations")
async def get_validations(
    ccp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all validations for a CCP"""
    try:
        haccp_service = HACCPService(db)
        validations = haccp_service.get_validations_for_ccp(ccp_id)
        
        return ResponseModel(
            success=True,
            message="Validations retrieved successfully",
            data={"items": validations, "total": len(validations)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validations: {str(e)}"
        )


@router.post("/validations/{validation_id}/review")
async def review_validation(
    validation_id: int,
    review_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:approve")),
    db: Session = Depends(get_db)
):
    """Review a validation (approve/reject)"""
    try:
        haccp_service = HACCPService(db)
        validation = haccp_service.review_validation(validation_id, review_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message=f"Validation {review_data['review_status']} successfully",
            data={
                "id": validation.id,
                "review_status": validation.review_status,
                "reviewed_by": validation.reviewed_by,
                "reviewed_at": validation.reviewed_at
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to review validation: {str(e)}"
        )


@router.get("/ccps/{ccp_id}/validation-status")
async def get_validation_status(
    ccp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Check validation status for a CCP"""
    try:
        haccp_service = HACCPService(db)
        status = haccp_service.check_ccp_validation_status(ccp_id)
        
        return ResponseModel(
            success=True,
            message="Validation status retrieved successfully",
            data=status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validation status: {str(e)}"
        )

# Verification Program Endpoints
@router.post("/ccps/{ccp_id}/verification-programs")
async def create_verification_program(
    ccp_id: int,
    program_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create a verification program for a CCP"""
    try:
        program_data["ccp_id"] = ccp_id
        haccp_service = HACCPService(db)
        program = haccp_service.create_verification_program(program_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Verification program created successfully",
            data={
                "id": program.id,
                "ccp_id": program.ccp_id,
                "verification_type": program.verification_type,
                "frequency": program.frequency,
                "next_verification_date": program.next_verification_date
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create verification program: {str(e)}"
        )

# Evidence Management Endpoints
@router.post("/evidence/attachments")
async def create_evidence_attachment(
    attachment_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create an evidence attachment for a HACCP record"""
    try:
        haccp_service = HACCPService(db)
        attachment = haccp_service.create_evidence_attachment(attachment_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Evidence attachment created successfully",
            data={
                "id": attachment.id,
                "record_type": attachment.record_type,
                "record_id": attachment.record_id,
                "document_id": attachment.document_id,
                "evidence_type": attachment.evidence_type
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create evidence attachment: {str(e)}"
        )


@router.get("/evidence/attachments/{record_type}/{record_id}")
async def get_evidence_attachments(
    record_type: str,
    record_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all evidence attachments for a specific record"""
    try:
        haccp_service = HACCPService(db)
        attachments = haccp_service.get_evidence_attachments(record_type, record_id)
        
        return ResponseModel(
            success=True,
            message="Evidence attachments retrieved successfully",
            data={"items": attachments, "total": len(attachments)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get evidence attachments: {str(e)}"
        )


@router.delete("/evidence/attachments/{attachment_id}")
async def delete_evidence_attachment(
    attachment_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete an evidence attachment"""
    try:
        haccp_service = HACCPService(db)
        success = haccp_service.delete_evidence_attachment(attachment_id, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Evidence attachment deleted successfully",
            data={"attachment_id": attachment_id}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete evidence attachment: {str(e)}"
        )


# ============================================================================
# OPRP MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/products/{product_id}/oprps", response_model=ResponseModel)
async def create_oprp(
    product_id: int,
    oprp_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create an OPRP for a product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Verify hazard exists
        hazard = db.query(Hazard).filter(Hazard.id == oprp_data.get("hazard_id")).first()
        if not hazard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hazard not found"
            )
        
        # Create OPRP
        oprp = OPRP(
            product_id=product_id,
            hazard_id=oprp_data["hazard_id"],
            oprp_number=oprp_data["oprp_number"],
            oprp_name=oprp_data["oprp_name"],
            description=oprp_data.get("description"),
            status=oprp_data.get("status", "active"),
            operational_limit_min=oprp_data.get("operational_limit_min"),
            operational_limit_max=oprp_data.get("operational_limit_max"),
            operational_limit_unit=oprp_data.get("operational_limit_unit"),
            operational_limit_description=oprp_data.get("operational_limit_description"),
            monitoring_frequency=oprp_data.get("monitoring_frequency"),
            monitoring_method=oprp_data.get("monitoring_method"),
            monitoring_responsible=oprp_data.get("monitoring_responsible"),
            monitoring_equipment=oprp_data.get("monitoring_equipment"),
            corrective_actions=oprp_data.get("corrective_actions"),
            verification_frequency=oprp_data.get("verification_frequency"),
            verification_method=oprp_data.get("verification_method"),
            verification_responsible=oprp_data.get("verification_responsible"),
            justification=oprp_data.get("justification"),
            effectiveness_validation=oprp_data.get("effectiveness_validation"),
            created_by=current_user.id
        )
        
        db.add(oprp)
        db.commit()
        db.refresh(oprp)
        
        try:
            audit_event(db, current_user.id, "haccp_oprp_created", "haccp", str(oprp.id))
        except Exception:
            pass
        
        return ResponseModel(
            success=True,
            message="OPRP created successfully",
            data={"id": oprp.id, "name": oprp.oprp_name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create OPRP: {str(e)}"
        )


@router.get("/products/{product_id}/oprps", response_model=ResponseModel)
async def get_oprps(
    product_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get all OPRPs for a product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        oprps = db.query(OPRP).filter(OPRP.product_id == product_id).all()
        
        return ResponseModel(
            success=True,
            message="OPRPs retrieved successfully",
            data=[{
                "id": oprp.id,
                "oprp_number": oprp.oprp_number,
                "oprp_name": oprp.oprp_name,
                "description": oprp.description,
                "status": oprp.status,
                "hazard_id": oprp.hazard_id,
                "operational_limit_min": oprp.operational_limit_min,
                "operational_limit_max": oprp.operational_limit_max,
                "operational_limit_unit": oprp.operational_limit_unit,
                "monitoring_frequency": oprp.monitoring_frequency,
                "monitoring_method": oprp.monitoring_method,
                "corrective_actions": oprp.corrective_actions,
                "justification": oprp.justification,
                "created_at": oprp.created_at,
                "updated_at": oprp.updated_at
            } for oprp in oprps]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve OPRPs: {str(e)}"
        )


@router.get("/oprps/{oprp_id}", response_model=ResponseModel)
async def get_oprp(
    oprp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get a specific OPRP"""
    try:
        oprp = db.query(OPRP).filter(OPRP.id == oprp_id).first()
        if not oprp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPRP not found"
            )
        
        return ResponseModel(
            success=True,
            message="OPRP retrieved successfully",
            data={
                "id": oprp.id,
                "product_id": oprp.product_id,
                "hazard_id": oprp.hazard_id,
                "oprp_number": oprp.oprp_number,
                "oprp_name": oprp.oprp_name,
                "description": oprp.description,
                "status": oprp.status,
                "operational_limit_min": oprp.operational_limit_min,
                "operational_limit_max": oprp.operational_limit_max,
                "operational_limit_unit": oprp.operational_limit_unit,
                "operational_limit_description": oprp.operational_limit_description,
                "monitoring_frequency": oprp.monitoring_frequency,
                "monitoring_method": oprp.monitoring_method,
                "monitoring_responsible": oprp.monitoring_responsible,
                "monitoring_equipment": oprp.monitoring_equipment,
                "corrective_actions": oprp.corrective_actions,
                "verification_frequency": oprp.verification_frequency,
                "verification_method": oprp.verification_method,
                "verification_responsible": oprp.verification_responsible,
                "justification": oprp.justification,
                "effectiveness_validation": oprp.effectiveness_validation,
                "created_at": oprp.created_at,
                "updated_at": oprp.updated_at,
                "created_by": oprp.created_by
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve OPRP: {str(e)}"
        )


@router.put("/oprps/{oprp_id}", response_model=ResponseModel)
async def update_oprp(
    oprp_id: int,
    oprp_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:update")),
    db: Session = Depends(get_db)
):
    """Update an OPRP"""
    try:
        oprp = db.query(OPRP).filter(OPRP.id == oprp_id).first()
        if not oprp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPRP not found"
            )
        
        # Update fields
        for field in [
            "oprp_number",
            "oprp_name",
            "description",
            "status",
            "operational_limit_min",
            "operational_limit_max",
            "operational_limit_unit",
            "operational_limit_description",
            "monitoring_frequency",
            "monitoring_method",
            "monitoring_responsible",
            "monitoring_equipment",
            "corrective_actions",
            "verification_frequency",
            "verification_method",
            "verification_responsible",
            "justification",
            "effectiveness_validation"
        ]:
            if field in oprp_data:
                setattr(oprp, field, oprp_data[field])
        
        db.commit()
        db.refresh(oprp)
        
        try:
            audit_event(db, current_user.id, "haccp_oprp_updated", "haccp", str(oprp.id))
        except Exception:
            pass
        
        return ResponseModel(
            success=True,
            message="OPRP updated successfully",
            data={"id": oprp.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update OPRP: {str(e)}"
        )


@router.delete("/oprps/{oprp_id}", response_model=ResponseModel)
async def delete_oprp(
    oprp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:delete")),
    db: Session = Depends(get_db)
):
    """Delete an OPRP"""
    try:
        oprp = db.query(OPRP).filter(OPRP.id == oprp_id).first()
        if not oprp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPRP not found"
            )
        
        db.delete(oprp)
        db.commit()
        
        try:
            audit_event(db, current_user.id, "haccp_oprp_deleted", "haccp", str(oprp_id))
        except Exception:
            pass
        
        return ResponseModel(
            success=True,
            message="OPRP deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete OPRP: {str(e)}"
        )


@router.post("/oprps/{oprp_id}/monitoring-logs", response_model=ResponseModel)
async def create_oprp_monitoring_log(
    oprp_id: int,
    log_data: dict,
    current_user: User = Depends(require_permission_dependency("haccp:create")),
    db: Session = Depends(get_db)
):
    """Create an OPRP monitoring log"""
    try:
        # Verify OPRP exists
        oprp = db.query(OPRP).filter(OPRP.id == oprp_id).first()
        if not oprp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPRP not found"
            )
        
        # Validate measured values against operational limits
        validation_results = oprp.validate_limits(log_data.get("measured_values", {}))
        is_within_limits = all(result.get("valid", False) for result in validation_results.values())
        
        # Create monitoring log
        monitoring_log = OPRPMonitoringLog(
            oprp_id=oprp_id,
            batch_number=log_data.get("batch_number"),
            measured_values=log_data.get("measured_values", {}),
            measured_at=datetime.fromisoformat(log_data["measured_at"]) if isinstance(log_data.get("measured_at"), str) else log_data.get("measured_at", datetime.now()),
            measured_by=current_user.id,
            equipment_used=log_data.get("equipment_used"),
            comments=log_data.get("comments"),
            validation_results=validation_results,
            is_within_limits=is_within_limits,
            corrective_actions_taken=log_data.get("corrective_actions_taken") if not is_within_limits else None
        )
        
        db.add(monitoring_log)
        db.commit()
        db.refresh(monitoring_log)
        
        try:
            audit_event(db, current_user.id, "haccp_oprp_monitoring_log_created", "haccp", str(monitoring_log.id))
        except Exception:
            pass
        
        return ResponseModel(
            success=True,
            message="OPRP monitoring log created successfully",
            data={
                "id": monitoring_log.id,
                "is_within_limits": is_within_limits,
                "validation_results": validation_results
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create OPRP monitoring log: {str(e)}"
        )


@router.get("/oprps/{oprp_id}/monitoring-logs", response_model=ResponseModel)
async def get_oprp_monitoring_logs(
    oprp_id: int,
    current_user: User = Depends(require_permission_dependency("haccp:view")),
    db: Session = Depends(get_db)
):
    """Get monitoring logs for an OPRP"""
    try:
        # Verify OPRP exists
        oprp = db.query(OPRP).filter(OPRP.id == oprp_id).first()
        if not oprp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPRP not found"
            )
        
        logs = db.query(OPRPMonitoringLog).filter(OPRPMonitoringLog.oprp_id == oprp_id).order_by(OPRPMonitoringLog.measured_at.desc()).all()
        
        return ResponseModel(
            success=True,
            message="OPRP monitoring logs retrieved successfully",
            data=[{
                "id": log.id,
                "batch_number": log.batch_number,
                "measured_values": log.measured_values,
                "measured_at": log.measured_at,
                "measured_by": log.measured_by,
                "equipment_used": log.equipment_used,
                "comments": log.comments,
                "validation_results": log.validation_results,
                "is_within_limits": log.is_within_limits,
                "corrective_actions_taken": log.corrective_actions_taken,
                "created_at": log.created_at
            } for log in logs]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve OPRP monitoring logs: {str(e)}"
        )
