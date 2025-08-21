from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus,
    RiskMatrix, RiskAssessment, RiskControl, RiskLevel,
    CorrectiveAction, PRPPreventiveAction, CorrectiveActionStatus
)
from app.schemas.common import ResponseModel
from app.schemas.prp import (
    PRPProgramCreate, PRPProgramUpdate, ChecklistCreate, ChecklistUpdate,
    ChecklistItemCreate, ChecklistCompletion, NonConformanceCreate,
    ReminderCreate, ScheduleCreate, PRPReportRequest,
    RiskMatrixCreate, RiskAssessmentCreate, RiskControlCreate,
    CorrectiveActionCreate, PreventiveActionCreate
)
from app.services.prp_service import PRPService
from app.utils.audit import audit_event

router = APIRouter()


# PRP Program Management Endpoints
@router.get("/programs")
async def get_prp_programs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all PRP programs with pagination and filters"""
    try:
        query = db.query(PRPProgram)
        
        # Apply filters
        if category:
            query = query.filter(PRPProgram.category == PRPCategory(category))
        if status_filter:
            query = query.filter(PRPProgram.status == PRPStatus(status_filter))
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (PRPProgram.name.ilike(search_filter)) |
                (PRPProgram.description.ilike(search_filter)) |
                (PRPProgram.program_code.ilike(search_filter))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        programs = query.order_by(desc(PRPProgram.updated_at)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for program in programs:
            # Get creator name
            creator = db.query(User).filter(User.id == program.created_by).first()
            creator_name = creator.full_name if creator else "Unknown"
            
            # Get responsible person name
            responsible_person = None
            if program.responsible_person:
                resp_user = db.query(User).filter(User.id == program.responsible_person).first()
                responsible_person = resp_user.full_name if resp_user else "Unknown"
            
            # Get checklist count
            checklist_count = db.query(PRPChecklist).filter(PRPChecklist.program_id == program.id).count()
            
            # Get overdue checklists count
            overdue_count = db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.due_date < datetime.utcnow(),
                    PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
                )
            ).count()
            
            items.append({
                "id": program.id,
                "program_code": program.program_code,
                "name": program.name,
                "description": program.description,
                "category": program.category.value if program.category else None,
                "status": program.status.value if program.status else None,
                "objective": program.objective,
                "scope": program.scope,
                "responsible_department": program.responsible_department,
                "responsible_person": responsible_person,
                "frequency": program.frequency.value if program.frequency else None,
                "frequency_details": program.frequency_details,
                "next_due_date": program.next_due_date.isoformat() if program.next_due_date else None,
                "sop_reference": program.sop_reference,
                "checklist_count": checklist_count,
                "overdue_count": overdue_count,
                "created_by": creator_name,
                "created_at": program.created_at.isoformat() if program.created_at else None,
                "updated_at": program.updated_at.isoformat() if program.updated_at else None,
            })
        
        return ResponseModel(
            success=True,
            message="PRP programs retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve PRP programs: {str(e)}"
        )


@router.post("/programs")
async def create_prp_program(
    program_data: dict = Body(
        ...,
        example={
            "program_code": "PRP-CLN-001",
            "name": "Cleaning and Sanitation Program",
            "description": "Routine cleaning and sanitation procedures for production area.",
            "category": "cleaning_sanitation",
            "objective": "Ensure hygienic conditions to prevent contamination.",
            "scope": "All production lines and adjacent areas",
            "responsible_department": "Quality Assurance",
            "responsible_person": 1,
            "frequency": "daily",
            "frequency_details": "Every shift before start-up",
            "start_date": "2025-01-01T08:00:00",
            "sop_reference": "SOP-CS-001",
            "forms_required": "Sanitation Checklist Form",
            "records_required": "Daily Sanitation Log",
            "training_requirements": "Sanitation Level 1",
            "monitoring_frequency": "daily",
            "verification_frequency": "weekly",
            "acceptance_criteria": "No visual residues; ATP swab < threshold",
            "trend_analysis_required": False,
            "corrective_action_procedure": "Re-clean and re-verify before production resumes.",
            "escalation_procedure": "Notify QA Manager if two consecutive failures occur.",
            "preventive_action_procedure": "Review chemical concentration and employee retraining."
        },
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new PRP program"""
    try:
        # Check if program code already exists
        existing_program = db.query(PRPProgram).filter(
            PRPProgram.program_code == program_data["program_code"]
        ).first()
        
        if existing_program:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program code already exists"
            )
        
        # Calculate next due date based on frequency
        next_due_date = None
        if program_data.get("frequency") and program_data.get("start_date"):
            start_date = datetime.fromisoformat(program_data["start_date"])
            frequency = PRPFrequency(program_data["frequency"])
            
            if frequency == PRPFrequency.DAILY:
                next_due_date = start_date + timedelta(days=1)
            elif frequency == PRPFrequency.WEEKLY:
                next_due_date = start_date + timedelta(weeks=1)
            elif frequency == PRPFrequency.MONTHLY:
                next_due_date = start_date + timedelta(days=30)
            elif frequency == PRPFrequency.QUARTERLY:
                next_due_date = start_date + timedelta(days=90)
            elif frequency == PRPFrequency.SEMI_ANNUALLY:
                next_due_date = start_date + timedelta(days=180)
            elif frequency == PRPFrequency.ANNUALLY:
                next_due_date = start_date + timedelta(days=365)
        
        program = PRPProgram(
            program_code=program_data["program_code"],
            name=program_data["name"],
            description=program_data.get("description"),
            category=PRPCategory(program_data["category"]),
            status=PRPStatus.ACTIVE,
            objective=program_data.get("objective"),
            scope=program_data.get("scope"),
            responsible_department=program_data.get("responsible_department"),
            responsible_person=program_data.get("responsible_person"),
            frequency=PRPFrequency(program_data["frequency"]),
            frequency_details=program_data.get("frequency_details"),
            next_due_date=next_due_date,
            sop_reference=program_data.get("sop_reference"),
            forms_required=program_data.get("forms_required"),
            created_by=current_user.id
        )
        
        db.add(program)
        db.commit()
        db.refresh(program)
        
        resp = ResponseModel(
            success=True,
            message="PRP program created successfully",
            data={"id": program.id}
        )
        try:
            audit_event(db, current_user.id, "prp_program_created", "prp", str(program.id))
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create PRP program: {str(e)}"
        )


# PRP Checklist Management
@router.get("/programs/{program_id}/checklists")
async def get_program_checklists(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    status_filter: Optional[str] = None
):
    """Get checklists for a specific PRP program"""
    try:
        # Verify program exists
        program = db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PRP program not found"
            )
        
        query = db.query(PRPChecklist).filter(PRPChecklist.program_id == program_id)
        
        # Apply status filter
        if status_filter:
            query = query.filter(PRPChecklist.status == ChecklistStatus(status_filter))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        checklists = query.order_by(desc(PRPChecklist.scheduled_date)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for checklist in checklists:
            # Get assigned user name
            assigned_user = db.query(User).filter(User.id == checklist.assigned_to).first()
            assigned_name = assigned_user.full_name if assigned_user else "Unknown"
            
            # Get reviewer name
            reviewer_name = None
            if checklist.reviewed_by:
                reviewer = db.query(User).filter(User.id == checklist.reviewed_by).first()
                reviewer_name = reviewer.full_name if reviewer else "Unknown"
            
            items.append({
                "id": checklist.id,
                "checklist_code": checklist.checklist_code,
                "name": checklist.name,
                "description": checklist.description,
                "status": checklist.status.value if checklist.status else None,
                "scheduled_date": checklist.scheduled_date.isoformat() if checklist.scheduled_date else None,
                "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                "completed_date": checklist.completed_date.isoformat() if checklist.completed_date else None,
                "assigned_to": assigned_name,
                "reviewed_by": reviewer_name,
                "reviewed_at": checklist.reviewed_at.isoformat() if checklist.reviewed_at else None,
                "total_items": checklist.total_items,
                "passed_items": checklist.passed_items,
                "failed_items": checklist.failed_items,
                "not_applicable_items": checklist.not_applicable_items,
                "compliance_percentage": checklist.compliance_percentage,
                "corrective_actions_required": checklist.corrective_actions_required,
                "created_at": checklist.created_at.isoformat() if checklist.created_at else None,
            })
        
        return ResponseModel(
            success=True,
            message="Checklists retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve checklists: {str(e)}"
        )


@router.post("/programs/{program_id}/checklists")
async def create_checklist(
    program_id: int,
    checklist_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new checklist for a PRP program"""
    try:
        # Verify program exists
        program = db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PRP program not found"
            )
        
        # Check if checklist code already exists
        existing_checklist = db.query(PRPChecklist).filter(
            PRPChecklist.checklist_code == checklist_data["checklist_code"]
        ).first()
        
        if existing_checklist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Checklist code already exists"
            )
        
        checklist = PRPChecklist(
            program_id=program_id,
            checklist_code=checklist_data["checklist_code"],
            name=checklist_data["name"],
            description=checklist_data.get("description"),
            status=ChecklistStatus.PENDING,
            scheduled_date=datetime.fromisoformat(checklist_data["scheduled_date"]),
            due_date=datetime.fromisoformat(checklist_data["due_date"]),
            assigned_to=checklist_data["assigned_to"],
            created_by=current_user.id
        )
        
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
        
        resp = ResponseModel(
            success=True,
            message="Checklist created successfully",
            data={"id": checklist.id}
        )
        try:
            audit_event(db, current_user.id, "prp_checklist_created", "prp", str(checklist.id), {"program_id": program_id})
        except Exception:
            pass
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checklist: {str(e)}"
        )


# Update an existing checklist
@router.put("/checklists/{checklist_id}")
async def update_checklist(
    checklist_id: int,
    checklist_update: ChecklistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update checklist metadata fields (name, description, dates, assignment, comments)."""
    try:
        checklist = db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
        if not checklist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

        # Optional cross-field validation for dates
        new_scheduled = checklist_update.scheduled_date or checklist.scheduled_date
        new_due = checklist_update.due_date or checklist.due_date
        if new_scheduled and new_due and new_due <= new_scheduled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Due date must be after scheduled date")

        # Apply provided fields only
        if checklist_update.name is not None:
            checklist.name = checklist_update.name
        if checklist_update.description is not None:
            checklist.description = checklist_update.description
        if checklist_update.scheduled_date is not None:
            checklist.scheduled_date = checklist_update.scheduled_date
        if checklist_update.due_date is not None:
            checklist.due_date = checklist_update.due_date
        if checklist_update.assigned_to is not None:
            checklist.assigned_to = checklist_update.assigned_to
        if checklist_update.general_comments is not None:
            checklist.general_comments = checklist_update.general_comments

        checklist.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(checklist)

        resp = ResponseModel(
            success=True,
            message="Checklist updated successfully",
            data={
                "id": checklist.id,
                "name": checklist.name,
                "description": checklist.description,
                "scheduled_date": checklist.scheduled_date.isoformat() if checklist.scheduled_date else None,
                "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                "assigned_to": checklist.assigned_to,
                "general_comments": checklist.general_comments,
            }
        )
        try:
            audit_event(db, current_user.id, "prp_checklist_updated", "prp", str(checklist.id))
        except Exception:
            pass
        return resp

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update checklist: {str(e)}"
        )


# Get single PRP program details
@router.get("/programs/{program_id}")
async def get_prp_program_detail(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a single PRP program with ISO-relevant fields and summary stats."""
    try:
        program = db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PRP program not found")

        # Resolve user names
        creator = db.query(User).filter(User.id == program.created_by).first()
        creator_name = creator.full_name if creator else "Unknown"
        responsible_person = None
        if program.responsible_person:
            resp_user = db.query(User).filter(User.id == program.responsible_person).first()
            responsible_person = resp_user.full_name if resp_user else "Unknown"

        # Checklist stats
        total_checklists = db.query(PRPChecklist).filter(PRPChecklist.program_id == program.id).count()
        overdue_count = db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.program_id == program.id,
                PRPChecklist.due_date < datetime.utcnow(),
                PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
            )
        ).count()

        return ResponseModel(
            success=True,
            message="PRP program retrieved successfully",
            data={
                "id": program.id,
                "program_code": program.program_code,
                "name": program.name,
                "description": program.description,
                "category": program.category.value if program.category else None,
                "status": program.status.value if program.status else None,
                "objective": program.objective,
                "scope": program.scope,
                "responsible_department": program.responsible_department,
                "responsible_person": responsible_person,
                "frequency": program.frequency.value if program.frequency else None,
                "frequency_details": program.frequency_details,
                "next_due_date": program.next_due_date.isoformat() if program.next_due_date else None,
                "sop_reference": program.sop_reference,
                "forms_required": program.forms_required,
                "records_required": program.records_required,
                "training_requirements": program.training_requirements,
                "monitoring_frequency": program.monitoring_frequency,
                "verification_frequency": program.verification_frequency,
                "acceptance_criteria": program.acceptance_criteria,
                "trend_analysis_required": program.trend_analysis_required,
                "created_by": creator_name,
                "created_at": program.created_at.isoformat() if program.created_at else None,
                "updated_at": program.updated_at.isoformat() if program.updated_at else None,
                "checklist_count": total_checklists,
                "overdue_count": overdue_count,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve PRP program: {str(e)}"
        )


# PRP Dashboard Statistics
@router.get("/dashboard")
async def get_prp_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PRP dashboard statistics"""
    try:
        # Get total programs
        total_programs = db.query(PRPProgram).count()
        
        # Get active programs
        active_programs = db.query(PRPProgram).filter(PRPProgram.status == PRPStatus.ACTIVE).count()
        
        # Get total checklists
        total_checklists = db.query(PRPChecklist).count()
        
        # Get pending checklists
        pending_checklists = db.query(PRPChecklist).filter(
            PRPChecklist.status == ChecklistStatus.PENDING
        ).count()
        
        # Get overdue checklists
        overdue_checklists = db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.due_date < datetime.utcnow(),
                PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
            )
        ).count()
        
        # Get completed checklists this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_this_month = db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.status == ChecklistStatus.COMPLETED,
                PRPChecklist.completed_date >= current_month_start
            )
        ).count()
        
        # Get recent checklists
        recent_checklists = db.query(PRPChecklist).order_by(
            desc(PRPChecklist.scheduled_date)
        ).limit(5).all()
        
        return ResponseModel(
            success=True,
            message="PRP dashboard data retrieved successfully",
            data={
                "total_programs": total_programs,
                "active_programs": active_programs,
                "total_checklists": total_checklists,
                "pending_checklists": pending_checklists,
                "overdue_checklists": overdue_checklists,
                "completed_this_month": completed_this_month,
                "recent_checklists": [
                    {
                        "id": checklist.id,
                        "name": checklist.name,
                        "status": checklist.status.value if checklist.status else None,
                        "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                        "compliance_percentage": checklist.compliance_percentage,
                    } for checklist in recent_checklists
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )


# Enhanced Checklist Completion with Signature
@router.post("/checklists/{checklist_id}/complete")
async def complete_checklist(
    checklist_id: int,
    completion_data: ChecklistCompletion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a checklist with signature and timestamp logging"""
    try:
        prp_service = PRPService(db)
        checklist, non_conformance_created = prp_service.complete_checklist(
            checklist_id, completion_data, current_user.id
        )
        
        response_data = {
            "id": checklist.id,
            "status": checklist.status.value,
            "compliance_percentage": checklist.compliance_percentage,
            "completed_date": checklist.completed_date.isoformat() if checklist.completed_date else None,
            "non_conformance_created": non_conformance_created
        }
        
        if non_conformance_created:
            response_data["alert_message"] = "Non-conformance has been created due to failed items"
        
        resp = ResponseModel(
            success=True,
            message="Checklist completed successfully",
            data=response_data
        )
        try:
            audit_event(db, current_user.id, "prp_checklist_completed", "prp", str(checklist.id), {
                "non_conformance_created": non_conformance_created,
                "compliance_percentage": checklist.compliance_percentage,
            })
        except Exception:
            pass
        return resp
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete checklist: {str(e)}"
        )


# File Upload for Evidence
@router.post("/checklists/{checklist_id}/upload-evidence")
async def upload_evidence_file(
    checklist_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload evidence file for a checklist"""
    try:
        # Read file data
        file_data = await file.read()
        
        prp_service = PRPService(db)
        upload_result = prp_service.upload_evidence_file(
            checklist_id, file_data, file.filename, current_user.id
        )
        
        resp = ResponseModel(
            success=True,
            message="Evidence file uploaded successfully",
            data=upload_result
        )
        try:
            audit_event(db, current_user.id, "prp_evidence_uploaded", "prp", str(checklist_id), {
                "filename": file.filename,
                "size": upload_result.get("file_size")
            })
        except Exception:
            pass
        return resp
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload evidence file: {str(e)}"
        )


# Overdue Checklists Check
@router.get("/checklists/overdue")
async def get_overdue_checklists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all overdue checklists and create escalation notifications"""
    try:
        prp_service = PRPService(db)
        overdue_checklists = prp_service.check_overdue_checklists()
        
        items = []
        for checklist in overdue_checklists:
            # Get assigned user name
            assigned_user = db.query(User).filter(User.id == checklist.assigned_to).first()
            assigned_name = assigned_user.full_name if assigned_user else "Unknown"
            
            # Get program details
            program = db.query(PRPProgram).filter(PRPProgram.id == checklist.program_id).first()
            program_name = program.name if program else "Unknown"
            
            # Calculate days overdue
            days_overdue = (datetime.utcnow() - checklist.due_date).days
            
            items.append({
                "id": checklist.id,
                "checklist_code": checklist.checklist_code,
                "name": checklist.name,
                "program_name": program_name,
                "assigned_to": assigned_name,
                "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                "days_overdue": days_overdue,
                "status": checklist.status.value if checklist.status else None,
            })
        
        return ResponseModel(
            success=True,
            message="Overdue checklists retrieved successfully",
            data={
                "total_overdue": len(items),
                "checklists": items
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve overdue checklists: {str(e)}"
        )


# Enhanced Dashboard with Compliance Rate
@router.get("/dashboard/enhanced")
async def get_enhanced_prp_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced PRP dashboard with compliance rate and upcoming checklists"""
    try:
        prp_service = PRPService(db)
        stats = prp_service.get_prp_dashboard_stats()
        
        return ResponseModel(
            success=True,
            message="Enhanced PRP dashboard data retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve enhanced dashboard data: {str(e)}"
        )


# PRP Report Generation
@router.post("/reports")
async def generate_prp_report(
    report_request: PRPReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PRP report"""
    try:
        prp_service = PRPService(db)
        report_data = prp_service.generate_prp_report(
            program_id=report_request.program_id,
            category=report_request.category,
            date_from=report_request.date_from,
            date_to=report_request.date_to
        )
        
        # Generate unique report ID
        report_id = f"prp_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return ResponseModel(
            success=True,
            message="PRP report generated successfully",
            data={
                "report_id": report_id,
                "report_data": report_data,
                "report_type": "prp_summary",
                "format": report_request.format,
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# Non-conformance Management
@router.get("/non-conformances")
async def get_non_conformances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    severity: Optional[str] = None
):
    """Get non-conformances from failed checklists"""
    try:
        # Get checklists with corrective actions required
        query = db.query(PRPChecklist).filter(
            PRPChecklist.corrective_actions_required == True
        )
        
        if severity:
            # Filter by severity (this would need a severity field in the model)
            pass
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        checklists = query.order_by(desc(PRPChecklist.updated_at)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for checklist in checklists:
            # Get assigned user name
            assigned_user = db.query(User).filter(User.id == checklist.assigned_to).first()
            assigned_name = assigned_user.full_name if assigned_user else "Unknown"
            
            # Get program details
            program = db.query(PRPProgram).filter(PRPProgram.id == checklist.program_id).first()
            program_name = program.name if program else "Unknown"
            
            # Determine severity based on failure rate
            failure_rate = checklist.failed_items / checklist.total_items if checklist.total_items > 0 else 0
            if failure_rate >= 0.5:
                severity_level = "critical"
            elif failure_rate >= 0.3:
                severity_level = "high"
            elif failure_rate >= 0.1:
                severity_level = "medium"
            else:
                severity_level = "low"
            
            items.append({
                "id": checklist.id,
                "checklist_code": checklist.checklist_code,
                "name": checklist.name,
                "program_name": program_name,
                "assigned_to": assigned_name,
                "severity": severity_level,
                "failed_items": checklist.failed_items,
                "total_items": checklist.total_items,
                "compliance_percentage": checklist.compliance_percentage,
                "corrective_actions": checklist.corrective_actions,
                "completed_date": checklist.completed_date.isoformat() if checklist.completed_date else None,
            })
        
        return ResponseModel(
            success=True,
            message="Non-conformances retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve non-conformances: {str(e)}"
        )


# Checklist Items Management
@router.get("/checklists/{checklist_id}/items")
async def get_checklist_items(
    checklist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items for a checklist"""
    try:
        # Verify checklist exists
        checklist = db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
        if not checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        
        items = db.query(PRPChecklistItem).filter(
            PRPChecklistItem.checklist_id == checklist_id
        ).order_by(PRPChecklistItem.item_number).all()
        
        items_data = []
        for item in items:
            items_data.append({
                "id": item.id,
                "item_number": item.item_number,
                "question": item.question,
                "description": item.description,
                "response_type": item.response_type,
                "response_options": item.response_options,
                "expected_response": item.expected_response,
                "is_critical": item.is_critical,
                "points": item.points,
                "response": item.response,
                "response_value": item.response_value,
                "is_compliant": item.is_compliant,
                "comments": item.comments,
                "evidence_files": item.evidence_files,
            })
        
        return ResponseModel(
            success=True,
            message="Checklist items retrieved successfully",
            data={
                "checklist_id": checklist_id,
                "checklist_name": checklist.name,
                "items": items_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve checklist items: {str(e)}"
        )


# =============================================================================
# PRP SCHEDULER AUTOMATION ENDPOINTS
# =============================================================================

@router.post("/schedules/trigger-generation")
async def trigger_checklist_generation(
    schedule_id: Optional[int] = Query(None),
    program_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger automatic checklist generation from schedules"""
    try:
        # Build query filters
        filters = []
        if schedule_id:
            filters.append(PRPSchedule.id == schedule_id)
        if program_id:
            filters.append(PRPSchedule.program_id == program_id)

        # Get schedules that need checklist generation
        # schedules = db.query(PRPSchedule).filter(*filters).all()
        
        # Mock generation process
        generated_checklists = []
        for i in range(3):  # Mock 3 checklists generated
            checklist_data = {
                "id": 100 + i,
                "program_id": program_id or 1,
                "name": f"Auto-generated Checklist {datetime.utcnow().strftime('%Y-%m-%d')}",
                "description": "Automatically generated from schedule",
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "status": "pending",
                "generated_from_schedule": schedule_id or 1,
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": "system"
            }
            generated_checklists.append(checklist_data)

        try:
            audit_event(db, current_user.id, "prp_checklist_generation_triggered", "prp", str(schedule_id or program_id))
        except Exception:
            pass

        return ResponseModel(
            success=True,
            message=f"Successfully triggered generation of {len(generated_checklists)} checklists",
            data={
                "generated_checklists": generated_checklists,
                "triggered_by": current_user.id,
                "triggered_at": datetime.utcnow().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger checklist generation: {str(e)}"
        )


@router.get("/schedules/next-due")
async def get_next_due_checklists(
    days_ahead: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get checklists due in the next X days"""
    try:
        # Calculate date range
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Mock due checklists
        due_checklists = [
            {
                "id": 1,
                "program_name": "Daily Cleaning",
                "checklist_name": "Production Area Cleaning",
                "due_date": (start_date + timedelta(days=1)).isoformat(),
                "days_until_due": 1,
                "priority": "high",
                "assigned_to": "cleaning_team"
            },
            {
                "id": 2,
                "program_name": "Weekly Maintenance",
                "checklist_name": "Equipment Calibration Check",
                "due_date": (start_date + timedelta(days=3)).isoformat(),
                "days_until_due": 3,
                "priority": "medium",
                "assigned_to": "maintenance_team"
            }
        ]

        return ResponseModel(
            success=True,
            message=f"Found {len(due_checklists)} checklists due in next {days_ahead} days",
            data={
                "due_checklists": due_checklists,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_ahead": days_ahead
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get due checklists: {str(e)}"
        )


@router.post("/schedules/bulk-update")
async def bulk_update_schedules(
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update PRP schedules"""
    try:
        schedule_ids = update_data.get("schedule_ids", [])
        update_fields = update_data.get("update_fields", {})
        
        if not schedule_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schedule_ids is required"
            )

        # Validate update fields
        allowed_fields = ["frequency", "auto_generate", "is_active", "start_date"]
        for field in update_fields:
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field '{field}' not allowed for bulk update"
                )

        # Mock bulk update
        updated_count = len(schedule_ids)
        
        try:
            audit_event(db, current_user.id, "prp_schedules_bulk_updated", "prp", str(schedule_ids))
        except Exception:
            pass

        return ResponseModel(
            success=True,
            message=f"Successfully updated {updated_count} schedules",
            data={
                "updated_schedules": schedule_ids,
                "update_fields": update_fields,
                "updated_by": current_user.id,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update schedules: {str(e)}"
        ) 

# Risk Assessment Endpoints (Phase 2.1)
@router.get("/risk-matrices")
async def get_risk_matrices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    is_default: Optional[bool] = None
):
    """Get all risk matrices with pagination and filters"""
    try:
        query = db.query(RiskMatrix)
        
        # Apply filters
        if is_default is not None:
            query = query.filter(RiskMatrix.is_default == is_default)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        matrices = query.order_by(desc(RiskMatrix.created_at)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for matrix in matrices:
            # Get creator name
            creator = db.query(User).filter(User.id == matrix.created_by).first()
            
            items.append({
                "id": matrix.id,
                "name": matrix.name,
                "description": matrix.description,
                "likelihood_levels": matrix.likelihood_levels,
                "severity_levels": matrix.severity_levels,
                "risk_levels": matrix.risk_levels,
                "is_default": getattr(matrix, 'is_default', False),
                "created_by": creator.full_name if creator else "Unknown",
                "created_at": matrix.created_at.isoformat() if matrix.created_at else None,
                "updated_at": matrix.updated_at.isoformat() if matrix.updated_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Risk matrices retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk matrices: {str(e)}"
        )


@router.post("/risk-matrices")
async def create_risk_matrix(
    matrix_data: RiskMatrixCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new risk matrix"""
    try:
        prp_service = PRPService(db)
        matrix = prp_service.create_risk_matrix(matrix_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Risk matrix created successfully",
            data={
                "id": matrix.id,
                "name": matrix.name,
                "description": matrix.description,
                "likelihood_levels": matrix.likelihood_levels,
                "severity_levels": matrix.severity_levels,
                "risk_levels": matrix.risk_levels,
                "is_default": getattr(matrix, 'is_default', False),
                "created_at": matrix.created_at.isoformat() if matrix.created_at else None
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
            detail=f"Failed to create risk matrix: {str(e)}"
        )


@router.get("/programs/{program_id}/risk-assessments")
async def get_program_risk_assessments(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    risk_level: Optional[str] = None,
    escalated: Optional[bool] = None
):
    """Get risk assessments for a specific PRP program"""
    try:
        # Verify program exists
        program = db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PRP program not found"
            )
        
        query = db.query(RiskAssessment).filter(RiskAssessment.program_id == program_id)
        
        # Apply filters
        if risk_level:
            query = query.filter(RiskAssessment.risk_level == RiskLevel(risk_level))
        if escalated is not None:
            query = query.filter(RiskAssessment.escalated_to_risk_register == escalated)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        assessments = query.order_by(desc(RiskAssessment.assessment_date)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for assessment in assessments:
            # Get creator name
            creator = db.query(User).filter(User.id == assessment.created_by).first()
            
            items.append({
                "id": assessment.id,
                "assessment_code": assessment.assessment_code,
                "hazard_identified": assessment.hazard_identified,
                "hazard_description": assessment.hazard_description,
                "likelihood_level": assessment.likelihood_level,
                "severity_level": assessment.severity_level,
                "risk_level": assessment.risk_level.value if assessment.risk_level else None,
                "risk_score": assessment.risk_score,
                "acceptability": assessment.acceptability,
                "existing_controls": assessment.existing_controls,
                "additional_controls_required": assessment.additional_controls_required,
                "control_effectiveness": assessment.control_effectiveness,
                "residual_risk_level": assessment.residual_risk_level.value if assessment.residual_risk_level else None,
                "residual_risk_score": assessment.residual_risk_score,
                "assessment_date": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
                "next_review_date": assessment.next_review_date.isoformat() if assessment.next_review_date else None,
                "escalated_to_risk_register": assessment.escalated_to_risk_register,
                "escalation_date": assessment.escalation_date.isoformat() if assessment.escalation_date else None,
                "risk_register_entry_id": getattr(assessment, 'risk_register_entry_id', None),
                "created_by": creator.full_name if creator else "Unknown",
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
                "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Risk assessments retrieved successfully",
            data={
                "program_id": program_id,
                "program_name": program.name,
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk assessments: {str(e)}"
        )


@router.post("/programs/{program_id}/risk-assessments")
async def create_risk_assessment(
    program_id: int,
    assessment_data: RiskAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new risk assessment for a PRP program"""
    try:
        # Verify program exists
        program = db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PRP program not found"
            )
        
        prp_service = PRPService(db)
        assessment = prp_service.create_risk_assessment(program_id, assessment_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Risk assessment created successfully",
            data={
                "id": assessment.id,
                "assessment_code": assessment.assessment_code,
                "hazard_identified": assessment.hazard_identified,
                "hazard_description": assessment.hazard_description,
                "likelihood_level": assessment.likelihood_level,
                "severity_level": assessment.severity_level,
                "risk_level": assessment.risk_level.value if assessment.risk_level else None,
                "risk_score": assessment.risk_score,
                "acceptability": assessment.acceptability,
                "existing_controls": assessment.existing_controls,
                "additional_controls_required": assessment.additional_controls_required,
                "control_effectiveness": assessment.control_effectiveness,
                "residual_risk_level": assessment.residual_risk_level.value if assessment.residual_risk_level else None,
                "residual_risk_score": assessment.residual_risk_score,
                "assessment_date": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
                "next_review_date": assessment.next_review_date.isoformat() if assessment.next_review_date else None,
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None
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
            detail=f"Failed to create risk assessment: {str(e)}"
        )


@router.put("/risk-assessments/{assessment_id}")
async def update_risk_assessment(
    assessment_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a risk assessment"""
    try:
        prp_service = PRPService(db)
        assessment = prp_service.update_risk_assessment(assessment_id, assessment_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Risk assessment updated successfully",
            data={
                "id": assessment.id,
                "assessment_code": assessment.assessment_code,
                "hazard_identified": assessment.hazard_identified,
                "hazard_description": assessment.hazard_description,
                "likelihood_level": assessment.likelihood_level,
                "severity_level": assessment.severity_level,
                "risk_level": assessment.risk_level.value if assessment.risk_level else None,
                "risk_score": assessment.risk_score,
                "acceptability": assessment.acceptability,
                "existing_controls": assessment.existing_controls,
                "additional_controls_required": assessment.additional_controls_required,
                "control_effectiveness": assessment.control_effectiveness,
                "residual_risk_level": assessment.residual_risk_level.value if assessment.residual_risk_level else None,
                "residual_risk_score": assessment.residual_risk_score,
                "assessment_date": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
                "next_review_date": assessment.next_review_date.isoformat() if assessment.next_review_date else None,
                "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None
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
            detail=f"Failed to update risk assessment: {str(e)}"
        )


@router.get("/risk-assessments/{assessment_id}/controls")
async def get_risk_controls(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    status_filter: Optional[str] = None
):
    """Get risk controls for a specific risk assessment"""
    try:
        # Verify assessment exists
        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk assessment not found"
            )
        
        query = db.query(RiskControl).filter(RiskControl.risk_assessment_id == assessment_id)
        
        # Apply status filter
        if status_filter:
            query = query.filter(RiskControl.implementation_status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        controls = query.order_by(desc(RiskControl.created_at)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for control in controls:
            # Get responsible person name
            responsible_person = db.query(User).filter(User.id == control.responsible_person).first()
            
            items.append({
                "id": control.id,
                "control_code": control.control_code,
                "control_type": control.control_type,
                "control_description": control.control_description,
                "control_procedure": control.control_procedure,
                "responsible_person": responsible_person.full_name if responsible_person else "Unknown",
                "responsible_person_id": control.responsible_person,
                "implementation_date": control.implementation_date.isoformat() if control.implementation_date else None,
                "frequency": control.frequency.value if control.frequency else None,
                "effectiveness_measure": control.effectiveness_measure,
                "effectiveness_threshold": control.effectiveness_threshold,
                "effectiveness_score": control.effectiveness_score,
                "is_implemented": control.is_implemented,
                "implementation_status": control.implementation_status,
                "created_at": control.created_at.isoformat() if control.created_at else None,
                "updated_at": control.updated_at.isoformat() if control.updated_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Risk controls retrieved successfully",
            data={
                "assessment_id": assessment_id,
                "assessment_code": assessment.assessment_code,
                "hazard_identified": assessment.hazard_identified,
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk controls: {str(e)}"
        )


@router.post("/risk-assessments/{assessment_id}/controls")
async def add_risk_control(
    assessment_id: int,
    control_data: RiskControlCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a risk control to a risk assessment"""
    try:
        # Verify assessment exists
        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk assessment not found"
            )
        
        prp_service = PRPService(db)
        control = prp_service.add_risk_control(assessment_id, control_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Risk control added successfully",
            data={
                "id": control.id,
                "control_code": control.control_code,
                "control_type": control.control_type,
                "control_description": control.control_description,
                "control_procedure": control.control_procedure,
                "responsible_person": control.responsible_person,
                "implementation_date": control.implementation_date.isoformat() if control.implementation_date else None,
                "frequency": control.frequency.value if control.frequency else None,
                "effectiveness_measure": control.effectiveness_measure,
                "effectiveness_threshold": control.effectiveness_threshold,
                "effectiveness_score": control.effectiveness_score,
                "is_implemented": control.is_implemented,
                "implementation_status": control.implementation_status,
                "created_at": control.created_at.isoformat() if control.created_at else None
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
            detail=f"Failed to add risk control: {str(e)}"
        )


@router.post("/risk-assessments/{assessment_id}/escalate")
async def escalate_risk_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Escalate a risk assessment to the main risk register"""
    try:
        prp_service = PRPService(db)
        result = prp_service.escalate_risk_to_register(assessment_id, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Risk assessment escalated successfully",
            data=result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to escalate risk assessment: {str(e)}"
        )


@router.get("/risk-assessments")
async def get_all_risk_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    program_id: Optional[int] = None,
    risk_level: Optional[str] = None,
    escalated: Optional[bool] = None
):
    """Get all risk assessments with optional filtering"""
    try:
        query = db.query(RiskAssessment)
        
        # Apply filters
        if program_id:
            query = query.filter(RiskAssessment.program_id == program_id)
        if risk_level:
            query = query.filter(RiskAssessment.risk_level == RiskLevel(risk_level))
        if escalated is not None:
            query = query.filter(RiskAssessment.escalated_to_risk_register == escalated)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        assessments = query.order_by(desc(RiskAssessment.assessment_date)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for assessment in assessments:
            # Get program details
            program = db.query(PRPProgram).filter(PRPProgram.id == assessment.program_id).first()
            
            # Get creator name
            creator = db.query(User).filter(User.id == assessment.created_by).first()
            
            items.append({
                "id": assessment.id,
                "assessment_code": assessment.assessment_code,
                "program": {
                    "id": program.id if program else None,
                    "name": program.name if program else None,
                    "program_code": program.program_code if program else None,
                    "category": program.category.value if program else None
                },
                "hazard_identified": assessment.hazard_identified,
                "hazard_description": assessment.hazard_description,
                "likelihood_level": assessment.likelihood_level,
                "severity_level": assessment.severity_level,
                "risk_level": assessment.risk_level.value if assessment.risk_level else None,
                "risk_score": assessment.risk_score,
                "acceptability": assessment.acceptability,
                "existing_controls": assessment.existing_controls,
                "additional_controls_required": assessment.additional_controls_required,
                "control_effectiveness": assessment.control_effectiveness,
                "residual_risk_level": assessment.residual_risk_level.value if assessment.residual_risk_level else None,
                "residual_risk_score": assessment.residual_risk_score,
                "assessment_date": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
                "next_review_date": assessment.next_review_date.isoformat() if assessment.next_review_date else None,
                "escalated_to_risk_register": assessment.escalated_to_risk_register,
                "escalation_date": assessment.escalation_date.isoformat() if assessment.escalation_date else None,
                "created_by": creator.full_name if creator else "Unknown",
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
                "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Risk assessments retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk assessments: {str(e)}"
        )


@router.get("/risk-assessments/{assessment_id}")
async def get_risk_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific risk assessment with full details"""
    try:
        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk assessment not found"
            )
        
        # Get program details
        program = db.query(PRPProgram).filter(PRPProgram.id == assessment.program_id).first()
        
        # Get creator name
        creator = db.query(User).filter(User.id == assessment.created_by).first()
        
        # Get escalated by name if escalated
        escalated_by = None
        if assessment.escalated_by:
            escalated_by_user = db.query(User).filter(User.id == assessment.escalated_by).first()
            escalated_by = escalated_by_user.full_name if escalated_by_user else "Unknown"
        
        # Get risk controls
        controls = db.query(RiskControl).filter(RiskControl.risk_assessment_id == assessment_id).all()
        control_items = []
        for control in controls:
            responsible_person = db.query(User).filter(User.id == control.responsible_person).first()
            control_items.append({
                "id": control.id,
                "control_code": control.control_code,
                "control_type": control.control_type,
                "control_description": control.control_description,
                "control_procedure": control.control_procedure,
                "responsible_person": responsible_person.full_name if responsible_person else "Unknown",
                "responsible_person_id": control.responsible_person,
                "implementation_date": control.implementation_date.isoformat() if control.implementation_date else None,
                "frequency": control.frequency.value if control.frequency else None,
                "effectiveness_measure": control.effectiveness_measure,
                "effectiveness_threshold": control.effectiveness_threshold,
                "effectiveness_score": control.effectiveness_score,
                "is_implemented": control.is_implemented,
                "implementation_status": control.implementation_status,
                "created_at": control.created_at.isoformat() if control.created_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Risk assessment retrieved successfully",
            data={
                "id": assessment.id,
                "assessment_code": assessment.assessment_code,
                "program": {
                    "id": program.id if program else None,
                    "name": program.name if program else None,
                    "program_code": program.program_code if program else None,
                    "category": program.category.value if program else None
                },
                "hazard_identified": assessment.hazard_identified,
                "hazard_description": assessment.hazard_description,
                "likelihood_level": assessment.likelihood_level,
                "severity_level": assessment.severity_level,
                "risk_level": assessment.risk_level.value if assessment.risk_level else None,
                "risk_score": assessment.risk_score,
                "acceptability": assessment.acceptability,
                "existing_controls": assessment.existing_controls,
                "additional_controls_required": assessment.additional_controls_required,
                "control_effectiveness": assessment.control_effectiveness,
                "residual_risk_level": assessment.residual_risk_level.value if assessment.residual_risk_level else None,
                "residual_risk_score": assessment.residual_risk_score,
                "assessment_date": assessment.assessment_date.isoformat() if assessment.assessment_date else None,
                "next_review_date": assessment.next_review_date.isoformat() if assessment.next_review_date else None,
                "escalated_to_risk_register": assessment.escalated_to_risk_register,
                "escalation_date": assessment.escalation_date.isoformat() if assessment.escalation_date else None,
                "escalated_by": escalated_by,
                "risk_register_entry_id": getattr(assessment, 'risk_register_entry_id', None),
                "created_by": creator.full_name if creator else "Unknown",
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
                "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None,
                "controls": control_items
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk assessment: {str(e)}"
        ) 

# Corrective Action Endpoints (Phase 2.2)
@router.get("/corrective-actions")
async def get_corrective_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    status_filter: Optional[str] = None,
    severity: Optional[str] = None,
    source_type: Optional[str] = None
):
    """Get all corrective actions with pagination and filters"""
    try:
        query = db.query(CorrectiveAction)
        
        # Apply filters
        if status_filter:
            query = query.filter(CorrectiveAction.status == CorrectiveActionStatus(status_filter))
        if severity:
            query = query.filter(CorrectiveAction.severity == severity)
        if source_type:
            query = query.filter(CorrectiveAction.source_type == source_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        actions = query.order_by(desc(CorrectiveAction.created_at)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for action in actions:
            # Get responsible person name
            responsible_person = db.query(User).filter(User.id == action.responsible_person).first()
            assigned_person = db.query(User).filter(User.id == action.assigned_to).first()
            
            items.append({
                "id": action.id,
                "action_code": action.action_code,
                "source_type": action.source_type,
                "source_id": action.source_id,
                "checklist_id": action.checklist_id,
                "non_conformance_description": action.non_conformance_description,
                "non_conformance_date": action.non_conformance_date.isoformat() if action.non_conformance_date else None,
                "severity": action.severity,
                "immediate_cause": action.immediate_cause,
                "root_cause_analysis": action.root_cause_analysis,
                "root_cause_category": action.root_cause_category,
                "action_description": action.action_description,
                "action_type": action.action_type,
                "responsible_person": responsible_person.full_name if responsible_person else "Unknown",
                "responsible_person_id": action.responsible_person,
                "assigned_to": assigned_person.full_name if assigned_person else "Unknown",
                "assigned_to_id": action.assigned_to,
                "target_completion_date": action.target_completion_date.isoformat() if action.target_completion_date else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "effectiveness_criteria": action.effectiveness_criteria,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "status": action.status.value if action.status else None,
                "created_at": action.created_at.isoformat() if action.created_at else None,
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Corrective actions retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve corrective actions: {str(e)}"
        )


@router.post("/corrective-actions")
async def create_corrective_action(
    action_data: CorrectiveActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new corrective action"""
    try:
        prp_service = PRPService(db)
        action = prp_service.create_corrective_action(action_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Corrective action created successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "source_type": action.source_type,
                "source_id": action.source_id,
                "checklist_id": action.checklist_id,
                "non_conformance_description": action.non_conformance_description,
                "non_conformance_date": action.non_conformance_date.isoformat() if action.non_conformance_date else None,
                "severity": action.severity,
                "action_description": action.action_description,
                "action_type": action.action_type,
                "responsible_person": action.responsible_person,
                "assigned_to": action.assigned_to,
                "target_completion_date": action.target_completion_date.isoformat() if action.target_completion_date else None,
                "status": action.status.value if action.status else None,
                "created_at": action.created_at.isoformat() if action.created_at else None
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
            detail=f"Failed to create corrective action: {str(e)}"
        )


@router.get("/corrective-actions/{action_id}")
async def get_corrective_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific corrective action with full details"""
    try:
        action = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corrective action not found"
            )
        
        # Get user names
        responsible_person = db.query(User).filter(User.id == action.responsible_person).first()
        assigned_person = db.query(User).filter(User.id == action.assigned_to).first()
        creator = db.query(User).filter(User.id == action.created_by).first()
        
        # Get source details if available
        source_details = None
        if action.source_type == "checklist" and action.checklist_id:
            checklist = db.query(PRPChecklist).filter(PRPChecklist.id == action.checklist_id).first()
            if checklist:
                source_details = {
                    "id": checklist.id,
                    "name": checklist.name,
                    "checklist_code": checklist.checklist_code,
                    "program_id": checklist.program_id
                }
        
        return ResponseModel(
            success=True,
            message="Corrective action retrieved successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "source_type": action.source_type,
                "source_id": action.source_id,
                "source_details": source_details,
                "checklist_id": action.checklist_id,
                "non_conformance_description": action.non_conformance_description,
                "non_conformance_date": action.non_conformance_date.isoformat() if action.non_conformance_date else None,
                "severity": action.severity,
                "immediate_cause": action.immediate_cause,
                "root_cause_analysis": action.root_cause_analysis,
                "root_cause_category": action.root_cause_category,
                "action_description": action.action_description,
                "action_type": action.action_type,
                "responsible_person": responsible_person.full_name if responsible_person else "Unknown",
                "responsible_person_id": action.responsible_person,
                "assigned_to": assigned_person.full_name if assigned_person else "Unknown",
                "assigned_to_id": action.assigned_to,
                "target_completion_date": action.target_completion_date.isoformat() if action.target_completion_date else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "effectiveness_criteria": action.effectiveness_criteria,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "status": action.status.value if action.status else None,
                "created_by": creator.full_name if creator else "Unknown",
                "created_at": action.created_at.isoformat() if action.created_at else None,
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve corrective action: {str(e)}"
        )


@router.put("/corrective-actions/{action_id}")
async def update_corrective_action(
    action_id: int,
    action_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a corrective action"""
    try:
        prp_service = PRPService(db)
        action = prp_service.update_corrective_action(action_id, action_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Corrective action updated successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "status": action.status.value if action.status else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
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
            detail=f"Failed to update corrective action: {str(e)}"
        )


@router.post("/corrective-actions/{action_id}/complete")
async def complete_corrective_action(
    action_id: int,
    completion_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a corrective action with effectiveness evaluation"""
    try:
        prp_service = PRPService(db)
        action = prp_service.complete_corrective_action(
            action_id, 
            completion_data.get("effectiveness_evaluation"),
            completion_data.get("actual_completion_date"),
            current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Corrective action completed successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "status": action.status.value if action.status else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "completed_by": current_user.id,
                "completed_at": action.updated_at.isoformat() if action.updated_at else None
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
            detail=f"Failed to complete corrective action: {str(e)}"
        )


# Preventive Action Endpoints
@router.get("/preventive-actions")
async def get_preventive_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    status_filter: Optional[str] = None,
    trigger_type: Optional[str] = None
):
    """Get all preventive actions with pagination and filters"""
    try:
        query = db.query(PRPPreventiveAction)
        
        # Apply filters
        if status_filter:
            query = query.filter(PRPPreventiveAction.status == CorrectiveActionStatus(status_filter))
        if trigger_type:
            query = query.filter(PRPPreventiveAction.trigger_type == trigger_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        actions = query.order_by(desc(PRPPreventiveAction.created_at)).offset((page - 1) * size).limit(size).all()
        
        items = []
        for action in actions:
            # Get user names
            responsible_person = db.query(User).filter(User.id == action.responsible_person).first()
            assigned_person = db.query(User).filter(User.id == action.assigned_to).first()
            
            items.append({
                "id": action.id,
                "action_code": action.action_code,
                "trigger_type": action.trigger_type,
                "trigger_description": action.trigger_description,
                "action_description": action.action_description,
                "objective": action.objective,
                "responsible_person": responsible_person.full_name if responsible_person else "Unknown",
                "responsible_person_id": action.responsible_person,
                "assigned_to": assigned_person.full_name if assigned_person else "Unknown",
                "assigned_to_id": action.assigned_to,
                "implementation_plan": action.implementation_plan,
                "resources_required": action.resources_required,
                "budget_estimate": action.budget_estimate,
                "planned_start_date": action.planned_start_date.isoformat() if action.planned_start_date else None,
                "planned_completion_date": action.planned_completion_date.isoformat() if action.planned_completion_date else None,
                "actual_start_date": action.actual_start_date.isoformat() if action.actual_start_date else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "success_criteria": action.success_criteria,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "status": action.status.value if action.status else None,
                "created_at": action.created_at.isoformat() if action.created_at else None,
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
            })
        
        return ResponseModel(
            success=True,
            message="Preventive actions retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preventive actions: {str(e)}"
        )


@router.post("/preventive-actions")
async def create_preventive_action(
    action_data: PreventiveActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new preventive action"""
    try:
        prp_service = PRPService(db)
        action = prp_service.create_preventive_action(action_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Preventive action created successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "trigger_type": action.trigger_type,
                "trigger_description": action.trigger_description,
                "action_description": action.action_description,
                "objective": action.objective,
                "responsible_person": action.responsible_person,
                "assigned_to": action.assigned_to,
                "implementation_plan": action.implementation_plan,
                "resources_required": action.resources_required,
                "budget_estimate": action.budget_estimate,
                "planned_start_date": action.planned_start_date.isoformat() if action.planned_start_date else None,
                "planned_completion_date": action.planned_completion_date.isoformat() if action.planned_completion_date else None,
                "success_criteria": action.success_criteria,
                "status": action.status.value if action.status else None,
                "created_at": action.created_at.isoformat() if action.created_at else None
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
            detail=f"Failed to create preventive action: {str(e)}"
        )


@router.get("/preventive-actions/{action_id}")
async def get_preventive_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific preventive action with full details"""
    try:
        action = db.query(PRPPreventiveAction).filter(PRPPreventiveAction.id == action_id).first()
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preventive action not found"
            )
        
        # Get user names
        responsible_person = db.query(User).filter(User.id == action.responsible_person).first()
        assigned_person = db.query(User).filter(User.id == action.assigned_to).first()
        creator = db.query(User).filter(User.id == action.created_by).first()
        
        return ResponseModel(
            success=True,
            message="Preventive action retrieved successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "trigger_type": action.trigger_type,
                "trigger_description": action.trigger_description,
                "action_description": action.action_description,
                "objective": action.objective,
                "responsible_person": responsible_person.full_name if responsible_person else "Unknown",
                "responsible_person_id": action.responsible_person,
                "assigned_to": assigned_person.full_name if assigned_person else "Unknown",
                "assigned_to_id": action.assigned_to,
                "implementation_plan": action.implementation_plan,
                "resources_required": action.resources_required,
                "budget_estimate": action.budget_estimate,
                "planned_start_date": action.planned_start_date.isoformat() if action.planned_start_date else None,
                "planned_completion_date": action.planned_completion_date.isoformat() if action.planned_completion_date else None,
                "actual_start_date": action.actual_start_date.isoformat() if action.actual_start_date else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "success_criteria": action.success_criteria,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "status": action.status.value if action.status else None,
                "created_by": creator.full_name if creator else "Unknown",
                "created_at": action.created_at.isoformat() if action.created_at else None,
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preventive action: {str(e)}"
        )


@router.put("/preventive-actions/{action_id}")
async def update_preventive_action(
    action_id: int,
    action_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a preventive action"""
    try:
        prp_service = PRPService(db)
        action = prp_service.update_preventive_action(action_id, action_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Preventive action updated successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "status": action.status.value if action.status else None,
                "actual_start_date": action.actual_start_date.isoformat() if action.actual_start_date else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
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
            detail=f"Failed to update preventive action: {str(e)}"
        )


@router.post("/preventive-actions/{action_id}/start")
async def start_preventive_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start implementation of a preventive action"""
    try:
        prp_service = PRPService(db)
        action = prp_service.start_preventive_action(action_id, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Preventive action started successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "status": action.status.value if action.status else None,
                "actual_start_date": action.actual_start_date.isoformat() if action.actual_start_date else None,
                "started_by": current_user.id,
                "started_at": action.updated_at.isoformat() if action.updated_at else None
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
            detail=f"Failed to start preventive action: {str(e)}"
        )


@router.post("/preventive-actions/{action_id}/complete")
async def complete_preventive_action(
    action_id: int,
    completion_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a preventive action with effectiveness evaluation"""
    try:
        prp_service = PRPService(db)
        action = prp_service.complete_preventive_action(
            action_id,
            completion_data.get("effectiveness_evaluation"),
            completion_data.get("actual_completion_date"),
            current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Preventive action completed successfully",
            data={
                "id": action.id,
                "action_code": action.action_code,
                "status": action.status.value if action.status else None,
                "actual_completion_date": action.actual_completion_date.isoformat() if action.actual_completion_date else None,
                "effectiveness_evaluation": getattr(action, 'effectiveness_evaluation', None),
                "completed_by": current_user.id,
                "completed_at": action.updated_at.isoformat() if action.updated_at else None
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
            detail=f"Failed to complete preventive action: {str(e)}"
        )


# CAPA Dashboard and Analytics
@router.get("/capa/dashboard")
async def get_capa_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CAPA dashboard statistics and analytics"""
    try:
        prp_service = PRPService(db)
        stats = prp_service.get_capa_dashboard_stats()
        
        return ResponseModel(
            success=True,
            message="CAPA dashboard data retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CAPA dashboard data: {str(e)}"
        )


@router.get("/capa/overdue")
async def get_overdue_capa_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    action_type: Optional[str] = None  # "corrective" or "preventive"
):
    """Get overdue CAPA actions"""
    try:
        prp_service = PRPService(db)
        overdue_actions = prp_service.get_overdue_capa_actions(action_type)
        
        return ResponseModel(
            success=True,
            message="Overdue CAPA actions retrieved successfully",
            data={
                "total_overdue": len(overdue_actions),
                "actions": overdue_actions
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve overdue CAPA actions: {str(e)}"
        )


@router.post("/capa/reports")
async def generate_capa_report(
    report_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate CAPA report"""
    try:
        prp_service = PRPService(db)
        report_data = prp_service.generate_capa_report(
            action_type=report_request.get("action_type"),
            date_from=report_request.get("date_from"),
            date_to=report_request.get("date_to"),
            status=report_request.get("status"),
            severity=report_request.get("severity")
        )
        
        # Generate unique report ID
        report_id = f"capa_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return ResponseModel(
            success=True,
            message="CAPA report generated successfully",
            data={
                "report_id": report_id,
                "report_data": report_data,
                "report_type": "capa_summary",
                "format": report_request.get("format", "json"),
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CAPA report: {str(e)}"
        ) 

# Phase 2.3: Enhanced Program Management Endpoints

# Advanced Program Management
@router.get("/programs/{program_id}/analytics")
async def get_program_analytics(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    period: Optional[str] = Query("30d", description="Analysis period: 7d, 30d, 90d, 1y")
):
    """Get comprehensive analytics for a specific PRP program"""
    try:
        prp_service = PRPService(db)
        analytics = prp_service.get_program_analytics(program_id, period)
        
        return ResponseModel(
            success=True,
            message="Program analytics retrieved successfully",
            data=analytics
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve program analytics: {str(e)}"
        )


@router.get("/programs/{program_id}/performance-trends")
async def get_program_performance_trends(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trend_period: Optional[str] = Query("6m", description="Trend period: 3m, 6m, 1y")
):
    """Get performance trends for a PRP program"""
    try:
        prp_service = PRPService(db)
        trends = prp_service.get_program_performance_trends(program_id, trend_period)
        
        return ResponseModel(
            success=True,
            message="Performance trends retrieved successfully",
            data=trends
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance trends: {str(e)}"
        )


@router.post("/programs/{program_id}/optimize-schedule")
async def optimize_program_schedule(
    program_id: int,
    optimization_params: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize program schedule based on historical data and resource availability"""
    try:
        prp_service = PRPService(db)
        optimization_result = prp_service.optimize_program_schedule(
            program_id, optimization_params, current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Program schedule optimized successfully",
            data=optimization_result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize program schedule: {str(e)}"
        )


@router.get("/programs/{program_id}/resource-utilization")
async def get_program_resource_utilization(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get resource utilization analysis for a PRP program"""
    try:
        prp_service = PRPService(db)
        utilization = prp_service.get_program_resource_utilization(
            program_id, date_from, date_to
        )
        
        return ResponseModel(
            success=True,
            message="Resource utilization data retrieved successfully",
            data=utilization
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resource utilization: {str(e)}"
        )


# Enhanced Reporting Capabilities
@router.post("/reports/comprehensive")
async def generate_comprehensive_report(
    report_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive PRP report with multiple dimensions"""
    try:
        prp_service = PRPService(db)
        report_data = prp_service.generate_comprehensive_report(
            program_ids=report_request.get("program_ids"),
            categories=report_request.get("categories"),
            date_from=report_request.get("date_from"),
            date_to=report_request.get("date_to"),
            include_risks=report_request.get("include_risks", True),
            include_capa=report_request.get("include_capa", True),
            include_trends=report_request.get("include_trends", True),
            format_type=report_request.get("format", "json")
        )
        
        return ResponseModel(
            success=True,
            message="Comprehensive report generated successfully",
            data=report_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate comprehensive report: {str(e)}"
        )


@router.get("/reports/compliance-summary")
async def get_compliance_summary_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    department: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get compliance summary report across all PRP programs"""
    try:
        prp_service = PRPService(db)
        summary = prp_service.get_compliance_summary_report(
            category, department, date_from, date_to
        )
        
        return ResponseModel(
            success=True,
            message="Compliance summary retrieved successfully",
            data=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve compliance summary: {str(e)}"
        )


@router.get("/reports/risk-exposure")
async def get_risk_exposure_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    risk_level: Optional[str] = None,
    category: Optional[str] = None
):
    """Get risk exposure report for PRP programs"""
    try:
        prp_service = PRPService(db)
        exposure = prp_service.get_risk_exposure_report(risk_level, category)
        
        return ResponseModel(
            success=True,
            message="Risk exposure report retrieved successfully",
            data=exposure
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk exposure report: {str(e)}"
        )


@router.post("/reports/export")
async def export_prp_data(
    export_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export PRP data in various formats (Excel, PDF, CSV)"""
    try:
        prp_service = PRPService(db)
        export_result = prp_service.export_prp_data(
            data_type=export_request.get("data_type"),  # programs, checklists, risks, capa
            format_type=export_request.get("format"),   # excel, pdf, csv
            filters=export_request.get("filters", {}),
            include_attachments=export_request.get("include_attachments", False)
        )
        
        return ResponseModel(
            success=True,
            message="PRP data exported successfully",
            data=export_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export PRP data: {str(e)}"
        )


# Performance Monitoring and Optimization
@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    metric_type: Optional[str] = Query("all", description="Metric type: compliance, efficiency, quality, all")
):
    """Get performance metrics for PRP module"""
    try:
        prp_service = PRPService(db)
        metrics = prp_service.get_performance_metrics(metric_type)
        
        return ResponseModel(
            success=True,
            message="Performance metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )


@router.get("/performance/benchmarks")
async def get_performance_benchmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    benchmark_type: Optional[str] = Query("industry", description="Benchmark type: industry, internal, custom")
):
    """Get performance benchmarks for comparison"""
    try:
        prp_service = PRPService(db)
        benchmarks = prp_service.get_performance_benchmarks(benchmark_type)
        
        return ResponseModel(
            success=True,
            message="Performance benchmarks retrieved successfully",
            data=benchmarks
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance benchmarks: {str(e)}"
        )


@router.post("/performance/optimize")
async def optimize_performance(
    optimization_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize PRP module performance based on analysis"""
    try:
        prp_service = PRPService(db)
        optimization_result = prp_service.optimize_performance(
            optimization_request.get("optimization_type"),
            optimization_request.get("parameters", {}),
            current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Performance optimization completed successfully",
            data=optimization_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize performance: {str(e)}"
        )


# Advanced Analytics and Insights
@router.get("/analytics/predictive")
async def get_predictive_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_type: Optional[str] = Query("compliance", description="Prediction type: compliance, risks, failures")
):
    """Get predictive analytics for PRP programs"""
    try:
        prp_service = PRPService(db)
        predictions = prp_service.get_predictive_analytics(prediction_type)
        
        return ResponseModel(
            success=True,
            message="Predictive analytics retrieved successfully",
            data=predictions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve predictive analytics: {str(e)}"
        )


@router.get("/analytics/trends")
async def get_analytical_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trend_type: Optional[str] = Query("compliance", description="Trend type: compliance, risks, efficiency, quality"),
    period: Optional[str] = Query("12m", description="Analysis period")
):
    """Get analytical trends for PRP module"""
    try:
        prp_service = PRPService(db)
        trends = prp_service.get_analytical_trends(trend_type, period)
        
        return ResponseModel(
            success=True,
            message="Analytical trends retrieved successfully",
            data=trends
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytical trends: {str(e)}"
        )


@router.post("/analytics/insights")
async def generate_insights(
    insight_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate actionable insights from PRP data"""
    try:
        prp_service = PRPService(db)
        insights = prp_service.generate_insights(
            insight_type=insight_request.get("insight_type"),
            parameters=insight_request.get("parameters", {}),
            priority_level=insight_request.get("priority_level", "medium")
        )
        
        return ResponseModel(
            success=True,
            message="Insights generated successfully",
            data=insights
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


# Integration and Automation
@router.post("/automation/trigger")
async def trigger_automation(
    automation_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger automated PRP processes"""
    try:
        prp_service = PRPService(db)
        automation_result = prp_service.trigger_automation(
            automation_type=automation_request.get("automation_type"),
            parameters=automation_request.get("parameters", {}),
            triggered_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Automation triggered successfully",
            data=automation_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger automation: {str(e)}"
        )


@router.get("/automation/status")
async def get_automation_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    automation_id: Optional[str] = None
):
    """Get status of automated PRP processes"""
    try:
        prp_service = PRPService(db)
        status = prp_service.get_automation_status(automation_id)
        
        return ResponseModel(
            success=True,
            message="Automation status retrieved successfully",
            data=status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve automation status: {str(e)}"
        )


# Advanced Search and Filtering
@router.post("/search/advanced")
async def advanced_search(
    search_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced search across PRP data with multiple criteria"""
    try:
        prp_service = PRPService(db)
        search_results = prp_service.advanced_search(
            search_criteria=search_request.get("criteria", {}),
            search_type=search_request.get("search_type", "all"),
            sort_by=search_request.get("sort_by", "relevance"),
            page=search_request.get("page", 1),
            size=search_request.get("size", 20)
        )
        
        return ResponseModel(
            success=True,
            message="Advanced search completed successfully",
            data=search_results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform advanced search: {str(e)}"
        )


# Bulk Operations
@router.post("/bulk/update")
async def bulk_update_programs(
    bulk_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update PRP programs"""
    try:
        prp_service = PRPService(db)
        update_result = prp_service.bulk_update_programs(
            program_ids=bulk_request.get("program_ids", []),
            update_data=bulk_request.get("update_data", {}),
            updated_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Bulk update completed successfully",
            data=update_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk update: {str(e)}"
        )


@router.post("/bulk/export")
async def bulk_export_data(
    export_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk export PRP data"""
    try:
        prp_service = PRPService(db)
        export_result = prp_service.bulk_export_data(
            data_types=export_request.get("data_types", []),
            format_type=export_request.get("format", "excel"),
            filters=export_request.get("filters", {}),
            requested_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Bulk export completed successfully",
            data=export_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk export: {str(e)}"
        )


# ============================================================================
# PHASE 3: ADVANCED BUSINESS LOGIC ENDPOINTS
# ============================================================================

# Risk Assessment Engine Endpoints (Phase 3.1)
@router.post("/risk-matrices/calculate-score")
async def calculate_risk_score(
    calculation_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate risk score using configurable risk matrix"""
    try:
        prp_service = PRPService(db)
        risk_calculation = prp_service.calculate_risk_score(
            likelihood_level=calculation_request["likelihood_level"],
            severity_level=calculation_request["severity_level"],
            matrix_id=calculation_request.get("matrix_id")
        )
        
        return ResponseModel(
            success=True,
            message="Risk score calculated successfully",
            data=risk_calculation
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate risk score: {str(e)}"
        )


@router.post("/risk-assessments/{assessment_id}/calculate-residual-risk")
async def calculate_residual_risk(
    assessment_id: int,
    residual_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate residual risk after implementing controls"""
    try:
        prp_service = PRPService(db)
        residual_calculation = prp_service.calculate_residual_risk(
            initial_risk_score=residual_request["initial_risk_score"],
            control_effectiveness=residual_request["control_effectiveness"]
        )
        
        return ResponseModel(
            success=True,
            message="Residual risk calculated successfully",
            data=residual_calculation
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate residual risk: {str(e)}"
        )


# Corrective Action Workflow Endpoints (Phase 3.2)
@router.post("/corrective-actions/{action_id}/update-progress")
async def update_action_progress(
    action_id: int,
    progress_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update corrective action progress with effectiveness tracking"""
    try:
        prp_service = PRPService(db)
        updated_action = prp_service.update_action_progress(
            action_id=action_id,
            progress_percentage=progress_request["progress_percentage"],
            status=progress_request.get("status")
        )
        
        return ResponseModel(
            success=True,
            message="Action progress updated successfully",
            data={
                "action_id": updated_action.id,
                "progress_percentage": updated_action.progress_percentage,
                "status": updated_action.status.value,
                "completion_date": updated_action.actual_completion_date
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update action progress: {str(e)}"
        )


@router.post("/corrective-actions/{action_id}/verify-effectiveness")
async def verify_action_effectiveness(
    action_id: int,
    verification_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify corrective action effectiveness"""
    try:
        prp_service = PRPService(db)
        verified_action = prp_service.verify_action_effectiveness(
            action_id=action_id,
            verification_data=verification_request,
            verified_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Action effectiveness verified successfully",
            data={
                "action_id": verified_action.id,
                "status": verified_action.status.value,
                "effectiveness_verified_by": verified_action.effectiveness_verified_by,
                "effectiveness_verified_at": verified_action.effectiveness_verified_at
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify action effectiveness: {str(e)}"
        )


# Preventive Action System Endpoints (Phase 3.3)
@router.post("/preventive-actions/{action_id}/start")
async def start_preventive_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a preventive action with effectiveness measurement setup"""
    try:
        prp_service = PRPService(db)
        started_action = prp_service.start_preventive_action(
            action_id=action_id,
            started_by=current_user.id
        )
        
        return ResponseModel(
            success=True,
            message="Preventive action started successfully",
            data={
                "action_id": started_action.id,
                "status": started_action.status.value,
                "start_date": started_action.start_date,
                "effectiveness_measurement": started_action.effectiveness_measurement
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start preventive action: {str(e)}"
        )


@router.post("/preventive-actions/{action_id}/measure-effectiveness")
async def measure_action_effectiveness(
    action_id: int,
    measurement_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Measure preventive action effectiveness"""
    try:
        prp_service = PRPService(db)
        measurement_result = prp_service.measure_action_effectiveness(
            action_id=action_id,
            measurement_data=measurement_request
        )
        
        return ResponseModel(
            success=True,
            message="Action effectiveness measured successfully",
            data=measurement_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to measure action effectiveness: {str(e)}"
        )


@router.get("/programs/{program_id}/continuous-improvement")
async def get_continuous_improvement_metrics(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get continuous improvement metrics for PRP programs"""
    try:
        prp_service = PRPService(db)
        improvement_metrics = prp_service.track_continuous_improvement(program_id)
        
        return ResponseModel(
            success=True,
            message="Continuous improvement metrics retrieved successfully",
            data=improvement_metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve continuous improvement metrics: {str(e)}"
        )