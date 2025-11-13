"""Main CLI entry point for VFXVox Pipeline Utils."""

import click
from vfxvox_pipeline_utils import __version__


@click.group()
@click.version_option(version=__version__)
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.option("--log-level", default="INFO", help="Logging level")
@click.pass_context
def cli(ctx, config, log_level):
    """VFXVox Pipeline Utilities - Tools for VFX production pipelines.

    A collection of validation tools for VFX production pipelines:

    \b
    - shotlint: Validate directory structures
    - validate-sequence: Check image sequences
    - lint-usd: Lint USD files

    Use --help with any command for more information.
    """
    # Setup logging and configuration
    from vfxvox_pipeline_utils.core.logging import setup_logging

    setup_logging(level=log_level)

    # Store config in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["log_level"] = log_level


# Register commands
from .shotlint_cmd import shotlint_command
from .sequence_cmd import validate_sequence_command
from .usd_cmd import lint_usd_command

cli.add_command(shotlint_command)
cli.add_command(validate_sequence_command)
cli.add_command(lint_usd_command)


if __name__ == "__main__":
    cli()
