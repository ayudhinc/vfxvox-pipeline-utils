"""ShotLint CLI command implementation."""

import sys
import click
from pathlib import Path

from vfxvox_pipeline_utils.shotlint import ShotLintValidator
from vfxvox_pipeline_utils.shotlint import reporters
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


@click.command(name="shotlint")
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--rules",
    required=True,
    type=click.Path(exists=True),
    help="Path to rules YAML file"
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
    "--fail-on",
    type=click.Choice(["error", "warning", "none"], case_sensitive=False),
    default="error",
    help="Exit code policy: fail on errors, warnings, or never fail"
)
@click.pass_context
def shotlint_command(ctx, directory, rules, format, report, fail_on):
    """Validate directory structure against rules.

    Validates VFX project directory structures using declarative YAML rules.
    Checks folder hierarchies, naming conventions, frame sequences, and file presence.

    Examples:

        \b
        # Validate with console output
        vfxvox shotlint ./project --rules rules.yaml

        \b
        # Generate JSON report
        vfxvox shotlint ./project --rules rules.yaml --format json --report report.json

        \b
        # Fail on warnings
        vfxvox shotlint ./project --rules rules.yaml --fail-on warning
    """
    try:
        # Create validator
        validator = ShotLintValidator()

        # Run validation
        logger.info(f"Validating directory: {directory}")
        result = validator.validate(Path(directory), Path(rules))

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

        # Determine exit code based on fail-on policy
        exit_code = 0

        if fail_on == "error" and result.has_errors():
            exit_code = 1
        elif fail_on == "warning" and (result.has_errors() or result.has_warnings()):
            exit_code = 1
        # fail_on == "none" always exits with 0

        if exit_code != 0:
            logger.warning(f"Validation failed with exit code {exit_code}")

        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"ShotLint command failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)  # Exit code 3 for execution failure
