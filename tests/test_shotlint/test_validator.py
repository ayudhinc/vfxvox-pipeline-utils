"""Tests for ShotLint validator."""

import pytest
from pathlib import Path
import yaml

from vfxvox_pipeline_utils.shotlint.validator import ShotLintValidator
from vfxvox_pipeline_utils.core.exceptions import FileNotFoundError, ConfigurationError


@pytest.mark.unit
def test_shotlint_validator_initialization():
    """Test that ShotLintValidator initializes correctly."""
    validator = ShotLintValidator()
    assert validator is not None
    assert validator.rules == []


@pytest.mark.unit
def test_validate_with_nonexistent_directory(temp_dir):
    """Test validation fails gracefully with nonexistent directory."""
    validator = ShotLintValidator()
    rules_file = temp_dir / "rules.yaml"
    rules_file.write_text("rules: []")
    
    nonexistent_dir = temp_dir / "nonexistent"
    
    with pytest.raises(FileNotFoundError) as exc_info:
        validator.validate(nonexistent_dir, rules_file)
    
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_with_nonexistent_rules_file(temp_dir):
    """Test validation fails gracefully with nonexistent rules file."""
    validator = ShotLintValidator()
    test_dir = temp_dir / "test_project"
    test_dir.mkdir()
    
    nonexistent_rules = temp_dir / "nonexistent_rules.yaml"
    
    with pytest.raises(FileNotFoundError) as exc_info:
        validator.validate(test_dir, nonexistent_rules)
    
    assert "rules file not found" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_with_invalid_rules_file(temp_dir):
    """Test validation fails gracefully with invalid YAML."""
    validator = ShotLintValidator()
    test_dir = temp_dir / "test_project"
    test_dir.mkdir()
    
    rules_file = temp_dir / "invalid_rules.yaml"
    rules_file.write_text("invalid: yaml: content: [")
    
    with pytest.raises(ConfigurationError):
        validator.validate(test_dir, rules_file)


@pytest.mark.unit
def test_validate_empty_rules(temp_dir):
    """Test validation with empty rules passes."""
    validator = ShotLintValidator()
    test_dir = temp_dir / "test_project"
    test_dir.mkdir()
    
    rules_file = temp_dir / "empty_rules.yaml"
    rules_file.write_text("rules: []")
    
    result = validator.validate(test_dir, rules_file)
    
    assert result.passed
    assert len(result.issues) == 0


@pytest.mark.unit
def test_load_rules_from_yaml(temp_dir):
    """Test loading rules from YAML file."""
    validator = ShotLintValidator()
    
    rules_content = """
rules:
  - name: "Test rule"
    type: "path_pattern"
    pattern: "seq_{sequence}/shot_{shot}"
    vars:
      sequence: "\\\\d{3}"
      shot: "\\\\d{3}"
    level: "error"
"""
    
    rules_file = temp_dir / "test_rules.yaml"
    rules_file.write_text(rules_content)
    
    rules = validator.load_rules(rules_file)
    
    assert len(rules) == 1
    assert rules[0]["name"] == "Test rule"
    assert rules[0]["type"] == "path_pattern"


@pytest.mark.integration
def test_validate_valid_directory_structure(create_test_directory_structure, temp_dir):
    """Test validation passes with valid directory structure."""
    # Create valid structure
    structure = {
        "seq_010": {
            "shot_010": {
                "comp": None,
                "plate": None
            },
            "shot_020": {
                "comp": None,
                "plate": None
            }
        }
    }
    
    test_dir = create_test_directory_structure(structure)
    
    # Create rules
    rules_content = """
rules:
  - name: "Sequence structure"
    type: "path_pattern"
    pattern: "seq_{sequence}/shot_{shot}"
    vars:
      sequence: "\\\\d{3}"
      shot: "\\\\d{3}"
    level: "error"
    message: "Must follow seq_XXX/shot_XXX structure"
"""
    
    rules_file = temp_dir / "rules.yaml"
    rules_file.write_text(rules_content)
    
    validator = ShotLintValidator()
    result = validator.validate(test_dir, rules_file)
    
    assert result.passed
    assert result.error_count() == 0


@pytest.mark.integration
def test_validate_invalid_directory_structure(create_test_directory_structure, temp_dir):
    """Test validation fails with invalid directory structure."""
    # Create invalid structure
    structure = {
        "sequence_010": {  # Wrong naming
            "shot_010": {
                "comp": None
            }
        }
    }
    
    test_dir = create_test_directory_structure(structure)
    
    # Create rules
    rules_content = """
rules:
  - name: "Sequence structure"
    type: "path_pattern"
    pattern: "seq_{sequence}/shot_{shot}"
    vars:
      sequence: "\\\\d{3}"
      shot: "\\\\d{3}"
    level: "error"
    message: "Must follow seq_XXX/shot_XXX structure"
"""
    
    rules_file = temp_dir / "rules.yaml"
    rules_file.write_text(rules_content)
    
    validator = ShotLintValidator()
    result = validator.validate(test_dir, rules_file)
    
    assert not result.passed
    assert result.error_count() > 0


@pytest.mark.integration
def test_validate_with_file_instead_of_directory(temp_dir):
    """Test validation fails when given a file instead of directory."""
    validator = ShotLintValidator()
    
    # Create a file
    test_file = temp_dir / "test_file.txt"
    test_file.write_text("test")
    
    rules_file = temp_dir / "rules.yaml"
    rules_file.write_text("rules: []")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        validator.validate(test_file, rules_file)
    
    assert "not a directory" in str(exc_info.value).lower()
