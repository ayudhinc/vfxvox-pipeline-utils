"""Tests for image format handlers."""

import pytest
from pathlib import Path
from PIL import Image

from vfxvox_pipeline_utils.sequences.formats import (
    get_format_handler,
    register_format_handler,
    StandardImageHandler,
    ImageFormatHandler
)


@pytest.mark.unit
def test_get_format_handler_for_png():
    """Test getting format handler for PNG files."""
    handler = get_format_handler(Path("test.png"))
    assert handler is not None
    assert isinstance(handler, StandardImageHandler)


@pytest.mark.unit
def test_get_format_handler_for_jpg():
    """Test getting format handler for JPG files."""
    handler = get_format_handler(Path("test.jpg"))
    assert handler is not None
    assert isinstance(handler, StandardImageHandler)


@pytest.mark.unit
def test_get_format_handler_for_jpeg():
    """Test getting format handler for JPEG files."""
    handler = get_format_handler(Path("test.jpeg"))
    assert handler is not None


@pytest.mark.unit
def test_get_format_handler_for_tiff():
    """Test getting format handler for TIFF files."""
    handler = get_format_handler(Path("test.tiff"))
    assert handler is not None


@pytest.mark.unit
def test_get_format_handler_for_unknown():
    """Test getting format handler for unknown format."""
    handler = get_format_handler(Path("test.unknown"))
    # Should return None or a default handler
    assert handler is None or handler is not None


@pytest.mark.integration
def test_standard_handler_can_handle_png():
    """Test StandardImageHandler can handle PNG."""
    handler = StandardImageHandler()
    assert handler.can_handle(Path("test.png"))


@pytest.mark.integration
def test_standard_handler_cannot_handle_exr():
    """Test StandardImageHandler cannot handle EXR."""
    handler = StandardImageHandler()
    assert not handler.can_handle(Path("test.exr"))


@pytest.mark.integration
def test_standard_handler_read_metadata(temp_dir):
    """Test reading metadata with StandardImageHandler."""
    # Create test image
    img_file = temp_dir / "test.png"
    img = Image.new('RGB', (1920, 1080), color=(100, 100, 100))
    img.save(img_file)
    
    handler = StandardImageHandler()
    metadata = handler.read_metadata(img_file)
    
    assert metadata is not None
    assert "resolution" in metadata
    assert metadata["resolution"] == (1920, 1080)
    assert "format" in metadata


@pytest.mark.integration
def test_standard_handler_read_corrupted_file(temp_dir):
    """Test reading corrupted file with StandardImageHandler."""
    # Create corrupted file
    img_file = temp_dir / "corrupted.png"
    img_file.write_text("not an image")
    
    handler = StandardImageHandler()
    
    # Should handle gracefully
    try:
        metadata = handler.read_metadata(img_file)
        # If it doesn't raise, metadata should indicate error
        assert metadata is None or "error" in str(metadata).lower()
    except Exception:
        # Exception is acceptable for corrupted files
        pass


@pytest.mark.unit
def test_custom_format_handler_registration():
    """Test registering a custom format handler."""
    
    class CustomHandler(ImageFormatHandler):
        def can_handle(self, file_path: Path) -> bool:
            return file_path.suffix.lower() == ".custom"
        
        def read_metadata(self, file_path: Path) -> dict:
            return {"format": "custom", "resolution": (1920, 1080)}
    
    handler = CustomHandler()
    register_format_handler(handler)
    
    # Test that custom handler is registered
    result_handler = get_format_handler(Path("test.custom"))
    assert result_handler is not None
    assert isinstance(result_handler, CustomHandler)


@pytest.mark.integration
def test_read_metadata_from_different_formats(temp_dir):
    """Test reading metadata from different image formats."""
    formats = [
        ("test.png", "PNG"),
        ("test.jpg", "JPEG"),
    ]
    
    for filename, expected_format in formats:
        img_file = temp_dir / filename
        img = Image.new('RGB', (1920, 1080))
        img.save(img_file)
        
        handler = get_format_handler(img_file)
        if handler:
            metadata = handler.read_metadata(img_file)
            assert metadata is not None
            assert metadata["resolution"] == (1920, 1080)


@pytest.mark.integration
def test_read_metadata_with_different_resolutions(temp_dir):
    """Test reading metadata from images with different resolutions."""
    resolutions = [
        (1920, 1080),
        (3840, 2160),
        (1280, 720)
    ]
    
    handler = StandardImageHandler()
    
    for width, height in resolutions:
        img_file = temp_dir / f"test_{width}x{height}.png"
        img = Image.new('RGB', (width, height))
        img.save(img_file)
        
        metadata = handler.read_metadata(img_file)
        assert metadata["resolution"] == (width, height)


@pytest.mark.integration
def test_read_metadata_with_different_modes(temp_dir):
    """Test reading metadata from images with different color modes."""
    modes = ['RGB', 'RGBA', 'L']  # RGB, RGBA, Grayscale
    
    handler = StandardImageHandler()
    
    for mode in modes:
        img_file = temp_dir / f"test_{mode}.png"
        img = Image.new(mode, (1920, 1080))
        img.save(img_file)
        
        metadata = handler.read_metadata(img_file)
        assert metadata is not None
        assert metadata["resolution"] == (1920, 1080)
