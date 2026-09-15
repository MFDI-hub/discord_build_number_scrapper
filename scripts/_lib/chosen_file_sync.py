from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from scripts._lib.bootstrap import REPO_ROOT, resolve_path
from scripts._lib.outputs import write_output

CODE_SKIP_DIRS = frozenset(
    {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "build",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "outputs",
        "bin",
        "logs",
        "script_logs",
    }
)
DEFAULT_CODE_GLOBS = ("*.py",)


@dataclass
class SyncConfig:
    """Watch files/directories and dump their contents to one text file."""

    watch_roots: list[Path]
    out_path: Path
    interval: float = 2.0
    mode: str = "code"
    code_globs: tuple[str, ...] = DEFAULT_CODE_GLOBS
    dedupe: bool = True
    sort_longest: bool = False
    include_header: bool = True


@dataclass
class SyncState:
    snapshot: dict[str, tuple[float, int]] = field(default_factory=dict)
    resolved_paths: list[Path] = field(default_factory=list)
    last_line_count: int = 0


def _should_skip(path: Path) -> bool:
    return any(part in CODE_SKIP_DIRS for part in path.parts)


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def discover_files(
    roots: list[Path],
    *,
    code_globs: tuple[str, ...] = DEFAULT_CODE_GLOBS,
) -> list[Path]:
    """Expand files and directories into a sorted list of source files."""
    discovered: set[Path] = set()

    for root in roots:
        resolved = resolve_path(root)
        if resolved.is_file():
            if not _should_skip(resolved):
                discovered.add(resolved.resolve())
            continue
        if not resolved.is_dir():
            continue
        for pattern in code_globs:
            for match in resolved.rglob(pattern):
                if match.is_file() and not _should_skip(match):
                    discovered.add(match.resolve())

    return sorted(discovered)


def resolve_watch_roots(
    paths: list[str | Path],
    *,
    dirs: list[str | Path] | None = None,
    file_list: str | Path | None = None,
) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()

    def add(raw: str | Path) -> None:
        path = resolve_path(raw)
        key = path.resolve() if path.exists() else path
        if key not in seen:
            seen.add(key)
            roots.append(path)

    if file_list:
        list_path = resolve_path(file_list)
        if not list_path.is_file():
            raise SystemExit(f"File list not found: {list_path}")
        for raw in list_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                add(line)

    for raw in paths:
        add(raw)

    for raw in dirs or []:
        add(raw)

    if not roots:
        raise SystemExit("No inputs. Pass file/dir paths, --dir, and/or --file-list.")
    return roots


def _read_plain_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_file_lines(path: Path, mode: str) -> list[str]:
    if not path.is_file():
        return []
    if mode in {"code", "concat"}:
        text = path.read_text(encoding="utf-8")
        return [text] if text else []
    return _read_plain_lines(path)


def collect_lines(paths: list[Path], config: SyncConfig) -> list[str]:
    collected: list[str] = []
    for path in paths:
        collected.extend(read_file_lines(path, config.mode))

    if config.dedupe:
        seen: set[str] = set()
        unique: list[str] = []
        for line in collected:
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(line)
        collected = unique

    if config.sort_longest:
        collected.sort(key=lambda line: (-len(line), line.lower()))
    else:
        collected.sort(key=str.lower)

    return collected


def build_code_output(paths: list[Path], *, include_header: bool) -> str:
    blocks: list[str] = []
    if include_header:
        blocks.append(
            "\n".join(
                [
                    "# synced source dump",
                    f"# files: {len(paths)}",
                    "",
                ]
            )
        )

    for path in paths:
        if not path.is_file():
            continue
        rel = _repo_relative(path)
        body = path.read_text(encoding="utf-8").rstrip()
        blocks.append(f"{'=' * 80}\nFILE: {rel}\n{'=' * 80}\n{body}\n")
    return "\n".join(blocks).rstrip() + ("\n" if blocks else "")


def build_output(paths: list[Path], config: SyncConfig) -> str:
    if config.mode == "code":
        return build_code_output(paths, include_header=config.include_header)
    if config.mode == "concat":
        blocks: list[str] = []
        for path in paths:
            if not path.is_file():
                continue
            body = path.read_text(encoding="utf-8")
            blocks.append(f"=== {_repo_relative(path)} ===\n{body.rstrip()}\n")
        return "\n".join(blocks).rstrip() + ("\n" if blocks else "")

    lines = collect_lines(paths, config)
    if config.include_header:
        header = [
            f"# synced from {len(paths)} file(s)",
            *(f"#   - {_repo_relative(path)}" for path in paths),
            "",
        ]
        return "\n".join(header + lines) + ("\n" if lines or header else "")
    return "\n".join(lines) + ("\n" if lines else "")


def snapshot_paths(paths: list[Path]) -> dict[str, tuple[float, int]]:
    state: dict[str, tuple[float, int]] = {}
    for path in paths:
        if path.is_file():
            stat = path.stat()
            state[str(path)] = (stat.st_mtime, stat.st_size)
    return state


def snapshot_changed(
    previous: dict[str, tuple[float, int]], current: dict[str, tuple[float, int]]
) -> bool:
    if set(current) != set(previous):
        return True
    return any(current[key] != previous.get(key) for key in current)


def resolve_paths_for_sync(config: SyncConfig) -> list[Path]:
    if config.mode in {"code", "concat"}:
        return discover_files(config.watch_roots, code_globs=config.code_globs)
    files: list[Path] = []
    for root in config.watch_roots:
        resolved = resolve_path(root)
        if resolved.is_file():
            files.append(resolved.resolve())
    return sorted(set(files))


def sync_once(config: SyncConfig, state: SyncState, *, force: bool = False) -> bool:
    paths = resolve_paths_for_sync(config)
    current = snapshot_paths(paths)
    if not force and not snapshot_changed(state.snapshot, current):
        return False

    content = build_output(paths, config)
    write_output(config.out_path, content, newline=False)
    state.snapshot = current
    state.resolved_paths = paths
    state.last_line_count = content.count("\n") if content else 0
    return True


def run_watch(config: SyncConfig) -> int:
    state = SyncState()
    sync_once(config, state, force=True)
    print(f"syncing {len(state.resolved_paths)} source file(s) -> {config.out_path}")
    print(f"mode={config.mode} interval={config.interval}s (Ctrl+C to stop)")
    print(f"initial write: {state.last_line_count} lines")

    try:
        while True:
            time.sleep(config.interval)
            if sync_once(config, state):
                print(f"updated: {len(state.resolved_paths)} files, {state.last_line_count} lines")
    except KeyboardInterrupt:
        print("\nstopped")
        return 0
