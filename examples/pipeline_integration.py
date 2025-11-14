#!/usr/bin/env python3
"""Example script demonstrating pipeline integration.

This script shows how to integrate VFXVox Pipeline Utils into production
pipelines for automated validation and quality control.
"""

from pathlib import Path
from typing import List, Dict, Any
from vfxvox_pipeline_utils.shotlint.validator import ShotLintValidator
from vfxvox_pipeline_utils.sequences.validator import SequenceValidator
from vfxvox_pipeline_utils.usd.linter import USDLinter
from vfxvox_pipeline_utils.core.config import Config
from vfxvox_pipeline_utils.core.logging import setup_logging, get_logger
import json
import sys


# Setup logging for pipeline
setup_logging(level="INFO")
logger = get_logger(__name__)


class PipelineValidator:
    """Integrated validator for VFX pipeline quality control."""
    
    def __init__(self, config_path: Path = None):
        """Initialize pipeline validator.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = Config(config_path) if config_path else Config()
        self.shotlint_validator = ShotLintValidator()
        self.sequence_validator = SequenceValidator(self.config)
        self.usd_linter = USDLinter(self.config)
        
    def validate_shot_delivery(self, shot_dir: Path, rules_path: Path) -> Dict[str, Any]:
        """Validate a complete shot delivery.
        
        Args:
            shot_dir: Path to shot directory
            rules_path: Path to validation rules
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating shot delivery: {shot_dir}")
        
        results = {
            "shot_dir": str(shot_dir),
            "passed": True,
            "checks": {}
        }
        
        # 1. Validate directory structure
        logger.info("Checking directory structure...")
        try:
            structure_result = self.shotlint_validator.validate(shot_dir, rules_path)
            results["checks"]["structure"] = {
                "passed": structure_result.passed,
                "errors": structure_result.error_count(),
                "warnings": structure_result.warning_count()
            }
            if not structure_result.passed:
                results["passed"] = False
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            results["checks"]["structure"] = {"passed": False, "error": str(e)}
            results["passed"] = False
        
        # 2. Validate comp sequences
        logger.info("Checking comp sequences...")
        comp_sequences = list(shot_dir.rglob("comp/v*/shot_*_comp.*.exr"))
        if comp_sequences:
            seq_results = []
            for seq_file in comp_sequences:
                # Extract pattern from first file
                pattern = self._extract_sequence_pattern(seq_file)
                try:
                    seq_result = self.sequence_validator.validate(pattern)
                    seq_results.append({
                        "pattern": pattern,
                        "passed": seq_result.passed,
                        "errors": seq_result.error_count()
                    })
                    if not seq_result.passed:
                        results["passed"] = False
                except Exception as e:
                    logger.error(f"Sequence validation failed for {pattern}: {e}")
                    seq_results.append({"pattern": pattern, "passed": False, "error": str(e)})
                    results["passed"] = False
            
            results["checks"]["sequences"] = {
                "total": len(seq_results),
                "passed": sum(1 for r in seq_results if r.get("passed", False)),
                "details": seq_results
            }
        
        # 3. Validate USD assets
        logger.info("Checking USD assets...")
        usd_files = list(shot_dir.rglob("*.usd*"))
        if usd_files:
            usd_results = []
            for usd_file in usd_files:
                try:
                    usd_result = self.usd_linter.validate(usd_file)
                    usd_results.append({
                        "file": str(usd_file.relative_to(shot_dir)),
                        "passed": usd_result.passed,
                        "errors": usd_result.error_count()
                    })
                    if not usd_result.passed:
                        results["passed"] = False
                except Exception as e:
                    logger.error(f"USD linting failed for {usd_file}: {e}")
                    usd_results.append({
                        "file": str(usd_file.relative_to(shot_dir)),
                        "passed": False,
                        "error": str(e)
                    })
            
            results["checks"]["usd"] = {
                "total": len(usd_results),
                "passed": sum(1 for r in usd_results if r.get("passed", False)),
                "details": usd_results
            }
        
        logger.info(f"Shot validation complete: {'PASSED' if results['passed'] else 'FAILED'}")
        return results
    
    def _extract_sequence_pattern(self, file_path: Path) -> str:
        """Extract sequence pattern from a file path.
        
        Args:
            file_path: Path to a frame file
            
        Returns:
            Sequence pattern string
        """
        # Simple pattern extraction - replace frame number with %04d
        name = file_path.stem
        # Find frame number (assumes 4-digit padding)
        import re
        pattern = re.sub(r'\.\d{4}$', '.%04d', name)
        return str(file_path.parent / f"{pattern}{file_path.suffix}")


def pre_render_validation(shot_dir: Path) -> bool:
    """Pre-render validation hook.
    
    Validates shot before submitting to render farm.
    
    Args:
        shot_dir: Path to shot directory
        
    Returns:
        True if validation passed, False otherwise
    """
    logger.info("=" * 60)
    logger.info("PRE-RENDER VALIDATION")
    logger.info("=" * 60)
    
    validator = PipelineValidator()
    rules_path = Path("vfx_project/shotlint_rules.yaml")
    
    results = validator.validate_shot_delivery(shot_dir, rules_path)
    
    # Print summary
    print("\nValidation Summary:")
    print("-" * 60)
    print(f"Shot: {results['shot_dir']}")
    print(f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}")
    print()
    
    for check_name, check_result in results["checks"].items():
        if isinstance(check_result, dict):
            status = "✅" if check_result.get("passed", False) else "❌"
            print(f"{status} {check_name.title()}: ", end="")
            if "errors" in check_result:
                print(f"{check_result['errors']} errors, {check_result.get('warnings', 0)} warnings")
            elif "total" in check_result:
                print(f"{check_result['passed']}/{check_result['total']} passed")
    
    return results["passed"]


def post_render_validation(sequence_pattern: str) -> bool:
    """Post-render validation hook.
    
    Validates rendered sequence after render completes.
    
    Args:
        sequence_pattern: Pattern for rendered sequence
        
    Returns:
        True if validation passed, False otherwise
    """
    logger.info("=" * 60)
    logger.info("POST-RENDER VALIDATION")
    logger.info("=" * 60)
    
    validator = SequenceValidator()
    
    logger.info(f"Validating rendered sequence: {sequence_pattern}")
    
    try:
        result = validator.validate(sequence_pattern)
        
        print("\nValidation Results:")
        print("-" * 60)
        print(f"Pattern: {sequence_pattern}")
        print(f"Frames: {result.metadata.get('frame_count', 0)}")
        print(f"Range: {result.metadata.get('frame_range', 'N/A')}")
        print(f"Errors: {result.error_count()}")
        print(f"Warnings: {result.warning_count()}")
        print(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        
        if not result.passed:
            print("\nIssues found:")
            for issue in result.issues[:10]:  # Show first 10
                print(f"  [{issue.severity.upper()}] {issue.message}")
                if issue.location:
                    print(f"    Location: {issue.location}")
        
        return result.passed
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n❌ Validation error: {e}")
        return False


def asset_publish_validation(asset_dir: Path) -> bool:
    """Asset publish validation hook.
    
    Validates asset before publishing to asset library.
    
    Args:
        asset_dir: Path to asset directory
        
    Returns:
        True if validation passed, False otherwise
    """
    logger.info("=" * 60)
    logger.info("ASSET PUBLISH VALIDATION")
    logger.info("=" * 60)
    
    # Check directory structure
    required_folders = ["model", "texture", "rig"]
    missing_folders = [f for f in required_folders if not (asset_dir / f).exists()]
    
    if missing_folders:
        logger.error(f"Missing required folders: {missing_folders}")
        print(f"\n❌ Missing folders: {', '.join(missing_folders)}")
        return False
    
    # Validate USD files
    linter = USDLinter()
    usd_files = list(asset_dir.rglob("*.usd*"))
    
    if not usd_files:
        logger.error("No USD files found in asset")
        print("\n❌ No USD files found")
        return False
    
    print(f"\nValidating {len(usd_files)} USD files...")
    
    all_passed = True
    for usd_file in usd_files:
        try:
            result = linter.validate(usd_file)
            status = "✅" if result.passed else "❌"
            print(f"{status} {usd_file.name}: {result.error_count()} errors")
            
            if not result.passed:
                all_passed = False
                # Show first few errors
                for issue in result.issues[:3]:
                    if issue.severity == "error":
                        print(f"    - {issue.message}")
                        
        except Exception as e:
            logger.error(f"Failed to lint {usd_file}: {e}")
            print(f"❌ {usd_file.name}: Error - {e}")
            all_passed = False
    
    print(f"\nAsset validation: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    return all_passed


def batch_shot_validation(project_dir: Path, output_report: Path):
    """Batch validate all shots in a project.
    
    Args:
        project_dir: Path to project directory
        output_report: Path to save validation report
    """
    logger.info("=" * 60)
    logger.info("BATCH SHOT VALIDATION")
    logger.info("=" * 60)
    
    validator = PipelineValidator()
    rules_path = project_dir / "shotlint_rules.yaml"
    
    # Find all shot directories
    shot_dirs = [d for d in project_dir.rglob("shot_*") if d.is_dir()]
    
    logger.info(f"Found {len(shot_dirs)} shots to validate")
    
    all_results = []
    
    for shot_dir in shot_dirs:
        logger.info(f"\nValidating: {shot_dir.relative_to(project_dir)}")
        
        try:
            results = validator.validate_shot_delivery(shot_dir, rules_path)
            all_results.append(results)
            
            status = "✅" if results["passed"] else "❌"
            print(f"{status} {shot_dir.name}")
            
        except Exception as e:
            logger.error(f"Validation failed for {shot_dir}: {e}")
            all_results.append({
                "shot_dir": str(shot_dir),
                "passed": False,
                "error": str(e)
            })
    
    # Generate summary report
    summary = {
        "project": str(project_dir),
        "total_shots": len(all_results),
        "passed": sum(1 for r in all_results if r.get("passed", False)),
        "failed": sum(1 for r in all_results if not r.get("passed", False)),
        "shots": all_results
    }
    
    # Save report
    output_report.write_text(json.dumps(summary, indent=2))
    logger.info(f"\n📄 Report saved to: {output_report}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("BATCH VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total shots: {summary['total_shots']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success rate: {summary['passed']/summary['total_shots']*100:.1f}%")


def main():
    """Run pipeline integration examples."""
    # Change to examples directory
    examples_dir = Path(__file__).parent
    import os
    os.chdir(examples_dir)
    
    print("Pipeline Integration Examples")
    print("=" * 60 + "\n")
    
    try:
        # Example 1: Pre-render validation
        shot_dir = Path("vfx_project/seq_010/shot_010")
        if shot_dir.exists():
            passed = pre_render_validation(shot_dir)
            if not passed:
                print("\n⚠️  Pre-render validation failed - fix issues before rendering")
        
        # Example 2: Post-render validation
        print("\n")
        sequence = "vfx_project/seq_010/shot_010/comp/v001/shot_010_v001_comp.%04d.exr"
        post_render_validation(sequence)
        
        # Example 3: Asset publish validation
        print("\n")
        asset_dir = Path("vfx_project/assets/characters/hero")
        if asset_dir.exists():
            asset_publish_validation(asset_dir)
        
        # Example 4: Batch validation
        print("\n")
        project_dir = Path("vfx_project")
        if project_dir.exists():
            batch_shot_validation(project_dir, Path("batch_validation_report.json"))
        
    except Exception as e:
        logger.error(f"Pipeline integration error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
