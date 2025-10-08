"""
Open-source monitoring and observability service replacing LangSmith
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from contextlib import asynccontextmanager
import aiosqlite
from dataclasses import dataclass, asdict
from enum import Enum

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from ..core.config import settings

logger = logging.getLogger(__name__)


class RunStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MonitoringRun:
    """Data class for monitoring runs"""
    id: str
    name: str
    run_type: str
    status: RunStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    inputs: Dict[str, Any] = None
    outputs: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    user_id: Optional[int] = None
    user_role: Optional[str] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = {}
        if self.outputs is None:
            self.outputs = {}
        if self.metadata is None:
            self.metadata = {}


class PrometheusMetrics:
    """Prometheus metrics for monitoring"""
    
    def __init__(self):
        # Counters
        self.query_total = Counter(
            'knowledge_assistant_queries_total',
            'Total number of queries processed',
            ['user_role', 'status']
        )
        
        self.document_uploads_total = Counter(
            'knowledge_assistant_document_uploads_total',
            'Total number of documents uploaded',
            ['user_role', 'file_type', 'status']
        )
        
        self.llm_requests_total = Counter(
            'knowledge_assistant_llm_requests_total',
            'Total number of LLM requests',
            ['model_name', 'status']
        )
        
        self.embedding_requests_total = Counter(
            'knowledge_assistant_embedding_requests_total',
            'Total number of embedding requests',
            ['model_name', 'status']
        )
        
        # Histograms
        self.query_duration = Histogram(
            'knowledge_assistant_query_duration_seconds',
            'Query processing duration',
            ['user_role']
        )
        
        self.llm_duration = Histogram(
            'knowledge_assistant_llm_duration_seconds',
            'LLM processing duration',
            ['model_name']
        )
        
        self.embedding_duration = Histogram(
            'knowledge_assistant_embedding_duration_seconds',
            'Embedding processing duration',
            ['model_name']
        )
        
        self.document_processing_duration = Histogram(
            'knowledge_assistant_document_processing_duration_seconds',
            'Document processing duration',
            ['file_type']
        )
        
        # Gauges
        self.active_users = Gauge(
            'knowledge_assistant_active_users',
            'Number of active users'
        )
        
        self.total_documents = Gauge(
            'knowledge_assistant_total_documents',
            'Total number of documents in the system'
        )
        
        self.indexed_documents = Gauge(
            'knowledge_assistant_indexed_documents',
            'Number of indexed documents'
        )
    
    def record_query(self, user_role: str, duration: float, status: str = "success"):
        """Record a query metric"""
        self.query_total.labels(user_role=user_role, status=status).inc()
        self.query_duration.labels(user_role=user_role).observe(duration)
    
    def record_document_upload(self, user_role: str, file_type: str, duration: float, status: str = "success"):
        """Record a document upload metric"""
        self.document_uploads_total.labels(user_role=user_role, file_type=file_type, status=status).inc()
        self.document_processing_duration.labels(file_type=file_type).observe(duration)
    
    def record_llm_request(self, model_name: str, duration: float, status: str = "success"):
        """Record an LLM request metric"""
        self.llm_requests_total.labels(model_name=model_name, status=status).inc()
        self.llm_duration.labels(model_name=model_name).observe(duration)
    
    def record_embedding_request(self, model_name: str, duration: float, status: str = "success"):
        """Record an embedding request metric"""
        self.embedding_requests_total.labels(model_name=model_name, status=status).inc()
        self.embedding_duration.labels(model_name=model_name).observe(duration)
    
    def update_system_metrics(self, active_users: int, total_docs: int, indexed_docs: int):
        """Update system-level metrics"""
        self.active_users.set(active_users)
        self.total_documents.set(total_docs)
        self.indexed_documents.set(indexed_docs)
    
    def export_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        return generate_latest().decode('utf-8')


class SQLiteMonitoringStore:
    """SQLite-based storage for monitoring data"""
    
    def __init__(self, db_path: str = "./data/monitoring.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS monitoring_runs (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        run_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration REAL,
                        inputs TEXT,
                        outputs TEXT,
                        metadata TEXT,
                        error TEXT,
                        user_id INTEGER,
                        user_role TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_runs_start_time ON monitoring_runs(start_time)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_runs_user_role ON monitoring_runs(user_role)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_runs_status ON monitoring_runs(status)
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize monitoring database: {str(e)}")
    
    async def store_run(self, run: MonitoringRun):
        """Store a monitoring run"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO monitoring_runs 
                    (id, name, run_type, status, start_time, end_time, duration, 
                     inputs, outputs, metadata, error, user_id, user_role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run.id,
                    run.name,
                    run.run_type,
                    run.status.value,
                    run.start_time.isoformat(),
                    run.end_time.isoformat() if run.end_time else None,
                    run.duration,
                    json.dumps(run.inputs),
                    json.dumps(run.outputs),
                    json.dumps(run.metadata),
                    run.error,
                    run.user_id,
                    run.user_role
                ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store monitoring run: {str(e)}")
    
    async def get_runs(
        self, 
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[RunStatus] = None,
        user_role: Optional[str] = None
    ) -> List[MonitoringRun]:
        """Retrieve monitoring runs"""
        try:
            query = "SELECT * FROM monitoring_runs WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND start_time >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND start_time <= ?"
                params.append(end_time.isoformat())
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if user_role:
                query += " AND user_role = ?"
                params.append(user_role)
            
            query += " ORDER BY start_time DESC LIMIT ?"
            params.append(limit)
            
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    runs = []
                    for row in rows:
                        run = MonitoringRun(
                            id=row[0],
                            name=row[1],
                            run_type=row[2],
                            status=RunStatus(row[3]),
                            start_time=datetime.fromisoformat(row[4]),
                            end_time=datetime.fromisoformat(row[5]) if row[5] else None,
                            duration=row[6],
                            inputs=json.loads(row[7]) if row[7] else {},
                            outputs=json.loads(row[8]) if row[8] else {},
                            metadata=json.loads(row[9]) if row[9] else {},
                            error=row[10],
                            user_id=row[11],
                            user_role=row[12]
                        )
                        runs.append(run)
                    
                    return runs
                    
        except Exception as e:
            logger.error(f"Failed to retrieve monitoring runs: {str(e)}")
            return []
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Total runs by status
                async with db.execute("""
                    SELECT status, COUNT(*) FROM monitoring_runs 
                    WHERE start_time >= ? GROUP BY status
                """, (start_time.isoformat(),)) as cursor:
                    status_counts = dict(await cursor.fetchall())
                
                # Runs by user role
                async with db.execute("""
                    SELECT user_role, COUNT(*) FROM monitoring_runs 
                    WHERE start_time >= ? AND user_role IS NOT NULL 
                    GROUP BY user_role
                """, (start_time.isoformat(),)) as cursor:
                    role_counts = dict(await cursor.fetchall())
                
                # Average duration by run type
                async with db.execute("""
                    SELECT run_type, AVG(duration) FROM monitoring_runs 
                    WHERE start_time >= ? AND duration IS NOT NULL 
                    GROUP BY run_type
                """, (start_time.isoformat(),)) as cursor:
                    avg_durations = dict(await cursor.fetchall())
                
                # Error rate
                async with db.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as errors
                    FROM monitoring_runs 
                    WHERE start_time >= ?
                """, (start_time.isoformat(),)) as cursor:
                    total, errors = await cursor.fetchone()
                    error_rate = (errors / total * 100) if total > 0 else 0
                
                return {
                    "time_period_hours": hours,
                    "status_counts": status_counts,
                    "role_counts": role_counts,
                    "average_durations": avg_durations,
                    "error_rate_percent": error_rate,
                    "total_runs": total
                }
                
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {str(e)}")
            return {}


class OpenSourceMonitoringService:
    """Main open-source monitoring service"""
    
    def __init__(self):
        self.metrics = PrometheusMetrics()
        self.store = SQLiteMonitoringStore()
        self.active_runs: Dict[str, MonitoringRun] = {}
    
    def start_run(
        self,
        run_id: str,
        name: str,
        run_type: str,
        inputs: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None
    ) -> MonitoringRun:
        """Start a new monitoring run"""
        
        run = MonitoringRun(
            id=run_id,
            name=name,
            run_type=run_type,
            status=RunStatus.STARTED,
            start_time=datetime.now(),
            inputs=inputs or {},
            metadata=metadata or {},
            user_id=user_id,
            user_role=user_role
        )
        
        self.active_runs[run_id] = run
        
        # Store asynchronously
        asyncio.create_task(self.store.store_run(run))
        
        return run
    
    def end_run(
        self,
        run_id: str,
        status: RunStatus = RunStatus.COMPLETED,
        outputs: Dict[str, Any] = None,
        error: Optional[str] = None
    ) -> Optional[MonitoringRun]:
        """End a monitoring run"""
        
        if run_id not in self.active_runs:
            logger.warning(f"Run {run_id} not found in active runs")
            return None
        
        run = self.active_runs[run_id]
        run.status = status
        run.end_time = datetime.now()
        run.duration = (run.end_time - run.start_time).total_seconds()
        run.outputs = outputs or {}
        run.error = error
        
        # Remove from active runs
        del self.active_runs[run_id]
        
        # Update Prometheus metrics
        self._update_prometheus_metrics(run)
        
        # Store asynchronously
        asyncio.create_task(self.store.store_run(run))
        
        return run
    
    def _update_prometheus_metrics(self, run: MonitoringRun):
        """Update Prometheus metrics based on completed run"""
        status = "success" if run.status == RunStatus.COMPLETED else "failed"
        
        if run.run_type == "query":
            self.metrics.record_query(
                user_role=run.user_role or "unknown",
                duration=run.duration or 0,
                status=status
            )
        elif run.run_type == "document_upload":
            file_type = run.metadata.get("file_type", "unknown")
            self.metrics.record_document_upload(
                user_role=run.user_role or "unknown",
                file_type=file_type,
                duration=run.duration or 0,
                status=status
            )
        elif run.run_type == "llm_request":
            model_name = run.metadata.get("model_name", "unknown")
            self.metrics.record_llm_request(
                model_name=model_name,
                duration=run.duration or 0,
                status=status
            )
        elif run.run_type == "embedding_request":
            model_name = run.metadata.get("model_name", "unknown")
            self.metrics.record_embedding_request(
                model_name=model_name,
                duration=run.duration or 0,
                status=status
            )
    
    async def get_runs(self, **kwargs) -> List[MonitoringRun]:
        """Get monitoring runs"""
        return await self.store.get_runs(**kwargs)
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary"""
        return await self.store.get_metrics_summary(hours)
    
    def export_prometheus_metrics(self) -> str:
        """Export Prometheus metrics"""
        return self.metrics.export_metrics()
    
    @asynccontextmanager
    async def monitor_operation(
        self,
        name: str,
        run_type: str,
        inputs: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None
    ):
        """Context manager for monitoring operations"""
        
        import uuid
        run_id = str(uuid.uuid4())
        
        run = self.start_run(
            run_id=run_id,
            name=name,
            run_type=run_type,
            inputs=inputs,
            metadata=metadata,
            user_id=user_id,
            user_role=user_role
        )
        
        try:
            yield run
            self.end_run(run_id, RunStatus.COMPLETED)
        except Exception as e:
            self.end_run(run_id, RunStatus.FAILED, error=str(e))
            raise
    
    def update_system_metrics(self, active_users: int, total_docs: int, indexed_docs: int):
        """Update system-level metrics"""
        self.metrics.update_system_metrics(active_users, total_docs, indexed_docs)
    
    def get_active_runs(self) -> List[MonitoringRun]:
        """Get currently active runs"""
        return list(self.active_runs.values())


# Global monitoring service instance
_monitoring_service = None

def get_monitoring_service() -> OpenSourceMonitoringService:
    """Get the global monitoring service instance"""
    global _monitoring_service
    
    if _monitoring_service is None:
        _monitoring_service = OpenSourceMonitoringService()
        logger.info("Initialized open-source monitoring service")
    
    return _monitoring_service


# Decorator for monitoring functions
def monitor_function(name: str, run_type: str):
    """Decorator to monitor function execution"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            monitoring = get_monitoring_service()
            async with monitoring.monitor_operation(name, run_type):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            monitoring = get_monitoring_service()
            import uuid
            run_id = str(uuid.uuid4())
            
            run = monitoring.start_run(run_id, name, run_type)
            try:
                result = func(*args, **kwargs)
                monitoring.end_run(run_id, RunStatus.COMPLETED)
                return result
            except Exception as e:
                monitoring.end_run(run_id, RunStatus.FAILED, error=str(e))
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator