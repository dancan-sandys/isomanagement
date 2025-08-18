"""
Allergen Non-Conformance Service
Automated NC creation for critical allergen issues - ISO 22000 compliant
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.models.nonconformance import (
    NonConformance, NonConformanceSource, NonConformanceStatus,
    CAPAAction, CAPAStatus, ImmediateAction
)
from app.models.allergen_label import AllergenFlag, AllergenFlagSeverity
from app.models.haccp import Product
from app.utils.audit import audit_event


class AllergenNCService:
    """
    Service for creating and managing allergen-related non-conformances
    Integrates with ISO 22000 requirements for allergen control
    """
    
    def __init__(self, db: Session):
        self.db = db

    def create_critical_allergen_nc(
        self,
        allergen_flag: AllergenFlag,
        detected_by: int,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> NonConformance:
        """
        Create non-conformance for critical allergen issues
        ISO 22000 compliant with immediate action requirements
        """
        
        # Get product information
        product = self.db.query(Product).filter(Product.id == allergen_flag.product_id).first()
        product_name = product.name if product else f"Product {allergen_flag.product_id}"
        
        # Generate NC number
        nc_number = self._generate_nc_number("ALG")
        
        # Determine severity and impact
        severity = self._map_allergen_severity_to_nc(allergen_flag.severity)
        impact_area = self._determine_impact_area(allergen_flag.allergen_type, allergen_flag.severity)
        
        # Create NC record
        nc = NonConformance(
            nc_number=nc_number,
            title=f"Critical Allergen Issue: Undeclared {allergen_flag.allergen_type.title()} in {product_name}",
            description=self._generate_nc_description(allergen_flag, product_name, additional_context),
            source=NonConformanceSource.HACCP,  # Allergen control is part of HACCP
            batch_reference=additional_context.get("batch_number") if additional_context else None,
            product_reference=product_name,
            process_reference=additional_context.get("process_step") if additional_context else None,
            location=additional_context.get("location", "Production facility"),
            severity=severity,
            impact_area=impact_area,
            category="Allergen Control",
            status=NonConformanceStatus.OPEN,
            reported_date=datetime.utcnow(),
            target_resolution_date=self._calculate_target_resolution_date(allergen_flag.severity),
            reported_by=detected_by,
            requires_immediate_action=allergen_flag.severity == AllergenFlagSeverity.CRITICAL,
            risk_level=severity,
            escalation_status="pending" if allergen_flag.severity == AllergenFlagSeverity.CRITICAL else "none",
            evidence_files=self._create_evidence_files_list(allergen_flag, additional_context),
            attachments=self._create_attachments_list(allergen_flag)
        )
        
        self.db.add(nc)
        self.db.commit()
        self.db.refresh(nc)
        
        # Create immediate actions for critical allergens
        if allergen_flag.severity == AllergenFlagSeverity.CRITICAL:
            self._create_immediate_actions(nc, allergen_flag)
        
        # Create CAPA actions
        self._create_capa_actions(nc, allergen_flag)
        
        # Update allergen flag with NC reference
        allergen_flag.nc_id = nc.id
        self.db.commit()
        
        # Log audit event
        try:
            audit_event(
                self.db, 
                detected_by, 
                "critical_allergen_nc_created", 
                "allergen_label", 
                str(nc.id),
                {
                    "nc_number": nc_number,
                    "allergen_type": allergen_flag.allergen_type,
                    "product_id": allergen_flag.product_id,
                    "severity": allergen_flag.severity.value,
                    "auto_created": True
                }
            )
        except Exception as e:
            print(f"Warning: Could not log audit event: {e}")
        
        return nc

    def _generate_nc_number(self, prefix: str = "ALG") -> str:
        """Generate unique NC number for allergen issues"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_suffix = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{timestamp}-{unique_suffix}"

    def _map_allergen_severity_to_nc(self, allergen_severity: AllergenFlagSeverity) -> str:
        """Map allergen flag severity to NC severity"""
        mapping = {
            AllergenFlagSeverity.CRITICAL: "critical",
            AllergenFlagSeverity.HIGH: "high",
            AllergenFlagSeverity.MEDIUM: "medium",
            AllergenFlagSeverity.LOW: "low"
        }
        return mapping.get(allergen_severity, "medium")

    def _determine_impact_area(self, allergen_type: str, severity: AllergenFlagSeverity) -> str:
        """Determine impact area based on allergen type and severity"""
        high_risk_allergens = ["peanuts", "tree_nuts", "shellfish", "fish"]
        
        if severity == AllergenFlagSeverity.CRITICAL:
            return "food safety"
        elif allergen_type in high_risk_allergens:
            return "food safety"
        else:
            return "regulatory"

    def _generate_nc_description(
        self, 
        flag: AllergenFlag, 
        product_name: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive NC description"""
        
        description_parts = [
            f"CRITICAL ALLERGEN NON-CONFORMANCE - AUTO-GENERATED",
            f"",
            f"Product: {product_name}",
            f"Allergen Type: {flag.allergen_type.title()}",
            f"Detection Location: {flag.detected_in.value.title()}",
            f"Severity: {flag.severity.value.upper()}",
            f"Detection Method: {flag.additional_data.get('detection_method', 'Unknown') if flag.additional_data else 'Unknown'}",
            f"Confidence Score: {flag.additional_data.get('confidence_score', 'N/A') if flag.additional_data else 'N/A'}",
            f"",
            f"ISSUE DESCRIPTION:",
            f"{flag.description}",
            f"",
            f"DETECTION DETAILS:",
            f"- Source: {flag.additional_data.get('source', 'Not specified') if flag.additional_data else 'Not specified'}",
            f"- Match Term: {flag.additional_data.get('match_term', 'Not specified') if flag.additional_data else 'Not specified'}",
            f"",
            f"IMMEDIATE ACTION REQUIRED:",
            f"{flag.immediate_action}",
        ]
        
        if context:
            description_parts.extend([
                f"",
                f"ADDITIONAL CONTEXT:",
                f"- Batch Number: {context.get('batch_number', 'Not specified')}",
                f"- Process Step: {context.get('process_step', 'Not specified')}",
                f"- Location: {context.get('location', 'Not specified')}",
                f"- Detection Time: {context.get('detection_time', 'Not specified')}",
            ])
        
        description_parts.extend([
            f"",
            f"ISO 22000 COMPLIANCE REQUIREMENTS:",
            f"- This NC must be addressed immediately per ISO 22000 Section 8.9",
            f"- Root cause analysis required per ISO 22000 Section 10.2",
            f"- Corrective actions must be implemented and verified",
            f"- Preventive actions must be evaluated and implemented",
            f"- Management review required for critical food safety issues",
        ])
        
        return "\n".join(description_parts)

    def _calculate_target_resolution_date(self, severity: AllergenFlagSeverity) -> datetime:
        """Calculate target resolution date based on severity"""
        base_date = datetime.utcnow()
        
        if severity == AllergenFlagSeverity.CRITICAL:
            return base_date + timedelta(hours=24)  # 24 hours for critical
        elif severity == AllergenFlagSeverity.HIGH:
            return base_date + timedelta(days=3)    # 3 days for high
        elif severity == AllergenFlagSeverity.MEDIUM:
            return base_date + timedelta(days=7)    # 1 week for medium
        else:
            return base_date + timedelta(days=14)   # 2 weeks for low

    def _create_evidence_files_list(
        self, 
        flag: AllergenFlag, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create evidence files list for the NC"""
        evidence = {
            "allergen_flag_id": flag.id,
            "detection_data": {
                "allergen_type": flag.allergen_type,
                "detected_in": flag.detected_in.value,
                "confidence": flag.additional_data.get("confidence_score") if flag.additional_data else None,
                "detection_method": flag.additional_data.get("detection_method") if flag.additional_data else None
            },
            "screenshots": [],
            "test_results": [],
            "supplier_certificates": [],
            "ingredient_specifications": []
        }
        
        if context and context.get("evidence_files"):
            evidence.update(context["evidence_files"])
        
        return evidence

    def _create_attachments_list(self, flag: AllergenFlag) -> Dict[str, Any]:
        """Create attachments list for the NC"""
        return {
            "allergen_flag_reference": flag.id,
            "detection_timestamp": flag.detected_at.isoformat(),
            "system_generated": True,
            "related_documents": []
        }

    def _create_immediate_actions(self, nc: NonConformance, flag: AllergenFlag) -> None:
        """Create immediate actions for critical allergen NC"""
        
        immediate_actions = [
            {
                "action": "STOP PRODUCTION",
                "description": "Immediately halt production of affected product lines",
                "priority": "critical",
                "due_date": datetime.utcnow() + timedelta(minutes=30)
            },
            {
                "action": "ISOLATE PRODUCTS",
                "description": "Isolate and quarantine all potentially affected products/batches",
                "priority": "critical", 
                "due_date": datetime.utcnow() + timedelta(hours=1)
            },
            {
                "action": "NOTIFY MANAGEMENT",
                "description": "Immediately notify QA manager and food safety team",
                "priority": "critical",
                "due_date": datetime.utcnow() + timedelta(minutes=15)
            },
            {
                "action": "ASSESS RECALL RISK",
                "description": "Evaluate need for product recall and notify regulatory authorities if required",
                "priority": "high",
                "due_date": datetime.utcnow() + timedelta(hours=4)
            },
            {
                "action": "DOCUMENT EVIDENCE",
                "description": "Collect and document all evidence related to the allergen detection",
                "priority": "high",
                "due_date": datetime.utcnow() + timedelta(hours=2)
            }
        ]
        
        for i, action_data in enumerate(immediate_actions):
            action = ImmediateAction(
                non_conformance_id=nc.id,
                action_number=f"IA-{nc.nc_number}-{i+1:02d}",
                description=action_data["action"],
                detailed_description=action_data["description"],
                priority=action_data["priority"],
                due_date=action_data["due_date"],
                status="pending",
                created_at=datetime.utcnow()
            )
            self.db.add(action)
        
        self.db.commit()

    def _create_capa_actions(self, nc: NonConformance, flag: AllergenFlag) -> None:
        """Create CAPA actions for allergen NC"""
        
        capa_actions = [
            {
                "type": "corrective",
                "title": "Update Allergen Declarations",
                "description": f"Update product allergen declarations to include {flag.allergen_type}",
                "due_date": datetime.utcnow() + timedelta(days=1),
                "priority": "high"
            },
            {
                "type": "corrective", 
                "title": "Verify Supplier Information",
                "description": "Review and verify all supplier allergen certificates and specifications",
                "due_date": datetime.utcnow() + timedelta(days=3),
                "priority": "high"
            },
            {
                "type": "corrective",
                "title": "Root Cause Analysis",
                "description": "Conduct thorough root cause analysis to identify why allergen was not declared",
                "due_date": datetime.utcnow() + timedelta(days=5),
                "priority": "high"
            },
            {
                "type": "preventive",
                "title": "Enhance Allergen Control Procedures",
                "description": "Review and enhance allergen control procedures to prevent recurrence",
                "due_date": datetime.utcnow() + timedelta(days=14),
                "priority": "medium"
            },
            {
                "type": "preventive",
                "title": "Staff Training",
                "description": "Provide additional allergen management training to relevant personnel",
                "due_date": datetime.utcnow() + timedelta(days=21),
                "priority": "medium"
            },
            {
                "type": "preventive",
                "title": "Supplier Audit",
                "description": "Schedule allergen-focused audit of affected suppliers",
                "due_date": datetime.utcnow() + timedelta(days=30),
                "priority": "medium"
            }
        ]
        
        for i, capa_data in enumerate(capa_actions):
            capa = CAPAAction(
                non_conformance_id=nc.id,
                action_number=f"CAPA-{nc.nc_number}-{i+1:02d}",
                action_type=capa_data["type"],
                title=capa_data["title"],
                description=capa_data["description"],
                due_date=capa_data["due_date"],
                priority=capa_data["priority"],
                status=CAPAStatus.PENDING,
                created_at=datetime.utcnow()
            )
            self.db.add(capa)
        
        self.db.commit()

    def get_allergen_related_ncs(
        self, 
        product_id: Optional[int] = None,
        allergen_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> list:
        """Get allergen-related non-conformances with filtering"""
        
        query = self.db.query(NonConformance).filter(
            NonConformance.category == "Allergen Control"
        )
        
        if product_id:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if product:
                query = query.filter(NonConformance.product_reference == product.name)
        
        if allergen_type:
            query = query.filter(NonConformance.title.contains(allergen_type.title()))
            
        if status:
            query = query.filter(NonConformance.status == status)
        
        return query.order_by(NonConformance.reported_date.desc()).all()

    def update_nc_from_flag_resolution(self, flag: AllergenFlag, resolved_by: int) -> None:
        """Update NC when allergen flag is resolved"""
        
        if not flag.nc_id:
            return
        
        nc = self.db.query(NonConformance).filter(NonConformance.id == flag.nc_id).first()
        if not nc:
            return
        
        # Update NC status based on flag resolution
        if flag.status == "resolved":
            nc.status = NonConformanceStatus.UNDER_INVESTIGATION
            nc.assigned_to = resolved_by
            nc.assigned_date = datetime.utcnow()
            
            # Add resolution notes to NC description
            if flag.resolution_notes:
                nc.description += f"\n\nALLERGEN FLAG RESOLUTION:\n{flag.resolution_notes}"
                nc.description += f"\nResolved by: User {resolved_by}"
                nc.description += f"\nResolved at: {flag.resolved_at}"
        
        self.db.commit()
        
        # Log audit event
        try:
            audit_event(
                self.db,
                resolved_by,
                "allergen_nc_updated_from_flag",
                "nonconformance",
                str(nc.id),
                {
                    "flag_id": flag.id,
                    "flag_status": flag.status,
                    "resolution_notes": flag.resolution_notes[:100] if flag.resolution_notes else None
                }
            )
        except Exception as e:
            print(f"Warning: Could not log audit event: {e}")

    def get_nc_statistics(self) -> Dict[str, Any]:
        """Get statistics for allergen-related NCs"""
        
        total_allergen_ncs = self.db.query(NonConformance).filter(
            NonConformance.category == "Allergen Control"
        ).count()
        
        open_critical = self.db.query(NonConformance).filter(
            NonConformance.category == "Allergen Control",
            NonConformance.severity == "critical",
            NonConformance.status.in_([
                NonConformanceStatus.OPEN,
                NonConformanceStatus.UNDER_INVESTIGATION,
                NonConformanceStatus.IN_PROGRESS
            ])
        ).count()
        
        overdue = self.db.query(NonConformance).filter(
            NonConformance.category == "Allergen Control",
            NonConformance.target_resolution_date < datetime.utcnow(),
            NonConformance.status != NonConformanceStatus.CLOSED
        ).count()
        
        return {
            "total_allergen_ncs": total_allergen_ncs,
            "open_critical": open_critical,
            "overdue": overdue,
            "compliance_rate": ((total_allergen_ncs - overdue) / total_allergen_ncs * 100) if total_allergen_ncs > 0 else 100
        }