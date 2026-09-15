# Installation

Requires **Python 3.10 or later**.

## Users

Install from [PyPI](https://pypi.org/project/discord_build_number_scrapper/). pip and uv resolve the same package; download stats on PyPI include both.

### Install the package

=== "uv"

    Add it to a project:

    ```shell
    uv add discord_build_number_scrapper
    ```

    Or install it as a user-wide CLI:

    ```shell
    uv tool install discord_build_number_scrapper
    ```

=== "pip"

    ```shell
    pip install discord_build_number_scrapper
    ```

### Run the CLI

=== "uv"

    One-off, no install:

    ```shell
    uvx discord_build_number_scrapper --from-repo
    ```

    After `uv add` (from the project directory):

    ```shell
    uv run discord_build_number_scrapper --from-repo
    ```

    After `uv tool install`:

    ```shell
    discord_build_number_scrapper --from-repo
    ```

=== "pip"

    ```shell
    discord_build_number_scrapper --from-repo
    python -m discord_build_number_scrapper --from-repo
    ```

See [Usage](usage.md) for scrape vs `--from-repo` and all flags.

## Contributors

This repo uses [uv](https://docs.astral.sh/uv/) for Python and dependency management.

### Install uv

=== "macOS / Linux"

    ```shell
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "Homebrew"

    ```shell
    brew update
    brew install uv
    ```

See [uv's install docs](https://docs.astral.sh/uv/getting-started/installation/) for other methods.

### Install Python with uv

```shell
uv python install 3.13
```

Any version in `>=3.10,<4.0` works.

### Install project dependencies

From the repository root:

```shell
uv sync --all-extras
```

This creates `.venv` and installs runtime plus development dependencies. `make install` also installs pre-commit hooks. See [Development](development.md).
