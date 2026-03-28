"""LLM interaction models for ANPEGT-POL."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """A single message in an LLM conversation."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMRequest(BaseModel):
    """Request payload for an LLM call."""

    messages: list[LLMMessage]
    temperature: float = Field(default=0.7)
    response_format: Optional[str] = Field(default=None)


class LLMResponse(BaseModel):
    """Response from an LLM call."""

    content: str
    model: str = Field(default="")
    usage: dict = Field(default_factory=dict)
