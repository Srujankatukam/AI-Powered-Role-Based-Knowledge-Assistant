"""
Open-source LLM service supporting multiple local inference engines
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import torch

# HuggingFace Transformers
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    pipeline, TextStreamer, BitsAndBytesConfig
)

# LangChain compatibility
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import Generation, LLMResult

# Ollama (optional)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# llama-cpp-python (optional)
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# ctransformers (optional)
try:
    from ctransformers import AutoModelForCausalLM as CTransformersModel
    CTRANSFORMERS_AVAILABLE = True
except ImportError:
    CTRANSFORMERS_AVAILABLE = False

from ..core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceLLM(LLM):
    """HuggingFace Transformers LLM implementation"""
    
    def __init__(
        self,
        model_name: str = "microsoft/DialoGPT-medium",
        device: str = "cpu",
        max_length: int = 512,
        temperature: float = 0.7,
        do_sample: bool = True,
        use_quantization: bool = False,
        cache_dir: Optional[str] = None
    ):
        super().__init__()
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.do_sample = do_sample
        self.use_quantization = use_quantization
        self.cache_dir = cache_dir or "./data/llm_models"
        
        # Create cache directory
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._initialize_model()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _initialize_model(self):
        """Initialize the HuggingFace model"""
        try:
            logger.info(f"Loading HuggingFace model: {self.model_name}")
            
            # Configure quantization if requested
            quantization_config = None
            if self.use_quantization and torch.cuda.is_available():
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            # Add padding token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                quantization_config=quantization_config,
                device_map="auto" if torch.cuda.is_available() else None,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            logger.info(f"Model loaded successfully on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace model: {str(e)}")
            # Create a simple fallback
            self._create_fallback_pipeline()
    
    def _create_fallback_pipeline(self):
        """Create a simple fallback pipeline for basic functionality"""
        try:
            logger.info("Creating fallback pipeline with distilgpt2")
            self.pipeline = pipeline(
                "text-generation",
                model="distilgpt2",
                device=-1  # CPU only
            )
        except Exception as e:
            logger.error(f"Failed to create fallback pipeline: {str(e)}")
            self.pipeline = None
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using the model"""
        if not self.pipeline:
            return "Error: Model not available. Please check the configuration."
        
        try:
            # Generate response
            response = self.pipeline(
                prompt,
                max_length=min(len(prompt.split()) + self.max_length, 1024),
                temperature=self.temperature,
                do_sample=self.do_sample,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
            
            # Extract generated text
            generated_text = response[0]["generated_text"]
            
            # Remove the original prompt from the response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            # Apply stop sequences
            if stop:
                for stop_seq in stop:
                    if stop_seq in generated_text:
                        generated_text = generated_text.split(stop_seq)[0]
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Async version of _call"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._call, prompt, stop, run_manager, **kwargs
        )
    
    @property
    def _llm_type(self) -> str:
        return "huggingface"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "quantization": self.use_quantization,
            "available": self.pipeline is not None
        }


class OllamaLLM(LLM):
    """Ollama LLM implementation for local models"""
    
    def __init__(
        self,
        model_name: str = "llama2:7b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        super().__init__()
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        
        if OLLAMA_AVAILABLE:
            self._initialize_client()
        else:
            logger.warning("Ollama not available. Install with: pip install ollama")
    
    def _initialize_client(self):
        """Initialize Ollama client"""
        try:
            self.client = ollama.Client(host=self.base_url)
            # Test connection
            self.client.list()
            logger.info(f"Ollama client initialized: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {str(e)}")
            self.client = None
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Ollama"""
        if not self.client:
            return "Error: Ollama not available. Please install and start Ollama server."
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "stop": stop or []
                }
            )
            
            return response.get("response", "No response generated")
            
        except Exception as e:
            logger.error(f"Error with Ollama generation: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Async version of _call"""
        # Ollama doesn't have native async support, so we use thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._call, prompt, stop, run_manager, **kwargs)
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Ollama model"""
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "available": self.client is not None
        }


class LlamaCppLLM(LLM):
    """llama-cpp-python LLM implementation"""
    
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        temperature: float = 0.7,
        max_tokens: int = 512,
        n_threads: Optional[int] = None
    ):
        super().__init__()
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n_threads = n_threads
        self.model = None
        
        if LLAMA_CPP_AVAILABLE:
            self._initialize_model()
        else:
            logger.warning("llama-cpp-python not available. Install with: pip install llama-cpp-python")
    
    def _initialize_model(self):
        """Initialize llama.cpp model"""
        try:
            if not Path(self.model_path).exists():
                logger.error(f"Model file not found: {self.model_path}")
                return
            
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
            
            logger.info(f"llama.cpp model loaded: {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load llama.cpp model: {str(e)}")
            self.model = None
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using llama.cpp"""
        if not self.model:
            return "Error: llama.cpp model not available."
        
        try:
            response = self.model(
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=stop or [],
                echo=False
            )
            
            return response["choices"][0]["text"].strip()
            
        except Exception as e:
            logger.error(f"Error with llama.cpp generation: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Async version of _call"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._call, prompt, stop, run_manager, **kwargs)
    
    @property
    def _llm_type(self) -> str:
        return "llama_cpp"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the llama.cpp model"""
        return {
            "model_path": self.model_path,
            "n_ctx": self.n_ctx,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "available": self.model is not None
        }


class OpenSourceLLMFactory:
    """Factory for creating open-source LLM instances"""
    
    @staticmethod
    def create_llm(llm_type: str = "huggingface", **kwargs) -> LLM:
        """Create an LLM instance based on type"""
        
        if llm_type.lower() == "huggingface":
            return HuggingFaceLLM(**kwargs)
        
        elif llm_type.lower() == "ollama":
            if not OLLAMA_AVAILABLE:
                logger.warning("Ollama not available, falling back to HuggingFace")
                return HuggingFaceLLM(**kwargs)
            return OllamaLLM(**kwargs)
        
        elif llm_type.lower() == "llama_cpp":
            if not LLAMA_CPP_AVAILABLE:
                logger.warning("llama-cpp-python not available, falling back to HuggingFace")
                return HuggingFaceLLM(**kwargs)
            return LlamaCppLLM(**kwargs)
        
        else:
            logger.warning(f"Unknown LLM type: {llm_type}, falling back to HuggingFace")
            return HuggingFaceLLM(**kwargs)
    
    @staticmethod
    def get_available_models() -> Dict[str, List[str]]:
        """Get list of available open-source models"""
        return {
            "huggingface": [
                "microsoft/DialoGPT-medium",  # Conversational
                "microsoft/DialoGPT-large",   # Better conversational
                "distilgpt2",                 # Fast, lightweight
                "gpt2",                       # Classic GPT-2
                "EleutherAI/gpt-neo-1.3B",   # Larger model
                "EleutherAI/gpt-j-6B",       # Even larger (requires GPU)
                "facebook/opt-1.3b",         # Meta's OPT model
                "bigscience/bloom-1b7",      # Multilingual
            ],
            "ollama": [
                "llama2:7b",                 # Llama 2 7B
                "llama2:13b",                # Llama 2 13B
                "mistral:7b",                # Mistral 7B
                "codellama:7b",              # Code Llama
                "neural-chat:7b",            # Intel's neural chat
                "zephyr:7b",                 # Zephyr 7B
            ],
            "llama_cpp": [
                "llama-2-7b-chat.gguf",     # Quantized Llama 2
                "mistral-7b-v0.1.gguf",     # Quantized Mistral
                "codellama-7b.gguf",        # Quantized Code Llama
            ]
        }
    
    @staticmethod
    def get_recommended_config() -> Dict[str, Any]:
        """Get recommended configuration based on system resources"""
        import psutil
        
        # Get system info
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()
        has_gpu = torch.cuda.is_available()
        
        if has_gpu and ram_gb >= 16:
            return {
                "llm_type": "huggingface",
                "model_name": "microsoft/DialoGPT-large",
                "device": "cuda",
                "use_quantization": True
            }
        elif ram_gb >= 8:
            return {
                "llm_type": "huggingface", 
                "model_name": "microsoft/DialoGPT-medium",
                "device": "cpu"
            }
        else:
            return {
                "llm_type": "huggingface",
                "model_name": "distilgpt2",
                "device": "cpu"
            }


# Global LLM instance
_llm_instance = None

def get_open_source_llm() -> LLM:
    """Get the global open-source LLM instance"""
    global _llm_instance
    
    if _llm_instance is None:
        # Get configuration from settings
        llm_config = {
            "llm_type": getattr(settings, 'LLM_TYPE', 'huggingface'),
            "model_name": getattr(settings, 'LLM_MODEL_NAME', 'microsoft/DialoGPT-medium'),
            "device": getattr(settings, 'LLM_DEVICE', 'cpu'),
            "temperature": getattr(settings, 'LLM_TEMPERATURE', 0.7),
            "max_length": getattr(settings, 'LLM_MAX_LENGTH', 512)
        }
        
        _llm_instance = OpenSourceLLMFactory.create_llm(**llm_config)
        logger.info(f"Initialized open-source LLM: {type(_llm_instance).__name__}")
    
    return _llm_instance

def reset_llm_instance():
    """Reset the global LLM instance"""
    global _llm_instance
    _llm_instance = None