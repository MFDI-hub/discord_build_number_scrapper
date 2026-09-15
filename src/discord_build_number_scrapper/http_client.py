from __future__ import annotations

from typing import Any

from curl_cffi import requests

from .config import Settings


def _proxy_dict(settings: Settings) -> dict[str, str] | None:
    if not settings.proxy:
        return None
    return {"http": settings.proxy, "https": settings.proxy}


def request_get(url: str, settings: Settings, **kwargs: Any):
    proxies = _proxy_dict(settings)
    if proxies is not None:
        kwargs.setdefault("proxies", proxies)
    kwargs.setdefault("timeout", settings.timeout)
    kwargs.setdefault("impersonate", settings.impersonate)
    kwargs.setdefault("verify", settings.verify)
    if settings.headers:
        headers = dict(settings.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        kwargs["headers"] = headers
    return requests.get(url, **kwargs)
