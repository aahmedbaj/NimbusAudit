# NimbusAudit

[![Tests](https://github.com/aahmedbaj/nimbusaudit/actions/workflows/tests.yml/badge.svg)](https://github.com/aahmedbaj/nimbusaudit/actions/workflows/tests.yml)

> See what your cloud forgot to secure.

NimbusAudit is a command-line security auditing tool that examines cloud resources and identifies risky or unintended configurations.

No more open ports for no reason. No more asking, “Since when has SSH been publicly accessible on this EC2 instance?”

NimbusAudit aims to make cloud security configurations easy to inspect, understand, and review as an environment grows.

## Overview

NimbusAudit is a defensive, read-only command-line tool designed for cloud administrators, security engineers, and developers.

It connects to an authorized cloud account, inspects supported resource configurations, and reports potential security issues with clear evidence, severity levels, and recommended remediation.

NimbusAudit currently supports AWS, with additional cloud providers considered for later versions.

## Problem

Cloud environments can contain many resources, permissions, and security settings. Reviewing every configuration manually can become tedious and error-prone, especially during scaling, deployment, or migration.

Features such as remote access, open network ports, flexible IAM permissions, and optional encryption can be useful when configured correctly. However, they can become serious security vulnerabilities when misconfigured.

For example, an EC2 security group may unintentionally expose SSH to the public internet, or a storage bucket may allow public access without a valid business requirement. These mistakes can remain unnoticed as the cloud environment changes.

## Solution

NimbusAudit connects to an authorized AWS account using read-only permissions and inspects supported cloud resource configurations.

It identifies potential security misconfigurations and displays findings in a clear, readable format. Each finding includes:

* A severity level
* The affected resource
* Evidence of the detected configuration
* A recommended remediation
* Relevant security standards mappings

As a command-line tool, NimbusAudit is lightweight, script-friendly, and suitable for local use, Linux administration workflows, and CI/CD integration.

## Current Scope

NimbusAudit currently:

* Supports AWS
* Operates as a command-line tool
* Uses Python and the AWS SDK for Python
* Authenticates using an authorized AWS profile
* Uses read-only AWS permissions
* Inspects EC2 security groups
* Inspects EC2 instance metadata configuration
* Inspects EBS volume encryption
* Inspects S3 bucket Block Public Access configuration
* Produces text and JSON reports
* Supports output files, configurable failure thresholds, and selectable check groups

Additional services and checks will be added incrementally after their behavior and test coverage are validated.

## Out of Scope

The current version does not include:

* Automatic remediation
* Resource creation, modification, or deletion
* Exploitation or active attacks
* Network penetration testing
* A graphical web dashboard
* Oracle Cloud Infrastructure support
* Machine-learning features
* Complete coverage of every AWS service
* Scanning accounts without explicit authorization

## Planned Technologies

* Python
* Boto3
* AWS IAM
* Bash
* Linux
* Git and GitHub
* GitHub Actions
* Pytest
* Terraform in a later phase
* Oracle Cloud Infrastructure in a later phase


## Project Status

NimbusAudit is under active development.

The current version can:

* Authenticate using an authorized AWS profile
* Persist a default AWS profile, region, and output format
* Retrieve supported AWS resources through Boto3
* Detect public IPv4 and IPv6 security-group exposure
* Detect publicly exposed SSH, RDP, MySQL, and PostgreSQL ports
* Detect security groups that expose all protocols and ports
* Detect EC2 instances that do not enforce IMDSv2
* Detect unencrypted EBS volumes
* Inspect S3 bucket Block Public Access configuration
* Detect S3 buckets whose Block Public Access configuration is missing or not fully enabled
* Run all checks or selected check groups
* Provide an optional interactive check-selection menu
* Produce text or JSON reports
* Write reports to output files
* Return exit codes suitable for scripting and CI/CD workflows
* Apply a configurable finding-severity failure threshold
* Serialize findings with severity, evidence, remediation, and standards mappings
* Run automated tests through GitHub Actions

The current scanning core is covered by 93 automated tests.

Planned next steps include expanding AWS service coverage, adding more rules to existing services, improving report presentation, and continuing to refine least-privilege permissions and documentation.

## Required AWS Permissions

NimbusAudit is designed as a read-only security auditing tool. It should be run using a dedicated least-privilege AWS profile or IAM role rather than an administrator profile.

The repository includes a reference IAM policy:

[`docs/nimbusaudit-readonly-policy.json`](docs/nimbusaudit-readonly-policy.json)

The current scanners require:

```text
ec2:DescribeSecurityGroups
ec2:DescribeInstances
ec2:DescribeVolumes
s3:ListAllMyBuckets
s3:GetBucketPublicAccessBlock
s3:GetEncryptionConfiguration
```

The policy uses:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "NimbusAuditEC2ReadOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes"
      ],
      "Resource": "*"
    },
    {
      "Sid": "NimbusAuditS3ReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketPublicAccessBlock",
        "s3:GetEncryptionConfiguration"
      ],
      "Resource": "*"
    }
  ]
}
```

The `"Resource": "*"` value does not grant unrestricted AWS access. It applies only to the listed `ec2:DescribeSecurityGroups` action. This AWS API operation does not support restricting access to individual security-group resources.

The policy file is a reference template. Adding it to the repository does not automatically create an IAM policy, IAM role, or AWS CLI profile.

A recommended setup is:

```text
IAM policy document
        ↓ attached to
NimbusAuditReadOnlyRole
        ↓ assumed through
nimbusaudit-readonly AWS profile
        ↓ stored as the default through
nimbusaudit configure
```

Configure NimbusAudit interactively:

```bash
nimbusaudit configure
```

Or configure individual values non-interactively:

```bash
nimbusaudit configure \
  --profile nimbusaudit-readonly \
  --region eu-central-1 \
  --format text
```

Once configured, start a normal scan with:

```bash
nimbusaudit
```

Command-line options can still be used as temporary overrides:

```bash
nimbusaudit --region us-east-1 --format json
```

Temporary overrides do not modify the saved NimbusAudit configuration.


### Saving reports to a file

NimbusAudit can print reports to stdout or write them to a file.

Print JSON to stdout:

```bash
nimbusaudit --format json
```

Write JSON to a file:

```bash
nimbusaudit --format json --output-file report.json
```

If the output file has no extension, NimbusAudit adds the extension that matches the selected output format:

```bash
nimbusaudit --format json --output-file report
```

This writes:

```text
report.json
```

For text output:

```bash
nimbusaudit --format text --output-file report
```

This writes:

```text
report.txt
```

If a file extension is provided, it must match the selected format. For example, this is rejected:

```bash
nimbusaudit --format json --output-file report.txt
```

NimbusAudit returns exit code `2` when the output file path is invalid or cannot be written.


## Selecting check groups

By default, NimbusAudit runs all available check groups:

```bash
nimbusaudit
```

You can run a specific check group with `--checks`:

```bash
nimbusaudit --checks security-groups
```

```bash
nimbusaudit --checks ec2
```

```bash
nimbusaudit --checks ebs
```

```bash
nimbusaudit --checks s3
```

You can also run multiple groups by separating them with commas:

```bash
nimbusaudit --checks security-groups,s3
```

To explicitly run every available group:

```bash
nimbusaudit --checks all
```

Available check groups:

```text
security-groups
ec2
ebs
s3
```

The `all` option cannot be combined with other groups.

### Interactive menu

NimbusAudit also includes an optional interactive menu:

```bash
nimbusaudit menu
```

The menu lets you select check groups without remembering the `--checks` syntax.

Example menu:

```text
NimbusAudit menu
========================================================================

Select check groups to run:

  0. exit
  1. security-groups
  2. ec2
  3. ebs
  4. s3
  a. all

Enter one option or multiple check numbers separated by commas.
Examples: 1,4 or a
```

Examples:

```text
1
```

Runs only security-group checks.

```text
1,4
```

Runs security-group and S3 checks.

```text
a
```

Runs all checks.

```text
0
```

Exits without starting a scan.

The menu is intended for interactive use. For automation and CI/CD, prefer direct CLI flags such as:

```bash
nimbusaudit --checks security-groups,s3
```


### Configuring failure threshold

NimbusAudit returns exit code `1` when findings meet or exceed the configured failure threshold.

By default, NimbusAudit fails on `HIGH` and `CRITICAL` findings:

```bash
nimbusaudit
```

This is equivalent to:

```bash
nimbusaudit --fail-on high
```

You can make the scan less strict and fail only on critical findings:

```bash
nimbusaudit --fail-on critical
```

Or make it stricter:

```bash
nimbusaudit --fail-on medium
```

```bash
nimbusaudit --fail-on low
```

Severity order:

```text
LOW < MEDIUM < HIGH < CRITICAL
```

Failure behavior:

| Option | Returns exit code `1` when findings include |
|---|---|
| `--fail-on critical` | `CRITICAL` |
| `--fail-on high` | `HIGH`, `CRITICAL` |
| `--fail-on medium` | `MEDIUM`, `HIGH`, `CRITICAL` |
| `--fail-on low` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |

NimbusAudit returns exit code `2` for scan, configuration, AWS, or output errors.
