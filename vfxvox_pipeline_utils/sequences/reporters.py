"""Result reporters for sequence validation."""

import json
import yaml
from typing import TextIO
from vfxvox_pipeline_utils.core.validators import ValidationResult


def render_console(result: ValidationResult, stream: TextIO) -> None:
    """Render validation result to console.

    Args:
        result: ValidationResult to render
        stream: Text stream to write to (e.g., sys.stdout)
    """
    pattern = result.metadata.get("pattern", "<unknown>")
    frame_count = result.metadata.get("frame_count", 0)
    frame_range = result.metadata.get("frame_range", "unknown")

    # Header
    stream.write(f"Sequence Validator — {pattern}\n")
    stream.write(
        f"Frames: {frame_count} ({frame_range})  "
        f"Errors: {result.error_count()}  "
        f"Warnings: {result.warning_count()}\n"
    )

    if not result.issues:
        stream.write("\n✅ No issues found.\n")
        return

    stream.write("\n")

    # Issues
    for issue in result.issues:
        stream.write(f"[{issue.severity.upper()}] {issue.message}\n")
        if issue.location:
            stream.write(f"    ↳ {issue.location}\n")
        if issue.details:
            for key, value in issue.details.items():
                # Format lists nicely
                if isinstance(value, list) and len(value) > 10:
                    stream.write(f"      {key}: {value[:10]}... ({len(value)} total)\n")
                else:
                    stream.write(f"      {key}: {value}\n")


def render_json(result: ValidationResult) -> str:
    """Render validation result as JSON.

    Args:
        result: ValidationResult to render

    Returns:
        JSON string
    """
    return json.dumps(result.to_dict(), indent=2)


def render_yaml(result: ValidationResult) -> str:
    """Render validation result as YAML.

    Args:
        result: ValidationResult to render

    Returns:
        YAML string
    """
    return yaml.dump(result.to_dict(), default_flow_style=False, sort_keys=False)


def render_markdown(result: ValidationResult) -> str:
    """Render validation result as Markdown.

    Args:
        result: ValidationResult to render

    Returns:
        Markdown string
    """
    lines = []
    pattern = result.metadata.get("pattern", "<unknown>")
    frame_count = result.metadata.get("frame_count", 0)
    frame_range = result.metadata.get("frame_range", "unknown")

    # Header
    lines.append(f"# Sequence Validation Report")
    lines.append("")
    lines.append(f"**Pattern**: `{pattern}`")
    lines.append(f"**Frames**: {frame_count} ({frame_range})")
    lines.append(f"**Errors**: {result.error_count()}")
    lines.append(f"**Warnings**: {result.warning_count()}")
    lines.append("")

    if not result.issues:
        lines.append("✅ No issues found.")
        return "\n".join(lines)

    # Group issues by severity
    errors = result.get_errors()
    warnings = result.get_warnings()
    info = result.get_info()

    if errors:
        lines.append("## Errors")
        lines.append("")
        for issue in errors:
            lines.append(f"### {issue.message}")
            if issue.location:
                lines.append(f"**Location**: `{issue.location}`")
            if issue.details:
                lines.append("")
                lines.append("**Details**:")
                for key, value in issue.details.items():
                    if isinstance(value, list) and len(value) > 10:
                        lines.append(f"- **{key}**: {value[:10]}... ({len(value)} total)")
                    else:
                        lines.append(f"- **{key}**: `{value}`")
            lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for issue in warnings:
            lines.append(f"### {issue.message}")
            if issue.location:
                lines.append(f"**Location**: `{issue.location}`")
            if issue.details:
                lines.append("")
                lines.append("**Details**:")
                for key, value in issue.details.items():
                    lines.append(f"- **{key}**: `{value}`")
            lines.append("")

    if info:
        lines.append("## Info")
        lines.append("")
        for issue in info:
            lines.append(f"- {issue.message}")
            if issue.location:
                lines.append(f"  - Location: `{issue.location}`")
        lines.append("")

    return "\n".join(lines)
