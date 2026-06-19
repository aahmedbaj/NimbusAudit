# NimbusAudit

> See what your cloud forgot to secure.

NimbusAudit is a command-line security auditing tool that examines cloud resources and identifies risky or unintended configurations.

No more open ports for no reason. No more asking, “Since when has SSH been publicly accessible on this EC2 instance?”

NimbusAudit aims to make cloud security configurations easy to inspect, understand, and review as an environment grows.

## Overview

NimbusAudit is a defensive, read-only command-line tool designed for cloud administrators, security engineers, and developers.

It connects to an authorized cloud account, inspects supported resource configurations, and reports potential security issues with clear evidence, severity levels, and recommended remediation.

The initial version will support AWS, with additional cloud providers considered later.

## Problem

Cloud environments can contain many resources, permissions, and security settings. Reviewing every configuration manually can become tedious and error-prone, especially during scaling, deployment, or migration.

Features such as remote access, open network ports, flexible IAM permissions, and optional encryption can be useful when configured correctly. However, they can become serious security vulnerabilities when misconfigured.

For example, an EC2 security group may unintentionally expose SSH to the public internet, or a storage bucket may allow public access without a valid business requirement. These mistakes can remain unnoticed as the cloud environment changes.

## Proposed Solution

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

NimbusAudit is currently in the planning and early development stage.
