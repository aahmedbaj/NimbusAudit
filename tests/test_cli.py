from pathlib import Path
from unittest.mock import MagicMock

import pytest

from nimbusaudit.aws import AwsError
from nimbusaudit.cli import main, resolve_output_format_and_file, OutputError, write_or_print_output, \
    resolve_check_groups, CheckSelectionError, should_fail_on_findings
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


def test_resolve_check_groups_defaults_to_all() -> None:
    selected = resolve_check_groups(None)

    assert selected == {
        "security-groups",
        "ec2",
        "ebs",
    }


def test_resolve_check_groups_accepts_all() -> None:
    selected = resolve_check_groups("all")

    assert selected == {
        "security-groups",
        "ec2",
        "ebs",
    }


def test_resolve_check_groups_accepts_single_group() -> None:
    selected = resolve_check_groups("ec2")

    assert selected == {
        "ec2",
    }


def test_resolve_check_groups_accepts_multiple_groups() -> None:
    selected = resolve_check_groups("security-groups,ec2")

    assert selected == {
        "security-groups",
        "ec2",
    }


def test_resolve_check_groups_ignores_extra_spaces() -> None:
    selected = resolve_check_groups(" security-groups , ebs ")

    assert selected == {
        "security-groups",
        "ebs",
    }


def test_resolve_check_groups_rejects_empty_value() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="no check groups were provided",
    ):
        resolve_check_groups("")


def test_resolve_check_groups_rejects_unsupported_group() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="unsupported check group",
    ):
        resolve_check_groups("s3")


def test_resolve_check_groups_rejects_all_combined_with_other_groups() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="'all' cannot be combined",
    ):
        resolve_check_groups("all,ec2")


from dataclasses import dataclass


@dataclass
class FakeFinding:
    severity: str

def test_should_fail_on_critical_only_when_critical_exists() -> None:
    findings = [
        FakeFinding(severity="HIGH"),
        FakeFinding(severity="MEDIUM"),
    ]

    assert should_fail_on_findings(
        findings,
        fail_on="critical",
    ) is False

    findings.append(
        FakeFinding(severity="CRITICAL")
    )

    assert should_fail_on_findings(
        findings,
        fail_on="critical",
    ) is True


def test_should_fail_on_high_for_high_and_critical() -> None:
    assert should_fail_on_findings(
        [FakeFinding(severity="HIGH")],
        fail_on="high",
    ) is True

    assert should_fail_on_findings(
        [FakeFinding(severity="CRITICAL")],
        fail_on="high",
    ) is True

    assert should_fail_on_findings(
        [FakeFinding(severity="MEDIUM")],
        fail_on="high",
    ) is False


def test_should_fail_on_medium_for_medium_and_above() -> None:
    assert should_fail_on_findings(
        [FakeFinding(severity="MEDIUM")],
        fail_on="medium",
    ) is True

    assert should_fail_on_findings(
        [FakeFinding(severity="HIGH")],
        fail_on="medium",
    ) is True

    assert should_fail_on_findings(
        [FakeFinding(severity="LOW")],
        fail_on="medium",
    ) is False


def test_should_fail_on_low_for_any_known_severity() -> None:
    findings = [
        FakeFinding(severity="LOW"),
    ]

    assert should_fail_on_findings(
        findings,
        fail_on="low",
    ) is True


def test_should_not_fail_when_no_findings_exist() -> None:
    assert should_fail_on_findings(
        [],
        fail_on="low",
    ) is False


def test_should_ignore_unknown_severity_for_failure_threshold() -> None:
    findings = [
        FakeFinding(severity="INFO"),
    ]

    assert should_fail_on_findings(
        findings,
        fail_on="low",
    ) is False