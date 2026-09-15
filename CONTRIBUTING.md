# Contributing

Thanks for your interest in contributing to **discord_build_number_scrapper**!

## Getting started

1. Fork and clone the repository.
2. Install dependencies and git hooks:

   ```shell
   uv sync --all-extras
   uv run pre-commit install
   ```

3. Create a branch for your change.

## Development workflow

```shell
uv run python devtools/lint.py
uv run pytest -n auto --cov --cov-report=term-missing
uv run mkdocs build --strict
```

See [development.md](docs/development.md) for full details.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) so automated releases work:

```text
feat: add new capability
fix: correct edge case in parser
docs: clarify installation steps
```

You can use Commitizen interactively:

```shell
uv run cz commit
```

## Pull requests

- Keep changes focused and reasonably sized.
- Update docs when behavior or public APIs change.
- Ensure CI passes before requesting review.
- Link related issues when applicable.

## Reporting issues

Use the GitHub issue templates for bugs and feature requests. Include steps to
reproduce, expected vs. actual behavior, and your environment when relevant.

## Code of conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful
and constructive in all interactions.
