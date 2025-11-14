"""Tests for ShotLint rule engine."""

import pytest
from pathlib import Path

from vfxvox_pipeline_utils.shotlint.engine import RuleEngine


@pytest.mark.unit
def test_engine_initialization(temp_dir):
    """Test RuleEngine initializes correctly."""
    engine = RuleEngine(temp_dir)
    assert engine is not None
    assert engine.root == temp_dir


@pytest.mark.unit
def test_execute_path_pattern_rule(create_test_directory_structure):
    """Test executing path_pattern rule through engine."""
    structure = {
        "seq_010": {
            "shot_010": None
        }
    }
    
    root = create_test_directory_structure(structure)
    engine = RuleEngine(root)
    
    rule = {
        "name": "Test pattern",
        "type": "path_pattern",
        "pattern": "seq_{sequence}/shot_{shot}",
        "vars": {
            "sequence": r"\d{3}",
            "shot": r"\d{3}"
        },
        "level": "error",
        "message": "Invalid structure"
    }
    
    issues = engine.execute_rule(rule)
    
    assert isinstance(issues, list)
    assert len(issues) == 0  # Valid structure


@pytest.mark.unit
def test_execute_filename_regex_rule(create_test_directory_structure):
    """Test executing filename_regex rule through engine."""
    structure = {
        "comp": {
            "shot_010_comp.0001.exr": ""
        }
    }
    
    root = create_test_directory_structure(structure)
    engine = RuleEngine(root)
    
    rule = {
        "name": "Filename check",
        "type": "filename_regex",
        "path": "comp",
        "regex": r"^shot_\d{3}_comp\.\d{4}\.exr$",
        "level": "error",
        "message": "Invalid filename"
    }
    
    issues = engine.execute_rule(rule)
    
    assert isinstance(issues, list)
    assert len(issues) == 0  # Valid filename


@pytest.mark.unit
def test_execute_must_exist_rule(create_test_directory_structure):
    """Test executing must_exist rule through engine."""
    structure = {
        "seq_010": {
            "shot_010": {
                "comp": None
            }
        }
    }
    
    root = create_test_directory_structure(structure)
    engine = RuleEngine(root)
    
    rule = {
        "name": "Required folder",
        "type": "must_exist",
        "glob": "seq_*/shot_*/comp",
        "level": "error",
        "message": "Comp folder missing"
    }
    
    issues = engine.execute_rule(rule)
    
    assert isinstance(issues, list)
    assert len(issues) == 0  # Folder exists


@pytest.mark.unit
def test_execute_frame_sequence_rule(create_test_directory_structure):
    """Test executing frame_sequence rule through engine."""
    structure = {
        "comp": {
            "shot_010.1001.exr": "",
            "shot_010.1002.exr": "",
            "shot_010.1003.exr": ""
        }
    }
    
    root = create_test_directory_structure(structure)
    engine = RuleEngine(root)
    
    rule = {
        "name": "Frame sequence",
        "type": "frame_sequence",
        "folder": "comp",
        "base": "shot_010",
        "ext": ".exr",
        "start": 1001,
        "end": 1003,
        "padding": 4,
        "level": "error",
        "message": "Missing frames"
    }
    
    issues = engine.execute_rule(rule)
    
    assert isinstance(issues, list)
    assert len(issues) == 0  # Complete sequence


@pytest.mark.unit
def test_execute_all_rules(create_test_directory_structure):
    """Test executing multiple rules."""
    structure = {
        "seq_010": {
            "shot_010": {
                "comp": {
                    "shot_010_comp.0001.exr": ""
                }
            }
        }
    }
    
    root = create_test_directory_structure(structure)
    engine = RuleEngine(root)
    
    rules = [
        {
            "name": "Structure",
            "type": "path_pattern",
            "pattern": "seq_{sequence}/shot_{shot}",
            "vars": {
                "sequence": r"\d{3}",
                "shot": r"\d{3}"
            },
            "level": "error",
            "message": "Invalid structure"
        },
        {
            "name": "Comp folder",
            "type": "must_exist",
            "glob": "seq_*/shot_*/comp",
            "level": "error",
            "message": "Comp missing"
        }
    ]
    
    issues = engine.execute_all(rules)
    
    assert isinstance(issues, list)
    # Both rules should pass
    assert len(issues) == 0


@pytest.mark.unit
def test_execute_unknown_rule_type(temp_dir):
    """Test executing unknown rule type."""
    engine = RuleEngine(temp_dir)
    
    rule = {
        "name": "Unknown",
        "type": "unknown_type",
        "level": "error",
        "message": "Test"
    }
    
    issues = engine.execute_rule(rule)
    
    # Should handle gracefully and return error issue
    assert isinstance(issues, list)
    assert len(issues) > 0
    assert any("unknown" in issue.message.lower() for issue in issues)


@pytest.mark.unit
def test_execute_rule_with_missing_required_fields(temp_dir):
    """Test executing rule with missing required fields."""
    engine = RuleEngine(temp_dir)
    
    rule = {
        "name": "Incomplete",
        "type": "path_pattern",
        # Missing pattern and vars
        "level": "error",
        "message": "Test"
    }
    
    issues = engine.execute_rule(rule)
    
    # Should handle gracefully
    assert isinstance(issues, list)


@pytest.mark.integration
def test_engine_with_mixed_results(create_test_directory_structure):
    """Test engine with rules that produce mixed results."""
    structure = {
        "seq_010": {
            "shot_010": {
                "comp": None
                # Missing plate folder
            }
        }
    }
    
    root = create_test_directory_structure(structure)
    engine = RuleEngine(root)
    
    rules = [
        {
            "name": "Comp exists",
            "type": "must_exist",
            "glob": "seq_*/shot_*/comp",
            "level": "error",
            "message": "Comp missing"
        },
        {
            "name": "Plate exists",
            "type": "must_exist",
            "glob": "seq_*/shot_*/plate",
            "level": "warning",
            "message": "Plate missing"
        }
    ]
    
    issues = engine.execute_all(rules)
    
    assert isinstance(issues, list)
    # First rule passes, second fails
    assert len(issues) > 0
    assert any("plate" in issue.message.lower() for issue in issues)
