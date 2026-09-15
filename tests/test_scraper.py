from datetime import datetime, timezone

from discord_build_number_scrapper.history import merge_history
from discord_build_number_scrapper.scraper import ChannelSnapshot, extract_build_number


def test_extract_build_number_found():
    source = 'this.build_number="nope";build_number:"401234";other:1'
    assert extract_build_number(source) == 401234


def test_extract_build_number_missing():
    assert extract_build_number("const foo = 1;") is None


def _snapshot(
    channel: str = "canary", number: int = 401234, build_hash: str = "abc"
) -> ChannelSnapshot:
    return ChannelSnapshot(
        channel=channel,
        build_number=number,
        build_hash=build_hash,
        build_date="2026-09-15T13:00:00+00:00",
        scraped_at="2026-09-15T13:50:00+00:00",
    )


def test_merge_history_appends_new_build():
    scraped_at = datetime(2026, 9, 15, 13, 50, tzinfo=timezone.utc)
    snapshot = _snapshot()

    latest, history = merge_history([], [snapshot], scraped_at=scraped_at)

    assert latest["updated_at"] == "2026-09-15T13:50:00+00:00"
    assert latest["channels"]["canary"]["build_number"] == 401234
    assert history == [
        {
            "channel": "canary",
            "build_number": 401234,
            "build_hash": "abc",
            "build_date": "2026-09-15T13:00:00+00:00",
            "first_seen": "2026-09-15T13:50:00+00:00",
        }
    ]


def test_merge_history_ignores_duplicate():
    scraped_at = datetime(2026, 9, 15, 14, 0, tzinfo=timezone.utc)
    existing = [
        {
            "channel": "canary",
            "build_number": 401234,
            "build_hash": "abc",
            "build_date": "2026-09-15T13:00:00+00:00",
            "first_seen": "2026-09-15T13:50:00+00:00",
        }
    ]

    latest, history = merge_history(existing, [_snapshot()], scraped_at=scraped_at)

    assert latest["channels"]["canary"]["scraped_at"] == "2026-09-15T13:50:00+00:00"
    assert history == existing
