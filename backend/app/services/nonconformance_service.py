from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import uuid

from app.models.nonconformance import (
    NonConformance, RootCauseAnalysis, CAPAAction, CAPAVerification,
    NonConformanceAttachment, NonConformanceSource, NonConformanceStatus,
    CAPAStatus, RootCauseMethod
)
from app.schemas.nonconformance import (
    NonConformanceCreate, NonConformanceUpdate, RootCauseAnalysisCreate,
    RootCauseAnalysisUpdate, CAPAActionCreate, CAPAActionUpdate,
    CAPAVerificationCreate, CAPAVerificationUpdate, NonConformanceAttachmentCreate,
    NonConformanceFilter, CAPAFilter, BulkNonConformanceAction, BulkCAPAAction
)


class NonConformanceService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _decode_text_array_fields(obj: RootCauseAnalysis) -> RootCauseAnalysis:
        """Convert JSON-encoded TEXT array fields back into Python lists for responses."""
        import json as _json
        for field_name in ['contributing_factors', 'system_failures', 'recommendations', 'preventive_measures']:
            value = getattr(obj, field_name, None)
            if isinstance(value, str):
                try:
                    setattr(obj, field_name, _json.loads(value))
                except Exception:
                    # leave as string if not valid JSON
                    pass
        return obj

    def _generate_nc_number(self) -> str:
        """Generate unique NC number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        return f"NC-{timestamp}-{unique_id}"

    def _generate_capa_number(self) -> str:
        """Generate unique CAPA number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        return f"CAPA-{timestamp}-{unique_id}"

    # Non-Conformance operations
    def create_non_conformance(self, nc_data: NonConformanceCreate, reported_by: int) -> NonConformance:
        """Create a new non-conformance"""
        nc_number = self._generate_nc_number()
        
        non_conformance = NonConformance(
            **nc_data.dict(),
            nc_number=nc_number,
            reported_by=reported_by,
            reported_date=datetime.now()
        )
        self.db.add(non_conformance)
        self.db.commit()
        self.db.refresh(non_conformance)
        return non_conformance

    def get_non_conformances(self, filter_params: NonConformanceFilter) -> Dict[str, Any]:
        """Get non-conformances with filtering and pagination"""
        query = self.db.query(NonConformance)

        # Apply filters
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    NonConformance.title.ilike(search_term),
                    NonConformance.description.ilike(search_term),
                    NonConformance.nc_number.ilike(search_term)
                )
            )

        if filter_params.source:
            query = query.filter(NonConformance.source == filter_params.source)

        if filter_params.status:
            query = query.filter(NonConformance.status == filter_params.status)

        if filter_params.severity:
            query = query.filter(NonConformance.severity == filter_params.severity)

        if filter_params.impact_area:
            query = query.filter(NonConformance.impact_area == filter_params.impact_area)

        if filter_params.reported_by:
            query = query.filter(NonConformance.reported_by == filter_params.reported_by)

        if filter_params.assigned_to:
            query = query.filter(NonConformance.assigned_to == filter_params.assigned_to)

        if filter_params.date_from:
            query = query.filter(NonConformance.reported_date >= filter_params.date_from)

        if filter_params.date_to:
            query = query.filter(NonConformance.reported_date <= filter_params.date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        non_conformances = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": non_conformances,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_non_conformance(self, nc_id: int) -> Optional[NonConformance]:
        """Get non-conformance by ID"""
        return self.db.query(NonConformance).filter(NonConformance.id == nc_id).first()

    def update_non_conformance(self, nc_id: int, nc_data: NonConformanceUpdate) -> Optional[NonConformance]:
        """Update non-conformance"""
        non_conformance = self.get_non_conformance(nc_id)
        if not non_conformance:
            return None

        update_data = nc_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(non_conformance, field, value)

        self.db.commit()
        self.db.refresh(non_conformance)
        return non_conformance

    def delete_non_conformance(self, nc_id: int) -> bool:
        """Delete non-conformance"""
        non_conformance = self.get_non_conformance(nc_id)
        if not non_conformance:
            return False

        self.db.delete(non_conformance)
        self.db.commit()
        return True

    def bulk_update_non_conformances(self, action_data: BulkNonConformanceAction) -> Dict[str, Any]:
        """Bulk update non-conformances"""
        non_conformances = self.db.query(NonConformance).filter(
            NonConformance.id.in_(action_data.non_conformance_ids)
        ).all()

        updated_count = 0
        for nc in non_conformances:
            if action_data.action == "assign":
                # This would need additional data for assignment
                pass
            elif action_data.action == "update_status":
                # This would need additional data for status update
                pass
            elif action_data.action == "close":
                nc.status = NonConformanceStatus.CLOSED
                nc.actual_resolution_date = datetime.now()
                updated_count += 1

        self.db.commit()
        return {"updated_count": updated_count, "total_requested": len(action_data.non_conformance_ids)}

    # Root Cause Analysis operations
    def create_root_cause_analysis(self, analysis_data: RootCauseAnalysisCreate, conducted_by: int) -> RootCauseAnalysis:
        """Create a new root cause analysis"""
        payload = analysis_data.dict()

        # Serialize list-based fields destined for TEXT columns to JSON strings
        text_array_fields = [
            'contributing_factors',
            'system_failures',
            'recommendations',
            'preventive_measures',
        ]

        for field_name in text_array_fields:
            value = payload.get(field_name)
            if isinstance(value, (list, dict)):
                payload[field_name] = json.dumps(value)
            elif value is None:
                payload[field_name] = None
            # if it's already a string, leave as-is

        analysis = RootCauseAnalysis(
            **payload,
            conducted_by=conducted_by
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        # Do not decode array fields on the managed instance to avoid flushing lists into TEXT columns
        return analysis

    def get_root_cause_analyses(self, non_conformance_id: int) -> List[RootCauseAnalysis]:
        """Get root cause analyses for a non-conformance"""
        analyses = self.db.query(RootCauseAnalysis).filter(
            RootCauseAnalysis.non_conformance_id == non_conformance_id
        ).all()
        return [self._decode_text_array_fields(a) for a in analyses]

    def get_root_cause_analysis(self, analysis_id: int) -> Optional[RootCauseAnalysis]:
        """Get root cause analysis by ID"""
        analysis = self.db.query(RootCauseAnalysis).filter(RootCauseAnalysis.id == analysis_id).first()
        if analysis:
            return self._decode_text_array_fields(analysis)
        return analysis

    def update_root_cause_analysis(self, analysis_id: int, analysis_data: RootCauseAnalysisUpdate) -> Optional[RootCauseAnalysis]:
        """Update root cause analysis"""
        analysis = self.get_root_cause_analysis(analysis_id)
        if not analysis:
            return None

        update_data = analysis_data.dict(exclude_unset=True)

        # Serialize list-based fields destined for TEXT columns to JSON strings
        text_array_fields = [
            'contributing_factors',
            'system_failures',
            'recommendations',
            'preventive_measures',
        ]
        for field in text_array_fields:
            if field in update_data:
                value = update_data[field]
                if isinstance(value, (list, dict)):
                    update_data[field] = json.dumps(value)
                elif value is None:
                    update_data[field] = None

        for field, value in update_data.items():
            setattr(analysis, field, value)

        self.db.commit()
        self.db.refresh(analysis)
        return self._decode_text_array_fields(analysis)

    def delete_root_cause_analysis(self, analysis_id: int) -> bool:
        """Delete root cause analysis"""
        analysis = self.get_root_cause_analysis(analysis_id)
        if not analysis:
            return False

        self.db.delete(analysis)
        self.db.commit()
        return True

    # CAPA Action operations
    def create_capa_action(self, capa_data: CAPAActionCreate, created_by: int) -> CAPAAction:
        """Create a new CAPA action"""
        capa_number = self._generate_capa_number()
        
        capa_action = CAPAAction(
            **capa_data.dict(),
            capa_number=capa_number,
            created_by=created_by,
            assigned_date=datetime.now()
        )
        self.db.add(capa_action)
        self.db.commit()
        self.db.refresh(capa_action)
        return capa_action

    def get_capa_actions(self, filter_params: CAPAFilter) -> Dict[str, Any]:
        """Get CAPA actions with filtering and pagination"""
        query = self.db.query(CAPAAction)

        # Apply filters
        if filter_params.non_conformance_id:
            query = query.filter(CAPAAction.non_conformance_id == filter_params.non_conformance_id)

        if filter_params.status:
            query = query.filter(CAPAAction.status == filter_params.status)

        if filter_params.responsible_person:
            query = query.filter(CAPAAction.responsible_person == filter_params.responsible_person)

        if filter_params.action_type:
            query = query.filter(CAPAAction.action_type == filter_params.action_type)

        if filter_params.date_from:
            query = query.filter(CAPAAction.assigned_date >= filter_params.date_from)

        if filter_params.date_to:
            query = query.filter(CAPAAction.assigned_date <= filter_params.date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        capa_actions = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": capa_actions,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_capa_action(self, capa_id: int) -> Optional[CAPAAction]:
        """Get CAPA action by ID"""
        return self.db.query(CAPAAction).filter(CAPAAction.id == capa_id).first()

    def update_capa_action(self, capa_id: int, capa_data: CAPAActionUpdate) -> Optional[CAPAAction]:
        """Update CAPA action"""
        capa_action = self.get_capa_action(capa_id)
        if not capa_action:
            return None

        update_data = capa_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(capa_action, field, value)

        # Update status based on progress
        if 'progress_percentage' in update_data:
            if capa_action.progress_percentage >= 100:
                capa_action.status = CAPAStatus.COMPLETED
                capa_action.actual_completion_date = datetime.now()

        self.db.commit()
        self.db.refresh(capa_action)
        return capa_action

    def delete_capa_action(self, capa_id: int) -> bool:
        """Delete CAPA action"""
        capa_action = self.get_capa_action(capa_id)
        if not capa_action:
            return False

        self.db.delete(capa_action)
        self.db.commit()
        return True

    def bulk_update_capa_actions(self, action_data: BulkCAPAAction) -> Dict[str, Any]:
        """Bulk update CAPA actions"""
        capa_actions = self.db.query(CAPAAction).filter(
            CAPAAction.id.in_(action_data.capa_ids)
        ).all()

        updated_count = 0
        for capa in capa_actions:
            if action_data.action == "update_status":
                # This would need additional data for status update
                pass
            elif action_data.action == "assign":
                # This would need additional data for assignment
                pass
            elif action_data.action == "complete":
                capa.status = CAPAStatus.COMPLETED
                capa.progress_percentage = 100.0
                capa.actual_completion_date = datetime.now()
                updated_count += 1

        self.db.commit()
        return {"updated_count": updated_count, "total_requested": len(action_data.capa_ids)}

    # CAPA Verification operations
    def create_capa_verification(self, verification_data: CAPAVerificationCreate, verified_by: int) -> CAPAVerification:
        """Create a new CAPA verification"""
        verification = CAPAVerification(
            **verification_data.dict(),
            verified_by=verified_by
        )
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification

    def get_capa_verifications(self, non_conformance_id: int) -> List[CAPAVerification]:
        """Get CAPA verifications for a non-conformance"""
        return self.db.query(CAPAVerification).filter(
            CAPAVerification.non_conformance_id == non_conformance_id
        ).all()

    def get_capa_verification(self, verification_id: int) -> Optional[CAPAVerification]:
        """Get CAPA verification by ID"""
        return self.db.query(CAPAVerification).filter(CAPAVerification.id == verification_id).first()

    def update_capa_verification(self, verification_id: int, verification_data: CAPAVerificationUpdate) -> Optional[CAPAVerification]:
        """Update CAPA verification"""
        verification = self.get_capa_verification(verification_id)
        if not verification:
            return None

        update_data = verification_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(verification, field, value)

        self.db.commit()
        self.db.refresh(verification)
        return verification

    def delete_capa_verification(self, verification_id: int) -> bool:
        """Delete CAPA verification"""
        verification = self.get_capa_verification(verification_id)
        if not verification:
            return False

        self.db.delete(verification)
        self.db.commit()
        return True

    # Attachment operations
    def create_attachment(self, attachment_data: NonConformanceAttachmentCreate, uploaded_by: int) -> NonConformanceAttachment:
        """Create a new attachment"""
        attachment = NonConformanceAttachment(
            **attachment_data.dict(),
            uploaded_by=uploaded_by
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def get_attachments(self, non_conformance_id: int) -> List[NonConformanceAttachment]:
        """Get attachments for a non-conformance"""
        return self.db.query(NonConformanceAttachment).filter(
            NonConformanceAttachment.non_conformance_id == non_conformance_id
        ).all()

    def get_attachment(self, attachment_id: int) -> Optional[NonConformanceAttachment]:
        """Get attachment by ID"""
        return self.db.query(NonConformanceAttachment).filter(NonConformanceAttachment.id == attachment_id).first()

    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete attachment"""
        attachment = self.get_attachment(attachment_id)
        if not attachment:
            return False

        self.db.delete(attachment)
        self.db.commit()
        return True

    # Dashboard operations
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get non-conformance dashboard statistics"""
        total_non_conformances = self.db.query(NonConformance).count()
        open_non_conformances = self.db.query(NonConformance).filter(
            NonConformance.status.in_([NonConformanceStatus.OPEN, NonConformanceStatus.UNDER_INVESTIGATION])
        ).count()

        # Overdue CAPAs (target_completion_date < today and status not completed)
        overdue_capas = self.db.query(CAPAAction).filter(
            and_(
                CAPAAction.target_completion_date < datetime.now(),
                CAPAAction.status != CAPAStatus.COMPLETED
            )
        ).count()

        # Non-conformances by source
        ncs_by_source = self.db.query(
            NonConformance.source,
            func.count(NonConformance.id).label('count')
        ).group_by(NonConformance.source).all()

        # Non-conformances by status
        ncs_by_status = self.db.query(
            NonConformance.status,
            func.count(NonConformance.id).label('count')
        ).group_by(NonConformance.status).all()

        # Non-conformances by severity
        ncs_by_severity = self.db.query(
            NonConformance.severity,
            func.count(NonConformance.id).label('count')
        ).group_by(NonConformance.severity).all()

        # Recent non-conformances (last 30 days)
        recent_ncs = self.db.query(NonConformance).filter(
            NonConformance.reported_date >= datetime.now() - timedelta(days=30)
        ).order_by(desc(NonConformance.reported_date)).limit(5).all()

        # CAPA completion rate
        total_capas = self.db.query(CAPAAction).count()
        completed_capas = self.db.query(CAPAAction).filter(
            CAPAAction.status == CAPAStatus.COMPLETED
        ).count()
        capa_completion_rate = (completed_capas / total_capas * 100) if total_capas > 0 else 0

        # Average resolution time
        completed_ncs = self.db.query(NonConformance).filter(
            and_(
                NonConformance.actual_resolution_date.isnot(None),
                NonConformance.reported_date.isnot(None)
            )
        ).all()

        total_resolution_time = 0
        count = 0
        for nc in completed_ncs:
            resolution_time = (nc.actual_resolution_date - nc.reported_date).days
            total_resolution_time += resolution_time
            count += 1

        average_resolution_time = total_resolution_time / count if count > 0 else 0

        return {
            "total_non_conformances": total_non_conformances,
            "open_non_conformances": open_non_conformances,
            "overdue_capas": overdue_capas,
            "non_conformances_by_source": [
                {"source": item.source, "count": item.count} 
                for item in ncs_by_source
            ],
            "non_conformances_by_status": [
                {"status": item.status, "count": item.count} 
                for item in ncs_by_status
            ],
            "non_conformances_by_severity": [
                {"severity": item.severity, "count": item.count} 
                for item in ncs_by_severity
            ],
            "recent_non_conformances": [
                {
                    "id": nc.id,
                    "nc_number": nc.nc_number,
                    "title": nc.title,
                    "status": nc.status,
                    "severity": nc.severity,
                    "reported_date": nc.reported_date
                }
                for nc in recent_ncs
            ],
            "capa_completion_rate": capa_completion_rate,
            "average_resolution_time": average_resolution_time
        }

    # Utility methods
    def get_overdue_capas(self) -> List[Dict[str, Any]]:
        """Get overdue CAPA actions"""
        overdue_capas = self.db.query(CAPAAction).filter(
            and_(
                CAPAAction.target_completion_date < datetime.now(),
                CAPAAction.status != CAPAStatus.COMPLETED
            )
        ).all()

        return [
            {
                "capa_id": capa.id,
                "capa_number": capa.capa_number,
                "title": capa.title,
                "responsible_person": capa.responsible_person,
                "target_completion_date": capa.target_completion_date,
                "days_overdue": (datetime.now() - capa.target_completion_date).days
            }
            for capa in overdue_capas
        ]

    def get_non_conformances_by_source(self, source: NonConformanceSource) -> List[Dict[str, Any]]:
        """Get non-conformances by source"""
        ncs = self.db.query(NonConformance).filter(
            NonConformance.source == source
        ).all()

        return [
            {
                "id": nc.id,
                "nc_number": nc.nc_number,
                "title": nc.title,
                "status": nc.status,
                "severity": nc.severity,
                "reported_date": nc.reported_date
            }
            for nc in ncs
        ] 

    def get_recent_nc_for_haccp(self, ccp_id: int, batch_number: Optional[str]) -> Optional[NonConformance]:
        """Get the most recent HACCP-origin NC for a given CCP and optional batch number"""
        query = self.db.query(NonConformance).filter(
            NonConformance.source == NonConformanceSource.HACCP
        )
        if batch_number:
            query = query.filter(NonConformance.batch_reference == batch_number)
        # process_reference may contain 'CCP:{id}'
        like_pattern = f"%CCP:{ccp_id}%"
        query = query.filter(NonConformance.process_reference.ilike(like_pattern))
        return query.order_by(desc(NonConformance.created_at)).first()