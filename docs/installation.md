## Installing uv and Python

This project is set up to use [**uv**](https://docs.astral.sh/uv/) for Python and
dependency management.

### Install uv

On macOS or Linux:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you use Homebrew (macOS):

```shell
brew update
brew install uv
```

See [uv's docs](https://docs.astral.sh/uv/getting-started/installation/) for all
supported installation methods.

### Install Python with uv

```shell
uv python install 3.13
```

You can choose any compatible version required by this project.

### Install project dependencies

From your project root:

```shell
uv sync --all-extras
```

This creates `.venv` and installs runtime + development dependencies.
