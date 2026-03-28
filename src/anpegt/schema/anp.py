"""ANP (Analytic Network Process) models for ANPEGT-POL."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .base import VersionedModel


class ANPNode(VersionedModel):
    """A node in the ANP network (criterion, alternative, or strategic element)."""

    node_id: str
    name: str
    cluster_id: str
    node_type: Literal["criterion", "alternative", "strategic"]


class ANPEdge(BaseModel):
    """A directed, weighted edge between two ANP nodes."""

    source_id: str
    target_id: str
    weight: float


class ANPNetworkDef(BaseModel):
    """Complete definition of an ANP network."""

    nodes: list[ANPNode]
    edges: list[ANPEdge]
    clusters: list[dict[str, str]]  # each dict has "id" and "name"


class PrioritySnapshot(VersionedModel):
    """Snapshot of computed ANP priorities for a given cycle."""

    cycle_id: str
    node_priorities: dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
