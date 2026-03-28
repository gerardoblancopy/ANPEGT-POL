"""Tests for SQLiteStore."""

from anpegt.schema.anp import PrioritySnapshot
from anpegt.schema.plan import SectorPlan, GlobalPlan, CommunicationPlan, Proposal
from anpegt.schema.fitness import FitnessScore
from anpegt.schema.voter import SegmentEmbedding
from anpegt.schema.cycle import CycleRun


def test_save_and_get_cycle_run(store):
    cr = CycleRun(cycle_number=1, status="completed")
    store.save_cycle_run(cr)
    retrieved = store.get_cycle_run(1)
    assert retrieved is not None
    assert retrieved.cycle_number == 1
    assert retrieved.status == "completed"


def test_get_latest_cycle_run(store):
    cr1 = CycleRun(cycle_number=1, status="completed")
    cr2 = CycleRun(cycle_number=2, status="completed")
    store.save_cycle_run(cr1)
    store.save_cycle_run(cr2)
    latest = store.get_latest_cycle_run()
    assert latest is not None
    assert latest.cycle_number == 2


def test_save_and_get_priority_snapshot(store):
    snap = PrioritySnapshot(cycle_id="c1", node_priorities={"a": 0.6, "b": 0.4})
    store.save_priority_snapshot(snap)
    retrieved = store.get_priority_snapshot("c1")
    assert retrieved is not None
    assert retrieved.node_priorities["a"] == 0.6


def test_save_and_get_sector_plans(store):
    sp = SectorPlan(
        cycle_id="c1", cluster_id="salud",
        priorities_used={"eq": 0.5}, objectives=["O1"],
        policies=[Proposal(id="p1", title="T", description="D",
                          estimated_cost="bajo", timeframe="1a", expected_impact="alto")],
        intercluster_conflicts=[], rationale="R",
    )
    store.save_sector_plan(sp)
    plans = store.get_sector_plans("c1")
    assert len(plans) == 1
    assert plans[0].cluster_id == "salud"


def test_save_and_get_fitness_score(store):
    fs = FitnessScore(
        cycle_id="c1", segment_id="s1",
        alignment=0.8, coherence=0.7, viability=0.9, robustness=0.95, composite=0.85,
    )
    store.save_fitness_score(fs)
    scores = store.get_fitness_scores("c1")
    assert len(scores) == 1
    assert scores[0].composite == 0.85


def test_save_and_get_segment_embedding(store):
    emb = SegmentEmbedding(
        segment_id="s1", cycle_id="c1",
        vector=[0.1, 0.2, 0.3], displacement_from_previous=None,
    )
    store.save_segment_embedding(emb)
    retrieved = store.get_latest_segment_embedding("s1")
    assert retrieved is not None
    assert retrieved.vector == [0.1, 0.2, 0.3]


def test_cycle_history(store):
    for i in range(5):
        cr = CycleRun(cycle_number=i + 1, status="completed")
        store.save_cycle_run(cr)
    history = store.get_cycle_history(last_n=3)
    assert len(history) == 3
