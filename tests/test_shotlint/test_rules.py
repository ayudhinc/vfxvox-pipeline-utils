"""Tests for ShotLint rule implementations."""

import pytest
from pathlib import Path

from vfxvox_pipeline_utils.shotlint.rules import (
    PathPatternRule,
    FilenameRegexRule,
    FrameSequenceRule,
    MustExistRule
)


@pytest.mark.unit
class TestPathPatternRule:
    """Tests for PathPatternRule."""
    
    def test_valid_path_pattern(self, create_test_directory_structure):
        """Test path pattern validation with valid structure."""
        structure = {
            "seq_010": {
                "shot_010": None,
                "shot_020": None
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "pattern": "seq_{sequence}/shot_{shot}",
            "vars": {
                "sequence": r"\d{3}",
                "shot": r"\d{3}"
            },
            "level": "error",
            "message": "Must follow pattern"
        }
        
        rule = PathPatternRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0
    
    def test_invalid_path_pattern(self, create_test_directory_structure):
        """Test path pattern validation with invalid structure."""
        structure = {
            "sequence_010": {  # Wrong prefix
                "shot_010": None
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "pattern": "seq_{sequence}/shot_{shot}",
            "vars": {
                "sequence": r"\d{3}",
                "shot": r"\d{3}"
            },
            "level": "error",
            "message": "Must follow pattern"
        }
        
        rule = PathPatternRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) > 0
        assert any("pattern" in issue.message.lower() for issue in issues)
    
    def test_path_pattern_with_multiple_levels(self, create_test_directory_structure):
        """Test path pattern with multiple directory levels."""
        structure = {
            "seq_010": {
                "shot_010": {
                    "comp": {
                        "v001": None
                    }
                }
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "pattern": "seq_{sequence}/shot_{shot}/comp/v{version}",
            "vars": {
                "sequence": r"\d{3}",
                "shot": r"\d{3}",
                "version": r"\d{3}"
            },
            "level": "error",
            "message": "Must follow pattern"
        }
        
        rule = PathPatternRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0


@pytest.mark.unit
class TestFilenameRegexRule:
    """Tests for FilenameRegexRule."""
    
    def test_valid_filename_pattern(self, create_test_directory_structure):
        """Test filename regex validation with valid files."""
        structure = {
            "comp": {
                "shot_010_comp.0001.exr": "",
                "shot_010_comp.0002.exr": ""
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "path": "comp",
            "regex": r"^shot_\d{3}_comp\.\d{4}\.exr$",
            "level": "error",
            "message": "Invalid filename"
        }
        
        rule = FilenameRegexRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0
    
    def test_invalid_filename_pattern(self, create_test_directory_structure):
        """Test filename regex validation with invalid files."""
        structure = {
            "comp": {
                "invalid_name.exr": "",
                "shot_010_comp.0001.exr": ""
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "path": "comp",
            "regex": r"^shot_\d{3}_comp\.\d{4}\.exr$",
            "level": "error",
            "message": "Invalid filename"
        }
        
        rule = FilenameRegexRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) > 0
        assert any("invalid_name.exr" in issue.location for issue in issues)
    
    def test_filename_regex_with_wildcard_path(self, create_test_directory_structure):
        """Test filename regex with wildcard path."""
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
        
        rule_config = {
            "path": "seq_*/shot_*/comp",
            "regex": r"^shot_\d{3}_comp\.\d{4}\.exr$",
            "level": "error",
            "message": "Invalid filename"
        }
        
        rule = FilenameRegexRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0


@pytest.mark.unit
class TestFrameSequenceRule:
    """Tests for FrameSequenceRule."""
    
    def test_complete_frame_sequence(self, create_test_directory_structure):
        """Test frame sequence validation with complete sequence."""
        structure = {
            "comp": {
                "shot_010_comp.1001.exr": "",
                "shot_010_comp.1002.exr": "",
                "shot_010_comp.1003.exr": "",
                "shot_010_comp.1004.exr": "",
                "shot_010_comp.1005.exr": ""
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "folder": "comp",
            "base": "shot_010_comp",
            "ext": ".exr",
            "start": 1001,
            "end": 1005,
            "padding": 4,
            "level": "error",
            "message": "Missing frames"
        }
        
        rule = FrameSequenceRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0
    
    def test_missing_frames_in_sequence(self, create_test_directory_structure):
        """Test frame sequence validation with missing frames."""
        structure = {
            "comp": {
                "shot_010_comp.1001.exr": "",
                "shot_010_comp.1002.exr": "",
                # Missing 1003
                "shot_010_comp.1004.exr": "",
                "shot_010_comp.1005.exr": ""
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "folder": "comp",
            "base": "shot_010_comp",
            "ext": ".exr",
            "start": 1001,
            "end": 1005,
            "padding": 4,
            "level": "error",
            "message": "Missing frames"
        }
        
        rule = FrameSequenceRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) > 0
        assert any("1003" in issue.message for issue in issues)
    
    def test_frame_sequence_with_variables(self, create_test_directory_structure):
        """Test frame sequence with variable substitution."""
        structure = {
            "seq_010": {
                "shot_020": {
                    "comp": {
                        "shot_020_comp.1001.exr": "",
                        "shot_020_comp.1002.exr": ""
                    }
                }
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "folder": "seq_{sequence}/shot_{shot}/comp",
            "base": "shot_{shot}_comp",
            "ext": ".exr",
            "start": 1001,
            "end": 1002,
            "padding": 4,
            "level": "error",
            "message": "Missing frames",
            "vars": {
                "sequence": "010",
                "shot": "020"
            }
        }
        
        rule = FrameSequenceRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0


@pytest.mark.unit
class TestMustExistRule:
    """Tests for MustExistRule."""
    
    def test_existing_files(self, create_test_directory_structure):
        """Test must_exist rule with existing files."""
        structure = {
            "seq_010": {
                "shot_010": {
                    "comp": None,
                    "plate": None
                }
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "glob": "seq_*/shot_*/comp",
            "level": "error",
            "message": "Required folder missing"
        }
        
        rule = MustExistRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0
    
    def test_missing_files(self, create_test_directory_structure):
        """Test must_exist rule with missing files."""
        structure = {
            "seq_010": {
                "shot_010": {
                    "comp": None
                    # Missing plate folder
                }
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "glob": "seq_*/shot_*/plate",
            "level": "error",
            "message": "Required folder missing"
        }
        
        rule = MustExistRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) > 0
        assert any("plate" in issue.message.lower() for issue in issues)
    
    def test_must_exist_with_file_pattern(self, create_test_directory_structure):
        """Test must_exist rule with file pattern."""
        structure = {
            "seq_010": {
                "shot_010": {
                    "shot_info.yaml": "metadata: test"
                }
            }
        }
        
        root = create_test_directory_structure(structure)
        
        rule_config = {
            "glob": "seq_*/shot_*/shot_info.yaml",
            "level": "warning",
            "message": "Metadata file missing"
        }
        
        rule = MustExistRule()
        issues = rule.check(root, rule_config)
        
        assert len(issues) == 0
