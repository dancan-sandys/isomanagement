import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid

from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.schemas.haccp import (
    ProductCreate, ProductUpdate, ProcessFlowCreate, HazardCreate, CCPCreate,
    MonitoringLogCreate, VerificationLogCreate, DecisionTreeResult, DecisionTreeStep,
    DecisionTreeQuestion, FlowchartData, FlowchartNode, FlowchartEdge
)

logger = logging.getLogger(__name__)


class HACCPService:
    """
    Service for handling HACCP business logic
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: ProductCreate, created_by: int) -> Product:
        """Create a new product"""
        
        # Check if product code already exists
        existing_product = self.db.query(Product).filter(
            Product.product_code == product_data.product_code
        ).first()
        
        if existing_product:
            raise ValueError("Product code already exists")
        
        product = Product(
            product_code=product_data.product_code,
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            formulation=product_data.formulation,
            allergens=product_data.allergens,
            shelf_life_days=product_data.shelf_life_days,
            storage_conditions=product_data.storage_conditions,
            packaging_type=product_data.packaging_type,
            created_by=created_by
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def create_process_flow(self, product_id: int, flow_data: ProcessFlowCreate, created_by: int) -> ProcessFlow:
        """Create a process flow step"""
        
        # Verify product exists
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        process_flow = ProcessFlow(
            product_id=product_id,
            step_number=flow_data.step_number,
            step_name=flow_data.step_name,
            description=flow_data.description,
            equipment=flow_data.equipment,
            temperature=flow_data.temperature,
            time_minutes=flow_data.time_minutes,
            ph=flow_data.ph,
            aw=flow_data.aw,
            parameters=flow_data.parameters,
            created_by=created_by
        )
        
        self.db.add(process_flow)
        self.db.commit()
        self.db.refresh(process_flow)
        
        return process_flow
    
    def create_hazard(self, product_id: int, hazard_data: HazardCreate, created_by: int) -> Hazard:
        """Create a hazard with risk assessment"""
        
        # Verify product exists
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Calculate risk score
        likelihood = hazard_data.likelihood
        severity = hazard_data.severity
        risk_score = likelihood * severity
        
        # Determine risk level
        if risk_score <= 4:
            risk_level = RiskLevel.LOW
        elif risk_score <= 8:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 15:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        hazard = Hazard(
            product_id=product_id,
            process_step_id=hazard_data.process_step_id,
            hazard_type=hazard_data.hazard_type,
            hazard_name=hazard_data.hazard_name,
            description=hazard_data.description,
            likelihood=likelihood,
            severity=severity,
            risk_score=risk_score,
            risk_level=risk_level,
            control_measures=hazard_data.control_measures,
            is_controlled=hazard_data.is_controlled,
            control_effectiveness=hazard_data.control_effectiveness,
            is_ccp=hazard_data.is_ccp,
            ccp_justification=hazard_data.ccp_justification,
            created_by=created_by
        )
        
        self.db.add(hazard)
        self.db.commit()
        self.db.refresh(hazard)
        
        return hazard
    
    def run_decision_tree(self, hazard_id: int) -> DecisionTreeResult:
        """
        Run the CCP decision tree for a hazard
        Based on Codex Alimentarius decision tree
        """
        
        hazard = self.db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise ValueError("Hazard not found")
        
        steps = []
        is_ccp = False
        justification = ""
        
        # Question 1: Is control at this step necessary for safety?
        q1_answer = hazard.risk_score >= 8  # High or critical risk
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q1,
            answer=q1_answer,
            explanation=f"Risk score: {hazard.risk_score} (High/Critical risk requires control)"
        ))
        
        if not q1_answer:
            justification = "Control at this step is not necessary for safety"
            return DecisionTreeResult(is_ccp=False, justification=justification, steps=steps)
        
        # Question 2: Is it likely that contamination may occur or increase?
        q2_answer = hazard.likelihood >= 3  # Medium or higher likelihood
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q2,
            answer=q2_answer,
            explanation=f"Likelihood: {hazard.likelihood}/5 (Medium or higher likelihood of contamination)"
        ))
        
        if not q2_answer:
            justification = "Contamination is unlikely to occur or increase at this step"
            return DecisionTreeResult(is_ccp=False, justification=justification, steps=steps)
        
        # Question 3: Will a subsequent step eliminate or reduce the hazard?
        # Check if there are subsequent steps with control measures
        subsequent_steps = self.db.query(ProcessFlow).filter(
            and_(
                ProcessFlow.product_id == hazard.product_id,
                ProcessFlow.step_number > hazard.process_step.step_number
            )
        ).all()
        
        subsequent_hazards = self.db.query(Hazard).filter(
            and_(
                Hazard.product_id == hazard.product_id,
                Hazard.process_step_id.in_([step.id for step in subsequent_steps])
            )
        ).all()
        
        q3_answer = any(h.is_controlled for h in subsequent_hazards)
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q3,
            answer=q3_answer,
            explanation=f"Subsequent control measures: {'Yes' if q3_answer else 'No'}"
        ))
        
        if q3_answer:
            justification = "A subsequent step will eliminate or reduce the hazard to acceptable levels"
            return DecisionTreeResult(is_ccp=False, justification=justification, steps=steps)
        else:
            justification = "No subsequent step will eliminate or reduce the hazard - this is a CCP"
            is_ccp = True
        
        return DecisionTreeResult(is_ccp=is_ccp, justification=justification, steps=steps)
    
    def create_ccp(self, product_id: int, ccp_data: CCPCreate, created_by: int) -> CCP:
        """Create a CCP"""
        
        # Verify product exists
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        ccp = CCP(
            product_id=product_id,
            hazard_id=ccp_data.hazard_id,
            ccp_number=ccp_data.ccp_number,
            ccp_name=ccp_data.ccp_name,
            description=ccp_data.description,
            status=CCPStatus.ACTIVE,
            critical_limit_min=ccp_data.critical_limit_min,
            critical_limit_max=ccp_data.critical_limit_max,
            critical_limit_unit=ccp_data.critical_limit_unit,
            critical_limit_description=ccp_data.critical_limit_description,
            monitoring_frequency=ccp_data.monitoring_frequency,
            monitoring_method=ccp_data.monitoring_method,
            monitoring_responsible=ccp_data.monitoring_responsible,
            monitoring_equipment=ccp_data.monitoring_equipment,
            corrective_actions=ccp_data.corrective_actions,
            verification_frequency=ccp_data.verification_frequency,
            verification_method=ccp_data.verification_method,
            verification_responsible=ccp_data.verification_responsible,
            monitoring_records=ccp_data.monitoring_records,
            verification_records=ccp_data.verification_records,
            created_by=created_by
        )
        
        self.db.add(ccp)
        self.db.commit()
        self.db.refresh(ccp)
        
        return ccp
    
    def create_monitoring_log(self, ccp_id: int, log_data: MonitoringLogCreate, created_by: int) -> Tuple[CCPMonitoringLog, bool]:
        """Create a monitoring log and check for alerts"""
        
        # Verify CCP exists
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Check if within limits
        measured_value = log_data.measured_value
        is_within_limits = True
        
        if ccp.critical_limit_min is not None and measured_value < ccp.critical_limit_min:
            is_within_limits = False
        if ccp.critical_limit_max is not None and measured_value > ccp.critical_limit_max:
            is_within_limits = False
        
        monitoring_log = CCPMonitoringLog(
            ccp_id=ccp_id,
            batch_number=log_data.batch_number,
            monitoring_time=datetime.utcnow(),
            measured_value=measured_value,
            unit=log_data.unit,
            is_within_limits=is_within_limits,
            additional_parameters=log_data.additional_parameters,
            observations=log_data.observations,
            evidence_files=log_data.evidence_files,
            corrective_action_taken=log_data.corrective_action_taken,
            corrective_action_description=log_data.corrective_action_description,
            corrective_action_by=log_data.corrective_action_by,
            created_by=created_by
        )
        
        self.db.add(monitoring_log)
        self.db.commit()
        self.db.refresh(monitoring_log)
        
        # Create alert if out of spec
        alert_created = False
        if not is_within_limits:
            alert_created = self._create_out_of_spec_alert(ccp, monitoring_log)
        
        return monitoring_log, alert_created
    
    def _create_out_of_spec_alert(self, ccp: CCP, monitoring_log: CCPMonitoringLog) -> bool:
        """Create an alert for out-of-spec readings"""
        
        try:
            # Get responsible person
            responsible_user_id = ccp.monitoring_responsible or ccp.created_by
            
            # Create notification
            notification = Notification(
                user_id=responsible_user_id,
                title=f"CCP Out-of-Spec Alert: {ccp.ccp_name}",
                message=f"CCP {ccp.ccp_number} ({ccp.ccp_name}) is out of specification. "
                       f"Batch: {monitoring_log.batch_number}, "
                       f"Value: {monitoring_log.measured_value} {monitoring_log.unit or ''}, "
                       f"Limits: {ccp.critical_limit_min or 'N/A'} - {ccp.critical_limit_max or 'N/A'}",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.HACCP,
                notification_data={
                    "ccp_id": ccp.id,
                    "ccp_number": ccp.ccp_number,
                    "ccp_name": ccp.ccp_name,
                    "batch_number": monitoring_log.batch_number,
                    "measured_value": monitoring_log.measured_value,
                    "unit": monitoring_log.unit,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max,
                    "monitoring_log_id": monitoring_log.id
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.warning(f"Out-of-spec alert created for CCP {ccp.ccp_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create out-of-spec alert: {str(e)}")
            return False
    
    def get_flowchart_data(self, product_id: int) -> FlowchartData:
        """Generate flowchart data for a product"""
        
        # Get process flows
        process_flows = self.db.query(ProcessFlow).filter(
            ProcessFlow.product_id == product_id
        ).order_by(ProcessFlow.step_number).all()
        
        nodes = []
        edges = []
        
        # Add start node
        nodes.append(FlowchartNode(
            id="start",
            type="start",
            label="Start",
            x=100,
            y=50
        ))
        
        # Add process nodes
        for i, flow in enumerate(process_flows):
            node_id = f"step_{flow.id}"
            x = 100 + (i * 200)
            y = 150
            
            nodes.append(FlowchartNode(
                id=node_id,
                type="process",
                label=flow.step_name,
                x=x,
                y=y,
                data={
                    "step_number": flow.step_number,
                    "description": flow.description,
                    "equipment": flow.equipment,
                    "temperature": flow.temperature,
                    "time_minutes": flow.time_minutes,
                    "ph": flow.ph,
                    "aw": flow.aw,
                    "parameters": flow.parameters
                }
            ))
            
            # Add edge from previous node
            if i == 0:
                edges.append(FlowchartEdge(
                    id=f"edge_start_{node_id}",
                    source="start",
                    target=node_id
                ))
            else:
                prev_node_id = f"step_{process_flows[i-1].id}"
                edges.append(FlowchartEdge(
                    id=f"edge_{prev_node_id}_{node_id}",
                    source=prev_node_id,
                    target=node_id
                ))
        
        # Add end node
        if process_flows:
            last_node_id = f"step_{process_flows[-1].id}"
            nodes.append(FlowchartNode(
                id="end",
                type="end",
                label="End",
                x=100 + (len(process_flows) * 200),
                y=250
            ))
            edges.append(FlowchartEdge(
                id=f"edge_{last_node_id}_end",
                source=last_node_id,
                target="end"
            ))
        
        return FlowchartData(nodes=nodes, edges=edges)
    
    def get_haccp_dashboard_stats(self) -> Dict[str, Any]:
        """Get HACCP dashboard statistics"""
        
        # Get total products
        total_products = self.db.query(Product).count()
        
        # Get approved HACCP plans
        approved_plans = self.db.query(Product).filter(Product.haccp_plan_approved == True).count()
        
        # Get total CCPs
        total_ccps = self.db.query(CCP).count()
        
        # Get active CCPs
        active_ccps = self.db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).count()
        
        # Get recent monitoring logs
        recent_logs = self.db.query(CCPMonitoringLog).order_by(
            desc(CCPMonitoringLog.monitoring_time)
        ).limit(5).all()
        
        # Get out-of-spec incidents
        out_of_spec_count = self.db.query(CCPMonitoringLog).filter(
            CCPMonitoringLog.is_within_limits == False
        ).count()
        
        # Get recent alerts
        recent_alerts = self.db.query(CCPMonitoringLog).filter(
            and_(
                CCPMonitoringLog.is_within_limits == False,
                CCPMonitoringLog.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).count()
        
        return {
            "total_products": total_products,
            "approved_plans": approved_plans,
            "total_ccps": total_ccps,
            "active_ccps": active_ccps,
            "out_of_spec_count": out_of_spec_count,
            "recent_alerts": recent_alerts,
            "recent_logs": [
                {
                    "id": log.id,
                    "ccp_name": log.ccp.ccp_name,
                    "batch_number": log.batch_number,
                    "measured_value": log.measured_value,
                    "unit": log.unit,
                    "is_within_limits": log.is_within_limits,
                    "monitoring_time": log.monitoring_time.isoformat() if log.monitoring_time else None,
                } for log in recent_logs
            ]
        }
    
    def generate_haccp_report(self, product_id: int, report_type: str, 
                            date_from: Optional[datetime] = None,
                            date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate HACCP report data"""
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Get process flows
        process_flows = self.db.query(ProcessFlow).filter(
            ProcessFlow.product_id == product_id
        ).order_by(ProcessFlow.step_number).all()
        
        # Get hazards
        hazards = self.db.query(Hazard).filter(
            Hazard.product_id == product_id
        ).all()
        
        # Get CCPs
        ccps = self.db.query(CCP).filter(
            CCP.product_id == product_id
        ).all()
        
        # Get monitoring logs if date range specified
        monitoring_logs = []
        if date_from and date_to:
            monitoring_logs = self.db.query(CCPMonitoringLog).filter(
                and_(
                    CCPMonitoringLog.ccp_id.in_([ccp.id for ccp in ccps]),
                    CCPMonitoringLog.monitoring_time >= date_from,
                    CCPMonitoringLog.monitoring_time <= date_to
                )
            ).order_by(desc(CCPMonitoringLog.monitoring_time)).all()
        
        report_data = {
            "product": {
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "category": product.category,
                "haccp_plan_approved": product.haccp_plan_approved,
                "haccp_plan_version": product.haccp_plan_version,
            },
            "process_flows": [
                {
                    "step_number": flow.step_number,
                    "step_name": flow.step_name,
                    "description": flow.description,
                    "equipment": flow.equipment,
                    "temperature": flow.temperature,
                    "time_minutes": flow.time_minutes,
                    "ph": flow.ph,
                    "aw": flow.aw,
                } for flow in process_flows
            ],
            "hazards": [
                {
                    "hazard_name": hazard.hazard_name,
                    "hazard_type": hazard.hazard_type.value,
                    "risk_score": hazard.risk_score,
                    "risk_level": hazard.risk_level.value,
                    "is_ccp": hazard.is_ccp,
                } for hazard in hazards
            ],
            "ccps": [
                {
                    "ccp_number": ccp.ccp_number,
                    "ccp_name": ccp.ccp_name,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max,
                    "critical_limit_unit": ccp.critical_limit_unit,
                    "monitoring_frequency": ccp.monitoring_frequency,
                    "corrective_actions": ccp.corrective_actions,
                } for ccp in ccps
            ],
            "monitoring_summary": {
                "total_logs": len(monitoring_logs),
                "in_spec_count": len([log for log in monitoring_logs if log.is_within_limits]),
                "out_of_spec_count": len([log for log in monitoring_logs if not log.is_within_limits]),
            },
            "generated_at": datetime.utcnow().isoformat(),
            "report_type": report_type,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            }
        }
        
        return report_data 