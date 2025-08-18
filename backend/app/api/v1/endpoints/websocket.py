from datetime import datetime
from typing import Dict, Set
import json
import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_websocket
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.services.dashboard_rbac_service import DashboardRBACService

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time dashboard updates"""
    
    def __init__(self):
        # Store active connections: {user_id: {websocket, last_ping, permissions}}
        self.active_connections: Dict[int, Dict] = {}
        # Store department subscriptions: {department_id: set(user_ids)}
        self.department_subscriptions: Dict[int, Set[int]] = {}
        # Store KPI subscriptions: {kpi_id: set(user_ids)}
        self.kpi_subscriptions: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, user_permissions: Dict[str, any]):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = {
            'websocket': websocket,
            'last_ping': datetime.utcnow(),
            'permissions': user_permissions,
            'subscriptions': {
                'departments': set(),
                'kpis': set()
            }
        }
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Send initial connection confirmation
        await self.send_personal_message({
            'type': 'connection_established',
            'data': {
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'permissions': user_permissions
            }
        }, user_id)
    
    def disconnect(self, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            # Remove from all subscriptions
            connection_data = self.active_connections[user_id]
            subscriptions = connection_data.get('subscriptions', {})
            
            # Remove from department subscriptions
            for dept_id in subscriptions.get('departments', set()):
                if dept_id in self.department_subscriptions:
                    self.department_subscriptions[dept_id].discard(user_id)
                    if not self.department_subscriptions[dept_id]:
                        del self.department_subscriptions[dept_id]
            
            # Remove from KPI subscriptions
            for kpi_id in subscriptions.get('kpis', set()):
                if kpi_id in self.kpi_subscriptions:
                    self.kpi_subscriptions[kpi_id].discard(user_id)
                    if not self.kpi_subscriptions[kpi_id]:
                        del self.kpi_subscriptions[kpi_id]
            
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]['websocket']
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_department(self, message: dict, department_id: int):
        """Send a message to all users subscribed to a department"""
        if department_id in self.department_subscriptions:
            tasks = []
            for user_id in self.department_subscriptions[department_id]:
                tasks.append(self.send_personal_message(message, user_id))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_kpi_subscribers(self, message: dict, kpi_id: int):
        """Send a message to all users subscribed to a KPI"""
        if kpi_id in self.kpi_subscriptions:
            tasks = []
            for user_id in self.kpi_subscriptions[kpi_id]:
                tasks.append(self.send_personal_message(message, user_id))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_all(self, message: dict):
        """Send a message to all connected users"""
        if self.active_connections:
            tasks = []
            for user_id in list(self.active_connections.keys()):
                tasks.append(self.send_personal_message(message, user_id))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def subscribe_to_department(self, user_id: int, department_id: int):
        """Subscribe a user to department updates"""
        if user_id in self.active_connections:
            if department_id not in self.department_subscriptions:
                self.department_subscriptions[department_id] = set()
            
            self.department_subscriptions[department_id].add(user_id)
            self.active_connections[user_id]['subscriptions']['departments'].add(department_id)
            logger.info(f"User {user_id} subscribed to department {department_id}")
    
    def subscribe_to_kpi(self, user_id: int, kpi_id: int):
        """Subscribe a user to KPI updates"""
        if user_id in self.active_connections:
            if kpi_id not in self.kpi_subscriptions:
                self.kpi_subscriptions[kpi_id] = set()
            
            self.kpi_subscriptions[kpi_id].add(user_id)
            self.active_connections[user_id]['subscriptions']['kpis'].add(kpi_id)
            logger.info(f"User {user_id} subscribed to KPI {kpi_id}")
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            'total_connections': len(self.active_connections),
            'department_subscriptions': {
                dept_id: len(users) for dept_id, users in self.department_subscriptions.items()
            },
            'kpi_subscriptions': {
                kpi_id: len(users) for kpi_id, users in self.kpi_subscriptions.items()
            }
        }

# Global connection manager instance
manager = ConnectionManager()

@router.websocket("/ws/dashboard/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time dashboard updates"""
    try:
        # Verify user authentication (simplified for WebSocket)
        # In production, you'd want proper JWT token validation
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            await websocket.close(code=1008, reason="Invalid user")
            return
        
        # Get user permissions
        rbac_service = DashboardRBACService(db)
        user_permissions = rbac_service.get_user_dashboard_permissions(user_id)
        accessible_modules = rbac_service.get_accessible_modules(user_id)
        
        # Connect to WebSocket
        await manager.connect(websocket, user_id, {
            'modules': accessible_modules,
            'permissions': user_permissions
        })
        
        # Start periodic data updates
        dashboard_service = DashboardService(db)
        update_task = asyncio.create_task(
            periodic_dashboard_updates(user_id, dashboard_service, rbac_service)
        )
        
        try:
            while True:
                # Listen for client messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_client_message(message, user_id, db, rbac_service)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
        finally:
            # Clean up
            update_task.cancel()
            manager.disconnect(user_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1011, reason="Internal server error")

async def handle_client_message(message: dict, user_id: int, db: Session, rbac_service: DashboardRBACService):
    """Handle messages from WebSocket clients"""
    try:
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type == 'subscribe_department':
            department_id = data.get('department_id')
            if department_id:
                manager.subscribe_to_department(user_id, department_id)
                await manager.send_personal_message({
                    'type': 'subscription_confirmed',
                    'data': {
                        'subscription_type': 'department',
                        'department_id': department_id
                    }
                }, user_id)
        
        elif message_type == 'subscribe_kpi':
            kpi_id = data.get('kpi_id')
            if kpi_id:
                # Check if user has access to this KPI
                accessible_kpis = rbac_service.get_accessible_kpis(user_id)
                if any(kpi.id == kpi_id for kpi in accessible_kpis):
                    manager.subscribe_to_kpi(user_id, kpi_id)
                    await manager.send_personal_message({
                        'type': 'subscription_confirmed',
                        'data': {
                            'subscription_type': 'kpi',
                            'kpi_id': kpi_id
                        }
                    }, user_id)
                else:
                    await manager.send_personal_message({
                        'type': 'error',
                        'data': {
                            'message': 'Access denied to KPI',
                            'kpi_id': kpi_id
                        }
                    }, user_id)
        
        elif message_type == 'ping':
            # Update last ping time
            if user_id in manager.active_connections:
                manager.active_connections[user_id]['last_ping'] = datetime.utcnow()
                await manager.send_personal_message({
                    'type': 'pong',
                    'data': {'timestamp': datetime.utcnow().isoformat()}
                }, user_id)
        
        elif message_type == 'get_stats':
            # Send current dashboard stats
            dashboard_service = DashboardService(db)
            stats = dashboard_service.get_dashboard_stats(user_id)
            
            await manager.send_personal_message({
                'type': 'dashboard_stats',
                'data': stats.dict()
            }, user_id)
        
        else:
            logger.warning(f"Unknown message type from user {user_id}: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling client message: {e}")
        await manager.send_personal_message({
            'type': 'error',
            'data': {'message': 'Error processing message'}
        }, user_id)

async def periodic_dashboard_updates(user_id: int, dashboard_service: DashboardService, rbac_service: DashboardRBACService):
    """Send periodic dashboard updates to connected user"""
    try:
        while True:
            # Wait for update interval (30 seconds)
            await asyncio.sleep(30)
            
            try:
                # Get latest dashboard stats
                stats = dashboard_service.get_dashboard_stats(user_id)
                
                # Send update
                await manager.send_personal_message({
                    'type': 'dashboard_update',
                    'data': {
                        'stats': stats.dict(),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }, user_id)
                
            except Exception as e:
                logger.error(f"Error sending periodic update to user {user_id}: {e}")
                
    except asyncio.CancelledError:
        logger.info(f"Periodic updates cancelled for user {user_id}")
    except Exception as e:
        logger.error(f"Error in periodic updates for user {user_id}: {e}")

# Helper functions for broadcasting updates from other parts of the application

async def broadcast_kpi_update(kpi_id: int, new_value: float, department_id: int = None):
    """Broadcast KPI update to subscribed users"""
    message = {
        'type': 'kpi_update',
        'data': {
            'kpi_id': kpi_id,
            'new_value': new_value,
            'department_id': department_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    await manager.broadcast_to_kpi_subscribers(message, kpi_id)
    
    if department_id:
        await manager.broadcast_to_department(message, department_id)

async def broadcast_alert(alert_id: int, kpi_id: int, level: str, message_text: str, department_id: int = None):
    """Broadcast alert to relevant users"""
    message = {
        'type': 'alert',
        'data': {
            'alert_id': alert_id,
            'kpi_id': kpi_id,
            'level': level,
            'message': message_text,
            'department_id': department_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    if department_id:
        await manager.broadcast_to_department(message, department_id)
    else:
        await manager.broadcast_to_all(message)

async def broadcast_system_status(status: str, message_text: str = None):
    """Broadcast system status update to all users"""
    message = {
        'type': 'system_status',
        'data': {
            'status': status,
            'message': message_text,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    await manager.broadcast_to_all(message)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()

# Export the manager for use in other modules
__all__ = ['manager', 'broadcast_kpi_update', 'broadcast_alert', 'broadcast_system_status']