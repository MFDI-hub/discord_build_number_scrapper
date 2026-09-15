from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any, get_args

from curl_cffi.requests import BrowserTypeLiteral

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_CHANNELS = ("stable", "ptb", "canary")
DEFAULT_DOMAINS = {
    "stable": "discord.com",
    "ptb": "ptb.discord.com",
    "canary": "canary.discord.com",
}
VALID_IMPERSONATE = set(get_args(BrowserTypeLiteral))


@dataclass(frozen=True)
class Settings:
    impersonate: str = "chrome"
    proxy: str | None = None
    timeout: float = 30
    verify: bool = True
    channels: tuple[str, ...] = DEFAULT_CHANNELS
    data_dir: str = "data"
    max_files: int = 200
    download_concurrency: int = 8
    asset_base_url: str = "https://discord.com"
    headers: dict[str, str] = field(default_factory=dict)
    domains: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_DOMAINS))

    def validate(self) -> Settings:
        if self.impersonate not in VALID_IMPERSONATE:
            allowed = ", ".join(sorted(VALID_IMPERSONATE))
            raise ValueError(f"Unknown impersonate {self.impersonate!r}. Allowed: {allowed}")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.max_files < 1:
            raise ValueError("max_files must be at least 1")
        if self.download_concurrency < 1:
            raise ValueError("download_concurrency must be at least 1")
        if not self.channels:
            raise ValueError("channels must not be empty")
        unknown = [channel for channel in self.channels if channel not in self.domains]
        if unknown:
            raise ValueError(
                f"No domain configured for channel(s): {', '.join(unknown)}. "
                "Add them under [domains] in config.toml."
            )
        return self


def _none_if_empty(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"0", "false", "none", "off"}:
        return None
    return text


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def _mapping_from_file(raw: Mapping[str, Any]) -> dict[str, Any]:
    known = {item.name for item in fields(Settings)}
    unknown = set(raw) - known
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"Unknown config key(s): {names}")
    return _normalize(raw)


def _normalize(raw: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "impersonate" in raw:
        out["impersonate"] = str(raw["impersonate"]).strip()
    if "proxy" in raw:
        out["proxy"] = _none_if_empty(raw["proxy"])
    if "timeout" in raw:
        out["timeout"] = float(raw["timeout"])
    if "verify" in raw:
        out["verify"] = _as_bool(raw["verify"])
    if "channels" in raw:
        out["channels"] = tuple(str(item) for item in raw["channels"])
    if "data_dir" in raw:
        out["data_dir"] = str(raw["data_dir"])
    if "max_files" in raw:
        out["max_files"] = int(raw["max_files"])
    if "download_concurrency" in raw:
        out["download_concurrency"] = int(raw["download_concurrency"])
    if "asset_base_url" in raw:
        out["asset_base_url"] = str(raw["asset_base_url"]).rstrip("/")
    if "headers" in raw:
        headers = raw["headers"] or {}
        if not isinstance(headers, Mapping):
            raise TypeError("headers must be a table/object of string keys and values")
        out["headers"] = {str(key): str(value) for key, value in headers.items()}
    if "domains" in raw:
        domains = raw["domains"] or {}
        if not isinstance(domains, Mapping):
            raise TypeError("domains must be a table/object of channel=host entries")
        merged = dict(DEFAULT_DOMAINS)
        merged.update({str(key): str(value) for key, value in domains.items()})
        out["domains"] = merged
    return out


def _env_overrides() -> dict[str, Any]:
    raw: dict[str, Any] = {}
    impersonate = os.getenv("SCRAPER_IMPERSONATE", "").strip()
    if impersonate:
        raw["impersonate"] = impersonate
    proxy = os.getenv("SCRAPER_PROXY")
    if proxy is not None and proxy.strip():
        raw["proxy"] = proxy
    timeout = os.getenv("SCRAPER_TIMEOUT", "").strip()
    if timeout:
        raw["timeout"] = timeout
    verify = os.getenv("SCRAPER_VERIFY", "").strip()
    if verify:
        raw["verify"] = verify
    channels = os.getenv("SCRAPER_CHANNELS", "").strip()
    if channels:
        raw["channels"] = [item.strip() for item in channels.split(",") if item.strip()]
    data_dir = os.getenv("SCRAPER_DATA_DIR", "").strip()
    if data_dir:
        raw["data_dir"] = data_dir
    max_files = os.getenv("SCRAPER_MAX_FILES", "").strip()
    if max_files:
        raw["max_files"] = max_files
    concurrency = os.getenv("SCRAPER_CONCURRENCY", "").strip()
    if concurrency:
        raw["download_concurrency"] = concurrency
    asset_base_url = os.getenv("SCRAPER_ASSET_BASE_URL", "").strip()
    if asset_base_url:
        raw["asset_base_url"] = asset_base_url
    return _normalize(raw)


def resolve_config_path(config_path: str | Path | None = None) -> Path | None:
    if config_path is not None:
        return Path(config_path)
    env_path = os.getenv("SCRAPER_CONFIG", "").strip()
    if env_path:
        return Path(env_path)
    if DEFAULT_CONFIG_PATH.is_file():
        return DEFAULT_CONFIG_PATH
    return None


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a TOML table")
    return payload


def load_settings(
    *,
    config_path: str | Path | None = None,
    overrides: Mapping[str, Any] | None = None,
    environ: bool = True,
) -> Settings:
    settings = Settings()
    path = resolve_config_path(config_path)
    if path is not None:
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        settings = replace(settings, **_mapping_from_file(load_toml(path)))
    if environ:
        env = _env_overrides()
        if env:
            settings = replace(settings, **env)
    if overrides:
        cleaned = {key: value for key, value in overrides.items() if value is not None}
        if cleaned:
            settings = replace(settings, **_normalize(cleaned))
    return settings.validate()
