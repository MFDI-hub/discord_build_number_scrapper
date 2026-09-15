# discord_build_number_scrapper

Scrape Discord web client build numbers for stable, PTB, and canary.

[![CI](https://github.com/MFDI-hub/discord_build_number_scrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/MFDI-hub/discord_build_number_scrapper/actions/workflows/ci.yml)
[![Docs](https://github.com/MFDI-hub/discord_build_number_scrapper/actions/workflows/docs.yml/badge.svg)](https://mfdi-hub.github.io/discord_build_number_scrapper/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-docs-222?logo=githubpages&logoColor=white)](https://mfdi-hub.github.io/discord_build_number_scrapper/)
[![PyPI](https://img.shields.io/pypi/v/discord-build-number-scrapper.svg?logo=pypi&logoColor=white)](https://pypi.org/project/discord-build-number-scrapper/)
[![Python versions](https://img.shields.io/pypi/pyversions/discord-build-number-scrapper.svg)](https://pypi.org/project/discord-build-number-scrapper/)
[![Downloads](https://img.shields.io/badge/downloads-PyPI-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/discord-build-number-scrapper/)
[![License](https://img.shields.io/pypi/l/discord-build-number-scrapper.svg)](https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/LICENSE)

[GitHub Pages](https://mfdi-hub.github.io/discord_build_number_scrapper/) ·
[PyPI](https://pypi.org/project/discord-build-number-scrapper/) ·
[latest.json](https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json)

A CLI and Python library that fetches Discord's `/app` pages (and JS assets when needed) to extract `build_number` and `build_hash`. This repo also publishes hourly scrape results in [`data/latest.json`](data/latest.json), so you can consume the numbers without hitting Discord yourself.

## Installation

Requires Python 3.10+.

**pip**

```shell
pip install discord_build_number_scrapper
```

**uv**

```shell
# Add as a project dependency
uv add discord_build_number_scrapper

# Or install as a user tool
uv tool install discord_build_number_scrapper
```

Both pip and uv install from the same PyPI package. Download counts on the badge above include all installers.

## Quick start

Scrape Discord and write `data/latest.json` plus `data/history.json`:

```shell
# pip
discord_build_number_scrapper

# uv (no install)
uvx discord_build_number_scrapper
```

```text
INFO discord_build_number_scrapper.cli: Scraping stable,ptb,canary with impersonate=chrome
INFO discord_build_number_scrapper.cli: stable build_number=613334 build_hash=fd72049652b026bf89686ce2515b1f1669cf7f68
INFO discord_build_number_scrapper.cli: ptb build_number=613334 build_hash=fd72049652b026bf89686ce2515b1f1669cf7f68
INFO discord_build_number_scrapper.cli: canary build_number=613515 build_hash=c2879f719a59d77013b84bf666a14f7e1a9f926b
```

Read the published snapshot from this repo instead of scraping Discord (`--from-repo` does not write data files):

```shell
# pip
discord_build_number_scrapper --from-repo

# uv
uvx discord_build_number_scrapper --from-repo
```

Python:

```python
from discord_build_number_scrapper import fetch_latest, fetch_latest_channel

latest = fetch_latest()
print(latest.updated_at)
print(latest["stable"].build_number)

canary = fetch_latest_channel("canary")
print(canary.build_hash)
```

## Features

- **Channels**: scrapes `stable`, `ptb`, and `canary` by default
- **Browser impersonation**: uses curl_cffi profiles such as `chrome` or `firefox147`
- **Published data**: hourly GitHub Actions updates [`data/latest.json`](https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json)
- **History**: appends new `(channel, build_number, build_hash)` rows to `data/history.json`
- **Config**: CLI flags override `SCRAPER_*` env vars, which override `config.toml`

## CLI

| Flag | Description |
|------|-------------|
| `--config PATH` | Path to `config.toml` (default: `./config.toml` if present) |
| `--impersonate PROFILE` | curl_cffi browser profile (e.g. `chrome`, `chrome150`, `firefox147`) |
| `--proxy URL` | Proxy URL, e.g. `socks5://user:pass@host:port` |
| `--timeout SECONDS` | HTTP timeout in seconds |
| `--no-verify` | Disable TLS certificate verify |
| `--channel NAME` | Channel to scrape (repeatable). Defaults to config/channels |
| `--data-dir PATH` | Directory for `latest.json` and `history.json` |
| `--max-files N` | Max JS files to inspect per channel |
| `--concurrency N` | Parallel download limit |
| `--asset-base-url URL` | Base URL for `/assets/` files |
| `--from-repo` | Fetch `latest.json` from GitHub instead of scraping Discord |
| `--latest-url URL` | URL of `latest.json` (GitHub blob URLs are converted to raw) |
| `-v`, `--verbose` | Debug logging |

Also runnable as a module:

```shell
python -m discord_build_number_scrapper --from-repo
uv run python -m discord_build_number_scrapper --from-repo
```

## Configuration

Priority: **CLI flags > environment variables > `config.toml` > defaults**.

See [configuration](https://mfdi-hub.github.io/discord_build_number_scrapper/configuration/) for `config.toml` keys and `SCRAPER_*` env vars.

## Documentation

Hosted on [GitHub Pages](https://mfdi-hub.github.io/discord_build_number_scrapper/):

- [Home](https://mfdi-hub.github.io/discord_build_number_scrapper/)
- [Installation](https://mfdi-hub.github.io/discord_build_number_scrapper/installation/)
- [Usage](https://mfdi-hub.github.io/discord_build_number_scrapper/usage/)
- [Configuration](https://mfdi-hub.github.io/discord_build_number_scrapper/configuration/)
- [Development](https://mfdi-hub.github.io/discord_build_number_scrapper/development/)
- [Publishing](https://mfdi-hub.github.io/discord_build_number_scrapper/publishing/)

## Contributing

Development uses [uv](https://docs.astral.sh/uv/). See [CONTRIBUTING.md](CONTRIBUTING.md) and [development docs](https://mfdi-hub.github.io/discord_build_number_scrapper/development/).

## License

[MIT](LICENSE)

*Built from [python-template](https://github.com/MFDI-hub/python-template).*
