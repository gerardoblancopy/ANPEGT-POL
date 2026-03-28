"""Plan models for ANPEGT-POL (sector plans, global plans, communications)."""

from pydantic import BaseModel, Field

from .base import VersionedModel


class Proposal(BaseModel):
    """A concrete policy proposal within a sector plan."""

    id: str
    title: str
    description: str
    estimated_cost: str  # e.g. "alto", "medio", "bajo"
    timeframe: str
    expected_impact: str
    implementation_risk: str = Field(default="medio")


class InterclusterConflict(BaseModel):
    """A detected conflict between sector clusters."""

    with_cluster: str
    description: str
    severity: str = Field(default="medium")


class SectorPlan(VersionedModel):
    """Plan generated for a single thematic cluster/sector."""

    cycle_id: str
    cluster_id: str
    priorities_used: dict[str, float]
    objectives: list[str]
    policies: list[Proposal]
    intercluster_conflicts: list[InterclusterConflict]
    rationale: str
    budget_estimate: float = Field(default=0.0)


class ConflictResolution(BaseModel):
    """Record of how an intercluster conflict was resolved."""

    conflict: InterclusterConflict
    resolution: str
    priority_used: str


class GlobalPlan(VersionedModel):
    """Consolidated plan merging all sector plans."""

    cycle_id: str
    sector_plan_ids: list[str]
    consolidated_proposals: list[Proposal]
    conflicts_resolved: list[ConflictResolution]
    conflicts_unresolved: list[InterclusterConflict]
    global_budget: float
    coherence_score: float = Field(default=0.0)
    summary: str


class CommunicationPlan(VersionedModel):
    """Tailored communication plan for a voter segment."""

    cycle_id: str
    segment_id: str
    key_messages: list[str]
    tone: str
    emphasis_areas: list[str]
    full_text: str
    cluster_focus: list[str] = Field(default=[])


class SocialPost(VersionedModel):
    """Social-media post optimised for a specific platform and segment."""

    cycle_id: str
    segment_id: str
    platform: str
    main_text: str
    hashtags: list[str]
    keywords_seo: list[str]
    call_to_action: str
    suggested_visual: str = Field(default="")
    tone: str
    engagement_hooks: list[str] = Field(default=[])
    thread_pieces: list[str] = Field(default=[])
    best_posting_time: str = Field(default="")
    cluster_tags: list[str] = Field(default=[])


class SpeechSection(BaseModel):
    """A single section within a speech body."""

    topic: str
    key_message: str
    supporting_data: str = Field(default="")
    emotional_anchor: str = Field(default="")
    policy_reference: str = Field(default="")


class Speech(VersionedModel):
    """Full speech prepared for a specific event and audience."""

    cycle_id: str
    event_type: str
    target_audience: str
    duration_minutes: int
    opening: str
    body_sections: list[SpeechSection]
    closing: str
    soundbites: list[str]
    qa_preparation: list[dict[str, str]] = Field(default=[])
    tone: str
    territorial_references: list[str] = Field(default=[])
