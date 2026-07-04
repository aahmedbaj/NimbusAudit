# NimbusAudit

> See what your cloud forgot to secure.

NimbusAudit is a read-only AWS security auditing CLI that inspects cloud configurations and reports risky or unintended security settings.

It is designed to help cloud administrators, security engineers, and developers quickly identify issues such as publicly exposed administrative ports, overly broad security-group rules, and other common cloud misconfigurations.

NimbusAudit focuses on clear evidence, practical remediation guidance, and automation-friendly output.

## Why NimbusAudit?

Cloud environments change constantly.

New instances are deployed, security groups are modified, temporary rules are added, and old configurations are sometimes forgotten. A setting that was acceptable during testing may remain active long after it is needed.

For example:

* SSH may be exposed to the entire internet.
* RDP may be reachable from any IPv4 or IPv6 address.
* A database port may be publicly accessible.
* A security group may allow every protocol and port from the public internet.

NimbusAudit provides a lightweight way to inspect these configurations before they become larger security problems.

## Current Capabilities

NimbusAudit currently supports AWS security-group auditing.

It can:

* Authenticate using an existing AWS CLI profile
* Scan security groups in a selected AWS region
* Retrieve resources using paginated AWS API calls
* Detect publicly exposed SSH
* Detect publicly exposed RDP
* Detect publicly exposed MySQL
* Detect publicly exposed PostgreSQL
* Detect security groups exposing all protocols and ports
* Detect both IPv4 and IPv6 public exposure
* Detect sensitive ports inside broader port ranges
* Produce readable terminal output
* Produce structured JSON output
* Include severity, evidence, remediation, and standards mappings
* Return CI/CD-friendly exit codes
* Run without modifying cloud resources

## Example Finding

```text
Scanned 5 security groups:

[HIGH] SSH exposed to the public internet
  Rule: AWS-EC2-SG-001
  Resource: sg-0390cexxxxxxxxxxx
  Evidence: Security group 'nimbusaudit-vulnerable-sg' allows TCP port 22 from 0.0.0.0/0.
  Remediation: Restrict SSH access to an approved admin IP, corporate VPN, bastion host, or private access mechanism.
  Standards: AWS Security Hub EC2.53, NIST AC-6, NIST AC-17

Findings summary:
  CRITICAL: 0
  HIGH: 1
  MEDIUM: 0
  LOW: 0
```

## How It Works

```text
Command-line interface
        ↓
AWS session and authentication
        ↓
Paginated resource collection
        ↓
Security check engine
        ↓
Structured Finding objects
        ↓
Text or JSON report
        ↓
Process exit code
```

NimbusAudit separates AWS resource collection from security checks and output formatting.

This makes it easier to add new checks without rewriting the command-line interface or reporting logic.

## Project Structure

```text
src/nimbusaudit/
├── __init__.py
├── __main__.py
├── aws.py
├── cli.py
├── models.py
└── checks/
    ├── __init__.py
    └── security_groups.py

tests/
└── test_security_groups.py
```

## Installation

Clone the repository:

```bash
git clone https://github.com/aahmedbaj/NimbusAudit.git
cd NimbusAudit
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install NimbusAudit in editable mode with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## AWS Authentication

NimbusAudit uses an authorized AWS profile.

Configure or authenticate your profile before running the scan:

```bash
aws configure --profile my-profile
```

For AWS CLI login-based profiles:

```bash
aws login --profile my-profile
```

NimbusAudit does not require credentials to be stored inside the project.

The AWS identity used for scanning should have read-only access to the resources being inspected.

## Usage

Run a security-group scan:

```bash
python -m nimbusaudit \
  --profile my-profile \
  --region eu-central-1
```

Generate JSON output:

```bash
python -m nimbusaudit \
  --profile my-profile \
  --region eu-central-1 \
  --format json
```

## Exit Codes

NimbusAudit uses process exit codes so it can be integrated into shell scripts and CI/CD pipelines.

```text
0 = Scan completed with no HIGH or CRITICAL findings
1 = Scan completed and found HIGH or CRITICAL findings
2 = Scan could not be completed
```

Example:

```bash
python -m nimbusaudit \
  --profile my-profile \
  --region eu-central-1

echo $?
```

A CI/CD pipeline can use the returned value to block a deployment when a serious security issue is detected.

## Security Checks

| Rule ID        | Check                                     | Severity |
| -------------- | ----------------------------------------- | -------: |
| AWS-EC2-SG-001 | SSH exposed to the public internet        |     HIGH |
| AWS-EC2-SG-002 | RDP exposed to the public internet        |     HIGH |
| AWS-EC2-SG-003 | MySQL exposed to the public internet      |     HIGH |
| AWS-EC2-SG-004 | PostgreSQL exposed to the public internet |     HIGH |
| AWS-EC2-SG-005 | All protocols and ports exposed publicly  | CRITICAL |

Public exposure currently includes:

```text
0.0.0.0/0
::/0
```

NimbusAudit also detects when a sensitive port is included inside a wider range.

For example:

```text
TCP ports 20–30
```

would still be flagged because the range includes SSH port 22.

## Testing

The project uses Pytest.

Run the test suite:

```bash
pytest -v
```

The current test suite covers:

* Public IPv4 exposure
* Public IPv6 exposure
* Exact sensitive ports
* Sensitive ports inside broader ranges
* Safe restricted CIDR rules
* Safe public HTTP access
* Private internal all-traffic rules
* Multiple findings collected by the check runner

Current status:

```text
12 tests passing
```

The tests use representative AWS response dictionaries and do not require a live AWS account.

## Security Philosophy

NimbusAudit is defensive and read-only.

It does not:

* Modify security groups
* Start or stop instances
* Create or delete resources
* Attempt exploitation
* Perform penetration testing
* Scan accounts without authorization
* Automatically remediate findings

The goal is to provide visibility and evidence while leaving remediation decisions to the cloud owner.

## Current Limitations

NimbusAudit is currently focused on AWS security groups.

It does not yet provide complete AWS coverage and should not be treated as a replacement for enterprise cloud-security platforms.

The current version does not yet scan:

* EC2 metadata configuration
* EBS encryption
* S3 bucket policies
* IAM policies
* CloudTrail configuration
* Multiple AWS accounts
* Multiple cloud providers

## Roadmap

Planned improvements include:

* EC2 instance configuration checks
* EBS encryption checks
* S3 public-access checks
* IAM policy analysis
* Improved AWS error handling
* Configurable severity thresholds
* Output-to-file support
* GitHub Actions integration
* Terraform-based demonstration infrastructure
* Oracle Cloud Infrastructure support
* Additional compliance mappings

## Technology Stack

* Python
* Boto3
* AWS IAM
* Pytest
* Bash
* Linux
* Git and GitHub

## Project Status

NimbusAudit is an active portfolio project.

The current version performs live AWS security-group scanning, produces structured findings, supports text and JSON reports, returns automation-friendly exit codes, and includes automated tests for both vulnerable and safe configurations.
