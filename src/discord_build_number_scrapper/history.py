from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson

from .scraper import ChannelSnapshot

LATEST_FILENAME = "latest.json"
HISTORY_FILENAME = "history.json"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    payload = path.read_bytes().strip()
    if not payload:
        return default
    return orjson.loads(payload)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = orjson.dumps(payload, option=orjson.OPT_INDENT_2)
    path.write_bytes(encoded + b"\n")


def history_key(row: dict[str, Any]) -> tuple[str, int, str]:
    return (str(row["channel"]), int(row["build_number"]), str(row["build_hash"]))


def merge_history(
    history: list[dict[str, Any]],
    snapshots: list[ChannelSnapshot],
    scraped_at: datetime | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    scraped_at = scraped_at or datetime.now(timezone.utc)
    latest = {
        "updated_at": scraped_at.isoformat(),
        "channels": {snapshot.channel: snapshot.to_dict() for snapshot in snapshots},
    }

    existing = {history_key(row) for row in history}
    merged = list(history)
    for snapshot in snapshots:
        row = {
            "channel": snapshot.channel,
            "build_number": snapshot.build_number,
            "build_hash": snapshot.build_hash,
            "build_date": snapshot.build_date,
            "first_seen": scraped_at.isoformat(),
        }
        if history_key(row) not in existing:
            merged.append(row)
            existing.add(history_key(row))

    return latest, merged


def write_data_files(
    data_dir: Path,
    snapshots: list[ChannelSnapshot],
    scraped_at: datetime | None = None,
) -> tuple[Path, Path]:
    latest_path = data_dir / LATEST_FILENAME
    history_path = data_dir / HISTORY_FILENAME
    history = load_json(history_path, [])
    if not isinstance(history, list):
        raise TypeError(f"{history_path} must contain a JSON array")

    latest, merged = merge_history(history, snapshots, scraped_at=scraped_at)
    dump_json(latest_path, latest)
    dump_json(history_path, merged)
    return latest_path, history_path
