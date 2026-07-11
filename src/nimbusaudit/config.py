import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REGION = "eu-central-1"
DEFAULT_OUTPUT_FORMAT = "text"
VALID_OUTPUT_FORMATS = ["text", "json"]

class config_error(Exception):
    """Raised when NimbusAudit configuration cannot be loaded or saved."""

@dataclass
class NimbusAuditConfig:
    profile :str | None = None
    region :str = DEFAULT_REGION
    output_format :str = DEFAULT_OUTPUT_FORMAT

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "region": self.region,
            "format": self.output_format,
        }
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NimbusAuditConfig":
        profile = data["profile"]
        region = data["region"]
        output_format = data["format"]

        if profile is not None and not isinstance(profile, str):
            raise config_error("Configuration field 'profile' must be a non-empty string")

        if not isinstance(region, str) or not region.strip():
            raise config_error(
                "Configuration field 'region' must be a non-empty string."
            )


        if output_format not in VALID_OUTPUT_FORMATS:
            raise config_error(
                "Configuration field 'format' must be either 'text' or 'json'."
            )

        if output_format not in VALID_OUTPUT_FORMATS:
            raise config_error("Configuration field 'output_format' must be must be either 'text' or 'json'.")

        return cls(
            profile=profile,
            region=region,
            output_format=output_format,
        )


def get_config_path() -> Path:
    """Return the platform-appropriate NimbusAudit config file path."""

    override_path = os.getenv("NIMBUSAUDIT_CONFIG_FILE")

    if override_path:
        return Path(override_path).expanduser()

    if os.name == "nt":
        base_directory = Path(
            os.environ.get(
                "APPDATA",
                Path.home() / "AppData" / "Roaming",
                )
        )
    else:
        base_directory = Path(
            os.environ.get(
                "XDG_CONFIG_HOME",
                Path.home() / ".config",
                )
        )

    return base_directory / "nimbusaudit" / "config.json"


def load_config(path: Path | None = None) -> NimbusAuditConfig:
    """Load NimbusAudit configuration or return defaults if none exists."""

    config_path = path or get_config_path()

    if not config_path.exists():
        return NimbusAuditConfig()

    try:
        raw_data = config_path.read_text(encoding="utf-8")
        data = json.loads(raw_data)
    except OSError as exc:
        raise config_error(
            f"Could not read configuration file '{config_path}': {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise config_error(
            f"Configuration file '{config_path}' contains invalid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise config_error(
            f"Configuration file '{config_path}' must contain a JSON object."
        )

    return NimbusAuditConfig.from_dict(data)


def save_config(
        config: NimbusAuditConfig,
        path: Path | None = None,
) -> Path:
    """Save NimbusAudit configuration and return the saved file path."""

    config_path = path or get_config_path()
    temporary_path = config_path.with_suffix(".tmp")

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path.write_text(
            json.dumps(config.to_dict(), indent=2) + "\n",
            encoding="utf-8",
            )

        temporary_path.replace(config_path)
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        raise config_error(
            f"Could not save configuration file '{config_path}': {exc}"
        ) from exc

    return config_path

