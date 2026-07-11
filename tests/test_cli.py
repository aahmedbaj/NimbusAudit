from unittest.mock import MagicMock

from nimbusaudit.aws import AwsError
from nimbusaudit.cli import main
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