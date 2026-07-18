from nimbusaudit.models import Finding


def check_imdsv2_not_enforced(
        instance: dict,
) -> Finding | None:
    instance_id = instance.get(
        "InstanceId",
        "unknown-instance",
    )

    metadata_options = instance.get(
        "MetadataOptions",
        {},
    )

    http_tokens = metadata_options.get(
        "HttpTokens",
    )

    if http_tokens == "required":
        return None

    return Finding(
        rule_id="AWS-EC2-INSTANCE-001",
        title="IMDSv2 is not enforced",
        severity="HIGH",
        resource_type="AWS::EC2::Instance",
        resource_id=instance_id,
        evidence=(
            f"EC2 instance '{instance_id}' has "
            f"MetadataOptions.HttpTokens set to "
            f"'{http_tokens or 'not reported'}'."
        ),
        remediation=(
            "Configure the instance metadata options to require "
            "IMDSv2 by setting HttpTokens to 'required'."
        ),
        standards=[
            "AWS Security Hub EC2.8",
            "NIST.800-53.r5 AC-3",
            "NIST.800-53.r5 AC-6",
        ],
    )


def run_ec2_instance_checks(
        instances: list[dict],
) -> list[Finding]:
    findings = []

    for instance in instances:
        finding = check_imdsv2_not_enforced(
            instance
        )

        if finding is not None:
            findings.append(finding)

    return findings