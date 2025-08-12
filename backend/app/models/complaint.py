from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ComplaintClassification(str, enum.Enum):
    FOREIGN_OBJECT = "foreign_object"
    OFF_FLAVOR = "off_flavor"
    PACKAGING = "packaging"
    MICROBIOLOGY = "microbiology"
    ALLERGEN = "allergen"
    LABELLING = "labelling"
    OTHER = "other"


class CommunicationChannel(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    MEETING = "meeting"
    OTHER = "other"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_number = Column(String(50), unique=True, index=True, nullable=False)
    complaint_date = Column(DateTime(timezone=True), nullable=False)
    received_via = Column(String(50))
    customer_name = Column(String(200), nullable=False)
    customer_contact = Column(String(200))
    description = Column(Text, nullable=False)
    classification = Column(Enum(ComplaintClassification), nullable=False, default=ComplaintClassification.OTHER)
    severity = Column(String(20), default="medium")
    status = Column(Enum(ComplaintStatus), nullable=False, default=ComplaintStatus.OPEN)

    # Linkages
    batch_id = Column(Integer, ForeignKey("batches.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"))

    attachments = Column(JSON)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    communications = relationship("ComplaintCommunication", back_populates="complaint", cascade="all, delete-orphan")
    investigation = relationship("ComplaintInvestigation", back_populates="complaint", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Complaint(id={self.id}, number='{self.complaint_number}', customer='{self.customer_name}')>"


class ComplaintCommunication(Base):
    __tablename__ = "complaint_communications"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    communication_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    channel = Column(Enum(CommunicationChannel), nullable=False, default=CommunicationChannel.OTHER)
    sender = Column(String(200))
    recipient = Column(String(200))
    message = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    complaint = relationship("Complaint", back_populates="communications")

    def __repr__(self):
        return f"<ComplaintCommunication(id={self.id}, complaint_id={self.complaint_id}, channel='{self.channel}')>"


class ComplaintInvestigation(Base):
    __tablename__ = "complaint_investigations"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    investigator_id = Column(Integer, ForeignKey("users.id"))
    root_cause_analysis_id = Column(Integer, ForeignKey("root_cause_analyses.id"))
    summary = Column(Text)
    outcome = Column(Text)

    complaint = relationship("Complaint", back_populates="investigation")

    def __repr__(self):
        return f"<ComplaintInvestigation(id={self.id}, complaint_id={self.complaint_id})>"


