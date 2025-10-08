"""
Open-source embedding service using Sentence Transformers and HuggingFace models
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from pathlib import Path
import torch
from concurrent.futures import ThreadPoolExecutor
import time

# Sentence Transformers
from sentence_transformers import SentenceTransformer

# HuggingFace Transformers
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F

# LangChain compatibility
from langchain.embeddings.base import Embeddings

from ..core.config import settings

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddings(Embeddings):
    """Sentence Transformers embedding service"""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        batch_size: int = 32,
        cache_folder: Optional[str] = None
    ):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.cache_folder = cache_folder or "./data/embeddings/sentence_transformers"
        
        # Create cache directory
        Path(self.cache_folder).mkdir(parents=True, exist_ok=True)
        
        # Initialize model
        self.model = None
        self._initialize_model()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def _initialize_model(self):
        """Initialize the Sentence Transformer model"""
        try:
            logger.info(f"Loading Sentence Transformer model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_folder
            )
            logger.info(f"Model loaded successfully on device: {self.device}")
            
            # Test the model with a simple embedding
            test_embedding = self.model.encode("test", show_progress_bar=False)
            logger.info(f"Model test successful. Embedding dimension: {len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentence Transformer model: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        if not self.model:
            raise ValueError("Model not initialized")
        
        try:
            # Process in batches
            all_embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                all_embeddings.extend(batch_embeddings.tolist())
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating document embeddings: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        if not self.model:
            raise ValueError("Model not initialized")
        
        try:
            embedding = self.model.encode(
                text,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async version of embed_documents"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.embed_documents, texts)
    
    async def aembed_query(self, text: str) -> List[float]:
        """Async version of embed_query"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.embed_query, text)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {"status": "not_initialized"}
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown'),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "batch_size": self.batch_size
        }


class HuggingFaceEmbeddings(Embeddings):
    """HuggingFace Transformers embedding service"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        batch_size: int = 32,
        max_length: int = 512
    ):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.max_length = max_length
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self._initialize_model()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def _initialize_model(self):
        """Initialize the HuggingFace model and tokenizer"""
        try:
            logger.info(f"Loading HuggingFace model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Move model to device
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.cuda()
            elif self.device == "mps" and torch.backends.mps.is_available():
                self.model = self.model.to("mps")
            
            self.model.eval()
            logger.info(f"HuggingFace model loaded successfully on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace model: {str(e)}")
            raise
    
    def _mean_pooling(self, model_output, attention_mask):
        """Mean pooling to get sentence embeddings"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def _encode_texts(self, texts: List[str]) -> List[List[float]]:
        """Encode texts using HuggingFace model"""
        all_embeddings = []
        
        with torch.no_grad():
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                
                # Tokenize
                encoded_input = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                
                # Move to device
                if self.device == "cuda":
                    encoded_input = {k: v.cuda() for k, v in encoded_input.items()}
                elif self.device == "mps":
                    encoded_input = {k: v.to("mps") for k, v in encoded_input.items()}
                
                # Get model output
                model_output = self.model(**encoded_input)
                
                # Mean pooling
                sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
                
                # Normalize embeddings
                sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
                
                # Convert to CPU and list
                batch_embeddings = sentence_embeddings.cpu().numpy().tolist()
                all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")
        
        return self._encode_texts(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")
        
        embeddings = self._encode_texts([text])
        return embeddings[0]
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async version of embed_documents"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.embed_documents, texts)
    
    async def aembed_query(self, text: str) -> List[float]:
        """Async version of embed_query"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.embed_query, text)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {"status": "not_initialized"}
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "batch_size": self.batch_size,
            "vocab_size": self.tokenizer.vocab_size if self.tokenizer else "unknown"
        }


class EmbeddingServiceFactory:
    """Factory class to create embedding services based on configuration"""
    
    @staticmethod
    def create_embedding_service() -> Embeddings:
        """Create an embedding service based on configuration"""
        
        embedding_type = settings.EMBEDDING_MODEL_TYPE.lower()
        
        if embedding_type == "sentence-transformers":
            return SentenceTransformerEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                device=settings.EMBEDDING_DEVICE,
                batch_size=settings.EMBEDDING_BATCH_SIZE
            )
        
        elif embedding_type == "huggingface":
            return HuggingFaceEmbeddings(
                model_name=settings.HUGGINGFACE_MODEL_NAME,
                device=settings.EMBEDDING_DEVICE,
                batch_size=settings.EMBEDDING_BATCH_SIZE
            )
        
        elif embedding_type == "openai":
            # Fallback to OpenAI if configured
            if settings.OPENAI_API_KEY:
                from langchain_openai import OpenAIEmbeddings
                return OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model="text-embedding-ada-002"
                )
            else:
                logger.warning("OpenAI API key not configured, falling back to Sentence Transformers")
                return SentenceTransformerEmbeddings(
                    model_name=settings.EMBEDDING_MODEL_NAME,
                    device=settings.EMBEDDING_DEVICE,
                    batch_size=settings.EMBEDDING_BATCH_SIZE
                )
        
        else:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
    
    @staticmethod
    def get_available_models() -> Dict[str, List[str]]:
        """Get list of available embedding models"""
        return {
            "sentence_transformers": [
                "all-MiniLM-L6-v2",  # Fast, good performance
                "all-MiniLM-L12-v2",  # Better performance, slower
                "all-mpnet-base-v2",  # Best performance, slowest
                "multi-qa-MiniLM-L6-cos-v1",  # Optimized for Q&A
                "paraphrase-multilingual-MiniLM-L12-v2",  # Multilingual
                "all-distilroberta-v1",  # Good balance
            ],
            "huggingface": [
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-mpnet-base-v2",
                "microsoft/DialoGPT-medium",
                "distilbert-base-uncased",
                "roberta-base",
            ]
        }


# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> Embeddings:
    """Get the global embedding service instance"""
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingServiceFactory.create_embedding_service()
        logger.info(f"Initialized embedding service: {type(_embedding_service).__name__}")
    
    return _embedding_service

def reset_embedding_service():
    """Reset the global embedding service (useful for testing)"""
    global _embedding_service
    _embedding_service = None