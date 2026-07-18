from nimbusaudit.models import Finding


PUBLIC_ACCESS_BLOCK_KEYS = (
    "BlockPublicAcls",
    "IgnorePublicAcls",
    "BlockPublicPolicy",
    "RestrictPublicBuckets",
)

def get_s3_default_encryption_algorithms(
        bucket: dict,
) -> set[str]:
    encryption_config = bucket.get(
        "ServerSideEncryptionConfiguration"
    )

    rules = (
            encryption_config or {}
    ).get(
        "Rules",
        [],
    )

    algorithms = set()

    for rule in rules:
        default_encryption = rule.get(
            "ApplyServerSideEncryptionByDefault",
            {},
        )

        algorithm = default_encryption.get(
            "SSEAlgorithm"
        )

        if algorithm:
            algorithms.add(algorithm)

    return algorithms


def check_s3_public_access_block(
        bucket: dict,
) -> Finding | None:
    bucket_name = bucket.get("Name", "unknown-bucket")
    public_access_block = bucket.get(
        "PublicAccessBlockConfiguration"
    )

    if public_access_block and all(
            public_access_block.get(key) is True
            for key in PUBLIC_ACCESS_BLOCK_KEYS
    ):
        return None

    missing_or_disabled = [
        key
        for key in PUBLIC_ACCESS_BLOCK_KEYS
        if not public_access_block
           or public_access_block.get(key) is not True
    ]

    return Finding(
        rule_id="AWS-S3-BUCKET-001",
        title="S3 bucket does not fully block public access",
        severity="HIGH",
        resource_type="AWS::S3::Bucket",
        resource_id=bucket_name,
        evidence=(
            f"S3 bucket '{bucket_name}' does not have all public access "
            f"block settings enabled. Missing or disabled settings: "
            f"{', '.join(missing_or_disabled)}."
        ),
        remediation=(
            "Enable S3 Block Public Access settings for the bucket: "
            "BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, "
            "and RestrictPublicBuckets."
        ),
        standards=[
            "AWS Security Hub S3.8",
            "NIST.800-53.r5 AC-3",
            "NIST.800-53.r5 AC-6",
            "NIST.800-53.r5 SC-7",
        ],
    )


def check_s3_default_encryption(
        bucket: dict,
) -> Finding | None:
    bucket_name = bucket.get("Name", "unknown-bucket")
    algorithms = get_s3_default_encryption_algorithms(
        bucket
    )

    if algorithms:
        return None

    return Finding(
        rule_id="AWS-S3-BUCKET-002",
        title="S3 bucket default encryption is not enabled",
        severity="HIGH",
        resource_type="AWS::S3::Bucket",
        resource_id=bucket_name,
        evidence=(
            f"S3 bucket '{bucket_name}' does not have a default "
            "server-side encryption configuration."
        ),
        remediation=(
            "Enable default server-side encryption for the S3 bucket, "
            "using SSE-S3 or SSE-KMS depending on your security requirements."
        ),
        standards=[
            "NIST.800-53.r5 SC-13",
            "NIST.800-53.r5 SC-28",
        ],
    )

def check_s3_default_encryption_uses_kms(
        bucket: dict,
) -> Finding | None:
    bucket_name = bucket.get("Name", "unknown-bucket")
    algorithms = get_s3_default_encryption_algorithms(
        bucket
    )

    if not algorithms:
        return None

    kms_algorithms = {
        "aws:kms",
        "aws:kms:dsse",
    }

    if algorithms & kms_algorithms:
        return None

    return Finding(
        rule_id="AWS-S3-BUCKET-003",
        title="S3 bucket default encryption does not use AWS KMS",
        severity="MEDIUM",
        resource_type="AWS::S3::Bucket",
        resource_id=bucket_name,
        evidence=(
            f"S3 bucket '{bucket_name}' uses default encryption "
            f"algorithm(s): {', '.join(sorted(algorithms))}. "
            "AWS KMS encryption was not detected."
        ),
        remediation=(
            "Configure default server-side encryption with AWS KMS "
            "using SSE-KMS or DSSE-KMS when stronger key management, "
            "auditability, or compliance alignment is required."
        ),
        standards=[
            "AWS Security Hub S3.17",
            "NIST.800-53.r5 SC-13",
            "NIST.800-53.r5 SC-28",
        ],
    )



def run_s3_bucket_checks(
        buckets: list[dict],
) -> list[Finding]:
    findings = []

    for bucket in buckets:
        for check in (
                check_s3_public_access_block,
                check_s3_default_encryption,
                check_s3_default_encryption_uses_kms,
        ):
            finding = check(bucket)

            if finding is not None:
                findings.append(finding)

    return findings