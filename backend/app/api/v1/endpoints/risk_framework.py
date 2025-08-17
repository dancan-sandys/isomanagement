from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.schemas.common import ResponseModel
from app.services.risk_management_service import RiskManagementService
from app.utils.audit import audit_event

router = APIRouter()


@router.get("/framework")
async def get_risk_framework(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current risk management framework"""
    try:
        service = RiskManagementService(db)
        framework = service.get_framework()
        if not framework:
            return ResponseModel(
                success=True,
                message="No risk management framework found",
                data=None
            )
        return ResponseModel(
            success=True,
            message="Risk management framework retrieved",
            data={
                "id": framework.id,
                "policy_statement": framework.policy_statement,
                "risk_appetite_statement": framework.risk_appetite_statement,
                "risk_tolerance_levels": framework.risk_tolerance_levels,
                "risk_criteria": framework.risk_criteria,
                "risk_assessment_methodology": framework.risk_assessment_methodology,
                "risk_treatment_strategies": framework.risk_treatment_strategies,
                "monitoring_review_frequency": framework.monitoring_review_frequency,
                "communication_plan": framework.communication_plan,
                "review_cycle": framework.review_cycle,
                "next_review_date": framework.next_review_date,
                "approved_by": framework.approved_by,
                "approved_at": framework.approved_at,
                "created_at": framework.created_at,
                "updated_at": framework.updated_at
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve framework: {str(e)}")


@router.post("/framework")
async def create_risk_framework(
    framework_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the risk management framework"""
    try:
        service = RiskManagementService(db)
        framework = service.create_framework(framework_data)
        
        try:
            audit_event(db, current_user.id, "risk_framework_created", "risk_framework", str(framework.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk management framework created/updated",
            data={"id": framework.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create framework: {str(e)}")


@router.get("/framework/appetite")
async def get_risk_appetite(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get risk appetite and tolerance levels"""
    try:
        service = RiskManagementService(db)
        appetite_data = service.get_risk_appetite()
        return ResponseModel(
            success=True,
            message="Risk appetite retrieved",
            data=appetite_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk appetite: {str(e)}")


@router.get("/framework/matrix")
async def get_risk_matrix(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get risk assessment matrix configuration"""
    try:
        service = RiskManagementService(db)
        matrix_data = service.get_risk_matrix()
        return ResponseModel(
            success=True,
            message="Risk matrix retrieved",
            data=matrix_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk matrix: {str(e)}")


@router.get("/context")
async def get_risk_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current risk context"""
    try:
        service = RiskManagementService(db)
        context = service.get_risk_context()
        if not context:
            return ResponseModel(
                success=True,
                message="No risk context found",
                data=None
            )
        return ResponseModel(
            success=True,
            message="Risk context retrieved",
            data={
                "id": context.id,
                "organizational_context": context.organizational_context,
                "external_context": context.external_context,
                "internal_context": context.internal_context,
                "risk_management_context": context.risk_management_context,
                "stakeholder_analysis": context.stakeholder_analysis,
                "risk_criteria": context.risk_criteria,
                "review_frequency": context.review_frequency,
                "last_review_date": context.last_review_date,
                "next_review_date": context.next_review_date,
                "created_at": context.created_at,
                "updated_at": context.updated_at
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk context: {str(e)}")


@router.post("/context")
async def create_risk_context(
    context_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the risk context"""
    try:
        service = RiskManagementService(db)
        context = service.create_risk_context(context_data)
        
        try:
            audit_event(db, current_user.id, "risk_context_created", "risk_context", str(context.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk context created/updated",
            data={"id": context.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create risk context: {str(e)}")


@router.post("/{risk_id}/assess")
async def assess_risk(
    risk_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform comprehensive risk assessment"""
    try:
        service = RiskManagementService(db)
        assessment_data["assessor_id"] = current_user.id
        risk = service.assess_risk(risk_id, assessment_data)
        
        try:
            audit_event(db, current_user.id, "risk_assessed", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk assessment completed",
            data={
                "risk_id": risk.id,
                "risk_score": risk.risk_score,
                "residual_risk_score": risk.residual_risk_score,
                "residual_risk_level": risk.residual_risk_level,
                "next_monitoring_date": risk.next_monitoring_date,
                "next_review_date": risk.next_review_date
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess risk: {str(e)}")


@router.post("/{risk_id}/treat")
async def plan_risk_treatment(
    risk_id: int,
    treatment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Plan comprehensive risk treatment"""
    try:
        service = RiskManagementService(db)
        treatment_data["approver_id"] = current_user.id
        risk = service.plan_risk_treatment(risk_id, treatment_data)
        
        try:
            audit_event(db, current_user.id, "risk_treatment_planned", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk treatment planned",
            data={
                "risk_id": risk.id,
                "treatment_strategy": risk.risk_treatment_strategy,
                "treatment_approved": risk.risk_treatment_approved
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to plan treatment: {str(e)}")


@router.post("/{risk_id}/treat/approve")
async def approve_risk_treatment(
    risk_id: int,
    approval_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve risk treatment plan"""
    try:
        service = RiskManagementService(db)
        risk = service.approve_risk_treatment(
            risk_id, 
            current_user.id, 
            approval_data.get("approval_notes")
        )
        
        try:
            audit_event(db, current_user.id, "risk_treatment_approved", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk treatment approved",
            data={
                "risk_id": risk.id,
                "treatment_approved": risk.risk_treatment_approved,
                "approval_date": risk.risk_treatment_approval_date
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve treatment: {str(e)}")


@router.post("/{risk_id}/monitor")
async def schedule_monitoring(
    risk_id: int,
    monitoring_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Schedule risk monitoring"""
    try:
        service = RiskManagementService(db)
        risk = service.schedule_monitoring(risk_id, monitoring_data)
        
        try:
            audit_event(db, current_user.id, "risk_monitoring_scheduled", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk monitoring scheduled",
            data={
                "risk_id": risk.id,
                "monitoring_frequency": risk.monitoring_frequency,
                "next_monitoring_date": risk.next_monitoring_date
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule monitoring: {str(e)}")


@router.post("/{risk_id}/review")
async def schedule_review(
    risk_id: int,
    review_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Schedule risk review"""
    try:
        service = RiskManagementService(db)
        risk = service.schedule_review(risk_id, review_data)
        
        try:
            audit_event(db, current_user.id, "risk_review_scheduled", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk review scheduled",
            data={
                "risk_id": risk.id,
                "review_frequency": risk.review_frequency,
                "next_review_date": risk.next_review_date
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule review: {str(e)}")


@router.post("/{risk_id}/review/conduct")
async def conduct_review(
    risk_id: int,
    review_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Conduct risk review"""
    try:
        service = RiskManagementService(db)
        risk = service.conduct_review(risk_id, review_data)
        
        try:
            audit_event(db, current_user.id, "risk_review_conducted", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk review conducted",
            data={
                "risk_id": risk.id,
                "last_review_date": risk.last_review_date,
                "next_review_date": risk.next_review_date,
                "review_outcome": risk.review_outcome
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to conduct review: {str(e)}")


@router.post("/{risk_id}/fsms/integrate")
async def integrate_with_fsms(
    risk_id: int,
    fsms_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Integrate risk with FSMS elements"""
    try:
        service = RiskManagementService(db)
        fsms_data["integrated_by"] = current_user.id
        integration = service.integrate_with_fsms(risk_id, fsms_data)
        
        try:
            audit_event(db, current_user.id, "risk_fsms_integrated", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk integrated with FSMS",
            data={"integration_id": integration.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to integrate with FSMS: {str(e)}")


@router.get("/{risk_id}/fsms/integrations")
async def get_fsms_integrations(
    risk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get FSMS integrations for a risk"""
    try:
        service = RiskManagementService(db)
        integrations = service.get_fsms_integrations(risk_id)
        return ResponseModel(
            success=True,
            message="FSMS integrations retrieved",
            data=[{
                "id": integration.id,
                "fsms_element": integration.fsms_element,
                "fsms_element_id": integration.fsms_element_id,
                "impact_on_fsms": integration.impact_on_fsms,
                "integration_date": integration.integration_date
            } for integration in integrations]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve FSMS integrations: {str(e)}")


@router.post("/{risk_id}/correlate")
async def correlate_risks(
    risk_id: int,
    correlation_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create risk correlation"""
    try:
        service = RiskManagementService(db)
        correlated_risk_id = correlation_data.get("correlated_risk_id")
        if not correlated_risk_id:
            raise HTTPException(status_code=400, detail="correlated_risk_id is required")
            
        correlation_data["identified_by"] = current_user.id
        correlation = service.correlate_risks(risk_id, correlated_risk_id, correlation_data)
        
        try:
            audit_event(db, current_user.id, "risk_correlation_created", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk correlation created",
            data={"correlation_id": correlation.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create correlation: {str(e)}")


@router.get("/{risk_id}/correlations")
async def get_risk_correlations(
    risk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get correlations for a risk"""
    try:
        service = RiskManagementService(db)
        correlations = service.get_risk_correlations(risk_id)
        return ResponseModel(
            success=True,
            message="Risk correlations retrieved",
            data=[{
                "id": correlation.id,
                "primary_risk_id": correlation.primary_risk_id,
                "correlated_risk_id": correlation.correlated_risk_id,
                "correlation_type": correlation.correlation_type,
                "correlation_strength": correlation.correlation_strength,
                "correlation_date": correlation.correlation_date
            } for correlation in correlations]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve correlations: {str(e)}")


@router.post("/{risk_id}/resources/allocate")
async def allocate_resources(
    risk_id: int,
    allocation_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allocate resources to risk treatment"""
    try:
        service = RiskManagementService(db)
        allocation_data["approver_id"] = current_user.id
        allocation = service.allocate_resources(risk_id, allocation_data)
        
        try:
            audit_event(db, current_user.id, "risk_resources_allocated", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Resources allocated",
            data={"allocation_id": allocation.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to allocate resources: {str(e)}")


@router.post("/resources/{allocation_id}/approve")
async def approve_resource_allocation(
    allocation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve resource allocation"""
    try:
        service = RiskManagementService(db)
        allocation = service.approve_resource_allocation(allocation_id, current_user.id)
        
        try:
            audit_event(db, current_user.id, "risk_resource_allocation_approved", "risk_allocation", str(allocation_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Resource allocation approved",
            data={"allocation_id": allocation.id}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve allocation: {str(e)}")


@router.post("/{risk_id}/communicate")
async def create_communication(
    risk_id: int,
    communication_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create risk communication"""
    try:
        service = RiskManagementService(db)
        communication_data["sent_by"] = current_user.id
        communication = service.create_communication(risk_id, communication_data)
        
        try:
            audit_event(db, current_user.id, "risk_communication_created", "risk", str(risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk communication created",
            data={"communication_id": communication.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create communication: {str(e)}")


@router.post("/communications/{communication_id}/send")
async def send_communication(
    communication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send risk communication"""
    try:
        service = RiskManagementService(db)
        communication = service.send_communication(communication_id)
        
        try:
            audit_event(db, current_user.id, "risk_communication_sent", "risk_communication", str(communication_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk communication sent",
            data={"communication_id": communication.id}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send communication: {str(e)}")


@router.post("/kpis")
async def create_kpi(
    kpi_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create risk KPI"""
    try:
        service = RiskManagementService(db)
        kpi = service.create_kpi(kpi_data)
        
        try:
            audit_event(db, current_user.id, "risk_kpi_created", "risk_kpi", str(kpi.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk KPI created",
            data={"kpi_id": kpi.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create KPI: {str(e)}")


@router.put("/kpis/{kpi_id}/value")
async def update_kpi_value(
    kpi_id: int,
    value_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update KPI current value"""
    try:
        service = RiskManagementService(db)
        new_value = value_data.get("value")
        if new_value is None:
            raise HTTPException(status_code=400, detail="value is required")
            
        kpi = service.update_kpi_value(kpi_id, new_value)
        
        try:
            audit_event(db, current_user.id, "risk_kpi_updated", "risk_kpi", str(kpi_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="KPI value updated",
            data={
                "kpi_id": kpi.id,
                "current_value": kpi.kpi_current_value,
                "last_updated": kpi.last_updated
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update KPI: {str(e)}")


@router.get("/kpis")
async def get_kpis(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get KPIs, optionally filtered by category"""
    try:
        service = RiskManagementService(db)
        kpis = service.get_kpis(category)
        return ResponseModel(
            success=True,
            message="KPIs retrieved",
            data=[{
                "id": kpi.id,
                "name": kpi.kpi_name,
                "description": kpi.kpi_description,
                "category": kpi.kpi_category,
                "target": kpi.kpi_target,
                "current_value": kpi.kpi_current_value,
                "unit": kpi.kpi_unit,
                "status": kpi.kpi_status
            } for kpi in kpis]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve KPIs: {str(e)}")


@router.get("/dashboard")
async def get_risk_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive risk dashboard data"""
    try:
        service = RiskManagementService(db)
        dashboard_data = service.get_risk_dashboard_data()
        return ResponseModel(
            success=True,
            message="Risk dashboard data retrieved",
            data=dashboard_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {str(e)}")
