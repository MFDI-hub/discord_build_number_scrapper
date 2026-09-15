# Development

## Setting up uv

This project uses [uv](https://docs.astral.sh/uv/) to manage Python and
dependencies. First, [install uv](installation.md#install-uv).

Then
[fork the MFDI-hub/discord_build_number_scrapper repo](https://github.com/MFDI-hub/discord_build_number_scrapper/fork)
and
[clone it](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

## Basic developer workflows

The `Makefile` offers shortcuts to `uv` commands. GitHub Actions call `uv`
directly, not the Makefile.

```shell
# First, install all dependencies, set up the venv, and install git hooks.
# This runs `uv sync --all-extras` and `pre-commit install`.
make install

# Run uv sync, lint, and test:
make

# Build wheel:
make build

# Linting (codespell, ruff, ty, vulture):
make lint

# Run tests (parallel + coverage):
make test

# Run all pre-commit hooks on the whole tree:
make pre-commit

# Preview documentation locally (MkDocs + Material):
make docs

# Strict docs build (same as CI):
make docs-build

# Delete build artifacts:
make clean

# Upgrade dependencies to compatible versions:
make upgrade

# Tests by hand:
uv run pytest
uv run pytest -n auto --cov --cov-report=term-missing
uv run pytest -s tests/test_scraper.py

# Install the current checkout as a local CLI:
uv tool install --editable .

# Dependency management:
uv add package_name
uv add --dev package_name
uv sync --upgrade
uv lock --upgrade-package package_name
uv add package_name@latest

# Activate the project venv:
uv venv
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
```

`pyproject.toml` defines an unused optional extra `observability` (`structlog`,
`tqdm`). Application code does not import it; prefer not adding it for new work.

See [uv docs](https://docs.astral.sh/uv/) for details.

## Sync chosen files

`scripts/sync_chosen_files.py` watches selected source paths and writes a single text
dump (useful for sharing code with LLMs or archiving a snapshot).

Edit `scripts/chosen_files.txt` to list files or directories (one path per line).
Then:

```shell
# One-shot dump:
uv run sync-chosen-files --once

# Watch and re-sync on changes:
uv run sync-chosen-files

# Custom paths or output file:
uv run sync-chosen-files --dir src/discord_build_number_scrapper --out outputs/builds/source_dump.txt --once
uv run sync-chosen-files --file-list scripts/chosen_files.txt --ext py,toml --once
```

Output defaults to `outputs/builds/source_dump.txt` (gitignored).

## Pre-commit and Commitizen

Install hooks once (also done by `make install`):

```shell
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

Hooks run ruff, codespell, ty, and vulture on commit. Commit messages should follow
[Conventional Commits](https://www.conventionalcommits.org/) (required for automated
releases). Use Commitizen interactively:

```shell
uv run cz commit
# or validate the last message:
uv run cz check --rev-range HEAD~1..HEAD
```

## IDE setup

If you use VS Code or a fork like Cursor or Windsurf, you can install the following
extensions:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [ty](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty)
  for type checking and the ty language server. Note that this extension works with
  non-Microsoft VS Code forks like Cursor.
- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

This repo also includes:

- **VS Code Tasks** (`.vscode/tasks.json`) — Run Task → `install` / `lint` / `test` / `docs` / …
- **Dev Container** (`.devcontainer/devcontainer.json`) — open in Codespaces or
  “Reopen in Container” for a ready uv + pre-commit environment

## Local CI with act

To run GitHub Actions workflows locally (optional):

```shell
# https://nektosact.com/
brew install act   # or see act install docs for your OS
act push           # simulate a push event (runs CI)
act -l             # list jobs
```

## HTTP client (httpie)

Handy for poking at HTTP APIs without adding a project dependency:

```shell
uvx httpie GET https://httpbin.org/get
# or install as a user tool:
uv tool install httpie
```

## Documentation hosting

Local and CI use MkDocs. For hosted docs you can:

- **GitHub Pages** — `.github/workflows/docs.yml` builds and deploys on push to
  `main`/`master`. Enable Pages in repo settings: **Settings → Pages → Build and
  deployment → GitHub Actions**. Site URL:
  [https://mfdi-hub.github.io/discord_build_number_scrapper/](https://mfdi-hub.github.io/discord_build_number_scrapper/)
- **Read the Docs** — import the repo on [Read the Docs](https://readthedocs.org/);
  `.readthedocs.yaml` is already included.

## Project management on GitHub

Optional GitHub features (not code):

- [Milestones](https://docs.github.com/en/issues/using-labels-and-milestones-for-issues-and-pull-requests/about-milestones)
  for version-scoped work
- [Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
  (boards) for kanban-style tracking

## Publishing releases

See [publishing.md](publishing.md) for GitHub Releases and PyPI.

## Documentation

- [uv docs](https://docs.astral.sh/uv/)
- [ty docs](https://docs.astral.sh/ty/)
- [MkDocs documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [pre-commit](https://pre-commit.com/)
- [Commitizen](https://commitizen-tools.github.io/commitizen/)
- [semantic-release](https://semantic-release.gitbook.io/)
- [Trivy](https://trivy.dev/)
