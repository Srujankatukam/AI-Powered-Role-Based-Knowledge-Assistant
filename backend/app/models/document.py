"""
Document models for knowledge base management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from ..core.database import Base
from .user import UserRole


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    
    # Access control
    access_level = Column(String, default="employee")  # employee, manager, admin
    department = Column(String, nullable=True)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Vector embeddings info
    embedding_id = Column(String, nullable=True)  # Reference to vector DB
    is_indexed = Column(Boolean, default=False)
    
    # Audit fields
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploader = relationship("User", back_populates="documents")


# Pydantic models
class DocumentBase(BaseModel):
    title: str
    content: str
    file_type: str
    access_level: str = "employee"
    department: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    access_level: Optional[str] = None
    department: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentInDB(DocumentBase):
    id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    embedding_id: Optional[str] = None
    is_indexed: bool = False
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Document(DocumentBase):
    id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    is_indexed: bool = False
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentChunk(BaseModel):
    """Represents a chunk of a document for vector storage"""
    document_id: int
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    query: str
    use_web_search: bool = False
    max_results: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float