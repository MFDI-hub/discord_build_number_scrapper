from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import load_settings
from .history import write_data_files
from .scraper import scrape_channels

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Discord web client build numbers")
    parser.add_argument(
        "--config",
        help="Path to config.toml (default: ./config.toml if present)",
    )
    parser.add_argument(
        "--impersonate",
        help="curl_cffi browser profile (e.g. chrome, chrome150, firefox147)",
    )
    parser.add_argument("--proxy", help="Proxy URL, e.g. socks5://user:pass@host:port")
    parser.add_argument("--timeout", type=float, help="HTTP timeout in seconds")
    parser.add_argument("--no-verify", action="store_true", help="Disable TLS certificate verify")
    parser.add_argument(
        "--channel",
        action="append",
        dest="channels",
        help="Channel to scrape (repeatable). Defaults to config/channels.",
    )
    parser.add_argument("--data-dir", help="Directory for latest.json and history.json")
    parser.add_argument("--max-files", type=int, help="Max JS files to inspect per channel")
    parser.add_argument("--concurrency", type=int, help="Parallel download limit")
    parser.add_argument("--asset-base-url", help="Base URL for /assets/ files")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        settings = load_settings(
            config_path=args.config,
            overrides={
                "impersonate": args.impersonate,
                "proxy": args.proxy,
                "timeout": args.timeout,
                "verify": False if args.no_verify else None,
                "channels": tuple(args.channels) if args.channels else None,
                "data_dir": args.data_dir,
                "max_files": args.max_files,
                "download_concurrency": args.concurrency,
                "asset_base_url": args.asset_base_url,
            },
        )
    except Exception as exc:
        logger.error("Invalid configuration: %s", exc)
        return 1

    scraped_at = datetime.now(timezone.utc)
    logger.info(
        "Scraping %s with impersonate=%s",
        ",".join(settings.channels),
        settings.impersonate,
    )

    try:
        snapshots = asyncio.run(scrape_channels(settings=settings, scraped_at=scraped_at))
    except Exception as exc:
        logger.error("Scrape failed: %s", exc)
        return 1

    write_data_files(Path(settings.data_dir), snapshots, scraped_at=scraped_at)
    for snapshot in snapshots:
        logger.info(
            "%s build_number=%s build_hash=%s",
            snapshot.channel,
            snapshot.build_number,
            snapshot.build_hash,
        )
    return 0


def run() -> None:
    sys.exit(main())
