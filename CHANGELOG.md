# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-13

### Added

#### Core Infrastructure
- Base validator classes and data models for validation results
- Configuration management with YAML support and config merging
- Logging utilities with configurable levels and output
- Custom exception classes with context information
- Type-safe validation result handling

#### ShotLint Module
- Directory structure validation against declarative YAML rules
- Path pattern validation with variable substitution
- Filename regex validation
- Frame sequence validation with missing frame detection
- File/folder existence checks using glob patterns
- Plugin system for custom validation logic
- Multiple output formats (console, JSON, YAML, Markdown)

#### Sequence Validator Module
- Image sequence validation for missing frames
- Corrupted frame detection
- Resolution consistency checking
- Bit depth consistency checking
- Support for multiple pattern styles (printf, hash, range)
- Format handlers for EXR, DPX, PNG, JPG, TIFF
- Extensible format handler system

#### USD Linter Module
- USD file validation and linting
- Built-in rules for broken references, invalid schemas, performance issues
- Custom rule system with YAML configuration
- Naming convention validation
- Required metadata validation
- Performance analysis (layer depth, composition complexity)
- Multiple output formats (console, JSON, YAML, Markdown)

#### CLI Interface
- `vfxvox` command-line tool with three main commands:
  - `shotlint`: Validate directory structures
  - `validate-sequence`: Validate image sequences
  - `lint-usd`: Lint USD files
- Global options for configuration and logging
- Branded ASCII logo display
- Consistent output formatting across all commands
- Proper exit codes for CI/CD integration

#### Documentation and Examples
- Comprehensive API documentation with Google-style docstrings
- Example scripts for all three modules
- Studio rules template for ShotLint
- Pipeline integration examples
- Testing documentation and fixtures

#### Development Tools
- Code quality tools configuration (flake8, black, mypy)
- Pytest configuration with coverage reporting
- Tox configuration for multi-version testing
- Makefile for convenient development commands
- Shared pytest fixtures for testing
- Python version compatibility testing

### Technical Details

- **Python Support**: Python 3.8, 3.9, 3.10, 3.11
- **Core Dependencies**: click, PyYAML, Pillow
- **Optional Dependencies**: usd-core (USD support), OpenImageIO (advanced image formats)
- **License**: MIT
- **Package Structure**: Modular design with independent subpackages

### Installation

```bash
# Basic installation
pip install vfxvox-pipeline-utils

# With USD support
pip install vfxvox-pipeline-utils[usd]

# With all optional dependencies
pip install vfxvox-pipeline-utils[all]

# Development installation
pip install -e ".[dev]"
```

### Usage Examples

```bash
# Validate directory structure
vfxvox shotlint ./project --rules rules.yaml

# Validate image sequence
vfxvox validate-sequence "shot_010.%04d.exr"

# Lint USD file
vfxvox lint-usd asset.usd --config custom_rules.yaml
```

### Known Limitations

- USD linting requires optional `usd-core` package
- Advanced image format support (EXR, DPX) requires optional `OpenImageIO` package
- Test coverage is not yet at 80% target (unit tests marked as optional in implementation plan)

### Contributors

- VFXVox Contributors

---

## [Unreleased]

### Planned Features

- Additional validation modules (color pipeline, metadata, Alembic)
- Enhanced USD linting rules
- Performance optimizations for large sequences
- Parallel processing support
- Web-based reporting interface
- Integration with production tracking systems

---

[0.1.0]: https://github.com/vfxvox/pipeline-utils/releases/tag/v0.1.0
[Unreleased]: https://github.com/vfxvox/pipeline-utils/compare/v0.1.0...HEAD
