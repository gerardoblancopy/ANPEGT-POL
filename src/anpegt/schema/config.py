"""Configuration models for ANPEGT-POL."""

from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field, model_validator


class PartyIdeals(BaseModel):
    """Core party identity and non-negotiable principles."""

    name: str
    non_negotiable_principles: list[str]
    fiscal_ceiling: float
    ideological_axes: dict[str, float]


class ClusterDef(BaseModel):
    """Definition of a thematic cluster (sector)."""

    id: str
    name: str
    description: str
    keywords: list[str]


class CriterionDef(BaseModel):
    """Definition of an ANP evaluation criterion."""

    id: str
    name: str
    description: str
    weight_hint: float = Field(default=1.0)


class VoterSegmentDef(BaseModel):
    """Definition of a voter segment for the simulation."""

    id: str
    name: str
    description: str
    size_fraction: float
    priority_issues: list[str]
    initial_embedding_seed: str


class CorpusSourceDef(BaseModel):
    """Definition of a corpus data source."""

    id: str
    source_type: str
    path_or_url: str
    enabled: bool = Field(default=True)
    classifier_mode: str = Field(default="keyword")
    metadata: dict[str, str] = Field(default_factory=dict)


class FitnessWeightsConfig(BaseModel):
    """Weights for the multi-objective fitness function."""

    alpha: float
    beta: float
    gamma: float
    delta: float
    epsilon: float = Field(default=0.0)

    @model_validator(mode="after")
    def check_weights_sum(self) -> "FitnessWeightsConfig":
        total = self.alpha + self.beta + self.gamma + self.delta + self.epsilon
        if not (0.95 <= total <= 1.05):
            raise ValueError(
                f"Fitness weights must sum to ~1.0, got {total:.4f}"
            )
        return self


class SegmentUpdateConfig(BaseModel):
    """Parameters controlling voter-segment embedding updates."""

    inertia: float
    influence_factor: float
    noise_scale: float


class GuardrailsConfig(BaseModel):
    """Safety guardrails for the evolutionary loop."""

    max_priority_delta: float
    max_embedding_displacement: float
    min_global_coherence: float
    rollback_on_critical: bool


class EmbeddingsConfig(BaseModel):
    """Configuration for the embedding provider."""

    provider: str = Field(default="mock")
    model: str = Field(default="")
    dimensionality: int = Field(default=128)
    pooling: str = Field(default="mean")


class LLMConfig(BaseModel):
    """Configuration for the LLM provider."""

    default_provider: str = Field(default="mock")
    temperature: float = Field(default=0.7)
    max_retries: int = Field(default=2)
    api_key: str = Field(default="")
    model: str = Field(default="")


class SystemConfig(BaseModel):
    """Top-level system configuration aggregating all sub-configs."""

    party_ideals: PartyIdeals
    clusters: list[ClusterDef]
    criteria: list[CriterionDef] = Field(default=[])
    voter_segments: list[VoterSegmentDef]
    corpus_sources: list[CorpusSourceDef] = Field(default=[])
    fitness_weights: FitnessWeightsConfig
    segment_update: SegmentUpdateConfig
    guardrails: GuardrailsConfig
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


def load_config(config_dir: Union[str, Path]) -> SystemConfig:
    """Load SystemConfig from YAML files in the given directory.

    Expects a directory containing YAML files whose contents are merged
    into a single configuration dict.  At minimum, a ``system.yaml`` or
    individual files such as ``party.yaml``, ``clusters.yaml``, etc.

    Parameters
    ----------
    config_dir:
        Path to the directory containing YAML configuration files.

    Returns
    -------
    SystemConfig
        Fully validated system configuration.
    """
    import yaml  # lazy import to keep module light when unused

    config_path = Path(config_dir)

    def _load_yaml(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data if isinstance(data, dict) else {}

    # Map file stems to SystemConfig field names / loading logic
    file_mapping: dict[str, str] = {
        "party_ideals": "party_ideals",
        "clusters": "_clusters_file",
        "voter_segments": "_voter_segments_file",
        "corpus_sources": "_corpus_sources_file",
        "cycle_params": "_cycle_params_file",
        "anp_network": "_anp_network_file",
    }

    raw_files: dict[str, dict] = {}
    for yaml_file in sorted(config_path.glob("*.yaml")):
        raw_files[yaml_file.stem] = _load_yaml(yaml_file)
    for yml_file in sorted(config_path.glob("*.yml")):
        raw_files[yml_file.stem] = _load_yaml(yml_file)

    merged: dict = {}

    # party_ideals.yaml -> direct object
    if "party_ideals" in raw_files:
        merged["party_ideals"] = raw_files["party_ideals"]

    # clusters.yaml -> has "clusters" and "criteria" keys
    if "clusters" in raw_files:
        cf = raw_files["clusters"]
        merged["clusters"] = cf.get("clusters", [])
        merged["criteria"] = cf.get("criteria", [])

    # voter_segments.yaml -> has "segments" key
    if "voter_segments" in raw_files:
        vs = raw_files["voter_segments"]
        merged["voter_segments"] = vs.get("segments", [])

    # corpus_sources.yaml -> has "sources" key
    if "corpus_sources" in raw_files:
        cs = raw_files["corpus_sources"]
        merged["corpus_sources"] = cs.get("sources", [])

    # cycle_params.yaml -> has fitness_weights, segment_update, guardrails, embeddings, llm
    if "cycle_params" in raw_files:
        cp = raw_files["cycle_params"]
        for key in ("fitness_weights", "segment_update", "guardrails", "embeddings", "llm"):
            if key in cp:
                merged[key] = cp[key]

    return SystemConfig(**merged)
