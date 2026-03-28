"""Base agent class for all ANPEGT-POL agents."""

import json
from typing import Optional

from pydantic import BaseModel

from anpegt.llm.base import LLMProvider
from anpegt.util.logging import get_logger

logger = get_logger("agents")


class BaseAgent:
    """Base class for all agents. Subclasses must define output_schema and build_prompt."""

    output_schema: type[BaseModel]  # Set by subclasses
    agent_name: str = "base"

    def __init__(
        self,
        llm: LLMProvider,
        config: dict | None = None,
        max_retries: int = 2,
    ):
        self.llm = llm
        self.config = config or {}
        self.max_retries = max_retries

    def build_prompt(self, context: dict) -> list[dict[str, str]]:
        """Build the messages list for the LLM. Must be overridden."""
        raise NotImplementedError

    def parse_response(self, raw: str) -> BaseModel:
        """Parse LLM response into the output schema."""
        data = json.loads(raw)
        return self.output_schema.model_validate(data)

    def run(self, context: dict) -> BaseModel:
        """Execute the agent: build prompt, call LLM, parse response."""
        messages = self.build_prompt(context)
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                raw = self.llm.complete(
                    messages, response_format=self.output_schema
                )
                result = self.parse_response(raw)
                logger.info(
                    f"Agent {self.agent_name} produced valid output",
                    extra={"agent_id": self.agent_name},
                )
                return result
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Agent {self.agent_name} attempt {attempt + 1} failed: {e}"
                )
        raise RuntimeError(
            f"Agent {self.agent_name} failed after {self.max_retries + 1} attempts: {last_error}"
        )
