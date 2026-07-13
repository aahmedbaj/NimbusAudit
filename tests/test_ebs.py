from nimbusaudit.checks.ebs import (
    check_unencrypted_ebs_volume,
    run_ebs_volume_checks,
)


def test_encrypted_ebs_volume_is_safe() -> None:
    volume = {
        "VolumeId": "vol-safe",
        "Encrypted": True,
    }

    finding = check_unencrypted_ebs_volume(volume)

    assert finding is None


def test_unencrypted_ebs_volume_creates_finding() -> None:
    volume = {
        "VolumeId": "vol-vulnerable",
        "Encrypted": False,
    }

    finding = check_unencrypted_ebs_volume(volume)

    assert finding is not None
    assert finding.rule_id == "AWS-EC2-EBS-001"
    assert finding.severity == "HIGH"
    assert finding.resource_id == "vol-vulnerable"
    assert "False" in finding.evidence


def test_missing_encryption_field_creates_finding() -> None:
    volume = {
        "VolumeId": "vol-missing",
    }

    finding = check_unencrypted_ebs_volume(volume)

    assert finding is not None
    assert finding.resource_id == "vol-missing"
    assert "not reported" in finding.evidence


def test_missing_volume_id_uses_fallback() -> None:
    volume = {
        "Encrypted": False,
    }

    finding = check_unencrypted_ebs_volume(volume)

    assert finding is not None
    assert finding.resource_id == "unknown-volume"


def test_run_ebs_volume_checks_collects_findings() -> None:
    volumes = [
        {
            "VolumeId": "vol-safe",
            "Encrypted": True,
        },
        {
            "VolumeId": "vol-unencrypted",
            "Encrypted": False,
        },
        {
            "VolumeId": "vol-missing",
        },
    ]

    findings = run_ebs_volume_checks(volumes)

    assert len(findings) == 2
    assert {
               finding.resource_id
               for finding in findings
           } == {
               "vol-unencrypted",
               "vol-missing",
           }