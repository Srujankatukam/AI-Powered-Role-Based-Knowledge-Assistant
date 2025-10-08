"""
Query processing endpoints for the RAG pipeline
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_database
from ...core.security import get_current_active_user
from ...models.user import User
from ...models.document import QueryRequest, QueryResponse
from ...services.rag_pipeline import AgenticRAGPipeline

router = APIRouter()

# Initialize RAG pipeline
rag_pipeline = AgenticRAGPipeline()


@router.post("/ask", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Process a user query through the agentic RAG pipeline"""
    
    try:
        # Get user department if available
        user_department = getattr(current_user, 'department', None)
        
        # Process query through RAG pipeline
        result = await rag_pipeline.process_query(
            query=query_request.query,
            user_role=current_user.role.value,
            department=user_department,
            use_web_search=query_request.use_web_search
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Unknown error occurred")
            )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence_score=result["confidence_score"],
            processing_time=result["processing_time"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/history")
async def get_conversation_history(
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation history for the current user"""
    
    try:
        history = await rag_pipeline.get_conversation_history()
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.delete("/history")
async def clear_conversation_history(
    current_user: User = Depends(get_current_active_user)
):
    """Clear conversation history for the current user"""
    
    try:
        rag_pipeline.clear_conversation_history()
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing conversation history: {str(e)}"
        )


@router.post("/search")
async def search_documents(
    query: str,
    max_results: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Search documents directly without full RAG processing"""
    
    try:
        from ...services.document_ingestion import DocumentIngestionPipeline
        
        ingestion_pipeline = DocumentIngestionPipeline()
        user_department = getattr(current_user, 'department', None)
        
        results = await ingestion_pipeline.search_documents(
            query=query,
            user_role=current_user.role.value,
            department=user_department,
            k=max_results
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )