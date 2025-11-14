#!/usr/bin/env python3
"""Example script demonstrating directory structure validation with ShotLint.

This script shows how to use the ShotLint module to validate VFX project
directory structures against studio standards defined in YAML rules.
"""

from pathlib import Path
from vfxvox_pipeline_utils.shotlint.validator import ShotLintValidator
from vfxvox_pipeline_utils.shotlint.reporters import render_console, render_json
import sys


def validate_project_structure(project_dir: str, rules_file: str):
    """Validate a project directory structure.
    
    Args:
        project_dir: Path to the project directory to validate
        rules_file: Path to the YAML rules file
    """
    print(f"Validating project: {project_dir}")
    print(f"Using rules: {rules_file}\n")
    
    # Create validator
    validator = ShotLintValidator()
    
    # Run validation
    result = validator.validate(
        root=Path(project_dir),
        rules_path=Path(rules_file)
    )
    
    # Display results
    render_console(result, sys.stdout)
    
    # Check results
    if result.has_errors():
        print(f"\n❌ Validation failed with {result.error_count()} errors")
        return False
    elif result.has_warnings():
        print(f"\n⚠️  Validation passed with {result.warning_count()} warnings")
        return True
    else:
        print("\n✅ Validation passed with no issues")
        return True


def validate_with_custom_rules():
    """Example using custom validation rules."""
    print("=" * 60)
    print("Example 1: Validating with strict rules")
    print("=" * 60 + "\n")
    
    validate_project_structure(
        project_dir="vfx_project",
        rules_file="vfx_project/shotlint_rules_strict.yaml"
    )


def validate_with_minimal_rules():
    """Example using minimal validation rules."""
    print("\n" + "=" * 60)
    print("Example 2: Validating with minimal rules")
    print("=" * 60 + "\n")
    
    validate_project_structure(
        project_dir="vfx_project",
        rules_file="vfx_project/shotlint_rules_minimal.yaml"
    )


def programmatic_validation():
    """Example of programmatic validation with result inspection."""
    print("\n" + "=" * 60)
    print("Example 3: Programmatic validation with result inspection")
    print("=" * 60 + "\n")
    
    validator = ShotLintValidator()
    result = validator.validate(
        root=Path("vfx_project"),
        rules_path=Path("vfx_project/shotlint_rules.yaml")
    )
    
    # Inspect results programmatically
    print(f"Total issues: {len(result.issues)}")
    print(f"Errors: {result.error_count()}")
    print(f"Warnings: {result.warning_count()}")
    print(f"Info: {result.info_count()}\n")
    
    # Group issues by severity
    errors = [issue for issue in result.issues if issue.severity == "error"]
    warnings = [issue for issue in result.issues if issue.severity == "warning"]
    
    if errors:
        print("Critical errors found:")
        for issue in errors[:3]:  # Show first 3
            print(f"  - {issue.message}")
            if issue.location:
                print(f"    Location: {issue.location}")
    
    if warnings:
        print("\nWarnings found:")
        for issue in warnings[:3]:  # Show first 3
            print(f"  - {issue.message}")
            if issue.location:
                print(f"    Location: {issue.location}")
    
    # Export to JSON for further processing
    json_output = render_json(result)
    output_file = Path("validation_report.json")
    output_file.write_text(json_output)
    print(f"\n📄 Full report saved to: {output_file}")


def main():
    """Run all examples."""
    # Change to examples directory
    examples_dir = Path(__file__).parent
    import os
    os.chdir(examples_dir)
    
    try:
        validate_with_custom_rules()
        validate_with_minimal_rules()
        programmatic_validation()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
