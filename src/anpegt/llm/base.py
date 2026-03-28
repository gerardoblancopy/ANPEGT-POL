"""Abstract LLM provider protocol."""

from typing import Optional, Protocol, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol that all LLM providers must satisfy."""

    def complete(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[type[BaseModel]] = None,
        temperature: float = 0.7,
    ) -> str:
        """Send messages to LLM and return raw text response."""
        ...
