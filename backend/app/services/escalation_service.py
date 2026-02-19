from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.nonconformance import (
    EscalationRule, RiskAssessment, NonConformance
)
from app.schemas.nonconformance import (
    EscalationRuleCreate, EscalationRuleUpdate, EscalationRuleFilter,
    EscalationRuleTriggerRequest
)


class EscalationService:
    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations
    def create_escalation_rule(self, rule_data: EscalationRuleCreate, created_by: int) -> EscalationRule:
        """Create a new escalation rule"""
        escalation_rule = EscalationRule(
            **rule_data.dict(),
            created_by=created_by
        )
        self.db.add(escalation_rule)
        self.db.commit()
        self.db.refresh(escalation_rule)
        return escalation_rule

    def get_escalation_rules(self, filter_params: EscalationRuleFilter) -> Dict[str, Any]:
        """Get escalation rules with filtering and pagination"""
        query = self.db.query(EscalationRule)

        # Apply filters
        if filter_params.trigger_condition:
            query = query.filter(EscalationRule.trigger_condition == filter_params.trigger_condition)

        if filter_params.escalation_level:
            query = query.filter(EscalationRule.escalation_level == filter_params.escalation_level)

        if filter_params.is_active is not None:
            query = query.filter(EscalationRule.is_active == filter_params.is_active)

        if filter_params.created_by:
            query = query.filter(EscalationRule.created_by == filter_params.created_by)

        # Count total
        total = query.count()

        # Apply pagination
        offset = (filter_params.page - 1) * filter_params.size
        escalation_rules = query.offset(offset).limit(filter_params.size).all()

        return {
            "items": escalation_rules,
            "total": total,
            "page": filter_params.page,
            "size": filter_params.size,
            "pages": (total + filter_params.size - 1) // filter_params.size
        }

    def get_escalation_rule(self, rule_id: int) -> Optional[EscalationRule]:
        """Get escalation rule by ID"""
        return self.db.query(EscalationRule).filter(EscalationRule.id == rule_id).first()

    def update_escalation_rule(self, rule_id: int, rule_data: EscalationRuleUpdate, updated_by: int) -> Optional[EscalationRule]:
        """Update escalation rule"""
        escalation_rule = self.get_escalation_rule(rule_id)
        if not escalation_rule:
            return None

        update_data = rule_data.dict(exclude_unset=True)
        update_data['updated_by'] = updated_by
        update_data['updated_at'] = datetime.now()

        for field, value in update_data.items():
            setattr(escalation_rule, field, value)

        self.db.commit()
        self.db.refresh(escalation_rule)
        return escalation_rule

    def delete_escalation_rule(self, rule_id: int) -> bool:
        """Delete escalation rule"""
        escalation_rule = self.get_escalation_rule(rule_id)
        if not escalation_rule:
            return False

        self.db.delete(escalation_rule)
        self.db.commit()
        return True

    def activate_escalation_rule(self, rule_id: int, updated_by: int) -> Optional[EscalationRule]:
        """Activate an escalation rule"""
        escalation_rule = self.get_escalation_rule(rule_id)
        if not escalation_rule:
            return None

        escalation_rule.is_active = True
        escalation_rule.updated_by = updated_by
        escalation_rule.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(escalation_rule)
        return escalation_rule

    def deactivate_escalation_rule(self, rule_id: int, updated_by: int) -> Optional[EscalationRule]:
        """Deactivate an escalation rule"""
        escalation_rule = self.get_escalation_rule(rule_id)
        if not escalation_rule:
            return None

        escalation_rule.is_active = False
        escalation_rule.updated_by = updated_by
        escalation_rule.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(escalation_rule)
        return escalation_rule

    # Escalation Logic
    def trigger_escalation_rule(self, trigger_request: EscalationRuleTriggerRequest) -> Dict[str, Any]:
        """Trigger an escalation rule"""
        rule = self.get_escalation_rule(trigger_request.rule_id)
        if not rule:
            return {"error": "Escalation rule not found"}

        if not rule.is_active:
            return {"error": "Escalation rule is not active"}

        if rule.should_trigger(trigger_request.trigger_value):
            # Execute escalation logic
            escalation_result = self._execute_escalation(rule, trigger_request)
            return {
                "triggered": True,
                "rule_name": rule.rule_name,
                "escalation_level": rule.escalation_level,
                "result": escalation_result
            }
        else:
            return {
                "triggered": False,
                "rule_name": rule.rule_name,
                "reason": f"Trigger value {trigger_request.trigger_value} does not meet threshold {rule.trigger_value}"
            }

    def _execute_escalation(self, rule: EscalationRule, trigger_request: EscalationRuleTriggerRequest) -> Dict[str, Any]:
        """Execute the escalation logic"""
        # Get notification recipients
        recipients = rule.get_notification_recipients()
        
        # Create escalation notification
        notification_data = {
            "escalation_level": rule.escalation_level,
            "rule_name": rule.rule_name,
            "trigger_value": trigger_request.trigger_value,
            "recipients": recipients,
            "timeframe": rule.escalation_timeframe,
            "context_data": trigger_request.context_data
        }
        
        # Here you would implement the actual notification logic
        # For now, we'll just return the notification data
        return {
            "notification_sent": True,
            "recipients_count": len(recipients),
            "escalation_level": rule.escalation_level,
            "timeframe_hours": rule.escalation_timeframe
        }

    def check_escalation_triggers(self, nc_id: int) -> List[Dict[str, Any]]:
        """Check all escalation triggers for a non-conformance"""
        non_conformance = self.db.query(NonConformance).filter(NonConformance.id == nc_id).first()
        if not non_conformance:
            return []

        risk_assessment = self.db.query(RiskAssessment).filter(
            RiskAssessment.non_conformance_id == nc_id
        ).order_by(RiskAssessment.created_at.desc()).first()

        triggered_rules = []
        active_rules = self.db.query(EscalationRule).filter(EscalationRule.is_active == True).all()

        for rule in active_rules:
            trigger_value = None
            
            if rule.trigger_condition == "risk_score" and risk_assessment:
                trigger_value = risk_assessment.overall_risk_score
            elif rule.trigger_condition == "severity_level":
                severity_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                trigger_value = severity_scores.get(non_conformance.severity.lower(), 0)
            elif rule.trigger_condition == "time_delay":
                # Calculate time since non-conformance was reported
                time_delta = datetime.now() - non_conformance.reported_date
                trigger_value = time_delta.total_seconds() / 3600  # Convert to hours

            if trigger_value is not None and rule.should_trigger(trigger_value):
                triggered_rules.append({
                    "rule_id": rule.id,
                    "rule_name": rule.rule_name,
                    "trigger_condition": rule.trigger_condition,
                    "trigger_value": trigger_value,
                    "escalation_level": rule.escalation_level,
                    "timeframe": rule.escalation_timeframe
                })

        return triggered_rules

    # Business Logic Methods
    def get_active_escalation_rules(self) -> List[EscalationRule]:
        """Get all active escalation rules"""
        return self.db.query(EscalationRule).filter(EscalationRule.is_active == True).all()

    def get_escalation_rules_by_level(self, escalation_level: str) -> List[EscalationRule]:
        """Get escalation rules by escalation level"""
        return self.db.query(EscalationRule).filter(
            EscalationRule.escalation_level == escalation_level
        ).all()

    def get_escalation_rules_by_condition(self, trigger_condition: str) -> List[EscalationRule]:
        """Get escalation rules by trigger condition"""
        return self.db.query(EscalationRule).filter(
            EscalationRule.trigger_condition == trigger_condition
        ).all()

    def get_escalation_statistics(self) -> Dict[str, Any]:
        """Get escalation rule statistics"""
        total_rules = self.db.query(EscalationRule).count()
        active_rules = self.db.query(EscalationRule).filter(EscalationRule.is_active == True).count()
        
        # Rules by escalation level
        levels = ['supervisor', 'manager', 'director', 'executive']
        rules_by_level = {}
        for level in levels:
            count = self.db.query(EscalationRule).filter(EscalationRule.escalation_level == level).count()
            rules_by_level[level] = count
        
        # Rules by trigger condition
        conditions = ['risk_score', 'time_delay', 'severity_level']
        rules_by_condition = {}
        for condition in conditions:
            count = self.db.query(EscalationRule).filter(EscalationRule.trigger_condition == condition).count()
            rules_by_condition[condition] = count
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "inactive_rules": total_rules - active_rules,
            "rules_by_level": rules_by_level,
            "rules_by_condition": rules_by_condition
        }

    def validate_escalation_rule(self, rule_data: EscalationRuleCreate) -> Dict[str, Any]:
        """Validate escalation rule data and provide recommendations"""
        recommendations = []
        warnings = []
        
        # Check for conflicting rules
        conflicting_rules = self.db.query(EscalationRule).filter(
            and_(
                EscalationRule.trigger_condition == rule_data.trigger_condition,
                EscalationRule.escalation_level == rule_data.escalation_level,
                EscalationRule.is_active == True
            )
        ).all()
        
        if conflicting_rules:
            warnings.append(f"Found {len(conflicting_rules)} conflicting active rules with same condition and level")
        
        # Check trigger value ranges
        if rule_data.trigger_condition == "risk_score" and rule_data.trigger_value > 4.0:
            warnings.append("Risk score trigger value exceeds maximum possible score (4.0)")
        
        if rule_data.trigger_condition == "severity_level" and rule_data.trigger_value > 4:
            warnings.append("Severity level trigger value exceeds maximum level (4)")
        
        # Check notification recipients
        if rule_data.notification_recipients:
            try:
                recipients = json.loads(rule_data.notification_recipients)
                if not isinstance(recipients, list):
                    warnings.append("Notification recipients should be a JSON array")
                elif len(recipients) == 0:
                    warnings.append("No notification recipients specified")
            except json.JSONDecodeError:
                warnings.append("Invalid JSON format for notification recipients")
        
        # Check escalation timeframe
        if rule_data.escalation_timeframe and rule_data.escalation_timeframe < 1:
            warnings.append("Escalation timeframe should be at least 1 hour")
        
        return {
            "is_valid": len(warnings) == 0,
            "recommendations": recommendations,
            "warnings": warnings,
            "conflicting_rules_count": len(conflicting_rules)
        }

    def get_escalation_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get escalation history (this would typically come from a separate escalation log table)"""
        # For now, we'll return a placeholder
        # In a real implementation, you would have an escalation log table
        return []

    def bulk_update_escalation_rules(self, rule_ids: List[int], update_data: Dict[str, Any], updated_by: int) -> Dict[str, Any]:
        """Bulk update escalation rules"""
        rules = self.db.query(EscalationRule).filter(EscalationRule.id.in_(rule_ids)).all()
        
        updated_count = 0
        for rule in rules:
            for field, value in update_data.items():
                if hasattr(rule, field):
                    setattr(rule, field, value)
            rule.updated_by = updated_by
            rule.updated_at = datetime.now()
            updated_count += 1
        
        self.db.commit()
        
        return {
            "total_requested": len(rule_ids),
            "updated_count": updated_count
        }

    def get_escalation_rule_templates(self) -> List[Dict[str, Any]]:
        """Get predefined escalation rule templates"""
        templates = [
            {
                "name": "High Risk Score Escalation",
                "description": "Escalate when risk score is high or critical",
                "trigger_condition": "risk_score",
                "trigger_value": 3.0,
                "escalation_level": "manager",
                "escalation_timeframe": 24
            },
            {
                "name": "Critical Severity Escalation",
                "description": "Escalate critical severity non-conformances immediately",
                "trigger_condition": "severity_level",
                "trigger_value": 4,
                "escalation_level": "executive",
                "escalation_timeframe": 2
            },
            {
                "name": "Delayed Resolution Escalation",
                "description": "Escalate non-conformances that haven't been resolved within timeframe",
                "trigger_condition": "time_delay",
                "trigger_value": 168,  # 7 days in hours
                "escalation_level": "director",
                "escalation_timeframe": 24
            }
        ]
        
        return templates

    def create_escalation_rule_from_template(self, template_name: str, created_by: int) -> Optional[EscalationRule]:
        """Create escalation rule from a template"""
        templates = self.get_escalation_rule_templates()
        
        template = next((t for t in templates if t["name"] == template_name), None)
        if not template:
            return None
        
        rule_data = EscalationRuleCreate(
            rule_name=template["name"],
            rule_description=template["description"],
            trigger_condition=template["trigger_condition"],
            trigger_value=template["trigger_value"],
            escalation_level=template["escalation_level"],
            escalation_timeframe=template["escalation_timeframe"],
            is_active=True
        )
        
        return self.create_escalation_rule(rule_data, created_by)

