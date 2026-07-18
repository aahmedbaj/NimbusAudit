from nimbusaudit.models import Finding


def check_unencrypted_ebs_volume(
        volume: dict,
) -> Finding | None:
    volume_id = volume.get(
        "VolumeId",
        "unknown-volume",
    )

    encrypted = volume.get("Encrypted")

    if encrypted is True:
        return None

    return Finding(
        rule_id="AWS-EC2-EBS-001",
        title="EBS volume is not encrypted",
        severity="HIGH",
        resource_type="AWS::EC2::Volume",
        resource_id=volume_id,
        evidence=(
            f"EBS volume '{volume_id}' has encryption "
            f"set to '{encrypted if encrypted is not None else 'not reported'}'."
        ),
        remediation=(
            "Create an encrypted snapshot or copy, create a new "
            "encrypted volume from it, and replace the unencrypted volume."
        ),
        standards=[
            "AWS Security Hub EC2.3",
            "NIST.800-53.r5 SC-13",
            "NIST.800-53.r5 SC-28",
        ],
    )


def run_ebs_volume_checks(
        volumes: list[dict],
) -> list[Finding]:
    findings = []

    for volume in volumes:
        finding = check_unencrypted_ebs_volume(
            volume
        )

        if finding is not None:
            findings.append(finding)

    return findings