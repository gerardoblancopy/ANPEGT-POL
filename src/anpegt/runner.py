"""Cycle orchestration engine for ANPEGT-POL.

Implements the 12-step adaptive planning cycle:
1. Load environment state and segment expectations
2. Update ANP signals
3. Compute cycle priorities
4. Run sectoral agents
5. Run global orchestrator
6. Run communication agents
7. Run social content agents
8. Run speechwriter agent
9. Compute fitness per segment
10. Update segment embeddings
11. Persist results
12. Prepare next cycle
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

from anpegt.agents.communication import CommunicationAgent
from anpegt.agents.orchestrator import OrchestratorAgent
from anpegt.agents.sectoral import SectoralAgent
from anpegt.agents.social_content import SocialContentAgent
from anpegt.agents.speechwriter import SpeechWriterAgent
from anpegt.anp.network import load_anp_network
from anpegt.anp.priorities import compute_priorities
from anpegt.embeddings.provider import get_embedding_provider
from anpegt.embeddings.segment_update import update_segment_embedding
from anpegt.fitness.alignment import compute_alignment
from anpegt.fitness.coherence import compute_coherence
from anpegt.fitness.composite import compute_composite_fitness
from anpegt.fitness.robustness import compute_robustness
from anpegt.fitness.viability import compute_viability
from anpegt.guardrails.checker import GuardrailChecker
from anpegt.llm.mock_provider import MockLLMProvider
from anpegt.schema.config import SystemConfig
from anpegt.schema.cycle import CycleRun
from anpegt.schema.voter import SegmentEmbedding
from anpegt.store.sqlite_store import SQLiteStore
from anpegt.store.vector_store import InMemoryVectorStore
from anpegt.util.logging import get_logger

logger = get_logger("runner")


def _get_llm_provider(config: SystemConfig):
    """Create an LLM provider based on config."""
    provider_name = config.llm.default_provider
    if provider_name == "mock":
        return MockLLMProvider()
    elif provider_name == "openai":
        from anpegt.llm.openai_provider import OpenAIProvider
        model = config.llm.model or "gpt-4o"
        return OpenAIProvider(
            model=model,
            api_key=config.llm.api_key or None,
            temperature=config.llm.temperature,
        )
    elif provider_name == "anthropic":
        from anpegt.llm.anthropic_provider import AnthropicProvider
        return AnthropicProvider(temperature=config.llm.temperature)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")


class CycleRunner:
    """Orchestrates the adaptive government planning cycle."""

    def __init__(self, config: SystemConfig, db_path: str = "anpegt.db", vector_path: str = "vectors.npz"):
        self.config = config
        self.store = SQLiteStore(db_path)
        self.vector_store = InMemoryVectorStore(vector_path)
        self.embedder = get_embedding_provider(config.embeddings)
        self.llm = _get_llm_provider(config)
        self.guardrail_checker = GuardrailChecker(config.party_ideals, config.guardrails)

        # Load ANP network
        anp_path = Path("config/anp_network.yaml")
        if anp_path.exists():
            with open(anp_path) as f:
                net_def = yaml.safe_load(f)
            self.anp_network = load_anp_network(net_def)
        else:
            self.anp_network = None

    def _get_previous_priorities(self) -> Optional[dict[str, float]]:
        """Get priorities from the most recent cycle."""
        latest = self.store.get_latest_cycle_run()
        if latest and latest.priority_snapshot_id:
            snap = self.store.get_priority_snapshot(latest.priority_snapshot_id)
            if snap:
                return snap.node_priorities
        return None

    def _get_segment_embedding(self, segment_id: str) -> Optional[np.ndarray]:
        """Get the latest embedding for a voter segment."""
        emb = self.store.get_latest_segment_embedding(segment_id)
        if emb:
            return np.array(emb.vector, dtype=np.float32)
        return None

    def _initialize_segment_embeddings(self) -> dict[str, np.ndarray]:
        """Initialize or load segment embeddings."""
        embeddings = {}
        for seg in self.config.voter_segments:
            existing = self._get_segment_embedding(seg.id)
            if existing is not None:
                embeddings[seg.id] = existing
            else:
                # Initialize from seed text
                vec = self.embedder.embed(seg.initial_embedding_seed)
                embeddings[seg.id] = np.array(vec, dtype=np.float32)
                # Persist initial embedding
                emb_record = SegmentEmbedding(
                    segment_id=seg.id,
                    cycle_id="init",
                    vector=vec,
                    displacement_from_previous=None,
                )
                self.store.save_segment_embedding(emb_record)
        return embeddings

    def _get_corpus_context(self, cluster_id: str) -> list[str]:
        """Get relevant corpus snippets for a cluster (RAG)."""
        chunks = self.store.get_chunks_by_cluster(cluster_id, limit=5)
        return [c.text for c in chunks]

    def run_cycle(self, cycle_number: int) -> CycleRun:
        """Execute a single planning cycle."""
        cycle_id = f"cycle_{cycle_number}"
        logger.info(f"Starting cycle {cycle_number}")

        cycle_run = CycleRun(
            cycle_number=cycle_number,
            status="running",
            started_at=datetime.utcnow(),
        )

        # === Step 1: Load state ===
        segment_embeddings = self._initialize_segment_embeddings()
        prev_priorities = self._get_previous_priorities()

        # === Step 2 & 3: Update ANP and compute priorities ===
        if self.anp_network:
            priority_snapshot = compute_priorities(
                self.anp_network,
                prev_snapshot=None,  # Simplified: use stored prev_priorities for clamping
                max_priority_delta=self.config.guardrails.max_priority_delta,
            )
            priority_snapshot.cycle_id = cycle_id
            self.store.save_priority_snapshot(priority_snapshot)
            priorities = priority_snapshot.node_priorities
            cycle_run.priority_snapshot_id = str(priority_snapshot.id)

            # Check priority guardrails
            violations = self.guardrail_checker.check_priorities(priorities, prev_priorities)
            for v in violations:
                logger.warning(f"Guardrail: {v.description}")
        else:
            priorities = {c.id: 1.0 / len(self.config.clusters) for c in self.config.clusters}

        # === Step 4: Run sectoral agents ===
        sector_plans = []
        for cluster in self.config.clusters:
            agent = SectoralAgent(
                llm=self.llm,
                config={"max_retries": self.config.llm.max_retries},
            )
            corpus_context = self._get_corpus_context(cluster.id)
            context = {
                "cluster": cluster.model_dump(mode="json"),
                "priorities": priorities,
                "party_ideals": self.config.party_ideals.model_dump(mode="json"),
                "corpus_context": corpus_context,
                "cycle_id": cycle_id,
            }
            plan = agent.run(context)
            plan.cycle_id = cycle_id
            plan.cluster_id = cluster.id
            sector_plans.append(plan)
            self.store.save_sector_plan(plan)
            cycle_run.sector_plan_ids.append(str(plan.id))
            logger.info(f"Sector plan generated: {cluster.id}")

        # === Step 5: Run global orchestrator ===
        orch_agent = OrchestratorAgent(
            llm=self.llm,
            config={"max_retries": self.config.llm.max_retries},
        )
        orch_context = {
            "sector_plans": [sp.model_dump(mode="json") for sp in sector_plans],
            "party_ideals": self.config.party_ideals.model_dump(mode="json"),
            "priorities": priorities,
            "fiscal_ceiling": self.config.party_ideals.fiscal_ceiling,
            "cycle_id": cycle_id,
        }
        global_plan = orch_agent.run(orch_context)
        global_plan.cycle_id = cycle_id
        self.store.save_global_plan(global_plan)
        cycle_run.global_plan_id = str(global_plan.id)
        logger.info("Global plan consolidated")

        # Check plan guardrails
        plan_violations = self.guardrail_checker.check_plan(global_plan)
        for v in plan_violations:
            logger.warning(f"Guardrail: {v.description}")

        # === Step 6: Run communication agents ===
        comm_plans = []
        for seg in self.config.voter_segments:
            comm_agent = CommunicationAgent(
                llm=self.llm,
                config={"max_retries": self.config.llm.max_retries},
            )
            comm_context = {
                "global_plan": global_plan.model_dump(mode="json"),
                "segment": seg.model_dump(mode="json"),
                "cycle_id": cycle_id,
            }
            comm_plan = comm_agent.run(comm_context)
            comm_plan.cycle_id = cycle_id
            comm_plan.segment_id = seg.id
            comm_plans.append(comm_plan)
            self.store.save_communication_plan(comm_plan)
            cycle_run.communication_plan_ids.append(str(comm_plan.id))
        logger.info(f"Communication plans generated for {len(comm_plans)} segments")

        # === Step 7: Run social content agents ===
        platforms = ["twitter", "instagram", "facebook"]
        social_posts = []
        for seg in self.config.voter_segments:
            seg_comm = next((c for c in comm_plans if c.segment_id == seg.id), None)
            for platform in platforms:
                social_agent = SocialContentAgent(
                    llm=self.llm,
                    config={"max_retries": self.config.llm.max_retries},
                )
                social_context = {
                    "global_plan": global_plan.model_dump(mode="json"),
                    "segment": seg.model_dump(mode="json"),
                    "platform": platform,
                    "communication_plan": seg_comm.model_dump(mode="json") if seg_comm else {},
                    "cycle_id": cycle_id,
                }
                post = social_agent.run(social_context)
                post.cycle_id = cycle_id
                post.segment_id = seg.id
                post.platform = platform
                social_posts.append(post)
                self.store.save_social_post(post)
                cycle_run.social_post_ids.append(str(post.id))
        logger.info(f"Social posts generated: {len(social_posts)}")

        # === Step 8: Run speechwriter ===
        speeches = []
        event_configs = [
            {"event_type": "rally", "audience": "general", "duration": 20, "territory": "", "themes": []},
        ]
        for event_cfg in event_configs:
            speech_agent = SpeechWriterAgent(
                llm=self.llm,
                config={"max_retries": self.config.llm.max_retries},
            )
            speech_context = {
                "global_plan": global_plan.model_dump(mode="json"),
                "event_config": event_cfg,
                "party_ideals": self.config.party_ideals.model_dump(mode="json"),
                "cycle_id": cycle_id,
            }
            speech = speech_agent.run(speech_context)
            speech.cycle_id = cycle_id
            speeches.append(speech)
            self.store.save_speech(speech)
            cycle_run.speech_ids.append(str(speech.id))
        logger.info(f"Speeches generated: {len(speeches)}")

        # === Step 9: Compute fitness per segment ===
        # Embed the global plan text
        global_plan_text = global_plan.summary
        for prop in global_plan.consolidated_proposals:
            global_plan_text += f" {prop.title}: {prop.description}"

        sector_plan_texts = []
        for sp in sector_plans:
            text = sp.rationale
            for pol in sp.policies:
                text += f" {pol.title}: {pol.description}"
            sector_plan_texts.append(text)

        coherence = compute_coherence(sector_plan_texts, self.embedder.embed)
        viability = compute_viability(global_plan.global_budget, self.config.party_ideals.fiscal_ceiling)
        robustness = compute_robustness(priorities, prev_priorities)

        fitness_scores = []
        for seg in self.config.voter_segments:
            seg_emb = segment_embeddings[seg.id]
            # Find communication plan for this segment
            seg_comm = next((c for c in comm_plans if c.segment_id == seg.id), None)
            if seg_comm:
                comm_emb = np.array(self.embedder.embed(seg_comm.full_text), dtype=np.float32)
            else:
                comm_emb = np.array(self.embedder.embed(global_plan_text), dtype=np.float32)

            alignment = compute_alignment(comm_emb, seg_emb)

            score = compute_composite_fitness(
                cycle_id=cycle_id,
                segment_id=seg.id,
                alignment=alignment,
                coherence=coherence,
                viability=viability,
                robustness=robustness,
                engagement=0.0,  # No engagement data in first cycles
                weights=self.config.fitness_weights,
            )
            fitness_scores.append(score)
            self.store.save_fitness_score(score)
            cycle_run.fitness_scores.append(str(score.id))
        logger.info(f"Fitness scores computed for {len(fitness_scores)} segments")

        # Check coherence guardrail
        coh_violations = self.guardrail_checker.check_coherence(coherence)
        for v in coh_violations:
            logger.warning(f"Guardrail: {v.description}")

        # === Step 10: Update segment embeddings ===
        updated_embeddings = {}
        for seg in self.config.voter_segments:
            old_emb = segment_embeddings[seg.id]
            seg_comm = next((c for c in comm_plans if c.segment_id == seg.id), None)
            if seg_comm:
                comm_emb = np.array(self.embedder.embed(seg_comm.full_text), dtype=np.float32)
            else:
                comm_emb = np.array(self.embedder.embed(global_plan_text), dtype=np.float32)

            new_emb, displacement = update_segment_embedding(
                old_embedding=old_emb,
                communication_embedding=comm_emb,
                inertia=self.config.segment_update.inertia,
                influence_factor=self.config.segment_update.influence_factor,
                noise_scale=self.config.segment_update.noise_scale,
                max_displacement=self.config.guardrails.max_embedding_displacement,
            )

            emb_record = SegmentEmbedding(
                segment_id=seg.id,
                cycle_id=cycle_id,
                vector=new_emb.tolist(),
                displacement_from_previous=displacement,
            )
            self.store.save_segment_embedding(emb_record)
            updated_embeddings[seg.id] = new_emb

            # Check displacement guardrail
            disp_violations = self.guardrail_checker.check_embeddings(displacement)
            for v in disp_violations:
                logger.warning(f"Guardrail ({seg.id}): {v.description}")

        # === Step 11: Persist results ===
        # Check for critical violations -> rollback
        all_violations = plan_violations + coh_violations
        if self.guardrail_checker.has_critical(all_violations) and self.config.guardrails.rollback_on_critical:
            cycle_run.status = "rolled_back"
            logger.warning(f"Cycle {cycle_number} ROLLED BACK due to critical violations")
        else:
            cycle_run.status = "completed"

        cycle_run.ended_at = datetime.utcnow()
        self.store.save_cycle_run(cycle_run)

        # Write artifacts to disk
        self._write_artifacts(cycle_number, cycle_id, priorities, sector_plans,
                              global_plan, comm_plans, social_posts, speeches, fitness_scores)

        logger.info(f"Cycle {cycle_number} {cycle_run.status}")
        return cycle_run

    def _write_artifacts(self, cycle_number, cycle_id, priorities, sector_plans,
                         global_plan, comm_plans, social_posts, speeches, fitness_scores):
        """Write all cycle artifacts as JSON files."""
        out_dir = Path(f"artifacts/runs/cycle_{cycle_number}")
        out_dir.mkdir(parents=True, exist_ok=True)

        def _write(filename, data):
            with open(out_dir / filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        _write("priorities.json", priorities)

        for sp in sector_plans:
            _write(f"sector_plan_{sp.cluster_id}.json", sp.model_dump(mode="json"))

        _write("global_plan.json", global_plan.model_dump(mode="json"))

        for cp in comm_plans:
            _write(f"communication_{cp.segment_id}.json", cp.model_dump(mode="json"))

        for post in social_posts:
            _write(f"social_post_{post.platform}_{post.segment_id}.json", post.model_dump(mode="json"))

        for speech in speeches:
            _write(f"speech_{speech.event_type}.json", speech.model_dump(mode="json"))

        fitness_data = [fs.model_dump(mode="json") for fs in fitness_scores]
        _write("fitness.json", fitness_data)

        _write("cycle_run.json", {
            "cycle_number": cycle_number,
            "cycle_id": cycle_id,
            "fitness_summary": {
                fs.segment_id: {"composite": fs.composite, "alignment": fs.alignment,
                                "coherence": fs.coherence, "viability": fs.viability,
                                "robustness": fs.robustness}
                for fs in fitness_scores
            },
        })

    def run(self, num_cycles: int) -> list[CycleRun]:
        """Run multiple planning cycles."""
        results = []
        for i in range(1, num_cycles + 1):
            run = self.run_cycle(i)
            results.append(run)
            if run.status == "rolled_back":
                logger.warning(f"Stopping after rolled-back cycle {i}")
                break
        return results
