from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.models.data_models import RetrievedContext


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations in the RAG system
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass