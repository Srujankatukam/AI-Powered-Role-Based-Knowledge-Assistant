# AI Audit Agent - Project Structure

Complete overview of the project structure and file organization.

## 📁 Directory Tree

```
ai_audit_agent/
├── main.py                      # FastAPI application entry point
├── llm_client.py               # Hugging Face LLM integration
├── pdf_builder.py              # PDF report generation with charts
├── mailer.py                   # Email delivery service
├── prompt_templates.py         # LLM prompt engineering
├── test_example.py             # Example test script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose orchestration
├── .env.example               # Environment variables template
├── README.md                  # Main documentation
├── PROJECT_STRUCTURE.md       # This file
└── docs/                      # Documentation directory
    ├── gs_script.txt          # Google Apps Script
    ├── SAMPLE_OUTPUT.json     # Example LLM output
    ├── API_DOCUMENTATION.md   # API reference
    ├── DEPLOYMENT_GUIDE.md    # Deployment instructions
    └── TESTING_GUIDE.md       # Testing procedures
```

## 📄 File Descriptions

### Core Application Files

#### `main.py`
**Purpose:** FastAPI application with webhook endpoint and background task processing

**Key Components:**
- FastAPI app initialization
- `/health` - Health check endpoint
- `/webhook/sheet-row` - Main webhook for receiving audit requests
- Background task processor for async LLM → PDF → Email workflow
- Global exception handler
- Pydantic models for request validation

**Dependencies:**
- FastAPI, Uvicorn
- Pydantic for validation
- llm_client, pdf_builder, mailer

**Lines of Code:** ~250

---

#### `llm_client.py`
**Purpose:** Interface with Hugging Face API for AI audit analysis

**Key Components:**
- `LLMClient` class
- `generate_audit_analysis()` - Main method to get LLM analysis
- API retry logic with exponential backoff
- Response parsing and validation
- Fallback response generation

**Features:**
- Async/await support
- Automatic retries (3 attempts)
- JSON response parsing
- Response structure validation
- Error handling with fallbacks

**Dependencies:**
- aiohttp for async HTTP
- prompt_templates for prompts

**Lines of Code:** ~300

---

#### `prompt_templates.py`
**Purpose:** LLM prompt engineering and template management

**Key Components:**
- `get_audit_analysis_prompt()` - Generate prompts from company data
- `get_system_instructions()` - System-level instructions

**Features:**
- Dynamic prompt generation
- Structured output requirements
- Assessment criteria definitions
- Department data formatting

**Lines of Code:** ~120

---

#### `pdf_builder.py`
**Purpose:** Generate professional PDF reports with visualizations

**Key Components:**
- `PDFBuilder` class
- Cover page generation
- Executive summary
- Visualization creation (bar chart, radar chart)
- Detailed analysis sections
- Custom styling

**Features:**
- ReportLab for PDF generation
- Matplotlib for charts
- Department-wise AI maturity bar chart
- Risk distribution radar chart
- Professional formatting
- Page numbering

**Dependencies:**
- ReportLab
- Matplotlib
- NumPy

**Lines of Code:** ~550

---

#### `mailer.py`
**Purpose:** Email delivery service for sending reports

**Key Components:**
- `EmailService` class
- SMTP configuration
- HTML email templates
- PDF attachment handling
- Connection testing

**Features:**
- Gmail SMTP support
- HTML and plain text emails
- Professional email templates
- PDF attachment
- Connection testing method

**Dependencies:**
- smtplib (standard library)
- email.mime modules

**Lines of Code:** ~250

---

#### `test_example.py`
**Purpose:** Quick test script for manual testing

**Key Components:**
- Health endpoint test
- Valid webhook test
- Invalid webhook test
- Colored terminal output
- Test summary

**Features:**
- Easy-to-run tests
- Visual feedback with colors
- Comprehensive test data
- Error reporting

**Lines of Code:** ~200

---

### Configuration Files

#### `requirements.txt`
**Purpose:** Python package dependencies

**Key Packages:**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- aiohttp==3.9.1
- reportlab==4.0.7
- matplotlib==3.8.2
- transformers==4.35.2
- pytest==7.4.3

**Total Dependencies:** 15+ packages

---

#### `Dockerfile`
**Purpose:** Container image definition

**Key Steps:**
1. Python 3.11 slim base
2. System dependencies installation
3. Python packages installation
4. Application code copying
5. Port exposure (8000)
6. Health check configuration
7. Uvicorn startup command

**Features:**
- Multi-stage optimization
- Health check included
- Non-root user (optional)
- Environment variables

---

#### `docker-compose.yml`
**Purpose:** Multi-container orchestration

**Configuration:**
- Service definition
- Port mapping (8000:8000)
- Environment variables
- Volume mounts
- Health checks
- Resource limits (4GB RAM, 2 CPU)
- Network configuration

---

#### `.env.example`
**Purpose:** Environment variables template

**Variables:**
- `HF_API_KEY` - Hugging Face API key
- `HF_MODEL_URL` - Model endpoint URL
- `SENDER_EMAIL` - Email sender address
- `SMTP_PASSWORD` - Email app password
- `SMTP_HOST` - SMTP server
- `SMTP_PORT` - SMTP port
- `LOG_LEVEL` - Logging level

---

### Documentation Files

#### `README.md`
**Purpose:** Main project documentation

**Sections:**
- Features overview
- Architecture diagram
- Prerequisites
- Quick start guide
- Docker deployment
- API endpoints
- Email configuration
- Google Sheets integration
- Testing instructions
- Troubleshooting
- Production deployment

**Length:** ~500 lines

---

#### `docs/API_DOCUMENTATION.md`
**Purpose:** Complete API reference

**Contents:**
- Endpoint descriptions
- Request/response schemas
- Examples in multiple languages
- Error handling
- Rate limiting
- Authentication
- Integration examples

**Length:** ~400 lines

---

#### `docs/DEPLOYMENT_GUIDE.md`
**Purpose:** Production deployment instructions

**Contents:**
- Docker deployment
- AWS EC2/ECS deployment
- Google Cloud Run
- Azure Container Instances
- VPS deployment
- Nginx configuration
- SSL setup
- Monitoring & logging
- Security checklist
- CI/CD pipeline

**Length:** ~600 lines

---

#### `docs/TESTING_GUIDE.md`
**Purpose:** Testing procedures and examples

**Contents:**
- Manual testing with cURL
- Automated testing with pytest
- Component testing
- Integration testing
- Load testing
- Debugging tips
- Test coverage goals

**Length:** ~500 lines

---

#### `docs/gs_script.txt`
**Purpose:** Google Apps Script for Sheets integration

**Contents:**
- Complete Apps Script code
- Configuration instructions
- Trigger setup guide
- Column header requirements
- Testing procedures
- Troubleshooting

**Length:** ~200 lines

---

#### `docs/SAMPLE_OUTPUT.json`
**Purpose:** Example LLM response format

**Contents:**
- Complete example response
- Field descriptions
- Sample department analysis
- Drawback examples

---

## 🔧 Technology Stack

### Backend Framework
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### AI/ML
- **Hugging Face API** - LLM inference
- **Mistral-7B-Instruct-v0.1** - Language model

### PDF & Visualization
- **ReportLab** - PDF generation
- **Matplotlib** - Chart creation
- **NumPy** - Numerical computations

### Communication
- **SMTP** - Email delivery
- **aiohttp** - Async HTTP client

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration

### Testing
- **pytest** - Testing framework
- **httpx** - HTTP testing

---

## 📊 Code Statistics

| Component | Lines of Code | Complexity |
|-----------|--------------|------------|
| main.py | ~250 | Medium |
| llm_client.py | ~300 | High |
| prompt_templates.py | ~120 | Low |
| pdf_builder.py | ~550 | High |
| mailer.py | ~250 | Medium |
| test_example.py | ~200 | Low |
| **Total** | **~1,670** | **Medium-High** |

---

## 🔄 Data Flow

```
1. Google Sheets
   ↓ (Apps Script Trigger)
2. POST /webhook/sheet-row
   ↓ (Request Validation)
3. Background Task Initiated
   ↓
4. LLM Client → Hugging Face API
   ↓ (Analysis Response)
5. PDF Builder → Generate Report
   ↓ (Create Charts & PDF)
6. Mailer → Send Email
   ↓
7. Cleanup & Logging
```

---

## 🎯 Key Design Patterns

### 1. **Separation of Concerns**
- Each module has a single responsibility
- Clear interfaces between components

### 2. **Async/Await Pattern**
- Non-blocking I/O operations
- Background task processing
- Concurrent API calls

### 3. **Dependency Injection**
- Services initialized at startup
- Easy to test and mock

### 4. **Template Method Pattern**
- PDF generation steps
- Email creation process

### 5. **Retry Pattern**
- LLM API calls with exponential backoff
- Error recovery

### 6. **Factory Pattern**
- Dynamic prompt generation
- Flexible department handling

---

## 🔒 Security Considerations

1. **Environment Variables**
   - Secrets stored in .env
   - Never committed to version control

2. **Input Validation**
   - Pydantic models for type checking
   - Email validation
   - Required field enforcement

3. **Error Handling**
   - Global exception handler
   - Graceful degradation
   - Fallback responses

4. **Resource Management**
   - Temporary file cleanup
   - Memory limits in Docker
   - Connection pooling

---

## 🚀 Performance Characteristics

### Average Processing Times
- **Health Check:** < 10ms
- **Webhook Acceptance:** < 50ms
- **LLM Analysis:** 10-30 seconds
- **PDF Generation:** 5-10 seconds
- **Email Delivery:** 2-5 seconds
- **Total:** 30-60 seconds

### Resource Usage
- **RAM:** 1-2 GB (with LLM cache)
- **CPU:** 0.5-1 core average
- **Disk:** < 100 MB per report (temporary)
- **Network:** ~1-5 MB per request

---

## 📈 Scalability

### Current Limits
- Sequential processing per request
- Single-instance deployment
- No caching

### Scaling Options
1. **Horizontal Scaling**
   - Multiple container instances
   - Load balancer
   - Shared storage for PDFs

2. **Vertical Scaling**
   - Increase memory/CPU
   - Better LLM performance

3. **Optimization**
   - LLM response caching
   - PDF template preloading
   - Connection pooling

---

## 🛠️ Development Workflow

1. **Local Development**
   ```bash
   python main.py  # Run locally
   ```

2. **Testing**
   ```bash
   pytest          # Run tests
   python test_example.py  # Quick test
   ```

3. **Docker Build**
   ```bash
   docker build -t ai-audit-agent .
   ```

4. **Docker Run**
   ```bash
   docker-compose up -d
   ```

5. **Deployment**
   - Push to registry
   - Deploy to cloud
   - Configure domain/SSL

---

## 📝 Maintenance

### Regular Tasks
- [ ] Update dependencies monthly
- [ ] Review logs weekly
- [ ] Monitor API limits
- [ ] Backup configurations
- [ ] Update documentation

### Monitoring Points
- Health endpoint status
- LLM API response times
- Email delivery rates
- Error rates
- Resource usage

---

## 🤝 Contributing

To contribute to this project:

1. Understand the architecture
2. Follow code style guidelines
3. Add tests for new features
4. Update documentation
5. Submit pull request

---

## 📞 Support & Contact

For questions about the project structure:
1. Review this document
2. Check specific file documentation
3. Review API documentation
4. Check deployment guide

---

**Last Updated:** 2024-01-15
**Version:** 1.0.0
