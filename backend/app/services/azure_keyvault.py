"""
Azure Key Vault integration for secure secret management
"""
import asyncio
from typing import Optional, Dict, Any
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ResourceNotFoundError
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class AzureKeyVaultService:
    """Service for managing secrets in Azure Key Vault"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure Key Vault client"""
        if not settings.KEY_VAULT_URL:
            logger.warning("Azure Key Vault URL not configured. Secret management will be disabled.")
            return
        
        try:
            # Try different authentication methods
            if all([settings.AZURE_CLIENT_ID, settings.AZURE_CLIENT_SECRET, settings.AZURE_TENANT_ID]):
                # Use service principal authentication
                credential = ClientSecretCredential(
                    tenant_id=settings.AZURE_TENANT_ID,
                    client_id=settings.AZURE_CLIENT_ID,
                    client_secret=settings.AZURE_CLIENT_SECRET
                )
            else:
                # Use default credential chain (managed identity, Azure CLI, etc.)
                credential = DefaultAzureCredential()
            
            self.client = SecretClient(
                vault_url=settings.KEY_VAULT_URL,
                credential=credential
            )
            
            logger.info("Azure Key Vault client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Key Vault client: {str(e)}")
            self.client = None
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve a secret from Azure Key Vault"""
        if not self.client:
            logger.warning("Azure Key Vault client not available")
            return None
        
        try:
            # Run the synchronous operation in a thread pool
            secret = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_secret, secret_name
            )
            return secret.value
            
        except ResourceNotFoundError:
            logger.warning(f"Secret '{secret_name}' not found in Key Vault")
            return None
        except Exception as e:
            logger.error(f"Error retrieving secret '{secret_name}': {str(e)}")
            return None
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store a secret in Azure Key Vault"""
        if not self.client:
            logger.warning("Azure Key Vault client not available")
            return False
        
        try:
            # Run the synchronous operation in a thread pool
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.set_secret, secret_name, secret_value
            )
            logger.info(f"Secret '{secret_name}' stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error storing secret '{secret_name}': {str(e)}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret from Azure Key Vault"""
        if not self.client:
            logger.warning("Azure Key Vault client not available")
            return False
        
        try:
            # Run the synchronous operation in a thread pool
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.begin_delete_secret, secret_name
            )
            logger.info(f"Secret '{secret_name}' deleted successfully")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Secret '{secret_name}' not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting secret '{secret_name}': {str(e)}")
            return False
    
    async def list_secrets(self) -> Dict[str, Any]:
        """List all secrets in the Key Vault (names only, not values)"""
        if not self.client:
            logger.warning("Azure Key Vault client not available")
            return {}
        
        try:
            # Run the synchronous operation in a thread pool
            secret_properties = await asyncio.get_event_loop().run_in_executor(
                None, lambda: list(self.client.list_properties_of_secrets())
            )
            
            secrets_info = {}
            for secret_property in secret_properties:
                secrets_info[secret_property.name] = {
                    "created_on": secret_property.created_on.isoformat() if secret_property.created_on else None,
                    "updated_on": secret_property.updated_on.isoformat() if secret_property.updated_on else None,
                    "enabled": secret_property.enabled,
                    "expires_on": secret_property.expires_on.isoformat() if secret_property.expires_on else None
                }
            
            return secrets_info
            
        except Exception as e:
            logger.error(f"Error listing secrets: {str(e)}")
            return {}
    
    async def get_multiple_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        """Retrieve multiple secrets at once"""
        results = {}
        
        # Use asyncio.gather for concurrent retrieval
        tasks = [self.get_secret(name) for name in secret_names]
        values = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, value in zip(secret_names, values):
            if isinstance(value, Exception):
                logger.error(f"Error retrieving secret '{name}': {str(value)}")
                results[name] = None
            else:
                results[name] = value
        
        return results
    
    def is_available(self) -> bool:
        """Check if Azure Key Vault service is available"""
        return self.client is not None


class SecretManager:
    """High-level secret management with fallback to environment variables"""
    
    def __init__(self):
        self.keyvault_service = AzureKeyVaultService()
    
    async def get_secret(self, secret_name: str, fallback_env_var: str = None) -> Optional[str]:
        """
        Get secret from Key Vault with fallback to environment variable
        """
        # Try Azure Key Vault first
        if self.keyvault_service.is_available():
            secret_value = await self.keyvault_service.get_secret(secret_name)
            if secret_value:
                return secret_value
        
        # Fallback to environment variable
        if fallback_env_var:
            import os
            env_value = os.getenv(fallback_env_var)
            if env_value:
                logger.info(f"Using environment variable fallback for secret '{secret_name}'")
                return env_value
        
        logger.warning(f"Secret '{secret_name}' not found in Key Vault or environment")
        return None
    
    async def get_database_connection_string(self) -> Optional[str]:
        """Get database connection string from secure storage"""
        return await self.get_secret("database-connection-string", "DATABASE_URL")
    
    async def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from secure storage"""
        return await self.get_secret("openai-api-key", "OPENAI_API_KEY")
    
    async def get_jwt_secret_key(self) -> Optional[str]:
        """Get JWT secret key from secure storage"""
        return await self.get_secret("jwt-secret-key", "SECRET_KEY")
    
    async def get_tavily_api_key(self) -> Optional[str]:
        """Get Tavily API key from secure storage"""
        return await self.get_secret("tavily-api-key", "TAVILY_API_KEY")
    
    async def get_langsmith_api_key(self) -> Optional[str]:
        """Get LangSmith API key from secure storage"""
        return await self.get_secret("langsmith-api-key", "LANGCHAIN_API_KEY")
    
    async def initialize_secrets(self) -> Dict[str, bool]:
        """Initialize and validate all required secrets"""
        secrets_to_check = [
            ("database-connection-string", "DATABASE_URL"),
            ("openai-api-key", "OPENAI_API_KEY"),
            ("jwt-secret-key", "SECRET_KEY"),
            ("tavily-api-key", "TAVILY_API_KEY"),
            ("langsmith-api-key", "LANGCHAIN_API_KEY")
        ]
        
        results = {}
        for secret_name, env_var in secrets_to_check:
            secret_value = await self.get_secret(secret_name, env_var)
            results[secret_name] = secret_value is not None
        
        return results


# Global secret manager instance
secret_manager = SecretManager()