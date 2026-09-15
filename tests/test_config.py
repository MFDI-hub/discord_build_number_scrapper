from pathlib import Path

from discord_build_number_scrapper.config import Settings, load_settings
from discord_build_number_scrapper.history import load_json, write_data_files
from discord_build_number_scrapper.scraper import CHANNELS, ChannelSnapshot


def _write_toml(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def test_load_settings_from_toml(tmp_path: Path):
    config = _write_toml(
        tmp_path / "config.toml",
        """
impersonate = "firefox147"
timeout = 12
channels = ["canary"]
max_files = 5
download_concurrency = 2
""",
    )

    settings = load_settings(config_path=config, environ=False)

    assert settings.impersonate == "firefox147"
    assert settings.timeout == 12
    assert settings.channels == ("canary",)
    assert settings.max_files == 5
    assert settings.download_concurrency == 2


def test_cli_overrides_beat_config_file(tmp_path: Path):
    config = _write_toml(tmp_path / "config.toml", 'impersonate = "chrome131"\n')

    settings = load_settings(
        config_path=config,
        overrides={"impersonate": "safari260"},
        environ=False,
    )

    assert settings.impersonate == "safari260"


def test_env_overrides_config_file(tmp_path: Path, monkeypatch):
    config = _write_toml(tmp_path / "config.toml", 'impersonate = "chrome131"\n')
    monkeypatch.setenv("SCRAPER_IMPERSONATE", "chrome150")

    settings = load_settings(config_path=config, environ=True)

    assert settings.impersonate == "chrome150"


def test_unknown_impersonate_rejected(tmp_path: Path):
    config = _write_toml(tmp_path / "config.toml", 'impersonate = "netscape"\n')
    try:
        load_settings(config_path=config, environ=False)
    except ValueError as exc:
        assert "Unknown impersonate" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_unknown_config_key_rejected(tmp_path: Path):
    config = _write_toml(tmp_path / "config.toml", "not_a_real_key = 1\n")
    try:
        load_settings(config_path=config, environ=False)
    except ValueError as exc:
        assert "Unknown config key" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_defaults_without_config_file(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = load_settings(environ=False)
    assert settings.impersonate == "chrome"
    assert settings.channels == CHANNELS
    assert settings.proxy is None


def test_orjson_roundtrip(tmp_path: Path):
    snapshot = ChannelSnapshot(
        channel="canary",
        build_number=401234,
        build_hash="abc",
        build_date="2026-09-15T13:00:00+00:00",
        scraped_at="2026-09-15T13:50:00+00:00",
    )
    write_data_files(tmp_path, [snapshot])
    latest = load_json(tmp_path / "latest.json", {})
    history = load_json(tmp_path / "history.json", [])
    assert latest["channels"]["canary"]["build_number"] == 401234
    assert history[0]["build_hash"] == "abc"


def test_settings_default_impersonate_is_valid():
    Settings().validate()
