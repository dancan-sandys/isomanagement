from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
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
        
        return ResponseModel(
            success=True,
            message="PRP program created successfully",
            data={"id": program.id}
        )
        
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
        
        return ResponseModel(
            success=True,
            message="Checklist created successfully",
            data={"id": checklist.id}
        )
        
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