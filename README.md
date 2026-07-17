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

NimbusAudit will connect to an authorized AWS account using read-only permissions and inspect supported cloud resource configurations.

It will identify potential security misconfigurations and display findings in a clear, readable format. Each finding will eventually include:

* A severity level
* The affected resource
* Evidence of the detected configuration
* A recommended remediation

As a command-line tool, NimbusAudit will be lightweight, script-friendly, and suitable for local use, Linux administration workflows, and future CI/CD integration.

## Initial Scope

The first version of NimbusAudit will intentionally remain small.

* Support AWS only
* Operate as a command-line tool
* Use Python and the AWS SDK for Python
* Authenticate using an authorized AWS profile
* Use read-only AWS permissions
* Inspect EC2 security-group rules
* Detect sensitive ports exposed to the public internet
* Display findings in the terminal

Additional checks will be added only after the initial design is tested and stable.

## Out of Scope

The initial version will not include:

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
* Retrieve EC2 security groups using paginated AWS API calls
* Detect public IPv4 and IPv6 exposure
* Detect publicly exposed SSH, RDP, MySQL, and PostgreSQL ports
* Detect security groups that expose all protocols and ports
* Produce text or JSON reports
* Return exit codes suitable for scripting and CI/CD workflows
* Serialize findings with severity, evidence, remediation, and standards mappings

The security-group scanning core is functional and covered by automated tests.

Planned next steps include improved AWS error handling, EC2 and EBS checks, output-to-file support, and continuous integration.

## Required AWS Permissions

NimbusAudit is designed as a read-only security auditing tool. It should be run using a dedicated least-privilege AWS profile or IAM role rather than an administrator profile.

The repository includes a reference IAM policy:

[`docs/nimbusaudit-readonly-policy.json`](docs/nimbusaudit-readonly-policy.json)

The current security-group scanner requires only:

```text
ec2:DescribeSecurityGroups
ec2:DescribeInstances
ec2:DescribeVolumes
```

The policy uses:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "NimbusAuditSecurityGroupReadOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSecurityGroups"
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


### Selecting check groups

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

You can also run multiple groups by separating them with commas:

```bash
nimbusaudit --checks security-groups,ec2
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
```

The `all` option cannot be combined with other groups.

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
  *. all

Enter one option or multiple check numbers separated by commas.
Examples: 1,3 or *
```

Examples:

```text
1
```

Runs only security group checks.

```text
1,3
```

Runs security group and EBS checks.

```text
*
```

Runs all checks.

```text
0
```

Exits without starting a scan.

The menu is intended for interactive use. For automation and CI/CD, prefer direct CLI flags such as:

```bash
nimbusaudit --checks security-groups,ebs
```