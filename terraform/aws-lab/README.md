# NimbusAudit Terraform AWS Lab

This directory contains a Terraform-based AWS lab for demonstrating NimbusAudit.

The lab creates intentionally misconfigured AWS resources so NimbusAudit can scan them and produce predictable findings.

The goal is to make NimbusAudit demos reproducible:

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

---

## Status

Current phase:

```text
Phase 5 — Demo workflow documentation
```

The lab currently includes network, EC2, EBS, and S3 resources that map to NimbusAudit checks.

---

## Safety Notice

This lab intentionally creates vulnerable AWS configurations for controlled testing.

Only deploy this lab in an AWS account where you are authorized to create resources.

The lab should not be deployed in a production AWS account.

Destroy the lab after testing:

```bash
terraform destroy
```

---

## Cost Notice

This lab may create AWS resources that can incur charges, including:

* EC2 instance
* EBS root volume
* VPC networking resources
* S3 bucket

The default EC2 instance type is `t3.micro`, but cost and free-tier eligibility depend on your AWS account, region, and usage.

Always run `terraform destroy` after testing.

---

## Requirements

* Terraform 1.6 or newer
* AWS CLI configured with a valid profile
* Permissions to create and destroy the lab resources
* NimbusAudit installed locally

Recommended AWS authentication check:

```bash
aws sts get-caller-identity --profile <your-profile>
```

---

## Resources Created

The lab currently creates:

* VPC
* Public subnet
* Internet gateway
* Public route table
* Route table association
* Security group with SSH open to `0.0.0.0/0`
* EC2 instance attached to the vulnerable security group
* EC2 instance with IMDSv2 not enforced
* Root EBS volume encryption test case
* S3 bucket with incomplete Block Public Access configuration
* S3 bucket using SSE-S3 encryption instead of AWS KMS

---

## Expected NimbusAudit Findings

Running NimbusAudit against this lab should detect:

```text
AWS-EC2-SG-001
SSH exposed to the public internet

AWS-EC2-INSTANCE-001
IMDSv2 is not enforced

AWS-S3-BUCKET-001
S3 bucket does not fully block public access

AWS-S3-BUCKET-003
S3 bucket default encryption does not use AWS KMS
```

Depending on AWS account or region defaults, it may also detect:

```text
AWS-EC2-EBS-001
EBS volume is not encrypted
```

Some AWS accounts enforce EBS encryption by default. In that case, the EBS finding may not appear even when the Terraform configuration requests an unencrypted root volume.

---

## Deploy the Lab

From this directory:

```bash
cd terraform/aws-lab
```

Initialize Terraform:

```bash
terraform init
```

Format and validate the configuration:

```bash
terraform fmt
terraform validate
```

Preview the planned resources:

```bash
terraform plan \
  -var="aws_profile=<your-profile>" \
  -var="aws_region=eu-central-1"
```

Apply the lab:

```bash
terraform apply \
  -var="aws_profile=<your-profile>" \
  -var="aws_region=eu-central-1"
```

When prompted, type:

```text
yes
```

---

## Run NimbusAudit Against the Lab

Return to the repository root:

```bash
cd ../..
```

Run all supported checks:

```bash
nimbusaudit \
  --profile <your-profile> \
  --region eu-central-1 \
  --checks security-groups,ec2,ebs,s3
```

Or run only the S3 checks:

```bash
nimbusaudit \
  --profile <your-profile> \
  --region eu-central-1 \
  --checks s3
```

Or run only the security group check:

```bash
nimbusaudit \
  --profile <your-profile> \
  --region eu-central-1 \
  --checks security-groups
```

---

## Review Terraform Outputs

After applying the lab, you can inspect Terraform outputs:

```bash
cd terraform/aws-lab
terraform output
```

Useful outputs include:

* VPC ID
* public subnet ID
* vulnerable security group ID
* EC2 instance ID
* root EBS volume ID
* demo S3 bucket name

These outputs can be compared with NimbusAudit finding resource IDs.

---

## Destroy the Lab

After testing, destroy all lab resources:

```bash
cd terraform/aws-lab
terraform destroy \
  -var="aws_profile=<your-profile>" \
  -var="aws_region=eu-central-1"
```

When prompted, type:

```text
yes
```

Verify that Terraform state no longer contains managed resources:

```bash
terraform state list
```

After a successful destroy, `terraform plan` may show resources to create again. That is normal because the `.tf` files still define the desired lab.

---

## Important Terraform Files

```text
main.tf
variables.tf
outputs.tf
README.md
.terraform.lock.hcl
```

Do not commit local Terraform runtime files such as:

```text
.terraform/
terraform.tfstate
terraform.tfstate.backup
*.tfvars
```

---

## Relationship to NimbusAudit

This lab supports NimbusAudit `v0.2.0`.

NimbusAudit `v0.1.0` introduced the AWS scanner.

NimbusAudit `v0.2.0` adds a reproducible Terraform lab that creates known misconfigurations and lets users validate the scanner safely.
