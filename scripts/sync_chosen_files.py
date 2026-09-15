#!/usr/bin/env python3
"""Watch source files and dump them to one text file.

Usage:
  uv run sync-chosen-files
  uv run sync-chosen-files --once
  uv run sync-chosen-files src/my_package
  uv run sync-chosen-files --dir src/my_package --dir scripts
  uv run sync-chosen-files --file-list scripts/chosen_files.txt
  uv run sync-chosen-files --ext py,toml --once
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts._lib.bootstrap import load_env, resolve_path
from scripts._lib.chosen_file_sync import SyncConfig, resolve_watch_roots, run_watch

DEFAULT_FILE_LIST = "scripts/chosen_files.txt"
DEFAULT_CODE_OUT = "outputs/builds/source_dump.txt"


def main() -> int:
    load_env()

    ap = argparse.ArgumentParser(description="Sync chosen source files into one text dump.")
    ap.add_argument(
        "paths",
        nargs="*",
        default=None,
        help="Files or directories to watch (default: scripts/chosen_files.txt)",
    )
    ap.add_argument(
        "--dir",
        action="append",
        default=[],
        metavar="PATH",
        help="Directory to watch recursively (repeatable)",
    )
    ap.add_argument(
        "--file-list",
        default=None,
        help=f"Text file with one path per line (default: {DEFAULT_FILE_LIST})",
    )
    ap.add_argument(
        "--out",
        default=DEFAULT_CODE_OUT,
        help=f"Output text file (default: {DEFAULT_CODE_OUT})",
    )
    ap.add_argument(
        "--mode",
        choices=("code", "concat", "lines"),
        default="code",
        help="code=full source dump (default), concat=raw bodies, lines=line dump",
    )
    ap.add_argument(
        "--ext",
        default="py",
        help="Comma-separated extensions for code/concat directory scan (default: py)",
    )
    ap.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Poll interval in seconds (default: 2)",
    )
    ap.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Keep duplicate lines (lines mode only)",
    )
    ap.add_argument(
        "--sort-longest",
        action="store_true",
        help="Sort output longest-first (lines mode only)",
    )
    ap.add_argument(
        "--no-header",
        action="store_true",
        help="Omit header block from output",
    )
    ap.add_argument(
        "--once",
        action="store_true",
        help="Write one dump and exit (default: watch and re-sync)",
    )
    args = ap.parse_args()

    code_globs = tuple(f"*.{ext.strip().lstrip('.')}" for ext in args.ext.split(",") if ext.strip())
    file_list = args.file_list
    if args.paths:
        watch_paths = args.paths
    elif file_list:
        watch_paths = []
    elif args.dir:
        watch_paths = []
        file_list = None
    else:
        watch_paths = []
        file_list = DEFAULT_FILE_LIST

    watch_roots = resolve_watch_roots(watch_paths, dirs=args.dir, file_list=file_list)

    missing = [path for path in watch_roots if not path.exists()]
    for path in missing:
        print(f"warning: not found yet (will watch for it): {path}")

    config = SyncConfig(
        watch_roots=watch_roots,
        out_path=resolve_path(args.out),
        interval=args.interval,
        mode=args.mode,
        code_globs=code_globs or ("*.py",),
        dedupe=not args.no_dedupe,
        sort_longest=args.sort_longest,
        include_header=not args.no_header,
    )
    if args.once:
        from scripts._lib.chosen_file_sync import SyncState, sync_once

        state = SyncState()
        sync_once(config, state, force=True)
        print(
            f"wrote {state.last_line_count} lines from {len(state.resolved_paths)} "
            f"file(s) -> {config.out_path}"
        )
        return 0
    return run_watch(config)


if __name__ == "__main__":
    raise SystemExit(main())
