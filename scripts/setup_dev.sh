#!/bin/bash

# Development Environment Setup Script

set -e

echo "🛠️  Setting up AI Knowledge Assistant Development Environment"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/documents
mkdir -p data/chroma_db
mkdir -p data/embeddings
mkdir -p backend/tests
mkdir -p frontend/tests

# Install pre-commit hooks (optional)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Installing pre-commit hooks..."
    pre-commit install
fi

# Set up database (if PostgreSQL is running)
if command -v psql &> /dev/null && pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "🗃️  Setting up database..."
    createdb knowledge_assistant 2>/dev/null || echo "Database already exists"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🚀 To start development:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Edit .env file with your API keys"
echo "   3. Start backend: cd backend && uvicorn app.main:app --reload"
echo "   4. Start frontend: cd frontend && streamlit run streamlit_app.py"
echo ""
echo "🧪 To run tests:"
echo "   pytest backend/tests/"
echo ""
echo "📚 Useful commands:"
echo "   Format code: black backend/ frontend/"
echo "   Lint code: flake8 backend/ frontend/"
echo "   Type check: mypy backend/"
echo ""