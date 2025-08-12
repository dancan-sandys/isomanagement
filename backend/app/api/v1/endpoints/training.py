from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import os
from uuid import uuid4
import csv
from io import StringIO

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.training import (
    TrainingProgramCreate, TrainingProgramUpdate, TrainingProgramResponse,
    TrainingSessionBase, TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse,
    TrainingAttendanceCreate, TrainingAttendanceResponse,
    TrainingMaterialUploadResponse,
    RoleRequiredTrainingCreate, RoleRequiredTrainingResponse,
    TrainingQuizCreate, TrainingQuizResponse, TrainingQuizAttemptSubmit, TrainingQuizAttemptResponse,
    TrainingCertificateResponse, TrainingMatrixItem,
)
from app.services.training_service import TrainingService

router = APIRouter()

UPLOAD_DIR = "uploads/training"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/programs", response_model=List[TrainingProgramResponse])
async def list_programs(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    programs = svc.list_programs(search)
    return programs


@router.post("/programs", response_model=TrainingProgramResponse)
async def create_program(
    program: TrainingProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    created = svc.create_program(program, current_user.id)
    return created


@router.get("/programs/{program_id}", response_model=TrainingProgramResponse)
async def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    program = svc.get_program(program_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program


@router.put("/programs/{program_id}", response_model=TrainingProgramResponse)
async def update_program(
    program_id: int,
    program: TrainingProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    updated = svc.update_program(program_id, program)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return updated


@router.delete("/programs/{program_id}")
async def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    ok = svc.delete_program(program_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return {"message": "Program deleted"}


# Sessions
@router.get("/programs/{program_id}/sessions", response_model=List[TrainingSessionResponse])
async def list_sessions(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.list_sessions(program_id)


@router.post("/programs/{program_id}/sessions", response_model=TrainingSessionResponse)
async def create_session(
    program_id: int,
    session: TrainingSessionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Build full payload with program id from path
    session = TrainingSessionCreate(program_id=program_id, **session.dict())
    svc = TrainingService(db)
    return svc.create_session(session, current_user.id)


@router.put("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def update_session(
    session_id: int,
    session: TrainingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    updated = svc.update_session(session_id, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return updated


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    ok = svc.delete_session(session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"message": "Session deleted"}


# Attendance
@router.get("/sessions/{session_id}/attendance", response_model=List[TrainingAttendanceResponse])
async def list_attendance(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    records = svc.list_attendance(session_id)
    # Enrich with user names
    for r in records:
        try:
            if getattr(r, 'user', None):
                r.user_full_name = r.user.full_name  # type: ignore
                r.username = r.user.username  # type: ignore
        except Exception:
            pass
    return records


@router.post("/sessions/{session_id}/attendance", response_model=TrainingAttendanceResponse)
async def add_attendance(
    session_id: int,
    att: TrainingAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    att.session_id = session_id
    svc = TrainingService(db)
    rec = svc.add_attendance(att)
    # attach user info
    try:
        if getattr(rec, 'user', None):
            rec.user_full_name = rec.user.full_name  # type: ignore
            rec.username = rec.user.username  # type: ignore
    except Exception:
        pass
    return rec


@router.put("/attendance/{attendance_id}", response_model=TrainingAttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attended: bool | None = Query(default=None),
    comments: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    rec = svc.update_attendance(attendance_id, attended=attended, comments=comments)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
    try:
        if getattr(rec, 'user', None):
            rec.user_full_name = rec.user.full_name  # type: ignore
            rec.username = rec.user.username  # type: ignore
    except Exception:
        pass
    return rec


@router.delete("/attendance/{attendance_id}")
async def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    ok = svc.delete_attendance(attendance_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
    return {"message": "Attendance deleted"}


@router.get("/sessions/{session_id}/attendance/export")
async def export_attendance_csv(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi.responses import StreamingResponse
    svc = TrainingService(db)
    rows = svc.list_attendance(session_id)
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "session_id", "user_id", "username", "full_name", "attended", "comments", "created_at"])
    for a in rows:
        username = getattr(getattr(a, 'user', None), 'username', None)
        full_name = getattr(getattr(a, 'user', None), 'full_name', None)
        writer.writerow([a.id, a.session_id, a.user_id, username or '', full_name or '', a.attended, a.comments or '', a.created_at.isoformat()])
    buf.seek(0)
    return StreamingResponse(buf, media_type='text/csv', headers={"Content-Disposition": f"attachment; filename=attendance_{session_id}.csv"})


# Materials
@router.post("/programs/{program_id}/materials", response_model=TrainingMaterialUploadResponse)
async def upload_program_material(
    program_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unique = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    svc = TrainingService(db)
    mat = svc.save_material(program_id=program_id, session_id=None, original_filename=file.filename, stored_filename=unique, file_path=file_path, file_type=file.content_type, uploaded_by=current_user.id)
    return mat


@router.post("/sessions/{session_id}/materials", response_model=TrainingMaterialUploadResponse)
async def upload_session_material(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unique = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    svc = TrainingService(db)
    mat = svc.save_material(program_id=None, session_id=session_id, original_filename=file.filename, stored_filename=unique, file_path=file_path, file_type=file.content_type, uploaded_by=current_user.id)
    return mat


@router.get("/programs/{program_id}/materials", response_model=list[TrainingMaterialUploadResponse])
async def list_program_materials(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.list_materials(program_id=program_id)


@router.get("/sessions/{session_id}/materials", response_model=list[TrainingMaterialUploadResponse])
async def list_session_materials(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.list_materials(session_id=session_id)


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    ok = svc.delete_material(material_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return {"message": "Material deleted"}


@router.get("/materials/{material_id}/download")
async def download_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi.responses import FileResponse
    svc = TrainingService(db)
    mat = svc.get_material(material_id)
    if not mat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return FileResponse(mat.file_path, filename=mat.original_filename, media_type=mat.file_type or "application/octet-stream")


# Role-required trainings
@router.post("/required", response_model=RoleRequiredTrainingResponse)
async def assign_required_training(
    payload: RoleRequiredTrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    rec = svc.assign_role_required_training(payload.role_id, payload.program_id, payload.is_mandatory if payload.is_mandatory is not None else True)
    return rec


@router.get("/required", response_model=list[RoleRequiredTrainingResponse])
async def list_required_trainings(
    role_id: int | None = Query(default=None),
    program_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.list_role_required_trainings(role_id=role_id, program_id=program_id)


@router.delete("/required/{record_id}")
async def delete_required_training(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    ok = svc.delete_role_required_training(record_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return {"message": "Record deleted"}


# Quizzes
@router.post("/programs/{program_id}/quizzes", response_model=TrainingQuizResponse)
async def create_program_quiz(
    program_id: int,
    payload: TrainingQuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    quiz = svc.create_quiz_for_program(program_id, payload, current_user.id)
    return quiz


@router.get("/programs/{program_id}/quizzes", response_model=list[TrainingQuizResponse])
async def list_program_quizzes(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.list_quizzes(program_id=program_id)


@router.get("/quizzes/{quiz_id}", response_model=TrainingQuizResponse)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    quiz = svc.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/quizzes/{quiz_id}/submit", response_model=TrainingQuizAttemptResponse)
async def submit_quiz(
    quiz_id: int,
    payload: TrainingQuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    attempt = svc.submit_quiz_attempt(quiz_id, current_user.id, [a.dict() for a in payload.answers])
    return attempt


# Certificates
@router.post("/sessions/{session_id}/certificates", response_model=TrainingCertificateResponse)
async def upload_certificate(
    session_id: int,
    file: UploadFile = File(...),
    quiz_attempt_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unique = f"{uuid4().hex}_{file.filename}"
    cert_dir = os.path.join(UPLOAD_DIR, "certificates")
    os.makedirs(cert_dir, exist_ok=True)
    file_path = os.path.join(cert_dir, unique)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    verification_code = uuid4().hex
    svc = TrainingService(db)
    cert = svc.issue_certificate(
        session_id=session_id,
        user_id=current_user.id,
        issued_by=current_user.id,
        quiz_attempt_id=quiz_attempt_id,
        original_filename=file.filename,
        stored_filename=unique,
        file_path=file_path,
        file_type=file.content_type,
        verification_code=verification_code,
    )
    return cert


@router.get("/sessions/{session_id}/certificates", response_model=list[TrainingCertificateResponse])
async def list_session_certificates(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.list_certificates(session_id=session_id)


@router.get("/certificates/verify/{code}", response_model=TrainingCertificateResponse)
async def verify_certificate(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    cert = svc.get_certificate_by_code(code)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.get("/certificates/{cert_id}/download")
async def download_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi.responses import FileResponse
    svc = TrainingService(db)
    items = svc.list_certificates()
    cert = next((c for c in items if c.id == cert_id), None)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return FileResponse(cert.file_path, filename=cert.original_filename, media_type=cert.file_type or "application/octet-stream")


@router.get("/matrix/me", response_model=list[TrainingMatrixItem])
async def get_my_training_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TrainingService(db)
    return svc.get_training_matrix_for_user(current_user.id)

