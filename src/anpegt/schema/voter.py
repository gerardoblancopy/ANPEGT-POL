"""Voter segment models for ANPEGT-POL."""

from typing import Optional

from pydantic import BaseModel, Field

from .base import VersionedModel


class VoterSegment(BaseModel):
    """A voter segment with demographic and preference information."""

    id: str
    name: str
    description: str
    size_fraction: float
    priority_issues: list[str]


class SegmentEmbedding(VersionedModel):
    """Embedding vector representing a voter segment's position in issue space."""

    segment_id: str
    cycle_id: str
    vector: list[float]
    displacement_from_previous: Optional[float] = Field(default=None)
