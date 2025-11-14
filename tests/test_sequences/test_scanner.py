"""Tests for sequence scanner."""

import pytest
from pathlib import Path
from PIL import Image

from vfxvox_pipeline_utils.sequences.scanner import SequenceScanner, FrameInfo


@pytest.mark.unit
def test_scanner_initialization_printf_style():
    """Test scanner initialization with printf-style pattern."""
    scanner = SequenceScanner("shot_010.%04d.exr")
    assert scanner is not None


@pytest.mark.unit
def test_scanner_initialization_hash_style():
    """Test scanner initialization with hash-style pattern."""
    scanner = SequenceScanner("shot_010.####.exr")
    assert scanner is not None


@pytest.mark.unit
def test_scanner_initialization_range_style():
    """Test scanner initialization with range-style pattern."""
    scanner = SequenceScanner("shot_010.[1001-1100].exr")
    assert scanner is not None


@pytest.mark.integration
def test_detect_frames_printf_style(create_test_sequence):
    """Test frame detection with printf-style pattern."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1005,
        missing_frames=[]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frames = scanner.detect_frames()
    
    assert len(frames) == 5
    assert 1001 in frames
    assert 1005 in frames


@pytest.mark.integration
def test_detect_frames_with_gaps(create_test_sequence):
    """Test frame detection with missing frames."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1010,
        missing_frames=[1003, 1007]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frames = scanner.detect_frames()
    
    assert len(frames) == 8  # 10 - 2 missing
    assert 1003 not in frames
    assert 1007 not in frames


@pytest.mark.integration
def test_get_frame_range(create_test_sequence):
    """Test getting frame range."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1010,
        missing_frames=[1005]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frame_range = scanner.get_frame_range()
    
    assert frame_range is not None
    assert frame_range[0] == 1001
    assert frame_range[1] == 1010


@pytest.mark.integration
def test_scan_single_frame(create_test_sequence):
    """Test scanning a single frame."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1001,
        missing_frames=[]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frame_info = scanner.scan_frame(1001)
    
    assert frame_info is not None
    assert frame_info.frame_number == 1001
    assert frame_info.exists
    assert frame_info.readable
    assert frame_info.resolution is not None


@pytest.mark.integration
def test_scan_nonexistent_frame(temp_dir):
    """Test scanning a frame that doesn't exist."""
    pattern = str(temp_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frame_info = scanner.scan_frame(1001)
    
    assert frame_info is not None
    assert frame_info.frame_number == 1001
    assert not frame_info.exists


@pytest.mark.integration
def test_scan_all_frames(create_test_sequence):
    """Test scanning all frames in sequence."""
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1005,
        missing_frames=[]
    )
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frames = scanner.scan_all()
    
    assert len(frames) == 5
    assert all(f.exists for f in frames)
    assert all(f.readable for f in frames)
    assert all(f.resolution == (1920, 1080) for f in frames)


@pytest.mark.integration
def test_scan_corrupted_frame(temp_dir):
    """Test scanning a corrupted frame."""
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create corrupted file
    frame_file = seq_dir / "test.1001.png"
    frame_file.write_text("not an image")
    
    pattern = str(seq_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frame_info = scanner.scan_frame(1001)
    
    assert frame_info.exists
    assert not frame_info.readable


@pytest.mark.unit
def test_frame_info_dataclass():
    """Test FrameInfo dataclass."""
    frame_info = FrameInfo(
        frame_number=1001,
        file_path=Path("/test/frame.1001.exr"),
        exists=True,
        readable=True,
        resolution=(1920, 1080),
        bit_depth=16,
        format="EXR"
    )
    
    assert frame_info.frame_number == 1001
    assert frame_info.resolution == (1920, 1080)
    assert frame_info.bit_depth == 16


@pytest.mark.integration
def test_detect_frames_empty_directory(temp_dir):
    """Test frame detection in empty directory."""
    pattern = str(temp_dir / "test.%04d.png")
    scanner = SequenceScanner(pattern)
    
    frames = scanner.detect_frames()
    
    assert len(frames) == 0


@pytest.mark.integration
def test_scan_sequence_with_different_padding(temp_dir):
    """Test scanning sequence with different frame padding."""
    seq_dir = temp_dir / "sequences"
    seq_dir.mkdir()
    
    # Create frames with 3-digit padding
    for frame in [101, 102, 103]:
        frame_file = seq_dir / f"test.{frame:03d}.png"
        img = Image.new('RGB', (1920, 1080))
        img.save(frame_file)
    
    pattern = str(seq_dir / "test.%03d.png")
    scanner = SequenceScanner(pattern)
    
    frames = scanner.detect_frames()
    
    assert len(frames) == 3
    assert 101 in frames
    assert 103 in frames
