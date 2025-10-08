"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from .database import get_database
from ..models.user import User, UserRole, TokenData


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
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


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username, role=UserRole(role) if role else None)
        return token_data
    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """Role-based access control checker"""
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user


# Role-based dependency factories
def require_employee_or_above():
    """Require employee role or above"""
    return RoleChecker([UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.ADMIN])


def require_manager_or_above():
    """Require manager role or above"""
    return RoleChecker([UserRole.MANAGER, UserRole.ADMIN])


def require_admin():
    """Require admin role"""
    return RoleChecker([UserRole.ADMIN])


class PermissionChecker:
    """Advanced permission checking for resources"""
    
    @staticmethod
    def can_access_document(user: User, document_access_level: str, document_department: str = None) -> bool:
        """Check if user can access a specific document"""
        # Admin can access everything
        if user.role == UserRole.ADMIN:
            return True
        
        # Check access level
        if document_access_level == "admin" and user.role != UserRole.ADMIN:
            return False
        
        if document_access_level == "manager" and user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
            return False
        
        # Check department access (if specified)
        if document_department and hasattr(user, 'department'):
            if user.department != document_department and user.role != UserRole.ADMIN:
                return False
        
        return True
    
    @staticmethod
    def can_upload_document(user: User) -> bool:
        """Check if user can upload documents"""
        # All authenticated users can upload documents
        return user.is_active
    
    @staticmethod
    def can_manage_users(user: User) -> bool:
        """Check if user can manage other users"""
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def can_view_analytics(user: User) -> bool:
        """Check if user can view system analytics"""
        return user.role in [UserRole.MANAGER, UserRole.ADMIN]


def check_document_access(document_access_level: str, document_department: str = None):
    """Dependency to check document access permissions"""
    def _check_access(current_user: User = Depends(get_current_active_user)) -> User:
        if not PermissionChecker.can_access_document(
            current_user, document_access_level, document_department
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this document"
            )
        return current_user
    
    return _check_access