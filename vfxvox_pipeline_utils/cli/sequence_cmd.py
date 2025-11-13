"""Sequence validation CLI command implementation."""

import sys
import click

from vfxvox_pipeline_utils.sequences import SequenceValidator
from vfxvox_pipeline_utils.sequences import reporters
from vfxvox_pipeline_utils.core.config import Config
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


@click.command(name="validate-sequence")
@click.argument("pattern")
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
    "--check-resolution/--no-check-resolution",
    default=True,
    help="Check resolution consistency across frames"
)
@click.option(
    "--check-bit-depth/--no-check-bit-depth",
    default=True,
    help="Check bit depth consistency across frames"
)
@click.pass_context
def validate_sequence_command(ctx, pattern, format, report, check_resolution, check_bit_depth):
    """Validate an image sequence for missing or corrupted frames.

    Validates image sequences by checking for missing frames, corrupted files,
    and consistency in resolution and bit depth.

    PATTERN: File pattern for the sequence. Supports:

    \b
    - Printf-style: shot_010.%04d.exr
    - Hash-style: shot_010.####.exr
    - Range-style: shot_010.[1001-1100].exr

    Examples:

        \b
        # Validate EXR sequence
        vfxvox validate-sequence "shot_010.%04d.exr"

        \b
        # Generate JSON report
        vfxvox validate-sequence "shot.####.dpx" --format json --report report.json

        \b
        # Skip resolution check
        vfxvox validate-sequence "frames.%04d.png" --no-check-resolution
    """
    try:
        # Create config with options
        config_dict = {
            "sequences": {
                "check_resolution": check_resolution,
                "check_bit_depth": check_bit_depth,
            }
        }
        config = Config.from_dict(config_dict)

        # Create validator
        validator = SequenceValidator(config)

        # Run validation
        logger.info(f"Validating sequence: {pattern}")
        result = validator.validate(pattern)

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
            logger.warning(f"Validation failed with exit code {exit_code}")

        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Sequence validation command failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)  # Exit code 3 for execution failure
