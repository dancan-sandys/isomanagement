from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserSession
from app.services.rbac_service import check_user_permission

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

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
        return None
    if not verify_password(password, user.hashed_password):
        return None
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
    Decorator to require specific permission.
    Supports both old string format ("users:write") and new RBAC format (("USERS", "CREATE"))
    """
    def permission_checker(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
        # Handle new RBAC format: ("USERS", "CREATE")
        if isinstance(permission, tuple) and len(permission) == 2:
            module, action = permission
            if not check_user_permission(db, current_user.id, module, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {module}:{action}"
                )
        # Handle old string format: "users:write"
        elif isinstance(permission, str):
            # Convert old format to new format
            if ":" in permission:
                module_action = permission.split(":")
                if len(module_action) == 2:
                    module, action = module_action
                    # Map old actions to new ones
                    action_mapping = {
                        "read": "VIEW",
                        "write": "CREATE",
                        "update": "UPDATE", 
                        "delete": "DELETE"
                    }
                    new_action = action_mapping.get(action, action.upper())
                    if not check_user_permission(db, current_user.id, module.upper(), new_action):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Insufficient permissions: {permission}"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Invalid permission format: {permission}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid permission format: {permission}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid permission format: {permission}"
            )
        return current_user
    return permission_checker 