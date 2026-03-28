"""FastAPI backend serving cycle artifacts for the dashboard."""

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ANPEGT-POL API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve dashboard static files if the build exists
DASHBOARD_DIST = Path(__file__).resolve().parent.parent.parent / "dashboard" / "dist"

ARTIFACTS_DIR = Path("artifacts/runs")


def _load_json(path: Path) -> dict | list:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Not found: {path.name}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/cycles")
def list_cycles():
    """List all available cycles."""
    if not ARTIFACTS_DIR.exists():
        return []
    cycles = []
    for d in sorted(ARTIFACTS_DIR.iterdir()):
        if d.is_dir() and d.name.startswith("cycle_"):
            num = int(d.name.split("_")[1])
            cycle_run_path = d / "cycle_run.json"
            data = _load_json(cycle_run_path) if cycle_run_path.exists() else {}
            cycles.append({"cycle_number": num, "dir": d.name, **data})
    return cycles


@app.get("/api/cycles/{cycle_number}/priorities")
def get_priorities(cycle_number: int):
    return _load_json(ARTIFACTS_DIR / f"cycle_{cycle_number}" / "priorities.json")


@app.get("/api/cycles/{cycle_number}/global-plan")
def get_global_plan(cycle_number: int):
    return _load_json(ARTIFACTS_DIR / f"cycle_{cycle_number}" / "global_plan.json")


@app.get("/api/cycles/{cycle_number}/sector-plans")
def get_sector_plans(cycle_number: int):
    cycle_dir = ARTIFACTS_DIR / f"cycle_{cycle_number}"
    if not cycle_dir.exists():
        raise HTTPException(status_code=404)
    plans = []
    for f in sorted(cycle_dir.glob("sector_plan_*.json")):
        plans.append(_load_json(f))
    return plans


@app.get("/api/cycles/{cycle_number}/sector-plans/{cluster_id}")
def get_sector_plan(cycle_number: int, cluster_id: str):
    return _load_json(ARTIFACTS_DIR / f"cycle_{cycle_number}" / f"sector_plan_{cluster_id}.json")


@app.get("/api/cycles/{cycle_number}/communication")
def get_communication_plans(cycle_number: int):
    cycle_dir = ARTIFACTS_DIR / f"cycle_{cycle_number}"
    if not cycle_dir.exists():
        raise HTTPException(status_code=404)
    plans = []
    for f in sorted(cycle_dir.glob("communication_*.json")):
        plans.append(_load_json(f))
    return plans


@app.get("/api/cycles/{cycle_number}/communication/{segment_id}")
def get_communication_plan(cycle_number: int, segment_id: str):
    return _load_json(ARTIFACTS_DIR / f"cycle_{cycle_number}" / f"communication_{segment_id}.json")


@app.get("/api/cycles/{cycle_number}/social-posts")
def get_social_posts(cycle_number: int):
    cycle_dir = ARTIFACTS_DIR / f"cycle_{cycle_number}"
    if not cycle_dir.exists():
        raise HTTPException(status_code=404)
    posts = []
    for f in sorted(cycle_dir.glob("social_post_*.json")):
        posts.append(_load_json(f))
    return posts


@app.get("/api/cycles/{cycle_number}/speeches")
def get_speeches(cycle_number: int):
    cycle_dir = ARTIFACTS_DIR / f"cycle_{cycle_number}"
    if not cycle_dir.exists():
        raise HTTPException(status_code=404)
    speeches = []
    for f in sorted(cycle_dir.glob("speech_*.json")):
        speeches.append(_load_json(f))
    return speeches


@app.get("/api/cycles/{cycle_number}/fitness")
def get_fitness(cycle_number: int):
    return _load_json(ARTIFACTS_DIR / f"cycle_{cycle_number}" / "fitness.json")


@app.get("/api/cycles/{cycle_number}/cycle-run")
def get_cycle_run(cycle_number: int):
    return _load_json(ARTIFACTS_DIR / f"cycle_{cycle_number}" / "cycle_run.json")


@app.get("/api/overview")
def get_overview():
    """Aggregated overview across all cycles."""
    if not ARTIFACTS_DIR.exists():
        return {"cycles": [], "latest": None}

    cycles = []
    for d in sorted(ARTIFACTS_DIR.iterdir()):
        if d.is_dir() and d.name.startswith("cycle_"):
            num = int(d.name.split("_")[1])
            cycle_data: dict = {"cycle_number": num}

            # Load fitness
            fitness_path = d / "fitness.json"
            if fitness_path.exists():
                fitness = _load_json(fitness_path)
                cycle_data["fitness"] = fitness

            # Load priorities
            priorities_path = d / "priorities.json"
            if priorities_path.exists():
                cycle_data["priorities"] = _load_json(priorities_path)

            cycles.append(cycle_data)

    return {
        "cycles": cycles,
        "latest": cycles[-1] if cycles else None,
        "total_cycles": len(cycles),
    }


# --- Static dashboard serving (must be AFTER all /api routes) ---
if DASHBOARD_DIST.exists():
    app.mount("/assets", StaticFiles(directory=DASHBOARD_DIST / "assets"), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for any non-API route."""
        file_path = DASHBOARD_DIST / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DASHBOARD_DIST / "index.html")
