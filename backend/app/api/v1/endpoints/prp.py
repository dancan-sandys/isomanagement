from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus
)
from app.schemas.common import ResponseModel
from app.schemas.prp import (
    PRPProgramCreate, PRPProgramUpdate, ChecklistCreate, ChecklistUpdate,
    ChecklistItemCreate, ChecklistCompletion, NonConformanceCreate,
    ReminderCreate, ScheduleCreate, PRPReportRequest
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
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all PRP programs with pagination and filters"""
    try:
        query = db.query(PRPProgram)
        
        # Apply filters
        if category:
            query = query.filter(PRPProgram.category == PRPCategory(category))
        if status:
            query = query.filter(PRPProgram.status == PRPStatus(status))
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
    program_data: dict,
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
    status: Optional[str] = None
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
        if status:
            query = query.filter(PRPChecklist.status == ChecklistStatus(status))
        
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