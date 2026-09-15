from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from .config import DEFAULT_CHANNELS, Settings
from .http_client import request_get

logger = logging.getLogger(__name__)

CHANNELS = DEFAULT_CHANNELS
IGNORED_FILENAMES = ("NW.js", "Node.js", "bn.js", "hash.js")

BUILD_NUMBER_REGEX = re.compile(r'build_number:"(\d+?)"')
HTML_URL_REGEX = re.compile(r'(?:src|href)=(?:"|\')(.+?)(?:"|\')')
JS_URL_REGEX__RSPACK = re.compile(r'"(?P<hash>(?:[\de]+?\.)?\w+?\.js)"')
JS_URL_REGEX__27_03_2024_RSPACK_group1 = re.compile(
    r'"(?P<id>[\de]+)"===\w\?(?:""\+\w\+)?"(?::?[\de]+)?(?P<hash>\.\w+?\.js)":?'
)
JS_URL_REGEX__27_03_2024_RSPACK_group2 = re.compile(r'\.js":""\+\(({(?:[\de]+:"\w+",?)+})\)')
JS_URL_REGEX__27_03_2024_RSPACK_group2_inner = re.compile(r'[\de]+:"(?P<hash>\w+)",?')


class BuildNumberNotFoundError(RuntimeError):
    """Raised when a Discord channel is fetched but no build number is found."""


@dataclass(frozen=True)
class ChannelSnapshot:
    channel: str
    build_number: int
    build_hash: str
    build_date: str
    scraped_at: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "build_number": self.build_number,
            "build_hash": self.build_hash,
            "build_date": self.build_date,
            "scraped_at": self.scraped_at,
        }


def extract_build_number(contents: str) -> int | None:
    match = BUILD_NUMBER_REGEX.search(contents)
    if not match:
        return None
    return int(match.group(1))


def _js_paths_from_html(body: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for match in HTML_URL_REGEX.finditer(body):
        url = match.group(1)
        if not url.startswith("/assets/") or not url.endswith(".js"):
            continue
        if url in seen:
            continue
        seen.add(url)
        paths.append(url)
    return paths


def _js_paths_from_js(body: str) -> list[str]:
    captured: list[re.Match[str]] = []
    matches_g1 = list(JS_URL_REGEX__27_03_2024_RSPACK_group1.finditer(body))
    if matches_g1:
        matches_g2 = list(JS_URL_REGEX__27_03_2024_RSPACK_group2.finditer(body))
        if matches_g2:
            inner_match = matches_g2[0].group(1)
            inner = list(JS_URL_REGEX__27_03_2024_RSPACK_group2_inner.finditer(inner_match))
            if inner:
                captured.extend(matches_g1)
                captured.extend(inner)

    if not captured:
        captured = list(JS_URL_REGEX__RSPACK.finditer(body))

    paths: list[str] = []
    seen: set[str] = set()
    for asset in captured:
        groups = asset.groupdict()
        asset_id = groups.get("id") or ""
        asset_hash = groups.get("hash") or ""
        url = f"{asset_id}{asset_hash}"
        if not url.endswith(".js"):
            url += ".js"
        if url in IGNORED_FILENAMES:
            continue
        path = f"/assets/{url}"
        if path in seen:
            continue
        seen.add(path)
        paths.append(path)
    return paths


def _parse_build_date(last_modified: str | None) -> datetime:
    if last_modified:
        build_date = parsedate_to_datetime(last_modified)
        if build_date.tzinfo is None:
            build_date = build_date.replace(tzinfo=timezone.utc)
        return build_date.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def _download_text(url: str, settings: Settings) -> str:
    response = request_get(url, settings)
    if not response.ok:
        raise RuntimeError(f"Failed to fetch {url}: HTTP {response.status_code}")
    return response.text


async def _download_text_async(url: str, settings: Settings, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        return await asyncio.to_thread(_download_text, url, settings)


async def scrape_channel(
    channel: str,
    settings: Settings | None = None,
    scraped_at: datetime | None = None,
) -> ChannelSnapshot:
    settings = settings or Settings()
    if channel not in settings.domains:
        raise ValueError(f"Unsupported channel: {channel}")

    scraped_at = scraped_at or datetime.now(timezone.utc)
    domain = settings.domains[channel]
    app_url = f"https://{domain}/app"
    logger.info(
        "Fetching %s build from %s (impersonate=%s)",
        channel,
        app_url,
        settings.impersonate,
    )

    response = await asyncio.to_thread(request_get, app_url, settings)
    if not response.ok:
        raise RuntimeError(
            f"Failed to fetch Discord build from {app_url}: HTTP {response.status_code}"
        )

    build_hash = response.headers.get("x-build-id")
    if not build_hash:
        raise RuntimeError(f"Missing x-build-id header from {app_url}")

    html = response.text
    build_date = _parse_build_date(response.headers.get("last-modified"))

    build_number = extract_build_number(html)
    if build_number:
        return _snapshot(channel, build_number, build_hash, build_date, scraped_at)

    semaphore = asyncio.Semaphore(settings.download_concurrency)
    visited: set[str] = set()
    queue = _js_paths_from_html(html)
    inspected = 0

    while queue and inspected < settings.max_files:
        batch: list[str] = []
        while (
            queue
            and len(batch) < settings.download_concurrency
            and inspected + len(batch) < settings.max_files
        ):
            path = queue.pop(0)
            if path in visited:
                continue
            visited.add(path)
            batch.append(path)

        if not batch:
            break

        results = await asyncio.gather(
            *[
                _download_text_async(f"{settings.asset_base_url}{path}", settings, semaphore)
                for path in batch
            ],
            return_exceptions=True,
        )
        inspected += len(batch)

        for path, result in zip(batch, results, strict=True):
            if isinstance(result, BaseException):
                logger.warning("Skipping %s: %s", path, result)
                continue
            build_number = extract_build_number(result)
            if build_number:
                logger.info("Found %s build number %s in %s", channel, build_number, path)
                return _snapshot(channel, build_number, build_hash, build_date, scraped_at)
            for nested in _js_paths_from_js(result):
                if nested not in visited:
                    queue.append(nested)

    raise BuildNumberNotFoundError(
        f"Could not find a build number for {channel} (hash={build_hash}, files_inspected={inspected})"
    )


def _snapshot(
    channel: str,
    build_number: int,
    build_hash: str,
    build_date: datetime,
    scraped_at: datetime,
) -> ChannelSnapshot:
    return ChannelSnapshot(
        channel=channel,
        build_number=build_number,
        build_hash=build_hash,
        build_date=build_date.isoformat(),
        scraped_at=scraped_at.isoformat(),
    )


async def scrape_channels(
    settings: Settings | None = None,
    channels: tuple[str, ...] | None = None,
    scraped_at: datetime | None = None,
) -> list[ChannelSnapshot]:
    settings = settings or Settings()
    channels = channels or settings.channels
    scraped_at = scraped_at or datetime.now(timezone.utc)
    snapshots: list[ChannelSnapshot] = []
    errors: list[str] = []

    for channel in channels:
        try:
            snapshots.append(
                await scrape_channel(channel, settings=settings, scraped_at=scraped_at)
            )
        except Exception as exc:
            logger.exception("Failed to scrape %s", channel)
            errors.append(f"{channel}: {exc}")

    if errors:
        details = "; ".join(errors)
        raise BuildNumberNotFoundError(f"Failed to scrape one or more channels: {details}")

    return snapshots
