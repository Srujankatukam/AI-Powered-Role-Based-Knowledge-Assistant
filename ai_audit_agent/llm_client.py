"""
LLM Client with Ollama Support
Supports both Hugging Face API and local Ollama
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from prompt_templates import get_audit_analysis_prompt

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM (Ollama or Hugging Face)"""
    
    def __init__(self):
        """Initialize LLM client with API credentials"""
        # Check if using Ollama
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        if self.use_ollama:
            # Ollama configuration
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
            self.model_url = f"{self.ollama_base_url}/api/generate"
            
            logger.info(f"Using Ollama - Model: {self.ollama_model} at {self.ollama_base_url}")
            
            self.headers = {
                "Content-Type": "application/json"
            }
        else:
            # Hugging Face configuration
            self.api_key = os.getenv("HF_API_KEY")
            default_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
            self.model_url = os.getenv("HF_MODEL_URL", default_url)
            
            if not self.model_url or "YOUR_API_URL" in self.model_url.upper():
                self.model_url = default_url
            
            if not self.api_key:
                logger.warning("HF_API_KEY not found in environment variables")
            
            logger.info(f"Using Hugging Face - Model: {self.model_url}")
            
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        self.max_retries = 3
        self.timeout = 120  # 2 minutes timeout
    
    async def generate_audit_analysis(self, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate AI audit analysis using LLM.
        
        Args:
            company_data: Dictionary containing company and department information
            
        Returns:
            Dictionary containing LLM analysis or None if failed
        """
        try:
            # Generate prompt
            prompt = get_audit_analysis_prompt(company_data)
            
            logger.info(f"Sending request to {'Ollama' if self.use_ollama else 'Hugging Face'}...")
            
            # Call LLM API with retries
            for attempt in range(self.max_retries):
                try:
                    if self.use_ollama:
                        response_text = await self._call_ollama_api(prompt, attempt + 1)
                    else:
                        response_text = await self._call_huggingface_api(prompt, attempt + 1)
                    
                    if response_text:
                        # Parse and validate JSON response
                        parsed_response = self._parse_llm_response(response_text)
                        
                        if parsed_response:
                            logger.info("Successfully generated audit analysis")
                            return parsed_response
                        else:
                            logger.warning(f"Attempt {attempt + 1}: Failed to parse LLM response")
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.info(f"Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
            
            # If all retries failed, return fallback response
            logger.error("All LLM API attempts failed, generating fallback response")
            return self._generate_fallback_response(company_data)
            
        except Exception as e:
            logger.error(f"Error in generate_audit_analysis: {str(e)}", exc_info=True)
            return self._generate_fallback_response(company_data)
    
    async def _call_ollama_api(self, prompt: str, attempt: int) -> Optional[str]:
        """
        Make API call to Ollama.
        
        Args:
            prompt: The prompt to send to the LLM
            attempt: Current attempt number
            
        Returns:
            Response text from LLM or None
        """
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 2048,
                "stop": ["<|eot_id|>", "<|end_of_text|>"]
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.model_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama returned status {response.status}: {error_text}")
                        return None
                    
                    result = await response.json()
                    
                    # Extract generated text from Ollama response
                    if isinstance(result, dict) and "response" in result:
                        return result["response"]
                    
                    logger.error(f"Unexpected Ollama response format: {result}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Ollama request timeout on attempt {attempt}")
            return None
        except aiohttp.ClientConnectorError:
            logger.error(f"Cannot connect to Ollama at {self.ollama_base_url}")
            logger.error("Make sure Ollama is running: ollama serve")
            return None
        except Exception as e:
            logger.error(f"Ollama API call error on attempt {attempt}: {str(e)}")
            return None
    
    async def _call_huggingface_api(self, prompt: str, attempt: int) -> Optional[str]:
        """
        Make API call to Hugging Face.
        
        Args:
            prompt: The prompt to send to the LLM
            attempt: Current attempt number
            
        Returns:
            Response text from LLM or None
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.1,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False,
                "stop": ["<|eot_id|>", "<|end_of_text|>"]
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.model_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 503:
                        logger.warning("Model is loading, waiting...")
                        await asyncio.sleep(20)
                        return None
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API returned status {response.status}: {error_text}")
                        return None
                    
                    result = await response.json()
                    
                    # Extract generated text
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    elif isinstance(result, dict):
                        return result.get("generated_text", "")
                    
                    logger.error(f"Unexpected API response format: {result}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Request timeout on attempt {attempt}")
            return None
        except Exception as e:
            logger.error(f"API call error on attempt {attempt}: {str(e)}")
            return None
    
    def _parse_llm_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse and validate LLM response.
        
        Args:
            response_text: Raw text response from LLM
            
        Returns:
            Parsed JSON dict or None if invalid
        """
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Find JSON object
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}")
            
            if start_idx == -1 or end_idx == -1:
                logger.error("No JSON object found in response")
                return None
            
            json_text = response_text[start_idx:end_idx + 1]
            
            # Parse JSON
            parsed = json.loads(json_text)
            
            # Validate structure
            if not self._validate_response_structure(parsed):
                logger.error("Response structure validation failed")
                return None
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return None
    
    def _validate_response_structure(self, response: Dict[str, Any]) -> bool:
        """
        Validate that the response has required fields.
        
        Args:
            response: Parsed response dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check summary section
            if "summary" not in response:
                logger.error("Missing 'summary' field")
                return False
            
            summary = response["summary"]
            required_summary_fields = ["personalized_summary", "overall_risk_score", "ai_maturity_level"]
            for field in required_summary_fields:
                if field not in summary:
                    logger.error(f"Missing '{field}' in summary")
                    return False
            
            # Check sections
            if "sections" not in response or not isinstance(response["sections"], list):
                logger.error("Missing or invalid 'sections' field")
                return False
            
            # Validate each section
            for section in response["sections"]:
                if not all(key in section for key in ["section_name", "level", "drawbacks"]):
                    logger.error("Section missing required fields")
                    return False
                
                if not isinstance(section["drawbacks"], list):
                    logger.error("Drawbacks must be a list")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False
    
    def _generate_fallback_response(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fallback response when LLM fails.
        
        Args:
            company_data: Original company data
            
        Returns:
            Fallback audit analysis
        """
        company_name = company_data.get('company_name', 'the organization')
        industry = company_data.get('industry', 'their industry')
        departments = company_data.get('departments', {})
        
        sections = []
        for dept_name in departments.keys():
            sections.append({
                "section_name": dept_name,
                "level": "Medium",
                "drawbacks": [
                    {
                        "title": "Limited Automation",
                        "details": f"The {dept_name} department shows opportunities for increased automation and AI integration."
                    },
                    {
                        "title": "Manual Data Processing",
                        "details": "Current processes rely on manual data handling, limiting scalability and real-time insights."
                    }
                ]
            })
        
        return {
            "summary": {
                "personalized_summary": f"{company_name} operates in the {industry} sector and demonstrates foundational digital capabilities. However, significant opportunities exist for AI integration across departments to enhance operational efficiency and decision-making capabilities.",
                "overall_risk_score": 60,
                "ai_maturity_level": "Medium"
            },
            "sections": sections
        }
