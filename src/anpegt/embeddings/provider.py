"""Embedding provider protocol and implementations."""
import hashlib
from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class EmbeddingProvider(Protocol):
    dimensionality: int

    def embed(self, text: str) -> list[float]: ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class MockEmbeddingProvider:
    """Deterministic mock embeddings based on text hash. For testing only."""

    def __init__(self, dimensionality: int = 128):
        self.dimensionality = dimensionality

    def embed(self, text: str) -> list[float]:
        # Generate deterministic vector from text hash
        h = hashlib.sha256(text.encode("utf-8")).digest()
        rng = np.random.RandomState(int.from_bytes(h[:4], "big"))
        vec = rng.randn(self.dimensionality).astype(np.float32)
        vec = vec / np.linalg.norm(vec)  # normalize
        return vec.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class HuggingFaceEmbeddingProvider:
    """Uses Recognai/bert-base-spanish-wwm-cased-xnli for Spanish text embeddings."""

    def __init__(
        self,
        model_name: str = "Recognai/bert-base-spanish-wwm-cased-xnli",
        dimensionality: int = 768,
    ):
        self.dimensionality = dimensionality
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        if self._model is None:
            try:
                from transformers import AutoModel, AutoTokenizer

                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModel.from_pretrained(self.model_name)
                self._model.eval()
            except ImportError:
                raise ImportError(
                    "Install embeddings dependencies: pip install anpegt-pol[embeddings]"
                )

    def embed(self, text: str) -> list[float]:
        self._load_model()
        import torch  # noqa: F811

        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512, padding=True
        )
        with torch.no_grad():
            outputs = self._model(**inputs)
        # Mean pooling over last hidden state
        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        vec = (token_embeddings * input_mask_expanded).sum(
            1
        ) / input_mask_expanded.sum(1).clamp(min=1e-9)
        vec = vec.squeeze().numpy()
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def get_embedding_provider(config) -> EmbeddingProvider:
    """Factory to create embedding provider from config."""
    # config is an EmbeddingsConfig object with provider, model, dimensionality, pooling
    if config.provider == "mock":
        return MockEmbeddingProvider(dimensionality=config.dimensionality)
    elif config.provider == "huggingface":
        return HuggingFaceEmbeddingProvider(
            model_name=config.model, dimensionality=config.dimensionality
        )
    else:
        raise ValueError(f"Unknown embedding provider: {config.provider}")
