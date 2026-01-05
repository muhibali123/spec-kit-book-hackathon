"""
Abstract base interface for LLM adapters.
This defines the contract that all LLM adapters must implement
to work with the OpenAI Agent SDK abstractions.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json


class LLMAdapter(ABC):
    """
    Abstract base class for LLM adapters that provide compatibility
    with OpenAI Agent SDK abstractions while using different LLM providers.
    """

    @abstractmethod
    async def chat_completions_create(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Create a chat completion using the LLM provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model name to use (if different from default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters

        Returns:
            Response object compatible with OpenAI API response format
        """
        pass

    @abstractmethod
    async def embeddings_create(
        self,
        input_text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Create embeddings using the LLM provider.

        Args:
            input_text: Text to generate embeddings for
            model: Model name to use (if different from default)
            **kwargs: Additional provider-specific parameters

        Returns:
            Response object compatible with OpenAI API response format
        """
        pass


class LLMResponse:
    """
    Wrapper class to provide OpenAI-compatible response format
    for responses from other LLM providers.
    """

    def __init__(self, response_data: Dict[str, Any]):
        self._data = response_data

    @property
    def choices(self) -> List:
        """Get the choices from the response (for chat completions)."""
        return self._data.get('choices', [])

    @property
    def data(self) -> List:
        """Get the data from the response (for embeddings)."""
        return self._data.get('data', [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        return self._data


def convert_openai_messages_to_gemini_format(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Convert OpenAI message format to Gemini format.

    OpenAI format: [{"role": "user", "content": "message"}]
    Gemini format: {"role": "user"|"model", "parts": ["message"]}

    Args:
        messages: List of messages in OpenAI format

    Returns:
        List of messages in Gemini format
    """
    gemini_messages = []

    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')

        # Convert role names to Gemini format
        if role == 'assistant':
            gemini_role = 'model'  # Gemini uses 'model' instead of 'assistant'
        elif role in ['user', 'system']:
            gemini_role = role
        else:
            # Default to user if unknown role
            gemini_role = 'user'

        gemini_messages.append({
            'role': gemini_role,
            'parts': [content]
        })

    return gemini_messages


def convert_gemini_response_to_openai_format(gemini_response: Any) -> Dict[str, Any]:
    """
    Convert Gemini API response to OpenAI-compatible format.

    Args:
        gemini_response: Response from Gemini API

    Returns:
        Dictionary in OpenAI API response format
    """
    # This is a simplified conversion - in practice, you'd extract the actual content
    # from the Gemini response object based on its actual structure
    try:
        # Extract text from Gemini response
        if hasattr(gemini_response, 'text'):
            content = gemini_response.text
        elif hasattr(gemini_response, 'candidates'):
            # If it's a GenerateContentResponse object
            if gemini_response.candidates:
                content = gemini_response.candidates[0].content.parts[0].text
            else:
                content = ""
        else:
            content = str(gemini_response)

        # Create OpenAI-compatible response format
        openai_format = {
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': content
                    },
                    'finish_reason': 'stop'
                }
            ],
            'model': 'gemini-converted',  # Placeholder for actual model info
            'object': 'chat.completion',
            'usage': {
                'prompt_tokens': 0,  # Placeholder
                'completion_tokens': 0,  # Placeholder
                'total_tokens': 0  # Placeholder
            }
        }

        return openai_format
    except Exception as e:
        # If conversion fails, return a minimal OpenAI-compatible structure
        return {
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': f"Error converting response: {str(e)}"
                    },
                    'finish_reason': 'stop'
                }
            ],
            'model': 'gemini-converted',
            'object': 'chat.completion',
            'usage': {
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0
            }
        }