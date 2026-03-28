"""Integration test: run 2 full cycles with mock providers."""

import os
import tempfile
from pathlib import Path

from anpegt.schema.config import load_config
from anpegt.runner import CycleRunner


def test_two_cycle_run(config_dir):
    """Run 2 cycles end-to-end with mock LLM and mock embeddings."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    vec_path = db_path.replace(".db", "_vec.npz")

    try:
        cfg = load_config(config_dir)
        runner = CycleRunner(cfg, db_path=db_path, vector_path=vec_path)
        results = runner.run(num_cycles=2)

        # Both cycles should complete
        assert len(results) == 2
        assert results[0].status == "completed"
        assert results[1].status == "completed"

        # Cycle 1 should have sector plans
        assert len(results[0].sector_plan_ids) == 4  # 4 clusters
        assert results[0].global_plan_id is not None
        assert len(results[0].communication_plan_ids) == 2  # 2 segments
        assert len(results[0].fitness_scores) == 2  # 2 segments

        # Artifacts should be written
        assert Path("artifacts/runs/cycle_1/global_plan.json").exists()
        assert Path("artifacts/runs/cycle_2/global_plan.json").exists()
        assert Path("artifacts/runs/cycle_1/fitness.json").exists()

        # Cycle 2 embeddings should differ from cycle 1
        emb1 = runner.store.get_latest_segment_embedding("urbano_progresista")
        assert emb1 is not None
        assert emb1.cycle_id == "cycle_2"
        if emb1.displacement_from_previous is not None:
            assert emb1.displacement_from_previous >= 0

    finally:
        os.unlink(db_path)
        if os.path.exists(vec_path):
            os.unlink(vec_path)
