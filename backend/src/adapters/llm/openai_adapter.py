"""
OpenAI adapter that maintains compatibility with the existing OpenAI Agent SDK
while using the LLM adapter interface.
"""
from typing import Any, Dict, List, Optional
import openai
from openai import OpenAI
from .llm_adapter import LLMAdapter, LLMResponse
from ..config.settings import settings


class OpenAIAdapter(LLMAdapter):
    """
    OpenAI adapter implementation that maintains compatibility with the existing
    OpenAI Agent SDK while using the LLM adapter interface.
    """

    def __init__(self):
        """
        Initialize the OpenAI adapter using the existing settings.
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model

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
        Create a chat completion using the OpenAI API.

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
        if timeout is not None:
            request_params["timeout"] = timeout

        # Add any additional parameters from kwargs
        request_params.update(kwargs)

        try:
            response = self.client.chat.completions.create(**request_params)

            # Convert response to LLMResponse format
            # We'll return the response as-is since it's already in OpenAI format
            response_dict = {
                'id': response.id,
                'choices': [],
                'created': response.created,
                'model': response.model,
                'object': response.object,
                'usage': {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                }
            }

            # Process choices
            for choice in response.choices:
                choice_dict = {
                    'index': choice.index,
                    'message': {
                        'role': choice.message.role,
                        'content': choice.message.content
                    },
                    'finish_reason': choice.finish_reason
                }
                response_dict['choices'].append(choice_dict)

            return LLMResponse(response_dict)

        except openai.APIError as e:
            # Handle errors and return appropriate response
            error_response = {
                'choices': [
                    {
                        'index': 0,
                        'message': {
                            'role': 'assistant',
                            'content': f"Error calling OpenAI API: {str(e)}"
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
        Create embeddings using the OpenAI API.

        Args:
            input_text: Text to generate embeddings for
            model: Model name to use (if different from default)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object compatible with OpenAI API response format
        """
        actual_model = model or self.model_name

        try:
            response = self.client.embeddings.create(
                input=input_text,
                model=actual_model,
                **kwargs
            )

            # Convert response to LLMResponse format
            response_dict = {
                'data': [],
                'model': response.model,
                'object': response.object,
                'usage': {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                }
            }

            # Process data
            for item in response.data:
                item_dict = {
                    'index': item.index,
                    'object': item.object,
                    'embedding': item.embedding
                }
                response_dict['data'].append(item_dict)

            return LLMResponse(response_dict)

        except openai.APIError as e:
            # Handle errors and return appropriate response
            error_response = {
                'data': [],
                'model': actual_model,
                'object': 'list',
                'error': {
                    'message': f"Error calling OpenAI API for embeddings: {str(e)}"
                }
            }
            return LLMResponse(error_response)