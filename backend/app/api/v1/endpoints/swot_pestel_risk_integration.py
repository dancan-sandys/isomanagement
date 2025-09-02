from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.actions_log import SWOTAnalysis, SWOTItem, PESTELAnalysis, PESTELItem, SWOTAction, PESTELAction
from app.schemas.swot_pestel import SWOTAnalysisUpdate, PESTELAnalysisUpdate
from app.services.actions_log_service import ActionsLogService
from app.services.iso_compliance_service import ISOComplianceService

router = APIRouter()

# Risk Integration Endpoints
@router.post("/swot-analyses/{analysis_id}/link-risk/{risk_id}")
def link_swot_to_risk(
    analysis_id: int,
    risk_id: int,
    db: Session = Depends(get_db)
):
    """Link a SWOT analysis to a risk assessment for ISO compliance"""
    service = ActionsLogService(db)
    analysis = service.get_swot_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="SWOT analysis not found")
    
    # Update the analysis with risk assessment ID
    update_data = SWOTAnalysisUpdate(risk_assessment_id=risk_id)
    updated_analysis = service.update_swot_analysis(analysis_id, update_data)
    
    if not updated_analysis:
        raise HTTPException(status_code=400, detail="Failed to link risk assessment")
    
    return {
        "message": "SWOT analysis successfully linked to risk assessment",
        "analysis_id": analysis_id,
        "risk_assessment_id": risk_id,
        "linked_at": datetime.now()
    }

@router.post("/pestel-analyses/{analysis_id}/link-risk/{risk_id}")
def link_pestel_to_risk(
    analysis_id: int,
    risk_id: int,
    db: Session = Depends(get_db)
):
    """Link a PESTEL analysis to a risk assessment for ISO compliance"""
    service = ActionsLogService(db)
    analysis = service.get_pestel_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="PESTEL analysis not found")
    
    # Update the analysis with risk assessment ID
    update_data = PESTELAnalysisUpdate(risk_assessment_id=risk_id)
    updated_analysis = service.update_pestel_analysis(analysis_id, update_data)
    
    if not updated_analysis:
        raise HTTPException(status_code=400, detail="Failed to link risk assessment")
    
    return {
        "message": "PESTEL analysis successfully linked to risk assessment",
        "analysis_id": analysis_id,
        "risk_assessment_id": risk_id,
        "linked_at": datetime.now()
    }

@router.get("/swot-analyses/{analysis_id}/risk-factors")
def get_swot_risk_factors(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get risk factors identified from SWOT analysis"""
    service = ActionsLogService(db)
    analysis = service.get_swot_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="SWOT analysis not found")
    
    # Get SWOT items that have associated risks
    items_with_risks = service.db.query(SWOTItem).filter(
        and_(
            SWOTItem.analysis_id == analysis_id,
            func.json_array_length(SWOTItem.associated_risks) > 0
        )
    ).all()
    
    risk_factors = []
    for item in items_with_risks:
        risk_factors.append({
            "item_id": item.id,
            "category": item.category,
            "description": item.description,
            "impact_level": item.impact_level,
            "associated_risks": item.associated_risks,
            "mitigation_strategies": item.mitigation_strategies
        })
    
    return {
        "analysis_id": analysis_id,
        "total_risk_factors": len(risk_factors),
        "risk_factors": risk_factors,
        "risk_summary": {
            "strengths_with_risks": len([r for r in risk_factors if r["category"] == "strengths"]),
            "weaknesses_with_risks": len([r for r in risk_factors if r["category"] == "weaknesses"]),
            "opportunities_with_risks": len([r for r in risk_factors if r["category"] == "opportunities"]),
            "threats_with_risks": len([r for r in risk_factors if r["category"] == "threats"])
        }
    }

@router.get("/pestel-analyses/{analysis_id}/risk-factors")
def get_pestel_risk_factors(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get external risk factors identified from PESTEL analysis"""
    service = ActionsLogService(db)
    analysis = service.get_pestel_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="PESTEL analysis not found")
    
    # Get PESTEL items that have associated risks
    items_with_risks = service.db.query(PESTELItem).filter(
        and_(
            PESTELItem.analysis_id == analysis_id,
            func.json_array_length(PESTELItem.associated_risks) > 0
        )
    ).all()
    
    risk_factors = []
    for item in items_with_risks:
        risk_factors.append({
            "item_id": item.id,
            "category": item.category,
            "description": item.description,
            "impact_level": item.impact_level,
            "timeframe": item.timeframe,
            "associated_risks": item.associated_risks,
            "monitoring_indicators": item.monitoring_indicators,
            "adaptation_strategies": item.adaptation_strategies
        })
    
    return {
        "analysis_id": analysis_id,
        "total_external_risks": len(risk_factors),
        "external_risk_factors": risk_factors,
        "risk_summary": {
            "political_risks": len([r for r in risk_factors if r["category"] == "political"]),
            "economic_risks": len([r for r in risk_factors if r["category"] == "economic"]),
            "social_risks": len([r for r in risk_factors if r["category"] == "social"]),
            "technological_risks": len([r for r in risk_factors if r["category"] == "technological"]),
            "environmental_risks": len([r for r in risk_factors if r["category"] == "environmental"]),
            "legal_risks": len([r for r in risk_factors if r["category"] == "legal"])
        }
    }

# Strategic Planning Integration Endpoints
@router.post("/strategic-context")
def create_strategic_context(
    context_data: dict,
    db: Session = Depends(get_db)
):
    """Create or update organizational strategic context per ISO 9001:2015 Clause 4.1"""
    
    # Validate required fields for ISO compliance
    required_fields = [
        "organizational_purpose",
        "interested_parties",
        "external_issues",
        "internal_issues"
    ]
    
    missing_fields = [field for field in required_fields if field not in context_data]
    if missing_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required fields for ISO compliance: {missing_fields}"
        )
    
    # Store the strategic context (this would typically be stored in a dedicated table)
    strategic_context = {
        "id": datetime.now().timestamp(),
        "created_at": datetime.now(),
        "organizational_purpose": context_data["organizational_purpose"],
        "interested_parties": context_data["interested_parties"],
        "external_issues": context_data["external_issues"],
        "internal_issues": context_data["internal_issues"],
        "qms_scope": context_data.get("qms_scope"),
        "last_review_date": datetime.now(),
        "next_review_date": datetime.now() + timedelta(days=365),  # Annual review
        "iso_compliance_status": "compliant"
    }
    
    return {
        "message": "Strategic context created successfully",
        "strategic_context": strategic_context,
        "iso_compliance": {
            "clause": "4.1",
            "status": "compliant",
            "assessment_date": datetime.now()
        }
    }

@router.get("/strategic-context/assessment")
def assess_strategic_context_completeness(db: Session = Depends(get_db)):
    """Assess completeness of strategic context documentation for ISO compliance"""
    
    iso_service = ISOComplianceService(db)
    clause_4_1_assessment = iso_service.assess_clause_4_1_compliance()
    
    return {
        "assessment": clause_4_1_assessment,
        "iso_requirements": {
            "clause": "4.1",
            "title": "Understanding the organization and its context",
            "key_requirements": [
                "Determine external and internal issues relevant to purpose and strategic direction",
                "Monitor and review information about these issues",
                "Consider the impact of these issues on QMS intended results"
            ]
        }
    }

@router.get("/management-review-input")
def generate_management_review_input(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate management review input from SWOT/PESTEL analyses per ISO 9001:2015"""
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).isoformat()
    if not end_date:
        end_date = datetime.now().isoformat()
    
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
    
    iso_service = ISOComplianceService(db)
    management_review_input = iso_service.generate_management_review_input(start_dt, end_dt)
    
    return {
        "management_review_input": management_review_input,
        "iso_reference": {
            "clause": "9.3",
            "title": "Management review",
            "input_requirements": [
                "Status of actions from previous management reviews",
                "Changes in external and internal issues relevant to QMS",
                "Information on QMS performance and effectiveness",
                "Adequacy of resources",
                "Effectiveness of actions taken to address risks and opportunities"
            ]
        }
    }

@router.get("/continuous-monitoring/dashboard")
def get_continuous_monitoring_dashboard(db: Session = Depends(get_db)):
    """Get continuous monitoring dashboard for ISO compliance"""
    
    service = ActionsLogService(db)
    iso_service = ISOComplianceService(db)
    
    # Get current status
    swot_analytics = service.get_swot_analytics()
    pestel_analytics = service.get_pestel_analytics()
    iso_metrics = service.get_iso_compliance_metrics()
    clause_4_1_assessment = iso_service.assess_clause_4_1_compliance()
    
    # Check for overdue reviews
    now = datetime.now()
    overdue_swot = service.db.query(SWOTAnalysis).filter(
        and_(
            SWOTAnalysis.next_review_date.isnot(None),
            SWOTAnalysis.next_review_date < now,
            SWOTAnalysis.status == "active"
        )
    ).count()
    
    overdue_pestel = service.db.query(PESTELAnalysis).filter(
        and_(
            PESTELAnalysis.next_review_date.isnot(None),
            PESTELAnalysis.next_review_date < now,
            PESTELAnalysis.status == "active"
        )
    ).count()
    
    # Upcoming reviews (next 30 days)
    upcoming_swot = service.db.query(SWOTAnalysis).filter(
        and_(
            SWOTAnalysis.next_review_date.isnot(None),
            SWOTAnalysis.next_review_date >= now,
            SWOTAnalysis.next_review_date <= now + timedelta(days=30),
            SWOTAnalysis.status == "active"
        )
    ).count()
    
    upcoming_pestel = service.db.query(PESTELAnalysis).filter(
        and_(
            PESTELAnalysis.next_review_date.isnot(None),
            PESTELAnalysis.next_review_date >= now,
            PESTELAnalysis.next_review_date <= now + timedelta(days=30),
            PESTELAnalysis.status == "active"
        )
    ).count()
    
    return {
        "monitoring_dashboard": {
            "last_updated": datetime.now(),
            "swot_status": swot_analytics,
            "pestel_status": pestel_analytics,
            "iso_compliance": iso_metrics,
            "clause_4_1_assessment": clause_4_1_assessment,
            "review_status": {
                "overdue_reviews": overdue_swot + overdue_pestel,
                "upcoming_reviews": upcoming_swot + upcoming_pestel,
                "overdue_swot": overdue_swot,
                "overdue_pestel": overdue_pestel,
                "upcoming_swot": upcoming_swot,
                "upcoming_pestel": upcoming_pestel
            }
        },
        "action_items": [
            f"Review {overdue_swot + overdue_pestel} overdue analyses" if overdue_swot + overdue_pestel > 0 else None,
            f"Prepare for {upcoming_swot + upcoming_pestel} upcoming reviews" if upcoming_swot + upcoming_pestel > 0 else None,
            "Enhance strategic context documentation" if iso_metrics.clause_4_1_compliance_rate < 80 else None,
            "Improve risk integration" if iso_metrics.risk_integration_rate < 70 else None
        ],
        "compliance_alerts": [
            "ISO 9001:2015 Clause 4.1 compliance rate below 80%" if iso_metrics.clause_4_1_compliance_rate < 80 else None,
            "Multiple overdue context reviews" if overdue_swot + overdue_pestel > 5 else None,
            "Low risk integration rate" if iso_metrics.risk_integration_rate < 50 else None
        ]
    }