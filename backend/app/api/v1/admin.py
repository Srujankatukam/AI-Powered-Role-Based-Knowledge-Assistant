"""
Admin endpoints for system management
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_database
from ...core.security import require_admin, require_manager_or_above, PermissionChecker
from ...models.user import User, UserInDB, UserCreate, UserUpdate, UserRole
from ...services.azure_keyvault import secret_manager

router = APIRouter()


@router.get("/users", response_model=List[UserInDB])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_database)
):
    """List all users (admin only)"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserInDB)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_database)
):
    """Create a new user (admin only)"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    from ...core.security import get_password_hash
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_database)
):
    """Update a user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_database)
):
    """Delete a user (admin only)"""
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/system/status")
async def get_system_status(
    current_user: User = Depends(require_manager_or_above())
):
    """Get system status and health information"""
    
    try:
        # Check secret management status
        secrets_status = await secret_manager.initialize_secrets()
        
        # Check vector database status
        from ...services.document_ingestion import VectorStoreService
        vector_store = VectorStoreService()
        
        # Get document statistics
        from ...models.document import Document
        from ...core.database import SessionLocal
        
        db = SessionLocal()
        try:
            total_documents = db.query(Document).count()
            indexed_documents = db.query(Document).filter(Document.is_indexed == True).count()
        finally:
            db.close()
        
        return {
            "status": "healthy",
            "secrets_status": secrets_status,
            "vector_database": {
                "status": "connected",
                "collection_name": vector_store.collection_name
            },
            "documents": {
                "total": total_documents,
                "indexed": indexed_documents,
                "pending_indexing": total_documents - indexed_documents
            },
            "user_role": current_user.role.value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/analytics")
async def get_system_analytics(
    current_user: User = Depends(require_manager_or_above()),
    db: Session = Depends(get_database)
):
    """Get system analytics and usage statistics"""
    
    if not PermissionChecker.can_view_analytics(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view analytics"
        )
    
    try:
        from ...models.document import Document
        from sqlalchemy import func
        
        # User statistics
        user_stats = db.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # Document statistics
        doc_stats = db.query(
            Document.access_level,
            func.count(Document.id).label('count')
        ).group_by(Document.access_level).all()
        
        # Document by department
        dept_stats = db.query(
            Document.department,
            func.count(Document.id).label('count')
        ).group_by(Document.department).all()
        
        return {
            "users_by_role": {stat.role.value: stat.count for stat in user_stats},
            "documents_by_access_level": {stat.access_level: stat.count for stat in doc_stats},
            "documents_by_department": {
                stat.department or "General": stat.count for stat in dept_stats
            },
            "total_users": db.query(User).count(),
            "active_users": db.query(User).filter(User.is_active == True).count(),
            "total_documents": db.query(Document).count(),
            "indexed_documents": db.query(Document).filter(Document.is_indexed == True).count()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )


@router.post("/secrets/validate")
async def validate_secrets(
    current_user: User = Depends(require_admin())
):
    """Validate all system secrets"""
    
    try:
        secrets_status = await secret_manager.initialize_secrets()
        
        return {
            "status": "completed",
            "secrets": secrets_status,
            "all_valid": all(secrets_status.values())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating secrets: {str(e)}"
        )