# NimbusAudit Terraform AWS Lab

This directory contains a Terraform-based AWS lab for demonstrating NimbusAudit.

The lab is designed to create intentionally misconfigured AWS resources that NimbusAudit can detect.

## Status

This lab is under active development.

Current phase:

```text
Phase 1 — Terraform foundation
```

At this stage, the lab defines the Terraform provider, variables, tags, and basic outputs. It does not create AWS resources yet.

## Requirements

* Terraform 1.6 or newer
* AWS CLI credentials or an AWS CLI profile
* Permission to create and destroy lab resources in the selected AWS account

## Usage

Initialize Terraform:

```bash
terraform init
```

Validate the configuration:

```bash
terraform validate
```

Preview changes:

```bash
terraform plan
```

Use a specific AWS profile and region:

```bash
terraform plan \
  -var="aws_profile=nimbusaudit-readonly" \
  -var="aws_region=eu-central-1"
```

## Safety Notice

Future phases of this lab will create intentionally vulnerable AWS resources for controlled testing.

Only deploy this lab in an AWS account where you are authorized to create resources.

Destroy lab resources after testing:

```bash
terraform destroy
```

## Planned Lab Resources

Future phases will add:

* VPC
* Public subnet
* Internet gateway
* Route table
* Security group with public SSH exposure
* EC2 instance with IMDSv2 not enforced
* EBS encryption test case
* S3 bucket public access and encryption test cases

## Relationship to NimbusAudit

The goal of this lab is to make NimbusAudit demos reproducible:

```text
terraform apply
      ↓
create intentionally misconfigured AWS resources
      ↓
run NimbusAudit
      ↓
review findings
      ↓
terraform destroy
```

## Current Lab Resources

This lab currently creates:

- VPC
- Public subnet
- Internet gateway
- Public route table
- Route table association
- Security group with SSH open to `0.0.0.0/0`
- EC2 instance attached to the vulnerable security group
- EC2 instance with IMDSv2 not enforced
- Root EBS volume encryption test case
- S3 bucket with incomplete Block Public Access configuration
- S3 bucket using SSE-S3 encryption instead of AWS KMS

## Expected NimbusAudit Findings

Running:

~~~bash
nimbusaudit --checks security-groups,ec2,ebs,s3
~~~

should detect:

~~~text
AWS-EC2-SG-001
SSH exposed to the public internet

AWS-EC2-INSTANCE-001
IMDSv2 is not enforced

AWS-S3-BUCKET-001
S3 bucket does not fully block public access

AWS-S3-BUCKET-003
S3 bucket default encryption does not use AWS KMS
~~~

Depending on AWS account or region defaults, it may also detect:

~~~text
AWS-EC2-EBS-001
EBS volume is not encrypted
~~~

The S3 lab intentionally uses SSE-S3 (`AES256`) instead of AWS KMS so NimbusAudit can detect the KMS posture finding.