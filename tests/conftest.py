"""Shared pytest fixtures and configuration for VFXVox Pipeline Utils tests."""

import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests.
    
    Yields:
        Path to temporary directory
        
    Cleanup:
        Removes temporary directory after test
    """
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def fixtures_dir() -> Path:
    """Get path to test fixtures directory.
    
    Returns:
        Path to fixtures directory
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_project_dir(fixtures_dir: Path) -> Path:
    """Get path to sample VFX project fixture.
    
    Args:
        fixtures_dir: Path to fixtures directory
        
    Returns:
        Path to sample project directory
    """
    return fixtures_dir / "sample_project"


@pytest.fixture
def sample_sequence_dir(fixtures_dir: Path) -> Path:
    """Get path to sample sequence fixtures.
    
    Args:
        fixtures_dir: Path to fixtures directory
        
    Returns:
        Path to sequence fixtures directory
    """
    return fixtures_dir / "sequences"


@pytest.fixture
def sample_usd_dir(fixtures_dir: Path) -> Path:
    """Get path to sample USD fixtures.
    
    Args:
        fixtures_dir: Path to fixtures directory
        
    Returns:
        Path to USD fixtures directory
    """
    return fixtures_dir / "usd"


@pytest.fixture
def sample_rules_file(fixtures_dir: Path) -> Path:
    """Get path to sample shotlint rules file.
    
    Args:
        fixtures_dir: Path to fixtures directory
        
    Returns:
        Path to rules YAML file
    """
    return fixtures_dir / "shotlint_rules.yaml"


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration between tests.
    
    This fixture automatically runs for every test to ensure
    logging state doesn't leak between tests.
    """
    from vfxvox_pipeline_utils.core.logging import reset_logging
    
    yield
    
    # Reset after test
    reset_logging()


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing.
    
    Returns:
        Config object with test settings
    """
    from vfxvox_pipeline_utils.core.config import Config
    
    return Config.from_dict({
        "sequences": {
            "supported_formats": ["exr", "dpx", "png", "jpg"],
            "check_resolution": True,
            "check_bit_depth": True,
        },
        "usd": {
            "max_layer_depth": 10,
            "check_references": True,
            "check_schemas": True,
            "check_performance": True,
        },
        "shotlint": {
            "fail_on": "error",
        },
        "logging": {
            "level": "ERROR",  # Reduce noise in tests
        },
    })


@pytest.fixture
def create_test_sequence(temp_dir: Path):
    """Factory fixture to create test image sequences.
    
    Args:
        temp_dir: Temporary directory path
        
    Returns:
        Function to create test sequences
    """
    def _create_sequence(
        base_name: str,
        start_frame: int,
        end_frame: int,
        missing_frames: list = None,
        padding: int = 4
    ) -> Path:
        """Create a test image sequence.
        
        Args:
            base_name: Base name for sequence files
            start_frame: First frame number
            end_frame: Last frame number
            missing_frames: List of frame numbers to skip
            padding: Frame number padding
            
        Returns:
            Path to sequence directory
        """
        from PIL import Image
        
        seq_dir = temp_dir / "sequences"
        seq_dir.mkdir(parents=True, exist_ok=True)
        
        missing_frames = missing_frames or []
        
        for frame in range(start_frame, end_frame + 1):
            if frame in missing_frames:
                continue
                
            frame_str = str(frame).zfill(padding)
            frame_file = seq_dir / f"{base_name}.{frame_str}.png"
            
            # Create a simple test image
            img = Image.new('RGB', (1920, 1080), color=(frame % 255, 128, 200))
            img.save(frame_file)
        
        return seq_dir
    
    return _create_sequence


@pytest.fixture
def create_test_directory_structure(temp_dir: Path):
    """Factory fixture to create test directory structures.
    
    Args:
        temp_dir: Temporary directory path
        
    Returns:
        Function to create directory structures
    """
    def _create_structure(structure: dict, base_path: Path = None) -> Path:
        """Create a directory structure from a dictionary.
        
        Args:
            structure: Dictionary defining directory structure
                      Keys are directory/file names
                      Values are either:
                        - dict: subdirectory structure
                        - str: file content
                        - None: empty directory
            base_path: Base path for structure (uses temp_dir if None)
            
        Returns:
            Path to created structure root
        """
        if base_path is None:
            base_path = temp_dir
        
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # Create directory and recurse
                path.mkdir(parents=True, exist_ok=True)
                _create_structure(content, path)
            elif isinstance(content, str):
                # Create file with content
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            else:
                # Create empty directory
                path.mkdir(parents=True, exist_ok=True)
        
        return base_path
    
    return _create_structure


# Markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_usd: mark test as requiring USD Python bindings"
    )
    config.addinivalue_line(
        "markers", "requires_oiio: mark test as requiring OpenImageIO"
    )


# Skip tests based on optional dependencies
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle optional dependencies."""
    skip_usd = pytest.mark.skip(reason="USD Python bindings not available")
    skip_oiio = pytest.mark.skip(reason="OpenImageIO not available")
    
    # Check for optional dependencies
    try:
        import pxr
        has_usd = True
    except ImportError:
        has_usd = False
    
    try:
        import OpenImageIO
        has_oiio = True
    except ImportError:
        has_oiio = False
    
    # Apply skip markers
    for item in items:
        if "requires_usd" in item.keywords and not has_usd:
            item.add_marker(skip_usd)
        if "requires_oiio" in item.keywords and not has_oiio:
            item.add_marker(skip_oiio)
