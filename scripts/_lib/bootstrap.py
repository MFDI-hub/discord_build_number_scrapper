from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV = REPO_ROOT / ".env"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def resolve_path(path: str | Path) -> Path:
    """Turn a repo-relative path into an absolute path under REPO_ROOT."""
    p = Path(path).expanduser()
    return p if p.is_absolute() else REPO_ROOT / p


def load_env(path: Path | None = None) -> None:
    """Load KEY=VALUE pairs from .env into os.environ (no overwrite)."""
    env_path = path or DEFAULT_ENV
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if value and value[0] in "\"'" and value[-1] == value[0]:
            value = value[1:-1]
        os.environ.setdefault(key, value)
