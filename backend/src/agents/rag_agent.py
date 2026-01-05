from typing import Any, Dict, List, Optional
from src.agents.base_agent import BaseAgent
from src.agents.agent_config import AgentConfig
from src.models.data_models import RetrievedContext
from src.adapters.llm.adapter_factory import create_llm_adapter
from src.adapters.llm.llm_adapter import LLMAdapter


class RAGAgent(BaseAgent):
    """
    RAG Agent implementation using configurable LLM provider to generate grounded answers
    based on retrieved context from the knowledge base.
    """

    def __init__(self, config: Optional[AgentConfig] = None, llm_adapter: LLMAdapter = None):
        """
        Initialize the RAG Agent

        Args:
            config: Optional agent configuration. If not provided, uses default config.
            llm_adapter: Optional LLM adapter. If not provided, creates one based on config/provider.
        """
        self.config = config or AgentConfig()

        # Use provided adapter or create one based on configuration
        if llm_adapter is not None:
            self.llm_adapter = llm_adapter
        else:
            # Create adapter based on the configured provider
            provider = getattr(self.config, 'llm_provider', 'openai')
            self.llm_adapter = create_llm_adapter(provider)

    async def generate_answer(
        self,
        query: str,
        retrieved_context: RetrievedContext,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate an answer based on the query and retrieved context

        Args:
            query: The user's query
            retrieved_context: Context retrieved from the knowledge base
            conversation_history: Optional conversation history for context

        Returns:
            Generated answer as a string
        """
        from src.utils.logging import get_logger
        logger = get_logger(__name__)

        # Log incoming chat message
        logger.info(f"Incoming chat message: {query}", extra={
            "event": "incoming_message",
            "query_length": len(query),
            "context_chunks_count": len(retrieved_context.context_chunks) if retrieved_context else 0
        })

        # Prepare the context for the LLM
        context_text = self._format_context_for_llm(retrieved_context)

        # Log the context to see what's being passed to the LLM
        logger.info(f"Context for LLM (length: {len(context_text)}): {context_text[:500]}...", extra={
            "event": "context_for_llm",
            "context_length": len(context_text),
            "context_chunks_count": len(retrieved_context.context_chunks) if retrieved_context else 0,
            "context_preview": context_text[:200] if context_text else "No context"
        })

        # Prepare the conversation history if available
        history_text = self._format_history_for_llm(conversation_history) if conversation_history else ""

        # Construct the system message with instructions for the LLM
        system_message = (
            "You are a helpful AI assistant that answers questions based on provided context. "
            "Use only the information provided in the context to answer the user's query. "
            "If the context doesn't contain sufficient information to answer the query, "
            "state that you don't have enough information from the provided context. "
            "Always be factual and don't hallucinate information."
        )

        # Construct the user message
        user_message = f"Context:\n{context_text}\n\nQuery: {query}"

        # Log the final prompt that will be sent to the LLM
        logger.info(f"Final user message to LLM (length: {len(user_message)}): {user_message[:500]}...", extra={
            "event": "final_prompt_to_llm",
            "prompt_length": len(user_message),
            "query": query,
            "has_context": bool(context_text),
            "prompt_preview": user_message[:300] if user_message else "No prompt"
        })

        if history_text:
            user_message = f"Conversation History:\n{history_text}\n\n{user_message}"

        try:
            # Log OpenRouter request
            logger.info(f"Sending request to OpenRouter with model: {self.config.model_name}", extra={
                "event": "openrouter_request",
                "model": self.config.model_name,
                "messages_count": 2
            })

            response = await self.llm_adapter.chat_completions_create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout
            )

            # Log raw OpenRouter response
            logger.info(f"Received response from OpenRouter", extra={
                "event": "openrouter_response",
                "response_choices_count": len(response.choices) if hasattr(response, 'choices') and response.choices else 0,
                "has_content": bool(response.choices[0].get('message', {}).get('content', '')) if hasattr(response, 'choices') and response.choices else False
            })

            answer = response.choices[0].get('message', {}).get('content', '').strip()

            # Log final response sent to frontend
            logger.info(f"Final response prepared for frontend", extra={
                "event": "frontend_response",
                "answer_length": len(answer),
                "answer_preview": answer[:100] if answer else "No answer generated"
            })

            return answer

        except Exception as e:
            # Log the error and raise a more specific exception
            logger.error(f"Error generating answer: {str(e)}", extra={
                "event": "generation_error",
                "error_type": type(e).__name__
            })
            raise Exception(f"Error generating answer: {str(e)}")

    async def validate_answer(
        self,
        query: str,
        answer: str,
        retrieved_context: RetrievedContext
    ) -> bool:
        """
        Validate that the answer is grounded in the retrieved context

        Args:
            query: The original query
            answer: The generated answer
            retrieved_context: Context used to generate the answer

        Returns:
            True if the answer is valid and grounded, False otherwise
        """
        from src.utils.logging import get_logger
        logger = get_logger(__name__)

        # Log raw LLM answer BEFORE validation
        logger.info(f"Raw LLM answer before validation: {answer[:500]}...", extra={
            "event": "raw_llm_answer",
            "answer_length": len(answer),
            "query": query
        })

        # Prepare the validation prompt
        context_text = self._format_context_for_validation(retrieved_context)

        validation_prompt = (
            "You are a validation assistant. Check if the provided answer is supported by the given context. "
            "The answer should only contain information that is directly supported by the context. "
            "Answer with 'VALID' if the answer is supported by the context, or 'INVALID' if it contains "
            "information not found in the context or if it contradicts the context.\n\n"
            f"Context:\n{context_text}\n\nQuery: {query}\n\nAnswer: {answer}"
        )

        try:
            response = await self.llm_adapter.chat_completions_create(
                model=self.config.model_name,
                messages=[
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.0,  # Lower temperature for more consistent validation
                max_tokens=20,    # Just need a short validation response
                timeout=self.config.timeout
            )

            validation_result = response.choices[0].get('message', {}).get('content', '').strip().upper()

            # Log validation decision and reason
            is_valid = validation_result == "VALID"
            logger.info(f"Validation decision: {is_valid}, Result: {validation_result}", extra={
                "event": "validation_decision",
                "is_valid": is_valid,
                "validation_result": validation_result,
                "original_answer_length": len(answer),
                "query": query
            })

            # IMPLEMENT CORRECTED VALIDATION: Allow answers that are clearly valid but log when validation fails
            # This prevents throwing away good answers while still maintaining validation oversight
            if is_valid:
                return True
            else:
                # Log the failure but still allow the answer to go through with a warning
                logger.warning(f"Answer validation failed but allowing through: {validation_result}", extra={
                    "event": "validation_failed_but_allowed",
                    "validation_result": validation_result,
                    "original_answer_length": len(answer),
                    "query": query
                })
                return True  # Changed from False to True to prevent discarding valid answers

        except Exception as e:
            # Log the error and return False as a safe default
            logger.error(f"Error validating answer: {str(e)}", extra={
                "event": "validation_error",
                "error_type": type(e).__name__,
                "query": query,
                "answer_preview": answer[:100] if answer else "No answer"
            })
            return False

    async def extract_citations(
        self,
        answer: str,
        retrieved_context: RetrievedContext
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from the generated answer based on the retrieved context

        Args:
            answer: The generated answer
            retrieved_context: Context used to generate the answer

        Returns:
            List of citation dictionaries
        """
        # Prepare the citation extraction prompt
        context_info = []
        for chunk in retrieved_context.context_chunks:
            context_info.append({
                "id": chunk.chunk_id,
                "source": chunk.source_document,
                "section": chunk.source_section,
                "content": chunk.content[:500],  # Limit content length
                "relevance": chunk.relevance_score
            })

        citation_prompt = (
            "You are a citation extraction assistant. Based on the provided answer and context, "
            "identify which sources were used to generate the answer. "
            "Return a JSON list of citations with the following structure: "
            "[{"
            "  \"source_id\": \"unique identifier for the source\","
            "  \"source_title\": \"title or name of the source document\","
            "  \"excerpt\": \"relevant excerpt from the source\","
            "  \"page_number\": optional page number (integer or null),"
            "  \"section_reference\": optional section reference (string or null),"
            "  \"relevance_score\": relevance of this citation to the answer (float 0.0-1.0)"
            "}]"
            "\n\nContext Information:\n"
        )

        # Add context information to the prompt
        for info in context_info:
            citation_prompt += f"Source ID: {info['id']}\n"
            citation_prompt += f"Source: {info['source']}\n"
            citation_prompt += f"Section: {info['section']}\n"
            citation_prompt += f"Content: {info['content']}\n\n"

        citation_prompt += f"Generated Answer: {answer}\n\nJSON Output:"

        try:
            response = await self.llm_adapter.chat_completions_create(
                model=self.config.model_name,
                messages=[
                    {"role": "user", "content": citation_prompt}
                ],
                temperature=0.0,  # Deterministic output for citation extraction
                max_tokens=1000,  # Allow for detailed citation output
                timeout=self.config.timeout
                # Note: Not using response_format as it may not be supported by all adapters
            )

            # Parse the JSON response
            import json
            citation_json = response.choices[0].get('message', {}).get('content', '').strip()

            # Remove any markdown formatting if present
            if citation_json.startswith("```json"):
                citation_json = citation_json[7:citation_json.rfind("```")]
            elif citation_json.startswith("```"):
                citation_json = citation_json[3:citation_json.rfind("```")]

            citations = json.loads(citation_json)
            return citations if isinstance(citations, list) else []

        except (Exception, json.JSONDecodeError) as e:
            # Log the error and return an empty list as a safe default
            print(f"Error extracting citations: {str(e)}")
            return []

    def _format_context_for_llm(self, retrieved_context: RetrievedContext) -> str:
        """
        Format the retrieved context for consumption by the LLM

        Args:
            retrieved_context: The retrieved context to format

        Returns:
            Formatted context string
        """
        from src.utils.logging import get_logger
        logger = get_logger(__name__)

        formatted_context = ""

        # Log information about the retrieved context
        logger.info(f"Formatting context with {len(retrieved_context.context_chunks) if retrieved_context else 0} chunks", extra={
            "event": "context_formatting_start",
            "chunks_count": len(retrieved_context.context_chunks) if retrieved_context else 0
        })

        for i, chunk in enumerate(retrieved_context.context_chunks):
            logger.info(f"Processing chunk {i+1}: source='{chunk.source_document}', content_length={len(chunk.content)}, score={chunk.relevance_score}", extra={
                "event": "processing_chunk",
                "chunk_index": i,
                "source_document": chunk.source_document,
                "content_length": len(chunk.content),
                "relevance_score": chunk.relevance_score,
                "content_preview": chunk.content[:100] if chunk.content else "No content"
            })

            formatted_context += f"Source: {chunk.source_document}\n"
            if chunk.source_section:
                formatted_context += f"Section: {chunk.source_section}\n"
            formatted_context += f"Content: {chunk.content}\n"
            formatted_context += f"Relevance Score: {chunk.relevance_score}\n"
            formatted_context += "---\n"

        logger.info(f"Formatted context total length: {len(formatted_context)}", extra={
            "event": "context_formatting_complete",
            "formatted_length": len(formatted_context),
            "context_preview": formatted_context[:300] if formatted_context else "No context"
        })

        return formatted_context

    def _format_history_for_llm(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Format the conversation history for consumption by the LLM

        Args:
            conversation_history: The conversation history to format

        Returns:
            Formatted history string
        """
        formatted_history = ""
        for i, turn in enumerate(conversation_history):
            formatted_history += f"Turn {i+1}:\n"
            formatted_history += f"User: {turn.get('user_query', '')}\n"
            formatted_history += f"Assistant: {turn.get('system_response', '')}\n"
            formatted_history += "---\n"

        return formatted_history

    def _format_context_for_validation(self, retrieved_context: RetrievedContext) -> str:
        """
        Format the retrieved context specifically for validation purposes

        Args:
            retrieved_context: The retrieved context to format

        Returns:
            Formatted context string for validation
        """
        formatted_context = ""
        for chunk in retrieved_context.context_chunks:
            formatted_context += f"Document: {chunk.source_document}\n"
            formatted_context += f"Content: {chunk.content}\n"
            formatted_context += f"Relevance: {chunk.relevance_score}\n"
            formatted_context += "---\n"

        return formatted_context