"""CLI entry point for ANPEGT-POL."""

import json
from pathlib import Path

import click

from anpegt.schema.config import load_config


@click.group()
@click.option("--config-dir", default="config", help="Path to config directory")
@click.pass_context
def main(ctx: click.Context, config_dir: str) -> None:
    """ANPEGT-POL: Adaptive Government Planning System."""
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config_dir


@main.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Validate configuration and initialize the system."""
    config_dir = ctx.obj["config_dir"]
    try:
        cfg = load_config(config_dir)
        click.echo(f"Configuration valid.")
        click.echo(f"  Party: {cfg.party_ideals.name}")
        click.echo(f"  Clusters: {[c.id for c in cfg.clusters]}")
        click.echo(f"  Criteria: {[c.id for c in cfg.criteria]}")
        click.echo(f"  Voter segments: {[s.id for s in cfg.voter_segments]}")
        click.echo(f"  Corpus sources: {len(cfg.corpus_sources)} configured")
        click.echo(f"  LLM provider: {cfg.llm.default_provider}")
        click.echo(f"  Embedding provider: {cfg.embeddings.provider}")

        # Ensure artifacts directory exists
        Path("artifacts/runs").mkdir(parents=True, exist_ok=True)
        click.echo("Artifacts directory ready.")
    except Exception as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.option("--cycles", default=1, help="Number of cycles to run")
@click.option("--llm", default=None, help="LLM provider override (mock/openai/anthropic)")
@click.pass_context
def run(ctx: click.Context, cycles: int, llm: str | None) -> None:
    """Run N planning cycles."""
    from anpegt.runner import CycleRunner

    config_dir = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    if llm:
        cfg.llm.default_provider = llm

    runner = CycleRunner(cfg)
    results = runner.run(num_cycles=cycles)

    for r in results:
        click.echo(
            f"Cycle {r.cycle_number}: status={r.status}"
        )


@main.command()
@click.argument("entity_type")
@click.argument("cycle_number", type=int)
@click.pass_context
def show(ctx: click.Context, entity_type: str, cycle_number: int) -> None:
    """Show artifacts for a given cycle. Entity types: cycle, plan, fitness, priorities."""
    artifacts_dir = Path(f"artifacts/runs/cycle_{cycle_number}")
    if not artifacts_dir.exists():
        click.echo(f"No artifacts found for cycle {cycle_number}", err=True)
        raise SystemExit(1)

    file_map = {
        "cycle": "cycle_run.json",
        "plan": "global_plan.json",
        "fitness": "fitness.json",
        "priorities": "priorities.json",
    }
    filename = file_map.get(entity_type)
    if not filename:
        click.echo(f"Unknown entity type: {entity_type}. Options: {list(file_map.keys())}", err=True)
        raise SystemExit(1)

    filepath = artifacts_dir / filename
    if not filepath.exists():
        click.echo(f"File not found: {filepath}", err=True)
        raise SystemExit(1)

    with open(filepath) as f:
        data = json.load(f)
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


@main.command()
@click.option("--cycle", required=True, type=int, help="Cycle number to export")
@click.option("--dir", "output_dir", default="./export", help="Output directory")
@click.pass_context
def export(ctx: click.Context, cycle: int, output_dir: str) -> None:
    """Export all artifacts for a cycle to a directory."""
    import shutil

    src = Path(f"artifacts/runs/cycle_{cycle}")
    if not src.exists():
        click.echo(f"No artifacts found for cycle {cycle}", err=True)
        raise SystemExit(1)

    dst = Path(output_dir) / f"cycle_{cycle}"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.json"):
        shutil.copy2(f, dst / f.name)
    click.echo(f"Exported to {dst}")


@main.command()
@click.option("--source", default=None, help="Source ID to ingest (or omit for all)")
@click.pass_context
def ingest(ctx: click.Context, source: str | None) -> None:
    """Run corpus ingestion from configured sources."""
    from anpegt.corpus.ingest import CorpusIngester

    config_dir = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    ingester = CorpusIngester(cfg)

    if source:
        count = ingester.ingest_source(source)
        click.echo(f"Ingested {count} documents from source '{source}'")
    else:
        total = ingester.ingest_all()
        click.echo(f"Ingested {total} documents from all sources")


if __name__ == "__main__":
    main()
