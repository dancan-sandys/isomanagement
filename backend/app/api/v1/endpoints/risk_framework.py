from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.risk import (
    RiskManagementFrameworkCreate, RiskManagementFrameworkUpdate, RiskManagementFrameworkResponse,
    RiskContextCreate, RiskContextUpdate, RiskContextResponse,
    FSMSRiskIntegrationCreate, FSMSRiskIntegrationResponse,
    RiskAssessmentCreate, RiskAssessmentResponse,
    RiskTreatmentCreate, RiskTreatmentResponse,
    RiskDashboardData, RiskAnalyticsFilter,
    RiskKPICreate, RiskKPIResponse
)
from app.services.risk_management_service import RiskManagementService
from app.utils.audit import audit_event

router = APIRouter()


@router.get("/framework")
async def get_risk_framework(
    current_user: User = Depends(require_permission("risk_opportunity:view")),
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


@router.post("/framework", response_model=ResponseModel)
async def create_risk_framework(
    framework_data: RiskManagementFrameworkCreate,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create or update the risk management framework"""
    try:
        service = RiskManagementService(db)
        framework = service.create_framework(framework_data.model_dump())
        
        try:
            audit_event(db, current_user.id, "risk_framework_created", "risk_framework", str(framework.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk management framework created/updated",
            data=RiskManagementFrameworkResponse.model_validate(framework)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create framework: {str(e)}")


@router.get("/framework/appetite")
async def get_risk_appetite(
    current_user: User = Depends(require_permission("risk_opportunity:view")),
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
    current_user: User = Depends(require_permission("risk_opportunity:view")),
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


# ============================================================================
# RISK CONTEXT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/context", response_model=ResponseModel)
async def get_risk_context(
    current_user: User = Depends(require_permission("risk_opportunity:view")),
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
            data=RiskContextResponse.model_validate(context)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve context: {str(e)}")


@router.post("/context", response_model=ResponseModel)
async def create_risk_context(
    context_data: RiskContextCreate,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create or update the risk context"""
    try:
        service = RiskManagementService(db)
        context = service.create_risk_context(context_data.model_dump())
        
        try:
            audit_event(db, current_user.id, "risk_context_created", "risk_context", str(context.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk context created/updated",
            data=RiskContextResponse.model_validate(context)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create context: {str(e)}")


# ============================================================================
# FSMS INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/fsms-integration", response_model=ResponseModel)
async def create_fsms_integration(
    integration_data: FSMSRiskIntegrationCreate,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create FSMS risk integration"""
    try:
        service = RiskManagementService(db)
        integration = service.create_fsms_integration(integration_data.model_dump(), current_user.id)
        
        try:
            audit_event(db, current_user.id, "fsms_integration_created", "fsms_integration", str(integration.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="FSMS integration created",
            data=FSMSRiskIntegrationResponse.model_validate(integration)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create integration: {str(e)}")


@router.get("/fsms-integration/{risk_id}", response_model=ResponseModel)
async def get_fsms_integrations(
    risk_id: int,
    current_user: User = Depends(require_permission("risk_opportunity:view")),
    db: Session = Depends(get_db),
):
    """Get FSMS integrations for a risk"""
    try:
        service = RiskManagementService(db)
        integrations = service.get_fsms_integrations(risk_id)
        return ResponseModel(
            success=True,
            message="FSMS integrations retrieved",
            data=[FSMSRiskIntegrationResponse.model_validate(i) for i in integrations]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve integrations: {str(e)}")


@router.post("/integrate/haccp-hazard/{hazard_id}", response_model=ResponseModel)
async def create_risk_from_haccp_hazard(
    hazard_id: int,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create risk from HACCP hazard"""
    try:
        service = RiskManagementService(db)
        risk = service.create_risk_from_haccp_hazard(hazard_id, current_user.id)
        
        try:
            audit_event(db, current_user.id, "risk_from_hazard_created", "risk", str(risk.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk created from HACCP hazard",
            data={"risk_id": risk.id, "risk_number": risk.risk_number}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create risk from hazard: {str(e)}")


@router.post("/integrate/prp-nonconformance/{prp_id}", response_model=ResponseModel)
async def create_risk_from_prp_nonconformance(
    prp_id: int,
    nonconformance_data: dict,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create risk from PRP non-conformance"""
    try:
        nonconformance_description = nonconformance_data.get("description", "PRP non-conformance identified")
        service = RiskManagementService(db)
        risk = service.create_risk_from_prp_nonconformance(prp_id, nonconformance_description, current_user.id)
        
        try:
            audit_event(db, current_user.id, "risk_from_prp_created", "risk", str(risk.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk created from PRP non-conformance",
            data={"risk_id": risk.id, "risk_number": risk.risk_number}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create risk from PRP: {str(e)}")


@router.post("/integrate/supplier-evaluation/{supplier_id}", response_model=ResponseModel)
async def create_risk_from_supplier_evaluation(
    supplier_id: int,
    evaluation_data: dict,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create risk from supplier evaluation"""
    try:
        evaluation_findings = evaluation_data.get("findings", "Supplier evaluation findings identified")
        service = RiskManagementService(db)
        risk = service.create_risk_from_supplier_evaluation(supplier_id, evaluation_findings, current_user.id)
        
        try:
            audit_event(db, current_user.id, "risk_from_supplier_created", "risk", str(risk.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk created from supplier evaluation",
            data={"risk_id": risk.id, "risk_number": risk.risk_number}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create risk from supplier: {str(e)}")


@router.post("/integrate/audit-finding/{finding_id}", response_model=ResponseModel)
async def create_risk_from_audit_finding(
    finding_id: int,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create risk from audit finding"""
    try:
        service = RiskManagementService(db)
        risk = service.create_risk_from_audit_finding(finding_id, current_user.id)
        
        try:
            audit_event(db, current_user.id, "risk_from_audit_created", "risk", str(risk.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk created from audit finding",
            data={"risk_id": risk.id, "risk_number": risk.risk_number}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create risk from audit: {str(e)}")


@router.post("/integrate/audit-opportunity/{finding_id}", response_model=ResponseModel)
async def create_opportunity_from_audit_finding(
    finding_id: int,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create opportunity from audit finding"""
    try:
        service = RiskManagementService(db)
        opportunity = service.create_opportunity_from_audit_finding(finding_id, current_user.id)
        
        try:
            audit_event(db, current_user.id, "opportunity_from_audit_created", "risk", str(opportunity.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Opportunity created from audit finding",
            data={"opportunity_id": opportunity.id, "risk_number": opportunity.risk_number}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create opportunity from audit: {str(e)}")


# ============================================================================
# RISK ASSESSMENT AND TREATMENT ENDPOINTS
# ============================================================================

@router.post("/assess", response_model=ResponseModel)
async def assess_risk(
    assessment_data: RiskAssessmentCreate,
    current_user: User = Depends(require_permission("risk_opportunity:update")),
    db: Session = Depends(get_db),
):
    """Conduct risk assessment"""
    try:
        service = RiskManagementService(db)
        assessment_data_dict = assessment_data.model_dump()
        assessment_data_dict['assessor_id'] = current_user.id
        risk = service.assess_risk(assessment_data.risk_id, assessment_data_dict)
        
        try:
            audit_event(db, current_user.id, "risk_assessed", "risk", str(assessment_data.risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk assessment completed",
            data=RiskAssessmentResponse.model_validate(risk)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess risk: {str(e)}")


@router.post("/treat", response_model=ResponseModel)
async def plan_risk_treatment(
    treatment_data: RiskTreatmentCreate,
    current_user: User = Depends(require_permission("risk_opportunity:update")),
    db: Session = Depends(get_db),
):
    """Plan risk treatment"""
    try:
        service = RiskManagementService(db)
        risk = service.plan_risk_treatment(treatment_data.risk_id, treatment_data.model_dump())
        
        try:
            audit_event(db, current_user.id, "risk_treatment_planned", "risk", str(treatment_data.risk_id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk treatment planned",
            data=RiskTreatmentResponse.model_validate(risk)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to plan treatment: {str(e)}")


# ============================================================================
# RISK ANALYTICS AND REPORTING ENDPOINTS
# ============================================================================

@router.get("/analytics", response_model=ResponseModel)
async def get_risk_analytics(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    include_opportunities: bool = True,
    current_user: User = Depends(require_permission("risk_opportunity:view")),
    db: Session = Depends(get_db),
):
    """Get comprehensive risk analytics"""
    try:
        service = RiskManagementService(db)
        filters = RiskAnalyticsFilter(
            date_from=date_from,
            date_to=date_to,
            category=category,
            severity=severity,
            status=status,
            include_opportunities=include_opportunities
        )
        analytics = service.get_risk_analytics(filters)
        return ResponseModel(
            success=True,
            message="Risk analytics retrieved",
            data=analytics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@router.get("/trends", response_model=ResponseModel)
async def get_risk_trends(
    period: str = Query("monthly", description="Trend period: weekly, monthly, quarterly"),
    periods_back: int = Query(12, description="Number of periods to include"),
    current_user: User = Depends(require_permission("risk_opportunity:view")),
    db: Session = Depends(get_db),
):
    """Get risk trends analysis"""
    try:
        service = RiskManagementService(db)
        trends = service.get_risk_trends(period, periods_back)
        return ResponseModel(
            success=True,
            message="Risk trends retrieved",
            data=trends
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trends: {str(e)}")


@router.get("/performance", response_model=ResponseModel)
async def get_risk_performance(
    current_user: User = Depends(require_permission("risk_opportunity:view")),
    db: Session = Depends(get_db),
):
    """Get risk management performance metrics"""
    try:
        service = RiskManagementService(db)
        performance = service.get_risk_performance()
        return ResponseModel(
            success=True,
            message="Risk performance metrics retrieved",
            data=performance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance: {str(e)}")


@router.get("/compliance-status", response_model=ResponseModel)
async def get_compliance_status(
    current_user: User = Depends(require_permission("risk_opportunity:view")),
    db: Session = Depends(get_db),
):
    """Get ISO compliance status"""
    try:
        service = RiskManagementService(db)
        compliance = service.get_compliance_status()
        return ResponseModel(
            success=True,
            message="Compliance status retrieved",
            data=compliance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance status: {str(e)}")


# ============================================================================
# ENHANCED KPI ENDPOINTS
# ============================================================================

@router.post("/kpis", response_model=ResponseModel)
async def create_kpi_enhanced(
    kpi_data: RiskKPICreate,
    current_user: User = Depends(require_permission("risk_opportunity:create")),
    db: Session = Depends(get_db),
):
    """Create risk KPI with proper validation"""
    try:
        service = RiskManagementService(db)
        kpi = service.create_kpi(kpi_data.model_dump())
        
        try:
            audit_event(db, current_user.id, "risk_kpi_created", "risk_kpi", str(kpi.id))
        except Exception:
            pass
            
        return ResponseModel(
            success=True,
            message="Risk KPI created",
            data=RiskKPIResponse.model_validate(kpi)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create KPI: {str(e)}")


@router.get("/kpis", response_model=ResponseModel)
async def get_kpis_enhanced(
    category: Optional[str] = None,
    current_user: User = Depends(require_permission("risk_opportunity:view")),
    db: Session = Depends(get_db),
):
    """Get KPIs with enhanced response"""
    try:
        service = RiskManagementService(db)
        kpis = service.get_kpis(category)
        return ResponseModel(
            success=True,
            message="KPIs retrieved",
            data=[RiskKPIResponse.model_validate(kpi) for kpi in kpis]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve KPIs: {str(e)}")


@router.get("/dashboard")
async def get_risk_dashboard(
    current_user: User = Depends(require_permission("risk_opportunity:view")),
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
