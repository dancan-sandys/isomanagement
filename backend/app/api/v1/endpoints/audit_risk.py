from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.schemas.common import ResponseModel
from app.services.audit_risk_service import AuditRiskService
from app.utils.audit import audit_event

router = APIRouter()


@router.post("/audits/{audit_id}/assess")
async def assess_audit_risk(
    audit_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform comprehensive risk assessment for an audit"""
    try:
        service = AuditRiskService(db)
        assessment_data["assessor_id"] = current_user.id
        assessment = service.assess_audit_risk(audit_id, assessment_data)
        
        try:
            audit_event(db, current_user.id, "audit_risk_assessed", "audit", str(audit_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Audit risk assessment completed",
            data={
                "assessment_id": assessment.id,
                "initial_risk_score": assessment.initial_risk_score,
                "residual_risk_score": assessment.residual_risk_score,
                "risk_acceptable": assessment.risk_acceptable
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess audit risk: {str(e)}")


@router.post("/findings/{finding_id}/assess")
async def assess_audit_finding_risk(
    finding_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform comprehensive risk assessment for an audit finding"""
    try:
        service = AuditRiskService(db)
        assessment_data["assessor_id"] = current_user.id
        assessment = service.assess_audit_finding_risk(finding_id, assessment_data)
        
        try:
            audit_event(db, current_user.id, "audit_finding_risk_assessed", "audit_finding", str(finding_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Audit finding risk assessment completed",
            data={
                "assessment_id": assessment.id,
                "initial_risk_score": assessment.initial_risk_score,
                "residual_risk_score": assessment.residual_risk_score,
                "risk_acceptable": assessment.risk_acceptable
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess finding risk: {str(e)}")


@router.post("/audits/{audit_id}/integrate")
async def integrate_audit_with_risk_register(
    audit_id: int,
    integration_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate an audit with the risk register"""
    try:
        service = AuditRiskService(db)
        risk_register_item_id = integration_data.get("risk_register_item_id")
        if not risk_register_item_id:
            raise HTTPException(status_code=400, detail="risk_register_item_id is required")
            
        integration_data["integrated_by"] = current_user.id
        integration = service.integrate_audit_with_risk_register(audit_id, risk_register_item_id, integration_data)
        
        try:
            audit_event(db, current_user.id, "audit_risk_integrated", "audit", str(audit_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Audit integrated with risk register",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate audit: {str(e)}")


@router.post("/findings/{finding_id}/integrate")
async def integrate_finding_with_risk_register(
    finding_id: int,
    integration_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate an audit finding with the risk register"""
    try:
        service = AuditRiskService(db)
        risk_register_item_id = integration_data.get("risk_register_item_id")
        if not risk_register_item_id:
            raise HTTPException(status_code=400, detail="risk_register_item_id is required")
            
        integration_data["integrated_by"] = current_user.id
        integration = service.integrate_finding_with_risk_register(finding_id, risk_register_item_id, integration_data)
        
        try:
            audit_event(db, current_user.id, "audit_finding_risk_integrated", "audit_finding", str(finding_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Audit finding integrated with risk register",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate finding: {str(e)}")


@router.post("/prp/{prp_program_id}/audit/{audit_finding_id}/integrate")
async def integrate_prp_with_audit_finding(
    prp_program_id: int,
    audit_finding_id: int,
    integration_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate a PRP program with an audit finding"""
    try:
        service = AuditRiskService(db)
        integration_data["integrated_by"] = current_user.id
        integration = service.integrate_prp_with_audit_finding(prp_program_id, audit_finding_id, integration_data)
        
        try:
            audit_event(db, current_user.id, "prp_audit_integrated", "prp_program", str(prp_program_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="PRP program integrated with audit finding",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate PRP with audit: {str(e)}")


@router.get("/analytics/summary")
async def get_audit_risk_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive audit risk summary"""
    try:
        service = AuditRiskService(db)
        summary = service.get_audit_risk_summary()
        
        return ResponseModel(
            success=True,
            message="Audit risk summary retrieved",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk summary: {str(e)}")


@router.get("/analytics/alerts")
async def get_audit_risk_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get audit risk alerts and notifications"""
    try:
        service = AuditRiskService(db)
        alerts = service.get_audit_risk_alerts()
        
        return ResponseModel(
            success=True,
            message="Audit risk alerts retrieved",
            data=alerts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk alerts: {str(e)}")


@router.get("/dashboard")
async def get_audit_risk_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive audit risk dashboard data"""
    try:
        service = AuditRiskService(db)
        
        # Get all dashboard data
        summary = service.get_audit_risk_summary()
        alerts = service.get_audit_risk_alerts()
        
        dashboard_data = {
            "summary": summary,
            "alerts": alerts
        }
        
        return ResponseModel(
            success=True,
            message="Audit risk dashboard data retrieved",
            data=dashboard_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {str(e)}")
