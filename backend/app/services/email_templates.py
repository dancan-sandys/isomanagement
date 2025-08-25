from typing import Dict, Any, Optional
from datetime import datetime
from app.models.notification import Notification, NotificationType, NotificationCategory, NotificationPriority


class EmailTemplates:
    """
    Email templates for ISO 22000 FSMS notifications
    """
    
    @staticmethod
    def get_template(template_name: str, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Get email template by name with data substitution
        """
        templates = {
            'welcome_user': EmailTemplates._welcome_user_template,
            'password_reset': EmailTemplates._password_reset_template,
            'document_approval': EmailTemplates._document_approval_template,
            'haccp_alert': EmailTemplates._haccp_alert_template,
            'audit_notification': EmailTemplates._audit_notification_template,
            'capa_assignment': EmailTemplates._capa_assignment_template,
            'training_reminder': EmailTemplates._training_reminder_template,
            'system_maintenance': EmailTemplates._system_maintenance_template,
            'ccp_violation': EmailTemplates._ccp_violation_template,
            'document_expiry': EmailTemplates._document_expiry_template,
            'supplier_audit': EmailTemplates._supplier_audit_template,
            'equipment_calibration': EmailTemplates._equipment_calibration_template,
            'compliance_deadline': EmailTemplates._compliance_deadline_template,
            'recall_notification': EmailTemplates._recall_notification_template,
        }
        
        if template_name not in templates:
            return EmailTemplates._default_template(data)
        
        return templates[template_name](data)
    
    @staticmethod
    def _welcome_user_template(data: Dict[str, Any]) -> Dict[str, str]:
        """Welcome email for new users"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">Welcome to ISO 22000 FSMS</h1>
                    <p style="font-size: 18px; color: #7f8c8d;">Your account has been successfully created</p>
                </div>
                
                <div style="padding: 20px; background-color: white;">
                    <h2>Hello {data.get('full_name', 'User')},</h2>
                    <p>Welcome to the ISO 22000 Food Safety Management System. Your account has been created with the following details:</p>
                    
                    <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Username:</strong> {data.get('username', 'N/A')}</p>
                        <p><strong>Role:</strong> {data.get('role_name', 'N/A')}</p>
                        <p><strong>Department:</strong> {data.get('department', 'N/A')}</p>
                    </div>
                    
                    <p>Please log in to the system and complete your profile setup. If you have any questions, please contact your system administrator.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{data.get('login_url', '#')}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Login to System</a>
                    </div>
                    
                    <p><strong>Important:</strong> Please change your password on first login for security purposes.</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                    <p>This is an automated message from the ISO 22000 FSMS. Please do not reply to this email.</p>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
Welcome to ISO 22000 FSMS

Hello {data.get('full_name', 'User')},

Welcome to the ISO 22000 Food Safety Management System. Your account has been created with the following details:

Username: {data.get('username', 'N/A')}
Role: {data.get('role_name', 'N/A')}
Department: {data.get('department', 'N/A')}

Please log in to the system and complete your profile setup. If you have any questions, please contact your system administrator.

Login URL: {data.get('login_url', '#')}

Important: Please change your password on first login for security purposes.

This is an automated message from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return {"html": html_content, "plain": plain_content}
    
    @staticmethod
    def _haccp_alert_template(data: Dict[str, Any]) -> Dict[str, str]:
        """HACCP critical control point violation alert"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #e74c3c; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                    <h1 style="margin-bottom: 10px;">🚨 HACCP CRITICAL ALERT</h1>
                    <p style="font-size: 18px;">Critical Control Point Violation Detected</p>
                </div>
                
                <div style="padding: 20px; background-color: white;">
                    <h2>Critical Control Point Violation</h2>
                    <p>A critical control point violation has been detected that requires immediate attention:</p>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Product:</strong> {data.get('product_name', 'N/A')}</p>
                        <p><strong>CCP:</strong> {data.get('ccp_name', 'N/A')}</p>
                        <p><strong>Batch Number:</strong> {data.get('batch_number', 'N/A')}</p>
                        <p><strong>Measured Value:</strong> {data.get('measured_value', 'N/A')} {data.get('unit', '')}</p>
                        <p><strong>Limit:</strong> {data.get('limit_value', 'N/A')} {data.get('unit', '')}</p>
                        <p><strong>Violation Time:</strong> {data.get('violation_time', 'N/A')}</p>
                    </div>
                    
                    <p><strong>Immediate Actions Required:</strong></p>
                    <ul>
                        <li>Stop production if necessary</li>
                        <li>Isolate affected product</li>
                        <li>Initiate corrective actions</li>
                        <li>Document the incident</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{data.get('action_url', '#')}" style="background-color: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Details & Take Action</a>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                    <p>This is a critical food safety alert. Immediate action is required.</p>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
🚨 HACCP CRITICAL ALERT - Critical Control Point Violation Detected

A critical control point violation has been detected that requires immediate attention:

Product: {data.get('product_name', 'N/A')}
CCP: {data.get('ccp_name', 'N/A')}
Batch Number: {data.get('batch_number', 'N/A')}
Measured Value: {data.get('measured_value', 'N/A')} {data.get('unit', '')}
Limit: {data.get('limit_value', 'N/A')} {data.get('unit', '')}
Violation Time: {data.get('violation_time', 'N/A')}

IMMEDIATE ACTIONS REQUIRED:
- Stop production if necessary
- Isolate affected product
- Initiate corrective actions
- Document the incident

View Details: {data.get('action_url', '#')}

This is a critical food safety alert. Immediate action is required.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return {"html": html_content, "plain": plain_content}
    
    @staticmethod
    def _document_approval_template(data: Dict[str, Any]) -> Dict[str, str]:
        """Document approval request notification"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #3498db; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                    <h1 style="margin-bottom: 10px;">📋 Document Approval Required</h1>
                    <p style="font-size: 18px;">A document requires your review and approval</p>
                </div>
                
                <div style="padding: 20px; background-color: white;">
                    <h2>Document Approval Request</h2>
                    <p>You have been assigned as an approver for the following document:</p>
                    
                    <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Document Title:</strong> {data.get('document_title', 'N/A')}</p>
                        <p><strong>Document Type:</strong> {data.get('document_type', 'N/A')}</p>
                        <p><strong>Submitted By:</strong> {data.get('submitted_by', 'N/A')}</p>
                        <p><strong>Submission Date:</strong> {data.get('submission_date', 'N/A')}</p>
                        <p><strong>Due Date:</strong> {data.get('due_date', 'N/A')}</p>
                    </div>
                    
                    <p>Please review the document and provide your approval or feedback within the specified timeframe.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{data.get('action_url', '#')}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Review Document</a>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                    <p>This is an automated notification from the ISO 22000 FSMS.</p>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
📋 Document Approval Required

You have been assigned as an approver for the following document:

Document Title: {data.get('document_title', 'N/A')}
Document Type: {data.get('document_type', 'N/A')}
Submitted By: {data.get('submitted_by', 'N/A')}
Submission Date: {data.get('submission_date', 'N/A')}
Due Date: {data.get('due_date', 'N/A')}

Please review the document and provide your approval or feedback within the specified timeframe.

Review Document: {data.get('action_url', '#')}

This is an automated notification from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return {"html": html_content, "plain": plain_content}
    
    @staticmethod
    def _default_template(data: Dict[str, Any]) -> Dict[str, str]:
        """Default template for notifications"""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">{data.get('title', 'Notification')}</h1>
                    <p style="font-size: 16px; color: #7f8c8d;">{data.get('subtitle', 'System Notification')}</p>
                </div>
                
                <div style="padding: 20px; background-color: white;">
                    <p>{data.get('message', 'You have received a notification from the ISO 22000 FSMS.')}</p>
                    
                    {f'<div style="text-align: center; margin: 30px 0;"><a href="{data.get("action_url", "#")}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">{data.get("action_text", "View Details")}</a></div>' if data.get('action_url') else ''}
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                    <p>This is an automated notification from the ISO 22000 FSMS.</p>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
{data.get('title', 'Notification')}

{data.get('message', 'You have received a notification from the ISO 22000 FSMS.')}

{f'{data.get("action_text", "View Details")}: {data.get("action_url", "#")}' if data.get('action_url') else ''}

This is an automated notification from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return {"html": html_content, "plain": plain_content}
