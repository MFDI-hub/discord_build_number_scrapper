from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts._lib.bootstrap import resolve_path

OUTPUTS_DIR = resolve_path("outputs")
BUILDS_DIR = OUTPUTS_DIR / "builds"


def output_dir(path: str | Path) -> Path:
    """Resolve a directory path and create it."""
    resolved = resolve_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def output_path(path: str | Path) -> Path:
    """Resolve a repo-relative path and create parent directories."""
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def write_output(
    path: str | Path,
    content: str | dict[str, Any] | list[Any],
    *,
    indent: int = 2,
    newline: bool = True,
) -> Path:
    """Write text or JSON to a file under the repo. Returns the resolved path."""
    out = output_path(path)
    if isinstance(content, (dict, list)):
        text = json.dumps(content, ensure_ascii=False, indent=indent) + "\n"
    elif newline and content and not content.endswith("\n"):
        text = content + "\n"
    else:
        text = content
    out.write_text(text, encoding="utf-8")
    return out.resolve()
