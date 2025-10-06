#!/bin/bash

# AI Knowledge Assistant Deployment Script

set -e

echo "🚀 Starting AI Knowledge Assistant Deployment"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    echo "Required variables: OPENAI_API_KEY, SECRET_KEY, TAVILY_API_KEY, LANGCHAIN_API_KEY"
    read -p "Press enter to continue after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/documents
mkdir -p data/chroma_db
mkdir -p data/embeddings
mkdir -p config/ssl

# Set permissions
chmod 755 data/documents
chmod 755 data/chroma_db
chmod 755 data/embeddings

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend
fi

# Check frontend
if curl -f http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    docker-compose logs frontend
fi

# Check database
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
    docker-compose logs postgres
fi

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend (Streamlit): http://localhost:8501"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Database: localhost:5432"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose logs -f [service_name]"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "📝 Next Steps:"
echo "   1. Visit http://localhost:8501 to access the frontend"
echo "   2. Register a new admin user"
echo "   3. Upload your first documents"
echo "   4. Start querying the AI assistant!"
echo ""

# Show running containers
echo "🐳 Running containers:"
docker-compose ps