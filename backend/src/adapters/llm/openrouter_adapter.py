"""
OpenRouter adapter that allows using OpenRouter API with the LLM adapter interface.
"""
from typing import Any, Dict, List, Optional
import httpx
from .llm_adapter import LLMAdapter, LLMResponse


class OpenRouterAdapter(LLMAdapter):
    """
    OpenRouter adapter implementation that uses the OpenRouter API
    while maintaining compatibility with the LLM adapter interface.
    """

    def __init__(self, api_key: str = None, model_name: str = "openai/gpt-4-turbo-preview"):
        """
        Initialize the OpenRouter adapter.

        Args:
            api_key: OpenRouter API key. If not provided, will use the one from settings.
            model_name: Model name to use with OpenRouter.
        """
        from ...config.settings import settings

        self.api_key = api_key or settings.openrouter_api_key
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required when using OpenRouter provider")

        self.model_name = model_name or settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"

    async def chat_completions_create(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Create a chat completion using the OpenRouter API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model name to use (if different from default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object compatible with OpenAI API response format
        """
        # Use provided model or default
        actual_model = model or self.model_name

        # Prepare the request parameters
        request_params = {
            "model": actual_model,
            "messages": messages,
        }

        if temperature is not None:
            request_params["temperature"] = temperature
        if max_tokens is not None:
            request_params["max_tokens"] = max_tokens

        # Add any additional parameters from kwargs
        request_params.update(kwargs)

        # Set timeout (default to 30 seconds if not specified)
        request_timeout = timeout or 30

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_params
                )

                if response.status_code != 200:
                    raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

                response_data = response.json()

                # Convert response to LLMResponse format compatible with OpenAI
                result = {
                    'id': response_data.get('id', ''),
                    'choices': [],
                    'created': response_data.get('created', 0),
                    'model': response_data.get('model', actual_model),
                    'object': response_data.get('object', 'chat.completion'),
                    'usage': response_data.get('usage', {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0
                    })
                }

                # Process choices
                for choice in response_data.get('choices', []):
                    choice_dict = {
                        'index': choice.get('index', 0),
                        'message': {
                            'role': choice.get('message', {}).get('role', 'assistant'),
                            'content': choice.get('message', {}).get('content', '')
                        },
                        'finish_reason': choice.get('finish_reason', 'stop')
                    }
                    result['choices'].append(choice_dict)

                return LLMResponse(result)

        except Exception as e:
            # Handle errors and return appropriate response
            error_response = {
                'choices': [
                    {
                        'index': 0,
                        'message': {
                            'role': 'assistant',
                            'content': f"Error calling OpenRouter API: {str(e)}"
                        },
                        'finish_reason': 'error'
                    }
                ],
                'model': actual_model,
                'object': 'chat.completion',
                'usage': {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0
                }
            }
            return LLMResponse(error_response)

    async def embeddings_create(
        self,
        input_text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Create embeddings using the OpenRouter API.

        Args:
            input_text: Text to generate embeddings for
            model: Model name to use (if different from default)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object compatible with OpenAI API response format
        """
        actual_model = model or self.model_name

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": actual_model,
                        "input": input_text,
                        **kwargs
                    }
                )

                if response.status_code != 200:
                    raise Exception(f"OpenRouter embeddings API error: {response.status_code} - {response.text}")

                response_data = response.json()

                # Convert response to LLMResponse format
                result = {
                    'data': [],
                    'model': response_data.get('model', actual_model),
                    'object': response_data.get('object', 'list'),
                    'usage': response_data.get('usage', {
                        'prompt_tokens': 0,
                        'total_tokens': 0
                    })
                }

                # Process data
                for item in response_data.get('data', []):
                    item_dict = {
                        'index': item.get('index', 0),
                        'object': item.get('object', 'embedding'),
                        'embedding': item.get('embedding', [])
                    }
                    result['data'].append(item_dict)

                return LLMResponse(result)

        except Exception as e:
            # Handle errors and return appropriate response
            error_response = {
                'data': [],
                'model': actual_model,
                'object': 'list',
                'error': {
                    'message': f"Error calling OpenRouter API for embeddings: {str(e)}"
                }
            }
            return LLMResponse(error_response)