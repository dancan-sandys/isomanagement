from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.training import TrainingAction


class TrainingProgramBase(BaseModel):
    code: str = Field(..., description="Unique training code")
    title: str
    description: Optional[str] = None
    department: Optional[str] = None


class TrainingProgramCreate(TrainingProgramBase):
    pass


class TrainingProgramUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None


class TrainingProgramResponse(TrainingProgramBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int

    class Config:
        from_attributes = True


class TrainingSessionBase(BaseModel):
    session_date: datetime
    location: Optional[str] = None
    trainer: Optional[str] = None
    notes: Optional[str] = None


class TrainingSessionCreate(TrainingSessionBase):
    program_id: int


class TrainingSessionUpdate(BaseModel):
    session_date: Optional[datetime] = None
    location: Optional[str] = None
    trainer: Optional[str] = None
    notes: Optional[str] = None


class TrainingSessionResponse(TrainingSessionBase):
    id: int
    program_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int

    class Config:
        from_attributes = True


class TrainingAttendanceCreate(BaseModel):
    # session_id is provided via the path param in the API, so keep it optional here
    session_id: Optional[int] = None
    user_id: int
    attended: Optional[bool] = True
    comments: Optional[str] = None


class TrainingAttendanceResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    attended: bool
    comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_full_name: Optional[str] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True


class TrainingMaterialUploadResponse(BaseModel):
    id: int
    program_id: Optional[int] = None
    session_id: Optional[int] = None
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: Optional[str] = None
    uploaded_by: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class RoleRequiredTrainingCreate(BaseModel):
    role_id: int
    program_id: int
    is_mandatory: Optional[bool] = True


class RoleRequiredTrainingResponse(BaseModel):
    id: int
    role_id: int
    program_id: int
    is_mandatory: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Quizzes
class TrainingQuizOptionCreate(BaseModel):
    text: str
    is_correct: bool = False


class TrainingQuizQuestionCreate(BaseModel):
    text: str
    order_index: int = 0
    options: List[TrainingQuizOptionCreate]


class TrainingQuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    pass_threshold: int = 70
    is_published: Optional[bool] = False
    questions: List[TrainingQuizQuestionCreate]


class TrainingQuizOptionResponse(BaseModel):
    id: int
    text: str
    is_correct: bool

    class Config:
        from_attributes = True


class TrainingQuizQuestionResponse(BaseModel):
    id: int
    text: str
    order_index: int
    options: List[TrainingQuizOptionResponse]

    class Config:
        from_attributes = True


class TrainingQuizResponse(BaseModel):
    id: int
    program_id: Optional[int] = None
    session_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    pass_threshold: int
    is_published: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List[TrainingQuizQuestionResponse]

    class Config:
        from_attributes = True


class TrainingQuizAttemptAnswer(BaseModel):
    question_id: int
    selected_option_id: int


class TrainingQuizAttemptSubmit(BaseModel):
    answers: List[TrainingQuizAttemptAnswer]


class TrainingQuizAttemptResponse(BaseModel):
    quiz_id: int
    user_id: int
    score_percent: float
    passed: bool
    submitted_at: datetime


class TrainingCertificateResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    quiz_attempt_id: Optional[int] = None
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: Optional[str] = None
    verification_code: str
    issued_by: int
    issued_at: datetime

    class Config:
        from_attributes = True


class TrainingMatrixItem(BaseModel):
    program_id: int
    program_code: str
    program_title: str
    completed: bool
    in_progress: bool
    last_attended_at: Optional[datetime] = None
    last_certificate_issued_at: Optional[datetime] = None
    last_quiz_score: Optional[float] = None
    last_quiz_passed: Optional[bool] = None


# HACCP Required Training (scoped) schemas
class HACCPRequiredTrainingCreate(BaseModel):
    role_id: int
    action: TrainingAction
    program_id: int
    ccp_id: Optional[int] = None
    equipment_id: Optional[int] = None
    is_mandatory: Optional[bool] = True


class HACCPRequiredTrainingResponse(BaseModel):
    id: int
    role_id: int
    action: TrainingAction
    program_id: int
    ccp_id: Optional[int] = None
    equipment_id: Optional[int] = None
    is_mandatory: bool
    created_at: datetime

    class Config:
        from_attributes = True
