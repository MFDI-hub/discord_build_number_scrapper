from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import orjson

from .config import Settings
from .http_client import request_get
from .scraper import ChannelSnapshot

logger = logging.getLogger(__name__)

DEFAULT_LATEST_URL = (
    "https://raw.githubusercontent.com/MFDI-hub/discord_build_number_scrapper/main/data/latest.json"
)
_BLOB_URL = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<ref>[^/]+)/(?P<path>.+)$"
)


class LatestFetchError(RuntimeError):
    """Raised when latest.json cannot be fetched or parsed."""


@dataclass(frozen=True)
class LatestBuilds:
    updated_at: str
    channels: dict[str, ChannelSnapshot]
    source_url: str

    def __getitem__(self, channel: str) -> ChannelSnapshot:
        try:
            return self.channels[channel]
        except KeyError as exc:
            available = ", ".join(sorted(self.channels)) or "(none)"
            raise KeyError(f"Channel {channel!r} not in latest.json. Available: {available}") from exc


def to_raw_github_url(url: str) -> str:
    """Turn a GitHub blob page URL into a raw file URL."""
    match = _BLOB_URL.match(url.strip())
    if not match:
        return url
    return (
        "https://raw.githubusercontent.com/"
        f"{match.group('owner')}/{match.group('repo')}/{match.group('ref')}/{match.group('path')}"
    )


def _snapshot_from_payload(channel: str, payload: Any) -> ChannelSnapshot:
    if not isinstance(payload, dict):
        raise LatestFetchError(f"Channel {channel!r} must be a JSON object")
    try:
        return ChannelSnapshot(
            channel=channel,
            build_number=int(payload["build_number"]),
            build_hash=str(payload["build_hash"]),
            build_date=str(payload["build_date"]),
            scraped_at=str(payload["scraped_at"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise LatestFetchError(f"Channel {channel!r} is missing or invalid: {exc}") from exc


def _parse_latest(payload: Any, source_url: str) -> LatestBuilds:
    if not isinstance(payload, dict):
        raise LatestFetchError("latest.json must be a JSON object")
    channels_raw = payload.get("channels")
    if not isinstance(channels_raw, dict) or not channels_raw:
        raise LatestFetchError("latest.json is missing a channels object")

    updated_at = payload.get("updated_at")
    if updated_at is None:
        raise LatestFetchError("latest.json is missing updated_at")

    channels = {
        str(name): _snapshot_from_payload(str(name), body) for name, body in channels_raw.items()
    }
    return LatestBuilds(updated_at=str(updated_at), channels=channels, source_url=source_url)


def fetch_latest(
    url: str = DEFAULT_LATEST_URL,
    settings: Settings | None = None,
) -> LatestBuilds:
    """Fetch Discord build numbers from the published latest.json in this repo."""
    settings = settings or Settings()
    source_url = to_raw_github_url(url)
    logger.info("Fetching latest builds from %s", source_url)
    response = request_get(source_url, settings)
    if not response.ok:
        raise LatestFetchError(f"Failed to fetch {source_url}: HTTP {response.status_code}")
    try:
        payload = orjson.loads(response.content)
    except orjson.JSONDecodeError as exc:
        raise LatestFetchError(f"Response from {source_url} is not valid JSON") from exc
    return _parse_latest(payload, source_url)


def fetch_latest_channel(
    channel: str,
    url: str = DEFAULT_LATEST_URL,
    settings: Settings | None = None,
) -> ChannelSnapshot:
    """Fetch a single channel's build from the published latest.json."""
    return fetch_latest(url=url, settings=settings)[channel]
