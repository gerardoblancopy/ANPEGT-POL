"""Anthropic (Claude) LLM provider for ANPEGT-POL."""

import json
from typing import Optional

from pydantic import BaseModel


class AnthropicProvider:
    """Wraps the ``anthropic`` SDK.  The package is imported lazily so the
    module can be loaded even when ``anthropic`` is not installed.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None,
        max_tokens: int = 4096,
    ):
        self.model = model
        self._api_key = api_key
        self.max_tokens = max_tokens
        self._client: Optional[object] = None

    # ------------------------------------------------------------------
    # Lazy client initialisation
    # ------------------------------------------------------------------

    def _get_client(self):  # noqa: ANN202
        if self._client is None:
            try:
                import anthropic  # noqa: WPS433
            except ImportError as exc:
                raise ImportError(
                    "The 'anthropic' package is required for AnthropicProvider. "
                    "Install it with: pip install anthropic"
                ) from exc
            kwargs: dict = {}
            if self._api_key:
                kwargs["api_key"] = self._api_key
            self._client = anthropic.Anthropic(**kwargs)
        return self._client

    # ------------------------------------------------------------------
    # Protocol-required method
    # ------------------------------------------------------------------

    def complete(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[type[BaseModel]] = None,
        temperature: float = 0.7,
    ) -> str:
        """Send *messages* to the Anthropic API and return raw text.

        The Anthropic Messages API uses a separate ``system`` parameter
        rather than a system message in the messages list, so this method
        extracts any leading system message before calling the API.

        When *response_format* is provided the schema is injected as a
        system-level instruction asking the model to reply exclusively with
        valid JSON matching the schema.
        """
        client = self._get_client()

        # Separate system prompt from conversation messages.
        system_text = ""
        conversation: list[dict[str, str]] = []
        for msg in messages:
            if msg["role"] == "system":
                system_text += msg["content"] + "\n"
            else:
                conversation.append(msg)

        # Inject JSON schema instruction when structured output is expected.
        if response_format is not None:
            schema_json = json.dumps(
                response_format.model_json_schema(), ensure_ascii=False
            )
            system_text += (
                "\n\nIMPORTANTE: Responde EXCLUSIVAMENTE con un JSON válido "
                "(sin markdown, sin texto adicional) que cumpla exactamente "
                f"este esquema JSON:\n{schema_json}"
            )

        # Ensure there is at least one user message.
        if not conversation:
            conversation = [{"role": "user", "content": "Genera la respuesta."}]

        call_kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "messages": conversation,
        }
        if system_text.strip():
            call_kwargs["system"] = system_text.strip()

        response = client.messages.create(**call_kwargs)

        # Extract text from the first content block.
        raw_text = response.content[0].text

        # Strip possible markdown fences that the model may wrap around JSON.
        stripped = raw_text.strip()
        if stripped.startswith("```"):
            lines = stripped.split("\n")
            # Remove first line (```json or ```) and last line (```)
            lines = [
                l for i, l in enumerate(lines)
                if not (i == 0 or (i == len(lines) - 1 and l.strip() == "```"))
            ]
            stripped = "\n".join(lines)

        return stripped
