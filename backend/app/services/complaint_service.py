from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.complaint import Complaint, ComplaintStatus, ComplaintCommunication, ComplaintInvestigation
from app.models.nonconformance import NonConformance, NonConformanceSource
from app.models.traceability import Batch
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, CommunicationCreate, InvestigationCreate, InvestigationUpdate


class ComplaintService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_number(self) -> str:
        prefix = "CMP-"
        count = self.db.query(func.count(Complaint.id)).scalar() or 0
        return f"{prefix}{datetime.utcnow().strftime('%Y%m%d')}-{count+1:04d}"

    def create_complaint(self, payload: ComplaintCreate, user_id: int) -> Complaint:
        number = self._generate_number()
        comp = Complaint(
            complaint_number=number,
            complaint_date=payload.complaint_date or datetime.utcnow(),
            received_via=payload.received_via,
            customer_name=payload.customer_name,
            customer_contact=payload.customer_contact,
            description=payload.description,
            classification=payload.classification,
            severity=payload.severity or "medium",
            batch_id=payload.batch_id,
            product_id=payload.product_id,
            attachments=payload.attachments or [],
            created_by=user_id,
        )
        self.db.add(comp)
        self.db.commit()
        self.db.refresh(comp)

        # Auto-link to NC if desired policy: create NC placeholder for complaints
        try:
            nc = NonConformance(
                nc_number=f"NC-{number}",
                title=f"Customer Complaint: {payload.classification.value}",
                description=payload.description,
                source=NonConformanceSource.COMPLAINT,
                batch_reference=str(payload.batch_id) if payload.batch_id else None,
                status=None,  # let service default
                reported_date=datetime.utcnow(),
                reported_by=user_id,
            )
            self.db.add(nc)
            self.db.commit()
            self.db.refresh(nc)
            comp.non_conformance_id = nc.id
            self.db.commit()
            self.db.refresh(comp)
        except Exception:
            self.db.rollback()

        return comp

    def update_complaint(self, complaint_id: int, payload: ComplaintUpdate) -> Optional[Complaint]:
        comp = self.db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not comp:
            return None
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(comp, field, value)
        comp.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(comp)
        return comp

    def get_complaint(self, complaint_id: int) -> Optional[Complaint]:
        return self.db.query(Complaint).filter(Complaint.id == complaint_id).first()

    def list_complaints(self, page: int = 1, size: int = 20) -> Dict[str, Any]:
        q = self.db.query(Complaint).order_by(Complaint.created_at.desc())
        total = q.count()
        items = q.offset((page - 1) * size).limit(size).all()
        pages = (total + size - 1) // size
        return {"items": items, "total": total, "page": page, "size": size, "pages": pages}

    # Communications
    def add_communication(self, complaint_id: int, payload: CommunicationCreate, user_id: int) -> Optional[ComplaintCommunication]:
        comp = self.get_complaint(complaint_id)
        if not comp:
            return None
        com = ComplaintCommunication(
            complaint_id=complaint_id,
            channel=payload.channel,
            sender=payload.sender,
            recipient=payload.recipient,
            message=payload.message,
            created_by=user_id,
        )
        self.db.add(com)
        self.db.commit()
        self.db.refresh(com)
        return com

    # Investigation
    def create_or_get_investigation(self, complaint_id: int, payload: InvestigationCreate) -> Optional[ComplaintInvestigation]:
        comp = self.get_complaint(complaint_id)
        if not comp:
            return None
        inv = self.db.query(ComplaintInvestigation).filter(ComplaintInvestigation.complaint_id == complaint_id).first()
        if inv:
            return inv
        inv = ComplaintInvestigation(
            complaint_id=complaint_id,
            investigator_id=payload.investigator_id,
            summary=payload.summary,
        )
        self.db.add(inv)
        self.db.commit()
        self.db.refresh(inv)
        return inv

    def update_investigation(self, complaint_id: int, payload: InvestigationUpdate) -> Optional[ComplaintInvestigation]:
        inv = self.db.query(ComplaintInvestigation).filter(ComplaintInvestigation.complaint_id == complaint_id).first()
        if not inv:
            return None
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(inv, field, value)
        self.db.commit()
        self.db.refresh(inv)
        return inv

    # Trends/Reports
    def get_trends(self) -> Dict[str, Any]:
        # by classification
        rows = self.db.query(Complaint.classification, func.count(Complaint.id)).group_by(Complaint.classification).all()
        by_classification = [{"classification": str(c.value if hasattr(c, 'value') else c), "count": int(n)} for c, n in rows]
        # by severity
        rows2 = self.db.query(Complaint.severity, func.count(Complaint.id)).group_by(Complaint.severity).all()
        by_severity = [{"severity": s, "count": int(n)} for s, n in rows2]
        # monthly counts
        rows3 = self.db.query(func.strftime('%Y-%m', Complaint.complaint_date), func.count(Complaint.id)).group_by(func.strftime('%Y-%m', Complaint.complaint_date)).all()
        monthly_counts = [{"month": m, "count": int(n)} for m, n in rows3]
        return {"by_classification": by_classification, "by_severity": by_severity, "monthly_counts": monthly_counts}

    # Reads
    def list_communications(self, complaint_id: int):
        return self.db.query(ComplaintCommunication).filter(ComplaintCommunication.complaint_id == complaint_id).order_by(ComplaintCommunication.communication_date.asc()).all()

    def get_investigation(self, complaint_id: int) -> Optional[ComplaintInvestigation]:
        return self.db.query(ComplaintInvestigation).filter(ComplaintInvestigation.complaint_id == complaint_id).first()


