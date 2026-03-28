"""Base models for ANPEGT-POL."""

import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class VersionedModel(BaseModel):
    """Base model with versioning, audit trail, and content hashing."""

    id: UUID = Field(default_factory=uuid4)
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: str = Field(default="")

    @model_validator(mode="after")
    def compute_hash(self) -> "VersionedModel":
        data = self.model_dump(exclude={"content_hash"})
        # Convert to stable string repr for hashing
        raw = str(sorted(str(data).encode()))
        self.content_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self


class AuditEntry(BaseModel):
    """Single entry in an audit trail."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    details: str
    agent_id: Optional[str] = None
