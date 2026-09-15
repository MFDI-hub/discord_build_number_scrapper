# Makefile for easy development workflows.
# See docs/development.md for docs.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

.PHONY: default install lint test docs docs-build upgrade build clean pre-commit sync sync-once

default: install lint test 

install:
	uv sync --all-extras
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg

lint:
	uv run python devtools/lint.py

test:
	uv run pytest -n auto --cov --cov-report=term-missing

docs:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build --strict

upgrade:
	uv sync --upgrade --all-extras --dev

build:
	uv build

pre-commit:
	uv run pre-commit run --all-files

sync:
	uv run sync-chosen-files

sync-once:
	uv run sync-chosen-files --once

clean:
	-rm -rf dist/
	-rm -rf site/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .ruff_cache/
	-rm -rf .coverage
	-rm -rf coverage.xml
	-rm -rf htmlcov/
	-rm -rf outputs/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +
