#!/usr/bin/env python3
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User
from app.models.document import Document, DocumentStatus, DocumentType, DocumentCategory, DocumentVersion, DocumentChangeLog, DocumentTemplate, DocumentTemplateVersion
from app.models.prp import PRPProgram, PRPCategory, PRPStatus, PRPFrequency, PRPChecklist
from app.models.haccp import Product, ProcessFlow, Hazard, HazardType, CCP


def get_admin(db: Session) -> User:
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        raise RuntimeError("Admin user not found; run create_admin_user.py first")
    return admin


def seed_documents(db: Session, admin: User) -> None:
    # Template
    tpl = DocumentTemplate(
        name="Generic SOP Template",
        description="A simple SOP template",
        document_type=DocumentType.PROCEDURE,
        category=DocumentCategory.QUALITY,
        template_content="Template Content",
        is_active=True,
        created_by=admin.id,
    )
    db.add(tpl)
    db.flush()
    tpl_v = DocumentTemplateVersion(
        template_id=tpl.id,
        version_number="1.0",
        template_content="Template v1",
        created_by=admin.id,
    )
    db.add(tpl_v)

    # Document
    doc = Document(
        document_number="DOC-0001",
        title="Quality Policy",
        description="Quality policy document",
        document_type=DocumentType.POLICY,
        category=DocumentCategory.QUALITY,
        status=DocumentStatus.APPROVED,
        version="1.0",
        created_by=admin.id,
        approved_by=admin.id,
        approved_at=datetime.utcnow(),
    )
    db.add(doc)
    db.flush()
    dv = DocumentVersion(
        document_id=doc.id,
        version_number="1.0",
        file_path="/tmp/quality_policy_v1.pdf",
        original_filename="quality_policy_v1.pdf",
        created_by=admin.id,
        approved_by=admin.id,
        approved_at=datetime.utcnow(),
    )
    db.add(dv)
    dcl = DocumentChangeLog(
        document_id=doc.id,
        change_type="approved",
        change_description="Initial approval",
        old_version=None,
        new_version="1.0",
        changed_by=admin.id,
    )
    db.add(dcl)


def seed_prp(db: Session, admin: User) -> None:
    program = PRPProgram(
        program_code="PRP-001",
        name="Cleaning and Sanitizing",
        description="PRP per ISO 22002-1",
        category=PRPCategory.CLEANING_AND_SANITIZING,
        status=PRPStatus.ACTIVE,
        objective="Ensure effective cleaning",
        scope="All production areas",
        responsible_department="QA",
        responsible_person=admin.id,
        frequency=PRPFrequency.MONTHLY,
        frequency_details="Monthly checks",
        sop_reference="SOP-CLEAN-01",
        created_by=admin.id,
    )
    db.add(program)
    db.flush()
    checklist = PRPChecklist(
        program_id=program.id,
        checklist_code="CHK-PRP-001",
        name="Monthly Cleaning Checklist",
        scheduled_date=datetime.utcnow(),
        due_date=datetime.utcnow(),
        assigned_to=admin.id,
        created_by=admin.id,
    )
    db.add(checklist)


def seed_haccp(db: Session, admin: User) -> None:
    product = Product(
        product_code="MILK-01",
        name="UHT Milk",
        description="UHT milk product",
        category="milk",
        created_by=admin.id,
        haccp_plan_approved=True,
        haccp_plan_version="1.0",
        haccp_plan_approved_by=admin.id,
        haccp_plan_approved_at=datetime.utcnow(),
    )
    db.add(product)
    db.flush()
    flow = ProcessFlow(
        product_id=product.id,
        step_number=1,
        step_name="Reception",
        description="Raw milk reception",
        created_by=admin.id,
    )
    db.add(flow)
    db.flush()
    hazard = Hazard(
        product_id=product.id,
        process_step_id=flow.id,
        hazard_type=HazardType.BIOLOGICAL,
        hazard_name="Pathogens",
        description="Potential biological hazards",
        created_by=admin.id,
    )
    db.add(hazard)
    db.flush()
    ccp = CCP(
        product_id=product.id,
        hazard_id=hazard.id,
        ccp_number="CCP-1",
        ccp_name="Thermal Treatment",
        description="Heat treatment CCP",
        created_by=admin.id,
    )
    db.add(ccp)


def main() -> None:
    db = SessionLocal()
    try:
        admin = get_admin(db)
        seed_documents(db, admin)
        seed_prp(db, admin)
        seed_haccp(db, admin)
        db.commit()
        print("✅ Minimal core seed inserted (documents, PRP, HACCP)")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


