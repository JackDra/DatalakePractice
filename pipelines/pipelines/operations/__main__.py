import logging
import shutil
import subprocess
from pathlib import Path

import click

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=LOG_FORMAT,
    )


@click.group()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable debug logging.",
)
def main(verbose: bool) -> None:
    configure_logging(verbose)


@main.command("upload-sample", help="Upload the local sample raw data files to ADLS.")
def upload_sample_command() -> None:
    from pipelines.operations.upload_sample import upload_samples

    upload_samples()


@main.command("create-bronze", help="Create the bronze pipeline")
@click.option(
    "--run",
    "run_pipeline",
    is_flag=True,
    help="Run the bronze pipeline after creating or updating it.",
)
def create_bronze(run_pipeline: bool) -> None:
    from pipelines.operations.build_bronze import build_bronze

    build_bronze(run_pipeline=run_pipeline)


@main.command("build-wheel", help="Build the package wheel for Databricks jobs.")
@click.option(
    "--clean/--no-clean",
    default=True,
    help="Delete the existing dist directory before building.",
)
def build_wheel(clean: bool) -> None:
    project_root = Path(__file__).resolve().parents[2]
    dist_dir = project_root / "dist"

    if clean and dist_dir.exists():
        shutil.rmtree(dist_dir)

    subprocess.run(["uv", "build", "--wheel"], cwd=project_root, check=True)

    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise click.ClickException(f"No wheel was created in {dist_dir}")

    click.echo(f"Built wheel: {wheels[-1]}")


@main.command("ingest-fake-orders", help="Upload a fake raw orders batch to ADLS.")
@click.option(
    "--rows",
    default=5,
    show_default=True,
    type=click.IntRange(min=1),
    help="Number of fake order rows to upload.",
)
def ingest_fake_orders_command(rows: int) -> None:
    from pipelines.operations.fake_ingestion import ingest_fake_orders

    ingest_fake_orders(row_count=rows)


@main.command("serve-dashboard", help="Serve the local gold dashboard frontend.")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, show_default=True, type=int)
def serve_dashboard_command(host: str, port: int) -> None:
    from pipelines.operations.serve_dashboard import serve_dashboard

    serve_dashboard(host=host, port=port)


if __name__ == "__main__":
    main()
