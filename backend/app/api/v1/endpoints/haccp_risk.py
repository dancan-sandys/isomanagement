from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.schemas.common import ResponseModel
from app.services.haccp_risk_service import HACCPRiskService
from app.utils.audit import audit_event

router = APIRouter()


@router.post("/hazards/{hazard_id}/assess")
async def assess_hazard_risk(
    hazard_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform comprehensive risk assessment for a HACCP hazard"""
    try:
        service = HACCPRiskService(db)
        assessment_data["assessor_id"] = current_user.id
        assessment = service.assess_hazard_risk(hazard_id, assessment_data)
        
        try:
            audit_event(db, current_user.id, "hazard_risk_assessed", "hazard", str(hazard_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Hazard risk assessment completed",
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
        raise HTTPException(status_code=500, detail=f"Failed to assess hazard risk: {str(e)}")


@router.post("/ccps/{ccp_id}/assess")
async def assess_ccp_risk(
    ccp_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform comprehensive risk assessment for a CCP"""
    try:
        service = HACCPRiskService(db)
        assessment_data["assessor_id"] = current_user.id
        assessment = service.assess_ccp_risk(ccp_id, assessment_data)
        
        try:
            audit_event(db, current_user.id, "ccp_risk_assessed", "ccp", str(ccp_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="CCP risk assessment completed",
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
        raise HTTPException(status_code=500, detail=f"Failed to assess CCP risk: {str(e)}")


@router.post("/prps/{prp_program_id}/assess")
async def assess_prp_risk(
    prp_program_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform comprehensive risk assessment for a PRP program"""
    try:
        service = HACCPRiskService(db)
        assessment_data["assessor_id"] = current_user.id
        assessment = service.assess_prp_risk(prp_program_id, assessment_data)
        
        try:
            audit_event(db, current_user.id, "prp_risk_assessed", "prp_program", str(prp_program_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="PRP risk assessment completed",
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
        raise HTTPException(status_code=500, detail=f"Failed to assess PRP risk: {str(e)}")


@router.post("/hazards/{hazard_id}/integrate")
async def integrate_hazard_with_risk_register(
    hazard_id: int,
    integration_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate a hazard with the risk register"""
    try:
        service = HACCPRiskService(db)
        risk_register_item_id = integration_data.get("risk_register_item_id")
        if not risk_register_item_id:
            raise HTTPException(status_code=400, detail="risk_register_item_id is required")
            
        integration_data["integrated_by"] = current_user.id
        integration = service.integrate_hazard_with_risk_register(hazard_id, risk_register_item_id, integration_data)
        
        try:
            audit_event(db, current_user.id, "hazard_risk_integrated", "hazard", str(hazard_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Hazard integrated with risk register",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate hazard: {str(e)}")


@router.post("/ccps/{ccp_id}/integrate")
async def integrate_ccp_with_risk_register(
    ccp_id: int,
    integration_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate a CCP with the risk register"""
    try:
        service = HACCPRiskService(db)
        risk_register_item_id = integration_data.get("risk_register_item_id")
        if not risk_register_item_id:
            raise HTTPException(status_code=400, detail="risk_register_item_id is required")
            
        integration_data["integrated_by"] = current_user.id
        integration = service.integrate_ccp_with_risk_register(ccp_id, risk_register_item_id, integration_data)
        
        try:
            audit_event(db, current_user.id, "ccp_risk_integrated", "ccp", str(ccp_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="CCP integrated with risk register",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate CCP: {str(e)}")


@router.post("/prps/{prp_program_id}/integrate")
async def integrate_prp_with_risk_register(
    prp_program_id: int,
    integration_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate a PRP program with the risk register"""
    try:
        service = HACCPRiskService(db)
        risk_register_item_id = integration_data.get("risk_register_item_id")
        if not risk_register_item_id:
            raise HTTPException(status_code=400, detail="risk_register_item_id is required")
            
        integration_data["integrated_by"] = current_user.id
        integration = service.integrate_prp_with_risk_register(prp_program_id, risk_register_item_id, integration_data)
        
        try:
            audit_event(db, current_user.id, "prp_risk_integrated", "prp_program", str(prp_program_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="PRP program integrated with risk register",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate PRP: {str(e)}")


@router.get("/analytics/summary")
async def get_haccp_risk_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive HACCP risk summary"""
    try:
        service = HACCPRiskService(db)
        summary = service.get_haccp_risk_summary()
        
        return ResponseModel(
            success=True,
            message="HACCP risk summary retrieved",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk summary: {str(e)}")


@router.get("/analytics/alerts")
async def get_haccp_risk_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get HACCP risk alerts and notifications"""
    try:
        service = HACCPRiskService(db)
        alerts = service.get_haccp_risk_alerts()
        
        return ResponseModel(
            success=True,
            message="HACCP risk alerts retrieved",
            data=alerts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk alerts: {str(e)}")


@router.get("/dashboard")
async def get_haccp_risk_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive HACCP risk dashboard data"""
    try:
        service = HACCPRiskService(db)
        
        # Get all dashboard data
        summary = service.get_haccp_risk_summary()
        distribution = service.get_haccp_risk_distribution()
        alerts = service.get_haccp_risk_alerts()
        
        dashboard_data = {
            "summary": summary,
            "distribution": distribution,
            "alerts": alerts
        }
        
        return ResponseModel(
            success=True,
            message="HACCP risk dashboard data retrieved",
            data=dashboard_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {str(e)}")


@router.get("/compliance/iso22000")
async def get_iso22000_compliance_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ISO 22000:2018 compliance status for risk-based thinking"""
    try:
        service = HACCPRiskService(db)
        summary = service.get_haccp_risk_summary()
        
        # Calculate compliance metrics
        total_elements = summary["total_hazards"] + summary["total_ccps"] + summary["total_prps"]
        assessed_elements = summary["hazard_assessments"] + summary["ccp_assessments"] + summary["prp_assessments"]
        
        compliance_percentage = (assessed_elements / total_elements * 100) if total_elements > 0 else 0
        
        compliance_status = {
            "overall_compliance": compliance_percentage,
            "clause_6_1_compliance": "Compliant" if compliance_percentage >= 80 else "Non-Compliant",
            "clause_8_5_compliance": "Compliant" if summary["ccp_assessments"] > 0 else "Non-Compliant",
            "risk_based_thinking": "Implemented" if assessed_elements > 0 else "Not Implemented",
            "assessment_coverage": {
                "hazards": f"{summary['hazard_assessments']}/{summary['total_hazards']}",
                "ccps": f"{summary['ccp_assessments']}/{summary['total_ccps']}",
                "prps": f"{summary['prp_assessments']}/{summary['total_prps']}"
            },
            "high_risk_items": summary["high_risk_hazards"] + summary["high_risk_ccps"],
            "overdue_reviews": summary["overdue_reviews"]
        }
        
        return ResponseModel(
            success=True,
            message="ISO 22000:2018 compliance status retrieved",
            data=compliance_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance status: {str(e)}")
