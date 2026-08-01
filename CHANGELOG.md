# Changelog

## 0.2.0

### Added

- Added Terraform AWS lab under `terraform/aws-lab`.
- Added reproducible network lab resources: VPC, public subnet, internet gateway, public route table, and route table association.
- Added intentionally vulnerable security group with SSH open to `0.0.0.0/0`.
- Added EC2 lab instance with IMDSv2 not enforced.
- Added EBS root volume encryption test case.
- Added S3 lab bucket with incomplete Block Public Access configuration.
- Added S3 lab bucket encryption configuration using SSE-S3 instead of AWS KMS.
- Added Terraform outputs for comparing lab resources with NimbusAudit findings.
- Added Terraform lab documentation for deploy, scan, and destroy workflow.

### Notes

- The Terraform lab intentionally creates vulnerable AWS configurations for controlled testing.
- The lab should be destroyed after testing to avoid unnecessary cost and exposure.
- Some AWS accounts or regions may enforce EBS encryption by default, so the EBS encryption finding may not always appear.

## 0.1.0

Initial NimbusAudit release.

### Added

- Added read-only AWS security auditing CLI.
- Added persistent configuration with `nimbusaudit configure`.
- Added security group checks for public SSH, RDP, database ports, and unrestricted access.
- Added EC2 IMDSv2 enforcement check.
- Added EBS encryption check.
- Added S3 bucket public access block, default encryption, and KMS encryption checks.
- Added selectable check groups with `--checks`.
- Added interactive scan menu with `nimbusaudit menu`.
- Added text and JSON report output.
- Added report file output with `--output-file`.
- Added configurable failure threshold with `--fail-on`.
- Added CI-friendly exit codes.
- Added GitHub Actions test workflow.
- Added pytest coverage for collectors, checks, CLI behavior, config handling, and report helpers.