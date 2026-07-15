from pathlib import Path
from unittest.mock import MagicMock

import pytest

from nimbusaudit.aws import AwsError
from nimbusaudit.cli import main, resolve_output_format_and_file, OutputError, write_or_print_output
from nimbusaudit.config import NimbusAuditConfig


def test_main_returns_exit_code_2_on_aws_error(
        monkeypatch,
        capsys,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["nimbusaudit"],
    )

    monkeypatch.setattr(
        "nimbusaudit.cli.load_config",
        MagicMock(
            return_value=NimbusAuditConfig(
                profile="missing-profile",
                region="eu-central-1",
                output_format="text",
            )
        ),
    )

    monkeypatch.setattr(
        "nimbusaudit.cli.create_session",
        MagicMock(
            side_effect=AwsError(
                "AWS profile 'missing-profile' was not found."
            )
        ),
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 2
    assert (
            "NimbusAudit AWS error: "
            "AWS profile 'missing-profile' was not found."
            in captured.out
    )


def test_resolve_output_uses_cli_format_without_file() -> None:
    output_format, output_file = resolve_output_format_and_file(
        configured_format="text",
        cli_format="json",
        output_file=None,
    )

    assert output_format == "json"
    assert output_file is None


def test_resolve_output_uses_configured_format_without_file() -> None:
    output_format, output_file = resolve_output_format_and_file(
        configured_format="json",
        cli_format=None,
        output_file=None,
    )

    assert output_format == "json"
    assert output_file is None


def test_resolve_output_adds_suffix_from_configured_format() -> None:
    output_format, output_file = resolve_output_format_and_file(
        configured_format="text",
        cli_format=None,
        output_file="report",
    )

    assert output_format == "text"
    assert output_file == Path("report.txt")


def test_resolve_output_adds_suffix_from_cli_format() -> None:
    output_format, output_file = resolve_output_format_and_file(
        configured_format="text",
        cli_format="json",
        output_file="report",
    )

    assert output_format == "json"
    assert output_file == Path("report.json")


def test_resolve_output_json_suffix_sets_json_format() -> None:
    output_format, output_file = resolve_output_format_and_file(
        configured_format="text",
        cli_format=None,
        output_file="report.json",
    )

    assert output_format == "json"
    assert output_file == Path("report.json")


def test_resolve_output_txt_suffix_sets_text_format() -> None:
    output_format, output_file = resolve_output_format_and_file(
        configured_format="json",
        cli_format=None,
        output_file="report.txt",
    )

    assert output_format == "text"
    assert output_file == Path("report.txt")


def test_resolve_output_rejects_text_format_with_json_suffix() -> None:
    with pytest.raises(
            OutputError,
            match="conflicts with --format 'text'",
    ):
        resolve_output_format_and_file(
            configured_format="text",
            cli_format="text",
            output_file="report.json",
        )


def test_resolve_output_rejects_json_format_with_txt_suffix() -> None:
    with pytest.raises(
            OutputError,
            match="conflicts with --format 'json'",
    ):
        resolve_output_format_and_file(
            configured_format="text",
            cli_format="json",
            output_file="report.txt",
        )


def test_resolve_output_rejects_unsupported_suffix() -> None:
    with pytest.raises(
            OutputError,
            match="unsupported output file extension '.csv'",
    ):
        resolve_output_format_and_file(
            configured_format="text",
            cli_format=None,
            output_file="report.csv",
        )


def test_write_or_print_output_prints_to_stdout(
        capsys,
) -> None:
    exit_code = write_or_print_output(
        content="hello from NimbusAudit",
        output_file=None,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "hello from NimbusAudit" in captured.out


def test_write_or_print_output_writes_file(
        tmp_path: Path,
        capsys,
) -> None:
    output_file = tmp_path / "report.txt"

    exit_code = write_or_print_output(
        content="NimbusAudit report",
        output_file=output_file,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_file.read_text(
        encoding="utf-8",
    ) == "NimbusAudit report\n"
    assert f"Output written to {output_file}" in captured.out


def test_write_or_print_output_creates_parent_directories(
        tmp_path: Path,
) -> None:
    output_file = (
            tmp_path
            / "reports"
            / "aws"
            / "report.txt"
    )

    exit_code = write_or_print_output(
        content="nested report",
        output_file=output_file,
    )

    assert exit_code == 0
    assert output_file.exists()
    assert output_file.read_text(
        encoding="utf-8",
    ) == "nested report\n"