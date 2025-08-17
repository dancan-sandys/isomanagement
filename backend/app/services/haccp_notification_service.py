"""
HACCP Notification and Dashboard Service with Smart Alerts
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case
from enum import Enum

from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.models.equipment import Equipment
from app.services.haccp_service import HACCPValidationError, HACCPBusinessError

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HACCPNotificationService:
    """
    Comprehensive HACCP notification service with smart alerts and dashboard features
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_smart_alerts(self, user_id: int) -> Dict[str, Any]:
        """
        Generate smart alerts based on HACCP system status
        
        Args:
            user_id: ID of the user requesting alerts
            
        Returns:
            Dictionary with categorized alerts
        """
        try:
            alerts = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "summary": {
                    "total_alerts": 0,
                    "critical_count": 0,
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0
                }
            }
            
            # Check for overdue monitoring
            overdue_monitoring = self._check_overdue_monitoring()
            for alert in overdue_monitoring:
                if alert["severity"] == AlertSeverity.CRITICAL.value:
                    alerts["critical"].append(alert)
                elif alert["severity"] == AlertSeverity.HIGH.value:
                    alerts["high"].append(alert)
                else:
                    alerts["medium"].append(alert)
            
            # Check for CCP deviations
            ccp_deviations = self._check_ccp_deviations()
            for alert in ccp_deviations:
                alerts["critical"].append(alert)
            
            # Check for high-risk hazards
            high_risk_hazards = self._check_high_risk_hazards()
            for alert in high_risk_hazards:
                alerts["high"].append(alert)
            
            # Check for equipment calibration issues
            calibration_issues = self._check_calibration_issues()
            for alert in calibration_issues:
                alerts["medium"].append(alert)
            
            # Check for verification overdue
            verification_overdue = self._check_verification_overdue()
            for alert in verification_overdue:
                alerts["medium"].append(alert)
            
            # Check for training requirements
            training_alerts = self._check_training_requirements()
            for alert in training_alerts:
                alerts["low"].append(alert)
            
            # Update summary
            alerts["summary"]["critical_count"] = len(alerts["critical"])
            alerts["summary"]["high_count"] = len(alerts["high"])
            alerts["summary"]["medium_count"] = len(alerts["medium"])
            alerts["summary"]["low_count"] = len(alerts["low"])
            alerts["summary"]["total_alerts"] = sum([
                alerts["summary"]["critical_count"],
                alerts["summary"]["high_count"],
                alerts["summary"]["medium_count"],
                alerts["summary"]["low_count"]
            ])
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating smart alerts: {e}")
            raise HACCPBusinessError(f"Failed to generate smart alerts: {str(e)}")
    
    def get_comprehensive_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive HACCP dashboard data
        
        Args:
            user_id: ID of the user requesting dashboard
            
        Returns:
            Dictionary with comprehensive dashboard data
        """
        try:
            dashboard_data = {
                "overview": self._get_overview_metrics(),
                "compliance": self._get_compliance_metrics(),
                "risk_analysis": self._get_risk_analysis(),
                "monitoring_status": self._get_monitoring_status(),
                "verification_status": self._get_verification_status(),
                "equipment_status": self._get_equipment_status(),
                "recent_activities": self._get_recent_activities(),
                "upcoming_tasks": self._get_upcoming_tasks(),
                "alerts": self.generate_smart_alerts(user_id)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard: {e}")
            raise HACCPBusinessError(f"Failed to get comprehensive dashboard: {str(e)}")
    
    def send_targeted_notifications(self, alert_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Send targeted notifications based on alert data
        
        Args:
            alert_data: Alert data from smart alerts
            user_id: ID of the user who triggered the notifications
            
        Returns:
            Dictionary with notification results
        """
        try:
            notification_results = {
                "notifications_sent": 0,
                "users_notified": 0,
                "details": []
            }
            
            # Get user roles for targeted notifications
            user_roles = self._get_user_roles_for_notifications()
            
            # Send notifications for critical alerts
            for alert in alert_data.get("critical", []):
                users_to_notify = self._get_users_for_alert(alert, user_roles)
                for user in users_to_notify:
                    self._send_alert_notification(user.id, alert, user_id)
                    notification_results["notifications_sent"] += 1
                notification_results["users_notified"] += len(users_to_notify)
                notification_results["details"].append({
                    "alert_type": alert["type"],
                    "users_notified": len(users_to_notify),
                    "severity": "critical"
                })
            
            # Send notifications for high alerts
            for alert in alert_data.get("high", []):
                users_to_notify = self._get_users_for_alert(alert, user_roles)
                for user in users_to_notify:
                    self._send_alert_notification(user.id, alert, user_id)
                    notification_results["notifications_sent"] += 1
                notification_results["users_notified"] += len(users_to_notify)
                notification_results["details"].append({
                    "alert_type": alert["type"],
                    "users_notified": len(users_to_notify),
                    "severity": "high"
                })
            
            return notification_results
            
        except Exception as e:
            logger.error(f"Error sending targeted notifications: {e}")
            raise HACCPBusinessError(f"Failed to send targeted notifications: {str(e)}")
    
    def _check_overdue_monitoring(self) -> List[Dict[str, Any]]:
        """Check for overdue CCP monitoring"""
        alerts = []
        
        try:
            # Get CCPs with monitoring schedules
            ccps = self.db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).all()
            
            for ccp in ccps:
                # Get latest monitoring log
                latest_log = self.db.query(CCPMonitoringLog).filter(
                    CCPMonitoringLog.ccp_id == ccp.id
                ).order_by(desc(CCPMonitoringLog.monitoring_timestamp)).first()
                
                if not latest_log:
                    # No monitoring logs - check if CCP is due
                    alerts.append({
                        "type": "overdue_monitoring",
                        "severity": AlertSeverity.CRITICAL.value,
                        "title": f"No monitoring records for CCP: {ccp.ccp_name}",
                        "message": f"CCP '{ccp.ccp_name}' has no monitoring records",
                        "ccp_id": ccp.id,
                        "ccp_name": ccp.ccp_name,
                        "product_id": ccp.product_id,
                        "days_overdue": None,
                        "requires_immediate_action": True
                    })
                    continue
                
                # Calculate if monitoring is overdue based on frequency
                days_since_last = (datetime.utcnow() - latest_log.monitoring_timestamp).days
                frequency_days = self._get_frequency_days(ccp.monitoring_frequency)
                
                if days_since_last > frequency_days:
                    severity = AlertSeverity.CRITICAL if days_since_last > frequency_days * 2 else AlertSeverity.HIGH
                    alerts.append({
                        "type": "overdue_monitoring",
                        "severity": severity.value,
                        "title": f"Overdue monitoring for CCP: {ccp.ccp_name}",
                        "message": f"CCP '{ccp.ccp_name}' monitoring is {days_since_last - frequency_days} days overdue",
                        "ccp_id": ccp.id,
                        "ccp_name": ccp.ccp_name,
                        "product_id": ccp.product_id,
                        "days_overdue": days_since_last - frequency_days,
                        "requires_immediate_action": severity == AlertSeverity.CRITICAL
                    })
            
        except Exception as e:
            logger.error(f"Error checking overdue monitoring: {e}")
        
        return alerts
    
    def _check_ccp_deviations(self) -> List[Dict[str, Any]]:
        """Check for CCP deviations"""
        alerts = []
        
        try:
            # Get recent monitoring logs with deviations
            recent_logs = self.db.query(CCPMonitoringLog).filter(
                and_(
                    CCPMonitoringLog.is_within_limits == False,
                    CCPMonitoringLog.monitoring_timestamp >= datetime.utcnow() - timedelta(days=7)
                )
            ).all()
            
            for log in recent_logs:
                ccp = self.db.query(CCP).filter(CCP.id == log.ccp_id).first()
                if ccp:
                    alerts.append({
                        "type": "ccp_deviation",
                        "severity": AlertSeverity.CRITICAL.value,
                        "title": f"CCP Deviation Detected: {ccp.ccp_name}",
                        "message": f"CCP '{ccp.ccp_name}' monitoring value {log.measured_value} {log.unit} is outside limits",
                        "ccp_id": ccp.id,
                        "ccp_name": ccp.ccp_name,
                        "product_id": ccp.product_id,
                        "monitoring_log_id": log.id,
                        "deviation_value": log.measured_value,
                        "deviation_unit": log.unit,
                        "requires_immediate_action": True
                    })
            
        except Exception as e:
            logger.error(f"Error checking CCP deviations: {e}")
        
        return alerts
    
    def _check_high_risk_hazards(self) -> List[Dict[str, Any]]:
        """Check for high-risk hazards"""
        alerts = []
        
        try:
            # Get high and critical risk hazards
            high_risk_hazards = self.db.query(Hazard).filter(
                Hazard.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
            ).all()
            
            for hazard in high_risk_hazards:
                product = self.db.query(Product).filter(Product.id == hazard.product_id).first()
                if product:
                    alerts.append({
                        "type": "high_risk_hazard",
                        "severity": AlertSeverity.HIGH.value,
                        "title": f"High Risk Hazard: {hazard.hazard_name}",
                        "message": f"Hazard '{hazard.hazard_name}' in product '{product.name}' has {hazard.risk_level.value} risk level",
                        "hazard_id": hazard.id,
                        "hazard_name": hazard.hazard_name,
                        "product_id": hazard.product_id,
                        "product_name": product.name,
                        "risk_level": hazard.risk_level.value,
                        "risk_score": hazard.risk_score,
                        "requires_immediate_action": False
                    })
            
        except Exception as e:
            logger.error(f"Error checking high risk hazards: {e}")
        
        return alerts
    
    def _check_calibration_issues(self) -> List[Dict[str, Any]]:
        """Check for equipment calibration issues"""
        alerts = []
        
        try:
            # This would integrate with the EquipmentCalibrationService
            # For now, return empty list
            pass
            
        except Exception as e:
            logger.error(f"Error checking calibration issues: {e}")
        
        return alerts
    
    def _check_verification_overdue(self) -> List[Dict[str, Any]]:
        """Check for overdue verification"""
        alerts = []
        
        try:
            # Get CCPs with verification requirements
            ccps = self.db.query(CCP).filter(
                and_(
                    CCP.status == CCPStatus.ACTIVE,
                    CCP.verification_frequency.isnot(None)
                )
            ).all()
            
            for ccp in ccps:
                # Get latest verification log
                latest_verification = self.db.query(CCPVerificationLog).filter(
                    CCPVerificationLog.ccp_id == ccp.id
                ).order_by(desc(CCPVerificationLog.verification_timestamp)).first()
                
                if not latest_verification:
                    alerts.append({
                        "type": "overdue_verification",
                        "severity": AlertSeverity.MEDIUM.value,
                        "title": f"No verification records for CCP: {ccp.ccp_name}",
                        "message": f"CCP '{ccp.ccp_name}' has no verification records",
                        "ccp_id": ccp.id,
                        "ccp_name": ccp.ccp_name,
                        "product_id": ccp.product_id,
                        "requires_immediate_action": False
                    })
                    continue
                
                # Calculate if verification is overdue
                days_since_last = (datetime.utcnow() - latest_verification.verification_timestamp).days
                frequency_days = self._get_frequency_days(ccp.verification_frequency)
                
                if days_since_last > frequency_days:
                    alerts.append({
                        "type": "overdue_verification",
                        "severity": AlertSeverity.MEDIUM.value,
                        "title": f"Overdue verification for CCP: {ccp.ccp_name}",
                        "message": f"CCP '{ccp.ccp_name}' verification is {days_since_last - frequency_days} days overdue",
                        "ccp_id": ccp.id,
                        "ccp_name": ccp.ccp_name,
                        "product_id": ccp.product_id,
                        "days_overdue": days_since_last - frequency_days,
                        "requires_immediate_action": False
                    })
            
        except Exception as e:
            logger.error(f"Error checking overdue verification: {e}")
        
        return alerts
    
    def _check_training_requirements(self) -> List[Dict[str, Any]]:
        """Check for training requirements"""
        alerts = []
        
        try:
            # This would integrate with the training service
            # For now, return empty list
            pass
            
        except Exception as e:
            logger.error(f"Error checking training requirements: {e}")
        
        return alerts
    
    def _get_overview_metrics(self) -> Dict[str, Any]:
        """Get overview metrics for dashboard"""
        try:
            total_products = self.db.query(Product).count()
            total_hazards = self.db.query(Hazard).count()
            total_ccps = self.db.query(CCP).count()
            active_ccps = self.db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).count()
            
            # Get recent monitoring logs
            recent_monitoring = self.db.query(CCPMonitoringLog).filter(
                CCPMonitoringLog.monitoring_timestamp >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Get compliance rate
            total_monitoring = self.db.query(CCPMonitoringLog).count()
            compliant_monitoring = self.db.query(CCPMonitoringLog).filter(
                CCPMonitoringLog.is_within_limits == True
            ).count()
            
            compliance_rate = (compliant_monitoring / total_monitoring * 100) if total_monitoring > 0 else 100
            
            return {
                "total_products": total_products,
                "total_hazards": total_hazards,
                "total_ccps": total_ccps,
                "active_ccps": active_ccps,
                "recent_monitoring_logs": recent_monitoring,
                "compliance_rate": round(compliance_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting overview metrics: {e}")
            return {}
    
    def _get_compliance_metrics(self) -> Dict[str, Any]:
        """Get compliance metrics"""
        try:
            # Calculate compliance by CCP
            ccp_compliance = []
            ccps = self.db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).all()
            
            for ccp in ccps:
                total_logs = self.db.query(CCPMonitoringLog).filter(CCPMonitoringLog.ccp_id == ccp.id).count()
                compliant_logs = self.db.query(CCPMonitoringLog).filter(
                    and_(
                        CCPMonitoringLog.ccp_id == ccp.id,
                        CCPMonitoringLog.is_within_limits == True
                    )
                ).count()
                
                compliance_rate = (compliant_logs / total_logs * 100) if total_logs > 0 else 100
                
                ccp_compliance.append({
                    "ccp_id": ccp.id,
                    "ccp_name": ccp.ccp_name,
                    "compliance_rate": round(compliance_rate, 2),
                    "total_logs": total_logs,
                    "compliant_logs": compliant_logs
                })
            
            return {
                "ccp_compliance": ccp_compliance,
                "overall_compliance": round(sum(c["compliance_rate"] for c in ccp_compliance) / len(ccp_compliance), 2) if ccp_compliance else 100
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance metrics: {e}")
            return {}
    
    def _get_risk_analysis(self) -> Dict[str, Any]:
        """Get risk analysis data"""
        try:
            # Risk distribution by level
            risk_distribution = self.db.query(
                Hazard.risk_level,
                func.count(Hazard.id).label('count')
            ).group_by(Hazard.risk_level).all()
            
            # Risk by product
            product_risk = self.db.query(
                Product.name,
                func.avg(Hazard.risk_score).label('avg_risk'),
                func.count(Hazard.id).label('hazard_count')
            ).join(Hazard).group_by(Product.id, Product.name).all()
            
            return {
                "risk_distribution": [{"level": r.risk_level.value, "count": r.count} for r in risk_distribution],
                "product_risk": [{"product": p.name, "avg_risk": round(p.avg_risk, 2), "hazard_count": p.hazard_count} for p in product_risk]
            }
            
        except Exception as e:
            logger.error(f"Error getting risk analysis: {e}")
            return {}
    
    def _get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        try:
            # Recent monitoring activity
            recent_activity = self.db.query(
                CCP.ccp_name,
                func.count(CCPMonitoringLog.id).label('log_count')
            ).join(CCPMonitoringLog).filter(
                CCPMonitoringLog.monitoring_timestamp >= datetime.utcnow() - timedelta(days=7)
            ).group_by(CCP.id, CCP.ccp_name).all()
            
            return {
                "recent_activity": [{"ccp_name": r.ccp_name, "log_count": r.log_count} for r in recent_activity]
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {}
    
    def _get_verification_status(self) -> Dict[str, Any]:
        """Get verification status"""
        try:
            # Recent verification activity
            recent_verification = self.db.query(
                CCP.ccp_name,
                func.count(CCPVerificationLog.id).label('verification_count')
            ).join(CCPVerificationLog).filter(
                CCPVerificationLog.verification_timestamp >= datetime.utcnow() - timedelta(days=30)
            ).group_by(CCP.id, CCP.ccp_name).all()
            
            return {
                "recent_verification": [{"ccp_name": r.ccp_name, "verification_count": r.verification_count} for r in recent_verification]
            }
            
        except Exception as e:
            logger.error(f"Error getting verification status: {e}")
            return {}
    
    def _get_equipment_status(self) -> Dict[str, Any]:
        """Get equipment status"""
        try:
            # This would integrate with equipment service
            return {}
            
        except Exception as e:
            logger.error(f"Error getting equipment status: {e}")
            return {}
    
    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent HACCP activities"""
        try:
            activities = []
            
            # Recent monitoring logs
            recent_monitoring = self.db.query(CCPMonitoringLog).order_by(
                desc(CCPMonitoringLog.monitoring_timestamp)
            ).limit(10).all()
            
            for log in recent_monitoring:
                ccp = self.db.query(CCP).filter(CCP.id == log.ccp_id).first()
                if ccp:
                    activities.append({
                        "type": "monitoring",
                        "timestamp": log.monitoring_timestamp,
                        "ccp_name": ccp.ccp_name,
                        "description": f"Monitoring log recorded for {ccp.ccp_name}",
                        "status": "within_limits" if log.is_within_limits else "deviation"
                    })
            
            # Recent verification logs
            recent_verification = self.db.query(CCPVerificationLog).order_by(
                desc(CCPVerificationLog.verification_timestamp)
            ).limit(10).all()
            
            for log in recent_verification:
                ccp = self.db.query(CCP).filter(CCP.id == log.ccp_id).first()
                if ccp:
                    activities.append({
                        "type": "verification",
                        "timestamp": log.verification_timestamp,
                        "ccp_name": ccp.ccp_name,
                        "description": f"Verification completed for {ccp.ccp_name}",
                        "status": log.verification_result
                    })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return activities[:20]  # Return top 20 activities
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            return []
    
    def _get_upcoming_tasks(self) -> List[Dict[str, Any]]:
        """Get upcoming HACCP tasks"""
        try:
            tasks = []
            
            # Upcoming monitoring tasks
            ccps = self.db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).all()
            
            for ccp in ccps:
                latest_log = self.db.query(CCPMonitoringLog).filter(
                    CCPMonitoringLog.ccp_id == ccp.id
                ).order_by(desc(CCPMonitoringLog.monitoring_timestamp)).first()
                
                if latest_log:
                    frequency_days = self._get_frequency_days(ccp.monitoring_frequency)
                    next_monitoring = latest_log.monitoring_timestamp + timedelta(days=frequency_days)
                    
                    if next_monitoring <= datetime.utcnow() + timedelta(days=7):
                        tasks.append({
                            "type": "monitoring",
                            "ccp_name": ccp.ccp_name,
                            "due_date": next_monitoring,
                            "priority": "high" if next_monitoring <= datetime.utcnow() else "medium"
                        })
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting upcoming tasks: {e}")
            return []
    
    def _get_frequency_days(self, frequency: str) -> int:
        """Convert frequency string to days"""
        frequency_map = {
            "hourly": 1,
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90,
            "annually": 365
        }
        return frequency_map.get(frequency, 30)
    
    def _get_user_roles_for_notifications(self) -> Dict[str, List[str]]:
        """Get user roles for targeted notifications"""
        return {
            "critical": ["HACCP Team", "Quality Manager", "Plant Manager"],
            "high": ["HACCP Team", "Quality Manager"],
            "medium": ["HACCP Team"],
            "low": ["HACCP Team"]
        }
    
    def _get_users_for_alert(self, alert: Dict[str, Any], user_roles: Dict[str, List[str]]) -> List[User]:
        """Get users to notify for a specific alert"""
        try:
            severity = alert.get("severity", "medium")
            roles_to_notify = user_roles.get(severity, ["HACCP Team"])
            
            users = self.db.query(User).filter(
                User.role.has(name=roles_to_notify)
            ).all()
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting users for alert: {e}")
            return []
    
    def _send_alert_notification(self, user_id: int, alert: Dict[str, Any], triggered_by: int) -> None:
        """Send notification for an alert"""
        try:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.ALERT if alert["severity"] in ["critical", "high"] else NotificationType.REMINDER,
                priority=NotificationPriority.HIGH if alert["severity"] == "critical" else NotificationPriority.MEDIUM,
                category=NotificationCategory.HACCP,
                title=alert["title"],
                message=alert["message"],
                data={
                    "alert_type": alert["type"],
                    "severity": alert["severity"],
                    "triggered_by": triggered_by,
                    "requires_action": alert.get("requires_immediate_action", False)
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
