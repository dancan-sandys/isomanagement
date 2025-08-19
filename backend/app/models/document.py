from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DocumentType(str, enum.Enum):
    POLICY = "policy"
    PROCEDURE = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    FORM = "form"
    RECORD = "record"
    MANUAL = "manual"
    SPECIFICATION = "specification"
    PLAN = "plan"
    CHECKLIST = "checklist"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class DocumentCategory(str, enum.Enum):
    HACCP = "haccp"
    PRP = "prp"
    TRAINING = "training"
    AUDIT = "audit"
    MAINTENANCE = "maintenance"
    SUPPLIER = "supplier"
    QUALITY = "quality"
    SAFETY = "safety"
    GENERAL = "general"
    PRODUCTION = "production"
    HR = "hr"
    FINANCE = "finance"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    document_type = Column(
        Enum(
            DocumentType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    category = Column(
        Enum(
            DocumentCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    status = Column(
        Enum(
            DocumentStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
        default=DocumentStatus.DRAFT,
    )
    version = Column(String(20), nullable=False, default="1.0")
    
    # File information
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(50))
    original_filename = Column(String(255))
    
    # Department and product information
    department = Column(String(100))
    product_line = Column(String(100))
    applicable_products = Column(Text)  # JSON string of product IDs
    
    # Approval information
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    effective_date = Column(DateTime(timezone=True))
    review_date = Column(DateTime(timezone=True))
    
    # Keywords for search
    keywords = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    approvals = relationship("DocumentApproval", back_populates="document", cascade="all, delete-orphan")
    change_logs = relationship("DocumentChangeLog", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, document_number='{self.document_number}', title='{self.title}')>"


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    original_filename = Column(String(255))
    
    # Change information
    change_description = Column(Text)
    change_reason = Column(Text)
    
    # Approval information
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="versions")
    
    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, version='{self.version_number}')>"


class DocumentApproval(Base):
    __tablename__ = "document_approvals"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_order = Column(Integer, nullable=False)  # 1, 2, 3 for sequential approvals
    status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    comments = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="approvals")
    # approver = relationship("User", back_populates="document_approvals")  # Commented out to avoid circular dependency
    
    def __repr__(self):
        return f"<DocumentApproval(id={self.id}, document_id={self.document_id}, approver_id={self.approver_id})>"


class DocumentChangeLog(Base):
    __tablename__ = "document_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    change_type = Column(String(50), nullable=False)  # created, updated, approved, obsoleted
    change_description = Column(Text)
    old_version = Column(String(20))
    new_version = Column(String(20))
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="change_logs")
    
    def __repr__(self):
        return f"<DocumentChangeLog(id={self.id}, document_id={self.document_id}, change_type='{self.change_type}')>"


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    document_type = Column(
        Enum(
            DocumentType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    category = Column(
        Enum(
            DocumentCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        nullable=False,
    )
    template_file_path = Column(String(500))
    template_content = Column(Text)  # For rich text templates
    
    # Template metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name='{self.name}', type='{self.document_type}')>" 


class DocumentTemplateVersion(Base):
    __tablename__ = "document_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    version_number = Column(String(20), nullable=False)
    template_file_path = Column(String(500))
    template_content = Column(Text)
    change_description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DocumentTemplateApproval(Base):
    __tablename__ = "document_template_approvals"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_order = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    comments = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DocumentDistribution(Base):
    __tablename__ = "document_distributions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    copy_number = Column(String(50))
    notes = Column(Text)
    distributed_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))