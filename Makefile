# Developer convenience targets for agent-quality-inspect.
# These wrap the same commands CI runs (see .github/workflows/run-unit-tests.yaml)
# so local checks match the pipeline. Run `make help` for the full list.

PYTHON ?= python
PACKAGE := agent_inspect
SRC := src tests

.DEFAULT_GOAL := help

.PHONY: help install install-dev lint format format-check test test-cov check clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in editable mode
	$(PYTHON) -m pip install -e .

install-dev: ## Install the package plus test and dev dependencies
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install -r requirements_test.txt -r requirements_dev.txt

lint: ## Run the ruff linter (matches CI)
	ruff check $(SRC)

format: ## Auto-format the code with ruff
	ruff format $(SRC)

format-check: ## Verify formatting without modifying files (matches CI)
	ruff format --check $(SRC)

test: ## Run the unit test suite
	$(PYTHON) -m pytest

test-cov: ## Run the unit test suite with coverage reporting
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=term-missing

check: lint format-check test ## Run lint, format check, and tests (pre-push gate)

clean: ## Remove build artifacts and caches
	rm -rf build dist *.egg-info src/*.egg-info .coverage coverage.xml htmlcov .pytest_cache
	find . -type d -name __pycache__ -not -path './agent_runners/*' -exec rm -rf {} +
