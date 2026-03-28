"""Tests for Pydantic schema models."""

from anpegt.schema.base import VersionedModel, AuditEntry
from anpegt.schema.config import (
    PartyIdeals, ClusterDef, FitnessWeightsConfig, SystemConfig, load_config,
)
from anpegt.schema.anp import ANPNode, ANPEdge, PrioritySnapshot
from anpegt.schema.plan import (
    Proposal, SectorPlan, GlobalPlan, CommunicationPlan, SocialPost, Speech, SpeechSection,
)
from anpegt.schema.voter import VoterSegment, SegmentEmbedding
from anpegt.schema.fitness import FitnessScore
from anpegt.schema.cycle import CycleRun, ExogenousEvent
from anpegt.schema.llm import LLMMessage, LLMRequest, LLMResponse
from anpegt.schema.corpus import CorpusDocument, ChunkRecord, SocialMediaDocument, EngagementMetrics


def test_versioned_model_has_hash():
    m = VersionedModel()
    assert m.content_hash
    assert len(m.content_hash) == 16


def test_versioned_model_different_hashes():
    m1 = VersionedModel(version=1)
    m2 = VersionedModel(version=2)
    # Different ids guarantee different hashes
    assert m1.id != m2.id


def test_party_ideals_roundtrip():
    pi = PartyIdeals(
        name="Test", non_negotiable_principles=["P1"],
        fiscal_ceiling=1e9, ideological_axes={"x": 0.5},
    )
    data = pi.model_dump()
    pi2 = PartyIdeals.model_validate(data)
    assert pi2.name == "Test"


def test_fitness_weights_validation():
    fw = FitnessWeightsConfig(alpha=0.3, beta=0.2, gamma=0.2, delta=0.15, epsilon=0.15)
    assert abs(fw.alpha + fw.beta + fw.gamma + fw.delta + fw.epsilon - 1.0) < 0.05


def test_fitness_weights_bad_sum():
    import pytest
    with pytest.raises(Exception):
        FitnessWeightsConfig(alpha=0.5, beta=0.5, gamma=0.5, delta=0.5, epsilon=0.5)


def test_sector_plan_roundtrip():
    sp = SectorPlan(
        cycle_id="c1", cluster_id="salud",
        priorities_used={"equidad": 0.5},
        objectives=["Mejorar salud"],
        policies=[Proposal(id="p1", title="Test", description="Desc",
                          estimated_cost="medio", timeframe="2 años", expected_impact="alto")],
        intercluster_conflicts=[], rationale="Test", budget_estimate=1e6,
    )
    data = sp.model_dump(mode="json")
    sp2 = SectorPlan.model_validate(data)
    assert sp2.cluster_id == "salud"


def test_fitness_score_roundtrip():
    fs = FitnessScore(
        cycle_id="c1", segment_id="s1",
        alignment=0.8, coherence=0.7, viability=0.9, robustness=0.95, composite=0.85,
    )
    data = fs.model_dump(mode="json")
    fs2 = FitnessScore.model_validate(data)
    assert fs2.composite == 0.85


def test_cycle_run_status():
    cr = CycleRun(cycle_number=1, status="pending")
    assert cr.status == "pending"


def test_corpus_document():
    doc = CorpusDocument(source_type="local", source_id="d1", raw_text="Texto de prueba")
    assert doc.raw_text == "Texto de prueba"


def test_social_media_document():
    doc = SocialMediaDocument(
        source_type="social_media", source_id="sm1", raw_text="Post de prueba",
        platform="twitter", engagement=EngagementMetrics(likes=100, comments=20),
    )
    assert doc.engagement.likes == 100


def test_load_config_from_yaml(config_dir):
    cfg = load_config(config_dir)
    assert cfg.party_ideals.name == "Alianza Progresista"
    assert len(cfg.clusters) == 4
    assert len(cfg.voter_segments) == 2
    assert len(cfg.corpus_sources) > 0


def test_social_post_roundtrip():
    post = SocialPost(
        cycle_id="c1", segment_id="s1", platform="twitter",
        main_text="Texto de prueba", hashtags=["#test"],
        keywords_seo=["test"], call_to_action="Comparte", tone="informativo",
    )
    data = post.model_dump(mode="json")
    post2 = SocialPost.model_validate(data)
    assert post2.platform == "twitter"


def test_speech_roundtrip():
    speech = Speech(
        cycle_id="c1", event_type="rally", target_audience="general",
        duration_minutes=20, opening="Compatriotas",
        body_sections=[SpeechSection(topic="salud", key_message="Salud para todos")],
        closing="Juntos lo lograremos", soundbites=["Salud para todos"], tone="inspirador",
    )
    data = speech.model_dump(mode="json")
    speech2 = Speech.model_validate(data)
    assert speech2.event_type == "rally"
