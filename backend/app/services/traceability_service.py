import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid
import qrcode
from io import BytesIO
import base64

from app.models.traceability import (
    Batch, TraceabilityLink, Recall, RecallEntry, RecallAction, TraceabilityReport,
    BatchType, BatchStatus, RecallStatus, RecallType
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.schemas.traceability import (
    BatchCreate, BatchUpdate, RecallCreate, RecallUpdate, TraceabilityLinkCreate,
    RecallEntryCreate, RecallActionCreate, TraceabilityReportCreate,
    BatchFilter, RecallFilter, TraceabilityReportRequest
)

logger = logging.getLogger(__name__)


class TraceabilityService:
    """
    Service for handling traceability business logic
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = "uploads/traceability"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def create_batch(self, batch_data: BatchCreate, created_by: int) -> Batch:
        """Create a new batch with enhanced barcode generation"""
        
        # Generate unique batch number
        batch_number = f"BATCH-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Generate enhanced barcode with more information
        barcode_data = {
            "batch_number": batch_number,
            "batch_type": batch_data.batch_type.value,
            "product_name": batch_data.product_name,
            "production_date": batch_data.production_date.isoformat(),
            "quantity": batch_data.quantity,
            "unit": batch_data.unit
        }
        
        barcode = self._generate_enhanced_barcode(barcode_data)
        qr_code_path = self._generate_qr_code(barcode_data, batch_number)
        
        batch = Batch(
            batch_number=batch_number,
            batch_type=batch_data.batch_type,
            status=BatchStatus.IN_PRODUCTION,
            product_name=batch_data.product_name,
            quantity=batch_data.quantity,
            unit=batch_data.unit,
            production_date=batch_data.production_date,
            expiry_date=batch_data.expiry_date,
            lot_number=batch_data.lot_number,
            supplier_id=batch_data.supplier_id,
            supplier_batch_number=batch_data.supplier_batch_number,
            coa_number=batch_data.coa_number,
            storage_location=batch_data.storage_location,
            storage_conditions=batch_data.storage_conditions,
            barcode=barcode,
            qr_code_path=qr_code_path,
            created_by=created_by
        )
        
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        
        return batch
    
    def _generate_enhanced_barcode(self, barcode_data: Dict[str, Any]) -> str:
        """Generate enhanced barcode with batch information"""
        # Create a structured barcode with batch information
        barcode_string = f"BC-{barcode_data['batch_number']}-{barcode_data['batch_type'][:3].upper()}-{barcode_data['quantity']}{barcode_data['unit'][:2]}"
        return barcode_string
    
    def _generate_qr_code(self, qr_data: Dict[str, Any], batch_number: str) -> str:
        """Generate QR code for batch"""
        try:
            # Create QR code with JSON data
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to file
            filename = f"qr_code_{batch_number}.png"
            file_path = os.path.join(self.upload_dir, filename)
            img.save(file_path)
            
            return file_path
        except Exception as e:
            logger.error(f"Failed to generate QR code: {str(e)}")
            return None
    
    def generate_barcode_print_data(self, batch_id: int) -> Dict[str, Any]:
        """Generate barcode print data for a batch"""
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Generate print-ready barcode data
        print_data = {
            "batch_number": batch.batch_number,
            "barcode": batch.barcode,
            "product_name": batch.product_name,
            "batch_type": batch.batch_type.value,
            "production_date": batch.production_date.strftime("%Y-%m-%d"),
            "quantity": batch.quantity,
            "unit": batch.unit,
            "lot_number": batch.lot_number,
            "qr_code_path": batch.qr_code_path,
            "print_timestamp": datetime.utcnow().isoformat()
        }
        
        return print_data
    
    def search_batches_enhanced(self, search_criteria: Dict[str, Any]) -> List[Batch]:
        """Enhanced search by batch ID, date, or product"""
        query = self.db.query(Batch)
        
        # Search by batch ID
        if search_criteria.get("batch_id"):
            query = query.filter(Batch.id == search_criteria["batch_id"])
        
        # Search by batch number
        if search_criteria.get("batch_number"):
            query = query.filter(Batch.batch_number.ilike(f"%{search_criteria['batch_number']}%"))
        
        # Search by product name
        if search_criteria.get("product_name"):
            query = query.filter(Batch.product_name.ilike(f"%{search_criteria['product_name']}%"))
        
        # Search by date range
        if search_criteria.get("date_from"):
            query = query.filter(Batch.production_date >= search_criteria["date_from"])
        if search_criteria.get("date_to"):
            query = query.filter(Batch.production_date <= search_criteria["date_to"])
        
        # Search by batch type
        if search_criteria.get("batch_type"):
            query = query.filter(Batch.batch_type == search_criteria["batch_type"])
        
        # Search by status
        if search_criteria.get("status"):
            query = query.filter(Batch.status == search_criteria["status"])
        
        # Search by lot number
        if search_criteria.get("lot_number"):
            query = query.filter(Batch.lot_number.ilike(f"%{search_criteria['lot_number']}%"))
        
        # Search by supplier
        if search_criteria.get("supplier_id"):
            query = query.filter(Batch.supplier_id == search_criteria["supplier_id"])
        
        return query.order_by(desc(Batch.created_at)).all()
    
    def simulate_recall(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a product recall"""
        try:
            # Find affected batches based on simulation criteria
            affected_batches = self._find_affected_batches(simulation_data)
            
            # Generate simulation report
            simulation_report = {
                "simulation_id": f"SIM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                "simulation_date": datetime.utcnow().isoformat(),
                "simulation_criteria": simulation_data,
                "affected_batches": affected_batches,
                "total_quantity_affected": sum(batch.quantity for batch in affected_batches),
                "trace_analysis": self._perform_simulation_trace_analysis(affected_batches),
                "risk_assessment": self._assess_recall_risk(affected_batches, simulation_data),
                "recommended_actions": self._generate_simulation_recommendations(affected_batches, simulation_data)
            }
            
            return simulation_report
            
        except Exception as e:
            logger.error(f"Failed to simulate recall: {str(e)}")
            raise ValueError(f"Recall simulation failed: {str(e)}")
    
    def _find_affected_batches(self, simulation_data: Dict[str, Any]) -> List[Batch]:
        """Find batches affected by recall simulation"""
        query = self.db.query(Batch)
        
        # Apply simulation filters
        if simulation_data.get("batch_id"):
            query = query.filter(Batch.id == simulation_data["batch_id"])
        
        if simulation_data.get("product_name"):
            query = query.filter(Batch.product_name.ilike(f"%{simulation_data['product_name']}%"))
        
        if simulation_data.get("date_from"):
            query = query.filter(Batch.production_date >= simulation_data["date_from"])
        
        if simulation_data.get("date_to"):
            query = query.filter(Batch.production_date <= simulation_data["date_to"])
        
        if simulation_data.get("batch_type"):
            query = query.filter(Batch.batch_type == simulation_data["batch_type"])
        
        return query.all()
    
    def _perform_simulation_trace_analysis(self, affected_batches: List[Batch]) -> Dict[str, Any]:
        """Perform trace analysis for simulation"""
        trace_analysis = {
            "backward_trace": {},
            "forward_trace": {},
            "total_related_batches": 0
        }
        
        all_related_batches = set()
        
        for batch in affected_batches:
            # Backward trace (ingredients)
            backward_batches = self._trace_backward(batch.id, 5)
            trace_analysis["backward_trace"][batch.id] = backward_batches
            all_related_batches.update(backward_batches)
            
            # Forward trace (distribution)
            forward_batches = self._trace_forward(batch.id, 5)
            trace_analysis["forward_trace"][batch.id] = forward_batches
            all_related_batches.update(forward_batches)
        
        trace_analysis["total_related_batches"] = len(all_related_batches)
        
        return trace_analysis
    
    def _assess_recall_risk(self, affected_batches: List[Batch], simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess recall risk based on affected batches"""
        risk_assessment = {
            "risk_level": "low",
            "risk_score": 0,
            "factors": []
        }
        
        total_quantity = sum(batch.quantity for batch in affected_batches)
        batch_types = [batch.batch_type for batch in affected_batches]
        
        # Calculate risk score
        risk_score = 0
        
        # Factor 1: Quantity affected
        if total_quantity > 1000:
            risk_score += 30
            risk_assessment["factors"].append("High quantity affected")
        elif total_quantity > 500:
            risk_score += 20
            risk_assessment["factors"].append("Medium quantity affected")
        else:
            risk_score += 10
            risk_assessment["factors"].append("Low quantity affected")
        
        # Factor 2: Batch types affected
        if BatchType.FINAL_PRODUCT in batch_types:
            risk_score += 25
            risk_assessment["factors"].append("Final products affected")
        
        if BatchType.RAW_MILK in batch_types:
            risk_score += 20
            risk_assessment["factors"].append("Raw materials affected")
        
        # Factor 3: Distribution status
        distributed_batches = [b for b in affected_batches if b.status in [BatchStatus.RELEASED, BatchStatus.COMPLETED]]
        if distributed_batches:
            risk_score += 25
            risk_assessment["factors"].append("Products already in distribution")
        
        # Determine risk level
        if risk_score >= 70:
            risk_assessment["risk_level"] = "critical"
        elif risk_score >= 50:
            risk_assessment["risk_level"] = "high"
        elif risk_score >= 30:
            risk_assessment["risk_level"] = "medium"
        else:
            risk_assessment["risk_level"] = "low"
        
        risk_assessment["risk_score"] = risk_score
        
        return risk_assessment
    
    def _generate_simulation_recommendations(self, affected_batches: List[Batch], simulation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for recall simulation"""
        recommendations = []
        
        # Recommendation 1: Immediate actions
        recommendations.append({
            "priority": "high",
            "action": "Immediate quarantine of affected batches",
            "description": "Quarantine all affected batches to prevent further distribution",
            "assigned_to": "Quality Manager",
            "due_date": datetime.utcnow() + timedelta(hours=1)
        })
        
        # Recommendation 2: Investigation
        recommendations.append({
            "priority": "high",
            "action": "Root cause investigation",
            "description": "Investigate the root cause of the issue",
            "assigned_to": "Quality Assurance",
            "due_date": datetime.utcnow() + timedelta(days=1)
        })
        
        # Recommendation 3: Customer notification
        if any(batch.status in [BatchStatus.RELEASED, BatchStatus.COMPLETED] for batch in affected_batches):
            recommendations.append({
                "priority": "high",
                "action": "Customer notification",
                "description": "Notify customers about potential affected products",
                "assigned_to": "Customer Service",
                "due_date": datetime.utcnow() + timedelta(hours=4)
            })
        
        # Recommendation 4: Regulatory notification
        if simulation_data.get("regulatory_notification_required", False):
            recommendations.append({
                "priority": "high",
                "action": "Regulatory notification",
                "description": "Notify regulatory authorities about the recall",
                "assigned_to": "Regulatory Affairs",
                "due_date": datetime.utcnow() + timedelta(hours=2)
            })
        
        return recommendations
    
    def generate_recall_report_with_corrective_action(self, recall_id: int) -> Dict[str, Any]:
        """Generate comprehensive recall report with corrective action form"""
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Get recall entries
        entries = self.db.query(RecallEntry).filter(RecallEntry.recall_id == recall_id).all()
        
        # Get recall actions
        actions = self.db.query(RecallAction).filter(RecallAction.recall_id == recall_id).all()
        
        # Perform trace analysis
        trace_analysis = self._perform_comprehensive_trace_analysis(entries)
        
        # Generate corrective action form
        corrective_action_form = self._generate_corrective_action_form(recall, entries, actions)
        
        # Compile comprehensive report
        report = {
            "recall_id": recall.id,
            "recall_number": recall.recall_number,
            "report_generated_at": datetime.utcnow().isoformat(),
            "recall_details": {
                "title": recall.title,
                "description": recall.description,
                "reason": recall.reason,
                "recall_type": recall.recall_type.value,
                "status": recall.status.value,
                "issue_discovered_date": recall.issue_discovered_date.isoformat(),
                "recall_initiated_date": recall.recall_initiated_date.isoformat() if recall.recall_initiated_date else None,
                "total_quantity_affected": recall.total_quantity_affected,
                "quantity_recalled": recall.quantity_recalled,
                "quantity_disposed": recall.quantity_disposed
            },
            "affected_batches": [
                {
                    "batch_id": entry.batch_id,
                    "batch_number": entry.batch.batch_number,
                    "product_name": entry.batch.product_name,
                    "quantity_affected": entry.quantity_affected,
                    "quantity_recalled": entry.quantity_recalled,
                    "quantity_disposed": entry.quantity_disposed,
                    "location": entry.location,
                    "customer": entry.customer,
                    "status": entry.status
                }
                for entry in entries
            ],
            "trace_analysis": trace_analysis,
            "corrective_action_form": corrective_action_form,
            "actions_taken": [
                {
                    "action_type": action.action_type,
                    "description": action.description,
                    "assigned_to": action.assigned_to,
                    "due_date": action.due_date.isoformat() if action.due_date else None,
                    "completed_date": action.completed_date.isoformat() if action.completed_date else None,
                    "status": action.status,
                    "results": action.results
                }
                for action in actions
            ],
            "regulatory_compliance": {
                "notification_required": recall.regulatory_notification_required,
                "notification_date": recall.regulatory_notification_date.isoformat() if recall.regulatory_notification_date else None,
                "regulatory_reference": recall.regulatory_reference
            }
        }
        
        return report
    
    def _perform_comprehensive_trace_analysis(self, entries: List[RecallEntry]) -> Dict[str, Any]:
        """Perform comprehensive trace analysis for recall report"""
        trace_analysis = {
            "backward_trace": {},
            "forward_trace": {},
            "total_ingredients_affected": 0,
            "total_products_affected": 0,
            "distribution_impact": {}
        }
        
        all_ingredients = set()
        all_products = set()
        
        for entry in entries:
            batch_id = entry.batch_id
            
            # Backward trace (ingredients)
            backward_batches = self._trace_backward(batch_id, 10)
            trace_analysis["backward_trace"][batch_id] = backward_batches
            all_ingredients.update(backward_batches)
            
            # Forward trace (products)
            forward_batches = self._trace_forward(batch_id, 10)
            trace_analysis["forward_trace"][batch_id] = forward_batches
            all_products.update(forward_batches)
        
        trace_analysis["total_ingredients_affected"] = len(all_ingredients)
        trace_analysis["total_products_affected"] = len(all_products)
        
        # Analyze distribution impact
        trace_analysis["distribution_impact"] = self._analyze_distribution_impact(entries)
        
        return trace_analysis
    
    def _analyze_distribution_impact(self, entries: List[RecallEntry]) -> Dict[str, Any]:
        """Analyze the distribution impact of the recall"""
        distribution_impact = {
            "customers_affected": set(),
            "locations_affected": set(),
            "total_distribution_value": 0,
            "geographic_spread": []
        }
        
        for entry in entries:
            if entry.customer:
                distribution_impact["customers_affected"].add(entry.customer)
            if entry.location:
                distribution_impact["locations_affected"].add(entry.location)
            
            # Calculate distribution value (simplified)
            distribution_impact["total_distribution_value"] += entry.quantity_affected * 10  # Assuming $10 per unit
        
        # Convert sets to lists for JSON serialization
        distribution_impact["customers_affected"] = list(distribution_impact["customers_affected"])
        distribution_impact["locations_affected"] = list(distribution_impact["locations_affected"])
        
        return distribution_impact
    
    def _generate_corrective_action_form(self, recall: Recall, entries: List[RecallEntry], actions: List[RecallAction]) -> Dict[str, Any]:
        """Generate comprehensive corrective action form"""
        corrective_action_form = {
            "form_id": f"CAF-{recall.recall_number}",
            "generated_date": datetime.utcnow().isoformat(),
            "recall_reference": recall.recall_number,
            "root_cause_analysis": {
                "immediate_cause": "",
                "underlying_cause": "",
                "systemic_cause": "",
                "analysis_date": "",
                "analyzed_by": ""
            },
            "corrective_actions": {
                "immediate_actions": [],
                "short_term_actions": [],
                "long_term_actions": []
            },
            "preventive_measures": {
                "process_improvements": [],
                "training_requirements": [],
                "system_updates": [],
                "monitoring_enhancements": []
            },
            "verification_plan": {
                "verification_methods": [],
                "verification_schedule": "",
                "responsible_person": "",
                "success_criteria": []
            },
            "effectiveness_review": {
                "review_date": "",
                "reviewed_by": "",
                "effectiveness_score": 0,
                "additional_actions_required": False
            }
        }
        
        # Populate with existing actions
        for action in actions:
            if action.action_type == "investigation":
                corrective_action_form["root_cause_analysis"]["analysis_date"] = action.completed_date.isoformat() if action.completed_date else ""
                corrective_action_form["root_cause_analysis"]["analyzed_by"] = action.assigned_to
        
        return corrective_action_form
    
    def update_batch(self, batch_id: int, batch_data: BatchUpdate, updated_by: int) -> Batch:
        """Update a batch"""
        
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Update fields
        if batch_data.batch_type is not None:
            batch.batch_type = batch_data.batch_type
        if batch_data.status is not None:
            batch.status = batch_data.status
        if batch_data.product_name is not None:
            batch.product_name = batch_data.product_name
        if batch_data.quantity is not None:
            batch.quantity = batch_data.quantity
        if batch_data.unit is not None:
            batch.unit = batch_data.unit
        if batch_data.expiry_date is not None:
            batch.expiry_date = batch_data.expiry_date
        if batch_data.lot_number is not None:
            batch.lot_number = batch_data.lot_number
        if batch_data.quality_status is not None:
            batch.quality_status = batch_data.quality_status
        if batch_data.test_results is not None:
            batch.test_results = batch_data.test_results
        if batch_data.storage_location is not None:
            batch.storage_location = batch_data.storage_location
        if batch_data.storage_conditions is not None:
            batch.storage_conditions = batch_data.storage_conditions
        
        batch.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(batch)
        
        return batch
    
    def get_batches(self, filters: BatchFilter, skip: int = 0, limit: int = 100) -> Tuple[List[Batch], int]:
        """Get batches with filtering and pagination"""
        
        query = self.db.query(Batch)
        
        # Apply filters
        if filters.batch_type:
            query = query.filter(Batch.batch_type == filters.batch_type)
        if filters.status:
            query = query.filter(Batch.status == filters.status)
        if filters.product_name:
            query = query.filter(Batch.product_name.ilike(f"%{filters.product_name}%"))
        if filters.search:
            query = query.filter(
                (Batch.batch_number.ilike(f"%{filters.search}%")) |
                (Batch.product_name.ilike(f"%{filters.search}%")) |
                (Batch.lot_number.ilike(f"%{filters.search}%"))
            )
        if filters.date_from:
            query = query.filter(Batch.production_date >= filters.date_from)
        if filters.date_to:
            query = query.filter(Batch.production_date <= filters.date_to)
        
        total = query.count()
        batches = query.order_by(desc(Batch.created_at)).offset(skip).limit(limit).all()
        
        return batches, total
    
    def create_traceability_link(self, batch_id: int, link_data: TraceabilityLinkCreate, created_by: int) -> TraceabilityLink:
        """Create a traceability link between batches"""
        
        # Verify both batches exist
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        linked_batch = self.db.query(Batch).filter(Batch.id == link_data.linked_batch_id).first()
        
        if not batch or not linked_batch:
            raise ValueError("One or both batches not found")
        
        # Check if link already exists
        existing_link = self.db.query(TraceabilityLink).filter(
            and_(
                TraceabilityLink.batch_id == batch_id,
                TraceabilityLink.linked_batch_id == link_data.linked_batch_id
            )
        ).first()
        
        if existing_link:
            raise ValueError("Traceability link already exists")
        
        link = TraceabilityLink(
            batch_id=batch_id,
            linked_batch_id=link_data.linked_batch_id,
            relationship_type=link_data.relationship_type,
            quantity_used=link_data.quantity_used,
            unit=link_data.unit,
            usage_date=link_data.usage_date,
            process_step=link_data.process_step,
            created_by=created_by
        )
        
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        
        return link
    
    def get_traceability_chain(self, batch_id: int) -> Dict[str, Any]:
        """Get complete traceability chain for a batch"""
        
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Get incoming links (ingredients)
        incoming_links = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.linked_batch_id == batch_id
        ).all()
        
        # Get outgoing links (products)
        outgoing_links = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.batch_id == batch_id
        ).all()
        
        # Build trace path
        trace_path = self._build_trace_path(batch_id, incoming_links, outgoing_links)
        
        return {
            "starting_batch": batch,
            "incoming_links": incoming_links,
            "outgoing_links": outgoing_links,
            "trace_path": trace_path
        }
    
    def _build_trace_path(self, batch_id: int, incoming_links: List[TraceabilityLink], outgoing_links: List[TraceabilityLink]) -> Dict[str, Any]:
        """Build a visual trace path"""
        
        # Get all related batch IDs
        related_batch_ids = [batch_id]
        for link in incoming_links:
            related_batch_ids.append(link.batch_id)
        for link in outgoing_links:
            related_batch_ids.append(link.linked_batch_id)
        
        # Get all related batches
        batches = self.db.query(Batch).filter(Batch.id.in_(related_batch_ids)).all()
        batch_dict = {batch.id: batch for batch in batches}
        
        # Build path structure
        path = {
            "nodes": [
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "type": batch.batch_type.value,
                    "product_name": batch.product_name,
                    "status": batch.status.value,
                    "is_starting": batch.id == batch_id
                }
                for batch in batches
            ],
            "links": [
                {
                    "source": link.batch_id,
                    "target": link.linked_batch_id,
                    "relationship_type": link.relationship_type,
                    "quantity_used": link.quantity_used,
                    "unit": link.unit,
                    "process_step": link.process_step
                }
                for link in incoming_links + outgoing_links
            ]
        }
        
        return path
    
    def create_recall(self, recall_data: RecallCreate, created_by: int) -> Recall:
        """Create a new recall"""
        
        # Generate unique recall number
        recall_number = f"RECALL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        recall = Recall(
            recall_number=recall_number,
            recall_type=recall_data.recall_type,
            status=RecallStatus.DRAFT,
            title=recall_data.title,
            description=recall_data.description,
            reason=recall_data.reason,
            hazard_description=recall_data.hazard_description,
            affected_products=json.dumps(recall_data.affected_products) if recall_data.affected_products else None,
            affected_batches=json.dumps(recall_data.affected_batches) if recall_data.affected_batches else None,
            date_range_start=recall_data.date_range_start,
            date_range_end=recall_data.date_range_end,
            total_quantity_affected=recall_data.total_quantity_affected,
            quantity_in_distribution=recall_data.quantity_in_distribution,
            issue_discovered_date=recall_data.issue_discovered_date,
            regulatory_notification_required=recall_data.regulatory_notification_required,
            assigned_to=recall_data.assigned_to,
            created_by=created_by
        )
        
        self.db.add(recall)
        self.db.commit()
        self.db.refresh(recall)
        
        # Create notification for assigned user
        self._create_recall_notification(recall)
        
        return recall
    
    def _create_recall_notification(self, recall: Recall):
        """Create notification for recall assignment"""
        
        try:
            notification = Notification(
                user_id=recall.assigned_to,
                title=f"New Recall Assignment: {recall.title}",
                message=f"You have been assigned to handle recall {recall.recall_number}. "
                       f"Type: {recall.recall_type.value.replace('_', ' ').title()}. "
                       f"Please review and take appropriate action.",
                notification_type=NotificationType.WARNING,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "recall_id": recall.id,
                    "recall_number": recall.recall_number,
                    "recall_type": recall.recall_type.value,
                    "status": recall.status.value
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.info(f"Recall notification created for {recall.recall_number}")
            
        except Exception as e:
            logger.error(f"Failed to create recall notification: {str(e)}")
    
    def update_recall_status(self, recall_id: int, new_status: RecallStatus, updated_by: int) -> Recall:
        """Update recall status"""
        
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        recall.status = new_status
        
        # Update dates based on status
        if new_status == RecallStatus.INITIATED:
            recall.recall_initiated_date = datetime.utcnow()
        elif new_status == RecallStatus.COMPLETED:
            recall.recall_completed_date = datetime.utcnow()
        
        recall.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(recall)
        
        # Create status change notification
        self._create_status_change_notification(recall, new_status)
        
        return recall
    
    def _create_status_change_notification(self, recall: Recall, new_status: RecallStatus):
        """Create notification for recall status change"""
        
        try:
            notification = Notification(
                user_id=recall.assigned_to,
                title=f"Recall Status Updated: {recall.recall_number}",
                message=f"Recall {recall.recall_number} status has been updated to {new_status.value.replace('_', ' ').title()}.",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "recall_id": recall.id,
                    "recall_number": recall.recall_number,
                    "old_status": recall.status.value,
                    "new_status": new_status.value
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create status change notification: {str(e)}")
    
    def get_recalls(self, filters: RecallFilter, skip: int = 0, limit: int = 100) -> Tuple[List[Recall], int]:
        """Get recalls with filtering and pagination"""
        
        query = self.db.query(Recall)
        
        # Apply filters
        if filters.status:
            query = query.filter(Recall.status == filters.status)
        if filters.recall_type:
            query = query.filter(Recall.recall_type == filters.recall_type)
        if filters.search:
            query = query.filter(
                (Recall.recall_number.ilike(f"%{filters.search}%")) |
                (Recall.title.ilike(f"%{filters.search}%"))
            )
        if filters.date_from:
            query = query.filter(Recall.issue_discovered_date >= filters.date_from)
        if filters.date_to:
            query = query.filter(Recall.issue_discovered_date <= filters.date_to)
        
        total = query.count()
        recalls = query.order_by(desc(Recall.created_at)).offset(skip).limit(limit).all()
        
        return recalls, total
    
    def create_traceability_report(self, report_data: TraceabilityReportCreate, created_by: int) -> TraceabilityReport:
        """Create a traceability report"""
        
        # Verify starting batch exists
        starting_batch = self.db.query(Batch).filter(Batch.id == report_data.starting_batch_id).first()
        if not starting_batch:
            raise ValueError("Starting batch not found")
        
        # Generate report number
        report_number = f"TRACE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Perform traceability analysis
        traced_batches = []
        trace_path = {}
        
        if report_data.report_type in ["backward_trace", "full_trace"]:
            # Trace backward (ingredients)
            traced_batches.extend(self._trace_backward(report_data.starting_batch_id, report_data.trace_depth))
        
        if report_data.report_type in ["forward_trace", "full_trace"]:
            # Trace forward (products)
            traced_batches.extend(self._trace_forward(report_data.starting_batch_id, report_data.trace_depth))
        
        # Remove duplicates
        traced_batches = list(set(traced_batches))
        
        # Create trace path visualization
        trace_path = self._build_trace_path(report_data.starting_batch_id, [], [])
        
        # Generate summary
        trace_summary = f"Trace report for batch {starting_batch.batch_number}. Found {len(traced_batches)} related batches."
        
        report = TraceabilityReport(
            report_number=report_number,
            report_type=report_data.report_type.value,
            starting_batch_id=report_data.starting_batch_id,
            trace_date=datetime.utcnow(),
            trace_depth=report_data.trace_depth,
            traced_batches=json.dumps(traced_batches),
            trace_path=json.dumps(trace_path),
            trace_summary=trace_summary,
            created_by=created_by
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def _trace_backward(self, batch_id: int, depth: int) -> List[int]:
        """Trace backward to find ingredient batches"""
        traced = []
        to_trace = [batch_id]
        current_depth = 0
        
        while to_trace and current_depth < depth:
            next_level = []
            for bid in to_trace:
                links = self.db.query(TraceabilityLink).filter(TraceabilityLink.linked_batch_id == bid).all()
                for link in links:
                    if link.batch_id not in traced:
                        traced.append(link.batch_id)
                        next_level.append(link.batch_id)
            to_trace = next_level
            current_depth += 1
        
        return traced
    
    def _trace_forward(self, batch_id: int, depth: int) -> List[int]:
        """Trace forward to find product batches"""
        traced = []
        to_trace = [batch_id]
        current_depth = 0
        
        while to_trace and current_depth < depth:
            next_level = []
            for bid in to_trace:
                links = self.db.query(TraceabilityLink).filter(TraceabilityLink.batch_id == bid).all()
                for link in links:
                    if link.linked_batch_id not in traced:
                        traced.append(link.linked_batch_id)
                        next_level.append(link.linked_batch_id)
            to_trace = next_level
            current_depth += 1
        
        return traced
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get traceability dashboard statistics"""
        
        # Total batches by type
        batch_counts = {}
        for batch_type in BatchType:
            count = self.db.query(Batch).filter(Batch.batch_type == batch_type).count()
            batch_counts[batch_type.value] = count
        
        # Total batches by status
        status_counts = {}
        for status in BatchStatus:
            count = self.db.query(Batch).filter(Batch.status == status).count()
            status_counts[status.value] = count
        
        # Recent batches (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_batches = self.db.query(Batch).filter(Batch.created_at >= thirty_days_ago).count()
        
        # Active recalls
        active_recalls = self.db.query(Recall).filter(
            Recall.status.in_([RecallStatus.INITIATED, RecallStatus.IN_PROGRESS])
        ).count()
        
        # Recent traceability reports (last 30 days)
        recent_reports = self.db.query(TraceabilityReport).filter(
            TraceabilityReport.created_at >= thirty_days_ago
        ).count()
        
        # Quality status breakdown
        quality_counts = self.db.query(Batch.quality_status, func.count(Batch.id)).group_by(Batch.quality_status).all()
        quality_breakdown = {status: count for status, count in quality_counts}
        
        return {
            "batch_counts": batch_counts,
            "status_counts": status_counts,
            "recent_batches": recent_batches,
            "active_recalls": active_recalls,
            "recent_reports": recent_reports,
            "quality_breakdown": quality_breakdown
        }
    
    def create_recall_entry(self, recall_id: int, entry_data: RecallEntryCreate, created_by: int) -> RecallEntry:
        """Create a recall entry"""
        
        # Verify recall exists
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Verify batch exists
        batch = self.db.query(Batch).filter(Batch.id == entry_data.batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        entry = RecallEntry(
            recall_id=recall_id,
            batch_id=entry_data.batch_id,
            quantity_affected=entry_data.quantity_affected,
            quantity_recalled=entry_data.quantity_recalled or 0,
            quantity_disposed=entry_data.quantity_disposed or 0,
            location=entry_data.location,
            customer=entry_data.customer,
            created_by=created_by
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def create_recall_action(self, recall_id: int, action_data: RecallActionCreate, created_by: int) -> RecallAction:
        """Create a recall action"""
        
        # Verify recall exists
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        action = RecallAction(
            recall_id=recall_id,
            action_type=action_data.action_type,
            description=action_data.description,
            assigned_to=action_data.assigned_to,
            due_date=action_data.due_date,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        return action 