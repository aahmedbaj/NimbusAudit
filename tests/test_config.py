import json
from pathlib import Path

import pytest

from nimbusaudit.config import (
    config_error,
    NimbusAuditConfig,
    get_config_path,
    load_config,
    save_config,
)


def test_load_config_returns_defaults_when_file_does_not_exist(
        tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"

    config = load_config(config_path)

    assert config.profile is None
    assert config.region == "eu-central-1"
    assert config.output_format == "text"


def test_save_and_load_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"

    original_config = NimbusAuditConfig(
        profile="nimbusaudit-readonly",
        region="eu-central-1",
        output_format="json",
    )

    saved_path = save_config(original_config, config_path)
    loaded_config = load_config(config_path)

    assert saved_path == config_path
    assert loaded_config == original_config


def test_save_config_creates_parent_directories(tmp_path: Path) -> None:
    config_path = (
            tmp_path
            / "nested"
            / "nimbusaudit"
            / "config.json"
    )

    config = NimbusAuditConfig(
        profile="nimbusaudit-readonly",
    )

    save_config(config, config_path)

    assert config_path.exists()


def test_load_config_rejects_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        "{not-valid-json",
        encoding="utf-8",
    )

    with pytest.raises(
            config_error,
            match="contains invalid JSON",
    ):
        load_config(config_path)


def test_load_config_rejects_non_object_json(
        tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '["text", "json"]',
        encoding="utf-8",
    )

    with pytest.raises(
            config_error,
            match="must contain a JSON object",
    ):
        load_config(config_path)


def test_load_config_rejects_invalid_profile_type(
        tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "profile": 123,
                "region": "eu-central-1",
                "format": "text",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
            config_error,
            match="'profile' must be a non-empty string",
    ):
        load_config(config_path)


def test_load_config_rejects_empty_region(
        tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "profile": "nimbusaudit-readonly",
                "region": "   ",
                "format": "text",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
            config_error,
            match="'region' must be a non-empty string",
    ):
        load_config(config_path)


def test_load_config_rejects_invalid_output_format(
        tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "profile": "nimbusaudit-readonly",
                "region": "eu-central-1",
                "format": "xml",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
            config_error,
            match="'format' must be either 'text' or 'json'",
    ):
        load_config(config_path)


def test_get_config_path_uses_environment_override(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
) -> None:
    custom_path = tmp_path / "custom-config.json"

    monkeypatch.setenv(
        "NIMBUSAUDIT_CONFIG_FILE",
        str(custom_path),
    )

    assert get_config_path() == custom_path