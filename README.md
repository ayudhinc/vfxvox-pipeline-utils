# VFXVox Pipeline Utils

> Open source toolkit for VFX production pipelines

VFXVox Pipeline Utils is a collection of Python-based utilities designed to solve common pain points in VFX production workflows. Built by artists and TDs for the community, this toolkit provides essential validation, linting, and automation tools that integrate seamlessly into existing pipelines.

## 🎯 Vision

Modern VFX pipelines involve complex workflows with multiple file formats, production tracking systems, and quality requirements. VFXVox Pipeline Utils aims to provide a unified, well-tested, and easy-to-use toolkit that addresses the most common challenges faced by studios of all sizes.

## 🛠️ Planned Tools

### 1. USD Asset Validator & Linter ✨

A comprehensive validation and linting tool for Universal Scene Description (USD) files.

**Features:**
- Validates USD file structure and schema definitions
- Detects broken or missing references to external assets
- Identifies performance issues (excessive layer depth, large arrays, complex composition)
- Supports custom linting rules for studio-specific conventions
- Configurable severity levels (error, warning, info)
- Both CLI and Python API

**Use Cases:**
- Pre-publish validation in asset pipelines
- CI/CD integration for automated quality checks
- Studio-wide USD standard enforcement
- Performance optimization analysis

### 2. Sequence Frame Validator ⭐

A fast and reliable tool for validating image sequences before rendering or compositing.

**Features:**
- Detects missing frames in sequences
- Identifies corrupted or unreadable files
- Validates resolution consistency across frames
- Checks bit depth uniformity
- Supports multiple formats (EXR, DPX, PNG, JPG, TIFF)
- Flexible pattern matching (printf-style, hash-style, range-style)
- JSON/YAML output for pipeline integration

**Use Cases:**
- Pre-comp validation to catch delivery issues early
- Render farm output verification
- Automated QC in pipeline hooks
- Shot delivery validation

### 3. Color Pipeline Utilities

A toolkit for managing OpenColorIO (OCIO) configurations and color workflows.

**Features:**
- Validates OCIO configuration files
- Tests color space conversions for accuracy
- Validates LUT files and transformations
- Generates common OCIO configs from templates
- Web-based visualizer for comparing color transforms
- Batch conversion utilities

**Use Cases:**
- OCIO config validation before deployment
- Color space migration verification
- LUT quality assurance
- Studio color pipeline setup

### 4. VFX Metadata Standardizer

A tool for normalizing and enriching metadata across VFX file formats.

**Features:**
- Reads and writes metadata for EXR, DPX, MOV, and other formats
- Enforces studio-specific metadata standards
- Batch metadata operations
- Template-based metadata injection
- Validates required fields (shot info, color space, frame rate)
- Preserves existing metadata while adding new fields

**Use Cases:**
- Shot metadata enforcement across departments
- Color space tagging automation
- Production tracking integration
- Delivery specification compliance

### 5. Alembic Diff & Merge Tool

A utility for comparing and analyzing Alembic cache files.

**Features:**
- Compares two Alembic files and identifies differences
- Detects geometric changes (vertex positions, topology)
- Identifies added/removed objects in hierarchy
- Analyzes animation differences
- Simple 3D viewer for visual comparison
- Generates diff reports in multiple formats

**Use Cases:**
- Version control for geometry caches
- QA validation between cache iterations
- Understanding what changed in updated assets
- Merge conflict resolution for cache files

### 6. Shotgrid/Ftrack Webhook Relay ⭐

A lightweight middleware service for production tracking automation.

**Features:**
- Listens to webhooks from Shotgrid, Ftrack, and other tracking systems
- Triggers custom pipeline actions based on events
- Auto-creates folder structures when shots/assets are created
- Syncs status changes to Slack, Discord, or other services
- Triggers automated tasks (transcoding, thumbnail generation, etc.)
- Updates downstream systems automatically
- Simple YAML-based configuration

**Use Cases:**
- Automated folder structure creation
- Cross-system status synchronization
- Pipeline event automation
- Notification routing
- Small studio automation without custom integrations

## 🚀 Getting Started

### Installation

```bash
# Install the complete toolkit
pip install vfxvox-pipeline-utils[all]

# Or install specific modules
pip install vfxvox-pipeline-utils[usd]      # USD tools only
pip install vfxvox-pipeline-utils[sequences] # Sequence validator only
```

### Quick Examples

**Validate an image sequence:**
```bash
vfxvox validate-sequence shot_010.%04d.exr
```

**Lint a USD file:**
```bash
vfxvox lint-usd /path/to/asset.usd --config studio_rules.yaml
```

**Python API usage:**
```python
from vfxvox_pipeline_utils.sequences import SequenceValidator

validator = SequenceValidator()
result = validator.validate("shot_010.%04d.exr")

if result.has_errors():
    for issue in result.issues:
        print(f"{issue.severity}: {issue.message}")
```

## 📦 Current Status

**Phase 1 (In Development):**
- ✅ Sequence Frame Validator
- ✅ USD Asset Validator & Linter
- 🚧 Core infrastructure and CLI

**Phase 2 (Planned):**
- Color Pipeline Utilities
- VFX Metadata Standardizer

**Phase 3 (Planned):**
- Alembic Diff & Merge Tool
- Shotgrid/Ftrack Webhook Relay

## 🤝 Contributing

We welcome contributions from the VFX community! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

**Ways to contribute:**
- Report bugs and request features via GitHub Issues
- Submit pull requests for bug fixes or new features
- Improve documentation and examples
- Share your use cases and feedback

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📋 Requirements

- Python 3.8 or higher
- Optional dependencies based on modules used:
  - USD Python bindings (for USD tools)
  - OpenImageIO (for advanced image format support)
  - OpenColorIO (for color pipeline tools)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Acknowledgments

Built with support from the VFX open source community. Special thanks to:
- The USD working group at Pixar
- The OpenImageIO and OCIO teams
- Studios and artists who provided feedback and use cases

## 📞 Contact

- GitHub Issues: [Report bugs or request features](https://github.com/vfxvox/pipeline-utils/issues)
- Discussions: [Join the conversation](https://github.com/vfxvox/pipeline-utils/discussions)
- Email: pipeline-utils@vfxvox.org

---

**Note:** This is an active open source project. Tools are being developed incrementally with community input. Star the repo to follow progress and get notified of releases!
