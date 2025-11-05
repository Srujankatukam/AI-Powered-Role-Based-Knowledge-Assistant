"""
AI Audit Agent - FastAPI Application
Handles webhook from Google Sheets, generates AI audit reports, and emails them.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
import uvicorn

from llm_client import LLMClient
from pdf_builder import PDFBuilder
from mailer import EmailService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Audit Agent",
    description="Automated AI Audit Report Generation and Delivery System",
    version="1.0.0"
)

# Initialize services
llm_client = LLMClient()
pdf_builder = PDFBuilder()
email_service = EmailService()


# Pydantic Models
class DepartmentData(BaseModel):
    """Model for department-specific data"""
    class Config:
        extra = "allow"  # Allow additional fields


class AuditRequest(BaseModel):
    """Model for incoming audit request from Google Sheets"""
    company_name: str = Field(..., min_length=1, description="Company name")
    recipient_name: str = Field(..., min_length=1, description="Recipient name")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    industry: str = Field(..., description="Industry type")
    company_size: str = Field(..., description="Company size category")
    annual_revenue_inr: str = Field(..., description="Annual revenue in INR")
    departments: Dict[str, DepartmentData] = Field(..., description="Department-wise data")

    @validator('departments')
    def validate_departments(cls, v):
        if not v:
            raise ValueError("At least one department must be provided")
        return v


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    service: str


class WebhookResponse(BaseModel):
    """Webhook response"""
    status: str
    message: str
    request_id: str
    timestamp: str


# Background Task Handler
async def process_audit_request(request_data: Dict[str, Any], request_id: str):
    """
    Background task to process audit request:
    1. Call LLM to generate analysis
    2. Create PDF with visualizations
    3. Send email with PDF attachment
    """
    try:
        logger.info(f"[{request_id}] Starting audit processing for {request_data['company_name']}")
        
        # Step 1: Generate LLM Analysis
        logger.info(f"[{request_id}] Calling LLM for analysis...")
        llm_response = await llm_client.generate_audit_analysis(request_data)
        
        if not llm_response:
            raise Exception("LLM returned empty response")
        
        logger.info(f"[{request_id}] LLM analysis completed successfully")
        
        # Step 2: Generate PDF with visualizations
        logger.info(f"[{request_id}] Generating PDF report...")
        pdf_path = pdf_builder.create_report(
            company_data=request_data,
            llm_analysis=llm_response,
            request_id=request_id
        )
        
        logger.info(f"[{request_id}] PDF generated at: {pdf_path}")
        
        # Step 3: Send Email
        logger.info(f"[{request_id}] Sending email to {request_data['recipient_email']}...")
        email_sent = email_service.send_report(
            recipient_email=request_data['recipient_email'],
            recipient_name=request_data['recipient_name'],
            company_name=request_data['company_name'],
            personalized_summary=llm_response['summary']['personalized_summary'],
            pdf_path=pdf_path
        )
        
        if email_sent:
            logger.info(f"[{request_id}] Email sent successfully to {request_data['recipient_email']}")
        else:
            logger.error(f"[{request_id}] Failed to send email")
        
        # Cleanup: Remove generated PDF after sending
        import os
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"[{request_id}] Cleaned up PDF file")
        
        logger.info(f"[{request_id}] Audit processing completed successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error processing audit request: {str(e)}", exc_info=True)


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Audit Agent"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Audit Agent"
    }


@app.post("/webhook/sheet-row", response_model=WebhookResponse)
async def webhook_sheet_row(
    request: AuditRequest,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint triggered by Google Sheets.
    Receives company data and initiates audit report generation.
    """
    try:
        # Generate unique request ID
        request_id = f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"[{request_id}] Received audit request for {request.company_name}")
        
        # Convert Pydantic model to dict for processing
        request_data = request.dict()
        
        # Add background task for processing
        background_tasks.add_task(process_audit_request, request_data, request_id)
        
        return {
            "status": "accepted",
            "message": f"Audit request accepted and being processed for {request.company_name}",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
