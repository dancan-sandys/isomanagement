from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserSession

# Password hashing context
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
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
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


def get_user_permissions(user: User) -> list:
    """Get user permissions based on role"""
    permissions = {
        "admin": [
            "users:read", "users:write", "users:delete",
            "documents:read", "documents:write", "documents:delete",
            "haccp:read", "haccp:write", "haccp:delete",
            "prp:read", "prp:write", "prp:delete",
            "suppliers:read", "suppliers:write", "suppliers:delete",
            "audits:read", "audits:write", "audits:delete",
            "reports:read", "reports:write",
            "system:admin"
        ],
        "qa_manager": [
            "users:read",
            "documents:read", "documents:write",
            "haccp:read", "haccp:write",
            "prp:read", "prp:write",
            "suppliers:read", "suppliers:write",
            "audits:read", "audits:write",
            "reports:read", "reports:write"
        ],
        "qa_specialist": [
            "documents:read", "documents:write",
            "haccp:read", "haccp:write",
            "prp:read", "prp:write",
            "suppliers:read",
            "audits:read", "audits:write",
            "reports:read"
        ],
        "production_manager": [
            "documents:read",
            "haccp:read", "haccp:write",
            "prp:read", "prp:write",
            "suppliers:read",
            "reports:read"
        ],
        "production_operator": [
            "haccp:read", "haccp:write",
            "prp:read", "prp:write"
        ],
        "maintenance": [
            "prp:read", "prp:write"
        ],
        "lab_technician": [
            "haccp:read", "haccp:write",
            "reports:read"
        ],
        "supplier": [
            "suppliers:read"
        ],
        "auditor": [
            "audits:read", "audits:write",
            "reports:read"
        ],
        "viewer": [
            "documents:read",
            "haccp:read",
            "prp:read",
            "reports:read"
        ]
    }
    
    return permissions.get(user.role.value, [])


def check_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return permission_checker 