# Contributing to VFXVox Pipeline Utils

Thank you for your interest in contributing to VFXVox Pipeline Utils! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayudhinc/vfxvox-pipeline-utils.git
   cd vfxvox-pipeline-utils
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .[dev]
   ```

4. **Run tests to verify setup:**
   ```bash
   pytest
   ```

## Development Workflow

### Code Style

We follow PEP 8 style guidelines with some modifications:

- **Line length:** 100 characters maximum
- **Formatting:** Use `black` for automatic code formatting
- **Linting:** Use `flake8` for code quality checks
- **Type hints:** Use type hints for all public APIs

**Format your code before committing:**
```bash
black vfxvox_pipeline_utils tests
flake8 vfxvox_pipeline_utils tests
mypy vfxvox_pipeline_utils
```

### Testing

- Write unit tests for all new functionality
- Aim for at least 80% code coverage
- Tests should be fast and isolated
- Use fixtures for test data

**Run tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vfxvox_pipeline_utils --cov-report=html

# Run specific test file
pytest tests/test_sequences/test_validator.py
```

### Commit Messages

Write clear, descriptive commit messages:

```
Add frame sequence validation for EXR files

- Implement FrameInfo dataclass for frame metadata
- Add EXRHandler for reading EXR metadata
- Include tests for missing frame detection
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description with bullet points if needed

## Contributing Code

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   pytest
   black vfxvox_pipeline_utils tests
   flake8 vfxvox_pipeline_utils tests
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   - Go to the GitHub repository
   - Click "New Pull Request"
   - Provide a clear description of your changes
   - Reference any related issues

### Pull Request Guidelines

- **One feature per PR:** Keep pull requests focused on a single feature or fix
- **Tests required:** All PRs must include tests
- **Documentation:** Update docs if you change APIs or add features
- **Code review:** Be responsive to feedback and questions
- **CI must pass:** All automated checks must pass before merging

## Adding New Modules

To add a new validation module:

1. **Create module structure:**
   ```
   vfxvox_pipeline_utils/
   └── your_module/
       ├── __init__.py
       ├── validator.py
       ├── rules.py
       └── reporters.py
   ```

2. **Extend BaseValidator:**
   ```python
   from vfxvox_pipeline_utils.core.validators import BaseValidator
   
   class YourValidator(BaseValidator):
       def validate(self, target):
           # Implementation
           pass
   ```

3. **Add CLI command:**
   - Create `cli/your_module_cmd.py`
   - Register command in `cli/main.py`

4. **Add tests:**
   - Create `tests/test_your_module/`
   - Add test fixtures and unit tests

5. **Update documentation:**
   - Add module to README.md
   - Create usage examples
   - Update API documentation

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- **Description:** Clear description of the issue
- **Steps to reproduce:** Minimal steps to reproduce the problem
- **Expected behavior:** What you expected to happen
- **Actual behavior:** What actually happened
- **Environment:** Python version, OS, package version
- **Code sample:** Minimal code that demonstrates the issue

### Feature Requests

When requesting features, include:

- **Use case:** Describe the problem you're trying to solve
- **Proposed solution:** How you envision the feature working
- **Alternatives:** Other approaches you've considered
- **Examples:** Code examples of how it would be used

## Documentation

- **Docstrings:** Use Google-style docstrings for all public APIs
- **Type hints:** Include type hints in function signatures
- **Examples:** Provide usage examples in docstrings
- **README:** Update README.md for user-facing changes

**Docstring example:**
```python
def validate_sequence(pattern: str, start: int, end: int) -> ValidationResult:
    """Validate an image sequence for missing frames.
    
    Args:
        pattern: File pattern (e.g., "shot_010.%04d.exr")
        start: First frame number
        end: Last frame number
        
    Returns:
        ValidationResult with issues found
        
    Example:
        >>> validator = SequenceValidator()
        >>> result = validator.validate("shot.%04d.exr", 1001, 1100)
        >>> if result.has_errors():
        ...     print(result.issues)
    """
```

## Questions?

- **GitHub Discussions:** For general questions and discussions
- **GitHub Issues:** For bug reports and feature requests
- **Email:** pipeline-utils@vfxvox.org for private inquiries

## License

By contributing to VFXVox Pipeline Utils, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to VFXVox Pipeline Utils! 🎬
