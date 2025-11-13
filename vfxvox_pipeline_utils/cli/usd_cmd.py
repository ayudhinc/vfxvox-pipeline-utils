"""USD linting CLI command implementation."""

import sys
import click
from pathlib import Path

from vfxvox_pipeline_utils.usd import USDLinter
from vfxvox_pipeline_utils.usd import reporters
from vfxvox_pipeline_utils.core.config import Config
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


@click.command(name="lint-usd")
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Custom rules configuration file"
)
@click.option(
    "--format",
    type=click.Choice(["console", "json", "yaml", "md"], case_sensitive=False),
    default="console",
    help="Output format"
)
@click.option(
    "--report",
    type=click.Path(),
    help="Output file for report (optional, prints to stdout if not specified)"
)
@click.option(
    "--check-references/--no-check-references",
    default=True,
    help="Check for broken references"
)
@click.option(
    "--check-schemas/--no-check-schemas",
    default=True,
    help="Check for invalid schemas"
)
@click.option(
    "--check-performance/--no-check-performance",
    default=True,
    help="Check for performance issues"
)
@click.pass_context
def lint_usd_command(ctx, filepath, config, format, report, check_references, check_schemas, check_performance):
    """Lint a USD file for issues and best practices.

    Validates Universal Scene Description files by checking for broken references,
    invalid schemas, and performance issues.

    FILEPATH: Path to USD file (.usd, .usda, .usdc, .usdz)

    Examples:

        \b
        # Lint USD file
        vfxvox lint-usd asset.usd

        \b
        # Lint with custom rules
        vfxvox lint-usd asset.usd --config custom_rules.yaml

        \b
        # Generate Markdown report
        vfxvox lint-usd asset.usd --format md --report report.md

        \b
        # Skip performance checks
        vfxvox lint-usd asset.usd --no-check-performance
    """
    try:
        # Create config with options
        config_dict = {
            "usd": {
                "check_references": check_references,
                "check_schemas": check_schemas,
                "check_performance": check_performance,
                "custom_rules_path": config if config else None,
            }
        }
        config_obj = Config.from_dict(config_dict)

        # Create linter
        linter = USDLinter(config_obj)

        # Run linting
        logger.info(f"Linting USD file: {filepath}")
        result = linter.validate(Path(filepath))

        # Format output
        if format == "json":
            output = reporters.render_json(result)
        elif format == "yaml":
            output = reporters.render_yaml(result)
        elif format == "md":
            output = reporters.render_markdown(result)
        else:  # console
            if report:
                # For console format with file output, render to string
                import io
                stream = io.StringIO()
                reporters.render_console(result, stream)
                output = stream.getvalue()
            else:
                # Render directly to stdout
                reporters.render_console(result, sys.stdout)
                output = None

        # Write to file if specified
        if report and output:
            with open(report, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Report written to: {report}")
        elif output:
            # Print to stdout for non-console formats
            print(output)

        # Determine exit code
        exit_code = 0
        if result.has_errors():
            exit_code = 1
        elif result.has_warnings():
            exit_code = 2

        if exit_code != 0:
            logger.warning(f"Linting failed with exit code {exit_code}")

        sys.exit(exit_code)

    except ImportError as e:
        logger.error("USD Python bindings not installed")
        click.echo(
            "Error: USD Python bindings not installed.\n"
            "Install with: pip install vfxvox-pipeline-utils[usd]",
            err=True
        )
        sys.exit(3)
    except Exception as e:
        logger.error(f"USD linting command failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)  # Exit code 3 for execution failure
