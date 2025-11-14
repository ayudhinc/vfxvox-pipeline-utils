# VFXVox Pipeline Utils - Test Suite

This directory contains the test suite for VFXVox Pipeline Utils.

## Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── fixtures/                # Test data and fixtures
│   ├── sample_project/      # Sample VFX project structure
│   ├── sequences/           # Sample image sequences
│   ├── usd/                 # Sample USD files
│   └── shotlint_rules.yaml  # Sample validation rules
├── test_shotlint/           # ShotLint module tests
├── test_sequences/          # Sequence validator tests
└── test_usd/                # USD linter tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=vfxvox_pipeline_utils --cov-report=html
```

### Run specific test modules
```bash
pytest tests/test_sequences/
pytest tests/test_shotlint/
pytest tests/test_usd/
```

### Run by marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with different verbosity
```bash
# Verbose output
pytest -v

# Very verbose output
pytest -vv

# Quiet output
pytest -q
```

## Test Markers

Tests can be marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, may require external resources)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_usd` - Tests requiring USD Python bindings
- `@pytest.mark.requires_oiio` - Tests requiring OpenImageIO

## Fixtures

### Directory Fixtures

- `temp_dir` - Temporary directory for test files
- `fixtures_dir` - Path to test fixtures directory
- `sample_project_dir` - Sample VFX project structure
- `sample_sequence_dir` - Sample image sequences
- `sample_usd_dir` - Sample USD files

### Configuration Fixtures

- `mock_config` - Mock configuration for testing
- `reset_logging` - Automatically resets logging between tests

### Factory Fixtures

- `create_test_sequence` - Create test image sequences
- `create_test_directory_structure` - Create test directory structures

## Writing Tests

### Example Unit Test

```python
import pytest
from vfxvox_pipeline_utils.sequences.validator import SequenceValidator

@pytest.mark.unit
def test_sequence_validator_initialization():
    """Test that SequenceValidator initializes correctly."""
    validator = SequenceValidator()
    assert validator is not None
```

### Example Integration Test

```python
import pytest
from pathlib import Path

@pytest.mark.integration
def test_validate_complete_sequence(create_test_sequence):
    """Test validation of a complete sequence."""
    # Create test sequence
    seq_dir = create_test_sequence(
        base_name="test",
        start_frame=1001,
        end_frame=1100
    )
    
    # Validate
    validator = SequenceValidator()
    pattern = str(seq_dir / "test.%04d.png")
    result = validator.validate(pattern)
    
    assert result.passed
    assert result.error_count() == 0
```

### Example Test with Fixtures

```python
@pytest.mark.unit
def test_with_temp_directory(temp_dir):
    """Test using temporary directory."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    
    assert test_file.exists()
    assert test_file.read_text() == "test content"
```

## Coverage

The test suite aims for at least 80% code coverage. To generate a coverage report:

```bash
pytest --cov=vfxvox_pipeline_utils --cov-report=html
```

Then open `htmlcov/index.html` in a browser to view the report.

## Continuous Integration

Tests are automatically run on:
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Different operating systems (Linux, macOS, Windows)
- With and without optional dependencies (USD, OpenImageIO)

See `.github/workflows/tests.yml` for CI configuration.

## Test Data

Test fixtures are located in the `fixtures/` directory. These include:

- Sample VFX project structures
- Image sequences (complete, missing frames, corrupted)
- USD files (valid, broken references, invalid schemas)
- Configuration files

## Adding New Tests

When adding new tests:

1. Place tests in the appropriate module directory
2. Use descriptive test names starting with `test_`
3. Add appropriate markers (`@pytest.mark.unit`, etc.)
4. Use fixtures for common setup
5. Keep tests focused and independent
6. Add docstrings explaining what is being tested

## Troubleshooting

### Tests fail with import errors

Make sure the package is installed in development mode:
```bash
pip install -e ".[dev]"
```

### Tests fail with missing dependencies

Install optional dependencies:
```bash
pip install -e ".[all,dev]"
```

### Coverage report not generated

Install coverage tools:
```bash
pip install pytest-cov
```
