# Changelog

## 0.3.0

### Added

* Added Docker support for running NimbusAudit as a containerized CLI.
* Added `scripts/run-docker.sh` for secure Docker execution.
* Added host-side AWS credential resolution and temporary credential export for Docker scans.
* Added support for assuming a dedicated least-privilege AWS role before running containerized scans.
* Added persistent Docker configuration using the existing `~/.config/nimbusaudit/config.json`.
* Added Docker support for interactive `nimbusaudit menu` and `nimbusaudit configure`.
* Added AWS profile precedence for Docker scans: explicit CLI profile, saved NimbusAudit configuration, then `nimbusaudit-readonly`.
* Added persistent Docker report output through a bind-mounted `outputs/` directory.
* Added GitHub Actions validation for Docker image builds and CLI startup.
* Added CI coverage for Python 3.11 and Python 3.14.
* Added CI validation that the Docker container runs as a non-root user.

### Changed

* Relative report filenames are now written under the `outputs/` directory.
* Docker output behavior now follows the same report path rules as local NimbusAudit execution.
* Docker image contents were reduced by copying only the package source and `pyproject.toml`.
* Docker build context exclusions were tightened to omit development artifacts, caches, Terraform files, tests, IDE files, and generated output.
* Docker containers remain ephemeral while configuration and reports persist on the host.

### Fixed

* Fixed `--checks` handling so explicitly selected check groups run only the requested checks.
* Fixed Docker output path handling so relative report paths persist correctly on the host.

### Security

* Dockerized AWS scans no longer require mounting the host `~/.aws` directory into the container.
* Only the resolved temporary AWS credential set is mounted into the container as read-only.
* AWS login cache, source profiles, refresh state, and other host AWS identities remain outside the container.
* The Docker image runs NimbusAudit as a dedicated non-root user.

### Notes

* The recommended Docker workflow uses a dedicated least-privilege AWS role such as `NimbusAuditReadOnlyRole`.
* The Docker image uses `python:3.11-slim` as its base image.
* Docker images are validated in CI but are not published to a container registry as part of this release.

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