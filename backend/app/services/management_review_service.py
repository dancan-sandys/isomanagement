from typing import Tuple, List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
import json

from app.models.management_review import (
    ManagementReview, ReviewAgendaItem, ReviewAction, ManagementReviewStatus,
    ManagementReviewInput, ManagementReviewOutput, ManagementReviewTemplate,
    ManagementReviewKPI, ReviewInputType, ReviewOutputType, ActionStatus,
    ActionPriority, ManagementReviewType
)
from app.schemas.management_review import (
    ManagementReviewCreate, ManagementReviewUpdate, ManagementReviewInputCreate,
    ManagementReviewOutputCreate, ReviewActionCreate, ReviewActionUpdate,
    DataCollectionRequest, ComplianceCheckResponse
)
from app.services.management_review_data_aggregation_service import ManagementReviewDataAggregationService
from app.services.actions_log_service import ActionsLogService
from app.models.actions_log import ActionSource


class ManagementReviewService:
    """Enhanced Management Review Service with ISO 22000:2018 compliance features"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_aggregation_service = ManagementReviewDataAggregationService(db)

    # ==================== CORE REVIEW MANAGEMENT ====================
    
    def create(self, payload: ManagementReviewCreate, created_by: int) -> ManagementReview:
        """Create a new management review with enhanced ISO compliance features"""
        try:
            # Create the review with all new fields
            review = ManagementReview(
                title=payload.title,
                review_date=payload.review_date,
                review_type=payload.review_type,
                review_scope=payload.review_scope,
                attendees=payload.attendees,
                chairperson_id=payload.chairperson_id,
                review_frequency=payload.review_frequency,
                
                # ISO compliance fields
                food_safety_policy_reviewed=payload.food_safety_policy_reviewed,
                food_safety_objectives_reviewed=payload.food_safety_objectives_reviewed,
                fsms_changes_required=payload.fsms_changes_required,
                resource_adequacy_assessment=payload.resource_adequacy_assessment,
                improvement_opportunities=payload.improvement_opportunities,
                external_issues=payload.external_issues,
                internal_issues=payload.internal_issues,
                
                status=payload.status or ManagementReviewStatus.PLANNED,
                next_review_date=payload.next_review_date,
                created_by=created_by,
            )
            
            self.db.add(review)
            self.db.flush()
            
            # Add agenda items
            if payload.agenda:
                for idx, agenda_item in enumerate(payload.agenda):
                    self.db.add(ReviewAgendaItem(
                        review_id=review.id,
                        topic=agenda_item.topic,
                        discussion=agenda_item.discussion,
                        decision=agenda_item.decision,
                        order_index=agenda_item.order_index if agenda_item.order_index is not None else idx + 1,
                    ))
            
            self.db.commit()
            self.db.refresh(review)
            return review
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create management review: {str(e)}")

    def create_from_template(self, template_id: int, payload: ManagementReviewCreate, created_by: int) -> ManagementReview:
        """Create a review from a template"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")
        
        # Merge template data with payload
        if template.agenda_template:
            agenda_items = []
            for item in template.agenda_template:
                agenda_items.append(ReviewAgendaItem(
                    topic=item.get('topic', ''),
                    discussion=item.get('discussion', ''),
                    order_index=item.get('order_index', 0)
                ))
            payload.agenda = agenda_items
        
        return self.create(payload, created_by)

    def list(self, page: int = 1, size: int = 20, status: Optional[ManagementReviewStatus] = None,
             review_type: Optional[ManagementReviewType] = None) -> Tuple[List[ManagementReview], int]:
        """List reviews with enhanced filtering"""
        q = self.db.query(ManagementReview)
        
        # Apply filters
        if status:
            q = q.filter(ManagementReview.status == status)
        if review_type:
            q = q.filter(ManagementReview.review_type == review_type)
        
        # Order by review date, then created date
        q = q.order_by(
            desc(func.coalesce(ManagementReview.review_date, ManagementReview.created_at)),
            desc(ManagementReview.created_at),
        )
        
        total = q.count()
        items = q.offset((page - 1) * size).limit(size).all()
        return items, total

    def get(self, review_id: int) -> Optional[ManagementReview]:
        """Get a management review by ID"""
        return self.db.query(ManagementReview).filter(ManagementReview.id == review_id).first()

    def update(self, review_id: int, payload: ManagementReviewUpdate) -> ManagementReview:
        """Update a management review with enhanced fields"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        # Update fields
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(review, k, v)
        
        # Update timestamp
        review.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(review)
        return review

    def complete_review(self, review_id: int, completed_by: int) -> ManagementReview:
        """Mark a review as completed and calculate effectiveness"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        review.status = ManagementReviewStatus.COMPLETED
        review.completed_at = datetime.utcnow()
        
        # Calculate review effectiveness
        effectiveness_score = self.calculate_review_effectiveness(review_id)
        review.review_effectiveness_score = effectiveness_score
        
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review_id: int) -> bool:
        """Delete a management review"""
        review = self.get(review_id)
        if not review:
            return False
        
        self.db.delete(review)
        self.db.commit()
        return True

    # ==================== DATA COLLECTION AND INPUTS ====================
    
    def collect_review_inputs(self, review_id: int, request: DataCollectionRequest) -> Dict[str, Any]:
        """Collect all required inputs for a management review"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        # Collect data using the aggregation service
        inputs_data = self.data_aggregation_service.collect_all_inputs(
            request.date_range_start, 
            request.date_range_end
        )
        
        # Store collected inputs
        for input_type, data in inputs_data.items():
            if input_type in request.input_types:
                input_record = ManagementReviewInput(
                    review_id=review_id,
                    input_type=input_type,
                    input_source="automated_collection",
                    input_data=data.get("data", {}),
                    input_summary=data.get("summary", ""),
                    collection_date=datetime.utcnow(),
                    data_completeness_score=data.get("completeness_score", 0.0),
                    data_accuracy_verified=True
                )
                self.db.add(input_record)
        
        self.db.commit()
        return inputs_data

    def add_manual_input(self, review_id: int, payload: ManagementReviewInputCreate) -> ManagementReviewInput:
        """Add manual input to a review"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        input_record = ManagementReviewInput(
            review_id=review_id,
            input_type=payload.input_type,
            input_source=payload.input_source,
            input_data=payload.input_data,
            input_summary=payload.input_summary,
            collection_date=payload.collection_date or datetime.utcnow(),
            responsible_person_id=payload.responsible_person_id
        )
        
        self.db.add(input_record)
        self.db.commit()
        self.db.refresh(input_record)
        return input_record

    def get_review_inputs(self, review_id: int) -> List[ManagementReviewInput]:
        """Get all inputs for a review"""
        return self.db.query(ManagementReviewInput).filter(
            ManagementReviewInput.review_id == review_id
        ).order_by(ManagementReviewInput.created_at).all()

    # ==================== OUTPUTS AND DECISIONS ====================
    
    def add_review_output(self, review_id: int, payload: ManagementReviewOutputCreate) -> ManagementReviewOutput:
        """Add a structured output/decision to a review"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        output_record = ManagementReviewOutput(
            review_id=review_id,
            output_type=payload.output_type,
            title=payload.title,
            description=payload.description,
            assigned_to=payload.assigned_to,
            target_completion_date=payload.target_completion_date,
            priority=payload.priority,
            implementation_plan=payload.implementation_plan,
            resource_requirements=payload.resource_requirements,
            success_criteria=payload.success_criteria,
            verification_required=payload.verification_required
        )
        
        self.db.add(output_record)
        self.db.commit()
        self.db.refresh(output_record)
        return output_record

    def get_review_outputs(self, review_id: int) -> List[ManagementReviewOutput]:
        """Get all outputs for a review"""
        return self.db.query(ManagementReviewOutput).filter(
            ManagementReviewOutput.review_id == review_id
        ).order_by(ManagementReviewOutput.created_at).all()

    def update_output_progress(self, output_id: int, progress_percentage: float, 
                             progress_notes: Optional[str] = None) -> ManagementReviewOutput:
        """Update progress on a review output"""
        output = self.db.query(ManagementReviewOutput).filter(
            ManagementReviewOutput.id == output_id
        ).first()
        
        if not output:
            raise ValueError("Review output not found")
        
        output.progress_percentage = progress_percentage
        if progress_notes:
            output.progress_updates = output.progress_updates or []
            output.progress_updates.append({
                "date": datetime.utcnow().isoformat(),
                "progress": progress_percentage,
                "notes": progress_notes
            })
        
        # Update status based on progress
        if progress_percentage >= 100:
            output.status = ActionStatus.COMPLETED
            output.completed = True
            output.completed_at = datetime.utcnow()
        elif progress_percentage > 0:
            output.status = ActionStatus.IN_PROGRESS
        
        self.db.commit()
        self.db.refresh(output)
        return output

    # ==================== ENHANCED ACTION MANAGEMENT ====================
    
    def add_action(self, review_id: int, payload: ReviewActionCreate, created_by: int = 1) -> ReviewAction:
        """Add an enhanced action to a review and sync with actions log"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        # Create the review action first
        action = ReviewAction(
            review_id=review_id,
            title=payload.title,
            description=payload.description,
            assigned_to=payload.assigned_to,
            due_date=payload.due_date,
            action_type=payload.action_type,
            priority=payload.priority,
            verification_required=payload.verification_required,
            estimated_effort_hours=payload.estimated_effort_hours,
            resource_requirements=payload.resource_requirements
        )
        
        self.db.add(action)
        self.db.flush()  # Get the ID without committing
        
        # Create corresponding entry in actions log
        actions_log_service = ActionsLogService(self.db)
        
        # Map management review priority to actions log priority
        priority_mapping = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "critical"
        }
        
        # Map management review status to actions log status
        status_mapping = {
            "assigned": "pending",
            "in_progress": "in_progress",
            "completed": "completed",
            "overdue": "overdue",
            "cancelled": "cancelled"
        }
        
        action_log_data = {
            "title": payload.title,
            "description": payload.description or "",
            "action_source": ActionSource.MANAGEMENT_REVIEW.value,
            "source_id": action.id,  # Link back to the review action
            "priority": priority_mapping.get(payload.priority.value if hasattr(payload.priority, 'value') else str(payload.priority), "medium"),
            "status": status_mapping.get(action.status.value if hasattr(action.status, 'value') else str(action.status), "pending"),
            "assigned_to": payload.assigned_to,
            "assigned_by": created_by,
            "due_date": payload.due_date,
            "estimated_hours": payload.estimated_effort_hours,
            "notes": f"Action from Management Review: {review.title}",
            "tags": {
                "review_id": review_id,
                "review_title": review.title,
                "action_type": payload.action_type.value if hasattr(payload.action_type, 'value') else str(payload.action_type) if payload.action_type else None
            }
        }
        
        action_log = actions_log_service.create_action(action_log_data)
        
        # Link the action log back to the review action
        action.action_log_id = action_log.id
        
        self.db.commit()
        self.db.refresh(action)
        return action

    def update_action(self, action_id: int, payload: ReviewActionUpdate) -> ReviewAction:
        """Update an action with enhanced tracking and sync with actions log"""
        action = self.db.query(ReviewAction).filter(ReviewAction.id == action_id).first()
        if not action:
            raise ValueError("Action not found")
        
        # Update fields
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(action, k, v)
        
        # Check if overdue
        if action.due_date and action.due_date < datetime.utcnow() and not action.completed:
            action.status = ActionStatus.OVERDUE
        
        action.updated_at = datetime.utcnow()
        
        # Sync changes to actions log if linked
        if action.action_log_id:
            actions_log_service = ActionsLogService(self.db)
            
            # Map status and priority
            priority_mapping = {
                "low": "low",
                "medium": "medium", 
                "high": "high",
                "critical": "critical"
            }
            
            status_mapping = {
                "assigned": "pending",
                "in_progress": "in_progress",
                "completed": "completed",
                "overdue": "overdue",
                "cancelled": "cancelled"
            }
            
            update_data = {}
            if 'title' in data:
                update_data['title'] = data['title']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'assigned_to' in data:
                update_data['assigned_to'] = data['assigned_to']
            if 'due_date' in data:
                update_data['due_date'] = data['due_date']
            if 'priority' in data:
                update_data['priority'] = priority_mapping.get(
                    data['priority'].value if hasattr(data['priority'], 'value') else str(data['priority']), 
                    "medium"
                )
            if 'status' in data or action.status:
                update_data['status'] = status_mapping.get(
                    action.status.value if hasattr(action.status, 'value') else str(action.status), 
                    "pending"
                )
            if 'progress_percentage' in data:
                update_data['progress_percent'] = data['progress_percentage']
            if 'estimated_effort_hours' in data:
                update_data['estimated_hours'] = data['estimated_effort_hours']
            
            if update_data:
                actions_log_service.update_action(action.action_log_id, update_data)
        
        self.db.commit()
        self.db.refresh(action)
        return action

    def complete_action(self, action_id: int, completed_by: int) -> ReviewAction:
        """Complete an action with enhanced tracking and sync with actions log"""
        action = self.db.query(ReviewAction).filter(ReviewAction.id == action_id).first()
        if not action:
            raise ValueError("Action not found")
        
        action.completed = True
        action.completed_at = datetime.utcnow()
        action.completed_by = completed_by
        action.status = ActionStatus.COMPLETED
        action.progress_percentage = 100.0
        
        # Sync completion to actions log if linked
        if action.action_log_id:
            actions_log_service = ActionsLogService(self.db)
            actions_log_service.update_action(action.action_log_id, {
                "status": "completed",
                "progress_percent": 100.0
            })
        
        self.db.commit()
        self.db.refresh(action)
        return action

    def list_actions(self, review_id: int, status: Optional[ActionStatus] = None) -> List[ReviewAction]:
        """List actions with filtering"""
        q = self.db.query(ReviewAction).filter(ReviewAction.review_id == review_id)
        
        if status:
            q = q.filter(ReviewAction.status == status)
        
        return q.order_by(desc(ReviewAction.created_at)).all()

    def get_overdue_actions(self, review_id: Optional[int] = None) -> List[ReviewAction]:
        """Get overdue actions"""
        q = self.db.query(ReviewAction).filter(
            and_(
                ReviewAction.due_date < datetime.utcnow(),
                ReviewAction.completed == False
            )
        )
        
        if review_id:
            q = q.filter(ReviewAction.review_id == review_id)
        
        return q.all()

    # ==================== EFFECTIVENESS AND ANALYTICS ====================
    
    def calculate_review_effectiveness(self, review_id: int) -> float:
        """Calculate review effectiveness score based on multiple factors"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        effectiveness_factors = []
        
        # Factor 1: Input completeness (30%)
        inputs = self.get_review_inputs(review_id)
        if inputs:
            avg_completeness = sum([i.data_completeness_score or 0 for i in inputs]) / len(inputs)
            effectiveness_factors.append(avg_completeness * 0.3)
        
        # Factor 2: Output implementation (40%)
        outputs = self.get_review_outputs(review_id)
        if outputs:
            avg_progress = sum([o.progress_percentage for o in outputs]) / len(outputs) / 100
            effectiveness_factors.append(avg_progress * 0.4)
        
        # Factor 3: Action completion rate (30%)
        actions = self.list_actions(review_id)
        if actions:
            completed_actions = len([a for a in actions if a.completed])
            completion_rate = completed_actions / len(actions)
            effectiveness_factors.append(completion_rate * 0.3)
        
        # Calculate overall effectiveness (scale 1-10)
        if effectiveness_factors:
            effectiveness_score = sum(effectiveness_factors) * 10
            return round(min(effectiveness_score, 10.0), 2)
        
        return 5.0  # Default neutral score

    def get_review_analytics(self, review_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a review"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        inputs = self.get_review_inputs(review_id)
        outputs = self.get_review_outputs(review_id)
        actions = self.list_actions(review_id)
        
        return {
            "review_summary": {
                "id": review.id,
                "title": review.title,
                "status": review.status,
                "effectiveness_score": review.review_effectiveness_score or 0
            },
            "input_analytics": {
                "total_inputs": len(inputs),
                "avg_completeness": sum([i.data_completeness_score or 0 for i in inputs]) / len(inputs) if inputs else 0,
                "input_types_covered": list(set([i.input_type for i in inputs]))
            },
            "output_analytics": {
                "total_outputs": len(outputs),
                "completed_outputs": len([o for o in outputs if o.completed]),
                "avg_progress": sum([o.progress_percentage for o in outputs]) / len(outputs) if outputs else 0,
                "output_types": list(set([o.output_type for o in outputs]))
            },
            "action_analytics": {
                "total_actions": len(actions),
                "completed_actions": len([a for a in actions if a.completed]),
                "overdue_actions": len([a for a in actions if a.due_date and a.due_date < datetime.utcnow() and not a.completed]),
                "avg_progress": sum([a.progress_percentage for a in actions]) / len(actions) if actions else 0
            }
        }

    # ==================== COMPLIANCE AND REPORTING ====================
    
    def check_iso_compliance(self, review_id: int) -> ComplianceCheckResponse:
        """Check ISO 22000:2018 compliance for a review"""
        review = self.get(review_id)
        if not review:
            raise ValueError("Management review not found")
        
        inputs = self.get_review_inputs(review_id)
        outputs = self.get_review_outputs(review_id)
        
        # Required inputs per ISO 22000:2018
        required_inputs = [
            ReviewInputType.AUDIT_RESULTS,
            ReviewInputType.NC_CAPA_STATUS,
            ReviewInputType.SUPPLIER_PERFORMANCE,
            ReviewInputType.HACCP_PERFORMANCE,
            ReviewInputType.PRP_PERFORMANCE,
            ReviewInputType.RISK_ASSESSMENT,
            ReviewInputType.PREVIOUS_ACTIONS
        ]
        
        # Required outputs per ISO 22000:2018
        required_outputs = [
            ReviewOutputType.IMPROVEMENT_ACTION,
            ReviewOutputType.RESOURCE_ALLOCATION,
            ReviewOutputType.SYSTEM_CHANGE
        ]
        
        # Check input compliance
        present_inputs = [i.input_type for i in inputs]
        missing_inputs = [req.value for req in required_inputs if req not in present_inputs]
        
        # Check output compliance
        present_outputs = [o.output_type for o in outputs]
        missing_outputs = [req.value for req in required_outputs if req not in present_outputs]
        
        # Calculate compliance score
        input_compliance = (len(required_inputs) - len(missing_inputs)) / len(required_inputs)
        output_compliance = (len(required_outputs) - len(missing_outputs)) / len(required_outputs)
        overall_compliance = (input_compliance + output_compliance) / 2 * 100
        
        # Generate recommendations
        recommendations = []
        if missing_inputs:
            recommendations.append(f"Collect missing inputs: {', '.join(missing_inputs)}")
        if missing_outputs:
            recommendations.append(f"Document missing outputs: {', '.join(missing_outputs)}")
        if not review.food_safety_policy_reviewed:
            recommendations.append("Review food safety policy compliance")
        if not review.food_safety_objectives_reviewed:
            recommendations.append("Review food safety objectives achievement")
        
        return ComplianceCheckResponse(
            iso_22000_compliance={
                "clause_9_3_compliance": overall_compliance,
                "input_compliance": input_compliance * 100,
                "output_compliance": output_compliance * 100,
                "policy_reviewed": review.food_safety_policy_reviewed,
                "objectives_reviewed": review.food_safety_objectives_reviewed
            },
            missing_inputs=missing_inputs,
            missing_outputs=missing_outputs,
            compliance_score=overall_compliance,
            recommendations=recommendations
        )

    # ==================== TEMPLATE MANAGEMENT ====================
    
    def create_template(self, name: str, description: str, created_by: int, 
                       agenda_template: Optional[List[Dict]] = None,
                       input_checklist: Optional[List[Dict]] = None) -> ManagementReviewTemplate:
        """Create a review template"""
        template = ManagementReviewTemplate(
            name=name,
            description=description,
            agenda_template=agenda_template,
            input_checklist=input_checklist,
            created_by=created_by
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_template(self, template_id: int) -> Optional[ManagementReviewTemplate]:
        """Get a template by ID"""
        return self.db.query(ManagementReviewTemplate).filter(
            ManagementReviewTemplate.id == template_id
        ).first()

    def list_templates(self, active_only: bool = True) -> List[ManagementReviewTemplate]:
        """List available templates"""
        q = self.db.query(ManagementReviewTemplate)
        if active_only:
            q = q.filter(ManagementReviewTemplate.is_active == True)
        return q.order_by(ManagementReviewTemplate.name).all()

    def get_default_template(self) -> Optional[ManagementReviewTemplate]:
        """Get the default template"""
        return self.db.query(ManagementReviewTemplate).filter(
            and_(
                ManagementReviewTemplate.is_default == True,
                ManagementReviewTemplate.is_active == True
            )
        ).first()


