from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """
    Abstract base class for all tools in the RAG system
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the tool
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        A description of what the tool does
        """
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema for the tool's parameters
        """
        pass

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """
        Execute the tool with the given parameters

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """
        pass