from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.training import TrainingProgram, TrainingSession, TrainingAttendance, TrainingMaterial, RoleRequiredTraining, TrainingQuiz, TrainingQuizQuestion, TrainingQuizOption, TrainingQuizAttempt, TrainingQuizAnswer, TrainingCertificate, HACCPRequiredTraining, TrainingAction
from app.models.user import User
from app.schemas.training import (
    TrainingProgramCreate, TrainingProgramUpdate,
    TrainingSessionCreate, TrainingSessionUpdate,
    TrainingAttendanceCreate,
)


class TrainingService:
    def __init__(self, db: Session):
        self.db = db

    # Programs
    def create_program(self, data: TrainingProgramCreate, created_by: int) -> TrainingProgram:
        program = TrainingProgram(
            code=data.code,
            title=data.title,
            description=data.description,
            department=data.department,
            created_by=created_by,
        )
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        return program

    def list_programs(self, search: Optional[str] = None) -> List[TrainingProgram]:
        q = self.db.query(TrainingProgram)
        if search:
            like = f"%{search}%"
            q = q.filter(TrainingProgram.title.ilike(like) | TrainingProgram.code.ilike(like))
        return q.order_by(TrainingProgram.created_at.desc()).all()

    def get_program(self, program_id: int) -> Optional[TrainingProgram]:
        return self.db.query(TrainingProgram).filter(TrainingProgram.id == program_id).first()

    def update_program(self, program_id: int, data: TrainingProgramUpdate) -> Optional[TrainingProgram]:
        program = self.get_program(program_id)
        if not program:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(program, k, v)
        self.db.commit()
        self.db.refresh(program)
        return program

    def delete_program(self, program_id: int) -> bool:
        program = self.get_program(program_id)
        if not program:
            return False
        self.db.delete(program)
        self.db.commit()
        return True

    # Sessions
    def create_session(self, data: TrainingSessionCreate, created_by: int) -> TrainingSession:
        session = TrainingSession(
            program_id=data.program_id,
            session_date=data.session_date,
            location=data.location,
            trainer=data.trainer,
            notes=data.notes,
            created_by=created_by,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def list_sessions(self, program_id: int) -> List[TrainingSession]:
        return (
            self.db.query(TrainingSession)
            .filter(TrainingSession.program_id == program_id)
            .order_by(TrainingSession.session_date.desc())
            .all()
        )

    def update_session(self, session_id: int, data: TrainingSessionUpdate) -> Optional[TrainingSession]:
        session = self.db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        if not session:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(session, k, v)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: int) -> bool:
        session = self.db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        if not session:
            return False
        self.db.delete(session)
        self.db.commit()
        return True

    # Attendance
    def add_attendance(self, data: TrainingAttendanceCreate) -> TrainingAttendance:
        att = TrainingAttendance(
            session_id=data.session_id,
            user_id=data.user_id,
            attended=data.attended if data.attended is not None else True,
            comments=data.comments,
        )
        self.db.add(att)
        self.db.commit()
        self.db.refresh(att)
        return att

    def list_attendance(self, session_id: int) -> List[TrainingAttendance]:
        return (
            self.db.query(TrainingAttendance)
            .filter(TrainingAttendance.session_id == session_id)
            .order_by(TrainingAttendance.created_at.desc())
            .all()
        )

    def update_attendance(self, att_id: int, *, attended: Optional[bool] = None, comments: Optional[str] = None) -> Optional[TrainingAttendance]:
        att = self.db.query(TrainingAttendance).filter(TrainingAttendance.id == att_id).first()
        if not att:
            return None
        if attended is not None:
            att.attended = attended
        if comments is not None:
            att.comments = comments
        self.db.commit()
        self.db.refresh(att)
        return att

    def delete_attendance(self, att_id: int) -> bool:
        att = self.db.query(TrainingAttendance).filter(TrainingAttendance.id == att_id).first()
        if not att:
            return False
        self.db.delete(att)
        self.db.commit()
        return True

    # Materials
    def save_material(self, *, program_id: Optional[int], session_id: Optional[int], original_filename: str, stored_filename: str, file_path: str, file_type: Optional[str], uploaded_by: int) -> TrainingMaterial:
        mat = TrainingMaterial(
            program_id=program_id,
            session_id=session_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file_type,
            uploaded_by=uploaded_by,
        )
        self.db.add(mat)
        self.db.commit()
        self.db.refresh(mat)
        return mat

    def list_materials(self, program_id: Optional[int] = None, session_id: Optional[int] = None) -> List[TrainingMaterial]:
        q = self.db.query(TrainingMaterial)
        if program_id is not None:
            q = q.filter(TrainingMaterial.program_id == program_id)
        if session_id is not None:
            q = q.filter(TrainingMaterial.session_id == session_id)
        return q.order_by(TrainingMaterial.uploaded_at.desc()).all()

    def get_material(self, material_id: int) -> Optional[TrainingMaterial]:
        return self.db.query(TrainingMaterial).filter(TrainingMaterial.id == material_id).first()

    def delete_material(self, material_id: int) -> bool:
        mat = self.get_material(material_id)
        if not mat:
            return False
        self.db.delete(mat)
        self.db.commit()
        return True

    # Role Required Trainings
    def assign_role_required_training(self, role_id: int, program_id: int, is_mandatory: bool = True) -> RoleRequiredTraining:
        record = RoleRequiredTraining(role_id=role_id, program_id=program_id, is_mandatory=is_mandatory)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_role_required_trainings(self, role_id: Optional[int] = None, program_id: Optional[int] = None) -> List[RoleRequiredTraining]:
        q = self.db.query(RoleRequiredTraining)
        if role_id is not None:
            q = q.filter(RoleRequiredTraining.role_id == role_id)
        if program_id is not None:
            q = q.filter(RoleRequiredTraining.program_id == program_id)
        return q.order_by(RoleRequiredTraining.created_at.desc()).all()

    def delete_role_required_training(self, record_id: int) -> bool:
        rec = self.db.query(RoleRequiredTraining).filter(RoleRequiredTraining.id == record_id).first()
        if not rec:
            return False
        self.db.delete(rec)
        self.db.commit()
        return True

    # HACCP required training (scoped)
    def assign_haccp_required_training(self, *, role_id: int, action: TrainingAction, program_id: int, ccp_id: int | None = None, equipment_id: int | None = None, is_mandatory: bool = True) -> HACCPRequiredTraining:
        rec = HACCPRequiredTraining(role_id=role_id, action=action, program_id=program_id, ccp_id=ccp_id, equipment_id=equipment_id, is_mandatory=is_mandatory)
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def list_haccp_required_trainings(self, *, role_id: int | None = None, action: TrainingAction | None = None, ccp_id: int | None = None, equipment_id: int | None = None) -> list[HACCPRequiredTraining]:
        q = self.db.query(HACCPRequiredTraining)
        if role_id is not None:
            q = q.filter(HACCPRequiredTraining.role_id == role_id)
        if action is not None:
            q = q.filter(HACCPRequiredTraining.action == action)
        if ccp_id is not None:
            q = q.filter(HACCPRequiredTraining.ccp_id == ccp_id)
        if equipment_id is not None:
            q = q.filter(HACCPRequiredTraining.equipment_id == equipment_id)
        return q.order_by(HACCPRequiredTraining.created_at.desc()).all()

    def delete_haccp_required_training(self, record_id: int) -> bool:
        rec = self.db.query(HACCPRequiredTraining).filter(HACCPRequiredTraining.id == record_id).first()
        if not rec:
            return False
        self.db.delete(rec)
        self.db.commit()
        return True

    # Quizzes
    def create_quiz_for_program(self, program_id: int, data, created_by: int) -> TrainingQuiz:
        quiz = TrainingQuiz(
            program_id=program_id,
            title=data.title,
            description=data.description,
            pass_threshold=data.pass_threshold,
            is_published=bool(data.is_published),
            created_by=created_by,
        )
        self.db.add(quiz)
        self.db.flush()
        for q in data.questions:
            qq = TrainingQuizQuestion(quiz_id=quiz.id, text=q.text, order_index=q.order_index)
            self.db.add(qq)
            self.db.flush()
            for opt in q.options:
                self.db.add(TrainingQuizOption(question_id=qq.id, text=opt.text, is_correct=bool(opt.is_correct)))
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def list_quizzes(self, program_id: int | None = None, session_id: int | None = None) -> list[TrainingQuiz]:
        q = self.db.query(TrainingQuiz)
        if program_id is not None:
            q = q.filter(TrainingQuiz.program_id == program_id)
        if session_id is not None:
            q = q.filter(TrainingQuiz.session_id == session_id)
        return q.order_by(TrainingQuiz.created_at.desc()).all()

    def get_quiz(self, quiz_id: int) -> TrainingQuiz | None:
        return self.db.query(TrainingQuiz).filter(TrainingQuiz.id == quiz_id).first()

    def submit_quiz_attempt(self, quiz_id: int, user_id: int, answers: list[dict]) -> TrainingQuizAttempt:
        # Load questions and correct options
        questions = (
            self.db.query(TrainingQuizQuestion)
            .filter(TrainingQuizQuestion.quiz_id == quiz_id)
            .all()
        )
        question_id_to_correct = {}
        for q in questions:
            correct = [o.id for o in self.db.query(TrainingQuizOption).filter(TrainingQuizOption.question_id == q.id, TrainingQuizOption.is_correct == True).all()]
            # Support single-correct for now; if multiple, any mismatch fails
            question_id_to_correct[q.id] = set(correct)

        # Evaluate
        total = len(questions) if questions else 1
        correct_count = 0
        for ans in answers:
            qid = ans.get('question_id')
            selected = ans.get('selected_option_id')
            if qid in question_id_to_correct and selected in question_id_to_correct[qid]:
                correct_count += 1

        score_percent = (correct_count / total) * 100.0
        quiz = self.get_quiz(quiz_id)
        passed = bool(score_percent >= (quiz.pass_threshold if quiz else 70))

        attempt = TrainingQuizAttempt(quiz_id=quiz_id, user_id=user_id, score_percent=score_percent, passed=passed)
        self.db.add(attempt)
        self.db.flush()
        for ans in answers:
            self.db.add(TrainingQuizAnswer(attempt_id=attempt.id, question_id=ans['question_id'], selected_option_id=ans['selected_option_id']))
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    # Certificates
    def issue_certificate(self, *, session_id: int, user_id: int, issued_by: int, quiz_attempt_id: int | None, original_filename: str, stored_filename: str, file_path: str, file_type: str | None, verification_code: str) -> TrainingCertificate:
        cert = TrainingCertificate(
            session_id=session_id,
            user_id=user_id,
            quiz_attempt_id=quiz_attempt_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file_type,
            verification_code=verification_code,
            issued_by=issued_by,
        )
        self.db.add(cert)
        self.db.commit()
        self.db.refresh(cert)
        return cert

    def list_certificates(self, session_id: int | None = None, user_id: int | None = None) -> list[TrainingCertificate]:
        q = self.db.query(TrainingCertificate)
        if session_id is not None:
            q = q.filter(TrainingCertificate.session_id == session_id)
        if user_id is not None:
            q = q.filter(TrainingCertificate.user_id == user_id)
        return q.order_by(TrainingCertificate.issued_at.desc()).all()

    def get_certificate_by_code(self, verification_code: str) -> TrainingCertificate | None:
        return self.db.query(TrainingCertificate).filter(TrainingCertificate.verification_code == verification_code).first()

    # Matrix aggregation (simple heuristic):
    # completed => has at least one certificate for any session of program
    # in_progress => has attendance but no certificate
    def get_training_matrix_for_user(self, user_id: int) -> list[dict]:
        from sqlalchemy import func as sa_func
        # Programs
        programs = self.db.query(TrainingProgram).all()
        result = []
        for p in programs:
            # Sessions under program
            session_ids = [s.id for s in self.db.query(TrainingSession).filter(TrainingSession.program_id == p.id).all()]
            if not session_ids:
                result.append({
                    "program_id": p.id,
                    "program_code": p.code,
                    "program_title": p.title,
                    "completed": False,
                    "in_progress": False,
                    "last_attended_at": None,
                    "last_certificate_issued_at": None,
                    "last_quiz_score": None,
                    "last_quiz_passed": None,
                })
                continue
            # Attendance
            last_att = (
                self.db.query(TrainingAttendance.created_at)
                .filter(TrainingAttendance.session_id.in_(session_ids), TrainingAttendance.user_id == user_id)
                .order_by(TrainingAttendance.created_at.desc())
                .first()
            )
            # Certificates
            last_cert = (
                self.db.query(TrainingCertificate.issued_at)
                .filter(TrainingCertificate.session_id.in_(session_ids), TrainingCertificate.user_id == user_id)
                .order_by(TrainingCertificate.issued_at.desc())
                .first()
            )
            # Quiz attempts
            quiz_ids = [q.id for q in self.db.query(TrainingQuiz).filter((TrainingQuiz.program_id == p.id) | (TrainingQuiz.session_id.in_(session_ids))).all()]
            last_attempt = None
            if quiz_ids:
                last_attempt = (
                    self.db.query(TrainingQuizAttempt)
                    .filter(TrainingQuizAttempt.quiz_id.in_(quiz_ids), TrainingQuizAttempt.user_id == user_id)
                    .order_by(TrainingQuizAttempt.submitted_at.desc())
                    .first()
                )
            result.append({
                "program_id": p.id,
                "program_code": p.code,
                "program_title": p.title,
                "completed": bool(last_cert),
                "in_progress": (last_att is not None) and (last_cert is None),
                "last_attended_at": last_att[0] if last_att else None,
                "last_certificate_issued_at": last_cert[0] if last_cert else None,
                "last_quiz_score": float(last_attempt.score_percent) if last_attempt else None,
                "last_quiz_passed": bool(last_attempt.passed) if last_attempt else None,
            })
        return result

    def check_eligibility(self, user_id: int, action: str | None = None, ccp_id: int | None = None, equipment_id: int | None = None) -> dict:
        """
        Determine if a user meets role-required trainings.
        - action, ccp_id, equipment_id are placeholders for future scoping; currently role-wide.
        Returns { eligible: bool, required_program_ids: list[int], completed_program_ids: list[int], missing_program_ids: list[int] }
        """
        user: User | None = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.role_id:
            return {
                "eligible": False,
                "required_program_ids": [],
                "completed_program_ids": [],
                "missing_program_ids": [],
            }

        required_records = (
            self.db.query(RoleRequiredTraining)
            .filter(RoleRequiredTraining.role_id == user.role_id, RoleRequiredTraining.is_mandatory == True)
            .all()
        )
        required_program_ids = [r.program_id for r in required_records]
        if not required_program_ids:
            return {
                "eligible": True,
                "required_program_ids": [],
                "completed_program_ids": [],
                "missing_program_ids": [],
            }

        # Determine program_ids with attendance or certificates
        session_programs = (
            self.db.query(TrainingSession.program_id)
            .join(TrainingAttendance, TrainingAttendance.session_id == TrainingSession.id)
            .filter(TrainingAttendance.user_id == user_id, TrainingAttendance.attended == True)
            .distinct()
            .all()
        )
        attended_program_ids = {pid for (pid,) in session_programs}

        cert_programs = (
            self.db.query(TrainingSession.program_id)
            .join(TrainingCertificate, TrainingCertificate.session_id == TrainingSession.id)
            .filter(TrainingCertificate.user_id == user_id)
            .distinct()
            .all()
        )
        certified_program_ids = {pid for (pid,) in cert_programs}

        completed_program_ids = sorted(attended_program_ids.union(certified_program_ids))
        missing = sorted(set(required_program_ids).difference(completed_program_ids))
        return {
            "eligible": len(missing) == 0,
            "required_program_ids": required_program_ids,
            "completed_program_ids": completed_program_ids,
            "missing_program_ids": missing,
        }


