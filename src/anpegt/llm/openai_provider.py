"""OpenAI LLM provider for ANPEGT-POL."""

import json
from typing import Optional

from pydantic import BaseModel


class OpenAIProvider:
    """Wraps the ``openai`` SDK. The package is imported lazily so the module
    can be loaded even when ``openai`` is not installed.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.model = model
        self._api_key = api_key
        self._base_url = base_url
        self._default_temperature = temperature
        self._client: Optional[object] = None

    # ------------------------------------------------------------------
    # Lazy client initialisation
    # ------------------------------------------------------------------

    def _get_client(self):  # noqa: ANN202
        if self._client is None:
            try:
                import openai  # noqa: WPS433
            except ImportError as exc:
                raise ImportError(
                    "The 'openai' package is required for OpenAIProvider. "
                    "Install it with: pip install openai"
                ) from exc
            kwargs: dict = {}
            if self._api_key:
                kwargs["api_key"] = self._api_key
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = openai.OpenAI(**kwargs)
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
        """Send *messages* to the OpenAI API and return the raw text response.

        When *response_format* is a Pydantic model the provider attempts to
        use the OpenAI structured-output ``response_format`` parameter.  If
        that is not available (older models) it falls back to injecting a
        JSON instruction into the system prompt.
        """
        client = self._get_client()

        call_kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if response_format is not None:
            # Try structured output first (supported by gpt-4o and later).
            try:
                call_kwargs["response_format"] = response_format
                response = client.beta.chat.completions.parse(**call_kwargs)
                return response.choices[0].message.content
            except Exception:
                # Fallback: inject JSON schema into system prompt.
                del call_kwargs["response_format"]
                schema_json = json.dumps(
                    response_format.model_json_schema(), ensure_ascii=False
                )
                json_instruction = (
                    "\n\nResponde EXCLUSIVAMENTE con un JSON válido que cumpla "
                    f"este esquema:\n{schema_json}"
                )
                patched_messages = list(messages)
                if patched_messages and patched_messages[0]["role"] == "system":
                    patched_messages[0] = {
                        "role": "system",
                        "content": patched_messages[0]["content"] + json_instruction,
                    }
                else:
                    patched_messages.insert(
                        0,
                        {"role": "system", "content": json_instruction.strip()},
                    )
                call_kwargs["messages"] = patched_messages

        response = client.chat.completions.create(**call_kwargs)
        return response.choices[0].message.content
