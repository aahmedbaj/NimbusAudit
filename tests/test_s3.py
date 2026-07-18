from nimbusaudit.checks.s3 import (
    check_s3_default_encryption,
    check_s3_default_encryption_uses_kms,
    check_s3_public_access_block,
    get_s3_default_encryption_algorithms,
    run_s3_bucket_checks,
)

def test_s3_public_access_block_fully_enabled_is_safe() -> None:
    bucket = {
        "Name": "safe-bucket",
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    }

    assert check_s3_public_access_block(bucket) is None


def test_s3_public_access_block_missing_is_finding() -> None:
    bucket = {
        "Name": "risky-bucket",
        "PublicAccessBlockConfiguration": None,
    }

    finding = check_s3_public_access_block(bucket)

    assert finding is not None
    assert finding.rule_id == "AWS-S3-BUCKET-001"
    assert finding.resource_id == "risky-bucket"
    assert finding.severity == "HIGH"


def test_s3_public_access_block_partial_config_is_finding() -> None:
    bucket = {
        "Name": "partial-bucket",
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": True,
        },
    }

    finding = check_s3_public_access_block(bucket)

    assert finding is not None
    assert "BlockPublicPolicy" in finding.evidence


def test_s3_default_encryption_enabled_is_safe() -> None:
    bucket = {
        "Name": "encrypted-bucket",
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256",
                    },
                },
            ],
        },
    }

    assert check_s3_default_encryption(bucket) is None


def test_s3_default_encryption_missing_is_finding() -> None:
    bucket = {
        "Name": "unencrypted-bucket",
        "ServerSideEncryptionConfiguration": None,
    }

    finding = check_s3_default_encryption(bucket)

    assert finding is not None
    assert finding.rule_id == "AWS-S3-BUCKET-002"
    assert finding.resource_id == "unencrypted-bucket"
    assert finding.severity == "HIGH"


def test_run_s3_bucket_checks_collects_multiple_findings() -> None:
    bucket = {
        "Name": "risky-bucket",
        "PublicAccessBlockConfiguration": None,
        "ServerSideEncryptionConfiguration": None,
    }

    findings = run_s3_bucket_checks([bucket])

    assert len(findings) == 2
    assert {
               finding.rule_id
               for finding in findings
           } == {
               "AWS-S3-BUCKET-001",
               "AWS-S3-BUCKET-002",
           }


def test_get_s3_default_encryption_algorithms_returns_empty_set_when_missing() -> None:
    bucket = {
        "Name": "unencrypted-bucket",
        "ServerSideEncryptionConfiguration": None,
    }

    assert get_s3_default_encryption_algorithms(bucket) == set()


def test_get_s3_default_encryption_algorithms_extracts_algorithms() -> None:
    bucket = {
        "Name": "encrypted-bucket",
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256",
                    },
                },
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms",
                    },
                },
            ],
        },
    }

    assert get_s3_default_encryption_algorithms(bucket) == {
        "AES256",
        "aws:kms",
    }


def test_s3_default_encryption_uses_kms_is_safe_for_sse_kms() -> None:
    bucket = {
        "Name": "kms-bucket",
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms",
                    },
                },
            ],
        },
    }

    assert check_s3_default_encryption_uses_kms(bucket) is None


def test_s3_default_encryption_uses_kms_is_safe_for_dsse_kms() -> None:
    bucket = {
        "Name": "dsse-kms-bucket",
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms:dsse",
                    },
                },
            ],
        },
    }

    assert check_s3_default_encryption_uses_kms(bucket) is None


def test_s3_default_encryption_uses_kms_finds_sse_s3() -> None:
    bucket = {
        "Name": "sse-s3-bucket",
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256",
                    },
                },
            ],
        },
    }

    finding = check_s3_default_encryption_uses_kms(bucket)

    assert finding is not None
    assert finding.rule_id == "AWS-S3-BUCKET-003"
    assert finding.severity == "MEDIUM"
    assert finding.resource_id == "sse-s3-bucket"
    assert "AWS Security Hub S3.17" in finding.standards


def test_s3_default_encryption_uses_kms_does_not_duplicate_missing_encryption() -> None:
    bucket = {
        "Name": "unencrypted-bucket",
        "ServerSideEncryptionConfiguration": None,
    }

    assert check_s3_default_encryption_uses_kms(bucket) is None


def test_run_s3_bucket_checks_reports_kms_finding_for_sse_s3() -> None:
    bucket = {
        "Name": "sse-s3-bucket",
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256",
                    },
                },
            ],
        },
    }

    findings = run_s3_bucket_checks([bucket])

    assert len(findings) == 1
    assert findings[0].rule_id == "AWS-S3-BUCKET-003"