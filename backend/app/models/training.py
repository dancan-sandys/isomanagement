from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.user import User


class TrainingProgram(Base):
    __tablename__ = "training_programs"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    department = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    sessions = relationship("TrainingSession", back_populates="program")

    def __repr__(self) -> str:
        return f"<TrainingProgram(id={self.id}, code='{self.code}', title='{self.title}')>"


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200))
    trainer = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    program = relationship("TrainingProgram", back_populates="sessions")
    attendance = relationship("TrainingAttendance", back_populates="session")

    def __repr__(self) -> str:
        return f"<TrainingSession(id={self.id}, program_id={self.program_id}, date={self.session_date})>"


class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attended = Column(Boolean, default=True, nullable=False)
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    session = relationship("TrainingSession", back_populates="attendance")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<TrainingAttendance(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"


class TrainingMaterial(Base):
    __tablename__ = "training_materials"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    program = relationship("TrainingProgram")
    session = relationship("TrainingSession")

    def __repr__(self) -> str:
        return f"<TrainingMaterial(id={self.id}, program_id={self.program_id}, session_id={self.session_id}, file='{self.original_filename}')>"


class RoleRequiredTraining(Base):
    __tablename__ = "role_required_trainings"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<RoleRequiredTraining(role_id={self.role_id}, program_id={self.program_id}, mandatory={self.is_mandatory})>"


class TrainingQuiz(Base):
    __tablename__ = "training_quizzes"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    pass_threshold = Column(Integer, nullable=False, default=70)  # percent
    is_published = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    questions = relationship("TrainingQuizQuestion", back_populates="quiz", cascade="all, delete-orphan")


class TrainingQuizQuestion(Base):
    __tablename__ = "training_quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("training_quizzes.id"), nullable=False)
    text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

    quiz = relationship("TrainingQuiz", back_populates="questions")
    options = relationship("TrainingQuizOption", back_populates="question", cascade="all, delete-orphan")


class TrainingQuizOption(Base):
    __tablename__ = "training_quiz_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("training_quiz_questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    question = relationship("TrainingQuizQuestion", back_populates="options")


class TrainingQuizAttempt(Base):
    __tablename__ = "training_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("training_quizzes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score_percent = Column(Float, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())


class TrainingQuizAnswer(Base):
    __tablename__ = "training_quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("training_quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("training_quiz_questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("training_quiz_options.id"), nullable=False)


class TrainingCertificate(Base):
    __tablename__ = "training_certificates"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_attempt_id = Column(Integer, ForeignKey("training_quiz_attempts.id"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=True)
    verification_code = Column(String(64), unique=True, nullable=False)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())

