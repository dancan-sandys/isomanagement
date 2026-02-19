from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.supplier import (
    Supplier, Material, SupplierEvaluation, IncomingDelivery, 
    SupplierDocument, SupplierStatus, SupplierCategory, 
    EvaluationStatus, InspectionStatus, InspectionChecklist, InspectionChecklistItem
)
from app.models.user import User
from app.schemas.supplier import (
    SupplierCreate, SupplierUpdate, MaterialCreate, MaterialUpdate,
    SupplierEvaluationCreate, SupplierEvaluationUpdate, IncomingDeliveryCreate,
    IncomingDeliveryUpdate, SupplierDocumentCreate, SupplierDocumentUpdate,
    SupplierFilter, MaterialFilter, EvaluationFilter, DeliveryFilter,
    BulkSupplierAction, BulkMaterialAction, InspectionChecklistCreate, InspectionChecklistUpdate, InspectionChecklistItemCreate, InspectionChecklistItemUpdate
)


class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    # Supplier operations
    def create_supplier(self, supplier_data: SupplierCreate, created_by: int) -> Supplier:
        """Create a new supplier"""
        from datetime import datetime
        
        supplier = Supplier(
            **supplier_data.dict(),
            created_by=created_by,
            updated_at=datetime.utcnow()  # Set updated_at to current time
        )
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def get_suppliers(self, filter_params: SupplierFilter) -> Dict[str, Any]:
        """Get suppliers with filtering and pagination (robust to invalid enum rows)."""
        from sqlalchemy import cast, String
        # Project columns and cast enum columns to String to avoid coercion errors on bad rows
        query = self.db.query(
            Supplier.id,
            Supplier.supplier_code,
            Supplier.name,
            cast(Supplier.category, String).label("category"),
            cast(Supplier.status, String).label("status"),
            Supplier.contact_person,
            Supplier.email,
            Supplier.phone,
            Supplier.website,
            Supplier.address_line1,
            Supplier.address_line2,
            Supplier.city,
            Supplier.state,
            Supplier.postal_code,
            Supplier.country,
            Supplier.business_registration_number,
            Supplier.tax_identification_number,
            Supplier.company_type,
            Supplier.year_established,
            Supplier.risk_level,
            Supplier.notes,
            Supplier.overall_score,
            Supplier.last_evaluation_date,
            Supplier.next_evaluation_date,
            Supplier.created_at,
            Supplier.updated_at,
            Supplier.created_by,
        )

        # Apply filters
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.supplier_code.ilike(search_term),
                    Supplier.contact_person.ilike(search_term)
                )
            )

        if filter_params.category:
            query = query.filter(cast(Supplier.category, String) == str(filter_params.category))

        if filter_params.status:
            query = query.filter(cast(Supplier.status, String) == str(filter_params.status))

        if filter_params.risk_level:
            query = query.filter(Supplier.risk_level == filter_params.risk_level)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        suppliers = query.offset(offset).limit(filter_params.size).all()

        # Pre-compute materials count by supplier for this page set
        material_counts_rows = (
            self.db.query(Material.supplier_id, func.count(Material.id))
            .group_by(Material.supplier_id)
            .all()
        )
        supplier_id_to_material_count = {sid: int(cnt) for sid, cnt in material_counts_rows}

        def normalize_enum(val: Any) -> str:
            try:
                return (val.value if hasattr(val, "value") else str(val)).lower()
            except Exception:
                return str(val).lower() if val is not None else ""

        # Serialize suppliers with normalized enums to satisfy Pydantic schemas
        items: List[Dict[str, Any]] = []
        for s in suppliers:
            creator = self.db.query(User).filter(User.id == s.created_by).first()
            created_by_name = creator.full_name if creator and creator.full_name else (creator.username if creator else "Unknown")
            items.append({
                "id": s.id,
                "supplier_code": s.supplier_code,
                "name": s.name,
                "category": normalize_enum(getattr(s, "category", None)),
                "status": normalize_enum(getattr(s, "status", None)),
                "contact_person": s.contact_person,
                "email": s.email,
                "phone": s.phone,
                "website": s.website,
                "address_line1": s.address_line1,
                "address_line2": s.address_line2,
                "city": s.city,
                "state": s.state,
                "postal_code": s.postal_code,
                "country": s.country,
                "business_registration_number": s.business_registration_number,
                "tax_identification_number": s.tax_identification_number,
                "company_type": s.company_type,
                "year_established": s.year_established,
                "risk_level": s.risk_level,
                "notes": s.notes,
                "overall_score": float(s.overall_score or 0.0),
                "last_evaluation_date": s.last_evaluation_date,
                "next_evaluation_date": s.next_evaluation_date,
                "materials_count": supplier_id_to_material_count.get(s.id, 0),
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "created_by": s.created_by,
                "created_by_name": created_by_name,
            })

        return {
            "items": items,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID"""
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def update_supplier(self, supplier_id: int, supplier_data: SupplierUpdate) -> Optional[Supplier]:
        """Update supplier"""
        from datetime import datetime
        
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            return None

        update_data = supplier_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        
        # Set updated_at to current time
        supplier.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete supplier"""
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            return False

        self.db.delete(supplier)
        self.db.commit()
        return True

    def bulk_update_suppliers(self, action_data: BulkSupplierAction) -> Dict[str, Any]:
        """Bulk update suppliers"""
        suppliers = self.db.query(Supplier).filter(
            Supplier.id.in_(action_data.supplier_ids)
        ).all()

        updated_count = 0
        for supplier in suppliers:
            if action_data.action == "activate":
                supplier.status = SupplierStatus.ACTIVE
            elif action_data.action == "deactivate":
                supplier.status = SupplierStatus.INACTIVE
            elif action_data.action == "suspend":
                supplier.status = SupplierStatus.SUSPENDED
            elif action_data.action == "blacklist":
                supplier.status = SupplierStatus.BLACKLISTED
            else:
                continue
            updated_count += 1

        self.db.commit()
        return {"updated_count": updated_count, "total_requested": len(action_data.supplier_ids)}

    # Material operations
    def create_material(self, material_data: MaterialCreate, created_by: int) -> Material:
        """Create a new material"""
        import json as _json
        
        # Get the validated data
        material_dict = material_data.dict()
        
        # Normalize list-like fields destined for Text columns by JSON-encoding them
        allergens = material_dict.get("allergens")
        if allergens is not None:
            if isinstance(allergens, list):
                material_dict["allergens"] = _json.dumps(allergens) if allergens else None
            elif not isinstance(allergens, str):
                material_dict["allergens"] = None
        
        quality_params = material_dict.get("quality_parameters")
        if quality_params is not None:
            if isinstance(quality_params, list):
                material_dict["quality_parameters"] = _json.dumps(quality_params) if quality_params else None
            elif not isinstance(quality_params, str):
                material_dict["quality_parameters"] = None
        
        # Specifications should already be converted to dict by the validator
        # Ensure it's a dict or None
        specs = material_dict.get("specifications")
        if specs is not None and isinstance(specs, list):
            specs_dict = {}
            for spec in specs:
                if isinstance(spec, dict) and "parameter_name" in spec:
                    specs_dict[spec["parameter_name"]] = spec
            material_dict["specifications"] = specs_dict if specs_dict else None
        
        # Create Material with only valid fields
        try:
            material = Material(
                material_code=material_dict["material_code"],
                name=material_dict["name"],
                description=material_dict.get("description"),
                category=material_dict.get("category"),
                supplier_id=material_dict["supplier_id"],
                supplier_material_code=material_dict.get("supplier_material_code"),
                specifications=material_dict.get("specifications"),
                quality_parameters=material_dict.get("quality_parameters"),
                acceptable_limits=material_dict.get("acceptable_limits"),
                allergens=material_dict.get("allergens"),
                allergen_statement=material_dict.get("allergen_statement"),
                storage_conditions=material_dict.get("storage_conditions"),
                shelf_life_days=material_dict.get("shelf_life_days"),
                handling_instructions=material_dict.get("handling_instructions"),
                created_by=created_by
            )
            self.db.add(material)
            try:
                self.db.commit()
            except Exception as commit_error:
                self.db.rollback()
                raise commit_error
            self.db.refresh(material)
            # Return the material - MaterialResponse validators will handle JSON string to list conversion
            return material
        except Exception as e:
            self.db.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating material: {type(e).__name__}: {str(e)}", exc_info=True)
            
            # Check for SQLAlchemy IntegrityError
            from sqlalchemy.exc import IntegrityError
            if isinstance(e, IntegrityError):
                error_str = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
                if "unique constraint" in error_str or "duplicate" in error_str or "UNIQUE constraint failed" in error_str:
                    if "material_code" in error_str or "materials.material_code" in error_str:
                        raise ValueError(f"Material code '{material_dict['material_code']}' already exists. Material codes must be globally unique.")
                    else:
                        raise ValueError(f"Database constraint violation: {error_str}")
                elif "foreign key" in error_str or "FOREIGN KEY constraint failed" in error_str:
                    if "supplier" in error_str or "suppliers.id" in error_str:
                        raise ValueError(f"Supplier with ID {material_dict['supplier_id']} does not exist.")
                    else:
                        raise ValueError(f"Foreign key constraint violation: {error_str}")
                else:
                    raise ValueError(f"Database integrity error: {str(e.orig) if hasattr(e, 'orig') else str(e)}")
            
            # Check for other database errors
            error_str = str(e).lower()
            if "unique constraint" in error_str or "duplicate" in error_str:
                if "material_code" in error_str:
                    raise ValueError(f"Material code '{material_dict['material_code']}' already exists. Material codes must be globally unique.")
            elif "foreign key" in error_str:
                if "supplier" in error_str:
                    raise ValueError(f"Supplier with ID {material_dict['supplier_id']} does not exist.")
            
            # Re-raise with original message if it's a different error
            raise ValueError(f"Failed to create material: {type(e).__name__}: {str(e)}")

    def get_materials(self, filter_params: MaterialFilter) -> Dict[str, Any]:
        """Get materials with filtering and pagination"""
        query = self.db.query(Material)

        # Apply filters
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    Material.name.ilike(search_term),
                    Material.material_code.ilike(search_term)
                )
            )

        if filter_params.category:
            query = query.filter(Material.category == filter_params.category)

        if filter_params.supplier_id:
            query = query.filter(Material.supplier_id == filter_params.supplier_id)

        if filter_params.approval_status:
            query = query.filter(Material.approval_status == filter_params.approval_status)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        materials = query.offset(offset).limit(filter_params.size).all()

        # Normalize list-like fields for response safety
        normalized_items = [self._material_to_response_safe(m) for m in materials]

        return {
            "items": normalized_items,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_material(self, material_id: int) -> Optional[Material]:
        """Get material by ID"""
        material = self.db.query(Material).filter(Material.id == material_id).first()
        return self._material_to_response_safe(material) if material else None

    def update_material(self, material_id: int, material_data: MaterialUpdate) -> Optional[Material]:
        """Update material"""
        material = self.get_material(material_id)
        if not material:
            return None

        update_data = material_data.dict(exclude_unset=True)
        # Normalize list-like fields destined for Text columns by JSON-encoding them
        try:
            import json as _json
            if isinstance(update_data.get("allergens"), list):
                update_data["allergens"] = _json.dumps(update_data["allergens"])  # Text column
            if isinstance(update_data.get("quality_parameters"), list):
                update_data["quality_parameters"] = _json.dumps(update_data["quality_parameters"])  # Text column
        except Exception:
            pass
        for field, value in update_data.items():
            setattr(material, field, value)

        self.db.commit()
        self.db.refresh(material)
        return self._material_to_response_safe(material)

    def delete_material(self, material_id: int) -> bool:
        """Delete material"""
        material = self.get_material(material_id)
        if not material:
            return False

        self.db.delete(material)
        self.db.commit()
        return True

    def bulk_update_materials(self, action_data: BulkMaterialAction) -> Dict[str, Any]:
        """Bulk update materials"""
        materials = self.db.query(Material).filter(
            Material.id.in_(action_data.material_ids)
        ).all()

        updated_count = 0
        for material in materials:
            if action_data.action == "approve":
                material.approval_status = "approved"
            elif action_data.action == "reject":
                material.approval_status = "rejected"
            elif action_data.action == "activate":
                material.is_active = True
            elif action_data.action == "deactivate":
                material.is_active = False
            else:
                continue
            updated_count += 1

        self.db.commit()
        return {"updated_count": updated_count, "total_requested": len(action_data.material_ids)}

    # Evaluation operations
    def create_evaluation(self, evaluation_data: SupplierEvaluationCreate, evaluated_by: int) -> SupplierEvaluation:
        """Create a new supplier evaluation"""
        # Calculate overall score
        scores = []
        if evaluation_data.quality_score:
            scores.append(evaluation_data.quality_score)
        if evaluation_data.delivery_score:
            scores.append(evaluation_data.delivery_score)
        if evaluation_data.price_score:
            scores.append(evaluation_data.price_score)
        if evaluation_data.communication_score:
            scores.append(evaluation_data.communication_score)
        if evaluation_data.technical_support_score:
            scores.append(evaluation_data.technical_support_score)
        if evaluation_data.hygiene_score:
            scores.append(evaluation_data.hygiene_score)

        overall_score = sum(scores) / len(scores) if scores else 0.0

        evaluation = SupplierEvaluation(
            **evaluation_data.dict(),
            overall_score=overall_score,
            evaluated_by=evaluated_by
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        # Update supplier's overall score and evaluation dates
        supplier = self.get_supplier(evaluation.supplier_id)
        if supplier:
            supplier.overall_score = overall_score
            supplier.last_evaluation_date = evaluation.evaluation_date
            supplier.next_evaluation_date = evaluation.evaluation_date + timedelta(days=365)
            self.db.commit()

        return evaluation

    def get_evaluations(self, filter_params: EvaluationFilter) -> Dict[str, Any]:
        """Get evaluations with filtering and pagination"""
        query = self.db.query(SupplierEvaluation)

        # Apply filters
        if filter_params.supplier_id:
            query = query.filter(SupplierEvaluation.supplier_id == filter_params.supplier_id)

        if filter_params.status:
            query = query.filter(SupplierEvaluation.status == filter_params.status)

        if filter_params.date_from:
            query = query.filter(SupplierEvaluation.evaluation_date >= filter_params.date_from)

        if filter_params.date_to:
            query = query.filter(SupplierEvaluation.evaluation_date <= filter_params.date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        evaluations = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": evaluations,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_evaluation(self, evaluation_id: int) -> Optional[SupplierEvaluation]:
        """Get evaluation by ID"""
        return self.db.query(SupplierEvaluation).filter(SupplierEvaluation.id == evaluation_id).first()

    def update_evaluation(self, evaluation_id: int, evaluation_data: SupplierEvaluationUpdate) -> Optional[SupplierEvaluation]:
        """Update evaluation"""
        evaluation = self.get_evaluation(evaluation_id)
        if not evaluation:
            return None

        update_data = evaluation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(evaluation, field, value)

        # Recalculate overall score if scores changed
        if any(field in update_data for field in ['quality_score', 'delivery_score', 'price_score', 'communication_score', 'technical_support_score', 'hygiene_score']):
            scores = []
            if evaluation.quality_score:
                scores.append(evaluation.quality_score)
            if evaluation.delivery_score:
                scores.append(evaluation.delivery_score)
            if evaluation.price_score:
                scores.append(evaluation.price_score)
            if evaluation.communication_score:
                scores.append(evaluation.communication_score)
            if evaluation.technical_support_score:
                scores.append(evaluation.technical_support_score)
            if evaluation.hygiene_score:
                scores.append(evaluation.hygiene_score)

            evaluation.overall_score = sum(scores) / len(scores) if scores else 0.0

        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def delete_evaluation(self, evaluation_id: int) -> bool:
        """Delete evaluation"""
        evaluation = self.db.query(SupplierEvaluation).filter(SupplierEvaluation.id == evaluation_id).first()
        if not evaluation:
            return False
        self.db.delete(evaluation)
        self.db.commit()
        return True

    # Inspection Checklist operations
    def create_inspection_checklist(self, checklist_data: InspectionChecklistCreate, created_by: int) -> InspectionChecklist:
        """Create a new inspection checklist"""
        checklist = InspectionChecklist(
            **checklist_data.dict(),
            created_by=created_by
        )
        self.db.add(checklist)
        self.db.commit()
        self.db.refresh(checklist)
        return checklist

    def get_inspection_checklists(self, delivery_id: int) -> List[InspectionChecklist]:
        """Get inspection checklists for a delivery"""
        return self.db.query(InspectionChecklist).filter(
            InspectionChecklist.delivery_id == delivery_id
        ).all()

    def get_inspection_checklist(self, checklist_id: int) -> Optional[InspectionChecklist]:
        """Get inspection checklist by ID"""
        return self.db.query(InspectionChecklist).filter(
            InspectionChecklist.id == checklist_id
        ).first()

    def update_inspection_checklist(self, checklist_id: int, checklist_data: InspectionChecklistUpdate) -> Optional[InspectionChecklist]:
        """Update inspection checklist"""
        checklist = self.get_inspection_checklist(checklist_id)
        if not checklist:
            return None

        update_data = checklist_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(checklist, field, value)

        self.db.commit()
        self.db.refresh(checklist)
        return checklist

    def delete_inspection_checklist(self, checklist_id: int) -> bool:
        """Delete inspection checklist"""
        checklist = self.get_inspection_checklist(checklist_id)
        if not checklist:
            return False

        self.db.delete(checklist)
        self.db.commit()
        return True

    def create_checklist_item(self, item_data: InspectionChecklistItemCreate) -> InspectionChecklistItem:
        """Create a new checklist item"""
        item = InspectionChecklistItem(**item_data.dict())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_checklist_items(self, checklist_id: int) -> List[InspectionChecklistItem]:
        """Get checklist items for a checklist"""
        return self.db.query(InspectionChecklistItem).filter(
            InspectionChecklistItem.checklist_id == checklist_id
        ).all()

    def update_checklist_item(self, item_id: int, item_data: InspectionChecklistItemUpdate, checked_by: int) -> Optional[InspectionChecklistItem]:
        """Update checklist item"""
        item = self.db.query(InspectionChecklistItem).filter(
            InspectionChecklistItem.id == item_id
        ).first()
        
        if not item:
            return None

        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        # Update checked status
        if 'is_checked' in update_data and update_data['is_checked']:
            item.checked_at = datetime.now()
            item.checked_by = checked_by

        self.db.commit()
        self.db.refresh(item)
        return item

    def complete_checklist(self, checklist_id: int, completed_by: int) -> Optional[InspectionChecklist]:
        """Complete an inspection checklist"""
        checklist = self.get_inspection_checklist(checklist_id)
        if not checklist:
            return None

        # Get all items
        items = self.get_checklist_items(checklist_id)
        total_items = len(items)
        passed_items = len([item for item in items if item.result == 'passed'])
        failed_items = len([item for item in items if item.result == 'failed'])

        # Determine overall result
        if failed_items == 0:
            overall_result = 'passed'
        elif passed_items == 0:
            overall_result = 'failed'
        else:
            overall_result = 'conditional'

        checklist.is_completed = True
        checklist.completed_by = completed_by
        checklist.completed_at = datetime.now()
        checklist.overall_result = overall_result
        checklist.total_items = total_items
        checklist.passed_items = passed_items
        checklist.failed_items = failed_items

        self.db.commit()
        self.db.refresh(checklist)
        return checklist

    # Noncompliant delivery alerts
    def get_noncompliant_delivery_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts for noncompliant deliveries"""
        noncompliant_deliveries = self.db.query(IncomingDelivery).filter(
            IncomingDelivery.inspection_status.in_(['failed', 'quarantined'])
        ).all()

        alerts = []
        for delivery in noncompliant_deliveries:
            days_since_delivery = (datetime.now() - delivery.delivery_date).days
            
            # Parse non-conformances
            non_conformances = []
            if delivery.non_conformances:
                try:
                    non_conformances = json.loads(delivery.non_conformances)
                except:
                    non_conformances = [delivery.non_conformances]

            alerts.append({
                "delivery_id": delivery.id,
                "delivery_number": delivery.delivery_number,
                "supplier_name": delivery.supplier.name,
                "material_name": delivery.material.name,
                "inspection_status": delivery.inspection_status,
                "non_conformances": non_conformances,
                "alert_date": delivery.inspection_date or delivery.created_at,
                "days_since_delivery": days_since_delivery
            })

        return alerts

    def get_delivery_alert_summary(self) -> Dict[str, Any]:
        """Get summary of delivery alerts"""
        alerts = self.get_noncompliant_delivery_alerts()
        
        critical_alerts = len([alert for alert in alerts if alert['days_since_delivery'] > 7])
        warning_alerts = len([alert for alert in alerts if alert['days_since_delivery'] <= 7])

        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts
        }

    # Delivery operations
    def create_delivery(self, delivery_data: IncomingDeliveryCreate, created_by: int) -> IncomingDelivery:
        """Create a new incoming delivery"""
        delivery = IncomingDelivery(
            **delivery_data.dict(),
            created_by=created_by
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def get_deliveries(self, filter_params: DeliveryFilter) -> Dict[str, Any]:
        """Get deliveries with filtering and pagination"""
        query = self.db.query(IncomingDelivery)

        # Apply filters
        if filter_params.supplier_id:
            query = query.filter(IncomingDelivery.supplier_id == filter_params.supplier_id)

        if filter_params.material_id:
            query = query.filter(IncomingDelivery.material_id == filter_params.material_id)

        if filter_params.inspection_status:
            query = query.filter(IncomingDelivery.inspection_status == filter_params.inspection_status)

        if filter_params.date_from:
            query = query.filter(IncomingDelivery.delivery_date >= filter_params.date_from)

        if filter_params.date_to:
            query = query.filter(IncomingDelivery.delivery_date <= filter_params.date_to)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        deliveries = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": deliveries,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_delivery(self, delivery_id: int) -> Optional[IncomingDelivery]:
        """Get delivery by ID"""
        return self.db.query(IncomingDelivery).filter(IncomingDelivery.id == delivery_id).first()

    def update_delivery(self, delivery_id: int, delivery_data: IncomingDeliveryUpdate) -> Optional[IncomingDelivery]:
        """Update delivery"""
        delivery = self.get_delivery(delivery_id)
        if not delivery:
            return None

        update_data = delivery_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(delivery, field, value)

        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def delete_delivery(self, delivery_id: int) -> bool:
        """Delete delivery"""
        delivery = self.get_delivery(delivery_id)
        if not delivery:
            return False

        self.db.delete(delivery)
        self.db.commit()
        return True

    # Document operations
    def create_document(self, document_data: SupplierDocumentCreate, created_by: int) -> SupplierDocument:
        """Create a new supplier document"""
        document = SupplierDocument(
            **document_data.dict(),
            created_by=created_by
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_documents(self, supplier_id: int) -> List[SupplierDocument]:
        """Get documents for a supplier"""
        return self.db.query(SupplierDocument).filter(
            SupplierDocument.supplier_id == supplier_id
        ).all()

    def get_document(self, document_id: int) -> Optional[SupplierDocument]:
        """Get document by ID"""
        return self.db.query(SupplierDocument).filter(SupplierDocument.id == document_id).first()

    def update_document(self, document_id: int, document_data: SupplierDocumentUpdate) -> Optional[SupplierDocument]:
        """Update document"""
        document = self.get_document(document_id)
        if not document:
            return None

        update_data = document_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        """Delete document"""
        document = self.get_document(document_id)
        if not document:
            return False

        self.db.delete(document)
        self.db.commit()
        return True

    # Dashboard operations
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get supplier dashboard statistics"""
        total_suppliers = self.db.query(Supplier).count()
        active_suppliers = self.db.query(Supplier).filter(Supplier.status == SupplierStatus.ACTIVE).count()
        
        # Overdue evaluations (next_evaluation_date < today)
        overdue_evaluations = self.db.query(Supplier).filter(
            and_(
                Supplier.next_evaluation_date < datetime.now(),
                Supplier.next_evaluation_date.isnot(None)
            )
        ).count()

        # Suppliers by category (normalize to strings)
        from sqlalchemy import cast, String
        suppliers_by_category_raw = self.db.query(
            cast(Supplier.category, String),
            func.count(Supplier.id).label('count')
        ).group_by(cast(Supplier.category, String)).all()

        # Suppliers by risk level
        suppliers_by_risk = self.db.query(
            Supplier.risk_level,
            func.count(Supplier.id).label('count')
        ).group_by(Supplier.risk_level).all()

        # Recent evaluations (last 30 days) — project columns and cast enums to String to avoid coercion errors
        from sqlalchemy import cast, String
        recent_evaluations_rows = (
            self.db.query(
                SupplierEvaluation.id.label("id"),
                Supplier.name.label("supplier_name"),
                SupplierEvaluation.evaluation_period.label("evaluation_period"),
                SupplierEvaluation.overall_score.label("overall_score"),
                SupplierEvaluation.evaluation_date.label("evaluation_date"),
                cast(SupplierEvaluation.status, String).label("status"),
            )
            .join(Supplier, Supplier.id == SupplierEvaluation.supplier_id, isouter=True)
            .filter(SupplierEvaluation.evaluation_date >= datetime.now() - timedelta(days=30))
            .order_by(SupplierEvaluation.evaluation_date.desc())
            .limit(5)
            .all()
        )

        # Recent deliveries (last 30 days) — select columns via joins to avoid loading Supplier/Material ORM rows (and enum coercion)
        recent_deliveries_rows = (
            self.db.query(
                IncomingDelivery.id.label("id"),
                Supplier.name.label("supplier_name"),
                Material.name.label("material_name"),
                IncomingDelivery.quantity_received.label("quantity_received"),
                IncomingDelivery.inspection_status.label("inspection_status"),
                IncomingDelivery.delivery_date.label("delivery_date"),
            )
            .join(Supplier, Supplier.id == IncomingDelivery.supplier_id, isouter=True)
            .join(Material, Material.id == IncomingDelivery.material_id, isouter=True)
            .filter(IncomingDelivery.delivery_date >= datetime.now() - timedelta(days=30))
            .order_by(desc(IncomingDelivery.delivery_date))
            .limit(5)
            .all()
        )

        # Average score
        avg_score = self.db.query(func.avg(Supplier.overall_score)).scalar() or 0.0

        # High risk suppliers
        high_risk_suppliers = self.db.query(Supplier).filter(Supplier.risk_level == "high").count()

        return {
            "total_suppliers": total_suppliers,
            "active_suppliers": active_suppliers,
            "overdue_evaluations": overdue_evaluations,
            "suppliers_by_category": [
                {
                    "category": str(item[0] or "unknown").lower(),
                    "count": int(item[1] or 0),
                }
                for item in suppliers_by_category_raw
            ],
            "suppliers_by_risk": [
                {"risk_level": item.risk_level, "count": item.count} 
                for item in suppliers_by_risk
            ],
            "recent_evaluations": [
                {
                    "id": row.id,
                    "supplier_name": row.supplier_name,
                    "period": row.evaluation_period,
                    "score": float(row.overall_score or 0.0),
                    "date": row.evaluation_date,
                    "status": (row.status or "").lower(),
                }
                for row in recent_evaluations_rows
            ],
            "recent_deliveries": [
                {
                    "id": row.id,
                    "supplier_name": row.supplier_name,
                    "material_name": row.material_name,
                    "quantity": row.quantity_received,
                    "status": row.inspection_status,
                    "date": row.delivery_date,
                }
                for row in recent_deliveries_rows
            ],
            "average_score": float(avg_score),
            "high_risk_suppliers": high_risk_suppliers
        }

    # Utility methods
    def check_expired_certificates(self) -> List[Dict[str, Any]]:
        """Check for expired supplier certificates"""
        expired_docs = self.db.query(SupplierDocument).filter(
            and_(
                SupplierDocument.expiry_date < datetime.now(),
                SupplierDocument.is_valid == True
            )
        ).all()

        return [
            {
                "document_id": doc.id,
                "supplier_id": doc.supplier_id,
                "supplier_name": doc.supplier.name,
                "document_name": doc.document_name,
                "expiry_date": doc.expiry_date
            }
            for doc in expired_docs
        ]

    def get_overdue_evaluations(self) -> List[Dict[str, Any]]:
        """Get suppliers with overdue evaluations"""
        overdue_suppliers = self.db.query(Supplier).filter(
            and_(
                Supplier.next_evaluation_date < datetime.now(),
                Supplier.next_evaluation_date.isnot(None)
            )
        ).all()

        return [
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "next_evaluation_date": supplier.next_evaluation_date,
                "days_overdue": (datetime.now() - supplier.next_evaluation_date).days
            }
            for supplier in overdue_suppliers
        ] 

    # Material approval utilities
    def approve_material(self, material_id: int, approved_by: int) -> Optional[Material]:
        """Approve a material and return updated record."""
        import json as _json
        
        # Get material directly from database without conversion
        material = self.db.query(Material).filter(Material.id == material_id).first()
        if not material:
            return None
        
        # Ensure list fields are JSON strings before saving
        if hasattr(material, 'allergens') and isinstance(material.allergens, list):
            material.allergens = _json.dumps(material.allergens) if material.allergens else None
        if hasattr(material, 'quality_parameters') and isinstance(material.quality_parameters, list):
            material.quality_parameters = _json.dumps(material.quality_parameters) if material.quality_parameters else None
        
        material.approval_status = "approved"
        # Touch updated_at via commit; optionally track approver via specifications meta
        self.db.commit()
        self.db.refresh(material)
        return material

    def reject_material(self, material_id: int, reason: str, rejected_by: int) -> Optional[Material]:
        """Reject a material with reason and return updated record."""
        import json as _json
        
        # Get material directly from database without conversion
        material = self.db.query(Material).filter(Material.id == material_id).first()
        if not material:
            return None
        
        # Ensure list fields are JSON strings before saving
        if hasattr(material, 'allergens') and isinstance(material.allergens, list):
            material.allergens = _json.dumps(material.allergens) if material.allergens else None
        if hasattr(material, 'quality_parameters') and isinstance(material.quality_parameters, list):
            material.quality_parameters = _json.dumps(material.quality_parameters) if material.quality_parameters else None
        
        material.approval_status = "rejected"
        # Persist reason into acceptable_limits metadata if possible
        try:
            limits = material.acceptable_limits or {}
            if isinstance(limits, dict):
                limits["rejection_reason"] = reason
                material.acceptable_limits = limits
        except Exception:
            pass
        self.db.commit()
        self.db.refresh(material)
        return material

    def bulk_approve_materials(self, material_ids: List[int], approved_by: int) -> Dict[str, Any]:
        """Bulk approve materials; returns results dictionary."""
        q = self.db.query(Material).filter(Material.id.in_(material_ids))
        count = 0
        for m in q.all():
            m.approval_status = "approved"
            m.approved_by = approved_by
            m.approved_at = datetime.utcnow()
            count += 1
        self.db.commit()
        return {
            "approved_count": count,
            "total_requested": len(material_ids),
            "success_rate": f"{(count/len(material_ids)*100):.1f}%" if material_ids else "0%"
        }

    def bulk_reject_materials(self, material_ids: List[int], reason: str, rejected_by: int) -> Dict[str, Any]:
        """Bulk reject materials; returns results dictionary."""
        q = self.db.query(Material).filter(Material.id.in_(material_ids))
        count = 0
        for m in q.all():
            m.approval_status = "rejected"
            try:
                limits = m.acceptable_limits or {}
                if isinstance(limits, dict):
                    limits["rejection_reason"] = reason
                    m.acceptable_limits = limits
            except Exception:
                pass
            count += 1
        self.db.commit()
        return {
            "rejected_count": count,
            "total_requested": len(material_ids),
            "rejection_reason": reason,
            "success_rate": f"{(count/len(material_ids)*100):.1f}%" if material_ids else "0%"
        }

    # Lightweight normalization helpers for Material list-like fields stored as Text/JSON
    def _ensure_list(self, value: Any) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                import json as _json
                parsed = _json.loads(value)
                if isinstance(parsed, list):
                    return parsed
                return [value]
            except Exception:
                return [value]
        return [str(value)]

    def _material_to_response_safe(self, material: Material) -> Material:
        """Normalize list-like fields to avoid Pydantic validation errors."""
        try:
            material.allergens = self._ensure_list(material.allergens)  # type: ignore
        except Exception:
            pass
        try:
            material.quality_parameters = self._ensure_list(material.quality_parameters)  # type: ignore
        except Exception:
            pass
        return material 
    def get_material_stats(self) -> Dict[str, Any]:
        """Get material statistics"""
        from sqlalchemy import func
        
        total = self.db.query(Material).count()
        approved = self.db.query(Material).filter(Material.approval_status == "approved").count()
        pending = self.db.query(Material).filter(Material.approval_status == "pending").count()
        rejected = self.db.query(Material).filter(Material.approval_status == "rejected").count()
        
        # Get materials by category
        by_category = self.db.query(Material.category, func.count(Material.id)).group_by(Material.category).all()
        
        # Get materials by supplier
        by_supplier = (self.db.query(Supplier.name, func.count(Material.id))
                      .join(Supplier, Supplier.id == Material.supplier_id)
                      .group_by(Supplier.name)
                      .all())
        
        return {
            "total_materials": total,
            "approved_materials": approved,
            "pending_materials": pending,
            "rejected_materials": rejected,
            "materials_by_category": [
                {"category": str(cat or "unknown"), "count": int(cnt)} 
                for cat, cnt in by_category
            ],
            "materials_by_supplier": [
                {"supplier_name": name, "count": int(cnt)} 
                for name, cnt in by_supplier
            ]
        }

    def search_materials(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search materials by name, code, or description"""
        from sqlalchemy import or_
        
        search_term = f"%{query}%"
        
        materials = (self.db.query(Material)
                    .filter(or_(
                        Material.name.ilike(search_term),
                        Material.material_code.ilike(search_term),
                        Material.description.ilike(search_term)
                    ))
                    .limit(limit)
                    .all())
        
        results = []
        for material in materials:
            supplier = self.db.query(Supplier).filter(Supplier.id == material.supplier_id).first()
            results.append({
                "id": material.id,
                "material_code": material.material_code,
                "name": material.name,
                "description": material.description,
                "category": material.category,
                "approval_status": material.approval_status,
                "supplier_name": supplier.name if supplier else "Unknown"
            })
        
        return results

