# Changelog

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