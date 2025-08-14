from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import logging

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserSession
from app.services.rbac_service import check_user_permission
import re

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing - use a more compatible configuration
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
except Exception as e:
    logger.warning(f"Failed to initialize bcrypt with default settings: {e}")
    # Fallback to basic configuration
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    logger.info(f"Verifying password. Hash length: {len(hashed_password)}")
    
    try:
        # First try bcrypt verification
        logger.info("Attempting bcrypt verification...")
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"Bcrypt verification result: {result}")
        return result
    except Exception as e:
        logger.warning(f"Bcrypt verification failed: {e}")
        # Fallback to simple hash verification
        try:
            logger.info("Attempting simple hash verification...")
            import hashlib
            simple_hash = hashlib.sha256(plain_password.encode()).hexdigest()
            logger.info(f"Generated simple hash: {simple_hash}")
            logger.info(f"Stored hash: {hashed_password}")
            result = (simple_hash == hashed_password)
            logger.info(f"Simple hash verification result: {result}")
            return result
        except Exception as e2:
            logger.error(f"Simple hash verification also failed: {e2}")
            return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        # Fallback to a simple hash if bcrypt fails
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def validate_password_policy(password: str) -> bool:
    """Validate password against policy from settings."""
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False
    if settings.PASSWORD_REQUIRE_NUMBER and not re.search(r"\d", password):
        return False
    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Check if user is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="User account is locked"
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.warning(f"User not found: {username}")
        return None
    
    logger.info(f"Attempting to verify password for user: {username}")
    logger.info(f"Stored hash: {user.hashed_password}")
    
    if not verify_password(password, user.hashed_password):
        logger.error(f"Password verification failed for user: {username}")
        return None
    
    logger.info(f"Password verification successful for user: {username}")
    return user

def create_user_session(db: Session, user_id: int, access_token: str, refresh_token: str, 
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
    """Create a new user session"""
    session = UserSession(
        user_id=user_id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def invalidate_user_session(db: Session, session_token: str) -> bool:
    """Invalidate a user session"""
    session = db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.is_active == True
    ).first()
    
    if session:
        session.is_active = False
        db.commit()
        return True
    return False

def require_permission(permission: Union[str, tuple]):
    """
    Dependency to enforce permissions.

    Supports:
    - Tuple form: ("MODULE", "ACTION") e.g. ("USERS", "CREATE")
    - Legacy string form: "module:action" e.g. "users:write"
    """

    def _normalize_legacy(permission_str: str) -> tuple[str, str]:
        # Expect "module:action"; normalize whitespace and case
        parts = [p.strip() for p in permission_str.split(":", 1)]
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid permission format: {permission_str}"
            )
        module, action = parts[0], parts[1]
        # Map common legacy action names to RBAC actions
        action_mapping = {
            "read": "VIEW",
            "view": "VIEW",
            "write": "CREATE",
            "create": "CREATE",
            "edit": "UPDATE",
            "update": "UPDATE",
            "remove": "DELETE",
            "delete": "DELETE",
        }
        normalized_action = action_mapping.get(action.lower(), action.upper())
        return module.upper(), normalized_action

    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ):
        # Handle tuple form
        if isinstance(permission, tuple) and len(permission) == 2:
            module, action = permission
            module_norm = (module or "").strip().upper()
            action_norm = (action or "").strip().upper()
            if not module_norm or not action_norm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid permission format: {permission}"
                )
            if not check_user_permission(db, current_user.id, module_norm, action_norm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {module_norm}:{action_norm}"
                )
        # Handle legacy string form
        elif isinstance(permission, str):
            if ":" not in permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid permission format: {permission}"
                )
            module_norm, action_norm = _normalize_legacy(permission)
            if not check_user_permission(db, current_user.id, module_norm, action_norm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {module_norm}:{action_norm}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid permission format: {permission}"
            )
        return current_user

    return permission_checker 