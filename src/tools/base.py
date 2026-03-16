from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique ID for the tool."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Clear description for RAG indexing."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool parameters."""
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """JSON schema for tool response."""
        pass

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Execute the tool's core logic."""
        pass
