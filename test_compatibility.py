#!/usr/bin/env python3
"""Test script to verify Python version compatibility.

This script tests that the package works correctly on the current Python version.
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core imports
        from vfxvox_pipeline_utils import __version__
        from vfxvox_pipeline_utils.core.validators import BaseValidator, ValidationResult, ValidationIssue
        from vfxvox_pipeline_utils.core.config import Config
        from vfxvox_pipeline_utils.core.exceptions import VFXVoxError
        from vfxvox_pipeline_utils.core.logging import setup_logging, get_logger
        
        # ShotLint imports
        from vfxvox_pipeline_utils.shotlint.validator import ShotLintValidator
        from vfxvox_pipeline_utils.shotlint.engine import RuleEngine
        from vfxvox_pipeline_utils.shotlint.rules import PathPatternRule
        
        # Sequences imports
        from vfxvox_pipeline_utils.sequences.validator import SequenceValidator
        from vfxvox_pipeline_utils.sequences.scanner import SequenceScanner
        from vfxvox_pipeline_utils.sequences.formats import get_format_handler
        
        # USD imports (may fail if USD not installed)
        try:
            from vfxvox_pipeline_utils.usd.linter import USDLinter
            from vfxvox_pipeline_utils.usd.rules import get_builtin_rules
            print("  ✓ USD module imports (USD available)")
        except ImportError as e:
            print(f"  ⚠ USD module imports skipped (USD not available: {e})")
        
        # CLI imports
        from vfxvox_pipeline_utils.cli.main import cli
        
        print("  ✓ All imports successful")
        return True
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality of validators."""
    print("\nTesting basic functionality...")
    
    try:
        # Test Config
        from vfxvox_pipeline_utils.core.config import Config
        config = Config()
        assert config.get("sequences.check_resolution") == True
        print("  ✓ Config works")
        
        # Test ValidationResult
        from vfxvox_pipeline_utils.core.validators import ValidationResult, ValidationIssue
        result = ValidationResult(passed=True)
        result.add_issue("error", "Test error", "test location")
        assert result.error_count() == 1
        assert not result.passed
        print("  ✓ ValidationResult works")
        
        # Test SequenceValidator initialization
        from vfxvox_pipeline_utils.sequences.validator import SequenceValidator
        validator = SequenceValidator()
        assert validator is not None
        print("  ✓ SequenceValidator initializes")
        
        # Test ShotLintValidator initialization
        from vfxvox_pipeline_utils.shotlint.validator import ShotLintValidator
        validator = ShotLintValidator()
        assert validator is not None
        print("  ✓ ShotLintValidator initializes")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_type_hints():
    """Test that type hints are compatible."""
    print("\nTesting type hints compatibility...")
    
    try:
        # This will fail if type hints use incompatible syntax
        from vfxvox_pipeline_utils.core.validators import ValidationResult
        from vfxvox_pipeline_utils.sequences.validator import SequenceValidator
        from vfxvox_pipeline_utils.shotlint.validator import ShotLintValidator
        
        # Check that annotations work
        import inspect
        sig = inspect.signature(SequenceValidator.validate)
        assert 'pattern' in sig.parameters
        
        print("  ✓ Type hints compatible")
        return True
        
    except Exception as e:
        print(f"  ✗ Type hints test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all compatibility tests."""
    print("=" * 60)
    print("Python Version Compatibility Test")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Python version info: {sys.version_info}")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    
    if sys.version_info >= (3, 12):
        print("⚠ Testing on Python 3.12+, target is 3.8-3.11")
    
    print()
    
    # Run tests
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("Type Hints", test_type_hints()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    print()
    if all_passed:
        print("✓ All compatibility tests passed!")
        return True
    else:
        print("✗ Some compatibility tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
