"""
Equipment Calibration Enforcement Service for HACCP Compliance
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from enum import Enum

from app.models.equipment import Equipment, CalibrationPlan, CalibrationRecord
from app.models.haccp import CCP, CCPMonitoringLog
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.services.haccp_service import HACCPValidationError, HACCPBusinessError

logger = logging.getLogger(__name__)


class CalibrationStatus(Enum):
    """Calibration status enumeration"""
    VALID = "valid"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    OVERDUE = "overdue"
    NOT_CALIBRATED = "not_calibrated"


class EquipmentCalibrationService:
    """
    Service for enforcing equipment calibration requirements in HACCP monitoring
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_equipment_calibration(self, equipment_id: int) -> Dict[str, Any]:
        """
        Check calibration status of equipment
        
        Returns:
            Dictionary with calibration status and details
        """
        try:
            equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
            if not equipment:
                raise HACCPValidationError(f"Equipment with ID {equipment_id} not found")
            
            # Get latest calibration record
            latest_calibration = self.db.query(CalibrationRecord).filter(
                CalibrationRecord.equipment_id == equipment_id
            ).order_by(desc(CalibrationRecord.calibration_date)).first()
            
            if not latest_calibration:
                return {
                    "equipment_id": equipment_id,
                    "equipment_name": equipment.name,
                    "status": CalibrationStatus.NOT_CALIBRATED.value,
                    "is_valid": False,
                    "message": "Equipment has never been calibrated",
                    "requires_calibration": True,
                    "days_until_expiry": None,
                    "last_calibration_date": None,
                    "next_calibration_date": None
                }
            
            # Get calibration plan
            calibration_plan = self.db.query(CalibrationPlan).filter(
                CalibrationPlan.equipment_id == equipment_id
            ).first()
            
            if not calibration_plan:
                return {
                    "equipment_id": equipment_id,
                    "equipment_name": equipment.name,
                    "status": CalibrationStatus.NOT_CALIBRATED.value,
                    "is_valid": False,
                    "message": "No calibration plan found for equipment",
                    "requires_calibration": True,
                    "days_until_expiry": None,
                    "last_calibration_date": latest_calibration.calibration_date,
                    "next_calibration_date": None
                }
            
            # Calculate next calibration date
            next_calibration_date = latest_calibration.calibration_date + timedelta(days=calibration_plan.frequency_days)
            days_until_expiry = (next_calibration_date - datetime.utcnow()).days
            
            # Determine status
            if days_until_expiry < 0:
                status = CalibrationStatus.EXPIRED
                is_valid = False
                message = f"Calibration expired {abs(days_until_expiry)} days ago"
                requires_calibration = True
            elif days_until_expiry <= 30:
                status = CalibrationStatus.EXPIRING_SOON
                is_valid = True
                message = f"Calibration expires in {days_until_expiry} days"
                requires_calibration = True
            else:
                status = CalibrationStatus.VALID
                is_valid = True
                message = f"Calibration valid for {days_until_expiry} more days"
                requires_calibration = False
            
            return {
                "equipment_id": equipment_id,
                "equipment_name": equipment.name,
                "status": status.value,
                "is_valid": is_valid,
                "message": message,
                "requires_calibration": requires_calibration,
                "days_until_expiry": days_until_expiry,
                "last_calibration_date": latest_calibration.calibration_date,
                "next_calibration_date": next_calibration_date,
                "calibration_frequency_days": calibration_plan.frequency_days
            }
            
        except Exception as e:
            logger.error(f"Error checking equipment calibration for equipment {equipment_id}: {e}")
            raise HACCPBusinessError(f"Failed to check equipment calibration: {str(e)}")
    
    def validate_monitoring_equipment(self, ccp_id: int, equipment_id: int) -> bool:
        """
        Validate that equipment used for CCP monitoring is properly calibrated
        
        Args:
            ccp_id: ID of the CCP
            equipment_id: ID of the equipment
            
        Returns:
            True if equipment is valid for monitoring, False otherwise
            
        Raises:
            HACCPValidationError: If equipment is not calibrated or calibration is expired
        """
        try:
            # Check if CCP exists
            ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
            if not ccp:
                raise HACCPValidationError(f"CCP with ID {ccp_id} not found")
            
            # Check equipment calibration
            calibration_status = self.check_equipment_calibration(equipment_id)
            
            if not calibration_status["is_valid"]:
                raise HACCPValidationError(
                    f"Equipment '{calibration_status['equipment_name']}' is not properly calibrated: "
                    f"{calibration_status['message']}"
                )
            
            return True
            
        except HACCPValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating monitoring equipment: {e}")
            raise HACCPBusinessError(f"Failed to validate monitoring equipment: {str(e)}")
    
    def get_ccps_with_uncalibrated_equipment(self) -> List[Dict[str, Any]]:
        """
        Get all CCPs that use uncalibrated or expired equipment
        
        Returns:
            List of CCPs with equipment calibration issues
        """
        try:
            ccps_with_issues = []
            
            # Get all CCPs that specify monitoring equipment
            ccps = self.db.query(CCP).filter(CCP.monitoring_equipment.isnot(None)).all()
            
            for ccp in ccps:
                # Parse equipment IDs from monitoring_equipment field
                equipment_ids = self._parse_equipment_ids(ccp.monitoring_equipment)
                
                for equipment_id in equipment_ids:
                    try:
                        calibration_status = self.check_equipment_calibration(equipment_id)
                        
                        if not calibration_status["is_valid"]:
                            ccps_with_issues.append({
                                "ccp_id": ccp.id,
                                "ccp_name": ccp.ccp_name,
                                "product_id": ccp.product_id,
                                "equipment_id": equipment_id,
                                "equipment_name": calibration_status["equipment_name"],
                                "calibration_status": calibration_status["status"],
                                "message": calibration_status["message"],
                                "days_until_expiry": calibration_status["days_until_expiry"],
                                "requires_calibration": calibration_status["requires_calibration"]
                            })
                    except Exception as e:
                        logger.error(f"Error checking equipment {equipment_id} for CCP {ccp.id}: {e}")
                        ccps_with_issues.append({
                            "ccp_id": ccp.id,
                            "ccp_name": ccp.ccp_name,
                            "product_id": ccp.product_id,
                            "equipment_id": equipment_id,
                            "equipment_name": "Unknown",
                            "calibration_status": "error",
                            "message": f"Error checking calibration: {str(e)}",
                            "days_until_expiry": None,
                            "requires_calibration": True
                        })
            
            return ccps_with_issues
            
        except Exception as e:
            logger.error(f"Error getting CCPs with uncalibrated equipment: {e}")
            raise HACCPBusinessError(f"Failed to get CCPs with uncalibrated equipment: {str(e)}")
    
    def enforce_calibration_requirements(self, user_id: int) -> Dict[str, Any]:
        """
        Enforce calibration requirements by checking all equipment and sending notifications
        
        Args:
            user_id: ID of the user performing the enforcement check
            
        Returns:
            Dictionary with enforcement results
        """
        try:
            enforcement_results = {
                "total_equipment_checked": 0,
                "equipment_requiring_calibration": 0,
                "ccps_affected": 0,
                "notifications_sent": 0,
                "details": []
            }
            
            # Get all equipment
            all_equipment = self.db.query(Equipment).all()
            enforcement_results["total_equipment_checked"] = len(all_equipment)
            
            # Check each equipment
            for equipment in all_equipment:
                try:
                    calibration_status = self.check_equipment_calibration(equipment.id)
                    
                    if calibration_status["requires_calibration"]:
                        enforcement_results["equipment_requiring_calibration"] += 1
                        
                        # Send notification to equipment manager
                        self._send_calibration_notification(equipment.id, calibration_status, user_id)
                        enforcement_results["notifications_sent"] += 1
                        
                        enforcement_results["details"].append({
                            "equipment_id": equipment.id,
                            "equipment_name": equipment.name,
                            "status": calibration_status["status"],
                            "message": calibration_status["message"],
                            "days_until_expiry": calibration_status["days_until_expiry"]
                        })
                        
                except Exception as e:
                    logger.error(f"Error checking equipment {equipment.id}: {e}")
            
            # Get CCPs affected by uncalibrated equipment
            affected_ccps = self.get_ccps_with_uncalibrated_equipment()
            enforcement_results["ccps_affected"] = len(affected_ccps)
            
            # Send notifications for affected CCPs
            for ccp_issue in affected_ccps:
                self._send_ccp_equipment_notification(ccp_issue, user_id)
                enforcement_results["notifications_sent"] += 1
            
            return enforcement_results
            
        except Exception as e:
            logger.error(f"Error enforcing calibration requirements: {e}")
            raise HACCPBusinessError(f"Failed to enforce calibration requirements: {str(e)}")
    
    def get_calibration_schedule(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming calibration schedule
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming calibrations
        """
        try:
            upcoming_calibrations = []
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            # Get all equipment with calibration plans
            equipment_with_plans = self.db.query(Equipment).join(CalibrationPlan).all()
            
            for equipment in equipment_with_plans:
                # Get latest calibration
                latest_calibration = self.db.query(CalibrationRecord).filter(
                    CalibrationRecord.equipment_id == equipment.id
                ).order_by(desc(CalibrationRecord.calibration_date)).first()
                
                if latest_calibration:
                    # Get calibration plan
                    calibration_plan = self.db.query(CalibrationPlan).filter(
                        CalibrationPlan.equipment_id == equipment.id
                    ).first()
                    
                    if calibration_plan:
                        next_calibration_date = latest_calibration.calibration_date + timedelta(days=calibration_plan.frequency_days)
                        
                        if next_calibration_date <= cutoff_date:
                            upcoming_calibrations.append({
                                "equipment_id": equipment.id,
                                "equipment_name": equipment.name,
                                "last_calibration_date": latest_calibration.calibration_date,
                                "next_calibration_date": next_calibration_date,
                                "calibration_frequency_days": calibration_plan.frequency_days,
                                "days_until_calibration": (next_calibration_date - datetime.utcnow()).days
                            })
            
            # Sort by days until calibration
            upcoming_calibrations.sort(key=lambda x: x["days_until_calibration"])
            
            return upcoming_calibrations
            
        except Exception as e:
            logger.error(f"Error getting calibration schedule: {e}")
            raise HACCPBusinessError(f"Failed to get calibration schedule: {str(e)}")
    
    def _parse_equipment_ids(self, equipment_string: str) -> List[int]:
        """
        Parse equipment IDs from equipment string
        
        Args:
            equipment_string: String containing equipment information
            
        Returns:
            List of equipment IDs
        """
        try:
            if not equipment_string:
                return []
            
            # Try to parse as JSON first
            try:
                import json
                equipment_data = json.loads(equipment_string)
                if isinstance(equipment_data, list):
                    return [item.get("id") for item in equipment_data if item.get("id")]
                elif isinstance(equipment_data, dict):
                    return [equipment_data.get("id")] if equipment_data.get("id") else []
            except (json.JSONDecodeError, TypeError):
                pass
            
            # Try to extract IDs from comma-separated string
            if "," in equipment_string:
                parts = equipment_string.split(",")
                equipment_ids = []
                for part in parts:
                    try:
                        equipment_id = int(part.strip())
                        equipment_ids.append(equipment_id)
                    except ValueError:
                        continue
                return equipment_ids
            
            # Try to extract single ID
            try:
                equipment_id = int(equipment_string.strip())
                return [equipment_id]
            except ValueError:
                return []
                
        except Exception as e:
            logger.error(f"Error parsing equipment IDs from string '{equipment_string}': {e}")
            return []
    
    def _send_calibration_notification(self, equipment_id: int, calibration_status: Dict[str, Any], user_id: int) -> None:
        """
        Send notification about equipment calibration requirement
        
        Args:
            equipment_id: ID of the equipment
            calibration_status: Calibration status information
            user_id: ID of the user who triggered the check
        """
        try:
            # Get equipment manager or responsible person
            equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
            if not equipment:
                return
            
            # Find users responsible for equipment maintenance
            responsible_users = self.db.query(User).filter(
                User.role.has(name__in=["Equipment Manager", "Maintenance", "HACCP Team"])
            ).all()
            
            for user in responsible_users:
                notification = Notification(
                    user_id=user.id,
                    type=NotificationType.ALERT if calibration_status["status"] == "expired" else NotificationType.REMINDER,
                    priority=NotificationPriority.HIGH if calibration_status["status"] == "expired" else NotificationPriority.MEDIUM,
                    category=NotificationCategory.EQUIPMENT,
                    title=f"Equipment Calibration Required: {calibration_status['equipment_name']}",
                    message=calibration_status["message"],
                    data={
                        "equipment_id": equipment_id,
                        "equipment_name": calibration_status["equipment_name"],
                        "calibration_status": calibration_status["status"],
                        "days_until_expiry": calibration_status["days_until_expiry"],
                        "checked_by_user_id": user_id
                    }
                )
                self.db.add(notification)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error sending calibration notification for equipment {equipment_id}: {e}")
    
    def _send_ccp_equipment_notification(self, ccp_issue: Dict[str, Any], user_id: int) -> None:
        """
        Send notification about CCP affected by uncalibrated equipment
        
        Args:
            ccp_issue: CCP equipment issue information
            user_id: ID of the user who triggered the check
        """
        try:
            # Get HACCP team members
            haccp_users = self.db.query(User).filter(User.role.has(name="HACCP Team")).all()
            
            for user in haccp_users:
                notification = Notification(
                    user_id=user.id,
                    type=NotificationType.ALERT,
                    priority=NotificationPriority.HIGH,
                    category=NotificationCategory.HACCP,
                    title=f"CCP Equipment Calibration Issue: {ccp_issue['ccp_name']}",
                    message=f"CCP '{ccp_issue['ccp_name']}' uses uncalibrated equipment '{ccp_issue['equipment_name']}': {ccp_issue['message']}",
                    data={
                        "ccp_id": ccp_issue["ccp_id"],
                        "ccp_name": ccp_issue["ccp_name"],
                        "equipment_id": ccp_issue["equipment_id"],
                        "equipment_name": ccp_issue["equipment_name"],
                        "calibration_status": ccp_issue["calibration_status"],
                        "checked_by_user_id": user_id
                    }
                )
                self.db.add(notification)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error sending CCP equipment notification: {e}")
