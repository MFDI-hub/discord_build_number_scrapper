# Configuration

Settings resolve in this order (highest wins):

1. CLI flags
2. Environment variables (`SCRAPER_*`)
3. `config.toml` (or the path from `--config` / `SCRAPER_CONFIG`)
4. Built-in defaults

If `--config` is omitted, `SCRAPER_CONFIG` is used when set; otherwise `./config.toml` is loaded when that file exists.

## `config.toml`

Example at the repo root:

```toml
# Priority: CLI flags > environment variables > this file > defaults.

impersonate = "chrome"
# proxy = ""
timeout = 30
verify = true
channels = ["stable", "ptb", "canary"]
data_dir = "data"
max_files = 200
download_concurrency = 8
asset_base_url = "https://discord.com"

# Extra HTTP headers merged on top of the impersonated browser headers.
# [headers]
# Accept-Language = "en-US,en;q=0.9"

# Override or add channel hosts.
# [domains]
# stable = "discord.com"
# ptb = "ptb.discord.com"
# canary = "canary.discord.com"
# staging = "staging.discord.com"
```

Unknown top-level keys are rejected. Every name in `channels` must have an entry in `[domains]` (defaults cover `stable`, `ptb`, and `canary`).

### Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `impersonate` | string | `"chrome"` | curl_cffi browser profile. Aliases include `chrome`, `edge`, `safari`, `firefox`, `chrome_android`. Concrete examples: `chrome150`, `firefox147`. |
| `proxy` | string | unset | Proxy URL, e.g. `socks5://user:pass@host:port` or `http://host:port`. |
| `timeout` | float | `30` | HTTP timeout in seconds (must be `> 0`). |
| `verify` | bool | `true` | TLS certificate verify. |
| `channels` | list of strings | `["stable", "ptb", "canary"]` | Channels to scrape or to read from `--from-repo`. Must be non-empty. |
| `data_dir` | string | `"data"` | Directory for `latest.json` and `history.json`. |
| `max_files` | int | `200` | Max JS files to inspect per channel (at least `1`). |
| `download_concurrency` | int | `8` | Parallel asset download limit (at least `1`). |
| `asset_base_url` | string | `"https://discord.com"` | Base URL for `/assets/` files (trailing slash is stripped). |
| `[headers]` | table | `{}` | Extra headers merged on top of impersonated browser headers. |
| `[domains]` | table | see below | Channel name → host. Merged over defaults. |

Default domains:

| Channel | Host |
|---------|------|
| `stable` | `discord.com` |
| `ptb` | `ptb.discord.com` |
| `canary` | `canary.discord.com` |

To scrape a custom channel, add it under both `channels` and `[domains]`.

## Environment variables

| Variable | Maps to |
|----------|---------|
| `SCRAPER_CONFIG` | Config file path (if `--config` is not passed) |
| `SCRAPER_IMPERSONATE` | `impersonate` |
| `SCRAPER_PROXY` | `proxy` |
| `SCRAPER_TIMEOUT` | `timeout` |
| `SCRAPER_VERIFY` | `verify` (`1`/`true`/`yes`/`on` or `0`/`false`/`no`/`off`) |
| `SCRAPER_CHANNELS` | Comma-separated `channels` |
| `SCRAPER_DATA_DIR` | `data_dir` |
| `SCRAPER_MAX_FILES` | `max_files` |
| `SCRAPER_CONCURRENCY` | `download_concurrency` |
| `SCRAPER_ASSET_BASE_URL` | `asset_base_url` |

There are no env vars for `[headers]` or `[domains]`; set those in `config.toml`.

The hourly scrape workflow sets `SCRAPER_PROXY` from a repository secret and `SCRAPER_IMPERSONATE` from a repository variable.

## CLI overrides

| Flag | Setting |
|------|---------|
| `--config` | Config file path |
| `--impersonate` | `impersonate` |
| `--proxy` | `proxy` |
| `--timeout` | `timeout` |
| `--no-verify` | `verify = false` |
| `--channel` | `channels` (repeatable) |
| `--data-dir` | `data_dir` |
| `--max-files` | `max_files` |
| `--concurrency` | `download_concurrency` |
| `--asset-base-url` | `asset_base_url` |

`--from-repo` and `--latest-url` are CLI-only; they are not config keys.
