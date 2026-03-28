"""In-memory vector store using numpy for cosine similarity search."""

import json
from pathlib import Path
from typing import Optional, Union

import numpy as np


class InMemoryVectorStore:
    """Simple vector store backed by a numpy matrix. Persists to .npz on flush."""

    def __init__(self, persist_path: str = "vectors.npz") -> None:
        self.persist_path = Path(persist_path)
        self._ids: list[str] = []
        self._vectors: Optional[np.ndarray] = None  # shape: (n, dim)
        self._metadata: dict[str, dict] = {}  # id -> metadata dict
        self._load()

    def _load(self) -> None:
        if self.persist_path.exists() and self.persist_path.stat().st_size > 0:
            try:
                data = np.load(self.persist_path, allow_pickle=True)
                self._vectors = data["vectors"]
                self._ids = data["ids"].tolist()
                if "metadata" in data:
                    self._metadata = json.loads(str(data["metadata"]))
            except (EOFError, ValueError):
                pass  # Empty or corrupted file, start fresh

    def add(
        self,
        id: str,
        vector: Union[list[float], np.ndarray],
        metadata: Optional[dict] = None,
    ) -> None:
        """Add a vector with an identifier and optional metadata."""
        vec = np.array(vector, dtype=np.float32).reshape(1, -1)
        if self._vectors is None:
            self._vectors = vec
        else:
            self._vectors = np.vstack([self._vectors, vec])
        self._ids.append(id)
        if metadata:
            self._metadata[id] = metadata

    def query(
        self,
        vector: Union[list[float], np.ndarray],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """Return the top-k most similar vectors by cosine similarity."""
        if self._vectors is None or len(self._ids) == 0:
            return []
        q = np.array(vector, dtype=np.float32).reshape(1, -1)
        # Cosine similarity
        norms_db = np.linalg.norm(self._vectors, axis=1, keepdims=True)
        norm_q = np.linalg.norm(q)
        if norm_q == 0:
            return []
        # Avoid division by zero
        norms_db = np.where(norms_db == 0, 1e-10, norms_db)
        similarities = (self._vectors @ q.T / (norms_db * norm_q)).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(self._ids[i], float(similarities[i])) for i in top_indices]

    def get_vector(self, id: str) -> Optional[np.ndarray]:
        """Retrieve the stored vector for a given identifier."""
        if id in self._ids:
            idx = self._ids.index(id)
            return self._vectors[idx] if self._vectors is not None else None
        return None

    def flush(self) -> None:
        """Persist vectors, ids, and metadata to disk as a .npz file."""
        if self._vectors is not None:
            np.savez(
                self.persist_path,
                vectors=self._vectors,
                ids=np.array(self._ids),
                metadata=json.dumps(self._metadata),
            )

    def __len__(self) -> int:
        return len(self._ids)
