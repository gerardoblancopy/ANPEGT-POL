"""SQLite-backed implementation of the Store protocol for ANPEGT-POL."""

import json
import sqlite3
from datetime import datetime
from typing import Optional

from anpegt.schema.anp import PrioritySnapshot
from anpegt.schema.corpus import ChunkRecord, CorpusDocument
from anpegt.schema.cycle import CycleRun
from anpegt.schema.fitness import FitnessScore
from anpegt.schema.plan import CommunicationPlan, GlobalPlan, SectorPlan, SocialPost, Speech
from anpegt.schema.voter import SegmentEmbedding

_TABLES = [
    "cycle_runs",
    "priority_snapshots",
    "sector_plans",
    "global_plans",
    "communication_plans",
    "social_posts",
    "speeches",
    "fitness_scores",
    "segment_embeddings",
    "corpus_documents",
    "chunk_records",
]


class SQLiteStore:
    """Synchronous SQLite store.  Each entity is stored as a JSON blob."""

    def __init__(self, db_path: str = "anpegt.db") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self.init_db()

    # ------------------------------------------------------------------
    # Schema bootstrap
    # ------------------------------------------------------------------

    def init_db(self) -> None:
        """Create all tables and indexes if they do not exist."""
        cur = self._conn.cursor()
        for table in _TABLES:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id         TEXT PRIMARY KEY,
                    cycle_id   TEXT,
                    created_at TEXT,
                    data       TEXT
                )
                """
            )
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_cycle_id ON {table}(cycle_id)"
            )

        # segment_embeddings needs the segment_id column
        # Add it if not present (idempotent via try/except)
        try:
            cur.execute("ALTER TABLE segment_embeddings ADD COLUMN segment_id TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_segment_embeddings_seg_cycle "
            "ON segment_embeddings(segment_id, cycle_id)"
        )

        # chunk_records: store cluster_tags as comma-separated for LIKE queries
        try:
            cur.execute("ALTER TABLE chunk_records ADD COLUMN cluster_tags TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_chunk_records_cluster_tags "
            "ON chunk_records(cluster_tags)"
        )

        # cycle_runs: index on cycle_number for fast lookup
        try:
            cur.execute("ALTER TABLE cycle_runs ADD COLUMN cycle_number INTEGER")
        except sqlite3.OperationalError:
            pass
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_cycle_runs_number ON cycle_runs(cycle_number)"
        )

        self._conn.commit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _upsert(
        self,
        table: str,
        id_val: str,
        cycle_id: str,
        created_at: str,
        data_json: str,
        extras: Optional[dict[str, object]] = None,
    ) -> None:
        extra_cols = ""
        extra_placeholders = ""
        extra_update = ""
        values: list[object] = [id_val, cycle_id, created_at, data_json]
        if extras:
            for col, val in extras.items():
                extra_cols += f", {col}"
                extra_placeholders += ", ?"
                extra_update += f", {col}=excluded.{col}"
                values.append(val)
        sql = (
            f"INSERT INTO {table} (id, cycle_id, created_at, data{extra_cols}) "
            f"VALUES (?, ?, ?, ?{extra_placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET "
            f"cycle_id=excluded.cycle_id, created_at=excluded.created_at, "
            f"data=excluded.data{extra_update}"
        )
        self._conn.execute(sql, values)
        self._conn.commit()

    @staticmethod
    def _serialize(model: object) -> str:
        # All schema models are Pydantic BaseModel subclasses
        return model.model_dump_json()  # type: ignore[union-attr]

    @staticmethod
    def _id_str(model: object) -> str:
        return str(getattr(model, "id"))

    @staticmethod
    def _created_str(model: object) -> str:
        created = getattr(model, "created_at", None)
        if isinstance(created, datetime):
            return created.isoformat()
        return str(created) if created else ""

    def _fetch_one(self, table: str, where: str, params: tuple) -> Optional[str]:
        row = self._conn.execute(
            f"SELECT data FROM {table} WHERE {where} LIMIT 1", params
        ).fetchone()
        return row["data"] if row else None

    def _fetch_many(self, table: str, where: str, params: tuple, limit: Optional[int] = None) -> list[str]:
        sql = f"SELECT data FROM {table} WHERE {where} ORDER BY created_at DESC"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return [row["data"] for row in self._conn.execute(sql, params).fetchall()]

    # ------------------------------------------------------------------
    # CycleRun
    # ------------------------------------------------------------------

    def save_cycle_run(self, run: CycleRun) -> None:
        self._upsert(
            "cycle_runs",
            self._id_str(run),
            str(getattr(run, "cycle_number", "")),
            self._created_str(run),
            self._serialize(run),
            extras={"cycle_number": run.cycle_number},
        )

    def get_cycle_run(self, cycle_number: int) -> Optional[CycleRun]:
        data = self._fetch_one("cycle_runs", "cycle_number = ?", (cycle_number,))
        return CycleRun.model_validate_json(data) if data else None

    def get_latest_cycle_run(self) -> Optional[CycleRun]:
        row = self._conn.execute(
            "SELECT data FROM cycle_runs ORDER BY cycle_number DESC LIMIT 1"
        ).fetchone()
        return CycleRun.model_validate_json(row["data"]) if row else None

    def get_cycle_history(self, last_n: int = 10) -> list[CycleRun]:
        rows = self._conn.execute(
            "SELECT data FROM cycle_runs ORDER BY cycle_number DESC LIMIT ?", (last_n,)
        ).fetchall()
        return [CycleRun.model_validate_json(r["data"]) for r in rows]

    # ------------------------------------------------------------------
    # PrioritySnapshot
    # ------------------------------------------------------------------

    def save_priority_snapshot(self, snap: PrioritySnapshot) -> None:
        self._upsert(
            "priority_snapshots",
            self._id_str(snap),
            snap.cycle_id,
            self._created_str(snap),
            self._serialize(snap),
        )

    def get_priority_snapshot(self, cycle_id: str) -> Optional[PrioritySnapshot]:
        data = self._fetch_one("priority_snapshots", "cycle_id = ?", (cycle_id,))
        return PrioritySnapshot.model_validate_json(data) if data else None

    # ------------------------------------------------------------------
    # SectorPlan
    # ------------------------------------------------------------------

    def save_sector_plan(self, plan: SectorPlan) -> None:
        self._upsert(
            "sector_plans",
            self._id_str(plan),
            plan.cycle_id,
            self._created_str(plan),
            self._serialize(plan),
        )

    def get_sector_plans(self, cycle_id: str) -> list[SectorPlan]:
        rows = self._fetch_many("sector_plans", "cycle_id = ?", (cycle_id,))
        return [SectorPlan.model_validate_json(r) for r in rows]

    # ------------------------------------------------------------------
    # GlobalPlan
    # ------------------------------------------------------------------

    def save_global_plan(self, plan: GlobalPlan) -> None:
        self._upsert(
            "global_plans",
            self._id_str(plan),
            plan.cycle_id,
            self._created_str(plan),
            self._serialize(plan),
        )

    def get_global_plan(self, cycle_id: str) -> Optional[GlobalPlan]:
        data = self._fetch_one("global_plans", "cycle_id = ?", (cycle_id,))
        return GlobalPlan.model_validate_json(data) if data else None

    # ------------------------------------------------------------------
    # CommunicationPlan
    # ------------------------------------------------------------------

    def save_communication_plan(self, plan: CommunicationPlan) -> None:
        self._upsert(
            "communication_plans",
            self._id_str(plan),
            plan.cycle_id,
            self._created_str(plan),
            self._serialize(plan),
        )

    def get_communication_plans(self, cycle_id: str) -> list[CommunicationPlan]:
        rows = self._fetch_many("communication_plans", "cycle_id = ?", (cycle_id,))
        return [CommunicationPlan.model_validate_json(r) for r in rows]

    # ------------------------------------------------------------------
    # SocialPost
    # ------------------------------------------------------------------

    def save_social_post(self, post: SocialPost) -> None:
        self._upsert(
            "social_posts",
            self._id_str(post),
            post.cycle_id,
            self._created_str(post),
            self._serialize(post),
        )

    def get_social_posts(self, cycle_id: str) -> list[SocialPost]:
        rows = self._fetch_many("social_posts", "cycle_id = ?", (cycle_id,))
        return [SocialPost.model_validate_json(r) for r in rows]

    # ------------------------------------------------------------------
    # Speech
    # ------------------------------------------------------------------

    def save_speech(self, speech: Speech) -> None:
        self._upsert(
            "speeches",
            self._id_str(speech),
            speech.cycle_id,
            self._created_str(speech),
            self._serialize(speech),
        )

    def get_speeches(self, cycle_id: str) -> list[Speech]:
        rows = self._fetch_many("speeches", "cycle_id = ?", (cycle_id,))
        return [Speech.model_validate_json(r) for r in rows]

    # ------------------------------------------------------------------
    # FitnessScore
    # ------------------------------------------------------------------

    def save_fitness_score(self, score: FitnessScore) -> None:
        self._upsert(
            "fitness_scores",
            self._id_str(score),
            score.cycle_id,
            self._created_str(score),
            self._serialize(score),
        )

    def get_fitness_scores(self, cycle_id: str) -> list[FitnessScore]:
        rows = self._fetch_many("fitness_scores", "cycle_id = ?", (cycle_id,))
        return [FitnessScore.model_validate_json(r) for r in rows]

    # ------------------------------------------------------------------
    # SegmentEmbedding
    # ------------------------------------------------------------------

    def save_segment_embedding(self, emb: SegmentEmbedding) -> None:
        self._upsert(
            "segment_embeddings",
            self._id_str(emb),
            emb.cycle_id,
            self._created_str(emb),
            self._serialize(emb),
            extras={"segment_id": emb.segment_id},
        )

    def get_latest_segment_embedding(self, segment_id: str) -> Optional[SegmentEmbedding]:
        row = self._conn.execute(
            "SELECT data FROM segment_embeddings WHERE segment_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (segment_id,),
        ).fetchone()
        return SegmentEmbedding.model_validate_json(row["data"]) if row else None

    # ------------------------------------------------------------------
    # CorpusDocument
    # ------------------------------------------------------------------

    def save_corpus_document(self, doc: CorpusDocument) -> None:
        self._upsert(
            "corpus_documents",
            self._id_str(doc),
            "",  # corpus documents are not tied to a cycle
            self._created_str(doc),
            self._serialize(doc),
        )

    # ------------------------------------------------------------------
    # ChunkRecord
    # ------------------------------------------------------------------

    def save_chunk_record(self, chunk: ChunkRecord) -> None:
        cluster_csv = ",".join(chunk.cluster_tags)
        self._upsert(
            "chunk_records",
            self._id_str(chunk),
            "",  # chunks are not tied to a cycle
            self._created_str(chunk),
            self._serialize(chunk),
            extras={"cluster_tags": cluster_csv},
        )

    def get_chunks_by_cluster(self, cluster_id: str, limit: int = 10) -> list[ChunkRecord]:
        rows = self._conn.execute(
            "SELECT data FROM chunk_records WHERE cluster_tags LIKE ? LIMIT ?",
            (f"%{cluster_id}%", limit),
        ).fetchall()
        return [ChunkRecord.model_validate_json(r["data"]) for r in rows]
