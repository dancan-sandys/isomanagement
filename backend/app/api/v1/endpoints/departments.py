from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user, require_permission
from app.models.user import User
from app.models.departments import Department as DepartmentModel, DepartmentUser as DepartmentUserModel
from app.schemas.departments import (
    DepartmentCreate, DepartmentUpdate, Department as DepartmentSchema,
    DepartmentListResponse, DepartmentUserAssignment
)

router = APIRouter()


@router.get("/", response_model=DepartmentListResponse)
def list_departments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    query = db.query(DepartmentModel)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (DepartmentModel.name.ilike(like)) | (DepartmentModel.department_code.ilike(like))
        )
    if status_filter:
        query = query.filter(DepartmentModel.status == status_filter)

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return DepartmentListResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments:create"))
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    # Uniqueness on department_code
    existing = db.query(DepartmentModel).filter(DepartmentModel.department_code == payload.department_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department code already exists")

    dep = DepartmentModel(
        department_code=payload.department_code,
        name=payload.name,
        description=payload.description,
        parent_department_id=payload.parent_department_id,
        manager_id=payload.manager_id,
        status=payload.status or "active",
        color_code=payload.color_code,
        created_by=payload.created_by
    )
    # Best-effort governance extras if columns exist in model
    if hasattr(DepartmentModel, 'raci_json'):
        setattr(dep, 'raci_json', payload.raci_json)
    if hasattr(DepartmentModel, 'governance_notes'):
        setattr(dep, 'governance_notes', payload.governance_notes)

    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep


@router.get("/{department_id}", response_model=DepartmentSchema)
def get_department(
    department_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    dep = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Department not found")
    return dep


@router.put("/{department_id}", response_model=DepartmentSchema)
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments:update"))
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    dep = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Department not found")
    update = payload.model_dump(exclude_unset=True)
    # Guard uniqueness for department_code
    if 'department_code' in update:
        exists = db.query(DepartmentModel).filter(
            DepartmentModel.department_code == update['department_code'],
            DepartmentModel.id != department_id
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="Department code already exists")
    for k, v in update.items():
        setattr(dep, k, v)
    db.commit()
    db.refresh(dep)
    return dep


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments:delete"))
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    dep = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Department not found")
    # Soft-delete if supported
    if hasattr(dep, 'status'):
        dep.status = 'archived'
        db.commit()
        return {"success": True, "message": "Department archived"}
    # Fallback hard delete
    db.delete(dep)
    db.commit()
    return {"success": True, "message": "Department deleted"}


@router.get("/{department_id}/users")
def list_department_users(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    assignments = db.query(DepartmentUserModel).filter(
        DepartmentUserModel.department_id == department_id,
        DepartmentUserModel.is_active == True
    ).all()
    users = []
    for a in assignments:
        users.append({
            "user_id": a.user_id,
            "role": a.role,
            "assigned_from": a.assigned_from,
            "assigned_until": a.assigned_until,
            "is_active": a.is_active
        })
    return {"department_id": department_id, "users": users}


@router.post("/{department_id}/users")
def assign_user_to_department(
    department_id: int,
    payload: DepartmentUserAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments:assign_user"))
):
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    dep = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Department not found")
    # Upsert active assignment
    if not settings.FEATURE_DEPARTMENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Departments feature is disabled")
    assignment = db.query(DepartmentUserModel).filter(
        DepartmentUserModel.department_id == department_id,
        DepartmentUserModel.user_id == payload.user_id
    ).first()
    if not assignment:
        assignment = DepartmentUserModel(
            department_id=department_id,
            user_id=payload.user_id,
            role=payload.role,
            assigned_from=payload.assigned_from,
            assigned_until=payload.assigned_until,
            is_active=payload.is_active if payload.is_active is not None else True,
            created_by=current_user.id
        )
        db.add(assignment)
    else:
        assignment.role = payload.role or assignment.role
        assignment.assigned_from = payload.assigned_from or assignment.assigned_from
        assignment.assigned_until = payload.assigned_until or assignment.assigned_until
        assignment.is_active = True if payload.is_active is None else payload.is_active
    db.commit()
    return {"success": True}


@router.delete("/{department_id}/users/{user_id}")
def unassign_user_from_department(
    department_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments:assign_user"))
):
    assignment = db.query(DepartmentUserModel).filter(
        DepartmentUserModel.department_id == department_id,
        DepartmentUserModel.user_id == user_id,
        DepartmentUserModel.is_active == True
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.is_active = False
    db.commit()
    return {"success": True}

