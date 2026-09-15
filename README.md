# discord_build_number_scrapper

> **This is the initial readme for your project from the
> [python-template](https://github.com/MFDI-hub/python-template) Copier template.** Fill it in and
> delete this message!
> Below are general setup instructions that you may remove or keep and adapt for your
> project.

* * *

## Project Docs

For how to install uv and Python, see [installation.md](docs/installation.md).

For development workflows, see [development.md](docs/development.md).

For instructions on publishing to PyPI, see [publishing.md](docs/publishing.md).

## Quickstart

```shell
# Install project dependencies + git hooks:
make install
# or: uv sync --all-extras && uv run pre-commit install

# Run quality checks:
uv run python devtools/lint.py
uv run pytest -n auto --cov --cov-report=term-missing

# Build package artifacts:
uv build
```

## Lockfile (`uv.lock`)

`make install` / `uv sync` creates a `uv.lock` for reproducible development
environments. For **libraries**, you may choose not to commit `uv.lock` so consumers
are not pinned to your exact dependency tree. For **applications**, commit `uv.lock`
so deployments are reproducible.

* * *

*This project was built from
[python-template](https://github.com/MFDI-hub/python-template).*
