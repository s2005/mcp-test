# Makefile for MCP Test Python Project
# Provides convenient commands for development workflow

.PHONY: help install test lint fix-lint clean coverage format check-format type-check all

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  test        - Run tests"
	@echo "  coverage    - Run tests with coverage"
	@echo "  lint        - Run all linting checks"
	@echo "  fix-lint    - Automatically fix linting issues"
	@echo "  format      - Format code with black"
	@echo "  check-format- Check code formatting"
	@echo "  type-check  - Run type checking with mypy"
	@echo "  clean       - Clean up generated files"
	@echo "  all         - Run install-dev, fix-lint, test"

# Installation targets
install:
	uv sync

install-dev:
	uv sync --group dev

# Testing targets
test:
	uv run pytest

coverage:
	uv run pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term

# Linting and formatting targets
lint:
	@chmod +x scripts/lint.sh
	@./scripts/lint.sh

fix-lint:
	@chmod +x scripts/fix-lint.sh
	@./scripts/fix-lint.sh

format:
	uv run black src/ tests/

check-format:
	uv run black --check --diff src/ tests/

type-check:
	uv run mypy src/ --ignore-missing-imports --no-strict-optional

# Quality checks
flake8:
	uv run flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

isort:
	uv run isort src/ tests/

check-isort:
	uv run isort --check-only --diff src/ tests/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# Combined workflows
all: install-dev fix-lint test

# CI/CD friendly target
ci: install-dev lint test coverage

# Development setup
setup: install-dev
	@echo "Development environment is ready!"
	@echo "Run 'make help' to see available commands."

# Pre-commit style checks
pre-commit: fix-lint test
	@echo "Pre-commit checks completed successfully!"
