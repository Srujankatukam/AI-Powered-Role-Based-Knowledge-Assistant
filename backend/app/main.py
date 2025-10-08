"""
Main FastAPI application
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from .core.config import settings
from .core.database import create_tables
from .api.auth.auth import router as auth_router
from .api.v1.documents import router as documents_router
from .api.v1.query import router as query_router
from .api.v1.admin import router as admin_router
from .services.open_source_monitoring import get_monitoring_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Knowledge Assistant API")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Initialize secrets
    try:
        from .services.azure_keyvault import secret_manager
        secrets_status = await secret_manager.initialize_secrets()
        logger.info(f"Secrets initialization status: {secrets_status}")
    except Exception as e:
        logger.warning(f"Failed to initialize secrets: {str(e)}")
    
    # Initialize vector database
    try:
        from .services.document_ingestion import VectorStoreService
        vector_store = VectorStoreService()
        logger.info("Vector database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {str(e)}")
    
    # Initialize monitoring service
    try:
        monitoring = get_monitoring_service()
        logger.info("Open-source monitoring service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize monitoring service: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Knowledge Assistant API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI-Powered Role-Based Knowledge Assistant
    
    An enterprise-grade AI assistant with:
    - Agentic RAG pipeline using LangChain
    - Role-based access control (Employee, Manager, Admin)
    - Document ingestion with OpenAI embeddings
    - Vector database storage and retrieval
    - Web search augmentation
    - Azure Key Vault integration
    - LangSmith monitoring
    """,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)


# Custom middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Knowledge Assistant API (100% Open Source)",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not settings.PROMETHEUS_METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    
    monitoring = get_monitoring_service()
    metrics_data = monitoring.export_prometheus_metrics()
    
    from fastapi import Response
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


# Include routers
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    documents_router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

app.include_router(
    query_router,
    prefix="/api/v1/query",
    tags=["Query Processing"]
)

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Administration"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )