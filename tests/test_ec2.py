from nimbusaudit.checks.ec2 import (
    check_imdsv2_not_enforced,
    run_ec2_instance_checks,
)

from nimbusaudit.checks.ec2 import (
    check_imdsv2_not_enforced,
    run_ec2_instance_checks,
)

def test_imdsv2_required_is_safe() -> None:
    instance = {
        "InstanceId": "i-safe",
        "MetadataOptions": {
            "HttpTokens": "required",
        },
    }

    finding = check_imdsv2_not_enforced(instance)

    assert finding is None

def test_imdsv2_optional_creates_finding() -> None:
    instance = {
        "InstanceId": "i-vulnerable",
        "MetadataOptions": {
            "HttpTokens": "optional",
        },
    }

    finding = check_imdsv2_not_enforced(instance)

    assert finding is not None
    assert finding.rule_id == "AWS-EC2-INSTANCE-001"
    assert finding.severity == "HIGH"
    assert finding.resource_id == "i-vulnerable"
    assert "optional" in finding.evidence

def test_missing_metadata_options_creates_finding() -> None:
    instance = {
        "InstanceId": "i-missing-metadata",
    }

    finding = check_imdsv2_not_enforced(instance)

    assert finding is not None
    assert finding.resource_id == "i-missing-metadata"
    assert "not reported" in finding.evidence

def test_missing_instance_id_uses_fallback() -> None:
    instance = {
        "MetadataOptions": {
            "HttpTokens": "optional",
        },
    }

    finding = check_imdsv2_not_enforced(instance)

    assert finding is not None
    assert finding.resource_id == "unknown-instance"


def test_run_ec2_instance_checks_collects_findings() -> None:
    instances = [
        {
            "InstanceId": "i-safe",
            "MetadataOptions": {
                "HttpTokens": "required",
            },
        },
        {
            "InstanceId": "i-optional",
            "MetadataOptions": {
                "HttpTokens": "optional",
            },
        },
        {
            "InstanceId": "i-missing",
        },
    ]

    findings = run_ec2_instance_checks(instances)

    assert len(findings) == 2
    assert {
               finding.resource_id
               for finding in findings
           } == {
               "i-optional",
               "i-missing",
           }

