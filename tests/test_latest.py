from types import SimpleNamespace

import orjson
import pytest

from discord_build_number_scrapper.latest import (
    DEFAULT_LATEST_URL,
    LatestFetchError,
    fetch_latest,
    fetch_latest_channel,
    to_raw_github_url,
)

BLOB_URL = "https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/data/latest.json"
SAMPLE = {
    "updated_at": "2026-09-15T17:04:00.715490+00:00",
    "channels": {
        "stable": {
            "build_number": 613334,
            "build_hash": "fd72049652b026bf89686ce2515b1f1669cf7f68",
            "build_date": "2026-09-15T07:22:14+00:00",
            "scraped_at": "2026-09-15T17:04:00.715490+00:00",
        },
        "canary": {
            "build_number": 613515,
            "build_hash": "c2879f719a59d77013b84bf666a14f7e1a9f926b",
            "build_date": "2026-09-15T16:56:00+00:00",
            "scraped_at": "2026-09-15T17:04:00.715490+00:00",
        },
    },
}


def test_blob_url_converts_to_raw():
    assert to_raw_github_url(BLOB_URL) == DEFAULT_LATEST_URL
    assert to_raw_github_url(DEFAULT_LATEST_URL) == DEFAULT_LATEST_URL


def test_fetch_latest_parses_channels(monkeypatch):
    requested: list[str] = []

    def fake_get(url, settings, **kwargs):
        requested.append(url)
        return SimpleNamespace(ok=True, status_code=200, content=orjson.dumps(SAMPLE))

    monkeypatch.setattr("discord_build_number_scrapper.latest.request_get", fake_get)

    latest = fetch_latest(url=BLOB_URL)

    assert requested == [DEFAULT_LATEST_URL]
    assert latest.updated_at == SAMPLE["updated_at"]
    assert latest["stable"].build_number == 613334
    assert fetch_latest_channel("canary").build_hash == "c2879f719a59d77013b84bf666a14f7e1a9f926b"


def test_fetch_latest_http_error(monkeypatch):
    monkeypatch.setattr(
        "discord_build_number_scrapper.latest.request_get",
        lambda url, settings, **kwargs: SimpleNamespace(ok=False, status_code=404, content=b""),
    )
    with pytest.raises(LatestFetchError, match="HTTP 404"):
        fetch_latest()


def test_fetch_latest_missing_channel(monkeypatch):
    monkeypatch.setattr(
        "discord_build_number_scrapper.latest.request_get",
        lambda url, settings, **kwargs: SimpleNamespace(
            ok=True, status_code=200, content=orjson.dumps(SAMPLE)
        ),
    )
    latest = fetch_latest()
    with pytest.raises(KeyError, match="ptb"):
        latest["ptb"]
