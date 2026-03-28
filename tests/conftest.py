"""Shared test fixtures for ANPEGT-POL."""

import os
import tempfile
from pathlib import Path

import pytest

from anpegt.schema.config import (
    ClusterDef,
    EmbeddingsConfig,
    FitnessWeightsConfig,
    GuardrailsConfig,
    LLMConfig,
    PartyIdeals,
    SegmentUpdateConfig,
    SystemConfig,
    VoterSegmentDef,
)
from anpegt.store.sqlite_store import SQLiteStore
from anpegt.store.vector_store import InMemoryVectorStore
from anpegt.llm.mock_provider import MockLLMProvider
from anpegt.embeddings.provider import MockEmbeddingProvider


@pytest.fixture
def party_ideals():
    return PartyIdeals(
        name="Alianza Test",
        non_negotiable_principles=["Salud universal", "Acción climática"],
        fiscal_ceiling=100_000_000_000,
        ideological_axes={"economic_left_right": -0.3},
    )


@pytest.fixture
def clusters():
    return [
        ClusterDef(id="salud", name="Salud", description="Salud pública", keywords=["salud", "hospital"]),
        ClusterDef(id="educacion", name="Educación", description="Educación pública", keywords=["educación", "escuela"]),
    ]


@pytest.fixture
def voter_segments():
    return [
        VoterSegmentDef(
            id="seg_a", name="Segmento A", description="Test A",
            size_fraction=0.5, priority_issues=["salud", "clima"],
            initial_embedding_seed="Votante preocupado por salud y clima",
        ),
        VoterSegmentDef(
            id="seg_b", name="Segmento B", description="Test B",
            size_fraction=0.5, priority_issues=["seguridad", "empleo"],
            initial_embedding_seed="Votante preocupado por seguridad y empleo",
        ),
    ]


@pytest.fixture
def fitness_weights():
    return FitnessWeightsConfig(alpha=0.3, beta=0.2, gamma=0.2, delta=0.15, epsilon=0.15)


@pytest.fixture
def system_config(party_ideals, clusters, voter_segments, fitness_weights):
    return SystemConfig(
        party_ideals=party_ideals,
        clusters=clusters,
        voter_segments=voter_segments,
        fitness_weights=fitness_weights,
        segment_update=SegmentUpdateConfig(inertia=0.7, influence_factor=0.25, noise_scale=0.05),
        guardrails=GuardrailsConfig(
            max_priority_delta=0.15, max_embedding_displacement=0.3,
            min_global_coherence=0.4, rollback_on_critical=True,
        ),
        embeddings=EmbeddingsConfig(provider="mock", dimensionality=128),
        llm=LLMConfig(default_provider="mock"),
    )


@pytest.fixture
def tmp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def store(tmp_db):
    return SQLiteStore(tmp_db)


@pytest.fixture
def vector_store():
    with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as f:
        path = f.name
    vs = InMemoryVectorStore(path)
    yield vs
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_llm():
    return MockLLMProvider()


@pytest.fixture
def mock_embedder():
    return MockEmbeddingProvider(dimensionality=128)


@pytest.fixture
def config_dir():
    return str(Path(__file__).parent.parent / "config")
