"""Main CLI entry point for VFXVox Pipeline Utils."""

import click
from vfxvox_pipeline_utils import __version__


@click.group()
@click.version_option(version=__version__)
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.option("--log-level", default="INFO", help="Logging level")
@click.pass_context
def cli(ctx, config, log_level):
    """VFXVox Pipeline Utilities - Tools for VFX production pipelines."""
    # Setup logging and configuration
    from vfxvox_pipeline_utils.core.logging import setup_logging

    setup_logging(level=log_level)

    # Store config in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["log_level"] = log_level


if __name__ == "__main__":
    cli()
