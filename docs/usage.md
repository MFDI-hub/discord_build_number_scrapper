# Usage

The console script is `discord_build_number_scrapper`. You can also run `python -m discord_build_number_scrapper`.

## Scrape Discord

Fetches each configured channel, writes `latest.json` and `history.json` under `--data-dir` (default `data/`), then logs `build_number` and `build_hash`.

=== "uv"

    ```shell
    uvx discord_build_number_scrapper
    uv run discord_build_number_scrapper
    uv run python -m discord_build_number_scrapper
    ```

=== "pip"

    ```shell
    discord_build_number_scrapper
    python -m discord_build_number_scrapper
    ```

```text
INFO discord_build_number_scrapper.cli: Scraping stable,ptb,canary with impersonate=chrome
INFO discord_build_number_scrapper.cli: stable build_number=613334 build_hash=fd72049652b026bf89686ce2515b1f1669cf7f68
```

Limit channels or pass a config file:

```shell
discord_build_number_scrapper --channel canary --channel ptb
discord_build_number_scrapper --config ./config.toml --impersonate chrome
```

## Read published data (`--from-repo`)

Downloads this repo's `latest.json` instead of scraping Discord. Logs the same channel lines; **does not write** `latest.json` or `history.json`.

The default URL is:

`https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json`

GitHub blob page URLs passed to `--latest-url` are converted to raw URLs.

=== "uv"

    ```shell
    uvx discord_build_number_scrapper --from-repo
    uvx discord_build_number_scrapper --from-repo --latest-url https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/data/latest.json
    ```

=== "pip"

    ```shell
    discord_build_number_scrapper --from-repo
    discord_build_number_scrapper --from-repo --latest-url https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/data/latest.json
    ```

## CLI flags

| Flag | Description |
|------|-------------|
| `--config PATH` | Path to `config.toml` (default: `./config.toml` if present, or `SCRAPER_CONFIG`) |
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
| `--latest-url URL` | URL of `latest.json` (blob URLs become raw). Default is this repo's file on `main` |
| `-v`, `--verbose` | Debug logging |

Exit code `0` on success, `1` on invalid config, scrape failure, or fetch failure.

Flags override environment variables and `config.toml`. See [Configuration](configuration.md).

## Python API

Public exports: `fetch_latest`, `fetch_latest_channel`, `LatestBuilds`, `LatestFetchError`, `ChannelSnapshot`, `main`.

```python
from discord_build_number_scrapper import (
    ChannelSnapshot,
    LatestFetchError,
    fetch_latest,
    fetch_latest_channel,
)

latest = fetch_latest()
print(latest.updated_at, latest.source_url)

stable: ChannelSnapshot = latest["stable"]
print(stable.build_number, stable.build_hash, stable.build_date, stable.scraped_at)

canary = fetch_latest_channel("canary")
print(canary.build_number)
```

`latest[channel]` raises `KeyError` if the channel is missing. HTTP/JSON problems raise `LatestFetchError`.

You can scrape programmatically by calling `main()` (same as the CLI, including writing data files unless you pass `--from-repo`):

```python
from discord_build_number_scrapper import main

raise SystemExit(main(["--channel", "canary", "-v"]))
```

## Data files

### `latest.json`

Written on scrape. Shape:

```json
{
  "updated_at": "2026-09-15T17:04:00.715490+00:00",
  "channels": {
    "stable": {
      "build_number": 613334,
      "build_hash": "fd72049652b026bf89686ce2515b1f1669cf7f68",
      "build_date": "2026-09-15T07:22:14+00:00",
      "scraped_at": "2026-09-15T17:04:00.715490+00:00"
    }
  }
}
```

Raw URL on `main`:

[https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json](https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json)

### `history.json`

JSON array. A row is appended only when the `(channel, build_number, build_hash)` triple is new:

```json
{
  "channel": "stable",
  "build_number": 612377,
  "build_hash": "8b3cee648b2457bdba2be1095faa28a0743c8c00",
  "build_date": "2026-09-14T07:22:28+00:00",
  "first_seen": "2026-09-15T14:07:36.567272+00:00"
}
```

## How scraping works

1. GET `https://{domain}/app` for each channel (`discord.com`, `ptb.discord.com`, `canary.discord.com` by default).
2. Read `x-build-id` as `build_hash` and `Last-Modified` as `build_date` (UTC now if the header is missing).
3. Search the HTML for `build_number:"…"`.
4. If that fails, walk `/assets/*.js` (capped by `max_files`, parallelized with `download_concurrency`) until a build number is found.
5. Channels run sequentially. Any channel failure fails the whole run.

## Hourly automation

[`.github/workflows/scrape.yml`](https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/.github/workflows/scrape.yml) runs on a cron (`0 * * * *`) and on `workflow_dispatch`. It runs `uv run discord_build_number_scrapper` and commits `data/latest.json` and `data/history.json` when they change.

Optional repo settings:

- Secret `SCRAPER_PROXY`
- Variable `SCRAPER_IMPERSONATE`

On scrape failure, the workflow opens or updates a `scraper-failure` issue; a later success closes those issues.
