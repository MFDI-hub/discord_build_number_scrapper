# discord_build_number_scrapper

Scrape Discord web client build numbers for **stable**, **PTB**, and **canary**.

This project is both a Python CLI/library and a data repo. The CLI fetches Discord `/app` pages (and JS assets when the build number is not in the HTML) using [curl_cffi](https://github.com/lexiforest/curl_cffi) browser impersonation. GitHub Actions also scrape hourly and commit [`data/latest.json`](https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/data/latest.json) so you can read published numbers without hitting Discord.

## Guides

- [Installation](installation.md) — pip and uv for users; uv for contributors
- [Usage](usage.md) — CLI flags, Python API, and JSON data files
- [Configuration](configuration.md) — `config.toml`, env vars, and CLI overrides
- [Development](development.md) — lint, test, hooks, and local docs
- [Publishing](publishing.md) — GitHub Releases and PyPI

## Quick start

=== "uv"

    ```shell
    uvx discord_build_number_scrapper --from-repo
    ```

=== "pip"

    ```shell
    pip install discord_build_number_scrapper
    discord_build_number_scrapper --from-repo
    ```

```python
from discord_build_number_scrapper import fetch_latest

latest = fetch_latest()
print(latest["stable"].build_number)
```

Published snapshot (updated hourly):

[https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json](https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json)
