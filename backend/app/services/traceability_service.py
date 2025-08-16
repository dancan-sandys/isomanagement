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
    BatchType, BatchStatus, RecallStatus, RecallType, TraceabilityNode, RecallClassification,
    RecallCommunication, RecallEffectiveness
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
                       f"Type: {str(recall.recall_type).replace('_', ' ').title()}. "
                       f"Please review and take appropriate action.",
                notification_type=NotificationType.WARNING,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "recall_id": recall.id,
                    "recall_number": recall.recall_number,
                    "recall_type": str(recall.recall_type),
                    "status": str(recall.status)
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
                message=f"Recall {recall.recall_number} status has been updated to {str(new_status).replace('_', ' ').title()}.",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "recall_id": recall.id,
                    "recall_number": recall.recall_number,
                    "old_status": str(recall.status),
                    "new_status": str(new_status)
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
            # Handle enum filtering by comparing string values
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

    # ============================================================================
    # PHASE 1.2.1: ENHANCED TRACEABILITY SERVICE METHODS
    # ============================================================================

    def get_one_up_one_back_trace(self, batch_id: int, depth: int = 2) -> Dict[str, Any]:
        """
        Get one-up, one-back traceability for a batch (ISO 22005:2007 compliant)
        
        Args:
            batch_id: The batch ID to trace
            depth: Number of levels to trace (default 2 for one-up, one-back)
        
        Returns:
            Dictionary containing upstream and downstream trace information
        """
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Get upstream trace (suppliers/ingredients)
        upstream_trace = self._get_upstream_trace(batch_id, depth)
        
        # Get downstream trace (customers/products)
        downstream_trace = self._get_downstream_trace(batch_id, depth)
        
        # Calculate trace completeness
        trace_completeness = self._calculate_trace_completeness(batch_id)
        
        # Get verification status
        verification_status = self._get_verification_status(batch_id)
        
        return {
            "batch_id": batch_id,
            "batch_number": batch.batch_number,
            "product_name": batch.product_name,
            "batch_type": batch.batch_type.value,
            "upstream_trace": upstream_trace,
            "downstream_trace": downstream_trace,
            "trace_completeness": trace_completeness,
            "verification_status": verification_status,
            "trace_date": datetime.utcnow().isoformat(),
            "iso_compliant": True
        }

    def _get_upstream_trace(self, batch_id: int, depth: int) -> List[Dict[str, Any]]:
        """
        Get upstream trace (suppliers/ingredients) for a batch
        
        Args:
            batch_id: The batch ID to trace upstream
            depth: Number of levels to trace
        
        Returns:
            List of trace levels with batch information
        """
        trace_chain = []
        current_level = 1
        to_trace = [batch_id]
        traced_batches = set()
        
        while to_trace and current_level <= depth:
            level_batches = []
            
            for bid in to_trace:
                # Get incoming links (ingredients used in this batch)
                links = self.db.query(TraceabilityLink).filter(
                    TraceabilityLink.linked_batch_id == bid
                ).all()
                
                for link in links:
                    if link.batch_id not in traced_batches:
                        # Get batch details
                        batch = self.db.query(Batch).filter(Batch.id == link.batch_id).first()
                        if batch:
                            batch_info = {
                                "batch_id": batch.id,
                                "batch_number": batch.batch_number,
                                "product_name": batch.product_name,
                                "batch_type": batch.batch_type.value,
                                "quantity_used": link.quantity_used,
                                "unit": link.unit,
                                "relationship_type": link.relationship_type,
                                "process_step": link.process_step,
                                "supplier_id": batch.supplier_id,
                                "supplier_batch_number": batch.supplier_batch_number,
                                "gtin": batch.gtin,
                                "sscc": batch.sscc,
                                "hierarchical_lot_number": batch.hierarchical_lot_number,
                                "quality_status": batch.quality_status,
                                "production_date": batch.production_date.isoformat() if batch.production_date else None
                            }
                            level_batches.append(batch_info)
                            traced_batches.add(batch.id)
            
            if level_batches:
                trace_chain.append({
                    "level": current_level,
                    "level_description": f"Level {current_level} - {'Immediate suppliers' if current_level == 1 else f'{current_level}-up suppliers'}",
                    "batches": level_batches,
                    "batch_count": len(level_batches)
                })
                
                # Prepare next level
                to_trace = [batch["batch_id"] for batch in level_batches]
            else:
                break
                
            current_level += 1
        
        return trace_chain

    def _get_downstream_trace(self, batch_id: int, depth: int) -> List[Dict[str, Any]]:
        """
        Get downstream trace (customers/products) for a batch
        
        Args:
            batch_id: The batch ID to trace downstream
            depth: Number of levels to trace
        
        Returns:
            List of trace levels with batch information
        """
        trace_chain = []
        current_level = 1
        to_trace = [batch_id]
        traced_batches = set()
        
        while to_trace and current_level <= depth:
            level_batches = []
            
            for bid in to_trace:
                # Get outgoing links (products made from this batch)
                links = self.db.query(TraceabilityLink).filter(
                    TraceabilityLink.batch_id == bid
                ).all()
                
                for link in links:
                    if link.linked_batch_id not in traced_batches:
                        # Get batch details
                        batch = self.db.query(Batch).filter(Batch.id == link.linked_batch_id).first()
                        if batch:
                            batch_info = {
                                "batch_id": batch.id,
                                "batch_number": batch.batch_number,
                                "product_name": batch.product_name,
                                "batch_type": batch.batch_type.value,
                                "quantity_produced": link.quantity_used,
                                "unit": link.unit,
                                "relationship_type": link.relationship_type,
                                "process_step": link.process_step,
                                "gtin": batch.gtin,
                                "sscc": batch.sscc,
                                "hierarchical_lot_number": batch.hierarchical_lot_number,
                                "quality_status": batch.quality_status,
                                "status": batch.status.value,
                                "production_date": batch.production_date.isoformat() if batch.production_date else None,
                                "distribution_location": batch.distribution_location,
                                "customer_information": batch.customer_information
                            }
                            level_batches.append(batch_info)
                            traced_batches.add(batch.id)
            
            if level_batches:
                trace_chain.append({
                    "level": current_level,
                    "level_description": f"Level {current_level} - {'Immediate customers' if current_level == 1 else f'{current_level}-down customers'}",
                    "batches": level_batches,
                    "batch_count": len(level_batches)
                })
                
                # Prepare next level
                to_trace = [batch["batch_id"] for batch in level_batches]
            else:
                break
                
            current_level += 1
        
        return trace_chain

    def _calculate_trace_completeness(self, batch_id: int) -> float:
        """
        Calculate trace completeness percentage for a batch
        
        Args:
            batch_id: The batch ID to calculate completeness for
        
        Returns:
            Completeness percentage (0-100)
        """
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            return 0.0
        
        completeness_score = 0
        total_checks = 0
        
        # Check 1: Basic batch information
        total_checks += 1
        if batch.batch_number and batch.product_name and batch.production_date:
            completeness_score += 1
        
        # Check 2: GS1 identification
        total_checks += 1
        if batch.gtin or batch.sscc or batch.hierarchical_lot_number:
            completeness_score += 1
        
        # Check 3: Supplier information
        total_checks += 1
        if batch.supplier_id or batch.supplier_batch_number or batch.supplier_information:
            completeness_score += 1
        
        # Check 4: Quality information
        total_checks += 1
        if batch.quality_status and batch.quality_status != "pending":
            completeness_score += 1
        
        # Check 5: Traceability links
        total_checks += 1
        incoming_links = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.linked_batch_id == batch_id
        ).count()
        outgoing_links = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.batch_id == batch_id
        ).count()
        if incoming_links > 0 or outgoing_links > 0:
            completeness_score += 1
        
        # Check 6: Storage information
        total_checks += 1
        if batch.storage_location or batch.storage_conditions:
            completeness_score += 1
        
        # Check 7: Customer information (for final products)
        total_checks += 1
        if batch.batch_type == BatchType.FINAL_PRODUCT:
            if batch.customer_information or batch.distribution_location:
                completeness_score += 1
        else:
            completeness_score += 1  # Not applicable for non-final products
        
        return round((completeness_score / total_checks) * 100, 2)

    def _get_verification_status(self, batch_id: int) -> Dict[str, Any]:
        """
        Get verification status for a batch
        
        Args:
            batch_id: The batch ID to get verification status for
        
        Returns:
            Dictionary containing verification status information
        """
        # Get traceability nodes for this batch
        nodes = self.db.query(TraceabilityNode).filter(
            TraceabilityNode.batch_id == batch_id
        ).all()
        
        verification_status = {
            "overall_status": "pending",
            "verified_nodes": 0,
            "total_nodes": len(nodes),
            "verification_details": []
        }
        
        if not nodes:
            verification_status["overall_status"] = "not_required"
            return verification_status
        
        for node in nodes:
            node_status = {
                "node_id": node.id,
                "node_type": node.node_type,
                "node_level": node.node_level,
                "relationship_type": node.relationship_type,
                "verification_required": node.verification_required,
                "verification_status": node.verification_status,
                "verification_date": node.verification_date.isoformat() if node.verification_date else None,
                "verified_by": node.verified_by,
                "ccp_related": node.ccp_related,
                "ccp_id": node.ccp_id
            }
            verification_status["verification_details"].append(node_status)
            
            if node.verification_status == "verified":
                verification_status["verified_nodes"] += 1
        
        # Calculate overall status
        if verification_status["total_nodes"] > 0:
            verification_rate = verification_status["verified_nodes"] / verification_status["total_nodes"]
            if verification_rate == 1.0:
                verification_status["overall_status"] = "verified"
            elif verification_rate > 0.5:
                verification_status["overall_status"] = "partially_verified"
            else:
                verification_status["overall_status"] = "pending"
        
        return verification_status

    def create_traceability_node(self, node_data: Dict[str, Any], created_by: int) -> TraceabilityNode:
        """
        Create a traceability node for enhanced traceability tracking
        
        Args:
            node_data: Dictionary containing node information
            created_by: User ID creating the node
        
        Returns:
            Created TraceabilityNode instance
        """
        # Validate required fields
        required_fields = ["batch_id", "node_type", "node_level", "relationship_type"]
        for field in required_fields:
            if field not in node_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Verify batch exists
        batch = self.db.query(Batch).filter(Batch.id == node_data["batch_id"]).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Create traceability node
        node = TraceabilityNode(
            batch_id=node_data["batch_id"],
            node_type=node_data["node_type"],
            node_level=node_data["node_level"],
            relationship_type=node_data["relationship_type"],
            ccp_related=node_data.get("ccp_related", False),
            ccp_id=node_data.get("ccp_id"),
            verification_required=node_data.get("verification_required", True),
            verification_status=node_data.get("verification_status", "pending"),
            created_by=created_by
        )
        
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        
        # Create notification for verification if required
        if node.verification_required:
            self._create_verification_notification(node)
        
        return node

    def update_traceability_node(self, node_id: int, node_data: Dict[str, Any], updated_by: int) -> TraceabilityNode:
        """
        Update a traceability node
        
        Args:
            node_id: The node ID to update
            node_data: Dictionary containing updated node information
            updated_by: User ID updating the node
        
        Returns:
            Updated TraceabilityNode instance
        """
        node = self.db.query(TraceabilityNode).filter(TraceabilityNode.id == node_id).first()
        if not node:
            raise ValueError("Traceability node not found")
        
        # Update fields
        if "node_type" in node_data:
            node.node_type = node_data["node_type"]
        if "node_level" in node_data:
            node.node_level = node_data["node_level"]
        if "relationship_type" in node_data:
            node.relationship_type = node_data["relationship_type"]
        if "ccp_related" in node_data:
            node.ccp_related = node_data["ccp_related"]
        if "ccp_id" in node_data:
            node.ccp_id = node_data["ccp_id"]
        if "verification_required" in node_data:
            node.verification_required = node_data["verification_required"]
        if "verification_status" in node_data:
            node.verification_status = node_data["verification_status"]
            if node_data["verification_status"] == "verified":
                node.verification_date = datetime.utcnow()
                node.verified_by = updated_by
        
        node.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(node)
        
        return node

    def delete_traceability_node(self, node_id: int) -> bool:
        """
        Delete a traceability node
        
        Args:
            node_id: The node ID to delete
        
        Returns:
            True if deleted successfully
        """
        node = self.db.query(TraceabilityNode).filter(TraceabilityNode.id == node_id).first()
        if not node:
            raise ValueError("Traceability node not found")
        
        self.db.delete(node)
        self.db.commit()
        
        return True

    def _create_verification_notification(self, node: TraceabilityNode):
        """Create notification for traceability node verification"""
        try:
            notification = Notification(
                user_id=node.created_by,
                title=f"Traceability Node Verification Required",
                message=f"Traceability node for batch {node.batch_id} requires verification. "
                       f"Node type: {node.node_type}, Level: {node.node_level}",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "node_id": node.id,
                    "batch_id": node.batch_id,
                    "node_type": node.node_type,
                    "verification_required": node.verification_required
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create verification notification: {str(e)}")

    def get_ccp_traceability_alerts(self) -> List[Dict[str, Any]]:
        """
        Get CCP-related traceability alerts for HACCP compliance
        
        Returns:
            List of CCP-related traceability alerts
        """
        alerts = []
        
        # Find traceability nodes related to CCPs
        ccp_nodes = self.db.query(TraceabilityNode).filter(
            TraceabilityNode.ccp_related == True
        ).all()
        
        for node in ccp_nodes:
            # Check if verification is overdue
            if node.verification_required and node.verification_status == "pending":
                # Check if node is older than 7 days
                if node.created_at < datetime.utcnow() - timedelta(days=7):
                    alerts.append({
                        "alert_type": "ccp_verification_overdue",
                        "node_id": node.id,
                        "batch_id": node.batch_id,
                        "ccp_id": node.ccp_id,
                        "node_type": node.node_type,
                        "days_overdue": (datetime.utcnow() - node.created_at).days,
                        "priority": "high",
                        "message": f"CCP-related traceability node verification overdue for {node.days_overdue} days"
                    })
            
            # Check if CCP verification is required
            if node.ccp_id and node.verification_status != "verified":
                alerts.append({
                    "alert_type": "ccp_verification_required",
                    "node_id": node.id,
                    "batch_id": node.batch_id,
                    "ccp_id": node.ccp_id,
                    "node_type": node.node_type,
                    "priority": "medium",
                    "message": f"CCP verification required for traceability node {node.id}"
                })
        
        return alerts

    def generate_haccp_compliance_report(self) -> Dict[str, Any]:
        """
        Generate HACCP compliance report for traceability
        
        Returns:
            Dictionary containing HACCP compliance information
        """
        # Get all CCP-related traceability nodes
        ccp_nodes = self.db.query(TraceabilityNode).filter(
            TraceabilityNode.ccp_related == True
        ).all()
        
        # Calculate compliance metrics
        total_ccp_nodes = len(ccp_nodes)
        verified_ccp_nodes = len([node for node in ccp_nodes if node.verification_status == "verified"])
        pending_ccp_nodes = len([node for node in ccp_nodes if node.verification_status == "pending"])
        overdue_ccp_nodes = len([node for node in ccp_nodes 
                               if node.verification_status == "pending" and 
                               node.created_at < datetime.utcnow() - timedelta(days=7)])
        
        compliance_rate = (verified_ccp_nodes / total_ccp_nodes * 100) if total_ccp_nodes > 0 else 0
        
        # Get CCP distribution by type
        ccp_by_type = {}
        for node in ccp_nodes:
            node_type = node.node_type
            if node_type not in ccp_by_type:
                ccp_by_type[node_type] = {"total": 0, "verified": 0, "pending": 0}
            ccp_by_type[node_type]["total"] += 1
            if node.verification_status == "verified":
                ccp_by_type[node_type]["verified"] += 1
            else:
                ccp_by_type[node_type]["pending"] += 1
        
        return {
            "report_date": datetime.utcnow().isoformat(),
            "total_ccp_nodes": total_ccp_nodes,
            "verified_ccp_nodes": verified_ccp_nodes,
            "pending_ccp_nodes": pending_ccp_nodes,
            "overdue_ccp_nodes": overdue_ccp_nodes,
            "compliance_rate": round(compliance_rate, 2),
            "compliance_status": "compliant" if compliance_rate >= 95 else "non_compliant",
            "ccp_by_type": ccp_by_type,
            "alerts": self.get_ccp_traceability_alerts()
        }

    # ============================================================================
    # PHASE 1.2.2: ENHANCED RECALL SERVICE METHODS
    # ============================================================================

    def classify_recall(self, recall_id: int, classification_data: Dict[str, Any], classified_by: int) -> RecallClassification:
        """
        Classify a recall with health risk assessment (ISO 22000:2018 compliant)
        
        Args:
            recall_id: The recall ID to classify
            classification_data: Dictionary containing classification information
            classified_by: User ID performing the classification
        
        Returns:
            Created RecallClassification instance
        """
        # Verify recall exists
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Validate required fields
        required_fields = ["health_risk_level", "affected_population", "exposure_route"]
        for field in required_fields:
            if field not in classification_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(classification_data)
        
        # Create recall classification
        classification = RecallClassification(
            recall_id=recall_id,
            health_risk_level=classification_data["health_risk_level"],
            affected_population=classification_data["affected_population"],
            exposure_route=classification_data["exposure_route"],
            severity_assessment=classification_data.get("severity_assessment"),
            probability_assessment=classification_data.get("probability_assessment"),
            risk_score=risk_score,
            classification_date=datetime.utcnow(),
            classified_by=classified_by
        )
        
        self.db.add(classification)
        self.db.commit()
        self.db.refresh(classification)
        
        # Update recall type based on health risk level
        self._update_recall_type_based_on_classification(recall, classification_data["health_risk_level"])
        
        # Create notification for high-risk recalls
        if classification_data["health_risk_level"] in ["high", "critical"]:
            self._create_high_risk_recall_notification(recall, classification)
        
        return classification

    def _calculate_risk_score(self, classification_data: Dict[str, Any]) -> int:
        """
        Calculate risk score based on classification data
        
        Args:
            classification_data: Dictionary containing classification information
        
        Returns:
            Risk score (0-100)
        """
        risk_score = 0
        
        # Factor 1: Health risk level
        health_risk_scores = {
            "low": 10,
            "medium": 30,
            "high": 60,
            "critical": 90
        }
        risk_score += health_risk_scores.get(classification_data["health_risk_level"], 0)
        
        # Factor 2: Affected population
        affected_population = classification_data.get("affected_population", "")
        if "vulnerable" in affected_population.lower() or "children" in affected_population.lower():
            risk_score += 20
        elif "elderly" in affected_population.lower():
            risk_score += 15
        elif "general" in affected_population.lower():
            risk_score += 10
        
        # Factor 3: Exposure route
        exposure_route = classification_data.get("exposure_route", "")
        if "ingestion" in exposure_route.lower():
            risk_score += 15
        elif "contact" in exposure_route.lower():
            risk_score += 10
        elif "inhalation" in exposure_route.lower():
            risk_score += 20
        
        # Factor 4: Severity assessment
        severity_assessment = classification_data.get("severity_assessment", "")
        if "life-threatening" in severity_assessment.lower():
            risk_score += 25
        elif "serious" in severity_assessment.lower():
            risk_score += 15
        elif "moderate" in severity_assessment.lower():
            risk_score += 10
        
        # Factor 5: Probability assessment
        probability_assessment = classification_data.get("probability_assessment", "")
        if "high" in probability_assessment.lower():
            risk_score += 20
        elif "medium" in probability_assessment.lower():
            risk_score += 10
        elif "low" in probability_assessment.lower():
            risk_score += 5
        
        return min(risk_score, 100)  # Cap at 100

    def _update_recall_type_based_on_classification(self, recall: Recall, health_risk_level: str):
        """Update recall type based on health risk classification"""
        if health_risk_level == "critical":
            recall.recall_type = RecallType.CLASS_I
        elif health_risk_level == "high":
            recall.recall_type = RecallType.CLASS_I
        elif health_risk_level == "medium":
            recall.recall_type = RecallType.CLASS_II
        elif health_risk_level == "low":
            recall.recall_type = RecallType.CLASS_III
        
        self.db.commit()

    def _create_high_risk_recall_notification(self, recall: Recall, classification: RecallClassification):
        """Create notification for high-risk recalls"""
        try:
            notification = Notification(
                user_id=recall.assigned_to,
                title=f"High Risk Recall Classification: {recall.recall_number}",
                message=f"Recall {recall.recall_number} has been classified as {classification.health_risk_level} risk. "
                       f"Risk score: {classification.risk_score}. Immediate action required.",
                notification_type=NotificationType.WARNING,
                priority=NotificationPriority.CRITICAL,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "recall_id": recall.id,
                    "recall_number": recall.recall_number,
                    "health_risk_level": classification.health_risk_level,
                    "risk_score": classification.risk_score
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create high-risk recall notification: {str(e)}")

    def create_recall_communication(self, recall_id: int, communication_data: Dict[str, Any], sent_by: int) -> RecallCommunication:
        """
        Create recall communication for stakeholder notification
        
        Args:
            recall_id: The recall ID
            communication_data: Dictionary containing communication information
            sent_by: User ID sending the communication
        
        Returns:
            Created RecallCommunication instance
        """
        # Verify recall exists
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Validate required fields
        required_fields = ["stakeholder_type", "communication_method", "message_template"]
        for field in required_fields:
            if field not in communication_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create recall communication
        communication = RecallCommunication(
            recall_id=recall_id,
            stakeholder_type=communication_data["stakeholder_type"],
            communication_method=communication_data["communication_method"],
            message_template=communication_data["message_template"],
            sent_date=datetime.utcnow() if communication_data.get("sent", False) else None,
            sent_by=sent_by if communication_data.get("sent", False) else None,
            confirmation_received=communication_data.get("confirmation_received", False),
            response_time=communication_data.get("response_time")
        )
        
        self.db.add(communication)
        self.db.commit()
        self.db.refresh(communication)
        
        return communication

    def send_communication(self, communication_id: int, sent_by: int) -> RecallCommunication:
        """
        Mark a communication as sent and track sending
        
        Args:
            communication_id: The communication ID to send
            sent_by: User ID sending the communication
        
        Returns:
            Updated RecallCommunication instance
        """
        communication = self.db.query(RecallCommunication).filter(
            RecallCommunication.id == communication_id
        ).first()
        
        if not communication:
            raise ValueError("Communication not found")
        
        communication.sent_date = datetime.utcnow()
        communication.sent_by = sent_by
        
        self.db.commit()
        self.db.refresh(communication)
        
        # Create notification for communication sent
        self._create_communication_sent_notification(communication)
        
        return communication

    def _create_communication_sent_notification(self, communication: RecallCommunication):
        """Create notification for communication sent"""
        try:
            notification = Notification(
                user_id=communication.sent_by,
                title=f"Recall Communication Sent",
                message=f"Communication to {communication.stakeholder_type} has been sent for recall {communication.recall_id}",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.TRACEABILITY,
                notification_data={
                    "communication_id": communication.id,
                    "recall_id": communication.recall_id,
                    "stakeholder_type": communication.stakeholder_type,
                    "communication_method": communication.communication_method
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create communication sent notification: {str(e)}")

    def track_recall_effectiveness(self, recall_id: int, effectiveness_data: Dict[str, Any], verified_by: int) -> RecallEffectiveness:
        """
        Track recall effectiveness and calculate metrics
        
        Args:
            recall_id: The recall ID to track effectiveness for
            effectiveness_data: Dictionary containing effectiveness information
            verified_by: User ID verifying the effectiveness
        
        Returns:
            Created RecallEffectiveness instance
        """
        # Verify recall exists
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Validate required fields
        required_fields = ["quantity_recalled_percentage"]
        for field in required_fields:
            if field not in effectiveness_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Calculate effectiveness score
        effectiveness_score = self._calculate_effectiveness_score(effectiveness_data)
        
        # Create recall effectiveness record
        effectiveness = RecallEffectiveness(
            recall_id=recall_id,
            verification_date=datetime.utcnow(),
            quantity_recalled_percentage=effectiveness_data["quantity_recalled_percentage"],
            time_to_complete=effectiveness_data.get("time_to_complete"),
            customer_response_rate=effectiveness_data.get("customer_response_rate"),
            product_recovery_rate=effectiveness_data.get("product_recovery_rate"),
            effectiveness_score=effectiveness_score,
            lessons_learned=effectiveness_data.get("lessons_learned"),
            improvement_actions=effectiveness_data.get("improvement_actions"),
            verified_by=verified_by
        )
        
        self.db.add(effectiveness)
        self.db.commit()
        self.db.refresh(effectiveness)
        
        # Update recall status if effectiveness is tracked
        if effectiveness_score >= 90:
            recall.status = RecallStatus.COMPLETED
            recall.recall_completed_date = datetime.utcnow()
            self.db.commit()
        
        return effectiveness

    def _calculate_effectiveness_score(self, effectiveness_data: Dict[str, Any]) -> int:
        """
        Calculate effectiveness score based on effectiveness data
        
        Args:
            effectiveness_data: Dictionary containing effectiveness information
        
        Returns:
            Effectiveness score (0-100)
        """
        effectiveness_score = 0
        
        # Factor 1: Quantity recalled percentage (40% weight)
        quantity_recalled = effectiveness_data.get("quantity_recalled_percentage", 0)
        effectiveness_score += int(quantity_recalled * 0.4)
        
        # Factor 2: Time to complete (25% weight)
        time_to_complete = effectiveness_data.get("time_to_complete", 0)
        if time_to_complete:
            # Score based on time efficiency (lower time = higher score)
            if time_to_complete <= 24:  # Within 24 hours
                effectiveness_score += 25
            elif time_to_complete <= 48:  # Within 48 hours
                effectiveness_score += 20
            elif time_to_complete <= 72:  # Within 72 hours
                effectiveness_score += 15
            elif time_to_complete <= 168:  # Within 1 week
                effectiveness_score += 10
            else:
                effectiveness_score += 5
        
        # Factor 3: Customer response rate (20% weight)
        customer_response_rate = effectiveness_data.get("customer_response_rate", 0)
        effectiveness_score += int(customer_response_rate * 0.2)
        
        # Factor 4: Product recovery rate (15% weight)
        product_recovery_rate = effectiveness_data.get("product_recovery_rate", 0)
        effectiveness_score += int(product_recovery_rate * 0.15)
        
        return min(effectiveness_score, 100)  # Cap at 100

    def get_stakeholder_notification_matrix(self, recall_id: int) -> Dict[str, Any]:
        """
        Get stakeholder notification matrix for a recall
        
        Args:
            recall_id: The recall ID to get notification matrix for
        
        Returns:
            Dictionary containing stakeholder notification matrix
        """
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Get recall classification for risk level
        classification = self.db.query(RecallClassification).filter(
            RecallClassification.recall_id == recall_id
        ).first()
        
        risk_level = classification.health_risk_level if classification else "medium"
        
        # Define notification matrix based on risk level
        notification_matrix = {
            "critical": {
                "regulators": {
                    "method": "immediate_phone",
                    "timeframe": "within_1_hour",
                    "required": True,
                    "template": "critical_regulatory_notification"
                },
                "customers": {
                    "method": "multiple_channels",
                    "timeframe": "within_2_hours",
                    "required": True,
                    "template": "critical_customer_notification"
                },
                "suppliers": {
                    "method": "email_phone",
                    "timeframe": "within_4_hours",
                    "required": True,
                    "template": "critical_supplier_notification"
                },
                "public": {
                    "method": "press_release",
                    "timeframe": "within_6_hours",
                    "required": True,
                    "template": "critical_public_notification"
                }
            },
            "high": {
                "regulators": {
                    "method": "email_phone",
                    "timeframe": "within_4_hours",
                    "required": True,
                    "template": "high_regulatory_notification"
                },
                "customers": {
                    "method": "email_sms",
                    "timeframe": "within_6_hours",
                    "required": True,
                    "template": "high_customer_notification"
                },
                "suppliers": {
                    "method": "email",
                    "timeframe": "within_12_hours",
                    "required": True,
                    "template": "high_supplier_notification"
                },
                "public": {
                    "method": "website_social",
                    "timeframe": "within_24_hours",
                    "required": False,
                    "template": "high_public_notification"
                }
            },
            "medium": {
                "regulators": {
                    "method": "email",
                    "timeframe": "within_24_hours",
                    "required": False,
                    "template": "medium_regulatory_notification"
                },
                "customers": {
                    "method": "email",
                    "timeframe": "within_24_hours",
                    "required": True,
                    "template": "medium_customer_notification"
                },
                "suppliers": {
                    "method": "email",
                    "timeframe": "within_48_hours",
                    "required": False,
                    "template": "medium_supplier_notification"
                },
                "public": {
                    "method": "website",
                    "timeframe": "within_48_hours",
                    "required": False,
                    "template": "medium_public_notification"
                }
            },
            "low": {
                "regulators": {
                    "method": "email",
                    "timeframe": "within_72_hours",
                    "required": False,
                    "template": "low_regulatory_notification"
                },
                "customers": {
                    "method": "email",
                    "timeframe": "within_72_hours",
                    "required": False,
                    "template": "low_customer_notification"
                },
                "suppliers": {
                    "method": "email",
                    "timeframe": "within_72_hours",
                    "required": False,
                    "template": "low_supplier_notification"
                },
                "public": {
                    "method": "website",
                    "timeframe": "within_72_hours",
                    "required": False,
                    "template": "low_public_notification"
                }
            }
        }
        
        return {
            "recall_id": recall_id,
            "recall_number": recall.recall_number,
            "risk_level": risk_level,
            "notification_matrix": notification_matrix.get(risk_level, notification_matrix["medium"]),
            "generated_date": datetime.utcnow().isoformat()
        }

    def get_recall_effectiveness_report(self, recall_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive recall effectiveness report
        
        Args:
            recall_id: The recall ID to generate report for
        
        Returns:
            Dictionary containing effectiveness report
        """
        recall = self.db.query(Recall).filter(Recall.id == recall_id).first()
        if not recall:
            raise ValueError("Recall not found")
        
        # Get effectiveness records
        effectiveness_records = self.db.query(RecallEffectiveness).filter(
            RecallEffectiveness.recall_id == recall_id
        ).order_by(RecallEffectiveness.verification_date.desc()).all()
        
        # Get communication records
        communications = self.db.query(RecallCommunication).filter(
            RecallCommunication.recall_id == recall_id
        ).all()
        
        # Calculate effectiveness metrics
        latest_effectiveness = effectiveness_records[0] if effectiveness_records else None
        
        effectiveness_metrics = {
            "overall_score": latest_effectiveness.effectiveness_score if latest_effectiveness else 0,
            "quantity_recalled_percentage": latest_effectiveness.quantity_recalled_percentage if latest_effectiveness else 0,
            "time_to_complete": latest_effectiveness.time_to_complete if latest_effectiveness else None,
            "customer_response_rate": latest_effectiveness.customer_response_rate if latest_effectiveness else 0,
            "product_recovery_rate": latest_effectiveness.product_recovery_rate if latest_effectiveness else 0,
            "communication_effectiveness": self._calculate_communication_effectiveness(communications),
            "trend_analysis": self._analyze_effectiveness_trends(effectiveness_records)
        }
        
        return {
            "recall_id": recall_id,
            "recall_number": recall.recall_number,
            "report_date": datetime.utcnow().isoformat(),
            "effectiveness_metrics": effectiveness_metrics,
            "effectiveness_history": [
                {
                    "verification_date": record.verification_date.isoformat(),
                    "effectiveness_score": record.effectiveness_score,
                    "quantity_recalled_percentage": record.quantity_recalled_percentage,
                    "lessons_learned": record.lessons_learned,
                    "improvement_actions": record.improvement_actions
                }
                for record in effectiveness_records
            ],
            "communication_summary": {
                "total_communications": len(communications),
                "communications_by_stakeholder": self._group_communications_by_stakeholder(communications),
                "response_times": self._calculate_average_response_times(communications)
            }
        }

    def _calculate_communication_effectiveness(self, communications: List[RecallCommunication]) -> Dict[str, Any]:
        """Calculate communication effectiveness metrics"""
        if not communications:
            return {"score": 0, "details": "No communications found"}
        
        total_communications = len(communications)
        confirmed_communications = len([c for c in communications if c.confirmation_received])
        avg_response_time = sum([c.response_time or 0 for c in communications]) / total_communications
        
        return {
            "score": round((confirmed_communications / total_communications) * 100, 2),
            "total_communications": total_communications,
            "confirmed_communications": confirmed_communications,
            "confirmation_rate": round((confirmed_communications / total_communications) * 100, 2),
            "average_response_time": round(avg_response_time, 2) if avg_response_time > 0 else None
        }

    def _analyze_effectiveness_trends(self, effectiveness_records: List[RecallEffectiveness]) -> Dict[str, Any]:
        """Analyze effectiveness trends over time"""
        if len(effectiveness_records) < 2:
            return {"trend": "insufficient_data", "details": "Need at least 2 records for trend analysis"}
        
        scores = [record.effectiveness_score for record in effectiveness_records]
        first_score = scores[0]
        last_score = scores[-1]
        
        if last_score > first_score:
            trend = "improving"
            improvement = last_score - first_score
        elif last_score < first_score:
            trend = "declining"
            improvement = first_score - last_score
        else:
            trend = "stable"
            improvement = 0
        
        return {
            "trend": trend,
            "improvement": improvement,
            "first_score": first_score,
            "last_score": last_score,
            "average_score": round(sum(scores) / len(scores), 2)
        }

    def _group_communications_by_stakeholder(self, communications: List[RecallCommunication]) -> Dict[str, int]:
        """Group communications by stakeholder type"""
        stakeholder_counts = {}
        for comm in communications:
            stakeholder_type = comm.stakeholder_type
            stakeholder_counts[stakeholder_type] = stakeholder_counts.get(stakeholder_type, 0) + 1
        return stakeholder_counts

    def _calculate_average_response_times(self, communications: List[RecallCommunication]) -> Dict[str, float]:
        """Calculate average response times by stakeholder type"""
        response_times = {}
        stakeholder_times = {}
        
        for comm in communications:
            if comm.response_time:
                stakeholder_type = comm.stakeholder_type
                if stakeholder_type not in stakeholder_times:
                    stakeholder_times[stakeholder_type] = []
                stakeholder_times[stakeholder_type].append(comm.response_time)
        
        for stakeholder_type, times in stakeholder_times.items():
            response_times[stakeholder_type] = round(sum(times) / len(times), 2)
        
        return response_times

    # ============================================================================
    # PHASE 1.2.3: INTEGRATION SERVICES
    # ============================================================================
    
    def get_supplier_information(self, supplier_id: int) -> Dict[str, Any]:
        """Retrieve comprehensive supplier information for traceability"""
        try:
            # Get supplier details from database
            supplier = self.db.query(User).filter(User.id == supplier_id).first()
            if not supplier:
                raise ValueError(f"Supplier with ID {supplier_id} not found")
            
            # Get supplier's batches
            supplier_batches = self.db.query(Batch).filter(
                Batch.supplier_id == supplier_id
            ).all()
            
            # Get supplier's traceability nodes
            supplier_nodes = self.db.query(TraceabilityNode).join(Batch).filter(
                Batch.supplier_id == supplier_id
            ).all()
            
            # Calculate supplier performance metrics
            total_batches = len(supplier_batches)
            verified_nodes = len([n for n in supplier_nodes if n.verification_status == "verified"])
            verification_rate = (verified_nodes / len(supplier_nodes)) * 100 if supplier_nodes else 0
            
            # Get recent recalls involving this supplier
            recent_recalls = self.db.query(Recall).join(Batch).filter(
                Batch.supplier_id == supplier_id,
                Recall.created_at >= datetime.now() - timedelta(days=365)
            ).all()
            
            return {
                "supplier_id": supplier_id,
                "supplier_name": supplier.full_name if supplier else "Unknown",
                "supplier_email": supplier.email if supplier else None,
                "supplier_phone": supplier.phone if supplier else None,
                "total_batches": total_batches,
                "verified_nodes": verified_nodes,
                "verification_rate": verification_rate,
                "recent_recalls": len(recent_recalls),
                "last_activity": max([b.created_at for b in supplier_batches]) if supplier_batches else None,
                "compliance_status": "compliant" if verification_rate >= 95 else "needs_attention",
                "contact_information": {
                    "email": supplier.email if supplier else None,
                    "phone": supplier.phone if supplier else None,
                    "address": getattr(supplier, 'address', None) if supplier else None
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving supplier information: {str(e)}")
            raise
    
    def send_supplier_notification(self, supplier_id: int, notification_data: Dict[str, Any], sent_by: int) -> Dict[str, Any]:
        """Send notification to supplier for traceability or recall purposes"""
        try:
            # Get supplier information
            supplier_info = self.get_supplier_information(supplier_id)
            
            # Create notification record
            notification = Notification(
                user_id=supplier_id,
                title=notification_data.get("title", "Traceability Notification"),
                message=notification_data.get("message", ""),
                notification_type=NotificationType.TRACEABILITY,
                priority=NotificationPriority.HIGH if notification_data.get("urgent", False) else NotificationPriority.MEDIUM,
                category=NotificationCategory.SUPPLIER,
                created_by=sent_by,
                metadata=json.dumps({
                    "notification_type": "supplier_notification",
                    "batch_ids": notification_data.get("batch_ids", []),
                    "recall_id": notification_data.get("recall_id"),
                    "action_required": notification_data.get("action_required", False),
                    "deadline": notification_data.get("deadline")
                })
            )
            
            self.db.add(notification)
            self.db.commit()
            
            # Log the notification
            logger.info(f"Supplier notification sent to {supplier_info['supplier_name']} (ID: {supplier_id})")
            
            return {
                "notification_id": notification.id,
                "supplier_id": supplier_id,
                "supplier_name": supplier_info["supplier_name"],
                "sent_at": notification.created_at,
                "status": "sent",
                "message": notification.message
            }
        except Exception as e:
            logger.error(f"Error sending supplier notification: {str(e)}")
            raise
    
    def track_supplier_response(self, notification_id: int, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track supplier response to notifications"""
        try:
            notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                raise ValueError(f"Notification with ID {notification_id} not found")
            
            # Update notification with response
            notification.metadata = json.dumps({
                **json.loads(notification.metadata or "{}"),
                "response_received": True,
                "response_date": datetime.now().isoformat(),
                "response_content": response_data.get("response_content"),
                "action_taken": response_data.get("action_taken"),
                "compliance_confirmed": response_data.get("compliance_confirmed", False),
                "additional_information": response_data.get("additional_information")
            })
            
            notification.updated_at = datetime.now()
            self.db.commit()
            
            # Calculate response time
            response_time = (datetime.now() - notification.created_at).total_seconds() / 3600  # hours
            
            return {
                "notification_id": notification_id,
                "response_time_hours": response_time,
                "response_received": True,
                "compliance_confirmed": response_data.get("compliance_confirmed", False),
                "action_taken": response_data.get("action_taken")
            }
        except Exception as e:
            logger.error(f"Error tracking supplier response: {str(e)}")
            raise
    
    def get_customer_information(self, customer_id: int) -> Dict[str, Any]:
        """Retrieve comprehensive customer information for traceability"""
        try:
            # Get customer details from database
            customer = self.db.query(User).filter(User.id == customer_id).first()
            if not customer:
                raise ValueError(f"Customer with ID {customer_id} not found")
            
            # Get customer's batches (batches sent to this customer)
            customer_batches = self.db.query(Batch).filter(
                Batch.customer_information.contains(json.dumps({"customer_id": customer_id}))
            ).all()
            
            # Get customer's traceability nodes
            customer_nodes = self.db.query(TraceabilityNode).join(Batch).filter(
                Batch.customer_information.contains(json.dumps({"customer_id": customer_id}))
            ).all()
            
            # Calculate customer metrics
            total_batches = len(customer_batches)
            recent_batches = len([b for b in customer_batches if b.created_at >= datetime.now() - timedelta(days=30)])
            
            # Get recalls affecting this customer
            customer_recalls = self.db.query(Recall).join(Batch).filter(
                Batch.customer_information.contains(json.dumps({"customer_id": customer_id}))
            ).all()
            
            return {
                "customer_id": customer_id,
                "customer_name": customer.full_name if customer else "Unknown",
                "customer_email": customer.email if customer else None,
                "customer_phone": customer.phone if customer else None,
                "total_batches": total_batches,
                "recent_batches": recent_batches,
                "affected_recalls": len(customer_recalls),
                "last_activity": max([b.created_at for b in customer_batches]) if customer_batches else None,
                "contact_information": {
                    "email": customer.email if customer else None,
                    "phone": customer.phone if customer else None,
                    "address": getattr(customer, 'address', None) if customer else None
                },
                "preferred_communication": getattr(customer, 'preferred_communication', 'email') if customer else 'email'
            }
        except Exception as e:
            logger.error(f"Error retrieving customer information: {str(e)}")
            raise
    
    def send_customer_notification(self, customer_id: int, notification_data: Dict[str, Any], sent_by: int) -> Dict[str, Any]:
        """Send notification to customer for recall or traceability purposes"""
        try:
            # Get customer information
            customer_info = self.get_customer_information(customer_id)
            
            # Create notification record
            notification = Notification(
                user_id=customer_id,
                title=notification_data.get("title", "Product Recall Notification"),
                message=notification_data.get("message", ""),
                notification_type=NotificationType.RECALL,
                priority=NotificationPriority.CRITICAL if notification_data.get("urgent", False) else NotificationPriority.HIGH,
                category=NotificationCategory.CUSTOMER,
                created_by=sent_by,
                metadata=json.dumps({
                    "notification_type": "customer_notification",
                    "batch_ids": notification_data.get("batch_ids", []),
                    "recall_id": notification_data.get("recall_id"),
                    "health_risk_level": notification_data.get("health_risk_level"),
                    "action_required": notification_data.get("action_required", True),
                    "deadline": notification_data.get("deadline")
                })
            )
            
            self.db.add(notification)
            self.db.commit()
            
            # Log the notification
            logger.info(f"Customer notification sent to {customer_info['customer_name']} (ID: {customer_id})")
            
            return {
                "notification_id": notification.id,
                "customer_id": customer_id,
                "customer_name": customer_info["customer_name"],
                "sent_at": notification.created_at,
                "status": "sent",
                "message": notification.message,
                "health_risk_level": notification_data.get("health_risk_level")
            }
        except Exception as e:
            logger.error(f"Error sending customer notification: {str(e)}")
            raise
    
    def track_customer_feedback(self, notification_id: int, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track customer feedback and response to notifications"""
        try:
            notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                raise ValueError(f"Notification with ID {notification_id} not found")
            
            # Update notification with feedback
            notification.metadata = json.dumps({
                **json.loads(notification.metadata or "{}"),
                "feedback_received": True,
                "feedback_date": datetime.now().isoformat(),
                "feedback_content": feedback_data.get("feedback_content"),
                "product_returned": feedback_data.get("product_returned", False),
                "return_quantity": feedback_data.get("return_quantity"),
                "satisfaction_level": feedback_data.get("satisfaction_level"),
                "additional_comments": feedback_data.get("additional_comments")
            })
            
            notification.updated_at = datetime.now()
            self.db.commit()
            
            return {
                "notification_id": notification_id,
                "feedback_received": True,
                "product_returned": feedback_data.get("product_returned", False),
                "return_quantity": feedback_data.get("return_quantity"),
                "satisfaction_level": feedback_data.get("satisfaction_level"),
                "feedback_content": feedback_data.get("feedback_content")
            }
        except Exception as e:
            logger.error(f"Error tracking customer feedback: {str(e)}")
            raise
    
    def generate_regulatory_report(self, report_type: str, date_range: Tuple[datetime, datetime], 
                                 format_type: str = "pdf") -> Dict[str, Any]:
        """Generate regulatory compliance reports in required formats"""
        try:
            start_date, end_date = date_range
            
            # Get data for the specified date range
            batches = self.db.query(Batch).filter(
                Batch.created_at.between(start_date, end_date)
            ).all()
            
            recalls = self.db.query(Recall).filter(
                Recall.created_at.between(start_date, end_date)
            ).all()
            
            traceability_reports = self.db.query(TraceabilityReport).filter(
                TraceabilityReport.created_at.between(start_date, end_date)
            ).all()
            
            # Generate report data based on type
            if report_type == "traceability_compliance":
                report_data = self._generate_traceability_compliance_data(batches, traceability_reports)
            elif report_type == "recall_management":
                report_data = self._generate_recall_management_data(recalls)
            elif report_type == "haccp_compliance":
                report_data = self._generate_haccp_compliance_data(batches, recalls)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Add metadata
            report_data.update({
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "format": format_type,
                "compliance_standards": ["ISO 22000:2018", "ISO 22005:2007", "ISO 22002-1:2025"]
            })
            
            return report_data
        except Exception as e:
            logger.error(f"Error generating regulatory report: {str(e)}")
            raise
    
    def _generate_traceability_compliance_data(self, batches: List[Batch], 
                                             traceability_reports: List[TraceabilityReport]) -> Dict[str, Any]:
        """Generate traceability compliance data for regulatory reports"""
        total_batches = len(batches)
        batches_with_gtin = len([b for b in batches if b.gtin])
        batches_with_sscc = len([b for b in batches if b.sscc])
        batches_with_supplier_info = len([b for b in batches if b.supplier_information])
        
        # Calculate compliance percentages
        gtin_compliance = (batches_with_gtin / total_batches) * 100 if total_batches > 0 else 0
        sscc_compliance = (batches_with_sscc / total_batches) * 100 if total_batches > 0 else 0
        supplier_info_compliance = (batches_with_supplier_info / total_batches) * 100 if total_batches > 0 else 0
        
        return {
            "total_batches": total_batches,
            "gtin_compliance_rate": gtin_compliance,
            "sscc_compliance_rate": sscc_compliance,
            "supplier_info_compliance_rate": supplier_info_compliance,
            "traceability_reports_generated": len(traceability_reports),
            "compliance_status": "compliant" if min(gtin_compliance, sscc_compliance, supplier_info_compliance) >= 95 else "needs_improvement"
        }
    
    def _generate_recall_management_data(self, recalls: List[Recall]) -> Dict[str, Any]:
        """Generate recall management data for regulatory reports"""
        total_recalls = len(recalls)
        class_i_recalls = len([r for r in recalls if r.recall_type == RecallType.CLASS_I])
        class_ii_recalls = len([r for r in recalls if r.recall_type == RecallType.CLASS_II])
        class_iii_recalls = len([r for r in recalls if r.recall_type == RecallType.CLASS_III])
        
        # Calculate average response times
        response_times = []
        for recall in recalls:
            if recall.recall_date and recall.created_at:
                response_time = (recall.recall_date - recall.created_at).total_seconds() / 3600  # hours
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_recalls": total_recalls,
            "class_i_recalls": class_i_recalls,
            "class_ii_recalls": class_ii_recalls,
            "class_iii_recalls": class_iii_recalls,
            "average_response_time_hours": avg_response_time,
            "compliance_status": "compliant" if avg_response_time <= 24 else "needs_improvement"
        }
    
    def _generate_haccp_compliance_data(self, batches: List[Batch], recalls: List[Recall]) -> Dict[str, Any]:
        """Generate HACCP compliance data for regulatory reports"""
        # Get CCP-related traceability nodes
        ccp_nodes = self.db.query(TraceabilityNode).filter(TraceabilityNode.ccp_related == True).all()
        
        verified_ccp_nodes = len([n for n in ccp_nodes if n.verification_status == "verified"])
        ccp_verification_rate = (verified_ccp_nodes / len(ccp_nodes)) * 100 if ccp_nodes else 0
        
        # Calculate HACCP compliance metrics
        total_batches = len(batches)
        batches_with_ccp_tracking = len([b for b in batches if any(n.ccp_related for n in b.traceability_nodes) if hasattr(b, 'traceability_nodes')])
        ccp_tracking_rate = (batches_with_ccp_tracking / total_batches) * 100 if total_batches > 0 else 0
        
        return {
            "ccp_verification_rate": ccp_verification_rate,
            "ccp_tracking_rate": ccp_tracking_rate,
            "total_ccp_nodes": len(ccp_nodes),
            "verified_ccp_nodes": verified_ccp_nodes,
            "compliance_status": "compliant" if ccp_verification_rate >= 95 and ccp_tracking_rate >= 90 else "needs_improvement"
        }
    
    def send_regulatory_notification(self, regulatory_body: str, notification_data: Dict[str, Any], 
                                   sent_by: int) -> Dict[str, Any]:
        """Send automated notification to regulatory bodies"""
        try:
            # Create regulatory notification record
            notification = Notification(
                user_id=None,  # Regulatory notifications may not have specific user
                title=f"Regulatory Notification - {regulatory_body}",
                message=notification_data.get("message", ""),
                notification_type=NotificationType.REGULATORY,
                priority=NotificationPriority.CRITICAL,
                category=NotificationCategory.REGULATORY,
                created_by=sent_by,
                metadata=json.dumps({
                    "notification_type": "regulatory_notification",
                    "regulatory_body": regulatory_body,
                    "report_type": notification_data.get("report_type"),
                    "compliance_status": notification_data.get("compliance_status"),
                    "action_required": notification_data.get("action_required", False),
                    "deadline": notification_data.get("deadline"),
                    "report_data": notification_data.get("report_data")
                })
            )
            
            self.db.add(notification)
            self.db.commit()
            
            # Log the regulatory notification
            logger.info(f"Regulatory notification sent to {regulatory_body}")
            
            return {
                "notification_id": notification.id,
                "regulatory_body": regulatory_body,
                "sent_at": notification.created_at,
                "status": "sent",
                "compliance_status": notification_data.get("compliance_status")
            }
        except Exception as e:
            logger.error(f"Error sending regulatory notification: {str(e)}")
            raise
    
    def track_regulatory_compliance(self, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track regulatory compliance status and requirements"""
        try:
            # Calculate overall compliance score
            compliance_score = 0
            total_checks = 0
            
            # Check traceability compliance
            if "traceability_compliance" in compliance_data:
                traceability_score = compliance_data["traceability_compliance"].get("score", 0)
                compliance_score += traceability_score
                total_checks += 1
            
            # Check recall management compliance
            if "recall_management_compliance" in compliance_data:
                recall_score = compliance_data["recall_management_compliance"].get("score", 0)
                compliance_score += recall_score
                total_checks += 1
            
            # Check HACCP compliance
            if "haccp_compliance" in compliance_data:
                haccp_score = compliance_data["haccp_compliance"].get("score", 0)
                compliance_score += haccp_score
                total_checks += 1
            
            # Calculate overall score
            overall_score = compliance_score / total_checks if total_checks > 0 else 0
            
            # Determine compliance status
            if overall_score >= 95:
                compliance_status = "fully_compliant"
            elif overall_score >= 80:
                compliance_status = "mostly_compliant"
            elif overall_score >= 60:
                compliance_status = "partially_compliant"
            else:
                compliance_status = "non_compliant"
            
            # Create compliance tracking record
            compliance_record = {
                "overall_score": overall_score,
                "compliance_status": compliance_status,
                "assessment_date": datetime.now().isoformat(),
                "traceability_compliance": compliance_data.get("traceability_compliance", {}),
                "recall_management_compliance": compliance_data.get("recall_management_compliance", {}),
                "haccp_compliance": compliance_data.get("haccp_compliance", {}),
                "improvement_areas": compliance_data.get("improvement_areas", []),
                "next_assessment_date": (datetime.now() + timedelta(days=90)).isoformat()
            }
            
            return compliance_record
        except Exception as e:
            logger.error(f"Error tracking regulatory compliance: {str(e)}")
            raise 

    # ============================================================================
    # PHASE 1.3.1: MISSING TRACEABILITY NODE METHODS
    # ============================================================================

    def get_traceability_nodes(self, skip: int = 0, limit: int = 100, 
                             node_type: Optional[str] = None, 
                             verification_status: Optional[str] = None) -> List[TraceabilityNode]:
        """Get traceability nodes with filtering"""
        try:
            query = self.db.query(TraceabilityNode)
            
            if node_type:
                query = query.filter(TraceabilityNode.node_type == node_type)
            
            if verification_status:
                query = query.filter(TraceabilityNode.verification_status == verification_status)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            self.logger.error(f"Error getting traceability nodes: {str(e)}")
            raise ValueError(f"Failed to get traceability nodes: {str(e)}")

    def get_traceability_node(self, node_id: int) -> Optional[TraceabilityNode]:
        """Get a specific traceability node"""
        try:
            return self.db.query(TraceabilityNode).filter(TraceabilityNode.id == node_id).first()
        except Exception as e:
            self.logger.error(f"Error getting traceability node {node_id}: {str(e)}")
            raise ValueError(f"Failed to get traceability node: {str(e)}")

    def verify_traceability_node(self, node_id: int, verification_data: dict, user_id: int) -> dict:
        """Verify a traceability node"""
        try:
            node = self.get_traceability_node(node_id)
            if not node:
                raise ValueError("Traceability node not found")
            
            # Update verification status
            node.verification_status = verification_data.get("verification_status", "verified")
            node.last_verified = datetime.utcnow()
            node.verification_notes = verification_data.get("verification_notes", "")
            node.verified_by = user_id
            node.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Create verification notification
            self._create_verification_notification(node, verification_data)
            
            return {
                "node_id": node.id,
                "verification_status": node.verification_status,
                "verification_date": node.last_verified.isoformat(),
                "verification_notes": node.verification_notes,
                "verified_by": user_id
            }
        except Exception as e:
            self.logger.error(f"Error verifying traceability node {node_id}: {str(e)}")
            raise ValueError(f"Failed to verify traceability node: {str(e)}")

    # ============================================================================
    # PHASE 1.3.3: ENHANCED BATCH MANAGEMENT METHODS
    # ============================================================================

    def create_enhanced_batch(self, batch_data: dict, created_by: int) -> Batch:
        """Create a new batch with enhanced GS1-compliant fields"""
        try:
            # Generate unique batch number
            batch_number = f"BATCH-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Generate GS1-compliant identifiers
            gtin = batch_data.get("gtin", f"GTIN-{str(uuid.uuid4())[:12]}")
            sscc = batch_data.get("sscc", f"SSCC-{str(uuid.uuid4())[:18]}")
            hierarchical_lot_number = batch_data.get("hierarchical_lot_number", f"HLN-{batch_number}")
            
            # Generate enhanced barcode with GS1 information
            barcode_data = {
                "batch_number": batch_number,
                "batch_type": batch_data.get("batch_type", "final_product"),
                "product_name": batch_data.get("product_name", ""),
                "production_date": batch_data.get("production_date", datetime.now().isoformat()),
                "quantity": batch_data.get("quantity", 0),
                "unit": batch_data.get("unit", ""),
                "gtin": gtin,
                "sscc": sscc
            }
            
            barcode = self._generate_enhanced_barcode(barcode_data)
            qr_code_path = self._generate_qr_code(barcode_data, batch_number)
            
            batch = Batch(
                batch_number=batch_number,
                batch_type=BatchType(batch_data.get("batch_type", "final_product")),
                status=BatchStatus.IN_PRODUCTION,
                product_name=batch_data.get("product_name", ""),
                quantity=batch_data.get("quantity", 0),
                unit=batch_data.get("unit", ""),
                production_date=datetime.fromisoformat(batch_data.get("production_date", datetime.now().isoformat())),
                expiry_date=datetime.fromisoformat(batch_data.get("expiry_date")) if batch_data.get("expiry_date") else None,
                lot_number=batch_data.get("lot_number"),
                supplier_id=batch_data.get("supplier_id"),
                supplier_batch_number=batch_data.get("supplier_batch_number"),
                coa_number=batch_data.get("coa_number"),
                storage_location=batch_data.get("storage_location"),
                storage_conditions=batch_data.get("storage_conditions"),
                gtin=gtin,
                sscc=sscc,
                hierarchical_lot_number=hierarchical_lot_number,
                supplier_information=json.dumps(batch_data.get("supplier_information", {})),
                customer_information=json.dumps(batch_data.get("customer_information", {})),
                distribution_location=batch_data.get("distribution_location"),
                barcode=barcode,
                qr_code_path=qr_code_path,
                created_by=created_by
            )
            
            self.db.add(batch)
            self.db.commit()
            self.db.refresh(batch)
            
            return batch
        except Exception as e:
            self.logger.error(f"Error creating enhanced batch: {str(e)}")
            raise ValueError(f"Failed to create enhanced batch: {str(e)}")

    def update_enhanced_batch(self, batch_id: int, batch_data: dict, updated_by: int) -> Batch:
        """Update a batch with enhanced GS1-compliant fields"""
        try:
            batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError("Batch not found")
            
            # Update basic fields
            if "batch_type" in batch_data:
                batch.batch_type = BatchType(batch_data["batch_type"])
            if "status" in batch_data:
                batch.status = BatchStatus(batch_data["status"])
            if "product_name" in batch_data:
                batch.product_name = batch_data["product_name"]
            if "quantity" in batch_data:
                batch.quantity = batch_data["quantity"]
            if "unit" in batch_data:
                batch.unit = batch_data["unit"]
            if "expiry_date" in batch_data:
                batch.expiry_date = datetime.fromisoformat(batch_data["expiry_date"]) if batch_data["expiry_date"] else None
            if "lot_number" in batch_data:
                batch.lot_number = batch_data["lot_number"]
            
            # Update GS1-compliant fields
            if "gtin" in batch_data:
                batch.gtin = batch_data["gtin"]
            if "sscc" in batch_data:
                batch.sscc = batch_data["sscc"]
            if "hierarchical_lot_number" in batch_data:
                batch.hierarchical_lot_number = batch_data["hierarchical_lot_number"]
            if "supplier_information" in batch_data:
                batch.supplier_information = json.dumps(batch_data["supplier_information"])
            if "customer_information" in batch_data:
                batch.customer_information = json.dumps(batch_data["customer_information"])
            if "distribution_location" in batch_data:
                batch.distribution_location = batch_data["distribution_location"]
            
            batch.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(batch)
            
            return batch
        except Exception as e:
            self.logger.error(f"Error updating enhanced batch {batch_id}: {str(e)}")
            raise ValueError(f"Failed to update enhanced batch: {str(e)}")

    def search_enhanced_batches_gs1(self, search_criteria: dict, skip: int = 0, limit: int = 100) -> List[Batch]:
        """Enhanced batch search with GS1-compliant fields"""
        try:
            query = self.db.query(Batch)
            
            # Apply search criteria
            if "batch_number" in search_criteria:
                query = query.filter(Batch.batch_number.ilike(f"%{search_criteria['batch_number']}%"))
            if "product_name" in search_criteria:
                query = query.filter(Batch.product_name.ilike(f"%{search_criteria['product_name']}%"))
            if "lot_number" in search_criteria:
                query = query.filter(Batch.lot_number.ilike(f"%{search_criteria['lot_number']}%"))
            if "gtin" in search_criteria:
                query = query.filter(Batch.gtin.ilike(f"%{search_criteria['gtin']}%"))
            if "sscc" in search_criteria:
                query = query.filter(Batch.sscc.ilike(f"%{search_criteria['sscc']}%"))
            if "hierarchical_lot_number" in search_criteria:
                query = query.filter(Batch.hierarchical_lot_number.ilike(f"%{search_criteria['hierarchical_lot_number']}%"))
            if "batch_type" in search_criteria:
                query = query.filter(Batch.batch_type == BatchType(search_criteria["batch_type"]))
            if "status" in search_criteria:
                query = query.filter(Batch.status == BatchStatus(search_criteria["status"]))
            if "production_date_from" in search_criteria:
                query = query.filter(Batch.production_date >= datetime.fromisoformat(search_criteria["production_date_from"]))
            if "production_date_to" in search_criteria:
                query = query.filter(Batch.production_date <= datetime.fromisoformat(search_criteria["production_date_to"]))
            if "distribution_location" in search_criteria:
                query = query.filter(Batch.distribution_location.ilike(f"%{search_criteria['distribution_location']}%"))
            
            return query.order_by(desc(Batch.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            self.logger.error(f"Error searching enhanced batches: {str(e)}")
            raise ValueError(f"Failed to search enhanced batches: {str(e)}")