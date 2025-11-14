#!/usr/bin/env python3
"""Example script demonstrating USD linting with custom rules.

This script shows how to use the USD Linter module to validate USD files
for common issues and enforce studio-specific conventions.
"""

from pathlib import Path
from vfxvox_pipeline_utils.usd.linter import USDLinter
from vfxvox_pipeline_utils.usd.reporters import render_console, render_json
from vfxvox_pipeline_utils.core.config import Config
import sys


def basic_usd_linting():
    """Example 1: Basic USD linting with built-in rules."""
    print("=" * 60)
    print("Example 1: Basic USD Linting")
    print("=" * 60 + "\n")
    
    # Create linter
    linter = USDLinter()
    
    # Lint a USD file
    usd_file = "vfx_project/assets/characters/hero/model/hero.usd"
    
    print(f"Linting USD file: {usd_file}\n")
    
    try:
        result = linter.validate(Path(usd_file))
        
        # Display results
        render_console(result, sys.stdout)
        
        # Check status
        if result.has_errors():
            print(f"\n❌ Linting failed: {result.error_count()} errors found")
        elif result.has_warnings():
            print(f"\n⚠️  Linting passed with {result.warning_count()} warnings")
        else:
            print("\n✅ USD file is valid")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def lint_with_custom_rules():
    """Example 2: Linting with custom rules from configuration."""
    print("\n" + "=" * 60)
    print("Example 2: Custom Rules Configuration")
    print("=" * 60 + "\n")
    
    # First, create a custom rules configuration file
    custom_rules_yaml = """
custom_rules:
  - name: naming_convention
    type: naming
    patterns:
      prim: "^[A-Z][a-zA-Z0-9_]*$"
      property: "^[a-z][a-zA-Z0-9_]*$"
    severity: warning
    message: "Prims must start with uppercase, properties with lowercase"
    
  - name: required_metadata
    type: metadata
    required_fields:
      - assetInfo:identifier
      - assetInfo:version
      - assetInfo:name
    severity: error
    message: "Asset must have required metadata fields"
    
  - name: forbidden_patterns
    type: naming
    patterns:
      prim: "^(?!temp_|test_|debug_)"
    severity: warning
    message: "Temporary naming patterns detected (temp_, test_, debug_)"
"""
    
    # Save custom rules
    rules_file = Path("custom_usd_rules.yaml")
    rules_file.write_text(custom_rules_yaml)
    print(f"Created custom rules file: {rules_file}\n")
    
    # Create config with custom rules
    config = Config.from_dict({
        "usd": {
            "custom_rules_path": str(rules_file),
            "check_references": True,
            "check_schemas": True,
            "check_performance": True,
            "max_layer_depth": 10
        }
    })
    
    # Create linter with config
    linter = USDLinter(config=config)
    
    usd_file = "vfx_project/assets/characters/hero/model/hero.usd"
    
    print(f"Linting with custom rules: {usd_file}\n")
    
    try:
        result = linter.validate(Path(usd_file))
        render_console(result, sys.stdout)
    except Exception as e:
        print(f"❌ Error: {e}")


def inspect_usd_issues():
    """Example 3: Programmatic inspection of linting results."""
    print("\n" + "=" * 60)
    print("Example 3: Programmatic Issue Inspection")
    print("=" * 60 + "\n")
    
    linter = USDLinter()
    usd_file = "vfx_project/assets/characters/hero/model/hero.usd"
    
    try:
        result = linter.validate(Path(usd_file))
        
        print(f"USD File: {usd_file}")
        print(f"Total issues: {len(result.issues)}\n")
        
        # Group issues by severity
        errors = [i for i in result.issues if i.severity == "error"]
        warnings = [i for i in result.issues if i.severity == "warning"]
        info = [i for i in result.issues if i.severity == "info"]
        
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print(f"Info: {len(info)}\n")
        
        # Group issues by type
        from collections import defaultdict
        issues_by_type = defaultdict(list)
        
        for issue in result.issues:
            # Extract issue type from message or details
            issue_type = issue.details.get("rule", "unknown") if issue.details else "unknown"
            issues_by_type[issue_type].append(issue)
        
        print("Issues by type:")
        for issue_type, issues in sorted(issues_by_type.items()):
            print(f"  {issue_type}: {len(issues)}")
        
        # Show critical errors
        if errors:
            print("\nCritical errors:")
            for error in errors[:5]:  # Show first 5
                print(f"  - {error.message}")
                if error.location:
                    print(f"    Location: {error.location}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


def batch_lint_assets():
    """Example 4: Batch linting multiple USD files."""
    print("\n" + "=" * 60)
    print("Example 4: Batch Linting")
    print("=" * 60 + "\n")
    
    # Find all USD files in assets directory
    assets_dir = Path("vfx_project/assets")
    usd_files = []
    
    if assets_dir.exists():
        usd_files = list(assets_dir.rglob("*.usd"))
        usd_files.extend(assets_dir.rglob("*.usda"))
        usd_files.extend(assets_dir.rglob("*.usdc"))
    
    if not usd_files:
        print("No USD files found in assets directory")
        return
    
    print(f"Found {len(usd_files)} USD files\n")
    
    linter = USDLinter()
    results = []
    
    for usd_file in usd_files:
        print(f"Linting: {usd_file.relative_to(Path.cwd())}")
        print("-" * 60)
        
        try:
            result = linter.validate(usd_file)
            results.append((usd_file, result))
            
            # Quick summary
            status = "✅" if result.passed else "❌"
            print(f"{status} Issues: {len(result.issues)} "
                  f"(E:{result.error_count()}, W:{result.warning_count()})\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
            results.append((usd_file, None))
    
    # Overall summary
    print("=" * 60)
    print("Batch Linting Summary")
    print("=" * 60)
    
    total_files = len(results)
    passed = sum(1 for _, r in results if r and r.passed)
    failed = sum(1 for _, r in results if r and not r.passed)
    errors = sum(1 for _, r in results if r is None)
    
    total_issues = sum(len(r.issues) for _, r in results if r)
    total_errors = sum(r.error_count() for _, r in results if r)
    total_warnings = sum(r.warning_count() for _, r in results if r)
    
    print(f"\nFiles processed: {total_files}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors during linting: {errors}")
    print(f"\nTotal issues: {total_issues}")
    print(f"  Errors: {total_errors}")
    print(f"  Warnings: {total_warnings}")


def performance_analysis():
    """Example 5: USD performance analysis."""
    print("\n" + "=" * 60)
    print("Example 5: Performance Analysis")
    print("=" * 60 + "\n")
    
    # Create config focused on performance checks
    config = Config.from_dict({
        "usd": {
            "check_performance": True,
            "max_layer_depth": 5,  # Stricter limit
            "check_references": False,  # Skip for performance focus
            "check_schemas": False
        }
    })
    
    linter = USDLinter(config=config)
    usd_file = "vfx_project/assets/characters/hero/model/hero.usd"
    
    print(f"Analyzing performance: {usd_file}\n")
    
    try:
        result = linter.validate(Path(usd_file))
        
        # Filter performance-related issues
        perf_issues = [
            i for i in result.issues 
            if i.details and "performance" in i.details.get("rule", "").lower()
        ]
        
        if perf_issues:
            print(f"Found {len(perf_issues)} performance issues:\n")
            for issue in perf_issues:
                print(f"  [{issue.severity.upper()}] {issue.message}")
                if issue.location:
                    print(f"    Location: {issue.location}")
                if issue.details:
                    for key, value in issue.details.items():
                        if key != "rule":
                            print(f"    {key}: {value}")
                print()
        else:
            print("✅ No performance issues detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def export_lint_reports():
    """Example 6: Exporting lint reports in various formats."""
    print("\n" + "=" * 60)
    print("Example 6: Exporting Reports")
    print("=" * 60 + "\n")
    
    linter = USDLinter()
    usd_file = "vfx_project/assets/characters/hero/model/hero.usd"
    
    try:
        result = linter.validate(Path(usd_file))
        
        # Export to JSON
        json_report = render_json(result)
        json_file = Path("usd_lint_report.json")
        json_file.write_text(json_report)
        print(f"📄 JSON report saved to: {json_file}")
        
        # Export to YAML
        from vfxvox_pipeline_utils.usd.reporters import render_yaml
        yaml_report = render_yaml(result)
        yaml_file = Path("usd_lint_report.yaml")
        yaml_file.write_text(yaml_report)
        print(f"📄 YAML report saved to: {yaml_file}")
        
        # Export to Markdown
        from vfxvox_pipeline_utils.usd.reporters import render_markdown
        md_report = render_markdown(result)
        md_file = Path("usd_lint_report.md")
        md_file.write_text(md_report)
        print(f"📄 Markdown report saved to: {md_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples."""
    # Change to examples directory
    examples_dir = Path(__file__).parent
    import os
    os.chdir(examples_dir)
    
    print("USD Linting Examples")
    print("=" * 60)
    print("Note: These examples require USD Python bindings (usd-core)")
    print("Install with: pip install vfxvox-pipeline-utils[usd]")
    print("=" * 60 + "\n")
    
    try:
        basic_usd_linting()
        lint_with_custom_rules()
        inspect_usd_issues()
        batch_lint_assets()
        performance_analysis()
        export_lint_reports()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
