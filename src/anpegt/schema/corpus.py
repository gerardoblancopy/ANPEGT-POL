"""Corpus and document models for ANPEGT-POL."""

from datetime import datetime

from pydantic import BaseModel, Field

from .base import VersionedModel


class CorpusDocument(VersionedModel):
    """A document ingested from an external corpus source."""

    source_type: str
    source_id: str
    raw_text: str
    cleaned_text: str = Field(default="")
    metadata: dict = Field(
        default_factory=dict
    )  # fecha, autor, medio, url, ubicacion, etc.
    cluster_tags: list[str] = Field(default=[])
    segment_tags: list[str] = Field(default=[])
    ingested_at: datetime = Field(default_factory=datetime.utcnow)


class ChunkRecord(VersionedModel):
    """A chunk of a document, optionally with its embedding."""

    document_id: str
    chunk_index: int
    text: str
    embedding: list[float] = Field(default=[])
    cluster_tags: list[str] = Field(default=[])
    segment_tags: list[str] = Field(default=[])


class EngagementMetrics(BaseModel):
    """Engagement metrics for a social-media document."""

    likes: int = Field(default=0)
    comments: int = Field(default=0)
    shares: int = Field(default=0)
    reach: int = Field(default=0)
    engagement_rate: float = Field(default=0.0)
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)


class SocialMediaDocument(CorpusDocument):
    """A social-media post ingested as a corpus document."""

    platform: str
    post_url: str = Field(default="")
    engagement: EngagementMetrics = Field(default_factory=EngagementMetrics)
    audience_comments: list[str] = Field(default=[])
