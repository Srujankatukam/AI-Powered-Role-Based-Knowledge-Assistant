"""
Document management endpoints
"""
import os
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path

from ...core.database import get_database
from ...core.security import get_current_active_user, PermissionChecker
from ...models.user import User
from ...models.document import Document, DocumentCreate, DocumentUpdate, DocumentInDB
from ...services.document_ingestion import DocumentIngestionPipeline
from ...core.config import settings

router = APIRouter()

# Initialize document ingestion pipeline
ingestion_pipeline = DocumentIngestionPipeline()


@router.post("/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    access_level: str = Form("employee"),
    department: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Upload and process a document"""
    
    # Check if user can upload documents
    if not PermissionChecker.can_upload_document(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload documents"
        )
    
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Create document record
        document_data = DocumentCreate(
            title=title,
            content="",  # Will be filled after processing
            file_type=file_extension,
            access_level=access_level,
            department=department
        )
        
        db_document = Document(
            **document_data.dict(),
            uploaded_by=current_user.id,
            file_size=file.size
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Save file to disk
        file_path = f"./data/documents/{db_document.id}_{file.filename}"
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Update document with file path
        db_document.file_path = file_path
        db.commit()
        
        # Process document through ingestion pipeline
        ingestion_result = await ingestion_pipeline.ingest_document(
            file_path=file_path,
            document_id=db_document.id,
            metadata={
                "title": title,
                "access_level": access_level,
                "department": department,
                "uploaded_by": current_user.username
            }
        )
        
        # Update document status
        if ingestion_result["status"] == "success":
            db_document.is_indexed = True
            db_document.content = "Document processed successfully"  # Placeholder
        else:
            db_document.content = f"Processing failed: {ingestion_result.get('error', 'Unknown error')}"
        
        db.commit()
        
        return {
            "document_id": db_document.id,
            "filename": file.filename,
            "status": ingestion_result["status"],
            "processing_info": ingestion_result
        }
        
    except Exception as e:
        # Clean up on error
        if 'db_document' in locals():
            db.delete(db_document)
            db.commit()
        
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/", response_model=List[DocumentInDB])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """List documents accessible to the current user"""
    
    query = db.query(Document)
    
    # Apply role-based filtering
    if current_user.role.value != "admin":
        # Non-admin users can only see documents they have access to
        accessible_levels = ["employee"]
        if current_user.role.value == "manager":
            accessible_levels.append("manager")
        
        query = query.filter(Document.access_level.in_(accessible_levels))
        
        # Filter by department if user has one
        if hasattr(current_user, 'department') and current_user.department:
            query = query.filter(
                (Document.department == current_user.department) | 
                (Document.department.is_(None))
            )
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentInDB)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check access permissions
    if not PermissionChecker.can_access_document(
        current_user, 
        document.access_level, 
        document.department
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this document"
        )
    
    return document


@router.put("/{document_id}", response_model=DocumentInDB)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update a document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user can modify this document
    if document.uploaded_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify documents you uploaded"
        )
    
    # Update document fields
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Delete a document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user can delete this document
    if document.uploaded_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete documents you uploaded"
        )
    
    # Delete file from disk
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}