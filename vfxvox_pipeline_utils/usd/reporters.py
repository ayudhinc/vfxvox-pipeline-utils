"""Result reporters for USD linting."""

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
    file_path = result.metadata.get("file_path", "<unknown>")
    file_format = result.metadata.get("file_format", "")

    # Header
    stream.write(f"USD Linter — {file_path}\n")
    stream.write(
        f"Format: {file_format}  "
        f"Errors: {result.error_count()}  "
        f"Warnings: {result.warning_count()}\n"
    )

    if not result.issues:
        stream.write("\n✅ No issues found.\n")
        return

    stream.write("\n")

    # Group by severity
    errors = result.get_errors()
    warnings = result.get_warnings()
    info = result.get_info()

    if errors:
        stream.write("ERRORS:\n")
        for issue in errors:
            stream.write(f"  [{issue.severity.upper()}] {issue.message}\n")
            if issue.location:
                stream.write(f"      ↳ {issue.location}\n")
            if issue.details:
                for key, value in issue.details.items():
                    stream.write(f"        {key}: {value}\n")
        stream.write("\n")

    if warnings:
        stream.write("WARNINGS:\n")
        for issue in warnings:
            stream.write(f"  [{issue.severity.upper()}] {issue.message}\n")
            if issue.location:
                stream.write(f"      ↳ {issue.location}\n")
            if issue.details:
                for key, value in issue.details.items():
                    stream.write(f"        {key}: {value}\n")
        stream.write("\n")

    if info:
        stream.write("INFO:\n")
        for issue in info:
            stream.write(f"  [{issue.severity.upper()}] {issue.message}\n")
            if issue.location:
                stream.write(f"      ↳ {issue.location}\n")


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
    file_path = result.metadata.get("file_path", "<unknown>")
    file_format = result.metadata.get("file_format", "")

    # Header
    lines.append(f"# USD Linting Report")
    lines.append("")
    lines.append(f"**File**: `{file_path}`")
    lines.append(f"**Format**: {file_format}")
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
