from typing import Dict, List, Optional, Type
from src.tools.base_tool import BaseTool


class ToolRegistry:
    """
    Registry for managing and accessing tools in the RAG system
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool instance in the registry

        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool

    def register_tool_class(self, name: str, tool_class: Type[BaseTool]) -> None:
        """
        Register a tool class in the registry

        Args:
            name: Name to register the tool class under
            tool_class: Tool class to register
        """
        self._tool_classes[name] = tool_class

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get a registered tool by name

        Args:
            name: Name of the tool to retrieve

        Returns:
            Tool instance if found, None otherwise
        """
        return self._tools.get(name)

    def get_tool_class(self, name: str) -> Optional[Type[BaseTool]]:
        """
        Get a registered tool class by name

        Args:
            name: Name of the tool class to retrieve

        Returns:
            Tool class if found, None otherwise
        """
        return self._tool_classes.get(name)

    def create_tool(self, name: str, *args, **kwargs) -> Optional[BaseTool]:
        """
        Create a tool instance from a registered class

        Args:
            name: Name of the tool class to instantiate
            *args: Positional arguments to pass to the constructor
            **kwargs: Keyword arguments to pass to the constructor

        Returns:
            Tool instance if class is found, None otherwise
        """
        tool_class = self._tool_classes.get(name)
        if tool_class:
            return tool_class(*args, **kwargs)
        return None

    def list_tool_names(self) -> List[str]:
        """
        Get a list of all registered tool names

        Returns:
            List of tool names
        """
        return list(self._tools.keys()) + list(self._tool_classes.keys())

    def list_tools(self) -> List[BaseTool]:
        """
        Get a list of all registered tool instances

        Returns:
            List of tool instances
        """
        return list(self._tools.values())

    def is_tool_registered(self, name: str) -> bool:
        """
        Check if a tool is registered (either as instance or class)

        Args:
            name: Name of the tool to check

        Returns:
            True if the tool is registered, False otherwise
        """
        return name in self._tools or name in self._tool_classes