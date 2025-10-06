"""
LangSmith monitoring and tracking service
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

from langsmith import Client
from langsmith.run_helpers import traceable
from langchain.callbacks import LangChainTracer
from langchain.schema import BaseMessage

from ..core.config import settings

logger = logging.getLogger(__name__)


class LangSmithMonitor:
    """LangSmith monitoring and tracking service"""
    
    def __init__(self):
        self.client = None
        self.tracer = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LangSmith client"""
        if not settings.LANGCHAIN_API_KEY:
            logger.warning("LangSmith API key not configured. Monitoring will be disabled.")
            return
        
        try:
            # Set environment variables for LangSmith
            os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
            os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
            
            # Initialize client
            self.client = Client(
                api_url=settings.LANGCHAIN_ENDPOINT,
                api_key=settings.LANGCHAIN_API_KEY
            )
            
            # Initialize tracer
            self.tracer = LangChainTracer(
                project_name=settings.LANGCHAIN_PROJECT,
                client=self.client
            )
            
            logger.info("LangSmith monitoring initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith monitoring: {str(e)}")
            self.client = None
            self.tracer = None
    
    def is_available(self) -> bool:
        """Check if LangSmith monitoring is available"""
        return self.client is not None
    
    @traceable(name="query_processing")
    async def track_query_processing(
        self,
        query: str,
        user_role: str,
        department: Optional[str] = None,
        use_web_search: bool = False
    ) -> Dict[str, Any]:
        """Track query processing with LangSmith"""
        
        if not self.is_available():
            return {"status": "monitoring_disabled"}
        
        try:
            # Create run metadata
            metadata = {
                "user_role": user_role,
                "department": department,
                "use_web_search": use_web_search,
                "query_length": len(query),
                "timestamp": datetime.now().isoformat()
            }
            
            # Track the query processing
            run_id = await self._create_run(
                name="query_processing",
                run_type="chain",
                inputs={"query": query},
                metadata=metadata
            )
            
            return {
                "status": "tracking_started",
                "run_id": run_id,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error tracking query processing: {str(e)}")
            return {"status": "tracking_error", "error": str(e)}
    
    @traceable(name="document_ingestion")
    async def track_document_ingestion(
        self,
        document_id: int,
        file_name: str,
        file_type: str,
        file_size: int,
        processing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track document ingestion process"""
        
        if not self.is_available():
            return {"status": "monitoring_disabled"}
        
        try:
            metadata = {
                "document_id": document_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "chunks_created": processing_result.get("chunks_created", 0),
                "processing_time": processing_result.get("processing_time", 0),
                "status": processing_result.get("status", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
            run_id = await self._create_run(
                name="document_ingestion",
                run_type="chain",
                inputs={"file_name": file_name, "file_type": file_type},
                outputs=processing_result,
                metadata=metadata
            )
            
            return {
                "status": "tracking_completed",
                "run_id": run_id,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error tracking document ingestion: {str(e)}")
            return {"status": "tracking_error", "error": str(e)}
    
    async def track_user_session(
        self,
        user_id: int,
        user_role: str,
        session_duration: float,
        queries_count: int,
        documents_accessed: int
    ) -> Dict[str, Any]:
        """Track user session metrics"""
        
        if not self.is_available():
            return {"status": "monitoring_disabled"}
        
        try:
            metadata = {
                "user_id": user_id,
                "user_role": user_role,
                "session_duration": session_duration,
                "queries_count": queries_count,
                "documents_accessed": documents_accessed,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create a session tracking run
            run_id = await self._create_run(
                name="user_session",
                run_type="tool",
                inputs={"user_id": user_id, "user_role": user_role},
                outputs={"session_metrics": metadata},
                metadata=metadata
            )
            
            return {
                "status": "session_tracked",
                "run_id": run_id,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error tracking user session: {str(e)}")
            return {"status": "tracking_error", "error": str(e)}
    
    async def get_project_runs(
        self,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get runs from the LangSmith project"""
        
        if not self.is_available():
            return []
        
        try:
            # Set default time range if not provided
            if not end_time:
                end_time = datetime.now()
            if not start_time:
                start_time = end_time - timedelta(days=7)  # Last 7 days
            
            runs = list(self.client.list_runs(
                project_name=settings.LANGCHAIN_PROJECT,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            ))
            
            # Convert runs to serializable format
            serialized_runs = []
            for run in runs:
                serialized_runs.append({
                    "id": str(run.id),
                    "name": run.name,
                    "run_type": run.run_type,
                    "status": run.status,
                    "start_time": run.start_time.isoformat() if run.start_time else None,
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "execution_time": run.execution_order,
                    "error": run.error,
                    "inputs": run.inputs,
                    "outputs": run.outputs,
                    "metadata": run.extra
                })
            
            return serialized_runs
            
        except Exception as e:
            logger.error(f"Error retrieving project runs: {str(e)}")
            return []
    
    async def get_project_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics for the project"""
        
        if not self.is_available():
            return {"status": "monitoring_disabled"}
        
        try:
            # Get recent runs
            runs = await self.get_project_runs(limit=1000)
            
            if not runs:
                return {"status": "no_data"}
            
            # Calculate metrics
            total_runs = len(runs)
            successful_runs = len([r for r in runs if r["status"] == "success"])
            failed_runs = len([r for r in runs if r["status"] == "error"])
            
            # Calculate average execution time
            execution_times = [
                r.get("execution_time", 0) for r in runs 
                if r.get("execution_time") is not None
            ]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Group by run type
            run_types = {}
            for run in runs:
                run_type = run.get("run_type", "unknown")
                run_types[run_type] = run_types.get(run_type, 0) + 1
            
            # Group by user role (from metadata)
            user_roles = {}
            for run in runs:
                metadata = run.get("metadata", {})
                user_role = metadata.get("user_role", "unknown")
                user_roles[user_role] = user_roles.get(user_role, 0) + 1
            
            return {
                "status": "success",
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "success_rate": (successful_runs / total_runs) * 100 if total_runs > 0 else 0,
                "average_execution_time": avg_execution_time,
                "run_types": run_types,
                "user_roles": user_roles,
                "project_name": settings.LANGCHAIN_PROJECT
            }
            
        except Exception as e:
            logger.error(f"Error calculating project metrics: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _create_run(
        self,
        name: str,
        run_type: str,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a run in LangSmith"""
        
        try:
            run = self.client.create_run(
                name=name,
                run_type=run_type,
                inputs=inputs,
                outputs=outputs or {},
                project_name=settings.LANGCHAIN_PROJECT,
                extra=metadata or {}
            )
            
            return str(run.id)
            
        except Exception as e:
            logger.error(f"Error creating run: {str(e)}")
            return None
    
    async def create_feedback(
        self,
        run_id: str,
        key: str,
        score: float,
        value: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create feedback for a run"""
        
        if not self.is_available():
            return {"status": "monitoring_disabled"}
        
        try:
            feedback = self.client.create_feedback(
                run_id=run_id,
                key=key,
                score=score,
                value=value,
                comment=comment
            )
            
            return {
                "status": "feedback_created",
                "feedback_id": str(feedback.id)
            }
            
        except Exception as e:
            logger.error(f"Error creating feedback: {str(e)}")
            return {"status": "error", "error": str(e)}


# Global monitor instance
langsmith_monitor = LangSmithMonitor()