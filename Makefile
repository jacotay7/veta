# Makefile for VETA development and testing

.PHONY: help install test test-unit test-integration test-slow test-coverage clean lint format docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install        Install dependencies"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-slow     Run slow tests only"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run code linting"
	@echo "  format        Format code with black"
	@echo "  clean         Clean up generated files"
	@echo "  docs          Generate documentation"

# Install dependencies
install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm || echo "Could not download English model"
	python -m spacy download de_core_news_sm || echo "Could not download German model"

# Run all tests
test:
	python run_tests.py

# Run unit tests only (fast)
test-unit:
	pytest tests/ -v -m "not integration and not slow"

# Run integration tests only
test-integration:
	pytest tests/ -v -m "integration"

# Run slow tests only
test-slow:
	pytest tests/ -v -m "slow"

# Run tests with detailed coverage report
test-coverage:
	pytest tests/ --cov=veta --cov-report=html --cov-report=term-missing --cov-branch
	@echo "Coverage report generated in htmlcov/index.html"

# Run specific test file
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make test-file FILE=test_filename.py"; \
	else \
		pytest tests/$(FILE) -v; \
	fi

# Run linting
lint:
	flake8 veta tests --max-line-length=127
	@echo "Linting complete"

# Format code
format:
	black veta tests
	isort veta tests
	@echo "Code formatting complete"

# Type checking
typecheck:
	mypy veta --ignore-missing-imports
	@echo "Type checking complete"

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Cleanup complete"

# Generate documentation
docs:
	@if command -v sphinx-build >/dev/null; then \
		sphinx-build -b html docs/ docs/_build/html; \
		echo "Documentation generated in docs/_build/html/"; \
	else \
		echo "Sphinx not installed. Install with: pip install sphinx sphinx-rtd-theme"; \
	fi

# Run pre-commit checks
pre-commit:
	@echo "Running pre-commit checks..."
	make lint
	make typecheck
	make test-unit
	@echo "Pre-commit checks passed!"

# Install development tools
dev-install:
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install
	@echo "Development environment setup complete"

# Run performance benchmarks
benchmark:
	@if pip list | grep pytest-benchmark >/dev/null; then \
		pytest tests/ --benchmark-only; \
	else \
		echo "pytest-benchmark not installed. Install with: pip install pytest-benchmark"; \
	fi

# Security audit
security:
	@echo "Running security audit..."
	@if pip list | grep bandit >/dev/null; then \
		bandit -r veta/; \
	else \
		echo "bandit not installed. Install with: pip install bandit"; \
	fi
	@if pip list | grep safety >/dev/null; then \
		safety check; \
	else \
		echo "safety not installed. Install with: pip install safety"; \
	fi

# Package building
build:
	python setup.py sdist bdist_wheel
	@echo "Package built in dist/"

# Upload to PyPI (test)
upload-test:
	twine upload --repository testpypi dist/*

# Upload to PyPI
upload:
	twine upload dist/*

# Run all quality checks
qa: lint typecheck test-coverage security
	@echo "All quality checks completed"
