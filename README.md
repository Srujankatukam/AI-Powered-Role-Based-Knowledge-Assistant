# 🤖 AI-Powered Role-Based Knowledge Assistant    
      
An enterprise-grade AI assistant built with LangChain, FastAPI, and Streamlit that provides secure, role-based access to organizational knowledge through an agentic RAG pipeline. 

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg) 
![LangChain](https://img.shields.io/badge/LangChain-0.1.0-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)  
  
## 🌟 Features   
  
### 🔐 **Role-Based Access Control (RBAC)**
- **Employee**: Access to general company documents and policies
- **Manager**: Additional access to management-level information and team data
- **Admin**: Full system access including user management and analytics

### 🧠 **Agentic RAG Pipeline**
- **Intelligent Query Processing**: Uses LangChain agents to determine the best approach for each query
- **Multi-Source Retrieval**: Combines internal documents with web search when needed
- **Context-Aware Responses**: Maintains conversation history and provides contextual answers

### 📄 **Document Management**
- **Multi-Format Support**: PDF, DOCX, TXT, and Markdown files
- **Automated Processing**: Open-source embeddings with ChromaDB vector storage
- **Smart Chunking**: Optimized text segmentation for better retrieval
- **Access Control**: Department and role-based document access

### 🔍 **Advanced Search & Retrieval**
- **Vector Similarity Search**: Semantic search using open-source embeddings (Sentence Transformers)
- **Multiple Embedding Models**: Support for various models (MiniLM, MPNet, DistilRoBERTa)
- **Web Search Integration**: Tavily API for current information augmentation
- **Hybrid Approach**: Combines internal knowledge with external sources

### 🛡️ **Enterprise Security**
- **JWT Authentication**: Secure token-based authentication
- **Azure Key Vault Integration**: Centralized secret management
- **Data Encryption**: Secure handling of sensitive information
- **Audit Logging**: Comprehensive activity tracking

### 📊 **Monitoring & Analytics**
- **LangSmith Integration**: Advanced AI model monitoring and debugging
- **Performance Metrics**: Response times, accuracy scores, and usage analytics
- **System Health**: Real-time status monitoring and alerting
- **User Analytics**: Role-based usage patterns and insights

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        ST[Streamlit UI]
    end
    
    subgraph "API Layer"
        FA[FastAPI Backend]
        AUTH[JWT Authentication]
        RBAC[Role-Based Access Control]
    end
    
    subgraph "AI/ML Layer"
        LC[LangChain Agents]
        OAI[OpenAI GPT-4]
        EMB[Open Source Embeddings]
        ST[Sentence Transformers]
    end
    
    subgraph "Data Layer"
        VDB[ChromaDB Vector Store]
        PG[PostgreSQL Database]
        FS[File Storage]
    end
    
    subgraph "External Services"
        AKV[Azure Key Vault]
        WS[Web Search API]
        LS[LangSmith Monitoring]
    end
    
    ST --> FA
    FA --> AUTH
    AUTH --> RBAC
    FA --> LC
    LC --> OAI
    LC --> EMB
    EMB --> ST
    LC --> WS
    EMB --> VDB
    FA --> PG
    FA --> FS
    FA --> AKV
    LC --> LS
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key (Optional - only for GPT models)
- PostgreSQL (for production)

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/ai-knowledge-assistant.git
cd ai-knowledge-assistant
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys and configuration
nano .env
```

### 3. Deploy with Docker (Recommended)
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### 4. Access the Application
- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

## 🛠️ Development Setup

### Local Development
```bash
# Setup development environment
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# Activate virtual environment
source venv/bin/activate

# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (new terminal)
cd frontend
streamlit run streamlit_app.py
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here  # Optional - only for GPT models
SECRET_KEY=your_jwt_secret_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here

# Embedding Model Configuration
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/knowledge_assistant

# Azure Key Vault (Optional)
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
KEY_VAULT_URL=https://your-keyvault.vault.azure.net/

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## 📚 Usage Guide

### 1. User Registration & Authentication
```python
# Register a new user (first user becomes admin)
POST /auth/register
{
    "email": "admin@company.com",
    "username": "admin",
    "full_name": "System Administrator",
    "password": "secure_password",
    "role": "admin"
}

# Login
POST /auth/login
{
    "username": "admin",
    "password": "secure_password"
}
```

### 2. Document Upload
```python
# Upload a document
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: [PDF/DOCX/TXT file]
title: "Company Policy Manual"
access_level: "employee"
department: "HR"
```

### 3. Query the AI Assistant
```python
# Ask a question
POST /api/v1/query/ask
{
    "query": "What is our remote work policy?",
    "use_web_search": false,
    "max_results": 5
}
```

### 4. System Administration
```python
# Get system status (Manager/Admin only)
GET /api/v1/admin/system/status

# View analytics (Manager/Admin only)
GET /api/v1/admin/analytics

# Manage users (Admin only)
GET /api/v1/admin/users
POST /api/v1/admin/users
PUT /api/v1/admin/users/{user_id}
DELETE /api/v1/admin/users/{user_id}
```

## 🔧 Configuration

### Vector Database Configuration
```python
# ChromaDB settings
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7
```

### Embedding Models Configuration

The system supports multiple open-source embedding models:

#### Sentence Transformers Models
- **all-MiniLM-L6-v2** (Default): Fast, good performance, 384 dimensions
- **all-MiniLM-L12-v2**: Better performance, slower, 384 dimensions  
- **all-mpnet-base-v2**: Best performance, slowest, 768 dimensions
- **multi-qa-MiniLM-L6-cos-v1**: Optimized for Q&A tasks
- **paraphrase-multilingual-MiniLM-L12-v2**: Multilingual support

#### Configuration Examples
```env
# Fast and efficient (recommended for most use cases)
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# Best performance (requires more resources)
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=all-mpnet-base-v2
EMBEDDING_DEVICE=cuda

# HuggingFace Transformers
EMBEDDING_MODEL_TYPE=huggingface
HUGGINGFACE_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

### RAG Pipeline Configuration
```python
# LangChain settings
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=knowledge-assistant
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# OpenAI settings (Optional)
OPENAI_MODEL=gpt-4-turbo-preview

# Open Source Embedding Settings
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

## 📊 Monitoring & Analytics

### LangSmith Integration
The system integrates with LangSmith for comprehensive AI monitoring:

- **Query Tracking**: Monitor all user queries and responses
- **Performance Metrics**: Track response times and accuracy
- **Error Monitoring**: Identify and debug issues
- **Usage Analytics**: Understand user patterns and system load

### System Metrics
Access real-time metrics through the admin dashboard:

- **Document Statistics**: Total, indexed, and pending documents
- **User Analytics**: Active users, queries per role, session duration
- **System Health**: API response times, database performance
- **Security Metrics**: Failed login attempts, access violations

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Role-Based Access**: Granular permissions by user role
- **Session Management**: Secure session handling and expiration

### Data Protection
- **Azure Key Vault**: Centralized secret management
- **Encryption**: Data encryption in transit and at rest
- **Access Logging**: Comprehensive audit trails
- **Input Validation**: Protection against injection attacks

### Compliance
- **GDPR Ready**: User data management and deletion
- **SOC 2 Compatible**: Security controls and monitoring
- **Enterprise Security**: Role-based access and audit logging

## 🧪 Testing

### Run Tests
```bash
# Backend tests
pytest backend/tests/ -v

# Frontend tests
pytest frontend/tests/ -v

# Integration tests
pytest tests/integration/ -v

# Load testing
locust -f tests/load/locustfile.py
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=backend/app --cov-report=html backend/tests/
```

## 📈 Performance Optimization

### Vector Database Optimization
- **Index Tuning**: Optimized HNSW parameters for ChromaDB
- **Batch Processing**: Efficient document ingestion
- **Caching**: Redis integration for frequently accessed data

### API Performance
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Rate Limiting**: Protection against abuse
- **Response Compression**: Reduced bandwidth usage

### Scaling Considerations
- **Horizontal Scaling**: Multi-instance deployment support
- **Load Balancing**: Nginx reverse proxy configuration
- **Database Scaling**: PostgreSQL read replicas
- **Vector Store Scaling**: Distributed ChromaDB setup

## 🚀 Deployment

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Using Kubernetes
kubectl apply -f k8s/

# Using cloud services
# See deployment guides for AWS, Azure, GCP
```

### Environment-Specific Configurations
- **Development**: Local setup with hot reloading
- **Staging**: Production-like environment for testing
- **Production**: Optimized for performance and security

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- **Python**: Follow PEP 8 style guide
- **Type Hints**: Use type annotations
- **Documentation**: Docstrings for all functions
- **Testing**: Minimum 80% test coverage

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📋 API Reference

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update current user

### Document Management
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

### Query Processing
- `POST /api/v1/query/ask` - Query AI assistant
- `POST /api/v1/query/search` - Search documents
- `GET /api/v1/query/history` - Get chat history
- `DELETE /api/v1/query/history` - Clear chat history

### Administration
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users` - Create user
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user
- `GET /api/v1/admin/system/status` - System status
- `GET /api/v1/admin/analytics` - System analytics
- `GET /api/v1/admin/embedding-models` - Available embedding models
- `POST /api/v1/admin/embedding-models/reload` - Reload embedding service
- `GET /api/v1/admin/embedding-models/benchmark` - Benchmark embedding performance

## 🐛 Troubleshooting

### Common Issues

#### 1. Embedding Model Issues
```bash
# Check current embedding model
curl http://localhost:8000/api/v1/admin/embedding-models

# Benchmark embedding performance
curl http://localhost:8000/api/v1/admin/embedding-models/benchmark

# For GPU support, ensure CUDA is available
python -c "import torch; print(torch.cuda.is_available())"
```

#### 2. OpenAI API Errors (if using GPT models)
```bash
# Check API key (optional - only needed for GPT models)
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# The system works without OpenAI for embeddings
# Only GPT models require OpenAI API key
```

#### 3. Vector Database Issues
```bash
# Reset ChromaDB
rm -rf data/chroma_db
# Restart application to recreate
```

#### 4. Authentication Problems
```bash
# Check JWT secret
echo $SECRET_KEY

# Verify token expiration
# Default: 30 minutes
```

#### 5. Document Processing Failures
```bash
# Check file permissions
ls -la data/documents/

# Verify file formats
file data/documents/your-file.pdf
```

### Logs and Debugging
```bash
# View application logs
docker-compose logs -f backend

# Enable debug mode
export DEBUG=true

# Check system status
curl http://localhost:8000/health
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For the powerful AI framework
- **OpenAI**: For GPT-4 and embedding models
- **FastAPI**: For the high-performance web framework
- **Streamlit**: For the intuitive frontend framework
- **ChromaDB**: For the vector database solution

## 📞 Support

For support and questions:

- **Documentation**: Check this README and API docs
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: support@your-organization.com

---

**Built with ❤️ for enterprise AI applications**

*Reducing manual knowledge lookup by 60% and improving enterprise data accessibility and decision-making speed.*
