# Frontend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Streamlit and required packages
RUN pip install --no-cache-dir \
    streamlit==1.29.0 \
    requests==2.31.0 \
    pandas==2.1.4 \
    plotly==5.17.0

# Copy frontend code
COPY frontend/streamlit_app.py .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]