#!/usr/bin/env python3
"""Example script demonstrating image sequence validation.

This script shows how to use the Sequence Validator module to check
image sequences for missing frames, corrupted files, and consistency issues.
"""

from pathlib import Path
from vfxvox_pipeline_utils.sequences.validator import SequenceValidator
from vfxvox_pipeline_utils.sequences.scanner import SequenceScanner
from vfxvox_pipeline_utils.sequences.reporters import render_console, render_json
from vfxvox_pipeline_utils.core.config import Config
import sys


def basic_sequence_validation():
    """Example 1: Basic sequence validation."""
    print("=" * 60)
    print("Example 1: Basic Sequence Validation")
    print("=" * 60 + "\n")
    
    # Create validator
    validator = SequenceValidator()
    
    # Validate a sequence using printf-style pattern
    pattern = "vfx_project/seq_010/shot_010/comp/v001/shot_010_v001_comp.%04d.exr"
    
    print(f"Validating sequence: {pattern}\n")
    
    result = validator.validate(pattern)
    
    # Display results
    render_console(result, sys.stdout)
    
    # Check status
    if result.has_errors():
        print(f"\n❌ Validation failed: {result.error_count()} errors found")
    elif result.has_warnings():
        print(f"\n⚠️  Validation passed with {result.warning_count()} warnings")
    else:
        print("\n✅ Sequence is valid")


def validate_with_different_patterns():
    """Example 2: Validating sequences with different pattern styles."""
    print("\n" + "=" * 60)
    print("Example 2: Different Pattern Styles")
    print("=" * 60 + "\n")
    
    patterns = [
        ("Printf style", "renders/shot_010.%04d.exr"),
        ("Hash style", "renders/shot_010.####.exr"),
        ("Range style", "renders/shot_010.[1001-1100].exr"),
    ]
    
    validator = SequenceValidator()
    
    for name, pattern in patterns:
        print(f"\n{name}: {pattern}")
        print("-" * 40)
        
        try:
            result = validator.validate(pattern)
            print(f"  Frames found: {result.metadata.get('frame_count', 0)}")
            print(f"  Frame range: {result.metadata.get('frame_range', 'N/A')}")
            print(f"  Issues: {len(result.issues)}")
        except Exception as e:
            print(f"  Error: {e}")


def validate_with_custom_config():
    """Example 3: Validation with custom configuration."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Configuration")
    print("=" * 60 + "\n")
    
    # Create custom config
    config = Config.from_dict({
        "sequences": {
            "check_resolution": True,
            "check_bit_depth": True,
            "supported_formats": ["exr", "dpx", "png"]
        }
    })
    
    # Create validator with config
    validator = SequenceValidator(config=config)
    
    pattern = "vfx_project/seq_010/shot_010/plate/shot_010_plate.%04d.exr"
    
    print(f"Validating with custom config: {pattern}\n")
    
    result = validator.validate(pattern)
    render_console(result, sys.stdout)


def scan_sequence_details():
    """Example 4: Detailed sequence scanning."""
    print("\n" + "=" * 60)
    print("Example 4: Detailed Sequence Scanning")
    print("=" * 60 + "\n")
    
    pattern = "vfx_project/seq_010/shot_010/comp/v001/shot_010_v001_comp.%04d.exr"
    
    # Create scanner
    scanner = SequenceScanner(pattern)
    
    # Detect frames
    frame_numbers = scanner.detect_frames()
    print(f"Pattern: {pattern}")
    print(f"Frames detected: {len(frame_numbers)}")
    
    if frame_numbers:
        frame_range = scanner.get_frame_range()
        print(f"Frame range: {frame_range[0]}-{frame_range[1]}")
        
        # Check for gaps
        expected_frames = set(range(frame_range[0], frame_range[1] + 1))
        actual_frames = set(frame_numbers)
        missing = sorted(expected_frames - actual_frames)
        
        if missing:
            print(f"\n⚠️  Missing frames: {len(missing)}")
            # Show first few missing frames
            if len(missing) <= 10:
                print(f"   {missing}")
            else:
                print(f"   {missing[:5]} ... {missing[-5:]}")
        else:
            print("\n✅ No missing frames")
        
        # Scan a few frames for details
        print("\nSample frame details:")
        for frame_num in frame_numbers[:3]:
            frame_info = scanner.scan_frame(frame_num)
            print(f"\n  Frame {frame_num}:")
            print(f"    Exists: {frame_info.exists}")
            print(f"    Readable: {frame_info.readable}")
            if frame_info.resolution:
                print(f"    Resolution: {frame_info.resolution[0]}x{frame_info.resolution[1]}")
            if frame_info.bit_depth:
                print(f"    Bit depth: {frame_info.bit_depth}")


def batch_validation():
    """Example 5: Batch validation of multiple sequences."""
    print("\n" + "=" * 60)
    print("Example 5: Batch Validation")
    print("=" * 60 + "\n")
    
    # List of sequences to validate
    sequences = [
        "vfx_project/seq_010/shot_010/comp/v001/shot_010_v001_comp.%04d.exr",
        "vfx_project/seq_010/shot_010/plate/shot_010_plate.%04d.exr",
        "vfx_project/seq_010/shot_020/comp/v001/shot_020_v001_comp.%04d.exr",
    ]
    
    validator = SequenceValidator()
    results = []
    
    for pattern in sequences:
        print(f"\nValidating: {pattern}")
        print("-" * 60)
        
        try:
            result = validator.validate(pattern)
            results.append((pattern, result))
            
            # Quick summary
            status = "✅" if result.passed else "❌"
            print(f"{status} Frames: {result.metadata.get('frame_count', 0)}, "
                  f"Issues: {len(result.issues)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((pattern, None))
    
    # Overall summary
    print("\n" + "=" * 60)
    print("Batch Validation Summary")
    print("=" * 60)
    
    total_sequences = len(results)
    passed = sum(1 for _, r in results if r and r.passed)
    failed = sum(1 for _, r in results if r and not r.passed)
    errors = sum(1 for _, r in results if r is None)
    
    print(f"\nTotal sequences: {total_sequences}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")


def export_validation_report():
    """Example 6: Exporting validation reports."""
    print("\n" + "=" * 60)
    print("Example 6: Exporting Reports")
    print("=" * 60 + "\n")
    
    validator = SequenceValidator()
    pattern = "vfx_project/seq_010/shot_010/comp/v001/shot_010_v001_comp.%04d.exr"
    
    result = validator.validate(pattern)
    
    # Export to JSON
    json_report = render_json(result)
    json_file = Path("sequence_validation_report.json")
    json_file.write_text(json_report)
    print(f"📄 JSON report saved to: {json_file}")
    
    # Export to YAML
    from vfxvox_pipeline_utils.sequences.reporters import render_yaml
    yaml_report = render_yaml(result)
    yaml_file = Path("sequence_validation_report.yaml")
    yaml_file.write_text(yaml_report)
    print(f"📄 YAML report saved to: {yaml_file}")
    
    # Export to Markdown
    from vfxvox_pipeline_utils.sequences.reporters import render_markdown
    md_report = render_markdown(result)
    md_file = Path("sequence_validation_report.md")
    md_file.write_text(md_report)
    print(f"📄 Markdown report saved to: {md_file}")


def main():
    """Run all examples."""
    # Change to examples directory
    examples_dir = Path(__file__).parent
    import os
    os.chdir(examples_dir)
    
    try:
        basic_sequence_validation()
        validate_with_different_patterns()
        validate_with_custom_config()
        scan_sequence_details()
        batch_validation()
        export_validation_report()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
