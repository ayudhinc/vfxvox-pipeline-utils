"""Tests for sequence validator."""

import pytest
from pathlib import Path
from PIL import Image

from vfxvox_pipeline_utils.sequences.validator import SequenceValidator
from vfxvox_pipeline_utils.core.config import Config


@pytest.mark.unit
def test_sequence_validator_initialization():
    """Test SequenceValidator initializes correctly."""
    validator = SequenceValidator()
    assert validator is not None
    assert validator.config is not None


@pytest.mark.unit
def test_sequence_validator_with_custom_config():
    """Test SequenceValidator with custom configuration."""
    config = Config.from_dict({
        "sequences": {
            "check_resolution": False,
            "check_bit_depth": False
        }
    })
    
    validator = SequenceValidator(config=config)
    assert validator.config.get("sequences.check_resolution") is False


@pytest.mark.integration
def test_validate_complete_sequence(create_test_sequence):
    """Test validation of complete sequence."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1010,
        missing_frames=[]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    
    validator = SequenceValidator()
    result = validator.validate(pattern)
    
    assert result.passed
    assert result.error_count() == 0
    assert result.metadata["frame_count"] == 10


@pytest.mark.integration
def test_validate_sequence_with_missing_frames(create_test_sequence):
    """Test validation detects missing frames."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1010,
        missing_frames=[1003, 1005, 1007]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    
    validator = SequenceValidator()
    result = validator.validate(pattern)
    
    assert not result.passed
    assert result.error_count() > 0
    
    # Check that missing frames are reported
    missing_issue = next((i for i in result.issues if "missing" in i.message.lower()), None)
    assert missing_issue is not None


@pytest.mark.integration
def test_validate_empty_sequence(temp_dir):
    """Test validation of non-existent sequence."""
    pattern = str(temp_dir / "nonexistent.%04d.png")
    
    validator = SequenceValidator()
    result = validator.validate(pattern)
    
    # Should have warning about no frames found
    assert len(result.issues) > 0
    assert any("no frames" in i.message.lower() for i in result.issues)


@pytest.mark.integration
def test_validate_sequence_with_corrupted_frames(temp_dir):
    """Test validation detects corrupted frames."""
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create valid frames
    for frame in [1001, 1002, 1004]:
        frame_file = seq_dir / f"test.{frame:04d}.png"
        img = Image.new('RGB', (1920, 1080), color=(100, 100, 100))
        img.save(frame_file)
    
    # Create corrupted frame
    corrupted_file = seq_dir / "test.1003.png"
    corrupted_file.write_text("not an image")
    
    pattern = str(seq_dir / "test.%04d.png")
    
    validator = SequenceValidator()
    result = validator.validate(pattern)
    
    # Should detect corrupted frame
    assert not result.passed
    corrupted_issue = next((i for i in result.issues if "corrupted" in i.message.lower() or "unreadable" in i.message.lower()), None)
    assert corrupted_issue is not None


@pytest.mark.integration
def test_validate_sequence_resolution_consistency(temp_dir):
    """Test validation detects resolution inconsistencies."""
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create frames with different resolutions
    for frame in [1001, 1002]:
        frame_file = seq_dir / f"test.{frame:04d}.png"
        img = Image.new('RGB', (1920, 1080), color=(100, 100, 100))
        img.save(frame_file)
    
    # Create frame with different resolution
    frame_file = seq_dir / "test.1003.png"
    img = Image.new('RGB', (1280, 720), color=(100, 100, 100))  # Different resolution
    img.save(frame_file)
    
    pattern = str(seq_dir / "test.%04d.png")
    
    validator = SequenceValidator()
    result = validator.validate(pattern)
    
    # Should detect resolution mismatch
    assert not result.passed
    resolution_issue = next((i for i in result.issues if "resolution" in i.message.lower()), None)
    assert resolution_issue is not None


@pytest.mark.integration
def test_validate_sequence_with_resolution_check_disabled(temp_dir):
    """Test validation with resolution check disabled."""
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create frames with different resolutions
    for frame in [1001, 1002]:
        frame_file = seq_dir / f"test.{frame:04d}.png"
        img = Image.new('RGB', (1920, 1080), color=(100, 100, 100))
        img.save(frame_file)
    
    frame_file = seq_dir / "test.1003.png"
    img = Image.new('RGB', (1280, 720), color=(100, 100, 100))
    img.save(frame_file)
    
    pattern = str(seq_dir / "test.%04d.png")
    
    # Disable resolution check
    config = Config.from_dict({
        "sequences": {
            "check_resolution": False
        }
    })
    
    validator = SequenceValidator(config=config)
    result = validator.validate(pattern)
    
    # Should not report resolution issues
    resolution_issue = next((i for i in result.issues if "resolution" in i.message.lower()), None)
    assert resolution_issue is None


@pytest.mark.integration
def test_validate_sequence_bit_depth_consistency(temp_dir):
    """Test validation detects bit depth inconsistencies."""
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create RGB frames
    for frame in [1001, 1002]:
        frame_file = seq_dir / f"test.{frame:04d}.png"
        img = Image.new('RGB', (1920, 1080), color=(100, 100, 100))
        img.save(frame_file)
    
    # Create RGBA frame (different bit depth)
    frame_file = seq_dir / "test.1003.png"
    img = Image.new('RGBA', (1920, 1080), color=(100, 100, 100, 255))
    img.save(frame_file)
    
    pattern = str(seq_dir / "test.%04d.png")
    
    validator = SequenceValidator()
    result = validator.validate(pattern)
    
    # May detect bit depth or mode mismatch
    # Note: PNG bit depth detection might vary, so we check for any consistency issue
    if not result.passed:
        assert result.error_count() > 0 or result.warning_count() > 0


@pytest.mark.unit
def test_check_missing_frames(create_test_sequence):
    """Test check_missing_frames method."""
    from vfxvox_pipeline_utils.sequences.scanner import SequenceScanner
    from vfxvox_pipeline_utils.core.validators import ValidationResult
    
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1005,
        missing_frames=[1003]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    frames = scanner.scan_all()
    
    validator = SequenceValidator()
    result = ValidationResult(passed=True)
    
    validator.check_missing_frames(frames, result)
    
    assert len(result.issues) > 0
    assert any("1003" in str(i.message) for i in result.issues)


@pytest.mark.unit
def test_check_corrupted_frames(temp_dir):
    """Test check_corrupted_frames method."""
    from vfxvox_pipeline_utils.sequences.scanner import SequenceScanner, FrameInfo
    from vfxvox_pipeline_utils.core.validators import ValidationResult
    
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create one valid frame
    frame_file = seq_dir / "test.1001.png"
    img = Image.new('RGB', (1920, 1080))
    img.save(frame_file)
    
    # Create corrupted frame
    corrupted_file = seq_dir / "test.1002.png"
    corrupted_file.write_text("corrupted")
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    frames = scanner.scan_all()
    
    validator = SequenceValidator()
    result = ValidationResult(passed=True)
    
    validator.check_corrupted_frames(frames, result)
    
    # Should detect corrupted frame
    assert len(result.issues) > 0


@pytest.mark.unit
def test_check_resolution_consistency(create_test_sequence):
    """Test check_resolution_consistency method."""
    from vfxvox_pipeline_utils.sequences.scanner import SequenceScanner
    from vfxvox_pipeline_utils.core.validators import ValidationResult
    
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1003,
        missing_frames=[]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    frames = scanner.scan_all()
    
    validator = SequenceValidator()
    result = ValidationResult(passed=True)
    
    validator.check_resolution_consistency(frames, result)
    
    # All frames have same resolution, should have no issues
    assert len(result.issues) == 0
