"""
Environment configuration loader for the embeddings generation module.
"""
import os
from typing import Optional
from dotenv import load_dotenv


class EnvironmentConfig:
    """
    Configuration class that loads environment variables with defaults.
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Cohere API configuration
        self.cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
        self.cohere_model: str = os.getenv("COHERE_MODEL", "embed-english-v3.0")
        self.batch_size: int = int(os.getenv("BATCH_SIZE", "64"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay: int = int(os.getenv("RETRY_DELAY", "1000"))  # in milliseconds

        # Validate required configuration
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

    def validate_config(self) -> bool:
        """
        Validate the configuration values.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not self.cohere_api_key:
            return False
        if self.batch_size <= 0 or self.batch_size > 96:  # Cohere API limit
            return False
        if self.max_retries < 0:
            return False
        if self.retry_delay < 0:
            return False

        return True


# Global configuration instance
config = EnvironmentConfig()