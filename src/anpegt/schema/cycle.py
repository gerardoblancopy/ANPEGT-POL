"""Cycle execution models for ANPEGT-POL."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .base import VersionedModel


class ExogenousEvent(BaseModel):
    """An external event that may affect cluster priorities."""

    id: str
    description: str
    timestamp: datetime
    affected_clusters: list[str]
    severity: str = Field(default="medium")


class ConflictRecord(BaseModel):
    """Record of a conflict detected during a cycle."""

    cycle_id: str
    clusters_involved: list[str]
    description: str
    resolved: bool
    resolution: Optional[str] = Field(default=None)


class CycleRun(VersionedModel):
    """Complete record of a single evolutionary cycle execution."""

    cycle_number: int
    status: Literal["pending", "running", "completed", "rolled_back"]
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    priority_snapshot_id: Optional[str] = Field(default=None)
    sector_plan_ids: list[str] = Field(default=[])
    global_plan_id: Optional[str] = Field(default=None)
    communication_plan_ids: list[str] = Field(default=[])
    social_post_ids: list[str] = Field(default=[])
    speech_ids: list[str] = Field(default=[])
    fitness_scores: list[str] = Field(default=[])
    exogenous_events: list[ExogenousEvent] = Field(default=[])
    metadata: dict = Field(default_factory=dict)
