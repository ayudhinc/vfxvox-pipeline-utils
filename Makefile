.PHONY: help install install-dev test lint format type-check clean docs

help:
	@echo "VFXVox Pipeline Utils - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install package in development mode"
	@echo "  install-dev   - Install package with development dependencies"
	@echo "  test          - Run tests with coverage"
	@echo "  test-fast     - Run tests without coverage"
	@echo "  lint          - Run flake8 linter"
	@echo "  format        - Format code with black"
	@echo "  format-check  - Check code formatting without changes"
	@echo "  type-check    - Run mypy type checker"
	@echo "  quality       - Run all quality checks (lint, format-check, type-check)"
	@echo "  clean         - Remove build artifacts and cache files"
	@echo "  clean-test    - Remove test and coverage artifacts"
	@echo "  docs          - Build documentation"
	@echo "  examples      - Run example scripts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-fast:
	pytest --no-cov

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

lint:
	flake8 vfxvox_pipeline_utils tests

format:
	black vfxvox_pipeline_utils tests examples

format-check:
	black --check vfxvox_pipeline_utils tests examples

type-check:
	mypy vfxvox_pipeline_utils

quality: lint format-check type-check
	@echo "All quality checks passed!"

clean: clean-test
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .eggs/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete

clean-test:
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf *.cover

docs:
	@echo "Documentation build not yet configured"

examples:
	@echo "Running example scripts..."
	python examples/shotlint_example.py
	python examples/validate_sequence.py
