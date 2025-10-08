# 🚀 Open Source Embeddings Guide

This guide explains how to use open-source embedding models instead of OpenAI embeddings in the AI Knowledge Assistant.

## 🌟 Overview

The system now supports multiple embedding options:
- **Sentence Transformers** (Default) - Fast, efficient, and high-quality
- **HuggingFace Transformers** - Flexible with many model options
- **OpenAI Embeddings** - Premium option (requires API key)

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Embedding Model Configuration
EMBEDDING_MODEL_TYPE=sentence-transformers  # Options: sentence-transformers, huggingface, openai
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2      # Model name for Sentence Transformers
HUGGINGFACE_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2  # Model name for HuggingFace
EMBEDDING_DEVICE=cpu                         # Options: cpu, cuda, mps
EMBEDDING_BATCH_SIZE=32                      # Batch size for processing

# OpenAI (Optional - only needed for GPT models and OpenAI embeddings)
OPENAI_API_KEY=your_openai_api_key_here
```

## 📊 Available Models

### Sentence Transformers Models

| Model | Size | Performance | Speed | Use Case |
|-------|------|-------------|-------|----------|
| `all-MiniLM-L6-v2` | 22MB | Good | Fast | **Default** - Best balance |
| `all-MiniLM-L12-v2` | 33MB | Better | Medium | Higher quality |
| `all-mpnet-base-v2` | 109MB | Best | Slow | Maximum quality |
| `multi-qa-MiniLM-L6-cos-v1` | 22MB | Good | Fast | Q&A optimized |
| `paraphrase-multilingual-MiniLM-L12-v2` | 109MB | Good | Medium | Multilingual |

### HuggingFace Models

| Model | Size | Performance | Use Case |
|-------|------|-------------|----------|
| `sentence-transformers/all-MiniLM-L6-v2` | 22MB | Good | General purpose |
| `sentence-transformers/all-mpnet-base-v2` | 109MB | Best | High quality |
| `distilbert-base-uncased` | 67MB | Good | BERT-based |
| `roberta-base` | 125MB | Better | RoBERTa-based |

## 🚀 Quick Start

### 1. Default Setup (Sentence Transformers)

```bash
# Set environment variables
export EMBEDDING_MODEL_TYPE=sentence-transformers
export EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
export EMBEDDING_DEVICE=cpu

# Start the application
docker-compose up -d
```

### 2. GPU Acceleration (if available)

```bash
# For NVIDIA GPUs
export EMBEDDING_DEVICE=cuda

# For Apple Silicon Macs
export EMBEDDING_DEVICE=mps
```

### 3. High-Performance Setup

```bash
# Use the best model with GPU
export EMBEDDING_MODEL_TYPE=sentence-transformers
export EMBEDDING_MODEL_NAME=all-mpnet-base-v2
export EMBEDDING_DEVICE=cuda
export EMBEDDING_BATCH_SIZE=64
```

## 🔍 Model Comparison

### Performance Benchmarks

| Model | Embedding Time (5 docs) | Query Time | Dimension | Memory Usage |
|-------|-------------------------|------------|-----------|--------------|
| all-MiniLM-L6-v2 | ~0.1s | ~0.02s | 384 | ~100MB |
| all-MiniLM-L12-v2 | ~0.2s | ~0.04s | 384 | ~150MB |
| all-mpnet-base-v2 | ~0.5s | ~0.1s | 768 | ~500MB |

### Quality Metrics

| Model | Semantic Similarity | Q&A Performance | Multilingual |
|-------|-------------------|-----------------|--------------|
| all-MiniLM-L6-v2 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| all-mpnet-base-v2 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| paraphrase-multilingual-* | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ |

## 🛠️ Advanced Configuration

### Custom Model Loading

```python
# In your configuration
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=your-custom-model-name
```

### Batch Processing Optimization

```bash
# For large document processing
EMBEDDING_BATCH_SIZE=64  # Increase for more memory/faster processing
EMBEDDING_BATCH_SIZE=8   # Decrease for less memory usage
```

### Device Selection

```bash
# Automatic device selection
EMBEDDING_DEVICE=auto

# Force CPU (most compatible)
EMBEDDING_DEVICE=cpu

# Use GPU if available (faster)
EMBEDDING_DEVICE=cuda

# Apple Silicon optimization
EMBEDDING_DEVICE=mps
```

## 📈 Performance Optimization

### Memory Optimization

1. **Use smaller models** for memory-constrained environments:
   ```bash
   EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
   ```

2. **Reduce batch size** if running out of memory:
   ```bash
   EMBEDDING_BATCH_SIZE=16
   ```

### Speed Optimization

1. **Use GPU acceleration**:
   ```bash
   EMBEDDING_DEVICE=cuda
   ```

2. **Increase batch size** (if you have enough memory):
   ```bash
   EMBEDDING_BATCH_SIZE=64
   ```

3. **Use faster models**:
   ```bash
   EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
   ```

## 🔧 API Endpoints

### Model Management

```bash
# Get available models
GET /api/v1/admin/embedding-models

# Reload embedding service
POST /api/v1/admin/embedding-models/reload

# Benchmark current model
GET /api/v1/admin/embedding-models/benchmark
```

### Example Responses

```json
{
  "current_model": {
    "model_name": "all-MiniLM-L6-v2",
    "device": "cpu",
    "embedding_dimension": 384,
    "batch_size": 32
  },
  "available_models": {
    "sentence_transformers": [
      "all-MiniLM-L6-v2",
      "all-mpnet-base-v2"
    ]
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Model Download Fails
```bash
# Solution: Check internet connection and disk space
# Models are downloaded to ./data/embeddings/sentence_transformers/
```

#### 2. CUDA Out of Memory
```bash
# Solution: Reduce batch size or use CPU
export EMBEDDING_DEVICE=cpu
export EMBEDDING_BATCH_SIZE=16
```

#### 3. Slow Performance
```bash
# Solution: Use GPU or smaller model
export EMBEDDING_DEVICE=cuda
export EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

#### 4. Import Errors
```bash
# Solution: Install missing dependencies
pip install sentence-transformers transformers torch
```

### Debugging

Enable debug logging:
```bash
export DEBUG=true
```

Check model loading:
```bash
# View logs
docker-compose logs backend | grep embedding
```

## 🔄 Migration from OpenAI

### Step 1: Update Configuration
```bash
# Change from OpenAI to Sentence Transformers
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

### Step 2: Re-index Documents
```bash
# Clear existing embeddings
rm -rf data/chroma_db/*

# Restart application to re-index
docker-compose restart backend
```

### Step 3: Test Performance
```bash
# Use the benchmark endpoint
curl -X GET "http://localhost:8000/api/v1/admin/embedding-models/benchmark" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Monitoring

### System Status

The admin dashboard shows:
- Current embedding model
- Device being used
- Embedding dimensions
- Processing performance

### Benchmarking

Regular benchmarking helps optimize performance:
- Document embedding speed
- Query embedding speed
- Memory usage
- Accuracy metrics

## 🌍 Multilingual Support

For multilingual documents:

```bash
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

Supported languages:
- English, German, French, Italian, Spanish
- Portuguese, Dutch, Polish, Russian
- Chinese, Japanese, Korean

## 🔒 Security Considerations

### Model Storage
- Models are cached locally in `./data/embeddings/`
- No data is sent to external services (unlike OpenAI)
- Complete privacy and data control

### Resource Usage
- Monitor CPU/GPU usage
- Set appropriate memory limits
- Consider rate limiting for API endpoints

## 📚 Additional Resources

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [HuggingFace Model Hub](https://huggingface.co/models)
- [Model Performance Comparison](https://www.sbert.net/docs/pretrained_models.html)

## 🤝 Contributing

To add new embedding models:

1. Update `EmbeddingServiceFactory.get_available_models()`
2. Test the new model
3. Update documentation
4. Submit a pull request

---

**🎉 Enjoy using open-source embeddings with complete privacy and control!**